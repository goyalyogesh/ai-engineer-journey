# Evaluation — Order Diagnosis Agent

**Status:** Draft v1 — for discussion, not final. Depends on
[`01-REQUIREMENTS.md`](01-REQUIREMENTS.md) and [`02-ARCHITECTURE.md`](02-ARCHITECTURE.md).

## Why this exists as its own document

FR6 ("must say 'insufficient evidence' rather than fabricate a root cause")
and the non-functional requirement around explainability are only real
requirements if something actually checks them. An agent that "seems to work"
in a few manual tries isn't evidence of anything — this is the harness that
makes the claims in the requirements doc checkable.

## 1. Golden dataset

A hand-built set of synthetic stuck-order scenarios, each with a
**known, designed-in ground truth** — since there's no real production data,
correctness is defined by what the scenario was built to test, not an
external label source.

### Failure archetypes to cover (answers requirements doc's open question)

| Archetype | Example | Tests |
|---|---|---|
| Provisioning failure, known error code | `ERR_4471` — missing circuit assignment | KB lookup (vector) correctly resolves the code |
| Provisioning failure, *unknown* error code | A code intentionally absent from the KB | FR6 — must report insufficient evidence, not guess |
| Billing hold, no provisioning issue | Payment declined, provisioning never started | Agent correctly attributes the failure to the billing hold rather than being confused by the Network specialist's benign "not_started" finding — note: the Network specialist still runs by default in Core (`02-ARCHITECTURE.md` Section 3.8's "engage both" decision), so this tests correct *attribution*, not selective specialist skipping (that's Extended-tier) |
| Inventory/address mismatch | Circuit exists but at the wrong address | Multi-hop reasoning across Provisioning → Inventory → the graph layer |
| Multiple plausible causes | Both a billing hold *and* a provisioning error present, both genuinely true (not contradictory) | Tests `02-ARCHITECTURE.md` Section 3.7's pipeline-order rule — expects `root_cause` to name the billing hold (earlier in `CRM → Billing → Provisioning → Inventory`), with the provisioning error still present in `evidence` |
| Clean order, no failure | Order fully succeeded | Agent correctly reports "no issue found" instead of manufacturing a problem |
| Conflicting evidence | Two systems disagree (e.g., Billing shows no hold, but a provisioning error code implies a billing cause) | Tests `02-ARCHITECTURE.md` Section 3.7's precedence rule and conflict-surfacing requirement — added after review, not part of the original set |

Target: ~3-4 scenarios per archetype, ~20-25 total (7 archetypes now, after
adding "conflicting evidence") — enough to catch systematic failure modes
without needing hundreds of hand-built cases.

**Corrected during actual Phase 6 implementation, worth being explicit
about:** the "conflicting evidence" archetype's golden-dataset entries
originally expected `insufficient_evidence=True` (04-BUILD-PLAN.md
Phase 6's own example). That's wrong for *this* archetype's specific
shape (a technical system's finding vs. an administrative system's clean
record, e.g. `ERR_BILL_MISMATCH`) — Section 3.7's precedence rule exists
specifically to *resolve* exactly this kind of conflict (technical beats
administrative), not to trigger `insufficient_evidence`. That fallback is
reserved for conflicts the precedence rule *can't* resolve (e.g. two
technical systems disagreeing with each other — covered by
`agent/supervisor.py`'s own unit tests, `test_unresolvable_conflict_between_two_technical_readings`,
but not currently a separate golden-dataset archetype). The golden
dataset's 3 `conflicting_evidence` scenarios now expect a *resolved*,
medium-confidence diagnosis favoring the technical (Network) specialist's
finding, matching `agent/supervisor.py`'s actual, already-unit-tested
behavior (`test_conflict_resolved_by_technical_precedence`,
`05-DEVELOPMENT-LOG.md`'s Phase 4 entry) — not the stale planning-time
example.

### Scenario schema

```python
class GoldenScenario(BaseModel):
    scenario_id: str
    order_id: str                  # seeded into the mock services
    archetype: str
    expected_root_cause: str | None  # None for scenarios where the correct
                                      # outcome IS insufficient_evidence=True —
                                      # there's no "expected root cause" to
                                      # grade against in that case (see
                                      # 04-BUILD-PLAN.md Phase 6's examples)
    expected_confidence_min: str   # compared via CONFIDENCE_ORDER
                                    # (02-ARCHITECTURE.md Section 3.4),
                                    # not string equality
    expected_evidence_tools: list[str]        # which tools SHOULD have been called
    expected_insufficient_evidence: bool      # mirrors DiagnosisOutput.insufficient_evidence
                                               # by name, deliberately — makes the
                                               # pass condition a direct field
                                               # comparison, not a renamed lookup
```

## 2. Metrics

| Metric | How it's measured | Why it matters |
|---|---|---|
| **Root cause accuracy** | LLM-as-judge: does the agent's `root_cause` match `expected_root_cause` in substance (not exact string match)? | The core correctness question |
| **Evidence citation correctness** | Does every item in `evidence` correspond to a tool call that actually happened (from the audit log), not a fabricated reference? | Catches the specific failure mode of citing evidence that doesn't exist — worse than no citation at all |
| **False-confidence rate** | % of *incorrect* diagnoses that were reported with `confidence: high` | The single most important enterprise metric here — a wrong answer stated with unwarranted confidence is more dangerous than the same wrong answer stated as uncertain |
| **Insufficient-evidence precision/recall** | Of the scenarios designed to require "insufficient evidence" (FR6), what fraction correctly triggered it? Of the scenarios that *shouldn't* trigger it, what fraction incorrectly did? | Directly tests FR6, in both directions — over-triggering "I don't know" is also a real failure mode |
| **Tool-call efficiency** | Number of tool calls **per specialist** vs. the minimum needed (measured separately for Billing/CRM and Network — `02-ARCHITECTURE.md` Section 3.8) | A specialist that calls both/all of its tools every time regardless of need is wasteful, even if the final diagnosis is right — measuring this flat across all 5 tools would hide which specialist is actually inefficient |
| **Latency** | Wall-clock time per diagnosis, p50/p95 | Against the sub-10-second budget from the requirements doc's NFRs |

## 3. LLM-as-judge grading

For "root cause accuracy" specifically — since `expected_root_cause` is a
sentence, not an exact value, grading needs a judge, not a string match:

```
Given:
- The scenario's expected root cause: {expected_root_cause}
- The agent's actual diagnosis: {actual_root_cause}

Question: does the agent's diagnosis identify the same underlying root cause,
even if worded differently? Answer PASS or FAIL, with one sentence of reasoning.
```

Run with a model separate from (or at minimum, a separate call from) the
agent's own reasoning — grading your own homework with the identical context
window is a real bias risk worth naming, not ignoring.

## 4. Regression testing

The golden set is a **regression suite**, not a one-time check — re-run it
whenever:
- A prompt inside `plan_next_action` / `evaluate_evidence` / `synthesize_diagnosis` changes
- A new tool is added (does the agent now over-call it, or correctly ignore it when irrelevant?)
- The underlying model changes (e.g. testing a Bedrock-hosted Claude version
  bump before rolling it out)

This is what Section 10 of the architecture doc means by "CI/CD with
eval-gated deploys" — named there as an infra concern out of scope to build,
but the *eval suite itself* (this document) is what such a pipeline would
actually run. Building the harness now means that gate is a real option
later, not a rewrite.

## 5. What this evaluation approach deliberately does NOT claim

Consistent with the honesty principle already established for this project:
these are **synthetic scenarios against synthetic data** — a good regression
signal for catching agent logic bugs and prompt regressions, not a claim of
measured production accuracy. Framed exactly that way in any interview
discussion of this project: "here's how I evaluated it," not "here's my
production accuracy number."
