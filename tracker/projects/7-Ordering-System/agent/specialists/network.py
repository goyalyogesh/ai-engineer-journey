"""Network specialist -- owns get_provisioning_log, get_inventory_status,
search_knowledge_base (02-ARCHITECTURE.md Section 3.8: mirrors a telecom's
NOC/network operations team). Graph-wiring logic lives in
agent/specialists/_shared.py, shared with billing_crm.py.
"""
from agent.specialists._shared import build_specialist_graph
from agent.tools import (
    get_inventory_status,
    get_provisioning_log,
    search_knowledge_base,
)

ROLE = "the Network specialist on a telecom order-diagnosis team"

TOOLS = {
    "get_provisioning_log": get_provisioning_log,
    "get_inventory_status": get_inventory_status,
    "search_knowledge_base": search_knowledge_base,
}

network_graph = build_specialist_graph("network", ROLE, TOOLS)
