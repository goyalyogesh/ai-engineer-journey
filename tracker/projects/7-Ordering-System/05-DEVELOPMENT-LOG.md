# Development Log — Order Diagnosis Agent

**What this file is, and why it's different from `04-BUILD-PLAN.md`:**
the build plan is the *spec* — what should get built, in what order, with
what schemas and signatures. This file is the *record* — what actually
happened while building it, phase by phase: decisions made in the moment
(not just at planning time), things that came up during real implementation
that the plan didn't anticipate, what got verified and how, and anything
that changed as a result. Read this to understand **how** the project
actually got built, not just what the end state looks like.

Updated after each phase completes — not written all at once up front.

## How development actually works on this project (the process itself)

For each phase, in order:

1. **Re-read that phase's section in `04-BUILD-PLAN.md`** — the schemas,
   signatures, and definition of done are the source of truth for what
   "done" means. Don't start from memory.
2. **Build exactly that phase — nothing from later phases.** The Core →
   Extended gate (`04-BUILD-PLAN.md`, between Phase 7 and 8) exists because
   building ahead means debugging unvalidated agent logic *and* unfamiliar
   infrastructure at the same time. The same logic applies at the
   individual-phase level, not just the Core/Extended boundary.
3. **Verify the phase's definition of done for real** — run the actual
   command, read the actual output. A phase isn't done because the code
   "looks right"; it's done because the DoD's specific check passed and
   the output was actually inspected. This project has been through 4 full
   documentation review passes precisely because "looks right" and "is
   right" turned out to be different things more than once during planning
   — the same discipline applies to code.
4. **Log it here** — what got built, what (if anything) diverged from the
   plan and why, what verification actually showed, current status.
5. **Comment the code per `04-BUILD-PLAN.md`'s "Code comprehensibility"
   principle** — the *why*, tied to the specific doc section that justifies
   it, as you write each piece — not a cleanup pass at the end.
6. **Move to the next phase** only once the current one's DoD is genuinely
   met — not "mostly," not "close enough."

This is the same plan-then-verify discipline used throughout this whole
project's planning phase, just applied to code now instead of docs.

---

## Phase 0 — Scaffolding

**Status:** ✅ Done.

**What was built:**
- Directory tree per `04-BUILD-PLAN.md`'s repo structure — created
  directly inside this project folder (`tracker/projects/7-Ordering-System/`),
  not a separate nested `order-diagnosis-agent/` folder, matching how other
  projects in this curriculum (e.g. `0-email-class-project/`) keep docs and
  code together in one project folder rather than adding an extra nesting
  layer the build plan's tree diagram implied but wasn't actually load-bearing.
- `.env.example` — exact content from the build plan's Phase 0 spec.
- `pyproject.toml` — real, working package config (not just a task list of
  dependency names): `[project.optional-dependencies].dev` holds
  `pytest`/`pytest-asyncio`/`pytest-cov` separately from runtime deps,
  `[tool.pytest.ini_options]` sets `asyncio_mode = "auto"` so async test
  functions work without per-test decorators, and `testpaths = ["tests"]`
  so `pytest` from the project root finds the right directory without
  extra flags.
- `docker-compose.yml` — one service block per mock backend, `build:`
  contexts pointing at each `mock_services/<name>/` folder, ports
  8001-8004, `env_file: .env`. Commands intentionally left as comments —
  Phase 1 is where each service gets real app code to actually run.
- `tests/conftest.py` — left empty per the plan, with a comment explaining
  *why* it's empty (fixtures get added per-phase as things exist to
  fixture against) rather than a blank file with no context.
- Empty placeholder `.py` files for every module the later phases will
  fill in (`agent/state.py`, `agent/tools.py`, `agent/supervisor.py`,
  `agent/specialists/{billing_crm,network}.py`, each mock service's
  `main.py`/`models.py`/`db.py`/`seed_data.py`, `api/main.py`, `ui/app.py`,
  `eval/{judge,metrics,run_eval}.py`) plus `__init__.py` files so these are
  real importable Python packages from Phase 1 onward, not just files.
- `env/` — a local venv, matching the convention already used elsewhere in
  this curriculum (`month-1/env`, `python/env`) rather than a global
  install.

**What diverged from the plan, and why:** the build plan's repo-structure
diagram showed a root folder literally named `order-diagnosis-agent/`. That
folder wasn't created — this project folder already serves as the root,
and adding another nesting level would just be a longer path to the same
files, with no actual benefit. Noted here specifically because it's the
kind of small deviation-from-spec worth writing down rather than silently
doing something slightly different from the documented plan.

**Verification actually performed (not assumed):**
- `pip install -e ".[dev]"` — ran for real, succeeded, installed the full
  dependency tree (FastAPI, LangGraph, LangChain, Chroma, pytest + plugins,
  ~140 packages resolved cleanly).
- `pytest` — ran for real: **0 tests collected, 0 errors** — exactly the
  Phase 0 DoD.
- `docker-compose.yml` — **could not run `docker compose config`**, since
  Docker isn't installed on this machine. Fell back to validating it's at
  least syntactically correct YAML (`python3 -c "import yaml; yaml.safe_load(...)"`
  — passed), which is a weaker check than the plan's actual DoD. **Flagged
  honestly rather than claimed as fully verified** — full `docker compose
  config` validation is still owed once Docker is available, or at the
  latest by Phase 1 when the services need to actually run.

**Next:** Phase 1 — mock backend microservices.

---

## Phase 1 — Mock backend microservices

**Status:** ✅ Done.

**What was built:**
- 4 real FastAPI services (CRM, Billing, Provisioning, Inventory), each
  with its own SQLite DB, own `db.py`/`models.py`/`seed_data.py`/`main.py`,
  built from the CRM service as a verified template before replicating the
  pattern to the other 3 (verified once, then scaled, rather than writing
  all 4 blind and debugging 4x the surface area at once).
- All endpoints exactly per `04-BUILD-PLAN.md`'s spec: `GET /orders/{id}`,
  `GET /billing/{customer_id}`, `GET /provisioning/{order_id}`,
  `GET /inventory?circuit_id=...&address=...`.
- 7 seed records per service (one per `03-EVALUATION.md` archetype),
  cross-referenced consistently: `customer_id` matches between CRM and
  Billing, `order_id` matches between CRM and Provisioning, and every
  `circuit_id` Provisioning produces has a matching Inventory record.
  Verified programmatically (not just by eye) — see below.
- `tests/test_mock_services.py` — 10 tests: happy path + 404 per service,
  the inventory 400 case, and one dedicated test reproducing the full
  `ORD-88213` worked example across all 4 services in one test.

**Decisions made during implementation (not anticipated at planning time):**
- **Latency/failure config is read fresh per-request, not cached at module
  import time.** The plan's pseudocode read `MOCK_FAILURE_RATE` etc. once;
  in practice that would make `pytest`'s `monkeypatch.setenv` overrides
  silently not apply after the first import of a given service's `main.py`
  module (Python caches imports). Reading env vars inside the request
  handler itself fixes this and is barely more code.
- **Seeding happens automatically on FastAPI startup** (`lifespan` context
  manager calls `init_db()` + `seed()`), rather than requiring a separate
  manual script run — guarantees the service is queryable immediately
  whenever it starts, including under `TestClient` and under `uvicorn`
  directly, with no separate setup step to forget.

**Verification actually performed:**
- `pytest -v` — **10/10 passed**, including the full `ORD-88213`
  cross-service reproduction.
- `pytest --cov=mock_services --cov-report=term-missing` — **98% → then
  100%** after adding the one missing case (inventory's 400 "no lookup
  key provided" path) that coverage surfaced as untested.
- All 4 services actually started via real `uvicorn` processes and queried
  via real `curl` (not just `TestClient`) — output matched the worked
  example exactly, including the `404` for `ORD-88213`'s address in
  Inventory.
- Cross-service seed data consistency checked **programmatically**
  (a Python one-liner comparing the actual ID sets across all 4 seed
  files), not just asserted by eye during construction — all three checks
  (CRM↔Billing customer_ids, CRM↔Provisioning order_ids, Provisioning↔
  Inventory circuit_ids) passed.

---

## Review — Phase 0 and Phase 1 together

Requested explicitly after Phase 1 completed. Two real gaps found, both fixed:

1. **No `.gitignore` existed**, and real clutter (`*.db` files,
   `__pycache__/`, `*.egg-info/`) was already sitting in the repo,
   unignored — would have been committed on the next `git add`. This was
   really a Phase 0 gap (scaffolding should have included it) that only
   became visible once Phase 1 actually generated files worth ignoring.
   **Fixed:** `.gitignore` added, covering the venv, Python artifacts,
   `.env` (secrets — `.env.example` stays committed, `.env` doesn't),
   generated `.db` files, and test/coverage artifacts.

2. **`docker-compose.yml` was left half-finished.** Phase 0 wrote it with
   `build:` contexts and a comment saying "command left for Phase 1" —
   but Phase 1's own definition of done in `04-BUILD-PLAN.md` explicitly
   requires `docker compose up` to work, and neither a `Dockerfile` nor a
   per-service `requirements.txt` had ever been specified anywhere in the
   plan, for any phase. **Fixed:** added both per service, and updated
   `04-BUILD-PLAN.md` itself (not just the code) so this isn't a
   surprise for whoever reads the plan next. Two decisions worth flagging:
   - Each service's `requirements.txt` is deliberately **minimal**
     (`fastapi`, `uvicorn`, `pydantic`, `python-dotenv`) — not the full
     agent dependency stack, which would be wasteful and would quietly
     undermine the "own process, own container" independence claim already
     made in `02-ARCHITECTURE.md` Section 3.3.
   - Each `Dockerfile` **recreates the `mock_services.<name>` package path
     inside the image**, so the same relative imports that work locally
     (and in the pytest suite) work identically in the container — avoids
     local-vs-Docker behavioral drift, which this project's documentation
     has already spent real effort hunting down elsewhere.

**Docker verification — closed out.** Docker was installed after the above
was written. Ran the actual, previously-owed checks:
- `docker compose config` — passed once a local `.env` existed (copied from
  `.env.example`; `.env` itself is gitignored on purpose, so this step is
  expected on any fresh clone, not a bug).
- `docker compose build` — all 4 images (`crm`, `billing`, `provisioning`,
  `inventory`) built successfully from their Dockerfiles.
- `docker compose up -d` — all 4 containers started and reported `Up`.
- Re-ran the exact `ORD-88213` worked-example `curl` sequence from the
  Phase 1 verification above, this time against the **containerized**
  services on their published ports (8001-8004) instead of local `uvicorn`
  processes — output matched exactly: CRM `status: created`, Billing
  `payment_status: authorized` / `hold_active: false`, Provisioning
  `status: failed` / `error_code: ERR_4471`, Inventory `404` for the
  address lookup.
- `docker compose down` — clean teardown, containers and network removed.

**One environment quirk found and worked around, not a project bug:** on
this machine, Docker Desktop is installed on an external SSD volume
(`/Volumes/SSD-Yogesh/Applications/Docker.app`), and the `/usr/local/bin/docker`
symlink meant to point at it was stale (pointed at an old, differently-named
volume mount, and at another point in the session `/Applications/Docker.app`
— itself a symlink to the SSD path — was also missing). Neither is a
`docker-compose.yml`/Dockerfile problem; both are local `PATH`/symlink
issues specific to this machine's setup, worked around by invoking Docker
via its real path directly. Noted here in case it recurs.

**Everything else checked out** — schemas match the plan exactly, endpoint
behavior matches, seed data is internally consistent, and the full
`ORD-88213` worked example now reproduces correctly end-to-end both via
local `uvicorn` and via Docker.

**Next:** Phase 2 — tools layer.

---

## Phase 2 — Tools layer

**Status:** ✅ Done.

**What was built:**
- `agent/tools.py` — `ToolResult`, `call_with_retry` (Section 3.6's one-retry-
  then-"unavailable" policy), and the 5 `@tool` functions
  (`get_order_record`, `get_billing_status`, `get_provisioning_log`,
  `get_inventory_status`, `search_knowledge_base`) exactly per
  `04-BUILD-PLAN.md`'s signatures, each calling its Phase 1 mock service
  over real HTTP via `httpx`.
- `search_knowledge_base` — Chroma-only this phase (Neo4j/GraphRAG merge is
  Phase 8). Seeded a small knowledge base (4 documents) covering the error
  codes actually seeded in `mock_services/provisioning/seed_data.py`
  (`ERR_4471`, `ERR_BILL_MISMATCH`, plus general billing-hold and
  inventory-address-mismatch facts) — `ERR_9999` deliberately has no KB
  entry, matching that seed record's own comment ("deliberately absent
  from the KB"), so the golden-dataset scenario using it genuinely
  exercises `insufficient_evidence`.
- `tests/test_tools.py` — one test per tool run against **real** Phase 1
  services (Section 13's testing table), plus the 404-is-evidence-not-an-
  error case, the missing-lookup-key case, the `search_knowledge_base`
  missing-API-key degradation case, and the `MOCK_FAILURE_RATE=1.0`
  retry-then-"unavailable" case.

**Decisions made during implementation (not anticipated at planning time):**
- **404 is a successful call with no data, not a failure.** The build
  plan's `ToolResult` schema has `success`/`error`, but didn't say how a
  404 should map onto those fields. Decided during implementation: a
  confirmed absence is itself diagnostic evidence here — Inventory
  returning 404 for `ORD-88213`'s address **is** the worked example's
  root-cause signal (`02-ARCHITECTURE.md` Section 1), not an error to
  retry away. So 404 → `success=True, data=None`, never retried; only a
  5xx/network failure triggers the retry-then-"unavailable" path. This
  distinction wasn't spelled out in `04-BUILD-PLAN.md` and would have
  been easy to get wrong (e.g. treating every non-200 as a failure).
- **`agent/tools.py` calls `load_dotenv()` itself**, rather than relying on
  another module (e.g. a mock service's `main.py`) having already loaded
  it as an import-order side effect. Caught during testing: the first test
  run passed only because `tests/test_tools.py` happens to import
  `mock_services.crm.main` (which calls `load_dotenv()`) before importing
  `agent.tools` — an accidental dependency, not real correctness. Fixed by
  making the module self-sufficient, then re-verified in a clean
  subprocess with no pre-loaded environment.
- **`search_knowledge_base` degrades explicitly when `OPENAI_API_KEY` is
  unset**, returning `success=False, error="unavailable: OPENAI_API_KEY
  not configured"` rather than raising or silently returning empty
  results — the same "unavailable" contract as an unreachable HTTP service
  (Section 3.6), applied to a missing credential instead of a network
  failure.
- **A real `OPENAI_API_KEY` was needed to actually test `search_knowledge_base`**
  (embeddings require a real call). Asked before acting (not assumed):
  the user confirmed reusing the key already present in this repo's
  `python/.env` (same person, same machine, other curriculum days already
  use it), copied into this project's own git-ignored `.env` — never
  committed, never printed to the terminal transcript in full.
- **`tests/test_tools.py` starts the 4 mock services as real `uvicorn`
  servers in background threads** (session-scoped `autouse` fixture),
  rather than reusing `test_mock_services.py`'s in-process `TestClient`
  approach — required because the tools under test make real outbound
  HTTP calls to `CRM_SERVICE_URL` etc., so something has to actually be
  listening on those ports. This is the same "real, not further-mocked"
  approach Section 13 calls for, just automated instead of the manual
  `curl` verification used in Phase 1.

**Verification actually performed:**
- `pytest tests/test_tools.py -v` — **9/9 passed** on first run (before the
  `load_dotenv()` fix was even made — the gap was caught by reasoning
  about *why* it passed, not by a failure).
- Re-verified `agent/tools.py` standalone in a clean subprocess (`env -i`,
  no inherited shell environment) after the `load_dotenv()` fix, calling
  `get_order_record` directly — confirmed it correctly read
  `CRM_SERVICE_URL` from its own `.env` load (failed only because no
  server was running in that isolated check, which was expected and
  correct).
- Full suite + coverage: `pytest -v --cov=agent --cov-report=term-missing`
  — **20/20 passed, 97% coverage** on `agent/tools.py` (2 uncovered lines
  are the Chroma singleton-reuse and already-seeded-KB branches — both
  legitimately only exercised on a truly cold start, not gaps).
- Manually inspected real `search_knowledge_base` output for the query
  "why did provisioning fail with ERR_4471" — top match was exactly the
  `err-4471` document, confirming the seeded KB actually retrieves the
  right fact, not just that the call succeeds.
- Confirmed `.env` (containing the real API key) and `chroma_kb_data/`
  (the persisted vector store) both stay git-ignored via `git check-ignore`
  — including `agent_checkpoints.db`, the SQLite checkpointer file Phase 4
  will create, already covered by the existing `*.db` pattern ahead of
  time.

**Next:** Phase 3 — specialist sub-agents.

---

## Phase 3 — Specialist sub-agents

**Status:** ✅ Done.

**What was built:**
- `agent/state.py` — `SpecialistState`, `SPECIALIST_MAX_ITERATIONS` (read
  from env, Section 8), `SpecialistFinding`. Also added `SupervisorState`,
  `DiagnosisOutput`, `CONFIDENCE_ORDER` in the same file (Phase 4's types),
  since `state.py` is the single file the repo tree assigns to all of
  these and they're pure data declarations with no behavior yet — inert
  until Phase 4 wires them up.
- `agent/specialists/_shared.py` — **new file, not in the original repo
  tree.** Holds the node-factory + graph-wiring logic both specialists
  share (04-BUILD-PLAN.md Phase 3 describes billing_crm.py/network.py as
  "the same shape"). Added during implementation to avoid duplicating that
  logic verbatim in both files — `billing_crm.py`/`network.py` each now
  just declare their own tool set + role string and call
  `build_specialist_graph(...)`.
- `agent/specialists/billing_crm.py`, `agent/specialists/network.py` — the
  2 specialist subgraphs, each a real compiled LangGraph graph
  (`plan → execute → evaluate`, conditional loop back to `plan`), wired
  per Section 3.8's domain split.
- `tests/test_specialists.py` — 13 tests: prompt-construction and
  response-handling tested independently (Section 13), the domain-split
  guarantee (each specialist's tool dict contains only its own tools),
  `should_continue`'s 3 branches, node-level tests with a fake LLM + fake
  tools (DI, Section 8/13), and one full-stack test running the real
  `network_graph` (real LLM, real tools, real mock services) against
  `ORD-88213`.
- Promoted the real-mock-services fixture from `tests/test_tools.py` into
  `tests/conftest.py` (session-scoped, autouse) — needed by
  `test_specialists.py` too now, so it belongs shared rather than
  duplicated.

**Decisions made during implementation (not anticipated at planning time):**
- **`SpecialistState` needed 3 more fields than `04-BUILD-PLAN.md`'s
  3-field pseudocode** (`pending_tool_calls`, `complete`,
  `preliminary_assessment`). LangGraph nodes only communicate through
  state — the plan's pseudocode named the *loop shape* but not how
  `plan_next_action`'s decision reaches `execute_tool`, or how
  `evaluate_evidence`'s verdict reaches both `should_continue` and the
  eventual `SpecialistFinding`. Added and documented in `agent/state.py`
  itself, not silently.
- **Prompt construction and response handling are separate, independently
  testable functions** (`build_plan_prompt`/`parse_plan_response`,
  `build_evaluate_prompt`), per Section 13's explicit "test isolation for
  LLM calls" requirement — makes it possible to test "is the right
  evidence actually in the prompt" and "does the node parse a model
  response correctly" as two separate, fast, deterministic tests, neither
  requiring the real model.
- **Tool-domain restriction is enforced structurally, not just by
  prompt wording** — each specialist's `bind_tools()` call only ever sees
  its own tools dict, so it's structurally impossible for the Network
  specialist to request `get_billing_status`, not just discouraged by the
  prompt. Verified directly (`test_billing_crm_specialist_does_not_own_network_tools`
  etc.), not just implied.
- **`ChatOpenAI(model="gpt-4o-mini", temperature=0)`** — same model/config
  already established in `16Langchain-Deep-Interview.ipynb`, reused for
  consistency rather than picking a new default.

**Verification actually performed:**
- `pytest tests/test_specialists.py -v` — **13/13 passed**, including the
  real full-stack test (real OpenAI call + real mock services): the
  Network specialist, given only `order_id=ORD-88213`, genuinely called
  `get_provisioning_log` and `get_inventory_status`, surfaced
  `error_code=ERR_4471` in its evidence, and produced a non-empty
  `preliminary_assessment` — reproducing the worked example end-to-end
  through actual agent reasoning, not scripted control flow.
- Full suite together: `pytest -v --cov=agent --cov-report=term-missing` —
  **33/33 passed, 98% coverage**. `agent/specialists/_shared.py`,
  `billing_crm.py`, `network.py` all at 100%. `agent/state.py`'s only
  uncovered lines (60-65) are `DiagnosisOutput`'s validator — expected,
  since that's Phase 4 territory not yet exercised by any test.
- Re-ran the Phase 1 + Phase 2 suites together with Phase 3's to confirm
  the `conftest.py` fixture promotion didn't break either — all still
  passed together in one session.

**Next:** Phase 4 — supervisor agent.

---

## Phase 4 — Supervisor agent

**Status:** ✅ Done.

**What was built:**
- `agent/supervisor.py` — `dispatch_specialists` (asyncio.gather on both
  specialist subgraphs, wraps each result into a `SpecialistFinding`),
  `synthesize_diagnosis`, and the compiled supervisor graph
  (`dispatch → synthesize`), per Section 3.8's subgraph-as-node mechanism.
- `agent/state.py` — added `SupervisorState`, `DiagnosisOutput`,
  `CONFIDENCE_ORDER` (these were already written in Phase 3 alongside
  `SpecialistState`, since `state.py` is one shared file — see Phase 3's
  entry above).
- `tests/test_supervisor.py` — 11 tests: 5 fast, deterministic tests for
  `apply_precedence_and_pipeline_rules` (conflict resolved by precedence,
  unresolvable conflict, pipeline-order rule, single clean cause, no clear
  cause), 2 node-level tests with a fake LLM (normal path + the exception
  fallback path), 1 direct test of `DiagnosisOutput`'s own invariant, 1 for
  `_evidence_to_text`'s "specialist didn't run" branch, and 2 real
  end-to-end tests: the full supervisor graph (real specialists, real LLM)
  against `ORD-88213`, and the real `AsyncSqliteSaver` checkpointer
  round-tripping a diagnosis through disk.

**Decisions made during implementation (not anticipated at planning time):**
- **Redesigned `synthesize_diagnosis` into an LLM-classification step +
  deterministic Python rule-application step**, instead of one
  `.with_structured_output()` call doing everything as
  `04-BUILD-PLAN.md`'s original pseudocode implied. `02-ARCHITECTURE.md`
  Section 3.7 explicitly wants the precedence rule to be "an auditable
  design decision, not an implicit bias buried in a prompt" — a single
  LLM call silently applying both the precedence rule and the pipeline-
  order rule inside its own reasoning would be exactly that. Also matches
  Section 13's stated Definition of Done much more literally: "fast,
  isolated... these run in milliseconds" only makes sense if the rule
  itself is plain code, not something whose correctness depends on how an
  LLM happens to apply an instruction that day. `apply_precedence_and_pipeline_rules()`
  is now real, synchronous, LLM-free Python — retroactively documented in
  `04-BUILD-PLAN.md` itself, not just here.
- **`SqliteSaver` → `AsyncSqliteSaver`.** The build plan's pseudocode named
  the sync `SqliteSaver`; tried it first, got `NotImplementedError: The
  SqliteSaver does not support async methods` immediately on
  `.ainvoke()`, since every node in this graph is `async def`. Switched to
  `langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver` (added
  `langgraph-checkpoint-sqlite` to `pyproject.toml`), confirmed working
  with a minimal standalone repro before wiring it into `supervisor.py` for
  real.
- **The checkpointer can't be built at plain module-import time.**
  `AsyncSqliteSaver.from_conn_string(...)` is itself an async context
  manager, and there's no running event loop at import time to enter it
  with. Solved with a lazy, cached `get_supervisor_graph()` async
  function instead of a module-level `compiled = ...` — proper lifecycle
  ownership (closing the connection on shutdown) is explicitly left to
  Phase 5's FastAPI `lifespan`, not built here since there's no server
  process yet to own it.
- **The safety-net fallback (`insufficient_evidence=True` on any synthesis
  error) is deliberately broad** (`except Exception`), not narrowed to a
  specific exception type. Justification: `DiagnosisOutput`'s own
  validator exists specifically to make a contradictory diagnosis
  unconstructable (Section 3.4) — if construction fails for *any* reason
  (a bad LLM response, a bug in the rule-application code, anything),
  crashing the whole `/diagnose` request would be strictly worse than
  degrading to an honest "couldn't produce a valid diagnosis, escalate."
  Same "report explicitly, never silently drop" philosophy already used
  for tool failures (Section 3.6), applied one level up.

**Verification actually performed:**
- Fast tests only: `pytest tests/test_supervisor.py -v -k "not full_stack and not checkpoints_for_real"`
  — **9/9 passed in ~1 second**, confirming the rule-application logic and
  the fake-LLM node tests really are the fast, deterministic layer Section
  13 asks for.
- Real tests: the full-stack test against `ORD-88213` — confirmed
  `insufficient_evidence=False`, `confidence="high"` (billing is clean in
  the worked example; only the Network specialist found a real, confirmed
  problem, so this correctly took the single-cause branch, not the
  pipeline-order branch), and `root_cause` referencing the circuit/`ERR_4471`
  finding.
- The checkpointer test: ran the real graph through `get_supervisor_graph()`
  with a real `thread_id`, confirmed the `.db` file was actually created on
  disk, then independently re-read the persisted state back via
  `graph.aget_state(config)` and confirmed it matched — proving the
  `AsyncSqliteSaver` fix genuinely works end-to-end, not just that it
  imports without error. Also confirmed a second call to
  `get_supervisor_graph()` returns the identical cached graph object
  (singleton behavior actually verified, not just assumed).
- Full suite together: `pytest -v --cov=agent --cov-report=term-missing` —
  **44/44 passed.** `agent/state.py` and `agent/supervisor.py` both at
  **100%** coverage after adding 2 small targeted tests for branches
  coverage first flagged (`DiagnosisOutput`'s validator actually raising,
  and `get_supervisor_graph()`'s cache-hit path). `agent/tools.py` remains
  at 99% (1 line, the already-explained Chroma re-seed branch from Phase
  2). Overall: **99%.**

**Next:** Phase 5 — FastAPI serving layer.

---

## Phase 5 — FastAPI serving layer

**Status:** ✅ Done.

**What was built:**
- `agent/observability.py` — **new file, not in the original repo tree.**
  Core-tier structured JSON-lines logging (`02-ARCHITECTURE.md` Section
  12): a `contextvars.ContextVar` carries the current request's
  `correlation_id` without threading it through every Phase 2-4 function
  signature, `log_event()` appends one JSON line per call, and
  `log_node_transitions()` is a decorator applied to each specialist/
  supervisor node.
- `agent/tools.py` — `call_with_retry` now logs one `tool_call` event per
  attempt (success or handled failure).
- `agent/specialists/_shared.py`, `agent/supervisor.py` — every node
  factory's returned function now wrapped with `@log_node_transitions`.
- `api/main.py` — `POST /diagnose`: `verify_api_key` (401 on missing/wrong
  `X-API-Key`), `slowapi`-based rate limiting (10/min, keyed by API key,
  not IP), a `get_graph_dependency` FastAPI dependency wrapping Phase 4's
  `get_supervisor_graph()`, and a `lifespan` that now properly owns the
  checkpointer's open/close lifecycle (the ownership Phase 4 explicitly
  deferred here).
- `tests/test_api.py` — 5 tests: missing-key 401, wrong-key 401, valid-key
  200 (both using a `FakeGraph` via `app.dependency_overrides` — the API
  layer's own contract, independent of the real agent logic), rate-limit
  429 (looping requests until one trips, not a fragile exact-count
  assumption), and one real end-to-end test with no stub at all,
  asserting the log file's lines all share one `correlation_id` and
  include both `tool_call` and `node_start`/`node_end` events.

**Decisions made during implementation (not anticipated at planning time):**
- **Rate limiting keyed by API key, not IP** — `slowapi`'s default
  `key_func` (`get_remote_address`) doesn't match this section's own
  "10 req/min **per API key**" wording; used a custom `key_func` reading
  the `X-API-Key` header instead.
- **`get_graph_dependency` as a real FastAPI dependency**, not a bare call
  inside the route handler — makes the DoD's "independent of whether the
  agent logic underneath it is real or stubbed" claim literally true via
  `app.dependency_overrides`, rather than requiring monkeypatching.
- **`correlation_id` doubles as the checkpointer's `thread_id`** — one ID
  per request links its log trace to its persisted graph state.
- **`lifespan` now opens the checkpointer at startup and closes it at
  shutdown** — closing the loop Phase 4 explicitly left open ("proper
  lifecycle ownership belongs to Phase 5's FastAPI lifespan").
- **Rate-limit test loops until a 429 shows up** (up to 15 requests),
  rather than asserting the exact 11th request fails — avoids a fragile
  hard-coded count assumption while still proving the limit is enforced,
  and used `Limiter.reset()` in an autouse fixture so tests don't bleed
  rate-limit budget into each other.

**A false alarm, corrected:** while preparing to curl-test the real
server, the project's local `.env` (git-ignored, never committed) was
found to contain a `GOOGLE_API_KEY` line and a real `ANTHROPIC_API_KEY`
value that hadn't been explicitly added by any command run in this
session — flagged directly rather than silently overwritten, and
temporarily stripped back down to only the explicitly-authorized
`OPENAI_API_KEY` value out of caution. The user confirmed they'd added
those two keys themselves, so both were restored. `.env` now has all
three real keys (`OPENAI_API_KEY`, `GOOGLE_API_KEY`, `ANTHROPIC_API_KEY`)
plus a locally-generated `API_KEY` value for the curl verification below.
`GOOGLE_API_KEY` still isn't read by any code in this project (harmless
either way) — noted here only because flagging-then-restoring is worth a
one-line record, not because anything was actually wrong.

**Verification actually performed:**
- `pytest tests/test_api.py -v` — **5/5 passed**, including the real
  end-to-end test.
- **Real, running-process curl verification** (not just `TestClient`) —
  started all 4 mock services via real `uvicorn` processes plus the real
  FastAPI app (`uvicorn api.main:app`), then:
  - No `X-API-Key` header → `401 {"detail":"invalid or missing API key"}`
  - Wrong key → same `401`
  - Correct key → `200`, with the exact expected diagnosis:
    `root_cause: "Provisioning failed due to no circuit assigned for the
    service address (ERR_4471)."`, `confidence: "high"`,
    `insufficient_evidence: false` — matching the worked example.
  - Inspected the resulting `agent_events.jsonl` directly: **47 log
    lines, all sharing one `correlation_id`**, tracing the full request
    from `supervisor.dispatch_specialists` through both specialists'
    complete `plan → execute → evaluate` loops (including their tool
    calls) through `supervisor.synthesize_diagnosis` — a genuine,
    grep-able, correlation-ID-linked trace of one real request, exactly
    what the Definition of Done asks for.
- Full suite together: `pytest -v --cov=agent --cov=api --cov-report=term-missing`
  — **49/49 passed.** `agent/observability.py` and `api/main.py` both
  **100%** coverage. `agent/tools.py` remains at 99% (same 1 known,
  already-explained Chroma re-seed line from Phase 2). Overall: **99%.**
- Confirmed `pip install -e ".[dev]"` still resolves cleanly with
  `slowapi` added to `pyproject.toml`, and confirmed `agent_events.jsonl`/
  `agent_checkpoints.db` (both regenerated by the real tests/curl run)
  stay correctly git-ignored (`*.jsonl` pattern added to `.gitignore`
  alongside the existing `*.db` pattern).

**Next:** Phase 6 — evaluation harness.
