"""Top-level graph -- specialists as subgraph nodes (02-ARCHITECTURE.md
Section 3.8: LangGraph's documented subgraph-as-node pattern, not three
unrelated systems glued together with custom code).

synthesize_diagnosis's design deliberately splits into two parts, not one
LLM call: an LLM *classifies* each specialist's raw evidence (a real
reasoning task -- deciding whether a data dict represents an actual
problem), then plain Python code applies the precedence rule (Section
3.7) and the pipeline-order rule (FR10). Section 3.7 states the precedence
rule exists specifically to be "an auditable design decision, not an
implicit bias buried in a prompt" -- so the rule itself has to be real,
testable code, not something an LLM is trusted to apply consistently
inside a single unstructured call.
"""
import asyncio
import os
from typing import Literal

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from agent.observability import log_node_transitions
from agent.specialists._shared import initial_specialist_state
from agent.specialists.billing_crm import billing_crm_graph as _default_billing_graph
from agent.specialists.network import network_graph as _default_network_graph
from agent.state import DiagnosisOutput, SpecialistFinding, SupervisorState

PIPELINE_ORDER = ["crm", "billing", "provisioning", "inventory"]  # FR10 / Section 3.7


def _evidence_to_text(finding: SpecialistFinding | None) -> str:
    if finding is None:
        return "(did not run)"
    if not finding.evidence:
        return "(no evidence gathered)"
    return "\n".join(
        f"  - {e.tool_name}: success={e.success} data={e.data} error={e.error}"
        for e in finding.evidence
    )


class SpecialistReading(BaseModel):
    has_real_problem: bool
    # Separate from has_real_problem -- added after a real eval finding
    # (05-DEVELOPMENT-LOG.md's Phase 6 entry): a specialist can be certain
    # *something* is wrong (e.g. provisioning failed with an error code)
    # while genuinely not knowing *why* (the error code is absent from the
    # knowledge base). Collapsing those into one boolean let the agent
    # confidently name a fabricated cause -- e.g. reusing ERR_4471's
    # explanation for the unrelated, unknown ERR_9999, because
    # search_knowledge_base always returns its *closest* match, never
    # "no match found" (vector search has no relevance floor by default).
    cause_understood: bool
    stage: Literal["crm", "billing", "provisioning", "inventory"] | None
    system_type: Literal["technical", "administrative"] | None
    summary: str
    recommended_action: str


class SynthesisAnalysis(BaseModel):
    billing_reading: SpecialistReading
    network_reading: SpecialistReading
    # True only if both readings disagree about the *same underlying
    # fact* -- not merely "both specialists found different problems"
    # (that's the FR10 multiple-true-causes case, handled separately).
    conflicting: bool
    conflict_description: str | None


def build_classification_prompt(
    order_id: str,
    billing_finding: SpecialistFinding | None,
    network_finding: SpecialistFinding | None,
) -> str:
    return (
        f"Read the raw evidence gathered by two specialists investigating "
        f"a stuck telecom order (order_id={order_id}), and classify each "
        f"specialist's finding.\n\n"
        f"Billing/CRM specialist evidence:\n{_evidence_to_text(billing_finding)}\n\n"
        f"Network specialist evidence:\n{_evidence_to_text(network_finding)}\n\n"
        "For EACH specialist, decide:\n"
        "- has_real_problem: did their evidence show an actual, confirmed "
        "problem (e.g. an active billing hold, a provisioning failure, no "
        "circuit assigned)? A tool call that failed/was 'unavailable' is "
        "inconclusive, not itself a confirmed problem. If get_order_record's "
        "address and get_inventory_status's address are BOTH present, "
        "compare them literally, character by character -- if they are the "
        "same string, that is NOT an address mismatch, no matter how "
        "confident it might feel to flag it as one; only report a mismatch "
        "if the two address strings actually differ.\n"
        "- cause_understood: is there a specific, evidence-backed "
        "explanation for that problem? A search_knowledge_base result "
        "carries two independent signals: exact_match_found (vector "
        "search) and graph_match_found (a Cypher graph traversal that, "
        "when true, also gives you 'graph': {cause, resolution, "
        "related_incidents}). If EITHER is true, the cause is genuinely "
        "understood -- trust the graph's cause/resolution over a vague "
        "vector snippet when both are present, since the graph is a "
        "curated, structured fact rather than a similarity guess. If BOTH "
        "are false (or the query wasn't about a specific error code at "
        "all), the knowledge base has NO real explanation -- it only "
        "returned its closest, unrelated vector match, which does NOT "
        "count as cause_understood=true. Set it false and let summary say "
        "the cause is unknown.\n"
        "- stage: which pipeline stage the problem belongs to -- crm, "
        "billing, provisioning, or inventory (null if no real problem).\n"
        "- system_type: 'technical' for provisioning/inventory evidence, "
        "'administrative' for CRM/billing evidence (null if no real "
        "problem).\n"
        "- summary: one sentence describing the specific problem found (or "
        "'no problem found' if none).\n"
        "- recommended_action: one concrete next step to resolve it (or "
        "'none' if no real problem).\n\n"
        "Then decide whether the two specialists' evidence CONFLICTS -- "
        "meaning they disagree about the *same underlying fact* (e.g. one "
        "says a circuit is assigned, the other says it isn't). Two "
        "specialists finding two *different, both-true* problems is NOT a "
        "conflict -- only set conflicting=True for an actual disagreement."
    )


def _unexplained_problem_diagnosis(evidence_summaries: list[str]) -> DiagnosisOutput:
    # Shared by every branch below: a confirmed problem whose cause isn't
    # actually understood must never be reported as a confident root
    # cause (05-DEVELOPMENT-LOG.md's Phase 6 finding -- naming a
    # fabricated cause here is exactly the FR6 failure mode the eval
    # harness exists to catch).
    return DiagnosisOutput(
        root_cause="a real problem was found but its specific cause could not be confidently determined",
        confidence="low",
        evidence=evidence_summaries,
        recommended_action="escalate for manual investigation of the unexplained failure",
        insufficient_evidence=True,
    )


def _any_tool_failures(finding: SpecialistFinding | None) -> bool:
    if finding is None:
        return False
    return any(not e.success for e in finding.evidence)


def apply_precedence_and_pipeline_rules(
    analysis: SynthesisAnalysis, evidence_complete: bool = True
) -> DiagnosisOutput:
    """Section 3.7's precedence rule + FR10's pipeline-order rule, as
    plain, auditable Python -- not LLM judgment. Deterministic and fast to
    unit test (02-ARCHITECTURE.md Section 13).

    `evidence_complete` distinguishes two outcomes the original version
    conflated into one (caught during Phase 8's eval re-run: it broke the
    "clean order" archetype, which had likely been silently wrong since
    Phase 4): neither specialist finding a real problem can mean either
    "confirmed nothing is wrong" (every tool call succeeded, both
    readings genuinely support a clean order) or "couldn't actually tell"
    (a tool call failed/was unavailable, so the investigation itself was
    incomplete). Those are not the same answer -- the first is a
    confident, correct diagnosis; the second is a genuine
    insufficient_evidence case.
    """
    readings = {
        "billing_crm": analysis.billing_reading,
        "network": analysis.network_reading,
    }

    if analysis.conflicting:
        technical = [r for r in readings.values() if r.system_type == "technical"]
        administrative = [r for r in readings.values() if r.system_type == "administrative"]
        if len(technical) == 1 and len(administrative) == 1:
            # Precedence rule: technical (Provisioning/Inventory) beats
            # administrative (CRM/Billing) when they conflict.
            winner = technical[0]
            if not winner.cause_understood:
                return _unexplained_problem_diagnosis([r.summary for r in readings.values()])
            return DiagnosisOutput(
                root_cause=winner.summary,
                confidence="medium",  # a resolved conflict, not a clean single finding
                evidence=[r.summary for r in readings.values()],
                recommended_action=winner.recommended_action,
                insufficient_evidence=False,
            )
        # Conflict can't be resolved by the precedence rule (e.g. both
        # sides technical, or the classification didn't clearly split
        # technical vs administrative) -- name the conflict, don't guess.
        return DiagnosisOutput(
            root_cause="conflicting evidence between specialists, unresolved",
            confidence="low",
            evidence=[analysis.conflict_description or "unspecified conflict"],
            recommended_action="escalate for manual review of the conflicting evidence",
            insufficient_evidence=True,
        )

    true_problems = [r for r in readings.values() if r.has_real_problem]

    if len(true_problems) >= 2:
        # Pipeline-order rule (FR10): report whichever real problem occurs
        # earliest in CRM -> Billing -> Provisioning -> Inventory. Every
        # genuinely-true finding still appears in `evidence`.
        earliest = min(true_problems, key=lambda r: PIPELINE_ORDER.index(r.stage))
        if not earliest.cause_understood:
            return _unexplained_problem_diagnosis([r.summary for r in true_problems])
        return DiagnosisOutput(
            root_cause=earliest.summary,
            confidence="high",
            evidence=[r.summary for r in true_problems],
            recommended_action=earliest.recommended_action,
            insufficient_evidence=False,
        )

    if len(true_problems) == 1:
        only = true_problems[0]
        if not only.cause_understood:
            return _unexplained_problem_diagnosis([only.summary])
        return DiagnosisOutput(
            root_cause=only.summary,
            confidence="high",
            evidence=[only.summary],
            recommended_action=only.recommended_action,
            insufficient_evidence=False,
        )

    if evidence_complete:
        # Both specialists genuinely investigated (no failed/unavailable
        # tool calls) and neither found a real problem -- a confirmed
        # clean order, not an ambiguous one. This is a positive finding,
        # not a shrug.
        return DiagnosisOutput(
            root_cause="No issue found -- all available evidence indicates the order is proceeding normally",
            confidence="high",
            evidence=[analysis.billing_reading.summary, analysis.network_reading.summary],
            recommended_action="No action needed",
            insufficient_evidence=False,
        )

    return DiagnosisOutput(
        root_cause="no clear cause identified from available evidence",
        confidence="low",
        evidence=[analysis.billing_reading.summary, analysis.network_reading.summary],
        recommended_action="gather more evidence or escalate for manual review",
        insufficient_evidence=True,
    )


def make_dispatch_specialists(billing_graph=None, network_graph_=None):
    billing_graph = billing_graph or _default_billing_graph
    network_graph_ = network_graph_ or _default_network_graph

    @log_node_transitions("supervisor.dispatch_specialists")
    async def dispatch_specialists(state: SupervisorState) -> dict:
        # Both specialists dispatched together, immediately -- same
        # reasoning as Section 3.5's Round 1, applied at agent granularity
        # instead of tool granularity (Section 3.8, step 1).
        billing_result, network_result = await asyncio.gather(
            billing_graph.ainvoke(initial_specialist_state(state["order_id"])),
            network_graph_.ainvoke(initial_specialist_state(state["order_id"])),
        )
        return {
            "billing_finding": SpecialistFinding(
                specialist="billing_crm",
                evidence=billing_result["evidence"],
                preliminary_assessment=billing_result["preliminary_assessment"],
            ),
            "network_finding": SpecialistFinding(
                specialist="network",
                evidence=network_result["evidence"],
                preliminary_assessment=network_result["preliminary_assessment"],
            ),
        }

    return dispatch_specialists


def _kb_search_found_no_match(finding: SpecialistFinding | None) -> bool:
    # Deterministic override, not just prompt guidance: the classifier LLM
    # doesn't *always* honor exact_match_found=False on its own, even
    # though it's an explicit instruction (05-DEVELOPMENT-LOG.md's Phase 6
    # finding -- gpt-4o-mini followed it in most, not all, cases). Since
    # exact_match_found/graph_match_found are already deterministic
    # signals computed in agent/tools.py, cross-checking them here in code
    # closes the gap completely instead of just reducing it.
    #
    # Phase 8 extends this to 2 independent signals (vector + graph) --
    # "no match" now means every *code-specific* search_knowledge_base
    # call this specialist made (there could be more than one) came back
    # with neither signal true. A real regression caught during Phase 8's
    # own eval re-run: only calls where exact_match_found is explicitly
    # False (a code was actually looked up and came back empty) count as
    # "searched, found nothing" -- a call where it's None (the query
    # wasn't about a specific error code at all, e.g. a specialist
    # confirming an address mismatch has no reason to search the KB) must
    # be excluded entirely, not treated as a failed lookup for a problem
    # the KB was never asked about in the first place.
    if finding is None:
        return False
    code_specific_calls = [
        e for e in finding.evidence
        if e.tool_name == "search_knowledge_base" and e.success and isinstance(e.data, dict)
        and e.data.get("exact_match_found") is not None
    ]
    if not code_specific_calls:
        return False
    return not any(
        e.data.get("exact_match_found") is True or e.data.get("graph_match_found") is True
        for e in code_specific_calls
    )


def _enforce_kb_grounding(analysis: SynthesisAnalysis, state: SupervisorState) -> SynthesisAnalysis:
    if _kb_search_found_no_match(state["billing_finding"]):
        analysis.billing_reading.cause_understood = False
    if _kb_search_found_no_match(state["network_finding"]):
        analysis.network_reading.cause_understood = False
    return analysis


def _provisioning_succeeded(finding: SpecialistFinding | None) -> bool:
    if finding is None:
        return False
    return any(
        e.tool_name == "get_provisioning_log" and e.success and e.data
        and e.data.get("status") == "succeeded"
        for e in finding.evidence
    )


def _addresses_confirmed_matching(
    billing_finding: SpecialistFinding | None, network_finding: SpecialistFinding | None
) -> bool:
    order_address = None
    for e in (billing_finding.evidence if billing_finding else []):
        if e.tool_name == "get_order_record" and e.success and e.data:
            order_address = e.data.get("address")
    inventory_address = None
    for e in (network_finding.evidence if network_finding else []):
        if e.tool_name == "get_inventory_status" and e.success and e.data:
            inventory_address = e.data.get("address")
    if order_address is None or inventory_address is None:
        return False
    return order_address.strip().lower() == inventory_address.strip().lower()


def _enforce_address_grounding(analysis: SynthesisAnalysis, state: SupervisorState) -> SynthesisAnalysis:
    # A real, observed regression during Phase 8's own eval re-run: the
    # classifier LLM occasionally hallucinated an "address mismatch" even
    # when provisioning succeeded and the CRM/Inventory address strings
    # were literally identical -- both facts are directly, deterministically
    # checkable from raw evidence (no LLM judgment needed), and a strengthened
    # prompt instruction alone did not reliably stop it (same lesson as
    # Phase 6: don't trust prompt wording for something code can just
    # verify). When both facts hold, the network reading cannot genuinely
    # have a real problem here -- force it, don't just hope the model
    # gets it right.
    if _provisioning_succeeded(state["network_finding"]) and _addresses_confirmed_matching(
        state["billing_finding"], state["network_finding"]
    ):
        analysis.network_reading.has_real_problem = False
        analysis.network_reading.summary = "no problem found"
    return analysis


def make_synthesize_diagnosis(llm: BaseChatModel | None = None):
    llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm = llm.with_structured_output(SynthesisAnalysis)

    @log_node_transitions("supervisor.synthesize_diagnosis")
    async def synthesize_diagnosis(state: SupervisorState) -> dict:
        prompt = build_classification_prompt(
            state["order_id"], state["billing_finding"], state["network_finding"]
        )
        try:
            analysis = await structured_llm.ainvoke(prompt)
            analysis = _enforce_kb_grounding(analysis, state)
            analysis = _enforce_address_grounding(analysis, state)
            evidence_complete = not (
                _any_tool_failures(state["billing_finding"])
                or _any_tool_failures(state["network_finding"])
            )
            diagnosis = apply_precedence_and_pipeline_rules(analysis, evidence_complete)
        except Exception as e:
            # agent/state.py's confidence_matches_evidence_state validator
            # (and apply_precedence_and_pipeline_rules above) exist to make
            # a contradictory diagnosis unconstructable (Section 3.4). If
            # anything in this path still fails, insufficient_evidence is
            # the only safe outcome -- never a crashed request (same
            # "report explicitly, never silently drop" philosophy as
            # Section 3.6's tool-failure handling).
            diagnosis = DiagnosisOutput(
                root_cause="unable to produce a valid diagnosis",
                confidence="low",
                evidence=[f"synthesis error: {e}"],
                recommended_action="escalate for manual review",
                insufficient_evidence=True,
            )
        return {"diagnosis": diagnosis}

    return synthesize_diagnosis


def build_supervisor_graph(
    billing_graph=None,
    network_graph_=None,
    llm: BaseChatModel | None = None,
    checkpointer=None,
):
    graph = StateGraph(SupervisorState)
    graph.add_node("dispatch", make_dispatch_specialists(billing_graph, network_graph_))
    graph.add_node("synthesize", make_synthesize_diagnosis(llm))
    graph.add_edge(START, "dispatch")
    graph.add_edge("dispatch", "synthesize")
    graph.add_edge("synthesize", END)
    # Only the supervisor gets a checkpointer, not each specialist -- the
    # interrupt()-readiness commitment (Section 3.1) is about a future
    # human-approval gate before a write action, and any such gate belongs
    # at the supervisor's decision point (before synthesize_diagnosis acts
    # on aggregated findings), not inside a specialist's internal loop.
    # Specialists run to completion and report back; only the supervisor's
    # decision point is a plausible future pause/resume boundary.
    return graph.compile(checkpointer=checkpointer)


# --- Real, checkpointed graph, built lazily -----------------------------
# AsyncSqliteSaver.from_conn_string(...) is itself an async context
# manager (04-BUILD-PLAN.md's pseudocode named the sync SqliteSaver, which
# doesn't support the async methods this graph's .ainvoke()-only nodes
# need -- caught during implementation, see 05-DEVELOPMENT-LOG.md). It
# can't be entered at plain module-import time (no running event loop
# yet), so the real, persisted graph is built lazily on first use and
# cached -- proper lifecycle ownership (closing it on shutdown) belongs to
# Phase 5's FastAPI lifespan, not this module.
_checkpointer_cm = None
_compiled_supervisor_graph = None


async def get_supervisor_graph():
    global _checkpointer_cm, _compiled_supervisor_graph
    if _compiled_supervisor_graph is not None:
        return _compiled_supervisor_graph

    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

    db_path = os.environ.get("SUPERVISOR_CHECKPOINT_DB", "agent_checkpoints.db")
    _checkpointer_cm = AsyncSqliteSaver.from_conn_string(db_path)
    checkpointer = await _checkpointer_cm.__aenter__()
    _compiled_supervisor_graph = build_supervisor_graph(checkpointer=checkpointer)
    return _compiled_supervisor_graph


def initial_supervisor_state(order_id: str) -> SupervisorState:
    return {
        "order_id": order_id,
        "billing_finding": None,
        "network_finding": None,
        "diagnosis": None,
    }
