"""Orchestrates the golden-dataset evaluation run (04-BUILD-PLAN.md
Phase 6's Definition of Done): seeds every scenario's order_id into the
Phase 1 mock DBs, calls the real POST /diagnose endpoint per scenario,
judges root-cause accuracy, and prints a metrics report.

Preconditions (same as Phase 5's manual curl verification): the 4 mock
services and the FastAPI app must already be running as real processes
(`uvicorn mock_services.<name>.main:app --port 800X` x4, plus
`uvicorn api.main:app --port 8000`) -- this script is a client of that
running system, not a replacement for it.
"""
import asyncio
import json
import os
import sys
import time

import httpx
from dotenv import load_dotenv

from eval.judge import judge_root_cause
from eval.metrics import EvalResult, GoldenScenario, compute_metrics, format_report

load_dotenv()

_API_BASE_URL = os.environ.get("EVAL_API_BASE_URL", "http://localhost:8000")
_GOLDEN_DATASET_PATH = os.path.join(os.path.dirname(__file__), "golden_dataset.json")


def _reseed_mock_services() -> None:
    # 04-BUILD-PLAN.md Phase 6: "seed each scenario's order_id into Phase 1's
    # DBs (idempotently)". The mock services already seed themselves on
    # their own FastAPI startup (Phase 1's lifespan hook), so this is a
    # belt-and-suspenders re-seed -- cheap, idempotent (INSERT OR REPLACE),
    # and makes this script self-contained rather than silently depending on
    # whoever started the services having done it already.
    from mock_services.billing.seed_data import seed as seed_billing
    from mock_services.crm.seed_data import seed as seed_crm
    from mock_services.inventory.seed_data import seed as seed_inventory
    from mock_services.provisioning.seed_data import seed as seed_provisioning

    seed_crm()
    seed_billing()
    seed_provisioning()
    seed_inventory()


def _load_golden_dataset() -> list[GoldenScenario]:
    with open(_GOLDEN_DATASET_PATH) as f:
        raw = json.load(f)
    return [GoldenScenario(**entry) for entry in raw]


async def _diagnose_with_retry(client: httpx.AsyncClient, order_id: str) -> tuple[dict, str, float]:
    # The eval harness is itself a legitimate high-volume caller of
    # /diagnose's own rate limiter (Phase 5, 10 req/min per API key) --
    # a real interaction worth handling, not ignoring. Waits out a 429
    # rather than treating it as a scenario failure.
    while True:
        start = time.monotonic()
        response = await client.post(
            f"{_API_BASE_URL}/diagnose",
            json={"order_id": order_id},
            headers={"X-API-Key": os.environ["API_KEY"]},
            timeout=60.0,
        )
        latency_ms = (time.monotonic() - start) * 1000
        if response.status_code == 429:
            await asyncio.sleep(6.0)
            continue
        response.raise_for_status()
        return response.json(), response.headers["X-Correlation-Id"], latency_ms


def _tool_calls_for(correlation_id: str) -> list[dict]:
    log_path = os.environ.get("LOG_FILE_PATH", "./agent_events.jsonl")
    if not os.path.exists(log_path):
        return []
    calls = []
    with open(log_path) as f:
        for line in f:
            record = json.loads(line)
            if record.get("correlation_id") == correlation_id and record.get("event") == "tool_call":
                calls.append(record)
    return calls


async def run() -> list[EvalResult]:
    _reseed_mock_services()
    scenarios = _load_golden_dataset()
    results = []

    async with httpx.AsyncClient() as client:
        for i, scenario in enumerate(scenarios, start=1):
            print(f"[{i}/{len(scenarios)}] {scenario.scenario_id} ({scenario.order_id})...", flush=True)
            diagnosis_dict, correlation_id, latency_ms = await _diagnose_with_retry(
                client, scenario.order_id
            )
            tool_calls = _tool_calls_for(correlation_id)

            judge_verdict = None
            if scenario.expected_root_cause is not None:
                judge_verdict = await judge_root_cause(
                    scenario.expected_root_cause, diagnosis_dict["root_cause"]
                )

            from agent.state import DiagnosisOutput

            results.append(EvalResult(
                scenario=scenario,
                diagnosis=DiagnosisOutput(**diagnosis_dict),
                correlation_id=correlation_id,
                latency_ms=latency_ms,
                tool_calls=tool_calls,
                judge_verdict=judge_verdict,
            ))

    return results


def main() -> None:
    results = asyncio.run(run())
    report = compute_metrics(results)
    print()
    print(format_report(report))


if __name__ == "__main__":
    sys.exit(main() or 0)
