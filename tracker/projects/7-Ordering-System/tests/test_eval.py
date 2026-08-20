from agent.state import DiagnosisOutput
from eval.judge import JudgeVerdict, judge_root_cause
from eval.metrics import (
    EvalResult,
    GoldenScenario,
    compute_metrics,
    evidence_citation_correctness,
    false_confidence_rate,
    format_report,
    insufficient_evidence_precision_recall,
    latency_percentiles,
    root_cause_accuracy,
    tool_call_efficiency_per_specialist,
)


class FakeLLM:
    """Same DI stand-in pattern as tests/test_specialists.py and
    tests/test_supervisor.py -- judge_root_cause is tested without a real
    API call."""

    def __init__(self, response):
        self._response = response

    def with_structured_output(self, schema):
        return self

    async def ainvoke(self, prompt):
        return self._response


async def test_judge_root_cause_passes_through_fake_verdict():
    fake_verdict = JudgeVerdict(passed=True, reasoning="Same underlying cause, different wording.")
    verdict = await judge_root_cause("no circuit assigned", "circuit missing", llm=FakeLLM(fake_verdict))
    assert verdict.passed is True
    assert verdict.reasoning == "Same underlying cause, different wording."


def _scenario(
    expected_root_cause="x", expected_insufficient_evidence=False,
    expected_evidence_tools=None,
) -> GoldenScenario:
    return GoldenScenario(
        scenario_id="s", order_id="ORD-1", archetype="a",
        expected_root_cause=expected_root_cause, expected_confidence_min="low",
        expected_evidence_tools=expected_evidence_tools or [],
        expected_insufficient_evidence=expected_insufficient_evidence,
    )


def _diagnosis(confidence="low", insufficient_evidence=True, evidence=None, root_cause="x") -> DiagnosisOutput:
    return DiagnosisOutput(
        root_cause=root_cause, confidence=confidence, evidence=evidence or [],
        recommended_action="a", insufficient_evidence=insufficient_evidence,
    )


def _result(scenario=None, diagnosis=None, tool_calls=None, judge_verdict=None, latency_ms=100.0) -> EvalResult:
    return EvalResult(
        scenario=scenario or _scenario(),
        diagnosis=diagnosis or _diagnosis(),
        correlation_id="c1",
        latency_ms=latency_ms,
        tool_calls=tool_calls or [],
        judge_verdict=judge_verdict,
    )


# --- root_cause_accuracy ---------------------------------------------------

def test_root_cause_accuracy_ignores_ungraded_scenarios():
    results = [
        _result(judge_verdict=JudgeVerdict(passed=True, reasoning="ok")),
        _result(judge_verdict=JudgeVerdict(passed=False, reasoning="wrong")),
        _result(judge_verdict=None),  # e.g. an insufficient_evidence scenario -- nothing to grade
    ]
    assert root_cause_accuracy(results) == 0.5


def test_root_cause_accuracy_none_when_nothing_gradable():
    assert root_cause_accuracy([_result(judge_verdict=None)]) is None


# --- evidence_citation_correctness -----------------------------------------

def test_evidence_citation_correctness_empty_results():
    assert evidence_citation_correctness([]) == 0.0


def test_evidence_citation_correctness_grounded_and_ungrounded():
    grounded = _result(
        diagnosis=_diagnosis(evidence=["found a problem"]),
        tool_calls=[{"event": "tool_call", "success": True, "tool_name": "get_order_record"}],
    )
    ungrounded = _result(
        diagnosis=_diagnosis(evidence=["found a problem"]),
        tool_calls=[],  # cites evidence but no tool call actually happened
    )
    no_claim = _result(diagnosis=_diagnosis(evidence=[]), tool_calls=[])  # nothing cited -- trivially fine
    assert evidence_citation_correctness([grounded, ungrounded, no_claim]) == 2 / 3


# --- false_confidence_rate --------------------------------------------------

def test_false_confidence_rate_only_counts_incorrect_high_confidence():
    correct = _result(
        judge_verdict=JudgeVerdict(passed=True, reasoning="ok"),
        diagnosis=_diagnosis(confidence="high", insufficient_evidence=False),
    )
    incorrect_high = _result(
        judge_verdict=JudgeVerdict(passed=False, reasoning="no"),
        diagnosis=_diagnosis(confidence="high", insufficient_evidence=False),
    )
    incorrect_low = _result(
        judge_verdict=JudgeVerdict(passed=False, reasoning="no"),
        diagnosis=_diagnosis(confidence="low", insufficient_evidence=False),
    )
    assert false_confidence_rate([correct, incorrect_high, incorrect_low]) == 0.5


def test_false_confidence_rate_counts_missed_insufficient_evidence_as_incorrect():
    missed = _result(
        scenario=_scenario(expected_insufficient_evidence=True),
        diagnosis=_diagnosis(confidence="high", insufficient_evidence=False),  # fabricated a confident answer
    )
    assert false_confidence_rate([missed]) == 1.0


def test_false_confidence_rate_zero_when_nothing_incorrect():
    assert false_confidence_rate([_result(judge_verdict=JudgeVerdict(passed=True, reasoning="ok"))]) == 0.0


# --- insufficient_evidence_precision_recall --------------------------------

def test_insufficient_evidence_precision_and_recall():
    true_positive = _result(
        scenario=_scenario(expected_insufficient_evidence=True),
        diagnosis=_diagnosis(insufficient_evidence=True),
    )
    false_negative = _result(
        scenario=_scenario(expected_insufficient_evidence=True),
        diagnosis=_diagnosis(insufficient_evidence=False),
    )
    false_positive = _result(
        scenario=_scenario(expected_insufficient_evidence=False),
        diagnosis=_diagnosis(insufficient_evidence=True),
    )
    true_negative = _result(
        scenario=_scenario(expected_insufficient_evidence=False),
        diagnosis=_diagnosis(insufficient_evidence=False),
    )
    precision, recall = insufficient_evidence_precision_recall(
        [true_positive, false_negative, false_positive, true_negative]
    )
    assert recall == 0.5  # 1 true positive out of 2 actual positives
    assert precision == 0.5  # 1 true positive out of 2 flagged (1 TP + 1 FP)


# --- tool_call_efficiency_per_specialist ------------------------------------

def test_tool_call_efficiency_splits_by_specialist():
    result = _result(
        scenario=_scenario(expected_evidence_tools=["get_order_record", "get_provisioning_log"]),
        tool_calls=[
            {"event": "tool_call", "tool_name": "get_order_record"},
            {"event": "tool_call", "tool_name": "get_billing_status"},
            {"event": "tool_call", "tool_name": "get_provisioning_log"},
        ],
    )
    report = tool_call_efficiency_per_specialist([result])
    assert report["billing_crm"]["avg_actual_calls"] == 2.0  # order_record + billing_status
    assert report["billing_crm"]["avg_expected_calls"] == 1.0  # only order_record was expected
    assert report["network"]["avg_actual_calls"] == 1.0
    assert report["network"]["avg_expected_calls"] == 1.0


# --- latency_percentiles -----------------------------------------------------

def test_latency_percentiles():
    results = [_result(latency_ms=ms) for ms in [100, 200, 300, 400, 500]]
    percentiles = latency_percentiles(results)
    assert percentiles["p50"] == 300
    assert percentiles["p95"] == 500


def test_latency_percentiles_empty():
    assert latency_percentiles([]) == {"p50": None, "p95": None}


# --- compute_metrics / format_report (smoke test) ---------------------------

def test_compute_metrics_and_format_report_smoke_test():
    results = [
        _result(judge_verdict=JudgeVerdict(passed=True, reasoning="ok")),
        _result(
            scenario=_scenario(expected_insufficient_evidence=True),
            diagnosis=_diagnosis(insufficient_evidence=True),
        ),
    ]
    report = compute_metrics(results)
    assert report.total_scenarios == 2
    text = format_report(report)
    assert "Evaluation Report" in text
    assert "Scenarios run: 2" in text


def test_format_report_handles_no_latency_data():
    report = compute_metrics([])
    text = format_report(report)
    assert "Latency: n/a" in text
