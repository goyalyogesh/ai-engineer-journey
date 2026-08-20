"""Shared node-factory + graph-wiring logic for both specialist subgraphs.

04-BUILD-PLAN.md Phase 3 describes billing_crm.py and network.py as having
"the same shape" (identical node signatures, identical graph wiring, only
the tool set and role description differ). This file isn't in the plan's
original repo tree -- added during implementation to hold that shared
logic once, instead of duplicating the graph-wiring code verbatim in both
specialist files.

Every node function is built by a factory that takes the LLM and tool set
as parameters (dependency injection, 02-ARCHITECTURE.md Section 8) rather
than importing a hardcoded model/tools -- the concrete payoff being that
tests can build the exact same graph shape with a fake LLM and fake tools,
with no real API calls (Section 13's "unit tests with fake tools" row).
"""
import asyncio
from typing import Literal

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from agent.observability import log_node_transitions
from agent.state import SPECIALIST_MAX_ITERATIONS, SpecialistState
from agent.tools import ToolResult


class _EvidenceAssessment(BaseModel):
    complete: bool
    preliminary_assessment: str


def _evidence_to_text(evidence: list[ToolResult]) -> str:
    if not evidence:
        return "(no evidence gathered yet)"
    return "\n".join(
        f"- {e.tool_name}: success={e.success} data={e.data} error={e.error}"
        for e in evidence
    )


def build_plan_prompt(role: str, order_id: str, evidence: list[ToolResult]) -> str:
    # plan_next_action's prompt (04-BUILD-PLAN.md Phase 3): given the
    # evidence gathered so far, decide which of this specialist's own
    # tools to call next. Tool *availability* is enforced structurally by
    # bind_tools() in make_plan_next_action below (this specialist
    # literally cannot request a tool it doesn't own, Section 3.8) -- the
    # prompt only needs to describe the decision, not re-state the
    # boundary.
    return (
        f"You are {role}, investigating a stuck telecom order "
        f"(order_id={order_id}).\n\n"
        f"Evidence gathered so far:\n{_evidence_to_text(evidence)}\n\n"
        "Decide which of your available tools to call next to investigate "
        "further. You may call more than one tool at once if their inputs "
        "are already available from the evidence above (parallel tool "
        "dispatch, Section 3.5). If you already have enough evidence from "
        "your own tools, don't call anything else."
    )


def parse_plan_response(response) -> list[dict]:
    # Response-handling, deliberately separate from prompt construction
    # above -- Section 13's "test isolation for LLM calls" tests prompt
    # construction and response handling independently, so a broken
    # extraction of tool_calls doesn't hide behind a passing prompt test.
    return [{"name": tc["name"], "args": tc["args"]} for tc in response.tool_calls]


def build_evaluate_prompt(role: str, order_id: str, evidence: list[ToolResult]) -> str:
    # evaluate_evidence's prompt: "is THIS specialist's own investigation
    # complete enough" -- a distinct question from the supervisor's later
    # cross-specialist synthesis (04-BUILD-PLAN.md Phase 3).
    return (
        f"You are {role}, investigating a stuck telecom order "
        f"(order_id={order_id}).\n\n"
        f"Evidence gathered so far:\n{_evidence_to_text(evidence)}\n\n"
        "Is your own investigation (using only your own tools) complete "
        "enough to hand off a preliminary assessment to the supervisor? "
        "Give a short preliminary_assessment either way, based on what "
        "you've found so far."
    )


def make_plan_next_action(specialist: str, role: str, llm: BaseChatModel, tools: dict):
    bound_llm = llm.bind_tools(list(tools.values()))

    @log_node_transitions(f"{specialist}.plan_next_action")
    async def plan_next_action(state: SpecialistState) -> dict:
        prompt = build_plan_prompt(role, state["order_id"], state["evidence"])
        response = await bound_llm.ainvoke(prompt)
        return {"pending_tool_calls": parse_plan_response(response)}

    return plan_next_action


def make_execute_tool(specialist: str, tools: dict):
    @log_node_transitions(f"{specialist}.execute_tool")
    async def execute_tool(state: SpecialistState) -> dict:
        calls = state["pending_tool_calls"]
        # asyncio, not threading/multiprocessing -- I/O-bound tool calls
        # (Section 3.5's reasoning, applied identically at the specialist
        # level).
        results = await asyncio.gather(
            *(tools[c["name"]].ainvoke(c["args"]) for c in calls)
        )
        return {
            "evidence": state["evidence"] + list(results),
            "iterations": state["iterations"] + 1,
            "pending_tool_calls": [],
        }

    return execute_tool


def make_evaluate_evidence(specialist: str, role: str, llm: BaseChatModel):
    structured_llm = llm.with_structured_output(_EvidenceAssessment)

    @log_node_transitions(f"{specialist}.evaluate_evidence")
    async def evaluate_evidence(state: SpecialistState) -> dict:
        prompt = build_evaluate_prompt(role, state["order_id"], state["evidence"])
        assessment = await structured_llm.ainvoke(prompt)
        return {
            "complete": assessment.complete,
            "preliminary_assessment": assessment.preliminary_assessment,
        }

    return evaluate_evidence


def should_continue(state: SpecialistState) -> Literal["continue", "done"]:
    if state["complete"]:
        return "done"
    if state["iterations"] >= SPECIALIST_MAX_ITERATIONS:
        # Cap reached -- report with whatever evidence exists rather than
        # loop forever chasing a "complete" verdict that never arrives.
        return "done"
    return "continue"


def build_specialist_graph(
    specialist: Literal["billing_crm", "network"],
    role: str,
    tools: dict,
    llm: BaseChatModel | None = None,
):
    llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0)
    graph = StateGraph(SpecialistState)
    graph.add_node("plan", make_plan_next_action(specialist, role, llm, tools))
    graph.add_node("execute", make_execute_tool(specialist, tools))
    graph.add_node("evaluate", make_evaluate_evidence(specialist, role, llm))
    graph.add_edge(START, "plan")
    graph.add_edge("plan", "execute")
    graph.add_edge("execute", "evaluate")
    graph.add_conditional_edges(
        "evaluate", should_continue, {"continue": "plan", "done": END}
    )
    # Deliberately no checkpointer here -- only the supervisor's graph
    # gets one (04-BUILD-PLAN.md Phase 4's note: the interrupt()-readiness
    # commitment is a supervisor-level concern, specialists just run to
    # completion and report back).
    return graph.compile()


def initial_specialist_state(order_id: str) -> SpecialistState:
    return {
        "order_id": order_id,
        "evidence": [],
        "iterations": 0,
        "pending_tool_calls": [],
        "complete": False,
        "preliminary_assessment": "",
    }
