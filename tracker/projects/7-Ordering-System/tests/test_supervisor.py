import os

import pytest

from agent.state import DiagnosisOutput, SpecialistFinding
from agent.supervisor import (
    SpecialistReading,
    SynthesisAnalysis,
    _enforce_kb_grounding,
    _evidence_to_text,
    apply_precedence_and_pipeline_rules,
    build_supervisor_graph,
    initial_supervisor_state,
    make_synthesize_diagnosis,
)
from agent.tools import ToolResult


class FakeLLM:
    """Same DI stand-in pattern as tests/test_specialists.py -- lets
    synthesize_diagnosis be tested without a real API call."""

    def __init__(self, response):
        self._response = response

    def with_structured_output(self, schema):
        return self

    async def ainvoke(self, prompt):
        return self._response


class RaisingLLM:
    def with_structured_output(self, schema):
        return self

    async def ainvoke(self, prompt):
        raise RuntimeError("boom")


def _reading(
    has_real_problem, stage=None, system_type=None, summary="no problem found",
    action="none", cause_understood=True,
):
    return SpecialistReading(
        has_real_problem=has_real_problem, cause_understood=cause_understood,
        stage=stage, system_type=system_type, summary=summary, recommended_action=action,
    )


def _finding(specialist: str) -> SpecialistFinding:
    return SpecialistFinding(specialist=specialist, evidence=[], preliminary_assessment="")


# --- DiagnosisOutput's own invariant (agent/state.py, Section 3.4) ------

def test_diagnosis_output_rejects_insufficient_evidence_with_non_low_confidence():
    # The core invariant this whole module's fallback paths depend on:
    # an impossible state must be genuinely unconstructable, not just
    # discouraged by prompt wording.
    with pytest.raises(ValueError, match="insufficient_evidence=True requires confidence='low'"):
        DiagnosisOutput(
            root_cause="x", confidence="high", evidence=[],
            recommended_action="x", insufficient_evidence=True,
        )


def test_evidence_to_text_handles_a_specialist_that_did_not_run():
    # Section 3.8's "What did NOT change" notes a future smarter supervisor
    # could choose to skip a specialist entirely -- not built in v1, but
    # _evidence_to_text must not crash if billing_finding/network_finding
    # is ever None.
    assert _evidence_to_text(None) == "(did not run)"


# --- apply_precedence_and_pipeline_rules ---------------------------------
# 02-ARCHITECTURE.md Section 13: "fast, isolated synthesize_diagnosis unit
# tests" -- these run in milliseconds, no LLM involved, because the rule
# itself is plain Python (Section 3.7's "auditable, not an implicit bias
# buried in a prompt").

def test_conflict_resolved_by_technical_precedence():
    analysis = SynthesisAnalysis(
        billing_reading=_reading(True, "billing", "administrative", "billing shows no hold", "n/a"),
        network_reading=_reading(True, "provisioning", "technical", "provisioning failed, no circuit assigned", "assign a circuit"),
        conflicting=True,
        conflict_description="provisioning implies a billing cause but billing shows clean",
    )
    diagnosis = apply_precedence_and_pipeline_rules(analysis)
    assert diagnosis.insufficient_evidence is False
    assert diagnosis.confidence == "medium"
    assert diagnosis.root_cause == "provisioning failed, no circuit assigned"


def test_unresolvable_conflict_between_two_technical_readings():
    analysis = SynthesisAnalysis(
        billing_reading=_reading(True, "provisioning", "technical", "provisioning says succeeded", "n/a"),
        network_reading=_reading(True, "inventory", "technical", "inventory says unassigned", "n/a"),
        conflicting=True,
        conflict_description="provisioning and inventory disagree",
    )
    diagnosis = apply_precedence_and_pipeline_rules(analysis)
    assert diagnosis.insufficient_evidence is True
    assert diagnosis.confidence == "low"


def test_pipeline_order_rule_picks_earliest_stage():
    # FR10: two independently *true* causes, not a conflict -- billing
    # (earlier in the pipeline) must win over provisioning.
    analysis = SynthesisAnalysis(
        billing_reading=_reading(True, "billing", "administrative", "active billing hold", "resolve the hold"),
        network_reading=_reading(True, "provisioning", "technical", "provisioning failed", "retry provisioning"),
        conflicting=False,
        conflict_description=None,
    )
    diagnosis = apply_precedence_and_pipeline_rules(analysis)
    assert diagnosis.insufficient_evidence is False
    assert diagnosis.confidence == "high"
    assert diagnosis.root_cause == "active billing hold"
    # Both true findings still appear in evidence, even though only one is root_cause.
    assert "active billing hold" in diagnosis.evidence
    assert "provisioning failed" in diagnosis.evidence


def test_single_clean_cause():
    analysis = SynthesisAnalysis(
        billing_reading=_reading(False),
        network_reading=_reading(True, "inventory", "technical", "no circuit assigned for address", "assign a circuit"),
        conflicting=False,
        conflict_description=None,
    )
    diagnosis = apply_precedence_and_pipeline_rules(analysis)
    assert diagnosis.insufficient_evidence is False
    assert diagnosis.confidence == "high"
    assert diagnosis.root_cause == "no circuit assigned for address"


# --- cause_understood=False (05-DEVELOPMENT-LOG.md's Phase 6 finding) ---
# A confirmed problem whose cause isn't actually understood must never be
# reported as a confident root cause -- e.g. an unknown provisioning error
# code where search_knowledge_base only returned an unrelated document's
# closest vector match, not a genuine explanation.

def test_single_problem_with_unknown_cause_is_insufficient_evidence():
    analysis = SynthesisAnalysis(
        billing_reading=_reading(False),
        network_reading=_reading(
            True, "provisioning", "technical", "provisioning failed with ERR_9999",
            "escalate", cause_understood=False,
        ),
        conflicting=False,
        conflict_description=None,
    )
    diagnosis = apply_precedence_and_pipeline_rules(analysis)
    assert diagnosis.insufficient_evidence is True
    assert diagnosis.confidence == "low"
    assert "ERR_9999" not in diagnosis.root_cause  # never fabricate a specific cause


def test_pipeline_order_winner_with_unknown_cause_is_insufficient_evidence():
    analysis = SynthesisAnalysis(
        billing_reading=_reading(True, "billing", "administrative", "active billing hold", "resolve the hold", cause_understood=False),
        network_reading=_reading(True, "provisioning", "technical", "provisioning failed", "retry", cause_understood=True),
        conflicting=False,
        conflict_description=None,
    )
    # billing is earliest in the pipeline and would normally win, but its
    # cause isn't understood -- must not silently fall through to network's
    # (later-stage) finding as if that were the answer either.
    diagnosis = apply_precedence_and_pipeline_rules(analysis)
    assert diagnosis.insufficient_evidence is True
    assert diagnosis.confidence == "low"


def test_resolved_conflict_with_unknown_cause_is_insufficient_evidence():
    analysis = SynthesisAnalysis(
        billing_reading=_reading(True, "billing", "administrative", "billing shows no hold", "n/a"),
        network_reading=_reading(
            True, "provisioning", "technical", "provisioning failed with an unrecognized code",
            "escalate", cause_understood=False,
        ),
        conflicting=True,
        conflict_description="provisioning implies a billing cause but billing shows clean",
    )
    diagnosis = apply_precedence_and_pipeline_rules(analysis)
    assert diagnosis.insufficient_evidence is True
    assert diagnosis.confidence == "low"


def test_kb_search_found_no_match_false_when_specialist_did_not_run():
    from agent.supervisor import _kb_search_found_no_match
    assert _kb_search_found_no_match(None) is False


def test_enforce_kb_grounding_also_checks_billing_reading():
    # billing_crm doesn't currently own search_knowledge_base, so this is
    # defensive rather than reachable today -- same reasoning as
    # test_evidence_to_text_handles_a_specialist_that_did_not_run above:
    # a future redesign could change tool ownership, and this shouldn't
    # silently stop working if it does.
    analysis = SynthesisAnalysis(
        billing_reading=_reading(True, "billing", "administrative", "billing issue", "fix it", cause_understood=True),
        network_reading=_reading(False),
        conflicting=False, conflict_description=None,
    )
    state = initial_supervisor_state("ORD-X")
    state["billing_finding"] = SpecialistFinding(
        specialist="billing_crm",
        evidence=[ToolResult(
            tool_name="search_knowledge_base", success=True,
            data={"results": [], "exact_match_found": False}, error=None, latency_ms=1.0,
        )],
        preliminary_assessment="",
    )
    state["network_finding"] = _finding("network")

    corrected = _enforce_kb_grounding(analysis, state)
    assert corrected.billing_reading.cause_understood is False


def test_enforce_kb_grounding_overrides_llm_when_kb_found_no_match():
    # The classifier LLM doesn't always honor exact_match_found=False on
    # its own -- this is the deterministic backstop
    # (05-DEVELOPMENT-LOG.md's Phase 6 finding), so it must actually flip
    # cause_understood even when the LLM's own analysis got it wrong.
    analysis = SynthesisAnalysis(
        billing_reading=_reading(False),
        network_reading=_reading(
            True, "provisioning", "technical", "provisioning failed",
            "assign a circuit", cause_understood=True,  # LLM wrongly trusted the KB's closest match
        ),
        conflicting=False, conflict_description=None,
    )
    state = initial_supervisor_state("ORD-X")
    state["network_finding"] = SpecialistFinding(
        specialist="network",
        evidence=[ToolResult(
            tool_name="search_knowledge_base", success=True,
            data={"results": [], "exact_match_found": False}, error=None, latency_ms=1.0,
        )],
        preliminary_assessment="",
    )
    state["billing_finding"] = _finding("billing_crm")

    corrected = _enforce_kb_grounding(analysis, state)
    assert corrected.network_reading.cause_understood is False


def test_enforce_kb_grounding_leaves_genuine_matches_alone():
    analysis = SynthesisAnalysis(
        billing_reading=_reading(False),
        network_reading=_reading(True, "provisioning", "technical", "provisioning failed", "fix it", cause_understood=True),
        conflicting=False, conflict_description=None,
    )
    state = initial_supervisor_state("ORD-X")
    state["network_finding"] = SpecialistFinding(
        specialist="network",
        evidence=[ToolResult(
            tool_name="search_knowledge_base", success=True,
            data={"results": [{"source": "err-4471"}], "exact_match_found": True}, error=None, latency_ms=1.0,
        )],
        preliminary_assessment="",
    )
    state["billing_finding"] = _finding("billing_crm")

    corrected = _enforce_kb_grounding(analysis, state)
    assert corrected.network_reading.cause_understood is True


def test_no_clear_cause_is_insufficient_evidence():
    analysis = SynthesisAnalysis(
        billing_reading=_reading(False), network_reading=_reading(False),
        conflicting=False, conflict_description=None,
    )
    diagnosis = apply_precedence_and_pipeline_rules(analysis)
    assert diagnosis.insufficient_evidence is True
    assert diagnosis.confidence == "low"


# --- synthesize_diagnosis node, with a fake LLM (DI, Section 8/13) ------

async def test_synthesize_diagnosis_node_wires_fake_analysis_through():
    fake_analysis = SynthesisAnalysis(
        billing_reading=_reading(False),
        network_reading=_reading(True, "inventory", "technical", "no circuit assigned", "assign a circuit"),
        conflicting=False, conflict_description=None,
    )
    node = make_synthesize_diagnosis(FakeLLM(fake_analysis))
    state = initial_supervisor_state("ORD-X")
    state["billing_finding"] = _finding("billing_crm")
    state["network_finding"] = _finding("network")

    update = await node(state)
    assert update["diagnosis"].root_cause == "no circuit assigned"
    assert update["diagnosis"].insufficient_evidence is False


async def test_synthesize_diagnosis_falls_back_to_insufficient_evidence_on_error():
    # agent/state.py's validator (and this fallback) exist so a broken
    # synthesis call degrades safely instead of crashing the request
    # (Section 3.6's "report explicitly, never silently drop" philosophy,
    # applied here to the supervisor instead of a tool call).
    node = make_synthesize_diagnosis(RaisingLLM())
    state = initial_supervisor_state("ORD-X")
    state["billing_finding"] = _finding("billing_crm")
    state["network_finding"] = _finding("network")

    update = await node(state)
    assert update["diagnosis"].insufficient_evidence is True
    assert update["diagnosis"].confidence == "low"


# --- Full-stack integration test: real specialists, real LLM ------------

async def test_supervisor_full_stack_ord_88213():
    graph = build_supervisor_graph()  # real specialists + real LLM, no checkpointer needed here
    result = await graph.ainvoke(initial_supervisor_state("ORD-88213"))

    diagnosis = result["diagnosis"]
    assert diagnosis.insufficient_evidence is False
    # Billing is clean for ORD-88213 (worked example); only the Network
    # side has a real, confirmed problem. Usually classified as the clean
    # single-cause branch (confidence="high"), but the classifier LLM
    # occasionally reads billing's "no problem" reading as a resolvable
    # conflict with network's finding instead (confidence="medium") --
    # both are a *correct* diagnosis, just via a different valid branch,
    # so this asserts "at least medium" rather than pinning an exact
    # confidence level against a live, not-fully-deterministic LLM call.
    assert diagnosis.confidence in ("medium", "high")
    root_cause_lower = diagnosis.root_cause.lower()
    assert "circuit" in root_cause_lower or "4471" in root_cause_lower or "provision" in root_cause_lower


# --- Checkpointer -- verifies the AsyncSqliteSaver fix actually works ---

async def test_get_supervisor_graph_checkpoints_for_real(tmp_path, monkeypatch):
    import agent.supervisor as supervisor_module

    db_path = str(tmp_path / "test_checkpoints.db")
    monkeypatch.setenv("SUPERVISOR_CHECKPOINT_DB", db_path)
    # Force a fresh graph/checkpointer for this test, regardless of
    # whatever else may have already called get_supervisor_graph().
    supervisor_module._compiled_supervisor_graph = None
    supervisor_module._checkpointer_cm = None

    graph = await supervisor_module.get_supervisor_graph()
    config = {"configurable": {"thread_id": "test-thread"}}
    result = await graph.ainvoke(initial_supervisor_state("ORD-88213"), config=config)
    assert result["diagnosis"] is not None
    assert os.path.exists(db_path)

    state_snapshot = await graph.aget_state(config)
    assert state_snapshot.values["order_id"] == "ORD-88213"

    # Second call must reuse the cached graph/checkpointer, not rebuild
    # them (module-level singleton -- see the comment above
    # get_supervisor_graph in agent/supervisor.py).
    same_graph = await supervisor_module.get_supervisor_graph()
    assert same_graph is graph
