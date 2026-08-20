"""Billing/CRM specialist -- owns get_order_record, get_billing_status
(02-ARCHITECTURE.md Section 3.8: mirrors a telecom's account/billing
support team). Graph-wiring logic lives in agent/specialists/_shared.py,
shared with network.py.
"""
from agent.specialists._shared import build_specialist_graph
from agent.tools import get_billing_status, get_order_record

ROLE = "the Billing/CRM specialist on a telecom order-diagnosis team"

TOOLS = {
    "get_order_record": get_order_record,
    "get_billing_status": get_billing_status,
}

billing_crm_graph = build_specialist_graph("billing_crm", ROLE, TOOLS)
