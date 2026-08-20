"""SpecialistState, SupervisorState, SpecialistFinding, DiagnosisOutput
(02-ARCHITECTURE.md Section 3.2, 3.4, 3.8). Two distinct state types, not
one flat state -- the Section 3.8 multi-agent redesign means there are 3
separate loops (2 specialists + the supervisor), each needing its own
shape, not a single global state everything shares.
"""
import os
from typing import Literal, TypedDict

from pydantic import BaseModel, model_validator

from agent.tools import ToolResult

# 12-factor config (Section 8) -- no hardcoded loop bound.
SPECIALIST_MAX_ITERATIONS = int(os.environ["SPECIALIST_MAX_ITERATIONS"])


class SpecialistState(TypedDict):
    order_id: str
    evidence: list[ToolResult]
    iterations: int
    # The 3 fields below aren't in 04-BUILD-PLAN.md Phase 3's original
    # pseudocode -- added during implementation because LangGraph nodes
    # only communicate through state, and the plan's 3-field version had
    # nowhere to carry the planner's decision to the executor, or the
    # evaluator's verdict to should_continue/the eventual SpecialistFinding.
    pending_tool_calls: list[dict]  # set by plan_next_action, consumed by execute_tool
    complete: bool  # set by evaluate_evidence; should_continue reads this
    preliminary_assessment: str  # set by evaluate_evidence once complete=True


class SpecialistFinding(BaseModel):
    specialist: Literal["billing_crm", "network"]
    evidence: list[ToolResult]  # everything gathered, raw -- never condensed
    # (Section 3.8: passing raw evidence, not just a prose summary, is what
    # keeps the supervisor's conflict-resolution logic from working off
    # already-lossy information -- the classic multi-agent failure mode).
    preliminary_assessment: str  # the specialist's own read -- a hint, never authoritative


# --- Supervisor (Phase 4) ------------------------------------------------

CONFIDENCE_ORDER = {"low": 0, "medium": 1, "high": 2}  # explicit ordinal
# mapping -- needed so "at least medium confidence" is a real, comparable
# check, not just a label (Section 3.4).


class DiagnosisOutput(BaseModel):
    root_cause: str
    confidence: Literal["low", "medium", "high"]
    evidence: list[str]
    recommended_action: str
    insufficient_evidence: bool

    @model_validator(mode="after")
    def confidence_matches_evidence_state(self):
        # Invariant, enforced by construction, not convention: an
        # "insufficient evidence" diagnosis can never simultaneously claim
        # high or medium confidence (Section 3.4).
        if self.insufficient_evidence and self.confidence != "low":
            raise ValueError(
                "insufficient_evidence=True requires confidence='low' — "
                "cannot report insufficient evidence with non-low confidence"
            )
        return self


class SupervisorState(TypedDict):
    order_id: str
    billing_finding: SpecialistFinding | None
    network_finding: SpecialistFinding | None
    diagnosis: DiagnosisOutput | None
