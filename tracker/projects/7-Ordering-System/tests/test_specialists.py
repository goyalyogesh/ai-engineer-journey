from types import SimpleNamespace

from langchain_core.tools import tool

from agent.specialists._shared import (
    build_evaluate_prompt,
    build_plan_prompt,
    initial_specialist_state,
    make_evaluate_evidence,
    make_execute_tool,
    make_plan_next_action,
    parse_plan_response,
    should_continue,
)
from agent.specialists.billing_crm import TOOLS as BILLING_CRM_TOOLS
from agent.specialists.billing_crm import billing_crm_graph
from agent.specialists.network import TOOLS as NETWORK_TOOLS
from agent.specialists.network import network_graph
from agent.tools import ToolResult


class FakeLLM:
    """Stand-in for a real chat model -- 02-ARCHITECTURE.md Section 8's DI
    pattern is what makes it possible to test plan_next_action/
    evaluate_evidence's *decision logic* without ever calling the real
    API (Section 13's "unit tests with fake tools" row)."""

    def __init__(self, response):
        self._response = response
        self.bound_tools = None

    def bind_tools(self, tools):
        self.bound_tools = tools
        return self

    def with_structured_output(self, schema):
        return self

    async def ainvoke(self, prompt):
        return self._response


@tool
async def _fake_get_order_record(order_id: str) -> ToolResult:
    """fake get_order_record for tests"""
    return ToolResult(
        tool_name="get_order_record", success=True,
        data={"order_id": order_id, "customer_id": "CUST-001"}, error=None,
        latency_ms=1.0,
    )


@tool
async def _fake_get_billing_status(customer_id: str) -> ToolResult:
    """fake get_billing_status for tests"""
    return ToolResult(
        tool_name="get_billing_status", success=True,
        data={"customer_id": customer_id, "hold_active": False}, error=None,
        latency_ms=1.0,
    )


# --- Prompt construction / response handling, tested independently ------
# (Section 13's "test isolation for LLM calls": prompt construction and
# response handling are separate concerns, tested separately, so a broken
# tool_calls extraction can't hide behind a passing prompt test.)

def test_build_plan_prompt_includes_order_id_and_evidence():
    evidence = [
        ToolResult(tool_name="get_order_record", success=True,
                   data={"status": "created"}, error=None, latency_ms=1.0)
    ]
    prompt = build_plan_prompt("the Billing/CRM specialist", "ORD-88213", evidence)
    assert "ORD-88213" in prompt
    assert "get_order_record" in prompt


def test_build_plan_prompt_with_no_evidence_yet():
    prompt = build_plan_prompt("the Network specialist", "ORD-88213", [])
    assert "no evidence gathered yet" in prompt


def test_build_evaluate_prompt_includes_order_id():
    prompt = build_evaluate_prompt("the Network specialist", "ORD-88213", [])
    assert "ORD-88213" in prompt


def test_parse_plan_response_extracts_name_and_args():
    response = SimpleNamespace(
        tool_calls=[{"name": "get_order_record", "args": {"order_id": "ORD-88213"}, "id": "1"}]
    )
    calls = parse_plan_response(response)
    assert calls == [{"name": "get_order_record", "args": {"order_id": "ORD-88213"}}]


# --- Domain split (Section 3.8): each specialist only owns its own tools -

def test_billing_crm_specialist_does_not_own_network_tools():
    assert set(BILLING_CRM_TOOLS) == {"get_order_record", "get_billing_status"}


def test_network_specialist_does_not_own_billing_crm_tools():
    assert set(NETWORK_TOOLS) == {
        "get_provisioning_log", "get_inventory_status", "search_knowledge_base",
    }


# --- should_continue -----------------------------------------------------

def test_should_continue_done_when_complete():
    state = {"complete": True, "iterations": 1}
    assert should_continue(state) == "done"


def test_should_continue_done_when_max_iterations_reached():
    state = {"complete": False, "iterations": 3}  # SPECIALIST_MAX_ITERATIONS
    assert should_continue(state) == "done"


def test_should_continue_continue_otherwise():
    state = {"complete": False, "iterations": 1}
    assert should_continue(state) == "continue"


# --- Node-level tests with fake LLM + fake tools (DI) --------------------

async def test_execute_tool_dispatches_in_parallel_and_appends_evidence():
    execute_tool = make_execute_tool(
        "billing_crm",
        {"get_order_record": _fake_get_order_record, "get_billing_status": _fake_get_billing_status},
    )
    state = initial_specialist_state("ORD-88213")
    state["pending_tool_calls"] = [
        {"name": "get_order_record", "args": {"order_id": "ORD-88213"}},
        {"name": "get_billing_status", "args": {"customer_id": "CUST-001"}},
    ]
    update = await execute_tool(state)
    assert len(update["evidence"]) == 2
    assert {e.tool_name for e in update["evidence"]} == {"get_order_record", "get_billing_status"}
    assert update["iterations"] == 1
    assert update["pending_tool_calls"] == []


async def test_plan_next_action_with_fake_llm():
    fake_response = SimpleNamespace(
        tool_calls=[{"name": "get_order_record", "args": {"order_id": "ORD-88213"}, "id": "1"}]
    )
    plan_next_action = make_plan_next_action(
        "billing_crm", "the Billing/CRM specialist", FakeLLM(fake_response),
        {"get_order_record": _fake_get_order_record},
    )
    state = initial_specialist_state("ORD-88213")
    update = await plan_next_action(state)
    assert update["pending_tool_calls"] == [
        {"name": "get_order_record", "args": {"order_id": "ORD-88213"}}
    ]


async def test_evaluate_evidence_with_fake_llm():
    fake_assessment = SimpleNamespace(
        complete=True, preliminary_assessment="Billing looks clean, no hold."
    )
    evaluate_evidence = make_evaluate_evidence(
        "billing_crm", "the Billing/CRM specialist", FakeLLM(fake_assessment)
    )
    state = initial_specialist_state("ORD-88213")
    update = await evaluate_evidence(state)
    assert update["complete"] is True
    assert update["preliminary_assessment"] == "Billing looks clean, no hold."


# --- Full-stack test: real LLM, real tools, real mock services -----------
# Slower, but validates real wiring (Section 13), not just the decision
# logic already covered above.

async def test_network_specialist_full_stack_ord_88213():
    result = await network_graph.ainvoke(initial_specialist_state("ORD-88213"))

    tool_names_called = {e.tool_name for e in result["evidence"]}
    # 02-ARCHITECTURE.md Section 1's worked example: provisioning failed
    # with ERR_4471, and there's no circuit in inventory for the address.
    assert "get_provisioning_log" in tool_names_called
    assert "get_inventory_status" in tool_names_called

    provisioning_evidence = next(
        e for e in result["evidence"] if e.tool_name == "get_provisioning_log"
    )
    assert provisioning_evidence.data["error_code"] == "ERR_4471"

    assert result["preliminary_assessment"] != ""
