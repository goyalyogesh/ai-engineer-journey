# Project 7: Order Diagnosis Agent

**Status:** ✅ Core complete — Phases 0-7 of 13 (see `05-DEVELOPMENT-LOG.md`). A real, runnable multi-agent HTTP service with a working demo UI: `POST /diagnose` (auth'd, rate-limited) and `streamlit run ui/app.py` both return a correct structured diagnosis for the worked example, with a live step-by-step agent trace. Verified with a real 21-scenario evaluation harness. Extended (Kafka/Neo4j/Bedrock) starts only when explicitly requested next.

## One-line pitch

An AI agent that diagnoses why a telecom service order is stuck — by autonomously
querying multiple backend systems (CRM, billing, provisioning, network inventory)
and a knowledge base (RAG), correlating the evidence, and producing a cited,
structured root-cause hypothesis — instead of an engineer manually checking 4-5
systems by hand.

## Why this project exists

Built as a standalone portfolio piece (not tied to a specific curriculum day
range) to demonstrate genuine multi-tool agent orchestration — not another
RAG-over-documents project. Grew out of a conversation about what a real,
complex, enterprise-relevant AI engineering problem looks like at a telecom
company, informed by real .NET/enterprise-integration experience (Bell Canada)
with exactly this kind of cross-system order-fulfillment complexity.

**Important honesty note:** this project has no access to, and makes no claims
about, any real telecom company's actual internal systems. All "enterprise
systems" (CRM, billing, provisioning, network inventory) are realistic **mock
services** built for this project, with synthetic data. The architecture and
problem shape are realistic; the systems and data are not real. See
[`01-REQUIREMENTS.md`](01-REQUIREMENTS.md) for the explicit scope boundary.

## Documents in this folder

| File | Contents |
|---|---|
| [`01-REQUIREMENTS.md`](01-REQUIREMENTS.md) | Problem statement, personas, functional + non-functional requirements, scope boundaries, success metrics |
| [`02-ARCHITECTURE.md`](02-ARCHITECTURE.md) | System architecture (Core + Extended tiers), agent design (LangGraph), event-driven trigger (Kafka), knowledge graph (Neo4j/GraphRAG), model hosting (Bedrock + SageMaker), observability, clean design principles |
| [`03-EVALUATION.md`](03-EVALUATION.md) | Golden dataset, metrics (accuracy, false-confidence rate, tool-call efficiency), LLM-as-judge grading, regression testing |
| [`04-BUILD-PLAN.md`](04-BUILD-PLAN.md) | 13 phases (0-12), Core → Extended gate, definition of done per phase — **Core (Phases 0-7) implemented and verified** |
| [`AGENTS.md`](AGENTS.md) | Context file for any AI agent (implementer or reviewer) working on this project — ground rules, review history, what's already been decided |
| [`05-DEVELOPMENT-LOG.md`](05-DEVELOPMENT-LOG.md) | Running record of the actual build, phase by phase — what got built, what verification showed, what diverged from the plan and why. Updated as each phase completes. |

## Scope tiers (see `02-ARCHITECTURE.md` Section 0)

- **Core** — a **multi-agent** system: a supervisor + 2 specialist sub-agents
  (Billing/CRM, Network), LangGraph orchestration, 4 mock backend
  microservices (each with its own SQLite DB) + 1 knowledge-base tool,
  structured diagnosis output, a FastAPI serving layer, a real evaluation
  harness, and a Streamlit demo UI. **Complete — Phases 0-7.**
- **Extended** — Kafka event-driven trigger, Neo4j knowledge graph, Bedrock
  hosting + API Gateway ingress, full observability stack. Builds next,
  once explicitly requested.
- **Optional / v2** — named honestly, not designed in depth: SageMaker
  triage classifier, guardrails/PII redaction, semantic caching, CI/CD
  eval-gating, containerization/IaC.

## Status

Planning complete (requirements, architecture, evaluation, build plan).
**Core is complete — Phases 0-7 of 13**, all built and verified against
real running processes, not just unit tests:
- `POST /diagnose` (`api/main.py`) is a real, running HTTP endpoint —
  API-key auth, per-key rate limiting, and a correlation-ID-linked
  structured log trace of every tool call and graph node transition.
- A real 21-scenario evaluation harness (`eval/run_eval.py`) that found
  and fixed 3 real agent-quality bugs by actually running it against real
  LLM calls — including a genuine FR6 violation (confidently fabricating
  a cause for an unrecognized error code) that's now fixed and measured
  (insufficient-evidence recall went from 0% to 100%).
- A Streamlit demo (`ui/app.py`) with a live, correlation-ID-linked
  step-by-step trace of the agent's reasoning, not just the final answer.

See [`05-DEVELOPMENT-LOG.md`](05-DEVELOPMENT-LOG.md) for the running
record of what's actually been built and verified, phase by phase. Per
`04-BUILD-PLAN.md`'s Core → Extended gate, Phase 8 (Neo4j) onward starts
only once explicitly requested next.
