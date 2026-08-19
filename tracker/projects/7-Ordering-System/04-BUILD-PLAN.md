# Build Plan — Order Diagnosis Agent

**Status:** Draft v2 — for review. **No implementation has started.** This
document is the plan only; nothing gets built until it's reviewed and
explicitly approved.

Depends on [`01-REQUIREMENTS.md`](01-REQUIREMENTS.md),
[`02-ARCHITECTURE.md`](02-ARCHITECTURE.md), and
[`03-EVALUATION.md`](03-EVALUATION.md) — this doc sequences *how* those get
built. **v2 change:** each phase now specifies exact file structure, schemas,
function signatures, and concrete seed data — v1 named tasks at too high a
level to actually start from.

## Sequencing principle (unchanged from v1)

1. **Core fully, before any Extended work starts.**
2. **Stub first, real infrastructure once Core passes evals.**
3. **Hard gate between Phase 7 and Phase 8** — the eval suite must pass on
   Core before Kafka/Neo4j/Bedrock/full observability work begins.

## Code comprehensibility — applies to every phase, whenever building starts

This project exists to be **understood and explained**, not just to run —
it's a portfolio piece and interview artifact, not a black box that happens
to pass its own eval suite. That changes the commenting bar from "comment
only the non-obvious" to something a bit more generous:

- **Comment the *why*, tied back to the actual design decision, not the
  *what*.** E.g., a comment on the retry wrapper should say *"one retry
  only — see 02-ARCHITECTURE.md Section 3.6, a full backoff policy was
  scoped out as disproportionate"*, not *"this retries the function."* The
  reasoning already exists in `01-REQUIREMENTS.md`/`02-ARCHITECTURE.md` —
  the code should point back to it, not restate it blindly.
- **Every deliberate design decision that isn't obvious from the code
  alone gets a comment where it's implemented** — the precedence rule
  (Section 3.7), the `insufficient_evidence`/`confidence` invariant
  (Section 3.4), why tools are dispatched via `asyncio.gather` and not
  threads (Section 3.5) — so reading the code later (or explaining it live
  in an interview) doesn't require re-deriving the reasoning from scratch.
- **Still don't narrate the obvious.** A straightforward FastAPI route or a
  Pydantic field doesn't need a comment explaining what it plainly does —
  the goal is a codebase that teaches its own non-obvious decisions, not
  one padded with restated syntax.
- This applies **once implementation actually starts** — not yet, per this
  document's status above.

## Repo structure (target state after Phase 7 — Core complete)

```
order-diagnosis-agent/
├── docker-compose.yml
├── .env.example
├── pyproject.toml
├── mock_services/
│   ├── crm/            (main.py, models.py, db.py, seed_data.py, crm.db)
│   ├── billing/        (same shape)
│   ├── provisioning/   (same shape)
│   └── inventory/      (same shape)
├── agent/
│   ├── state.py            # SpecialistState, SupervisorState, SpecialistFinding, DiagnosisOutput
│   ├── tools.py             # the 5 @tool functions + ToolResult
│   ├── specialists/
│   │   ├── billing_crm.py
│   │   └── network.py
│   └── supervisor.py
├── api/
│   └── main.py              # POST /diagnose
├── ui/
│   └── app.py                # Streamlit demo
├── eval/
│   ├── golden_dataset.json
│   ├── judge.py
│   ├── metrics.py
│   └── run_eval.py
└── tests/
    ├── test_mock_services.py
    ├── test_tools.py
    ├── test_specialists.py
    ├── test_supervisor.py
    ├── test_api.py
    ├── test_kb_vector.py       # Phase 8, Extended
    ├── test_kb_graph.py        # Phase 8, Extended
    ├── test_kb_merged.py       # Phase 8, Extended
    └── test_consumer.py        # Phase 9, Extended
```

## Phase 0 — Scaffolding

**Goal:** a repo that runs, before any real logic exists.

**Tasks:**
1. Create the directory tree above (empty files where noted).
2. `.env.example` listing every config value the system will need (fill in
   real values in a git-ignored `.env` later, not now):
   ```
   OPENAI_API_KEY=
   ANTHROPIC_API_KEY=
   CRM_SERVICE_URL=http://localhost:8001
   BILLING_SERVICE_URL=http://localhost:8002
   PROVISIONING_SERVICE_URL=http://localhost:8003
   INVENTORY_SERVICE_URL=http://localhost:8004
   CHROMA_PATH=./chroma_kb_data
   SPECIALIST_MAX_ITERATIONS=3
   API_KEY=                        # for POST /diagnose auth (Phase 5)
   MOCK_FAILURE_RATE=0.1           # Phase 1 — % of calls that simulate a transient failure
   MOCK_LATENCY_MIN_MS=200
   MOCK_LATENCY_MAX_MS=1500
   ```
3. `pyproject.toml` (or `requirements.txt`) — `fastapi`, `uvicorn`,
   `langgraph`, `langchain`, `langchain-openai`, `langchain-anthropic`,
   `langchain-chroma`, `pydantic`, `pytest`, `pytest-asyncio`, `httpx`,
   `python-dotenv`.
4. `docker-compose.yml` — one service block per mock backend (Phase 1),
   ports `8001`-`8004`, empty `command:` placeholders until Phase 1 fills
   them in.
5. `tests/conftest.py` — shared pytest fixtures (empty for now, filled in
   per phase).

**Definition of done:** `docker compose config` validates without error;
`pip install -e .` (or equivalent) succeeds; `pytest` runs with 0 tests
collected, 0 errors.

## Phase 1 — Mock backend microservices [CORE]

**Goal:** 4 independently deployable FastAPI services, each with its own
SQLite DB (`02-ARCHITECTURE.md` Section 3.3, Section 12).

**Schemas — one SQLite table per service:**

```sql
-- mock_services/crm/crm.db
CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    service_type TEXT NOT NULL,      -- e.g. 'fiber_internet'
    address TEXT NOT NULL,
    status TEXT NOT NULL,            -- 'created' | 'cancelled'
    created_at TEXT NOT NULL
);

-- mock_services/billing/billing.db
CREATE TABLE billing_status (
    customer_id TEXT PRIMARY KEY,
    payment_status TEXT NOT NULL,    -- 'authorized' | 'declined' | 'pending'
    hold_active BOOLEAN NOT NULL,
    hold_reason TEXT,
    plan TEXT NOT NULL
);

-- mock_services/provisioning/provisioning.db
CREATE TABLE provisioning_log (
    order_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,            -- 'succeeded' | 'failed' | 'not_started'
    error_code TEXT,
    circuit_id TEXT,
    updated_at TEXT NOT NULL
);

-- mock_services/inventory/inventory.db
CREATE TABLE inventory (
    circuit_id TEXT PRIMARY KEY,
    address TEXT NOT NULL,
    status TEXT NOT NULL             -- 'assigned' | 'unassigned'
);
```

**Endpoints (one per service, `main.py`):**

```
GET /orders/{order_id}                          -> 200 CRM record | 404
GET /billing/{customer_id}                       -> 200 billing record | 404
GET /provisioning/{order_id}                     -> 200 provisioning record | 404
GET /inventory?circuit_id=...&address=...         -> 200 inventory record | 404
```

**Latency/failure simulation** (in each service, before returning):
```python
await asyncio.sleep(random.uniform(MOCK_LATENCY_MIN_MS, MOCK_LATENCY_MAX_MS) / 1000)
if random.random() < MOCK_FAILURE_RATE:
    raise HTTPException(status_code=503, detail="transient failure")
```

**Seed data — concrete records per archetype (`03-EVALUATION.md` Section 1),
1 example each, 2-3 more variants per archetype to be added during this
phase following the same pattern:**

| Archetype | Order ID | CRM | Billing | Provisioning | Inventory |
|---|---|---|---|---|---|
| Known error code | `ORD-88213` (the worked example) | created | authorized | failed, `ERR_4471` | no record for the address |
| Unknown error code | `ORD-90001` | created | authorized | failed, `ERR_9999` (deliberately absent from the KB — Phase 8) | n/a |
| Billing hold only | `ORD-90002` | created | `hold_active=true`, reason `payment_declined` | `not_started` | n/a |
| Inventory/address mismatch | `ORD-90003` | created, address A | authorized | succeeded, `circuit_id=C-500` | `C-500` exists, assigned to a *different* address |
| Multiple causes | `ORD-90004` | created | `hold_active=true` | failed, `ERR_4471` | no record |
| Clean order | `ORD-90005` | created | authorized | succeeded, `circuit_id=C-600` | `C-600` assigned, matches address |
| Conflicting evidence | `ORD-90006` | created | `hold_active=false` | failed, `ERR_BILL_MISMATCH` (implies a billing cause despite Billing showing clean) | n/a |

**Definition of done:** all 4 services running (`docker compose up`), each
queryable via `curl`; querying `ORD-88213` across all 4 reproduces the
worked example's raw data exactly; `tests/test_mock_services.py` covers one
happy-path + one 404 case per service.

## Phase 2 — Tools layer [CORE]

**Goal:** the 5 `@tool` functions (`02-ARCHITECTURE.md` Section 3.3),
calling Phase 1's services over real HTTP.

**`agent/tools.py` — shared result type:**
```python
class ToolResult(BaseModel):
    tool_name: str
    success: bool
    data: dict | None
    error: str | None       # populated on failure, incl. "unavailable" (Section 3.6)
    latency_ms: float
```

**Function signatures:**
```python
@tool
async def get_order_record(order_id: str) -> ToolResult: ...

@tool
async def get_billing_status(customer_id: str) -> ToolResult: ...

@tool
async def get_provisioning_log(order_id: str) -> ToolResult: ...

@tool
async def get_inventory_status(circuit_id: str | None = None, address: str | None = None) -> ToolResult: ...

@tool
async def search_knowledge_base(query: str) -> ToolResult: ...   # Chroma only this phase — Neo4j is Phase 8
```

**Retry wrapper** (Section 3.6 — one retry, then explicit "unavailable"):
```python
async def call_with_retry(fn, *args, retries: int = 1, **kwargs) -> ToolResult:
    for attempt in range(retries + 1):
        try:
            return await fn(*args, **kwargs)
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            if attempt == retries:
                return ToolResult(tool_name=fn.__name__, success=False,
                                   data=None, error=f"unavailable: {e}", latency_ms=0)
```

**Definition of done:** `tests/test_tools.py` — one test per tool against
the real Phase 1 services (not further-mocked, per `02-ARCHITECTURE.md`
Section 13), plus one test forcing `MOCK_FAILURE_RATE=1.0` to verify the
retry-then-"unavailable" path.

## Phase 3 — Specialist sub-agents [CORE]

**Goal:** `agent/specialists/billing_crm.py` and `agent/specialists/network.py`
— the 2 LangGraph subgraphs from Section 3.8.

**`agent/state.py`:**
```python
class SpecialistState(TypedDict):
    order_id: str
    evidence: list[ToolResult]
    iterations: int

SPECIALIST_MAX_ITERATIONS = int(os.environ["SPECIALIST_MAX_ITERATIONS"])  # =3, 12-factor (Section 8)

class SpecialistFinding(BaseModel):
    specialist: Literal["billing_crm", "network"]
    evidence: list[ToolResult]
    preliminary_assessment: str
```

**Node signatures (same shape in both specialist files):**
```python
async def plan_next_action(state: SpecialistState) -> SpecialistState: ...
async def execute_tool(state: SpecialistState) -> SpecialistState: ...   # asyncio.gather for parallel calls, Section 3.5
async def evaluate_evidence(state: SpecialistState) -> SpecialistState: ...
def should_continue(state: SpecialistState) -> Literal["continue", "done"]: ...
```

**Graph wiring:**
```python
graph = StateGraph(SpecialistState)
graph.add_node("plan", plan_next_action)
graph.add_node("execute", execute_tool)
graph.add_node("evaluate", evaluate_evidence)
graph.add_edge(START, "plan")
graph.add_edge("plan", "execute")
graph.add_edge("execute", "evaluate")
graph.add_conditional_edges("evaluate", should_continue, {"continue": "plan", "done": END})
billing_crm_graph = graph.compile()  # deliberately no checkpointer here —
                                       # see Phase 4's checkpointer note
```

**Prompt design tasks (content, not just structure):**
- `plan_next_action` prompt: given `evidence` so far, decide which of this
  specialist's own tools to call next (possibly several in parallel) —
  must know its own tool set only (Billing/CRM specialist never sees
  Provisioning/Inventory/KB as options).
- `evaluate_evidence` prompt: "is this specialist's own investigation
  complete enough to hand off a `preliminary_assessment`" — distinct
  question from the supervisor's later, cross-specialist synthesis.

**Definition of done:** each specialist graph runnable standalone (no
supervisor yet). Running the Network specialist alone against `ORD-88213`
surfaces `ERR_4471`, calls `search_knowledge_base`, and calls
`get_inventory_status` — verified via `tests/test_specialists.py` using
DI-injected fake tools (Section 13) for fast/deterministic node-level tests,
plus one slower test against the real Phase 1/2 stack for the full
`ORD-88213` path.

## Phase 4 — Supervisor agent [CORE]

**Goal:** `agent/supervisor.py` — top-level graph, specialists as subgraph
nodes (Section 3.8).

**`agent/state.py` addition:**
```python
class SupervisorState(TypedDict):
    order_id: str
    billing_finding: SpecialistFinding | None
    network_finding: SpecialistFinding | None
    diagnosis: DiagnosisOutput | None
```

**Node signatures:**
```python
async def dispatch_specialists(state: SupervisorState) -> SupervisorState: ...  # asyncio.gather on both subgraphs
async def synthesize_diagnosis(state: SupervisorState) -> SupervisorState: ...   # applies Section 3.7 precedence rule
```

**Graph wiring (subgraph-as-node — Section 3.8's stated LangGraph mechanism):**
```python
supervisor_graph = StateGraph(SupervisorState)
supervisor_graph.add_node("dispatch", dispatch_specialists)
supervisor_graph.add_node("synthesize", synthesize_diagnosis)
supervisor_graph.add_edge(START, "dispatch")
supervisor_graph.add_edge("dispatch", "synthesize")
supervisor_graph.add_edge("synthesize", END)

checkpointer = SqliteSaver.from_conn_string("agent_checkpoints.db")  # Section 12
compiled = supervisor_graph.compile(checkpointer=checkpointer)
```

**Why only the supervisor gets a checkpointer, not each specialist —
stated explicitly, since the asymmetry looks like an oversight otherwise:**
the `interrupt()`-readiness commitment (Section 3.1) is about a *future*
human-approval gate before a write action — and any such gate belongs at
the supervisor level (before `synthesize_diagnosis` acts on aggregated
findings), not inside an individual specialist's internal tool-calling loop.
Specialists are supposed to run to completion and report back; only the
supervisor's decision point is a plausible future pause/resume boundary.

**`synthesize_diagnosis` internal logic (spelled out, not just named):**
1. Pull `billing_finding.evidence` + `network_finding.evidence` (raw, not
   the `preliminary_assessment` text — Section 3.8's safety constraint).
2. Run conflict detection: does anything in one evidence set **contradict**
   the other? If yes, apply the precedence rule (technical > administrative,
   Section 3.7); if unresolvable, set `insufficient_evidence=True` with the
   conflict named.
3. If no contradiction, check for **multiple independently true** findings
   (FR10, Section 3.7's pipeline-order rule — a distinct case from step 2:
   evidence agrees, there's just more than one real problem). If found,
   `root_cause` names whichever is earliest in `CRM → Billing →
   Provisioning → Inventory`; every true finding still goes into `evidence`.
4. Otherwise (single clear cause, or none), produce `DiagnosisOutput` via
   `.with_structured_output()` (same mechanism as
   `16Langchain-Deep-Interview.ipynb`), which triggers the
   `confidence`/`insufficient_evidence` validator (Section 3.4) automatically.

**Definition of done — two distinct test types, per `02-ARCHITECTURE.md`
Section 13's revised testing table:**
- **Fast, isolated `synthesize_diagnosis` unit tests** — construct
  `SupervisorState` directly with hand-crafted `SpecialistFinding` objects
  (no specialists, no mock services, no network calls involved at all):
  one conflict case, one multiple-true-causes case verifying the
  pipeline-order rule, one clean case. These run in milliseconds and are
  what actually test the supervisor's own logic in isolation.
- **Full-stack integration test** — running the compiled supervisor graph
  (real specialists, real mock services) against `ORD-88213` end-to-end
  reproduces the worked example's diagnosis exactly. Slower, but validates
  real wiring, not just logic.

`tests/test_supervisor.py` contains both kinds, clearly separated (e.g. by
test class or filename suffix) — not blended together as if they were the
same kind of test.

## Phase 5 — FastAPI serving layer [CORE]

**Goal:** `api/main.py` — `POST /diagnose`.

```python
@app.post("/diagnose", dependencies=[Depends(verify_api_key)])
async def diagnose(request: DiagnoseRequest) -> DiagnosisOutput:
    ...
```
- `DiagnoseRequest = {"order_id": str}`
- `verify_api_key` — header-based check against `API_KEY` env var (Section
  10's "cheap to build, pull into Core" item)
- Basic rate limiting via `slowapi` (or equivalent) — e.g. 10 req/min per
  API key
- Structured JSON log line per tool call + per graph node transition,
  `correlation_id = ` the request's generated UUID, written to a local
  JSON Lines file (Section 12's Core-tier logging choice)

**Definition of done:** `curl -H "X-API-Key: ..." -X POST /diagnose -d
'{"order_id": "ORD-88213"}'` returns the correct structured diagnosis; a
request without the header returns 401; log file shows a full
correlation-ID-linked trace of that one request's tool calls.
`tests/test_api.py` (using FastAPI's `TestClient`, no real server process
needed) covers this same set automatically: valid key succeeds, missing/
wrong key returns 401, and exceeding the rate limit returns 429 — the API
layer's own contract, independent of whether the agent logic underneath it
is real or stubbed.

## Phase 6 — Evaluation harness [CORE]

**Goal:** `eval/` — `03-EVALUATION.md` made real.

**`eval/golden_dataset.json`** — 20-25 `GoldenScenario` entries. Concrete
first 3 (rest follow the same shape, ~3 more per archetype):
```json
[
  {
    "scenario_id": "known-error-1",
    "order_id": "ORD-88213",
    "archetype": "provisioning_failure_known_code",
    "expected_root_cause": "No circuit was assigned in inventory for the service address",
    "expected_confidence_min": "medium",
    "expected_evidence_tools": ["get_order_record", "get_provisioning_log", "search_knowledge_base", "get_inventory_status"],
    "expected_insufficient_evidence": false
  },
  {
    "scenario_id": "unknown-error-1",
    "order_id": "ORD-90001",
    "archetype": "provisioning_failure_unknown_code",
    "expected_root_cause": null,
    "expected_confidence_min": "low",
    "expected_evidence_tools": ["get_order_record", "get_provisioning_log", "search_knowledge_base"],
    "expected_insufficient_evidence": true
  },
  {
    "scenario_id": "conflict-1",
    "order_id": "ORD-90006",
    "archetype": "conflicting_evidence",
    "expected_root_cause": null,
    "expected_confidence_min": "low",
    "expected_evidence_tools": ["get_order_record", "get_billing_status", "get_provisioning_log"],
    "expected_insufficient_evidence": true
  }
]
```

**`eval/judge.py`** — LLM-as-judge (Section 3's prompt from
`03-EVALUATION.md`), separate model call from the agent's own reasoning.

**`eval/metrics.py`** — computes, from a batch of `(scenario, actual_result)`
pairs: root cause accuracy (via judge), evidence citation correctness
(cross-check `evidence` field entries against the audit log), false-
confidence rate, insufficient-evidence precision/recall, **per-specialist**
tool-call efficiency, p50/p95 latency.

**`eval/run_eval.py`** — orchestrates: seed each scenario's `order_id` into
Phase 1's DBs (idempotently), call `POST /diagnose`, collect results, run
`metrics.py`, print a report.

**Definition of done — the Core/Extended gate:** `python eval/run_eval.py`
runs all 20-25 scenarios end-to-end and prints a real metrics report.
Numbers don't need to be perfect, but every metric must be measured. Any
FR6/FR9 scenario that fails gets fixed here, before Phase 8.

## Phase 7 — Demo UI [CORE]

**Goal:** `ui/app.py` — Streamlit, resolving `01-REQUIREMENTS.md` Section 8's
last open question.

- Text input for `order_id` → button → calls `POST /diagnose` → renders
  `DiagnosisOutput` (root cause, confidence badge, evidence list,
  recommended action)
- **Decide during this phase:** pull the correlation-ID's log lines (Phase
  5) and render them as a live step-by-step trace, or skip that and show
  only the final result — call this once Phase 5's logging is in hand and
  the actual UI effort is clear, not before.

**Definition of done:** a runnable `streamlit run ui/app.py` demo, working
end to end against real (mock) data, presentable to a coworker.

---

## 🚧 Gate: Core complete, eval suite passing — Extended work starts only after this 🚧

---

## Phase 8 — Neo4j knowledge graph [EXTENDED]

**Goal:** swap Phase 2's Chroma-only `search_knowledge_base` for
vector + graph (`02-ARCHITECTURE.md` Section 5, FR8).

- `graph/schema.cypher` — constraints/indexes for `(:Customer)`, `(:Order)`,
  `(:Circuit)`, `(:Address)`, `(:ErrorCode)` node types and the
  relationships from Section 5.1/5.2
- `graph/populate.py` — loads Phase 1's seed data + the error-code/incident
  graph (including `ERR_4471`'s documented cause/resolution/related
  incidents) into the real Neo4j Aura instance via `neo4j_for_adk.py`
- `search_knowledge_base` updated: vector search (existing) run in parallel
  with a Cypher traversal query for the error code, results merged
- Re-run `eval/run_eval.py` in full — confirm no regression from Phase 2's
  Chroma-only version

**Definition of done — isolated first, then merged, per the same
isolation-then-integration pattern as `02-ARCHITECTURE.md` Section 13:**
- `tests/test_kb_vector.py` — vector search alone (Chroma only, no Neo4j
  connection needed) returns the expected semantic match for `ERR_4471`.
- `tests/test_kb_graph.py` — graph traversal alone (a direct Cypher query
  via `neo4j_for_adk.py`, no vector search involved) returns the correct
  cause/resolution/related-incident chain for `ERR_4471`.
- `tests/test_kb_merged.py` — `search_knowledge_base`'s actual merge logic,
  verifying both results land in the combined response correctly.
- Only then: eval suite still passing; a live query for `ERR_4471` returns
  both the vector-matched explanation *and* the graph-traversed resolution
  path + related incident IDs.

## Phase 9 — Kafka event-driven trigger [EXTENDED]

**Goal:** FR7's async half.

- `docker-compose.yml` extended with a Kafka broker (KRaft mode, no
  separate Zookeeper needed)
- `events/topics.py` — topic creation: `order.created`,
  `order.payment_authorized`, `order.provisioning_failed`,
  `order.provisioning_succeeded`, `order.billing_hold_applied`,
  `diagnosis.events`
- Phase 1's mock services updated to publish to their respective topics as
  they process requests
- `events/consumer.py` — subscribes to `*_failed`/`*_hold_applied`, calls
  the **same** compiled supervisor graph from Phase 4, publishes results +
  audit trail to `diagnosis.events`

**Definition of done — isolated first, then integrated:**
- `tests/test_consumer.py` — the consumer's own handler function called
  directly with a **constructed fake event payload** and a **fake/injected
  graph invocation** (no real Kafka broker, no real supervisor graph) —
  verifies the handler correctly parses the event into an `order_id`,
  calls the graph with it, and publishes to `diagnosis.events`. Same
  isolation principle as the supervisor's `synthesize_diagnosis` tests
  (`02-ARCHITECTURE.md` Section 13) — fast, no infrastructure dependency.
- Full integration test (the original v1 check): publishing a real
  `provisioning_failed` event for `ORD-88213` via a producer script,
  against the real Docker Kafka broker and the real compiled supervisor
  graph, triggers a full diagnosis with zero API calls involved, visible
  on `diagnosis.events`.

## Phase 10 — Full observability stack [EXTENDED]

**Goal:** upgrade Phase 5's flat JSON logs to the real 3-part stack
(Section 7).

- OpenTelemetry SDK instrumentation — one trace per diagnosis request,
  child spans per tool call and per graph node (both specialist graphs and
  the supervisor graph)
- `/metrics` endpoint (Prometheus text format) — counters/histograms for
  latency per node, tool-call counts, `insufficient_evidence` rate
- `correlation_id` (Phase 5) becomes the trace ID, threading logs/traces/
  metrics together

**Definition of done:** one diagnosis request visible end-to-end in a local
trace viewer (e.g. Jaeger via Docker), not just readable as flat log lines.

## Phase 11 — AWS hosting migration: Bedrock + API Gateway [EXTENDED]

**Goal:** Section 6's model-hosting decision and Section 14's ingress
decision, both made real — paired in one phase since both are "move this
layer to AWS-managed infra," neither touches agent logic.

**Bedrock (Section 6):**
- Swap `ChatAnthropic`/`ChatOpenAI` calls for `langchain_aws.ChatBedrock`
  (Claude via Bedrock) across `plan_next_action`, `evaluate_evidence`,
  `synthesize_diagnosis`, and `eval/judge.py`
- Bedrock Guardrails configuration for PII/content filtering (Section 10)

**API Gateway (Section 14):**
- Provision an HTTP API Gateway in front of the FastAPI app's existing
  deployment
- Configure an API key + usage plan (throttle limits) — replaces Phase 5's
  in-app `verify_api_key` dependency and `slowapi` limiter for traffic
  arriving through the gateway
- Phase 5's `tests/test_api.py` is untouched — still tests the app's own
  logic directly via `TestClient`; the gateway's config is verified
  separately, at deployment time, not via pytest (Section 14's stated
  testing boundary)

- Re-run `eval/run_eval.py` once more — confirm the Bedrock swap didn't
  regress anything (API Gateway has no bearing on eval results, since it's
  purely ingress)

**Definition of done:** eval suite passing against the Bedrock-hosted
model; a request through the deployed API Gateway (valid key) reaches the
app and returns a correct diagnosis; a request with no/invalid key is
rejected by the gateway itself, before it ever reaches the app.

## Phase 12 — Polish

- Final README pass; architecture diagram embedded and current
- A short, rehearsed demo script/walkthrough
- `docker compose up` brings up the full stack (mock services + agent API
  + Kafka + Neo4j connection + observability) in one command

---

## Explicitly not scheduled — [OPTIONAL / v2]

SageMaker triage classifier, semantic response caching, CI/CD eval-gating,
deeper PII redaction beyond Bedrock Guardrails, Kubernetes/Terraform —
named in `02-ARCHITECTURE.md` Section 10, a deliberate later choice, not a
promise made now.

## Rough sizing (relative, not a schedule commitment)

| Phase | Relative size |
|---|---|
| 0 — Scaffolding | S |
| 1 — Mock services | M |
| 2 — Tools | S |
| 3 — Specialists | M |
| 4 — Supervisor | M |
| 5 — FastAPI | S |
| 6 — Evaluation harness | M-L |
| 7 — Demo UI | S |
| 8 — Neo4j | M |
| 9 — Kafka | M |
| 10 — Observability | M |
| 11 — Bedrock + API Gateway | M |
| 12 — Polish | S |

---

**Nothing above has been built.** Awaiting review — approve as-is, request
changes, or flag anything that still needs to change before Phase 0 starts.
