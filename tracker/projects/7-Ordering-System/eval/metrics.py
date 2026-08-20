"""Computes the 6 metrics from 03-EVALUATION.md Section 2, from a batch of
(scenario, actual_result) pairs. Every function below is pure -- no LLM
calls, no network calls -- so each is directly unit-testable against
hand-crafted `EvalResult` objects (02-ARCHITECTURE.md Section 13's "fast,
isolated" testing discipline, applied to the eval harness itself, not just
the agent). The one genuinely non-deterministic input (the LLM-as-judge
verdict, `eval/judge.py`) is computed once per scenario by `run_eval.py`
and passed in already-resolved -- these functions never call the judge
themselves.
"""
from statistics import mean

from pydantic import BaseModel

from agent.state import DiagnosisOutput
from eval.judge import JudgeVerdict

# Owned-by mapping mirrors 02-ARCHITECTURE.md Section 3.8's domain split --
# needed to measure tool-call efficiency *per specialist*, not flat across
# all 5 tools (Section 2's stated reason: a flat count would hide which
# specialist is actually inefficient).
_SPECIALIST_TOOLS = {
    "billing_crm": {"get_order_record", "get_billing_status"},
    "network": {"get_provisioning_log", "get_inventory_status", "search_knowledge_base"},
}


class GoldenScenario(BaseModel):
    scenario_id: str
    order_id: str
    archetype: str
    expected_root_cause: str | None
    expected_confidence_min: str
    expected_evidence_tools: list[str]
    expected_insufficient_evidence: bool


class EvalResult(BaseModel):
    scenario: GoldenScenario
    diagnosis: DiagnosisOutput
    correlation_id: str
    latency_ms: float
    tool_calls: list[dict]  # this scenario's "tool_call" log lines (agent/observability.py)
    judge_verdict: JudgeVerdict | None  # None when expected_root_cause is None -- nothing to grade


def root_cause_accuracy(results: list[EvalResult]) -> float | None:
    graded = [r for r in results if r.judge_verdict is not None]
    if not graded:
        return None
    return sum(1 for r in graded if r.judge_verdict.passed) / len(graded)


def evidence_citation_correctness(results: list[EvalResult]) -> float:
    # Does every cited `evidence` entry correspond to a tool call that
    # actually happened, not a fabricated reference? DiagnosisOutput.evidence
    # holds prose summaries (agent/supervisor.py's SpecialistReading.summary),
    # not literal tool-call IDs, so this checks the honest, checkable version
    # of that question: if the diagnosis cites evidence at all, at least one
    # real, successful tool call exists in this request's trace to back it.
    def is_grounded(r: EvalResult) -> bool:
        if not r.diagnosis.evidence:
            return True
        return any(
            tc.get("event") == "tool_call" and tc.get("success") for tc in r.tool_calls
        )

    if not results:
        return 0.0
    return sum(1 for r in results if is_grounded(r)) / len(results)


def false_confidence_rate(results: list[EvalResult]) -> float:
    # % of *incorrect* diagnoses reported with confidence="high". A
    # diagnosis is "incorrect" if the judge failed it, or if the scenario
    # expected insufficient_evidence and the agent didn't report it (a
    # fabricated-confidence failure in its own right, not just a missed
    # judge grade).
    incorrect = [
        r for r in results
        if (r.judge_verdict is not None and not r.judge_verdict.passed)
        or (r.scenario.expected_insufficient_evidence and not r.diagnosis.insufficient_evidence)
    ]
    if not incorrect:
        return 0.0
    return sum(1 for r in incorrect if r.diagnosis.confidence == "high") / len(incorrect)


def insufficient_evidence_precision_recall(
    results: list[EvalResult],
) -> tuple[float | None, float | None]:
    positives = [r for r in results if r.scenario.expected_insufficient_evidence]
    negatives = [r for r in results if not r.scenario.expected_insufficient_evidence]

    true_positives = sum(1 for r in positives if r.diagnosis.insufficient_evidence)
    false_positives = sum(1 for r in negatives if r.diagnosis.insufficient_evidence)

    recall = (true_positives / len(positives)) if positives else None
    denom = true_positives + false_positives
    precision = (true_positives / denom) if denom else None
    return precision, recall


def tool_call_efficiency_per_specialist(results: list[EvalResult]) -> dict:
    report = {}
    for specialist, owned in _SPECIALIST_TOOLS.items():
        actual_counts, expected_counts = [], []
        for r in results:
            actual_counts.append(sum(
                1 for tc in r.tool_calls
                if tc.get("event") == "tool_call" and tc.get("tool_name") in owned
            ))
            expected_counts.append(sum(1 for t in r.scenario.expected_evidence_tools if t in owned))
        report[specialist] = {
            "avg_actual_calls": mean(actual_counts) if actual_counts else 0.0,
            "avg_expected_calls": mean(expected_counts) if expected_counts else 0.0,
        }
    return report


def latency_percentiles(results: list[EvalResult]) -> dict:
    latencies = sorted(r.latency_ms for r in results)
    if not latencies:
        return {"p50": None, "p95": None}

    def pct(p: float) -> float:
        idx = min(len(latencies) - 1, int(len(latencies) * p))
        return latencies[idx]

    return {"p50": pct(0.5), "p95": pct(0.95)}


class MetricsReport(BaseModel):
    total_scenarios: int
    root_cause_accuracy: float | None
    evidence_citation_correctness: float
    false_confidence_rate: float
    insufficient_evidence_precision: float | None
    insufficient_evidence_recall: float | None
    tool_call_efficiency: dict
    latency_p50_ms: float | None
    latency_p95_ms: float | None


def compute_metrics(results: list[EvalResult]) -> MetricsReport:
    precision, recall = insufficient_evidence_precision_recall(results)
    latency = latency_percentiles(results)
    return MetricsReport(
        total_scenarios=len(results),
        root_cause_accuracy=root_cause_accuracy(results),
        evidence_citation_correctness=evidence_citation_correctness(results),
        false_confidence_rate=false_confidence_rate(results),
        insufficient_evidence_precision=precision,
        insufficient_evidence_recall=recall,
        tool_call_efficiency=tool_call_efficiency_per_specialist(results),
        latency_p50_ms=latency["p50"],
        latency_p95_ms=latency["p95"],
    )


def _pct(value: float | None) -> str:
    return f"{value:.0%}" if value is not None else "n/a"


def format_report(report: MetricsReport) -> str:
    lines = [
        "=== Order Diagnosis Agent -- Evaluation Report ===",
        f"Scenarios run: {report.total_scenarios}",
        f"Root cause accuracy (LLM-as-judge): {_pct(report.root_cause_accuracy)}",
        f"Evidence citation correctness: {_pct(report.evidence_citation_correctness)}",
        f"False-confidence rate: {_pct(report.false_confidence_rate)}",
        f"Insufficient-evidence precision: {_pct(report.insufficient_evidence_precision)}",
        f"Insufficient-evidence recall: {_pct(report.insufficient_evidence_recall)}",
        "Tool-call efficiency (avg calls per specialist, actual vs. expected):",
    ]
    for specialist, stats in report.tool_call_efficiency.items():
        lines.append(
            f"  {specialist}: actual={stats['avg_actual_calls']:.1f}, "
            f"expected={stats['avg_expected_calls']:.1f}"
        )
    if report.latency_p50_ms is not None:
        lines.append(
            f"Latency: p50={report.latency_p50_ms:.0f}ms, p95={report.latency_p95_ms:.0f}ms"
        )
    else:
        lines.append("Latency: n/a")
    return "\n".join(lines)
