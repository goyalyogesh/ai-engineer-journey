"""Core-tier structured logging (02-ARCHITECTURE.md Section 12: "Local
JSON Lines file"). The full 3-part observability stack -- OpenTelemetry
tracing and Prometheus metrics -- is [EXTENDED] (Section 7); this module
is only the piece Phase 5's Definition of Done actually requires: one JSON
log line per tool call and per graph node transition, every line carrying
a `correlation_id` so a single `grep` reconstructs the full trace of one
`/diagnose` request across every specialist and every tool call.

Threading `correlation_id` through a `contextvars.ContextVar`, instead of
adding a `correlation_id` parameter to every tool/node function, is
deliberate -- it lets Phase 5 add request-scoped logging without touching
the signatures of the already-built, already-tested Phase 2-4 functions.
"""
import contextvars
import json
import os
import time
from functools import wraps

correlation_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "correlation_id", default=None
)


def _log_path() -> str:
    # Read fresh per call, not cached -- same reasoning as
    # mock_services/*/main.py's env-var handling (Phase 1): tests need to
    # redirect this via monkeypatch/env override without import-order
    # surprises.
    return os.environ.get("LOG_FILE_PATH", "./agent_events.jsonl")


def log_event(event: str, **fields) -> None:
    # Deliberately simple synchronous file I/O -- a production system
    # would use async file I/O or a log shipper (Section 12 names
    # CloudWatch/Loki/Elasticsearch as the Extended-tier answer); at this
    # project's scale, a blocking append is not a real bottleneck and
    # isn't worth the extra dependency/complexity here.
    record = {
        "timestamp": time.time(),
        "correlation_id": correlation_id_var.get(),
        "event": event,
        **fields,
    }
    with open(_log_path(), "a") as f:
        f.write(json.dumps(record, default=str) + "\n")


def log_node_transitions(node_name: str):
    """Decorator for a LangGraph node function -- logs its start/end so
    every node transition shows up in the structured log without changing
    the node's own logic (Phase 5's "per graph node transition"
    requirement, applied to the already-built Phase 3/4 node factories)."""

    def decorator(fn):
        @wraps(fn)
        async def wrapper(state):
            log_event("node_start", node=node_name)
            start = time.monotonic()
            result = await fn(state)
            log_event(
                "node_end", node=node_name,
                duration_ms=(time.monotonic() - start) * 1000,
            )
            return result

        return wrapper

    return decorator
