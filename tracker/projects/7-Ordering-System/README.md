# Project 7: Order Diagnosis Agent

**Status:** 📋 Planning complete (requirements, architecture, evaluation, build plan) — awaiting review before any implementation starts.

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
| [`04-BUILD-PLAN.md`](04-BUILD-PLAN.md) | 13 phases (0-12), Core → Extended gate, definition of done per phase — **planning only, no implementation started** |
| [`AGENTS.md`](AGENTS.md) | Context file for any AI agent (implementer or reviewer) working on this project — ground rules, review history, what's already been decided |

## Scope tiers (see `02-ARCHITECTURE.md` Section 0)

- **Core** — a **multi-agent** system: a supervisor + 2 specialist sub-agents
  (Billing/CRM, Network), LangGraph orchestration, 4 mock backend
  microservices (each with its own SQLite DB) + 1 knowledge-base tool,
  structured diagnosis output. Builds first.
- **Extended** — Kafka event-driven trigger, Neo4j knowledge graph, Bedrock
  hosting + API Gateway ingress, full observability stack, evaluation
  harness. Builds once Core works.
- **Optional / v2** — named honestly, not designed in depth: SageMaker
  triage classifier, guardrails/PII redaction, semantic caching, CI/CD
  eval-gating, containerization/IaC.

## Status

Requirements, architecture, evaluation, and a phased build plan are all
drafted — see `04-BUILD-PLAN.md` for the full 13-phase sequence and the
Core/Extended gate. **Awaiting review and explicit go-ahead before any
implementation starts.** No code has been written yet, by design.
