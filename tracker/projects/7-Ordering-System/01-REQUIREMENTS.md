# Requirements — Order Diagnosis Agent

**Status:** Draft v1 — for discussion, not final.

## 1. Problem statement

At a large telecom, activating or modifying a customer's service (new fiber
connection, plan change, line move) touches several independent backend
systems — typically something like:

- **CRM** — customer account state, order record, service history
- **Billing** — payment/plan status, billing holds
- **Provisioning** — network activation status, provisioning error codes
- **Network Inventory** — physical/logical resource assignment (circuits,
  ports, addresses)

None of these systems has the full picture on its own. When an order gets
stuck or fails, a support engineer or NOC analyst has to manually query each
system, correlate results by order ID/customer ID/timestamp (which often
don't share a clean common key), and reason about *where in the chain*
something broke. This is:

- **Slow** — minutes to hours per incident, entirely manual
- **Inconsistent** — diagnosis quality depends on which engineer is on shift
  and how much tribal knowledge they've built up
- **Not scalable** — every new engineer needs months of exposure before they
  can do this well independently

## 2. Goal

Build an agent that, given an order ID, **autonomously**:
1. Decides which backend systems to query (not a fixed, hardcoded sequence —
   a provisioning failure needs different evidence than a billing hold)
2. Retrieves and correlates state across those systems
3. When it hits an error code it doesn't recognize, looks it up against an
   internal knowledge base (RAG) instead of guessing
4. Produces a structured, cited root-cause hypothesis + recommended next
   action — not a wall of prose

Target outcome: first-pass diagnosis in seconds instead of manual cross-system
lookup, with output that's consistent and auditable regardless of who (or
what) triggered it.

## 3. Personas

| Persona | Need |
|---|---|
| NOC / Support Engineer | Fast, trustworthy first-pass diagnosis before escalating or acting |
| Engineering Manager / Coworker (real audience for this project) | Wants to see the architecture and reasoning process, not just a final answer |

## 4. Scope

### In scope (v1)
- Single-order diagnosis, one order ID per invocation
- Read-only investigation across 4 mock backend systems + 1 knowledge base
- Structured, cited diagnostic output
- Full audit trail of every tool call the agent makes

### Explicitly out of scope (v1) — and why

- **No corrective action.** The agent never writes to any system (no
  auto-retry, no auto-refund, no re-provisioning). It produces a diagnosis +
  recommendation for a human to act on. This is a deliberate constraint, not
  a missing feature — no real enterprise ships an agent with write access to
  billing/provisioning without a much larger safety/approval design than a
  portfolio project can responsibly cover.
- **No real system integration.** All 4 backend systems are realistic mock
  services with synthetic data, built for this project. There is no access
  to, and no claim of access to, any real telecom's actual systems.
- **No batch/bulk scanning.** Diagnoses one order at a time; scanning all
  currently-stuck orders across the platform is a natural v2, not v1.
- **No live-alerting/NOC-integration.** This is an on-demand diagnostic tool
  (call it with an order ID), not a monitoring system that watches for
  failures proactively.

## 5. Functional requirements

| ID | Requirement |
|---|---|
| FR1 | Given an order ID, the agent decides which systems to query — not a fixed script. A billing-hold scenario and a provisioning-failure scenario should result in different tool-call sequences. |
| FR2 | The agent correlates evidence across systems that don't share a clean common key (e.g., CRM keys on `customer_id`, provisioning keys on `circuit_id` — `order_id` is the join key it has to carry through). |
| FR3 | When a tool returns an error code the agent doesn't already understand, it must query the knowledge base (RAG) for documented meaning/resolution before finalizing a diagnosis — it may not guess what an internal error code means. |
| FR4 | Final output is a structured object: `root_cause`, `confidence`, `evidence` (list of which tool call / doc supported the conclusion), `recommended_action` — not unstructured prose. |
| FR5 | Every tool call is logged: which system, what was queried, what was returned, timestamp — full audit trail. |
| FR6 | If the gathered evidence is insufficient for a confident diagnosis, the agent must say so explicitly rather than fabricate a root cause. (Same principle already proven live in `16Langchain-Core.ipynb`'s "context does not contain the answer" result — carried forward as a hard requirement here, not an accident.) |
| FR7 | The agent must be triggerable both synchronously (on-demand via API) and asynchronously (automatically, on a `provisioning_failed`/`billing_hold_applied` event) — through the same underlying agent core, not two separate implementations. See `02-ARCHITECTURE.md` Section 4. |
| FR8 | The knowledge base lookup must combine vector similarity search (what does this error generally mean) with graph relationship traversal (what specific resolution path and related past incidents does it connect to) — see `02-ARCHITECTURE.md` Section 5. |
| FR9 | When evidence from two systems conflicts, the agent must explicitly surface the conflict rather than silently picking a side, and fall back to `insufficient_evidence=True` if the conflict can't be resolved by the stated precedence rule — see `02-ARCHITECTURE.md` Section 3.7. |
| FR10 | When two systems report independently *true* (non-contradictory) problems at once, the agent must report the one earliest in the `CRM → Billing → Provisioning → Inventory` pipeline as `root_cause`, while still including every genuinely-true finding in `evidence` — not a conflict-resolution case (FR9), a distinct priority rule — see `02-ARCHITECTURE.md` Section 3.7. |

## 6. Non-functional requirements

These are what separate this from a toy demo — an interviewer will ask about
these, so they're requirements, not afterthoughts.

| Requirement | Why it matters here |
|---|---|
| **Auditability** | Every agent decision and tool call must be traceable end-to-end — regulated industries (telecom) can't accept black-box diagnoses |
| **Grounded structure over free text** | Tool outputs are Pydantic-validated, not loosely parsed strings — the agent reasons over typed data |
| **Latency budget** | Target: single-digit seconds for a full diagnosis. A NOC engineer won't wait; this constrains tool design toward parallelizable calls where possible |
| **Least-privilege access pattern** | Mock services simulate a support agent's actual scoped, read-only access — not admin/god-mode access to core systems |
| **Extensibility** | Adding a 5th backend system should mean adding one new tool to whichever specialist owns that domain (or a new specialist, if it fits neither existing domain) — never a supervisor redesign (see `02-ARCHITECTURE.md` Section 3.8) |
| **Explainability** | Every claim in the final diagnosis must cite exactly which evidence supports it |
| **Distributed observability** | One diagnosis request must be traceable end-to-end across every tool call and agent node (OpenTelemetry), not just a flat log line — see `02-ARCHITECTURE.md` Section 7 |
| **PII awareness** | Order/customer data includes real-shaped PII (address, account info) even though it's synthetic — the design must not assume this is safe to log/trace unredacted, even if full redaction is out of scope for v1 (see `02-ARCHITECTURE.md` Section 10) |

## 7. Success metrics

Since this is a portfolio project with no real production baseline, metrics
are framed honestly as **illustrative, not measured-in-production**:

- **Diagnostic accuracy** against a hand-built "golden set" of ~20-25
  synthetic stuck-order scenarios (7 archetypes) with known, designed-in
  root causes — see `03-EVALUATION.md` Section 1
- **Consistency** — same order ID, same evidence, same diagnosis across
  repeated runs (a real concern with LLM-based reasoning, worth measuring
  explicitly rather than assuming)
- **Estimated time savings** vs. the manual multi-system lookup process,
  stated as an estimate for the interview narrative, not a claimed
  production metric

## 8. Open questions

- [x] How many distinct "failure archetypes" should the mock data cover?
      **Resolved** — 7 archetypes (the 7th, conflicting evidence, added
      after `02-ARCHITECTURE.md` Section 3.7 was written), `03-EVALUATION.md`
      Section 1.
- [x] Confidence scoring — numeric or categorical? **Resolved** — categorical
      (`low`/`medium`/`high`), `02-ARCHITECTURE.md` Section 11.
- [x] Should the demo UI show the agent's reasoning step-by-step live (more
      impressive for a coworker demo, more engineering work) or just the
      final diagnosis (simpler, less "wow factor")? **Resolved** — both,
      via a toggle defaulting to the live step-by-step trace. Decided at
      Phase 7 once Phase 5's logging and Phase 6's correlation-ID header
      made the "more engineering work" side of the tradeoff basically
      free (`04-BUILD-PLAN.md` Phase 7, `05-DEVELOPMENT-LOG.md`'s Phase 7
      entry).

## 9. Data model — the cross-system join problem (restored)

**This section existed in an earlier draft and was lost during
`02-ARCHITECTURE.md`'s v1→v2 rewrite — two places (`02-ARCHITECTURE.md`
Sections 3.5 and 5.1) reference it as if it still exists. Restored here
rather than leaving those as dangling pointers.**

FR2 states the problem in one line; this is the actual shape of it. Each
system has its own natural key, and they don't line up:

| System | Keys on | Notes |
|---|---|---|
| CRM | `customer_id`, `order_id` | Both known from the initial order record |
| Billing | `customer_id` | Only queryable *after* CRM returns it |
| Provisioning | `order_id` | Known upfront — but **produces** `circuit_id` once (if) provisioning succeeds |
| Network Inventory | `circuit_id` or `address` | `circuit_id` only exists *after* Provisioning returns it; `address` is known upfront from the CRM record |

**Why this matters, concretely:** `order_id` is the only key known before
any tool has been called. Every other key is discovered progressively —
`customer_id` after CRM, `circuit_id` after Provisioning. This progressive
discovery is *why* `plan_next_action` (`02-ARCHITECTURE.md` Section 3.1)
has to be a genuine reasoning step rather than a fixed call sequence, and
it's the concrete data behind Section 3.5's "Round 1 / Round 2 / Round 3"
parallel-dispatch breakdown — Round 1 only fires tools needing `order_id`
(the only key available at the start); Round 2 fires once Round 1 has
produced `customer_id`; Round 3 (in the specific case where an address
lookup depends on a resolved circuit) waits on that.
