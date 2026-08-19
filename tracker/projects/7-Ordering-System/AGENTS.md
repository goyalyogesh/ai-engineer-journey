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

**Planning is complete. Zero implementation code exists.** Requirements,
architecture, evaluation, and a 13-phase build plan are all fully drafted
and have been through 4 review passes (see "Review history" below).

**If you are an implementing agent: do not write implementation code unless
the human running this session has explicitly said to start.** This applies
regardless of how complete or "ready to build" the plan looks — completeness
of the plan is not authorization to execute it.

## Document map (read in this order)

| File | What it is |
|---|---|
| [`README.md`](README.md) | Project pitch, honesty boundary, scope tiers |
| [`01-REQUIREMENTS.md`](01-REQUIREMENTS.md) | Problem, personas, FR1-FR10, NFRs, scope in/out, data model (Section 9) |
| [`02-ARCHITECTURE.md`](02-ARCHITECTURE.md) | Full system design — read Section 0 (scope tiers) and Section 3 (core agent design) first |
| [`03-EVALUATION.md`](03-EVALUATION.md) | Golden dataset, metrics, LLM-as-judge, regression strategy |
| [`04-BUILD-PLAN.md`](04-BUILD-PLAN.md) | 13 phases with exact schemas/signatures/seed data — the actual build sequence |

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
- **Each specialist:** its own `plan → execute → evaluate` loop, capped at
  `SPECIALIST_MAX_ITERATIONS = 3`, dispatches its own tools in parallel via
  `asyncio.gather` when inputs allow (I/O-bound work — not threads/processes,
  see Section 3.5 for the GIL-grounded reasoning).
- **5 tools**, split by domain: Billing/CRM owns `get_order_record` +
  `get_billing_status`; Network owns `get_provisioning_log` +
  `get_inventory_status` + `search_knowledge_base` (vector via Chroma +
  graph via Neo4j once Extended).
- **Stack:** FastAPI (serving), LangGraph (orchestration), Pydantic
  (structured I/O everywhere), SQLite-per-service at Core (Postgres/RDS
  named for Extended), Bedrock-hosted Claude at Extended (direct API at
  Core), pytest (3-layer testing strategy, Section 13).

## Review history — what's already been checked, so you don't re-flag it

This project has been through **4 full review passes** by the assistant
that helped build it. Known classes of issue that were found and fixed:
cross-reference drift after section renumbering, stale numbers after scope
changes (archetype counts, scenario counts), a real Pydantic type
contradiction (`expected_root_cause` needed to allow `None`), an
architectural gap where no rule existed for "multiple true causes" vs.
"conflicting evidence" (now FR10), and — this pass — actual content loss
(the data-model/join-problem section was dropped during a rewrite and only
referenced by dangling pointers; restored as `01-REQUIREMENTS.md` Section 9).

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

- `01-REQUIREMENTS.md` Section 8: whether the demo UI (Phase 7) should show
  live step-by-step agent reasoning or just the final diagnosis — explicitly
  deferred to build time.
- Nothing else is currently marked open across the 4 docs as of this file's
  writing — if you find something that contradicts that, it's a real finding.
