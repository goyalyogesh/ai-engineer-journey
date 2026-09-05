# AGENTS.md — Order Diagnosis Agent

Context file for any AI agent (implementer, reviewer, or otherwise) working
on this project. Read this first — it's the map, not a substitute for the
underlying docs.

## What this project is

An AI agent that diagnoses why a telecom service order is stuck, by
autonomously querying multiple backend systems (CRM, Billing, Provisioning,
Network Inventory) plus a knowledge base (vector + graph RAG), correlating
the evidence, and producing a structured, cited root-cause diagnosis —
instead of an engineer manually checking 4-5 systems by hand. Built as a
standalone portfolio/interview piece, not tied to a day-numbered curriculum.

**Full context on why this project exists, and the honesty boundary around
mocked vs. real systems, is in [`README.md`](README.md) — read that first
if you haven't.**

## Current status — read before doing anything else

**Planning is complete. Core is complete (Phases 0-7). Extended is in
progress — Phase 8 (Neo4j) is done (Phase 9 of 13 total not yet started).**
Requirements, architecture, evaluation, and a 13-phase build plan are fully
drafted and have been through 4 review passes (see "Review history"
below). Every Core phase is done and verified: scaffolding, mock backend
microservices, the tools layer, the 2 specialist sub-agents, the
supervisor agent, the FastAPI serving layer, a real 21-scenario evaluation
harness, and a Streamlit demo UI with a live step-by-step agent trace.
Phase 8 added a real (locally-Dockerized, not Aura — see below) Neo4j
knowledge graph, merged into `search_knowledge_base` alongside the
existing Chroma vector search. `POST /diagnose` with a valid `X-API-Key`
runs the full multi-agent loop end-to-end and returns a correct structured
diagnosis, verified against real running processes with `curl`, a real
browser, and a real 21-scenario eval harness run multiple times — not just
`TestClient`. See [`05-DEVELOPMENT-LOG.md`](05-DEVELOPMENT-LOG.md) for
exactly what exists and what was verified, phase by phase. Docker itself
has been verified for real (`docker compose config`/`build`/`up` for all 5
containers together, including a full down/up data-persistence check for
Neo4j's named volume).

**Extended work continues phase by phase, same discipline as Core.** Per
`04-BUILD-PLAN.md`'s sequencing principle, Phase 9 (Kafka) onward does not
start until the human running this session explicitly says to continue —
Phase 8 being "done" is not itself permission to keep going.

**If you are an implementing agent: do not jump ahead of the current phase
recorded in `05-DEVELOPMENT-LOG.md` without the human running this session
explicitly saying to.** Read the development log first to know exactly
where the project currently stands before writing anything.

## Document map (read in this order)

| File | What it is |
|---|---|
| [`README.md`](README.md) | Project pitch, honesty boundary, scope tiers |
| [`01-REQUIREMENTS.md`](01-REQUIREMENTS.md) | Problem, personas, FR1-FR10, NFRs, scope in/out, data model (Section 9) |
| [`02-ARCHITECTURE.md`](02-ARCHITECTURE.md) | Full system design — read Section 0 (scope tiers) and Section 3 (core agent design) first |
| [`03-EVALUATION.md`](03-EVALUATION.md) | Golden dataset, metrics, LLM-as-judge, regression strategy |
| [`04-BUILD-PLAN.md`](04-BUILD-PLAN.md) | 13 phases with exact schemas/signatures/seed data — the actual build sequence |
| [`05-DEVELOPMENT-LOG.md`](05-DEVELOPMENT-LOG.md) | **Read this to know what phase the project is actually at right now** — running record of what's been built and verified, phase by phase |

## Non-negotiable ground rules

These aren't preferences — violating them undoes the point of the project:

1. **Honesty about what's real.** This project has no access to, and makes
   no claim of access to, any real telecom's internal systems. CRM/Billing/
   Provisioning/Inventory are permanently mocked (`01-REQUIREMENTS.md`
   Section 4). Never write anything implying otherwise.
2. **Core before Extended, always.** Kafka, Neo4j (real Aura), Bedrock, and
   the full observability stack are `[EXTENDED]` — they get built only
   after Core's eval suite passes (`04-BUILD-PLAN.md`'s Phase 7→8 gate).
   Don't skip ahead because a later phase looks more interesting.
3. **Stub first, real infrastructure second**, specifically for Neo4j/Kafka
   (`02-ARCHITECTURE.md` Section 11) — isolates agent-logic bugs from
   infrastructure bugs.
4. **No corrective/write actions, ever, in this version.** The agent
   diagnoses; a human acts. This is a stated scope boundary
   (`01-REQUIREMENTS.md` Section 4), not a missing feature.
5. **Specialists return full structured evidence, never prose summaries**
   (`02-ARCHITECTURE.md` Section 3.8) — this is what keeps the multi-agent
   split from degrading correctness. Don't "simplify" this later.
6. **Comment the *why*, tied to the specific doc section that justifies it**
   (`04-BUILD-PLAN.md`'s "Code comprehensibility" section) — once
   implementation starts. This project is meant to be explained in an
   interview, not just to run.

## Condensed architecture (for fast orientation — not a substitute for
`02-ARCHITECTURE.md`)

- **Multi-agent, not single-agent:** a Supervisor + 2 specialist sub-agents
  (Billing/CRM, Network), each a LangGraph subgraph, specialists invoked as
  subgraph nodes inside the supervisor's graph.
- **Supervisor:** dispatches to both specialists in parallel, applies
  conflict-resolution (Section 3.7) and the multi-cause pipeline-order rule
  (Section 3.7, FR10) to their raw evidence, produces the final
  `DiagnosisOutput`. Does **not** loop — single dispatch → synthesize pass.
  `synthesize_diagnosis` itself is 2 steps, deliberately not 1: an LLM call
  *classifies* each specialist's raw evidence (real problem? which stage?
  technical or administrative?), then plain, LLM-free Python
  (`apply_precedence_and_pipeline_rules` in `agent/supervisor.py`)
  mechanically applies the precedence/pipeline-order rules to that
  classification — Section 3.7 wants these rules "auditable... not an
  implicit bias buried in a prompt," so the rule itself is real code, not
  something trusted to an LLM's judgment inside one opaque call. If you're
  reviewing this and it looks like it should be one `.with_structured_output()`
  call — it deliberately isn't; see `05-DEVELOPMENT-LOG.md`'s Phase 4 entry.
- **Each specialist:** its own `plan → execute → evaluate` loop, capped at
  `SPECIALIST_MAX_ITERATIONS = 3`, dispatches its own tools in parallel via
  `asyncio.gather` when inputs allow (I/O-bound work — not threads/processes,
  see Section 3.5 for the GIL-grounded reasoning).
- **5 tools**, split by domain: Billing/CRM owns `get_order_record` +
  `get_billing_status`; Network owns `get_provisioning_log` +
  `get_inventory_status` + `search_knowledge_base` (vector via Chroma
  **and** graph via Neo4j, run in parallel and merged — built, Phase 8).
- **Knowledge graph (`graph/`, Phase 8):** local Neo4j (Docker, not Aura —
  the coursework Aura instance had expired; see below), populated by
  `graph/populate.py` from the same seed data the mock services use.
  `search_knowledge_base` merges vector results (`exact_match_found`) with
  a Cypher traversal (`graph_match_found`, plus `cause`/`resolution`/
  `related_incidents` when found) — either signal counts as a genuine
  explanation, checked deterministically in `agent/supervisor.py`
  (`_enforce_kb_grounding`), not left to the classifier LLM's judgment
  alone (same reasoning as Phase 6's `exact_match_found` fix).
- **Stack:** FastAPI (serving), LangGraph (orchestration), Pydantic
  (structured I/O everywhere), SQLite-per-service at Core (Postgres/RDS
  named for Extended), Neo4j (Phase 8, built), Bedrock-hosted Claude + API
  Gateway ingress + Kafka still named-not-built, in-app auth/rate-limit at
  Core (Section 14), pytest (testing strategy, Section 13).
- **API layer (`api/main.py`, Phase 5):** `POST /diagnose`, header-based
  `X-API-Key` auth, `slowapi` rate limiting keyed by API key (not IP),
  `correlation_id` = the LangGraph checkpointer's `thread_id`, structured
  JSON-lines logging (`agent/observability.py`) via a `contextvars`-based
  correlation ID rather than threading it through every function
  signature. FastAPI `lifespan` owns the checkpointer's open/close.

## Review history — what's already been checked, so you don't re-flag it

This project has been through **4 full review passes** (planning-phase,
docs only) by the assistant that helped build it. Known classes of issue
that were found and fixed: cross-reference drift after section
renumbering, stale numbers after scope changes (archetype counts, scenario
counts), a real Pydantic type contradiction (`expected_root_cause` needed
to allow `None`), an architectural gap where no rule existed for "multiple
true causes" vs. "conflicting evidence" (now FR10), and — that pass —
actual content loss (the data-model/join-problem section was dropped
during a rewrite and only referenced by dangling pointers; restored as
`01-REQUIREMENTS.md` Section 9).

**Implementation-phase corrections (Phases 0-4), already resolved — don't
re-flag these either:** `04-BUILD-PLAN.md`'s pseudocode named the *sync*
`SqliteSaver` for the supervisor's checkpointer, which doesn't support the
async methods this graph's `.ainvoke()`-only nodes need — corrected to
`AsyncSqliteSaver`, verified with a real disk round-trip test (Phase 4).
`SpecialistState`'s original 3-field pseudocode had no way for
`plan_next_action` to hand its decision to `execute_tool`, or for
`evaluate_evidence`'s verdict to reach `should_continue` — 3 more fields
added, documented in `agent/state.py` and retroactively in
`04-BUILD-PLAN.md` (Phase 3). `synthesize_diagnosis` was redesigned from
one `.with_structured_output()` call into an LLM-classification step +
deterministic Python rule-application step (Phase 4, see the "Condensed
architecture" section above) — a deliberate design improvement over the
original pseudocode, not a deviation to flag. Phase 5 added
`agent/observability.py` (not in the original repo tree — structured
logging's mechanism was never specified, only the requirement) and keyed
`slowapi` rate limiting by API key instead of its IP-based default, to
actually match this doc's own "10 req/min per API key" wording. Phase 6
found and fixed a real FR6 violation via the eval harness itself (not
review, not assumption): `search_knowledge_base` had no relevance floor,
so an unknown provisioning error code got confidently "explained" using a
different, unrelated error code's real KB entry. Fixed with a
deterministic `exact_match_found` signal (`agent/tools.py`) plus a new
`SpecialistReading.cause_understood` field and a code-level
`_enforce_kb_grounding()` cross-check (`agent/supervisor.py`) — prompt-only
fixes were tried first and didn't reliably work. Insufficient-evidence
recall went 0% → 100% across the fix. Phase 6 also corrected the
golden dataset's own "conflicting evidence" archetype, which had
originally expected `insufficient_evidence=True` in direct contradiction
of Phase 4's own already-tested precedence-resolution behavior. Phase 8's
own plan assumed the Aura instance from earlier coursework still existed
(it didn't — auto-deleted from inactivity; swapped for local Docker, both
named honestly in `docker-compose.yml`), and re-running the eval harness
(the plan's own explicit requirement) surfaced 2 more real bugs: a
regression in the just-rewritten KB grounding override (it stopped
distinguishing "searched, found nothing" from "wasn't even a code-specific
search," incorrectly penalizing unrelated findings like inventory address
mismatches), and a genuinely pre-existing bug since Phase 4
(`apply_precedence_and_pipeline_rules`'s "no true problems" branch always
returned `insufficient_evidence=True`, even for a confirmed-clean order
with complete evidence — should have been a confident "no issue found").
Root cause accuracy dropped from 72% to 44% before both were found and
fixed; recovered to 72% afterward, with false-confidence rate additionally
improved from 20% to 0%. Full reasoning for all of these is in
`05-DEVELOPMENT-LOG.md`'s Phase 3-8 entries.

**If you're reviewing this project:** the scope boundaries (mocked systems,
no write access, Core/Extended/Optional tiers) are deliberate, reasoned
decisions with justification already written down in the docs — re-flagging
"you should add Kubernetes" or "why isn't this connected to real systems"
without reading `02-ARCHITECTURE.md` Section 10 / `01-REQUIREMENTS.md`
Section 4 first will just repeat ground already covered. **The most useful
review finds things like:** logical contradictions between docs, schema
mismatches, requirements with no corresponding design (or vice versa),
or genuinely new scope gaps — not a generic "add more enterprise tech"
pass, which this project has already deliberately scoped and explained.

## Known open items (not yet resolved — fair game for a reviewer)

- `01-REQUIREMENTS.md` Section 8's UI question is now resolved (Phase 7) —
  no longer open.
- **Real, measured, deliberately-not-chased eval limitations (Phase 6):**
  insufficient-evidence precision is 60% (2 of the 21 golden scenarios
  still trigger `insufficient_evidence` when they shouldn't), and both
  specialists call more tools than `expected_evidence_tools` suggests
  (some redundant re-calls of the same tool across planning iterations —
  a cost/efficiency issue, not a correctness one). Consistent with
  `03-EVALUATION.md` Section 5's explicit "illustrative, not a production
  accuracy claim" framing — these are real numbers, reported honestly, not
  bugs left unfixed by oversight. See `05-DEVELOPMENT-LOG.md`'s Phase 6
  entry for the full before/after picture.
- Nothing else is currently marked open across the 4 docs as of this file's
  writing — if you find something that contradicts that, it's a real finding.
