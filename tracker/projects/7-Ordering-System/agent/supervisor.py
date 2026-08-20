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
        "inconclusive, not itself a confirmed problem.\n"
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


def apply_precedence_and_pipeline_rules(analysis: SynthesisAnalysis) -> DiagnosisOutput:
    """Section 3.7's precedence rule + FR10's pipeline-order rule, as
    plain, auditable Python -- not LLM judgment. Deterministic and fast to
    unit test (02-ARCHITECTURE.md Section 13)."""
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
        return DiagnosisOutput(
            root_cause=earliest.summary,
            confidence="high",
            evidence=[r.summary for r in true_problems],
            recommended_action=earliest.recommended_action,
            insufficient_evidence=False,
        )

    if len(true_problems) == 1:
        only = true_problems[0]
        return DiagnosisOutput(
            root_cause=only.summary,
            confidence="high",
            evidence=[only.summary],
            recommended_action=only.recommended_action,
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
            diagnosis = apply_precedence_and_pipeline_rules(analysis)
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
