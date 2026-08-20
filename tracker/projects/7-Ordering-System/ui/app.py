"""Streamlit demo -- 04-BUILD-PLAN.md Phase 7, resolving 01-REQUIREMENTS.md
Section 8's last open question: this UI shows the agent's reasoning
step-by-step live, not just the final diagnosis. Now that Phase 5's
structured logging and Phase 6's X-Correlation-Id response header both
exist, doing so is a straightforward read of an already-built trace, not
new engineering -- exactly the "call it once the actual effort is clear"
timing that question asked for. It's also the more compelling demo for a
coworker: the point of this whole project is the multi-agent
investigation, not just the final answer.

Run with `streamlit run ui/app.py`. Requires the 4 mock services and
`api/main.py` already running as real processes (same precondition as
Phase 5/6's manual verification) -- this is a client of that running
system, not a replacement for it.
"""
import json
import os

import httpx
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

_API_BASE_URL = os.environ.get("UI_API_BASE_URL", "http://localhost:8000")

_CONFIDENCE_COLOR = {"high": "green", "medium": "orange", "low": "red"}

st.set_page_config(page_title="Order Diagnosis Agent", page_icon="🔍")

st.title("🔍 Order Diagnosis Agent")
st.caption(
    "A multi-agent system that diagnoses why a telecom order is stuck by "
    "querying CRM, Billing, Provisioning, and Inventory -- all realistic "
    "**mock services with synthetic data**, not a real telecom's systems "
    "(see this project's README for the full honesty boundary)."
)

order_id = st.text_input("Order ID", value="ORD-88213")
show_trace = st.checkbox("Show step-by-step agent trace", value=True)
submitted = st.button("Diagnose", type="primary")


def _load_trace(correlation_id: str) -> list[dict]:
    log_path = os.environ.get("LOG_FILE_PATH", "./agent_events.jsonl")
    if not os.path.exists(log_path):
        return []
    events = []
    with open(log_path) as f:
        for line in f:
            record = json.loads(line)
            if record.get("correlation_id") == correlation_id:
                events.append(record)
    return events


def _render_trace(events: list[dict]) -> None:
    if not events:
        st.info("No trace found for this request (log file not available).")
        return
    for event in events:
        if event["event"] == "node_start":
            st.markdown(f"▶️ **{event['node']}** started")
        elif event["event"] == "node_end":
            st.markdown(f"&nbsp;&nbsp;✅ finished in {event['duration_ms']:.0f}ms")
        elif event["event"] == "tool_call":
            icon = "✅" if event["success"] else "⚠️"
            detail = f" — {event['error']}" if event.get("error") else ""
            st.markdown(
                f"&nbsp;&nbsp;{icon} tool call `{event['tool_name']}` "
                f"({event['latency_ms']:.0f}ms){detail}"
            )


def _render_diagnosis(diagnosis: dict) -> None:
    if diagnosis["insufficient_evidence"]:
        st.warning("⚠️ **Insufficient evidence** to confidently diagnose this order.")

    color = _CONFIDENCE_COLOR.get(diagnosis["confidence"], "gray")
    st.markdown(f"**Confidence:** :{color}[{diagnosis['confidence'].upper()}]")
    st.subheader("Root cause")
    st.write(diagnosis["root_cause"])
    st.subheader("Evidence")
    # One st.markdown call for the whole list -- each call renders as its
    # own isolated block, so looping st.markdown per item produced several
    # separate single-item lists instead of one bulleted list.
    st.markdown("\n".join(f"- {item}" for item in diagnosis["evidence"]))
    st.subheader("Recommended action")
    st.write(diagnosis["recommended_action"])


if submitted:
    api_key = os.environ.get("API_KEY", "")
    with st.spinner("Dispatching Billing/CRM and Network specialists..."):
        try:
            response = httpx.post(
                f"{_API_BASE_URL}/diagnose",
                json={"order_id": order_id},
                headers={"X-API-Key": api_key},
                timeout=60.0,
            )
        except httpx.ConnectError:
            st.error(
                "Could not reach the API. Make sure the 4 mock services and "
                "`api/main.py` are running as real processes first "
                "(see 05-DEVELOPMENT-LOG.md's Phase 5 entry for the exact commands)."
            )
            st.stop()

    if response.status_code == 401:
        st.error("Invalid or missing API key -- check API_KEY in .env.")
    elif response.status_code == 429:
        st.error("Rate limit exceeded (10 requests/minute per API key) -- wait a moment and try again.")
    elif response.status_code != 200:
        st.error(f"Request failed: {response.status_code} — {response.text}")
    else:
        diagnosis = response.json()
        correlation_id = response.headers.get("X-Correlation-Id")

        if show_trace and correlation_id:
            st.subheader("Agent trace")
            _render_trace(_load_trace(correlation_id))
            st.divider()

        _render_diagnosis(diagnosis)
