"""POST /diagnose (02-ARCHITECTURE.md Section 12's "API ingress: auth +
rate limiting -- In-app" row; Section 14 covers the Extended-tier API
Gateway ahead of this app, not built here).
"""
import os
import uuid
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from agent.observability import correlation_id_var
from agent.state import DiagnosisOutput
from agent.supervisor import close_supervisor_graph, get_supervisor_graph, initial_supervisor_state

load_dotenv()


def _api_key_from_request(request: Request) -> str:
    # Rate limiting is scoped per API key (04-BUILD-PLAN.md Phase 5's DoD:
    # "10 req/min per API key"), not per client IP -- slowapi's default
    # get_remote_address key_func would rate-limit the wrong thing here.
    return request.headers.get("X-API-Key", "unknown")


limiter = Limiter(key_func=_api_key_from_request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm the checkpointer up front (Phase 4 deferred its proper lifecycle
    # ownership to "Phase 5's FastAPI lifespan" -- this is that promise
    # kept): opens the AsyncSqliteSaver connection once at startup rather
    # than lazily on the first request, and closes it cleanly on shutdown
    # instead of leaking the connection for the life of the process.
    await get_supervisor_graph()
    yield
    await close_supervisor_graph()


app = FastAPI(title="Order Diagnosis Agent API", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


class DiagnoseRequest(BaseModel):
    order_id: str


async def verify_api_key(request: Request) -> None:
    # Header-based check against API_KEY (02-ARCHITECTURE.md Section 10's
    # "cheap to build, pull into Core" item). An unset API_KEY means
    # nothing can ever authenticate -- same "fail closed, never silently
    # open" posture as agent/tools.py's missing-OPENAI_API_KEY handling.
    expected = os.environ.get("API_KEY")
    provided = request.headers.get("X-API-Key")
    if not expected or provided != expected:
        raise HTTPException(status_code=401, detail="invalid or missing API key")


async def get_graph_dependency():
    # A real FastAPI dependency, not a bare module-level import, so tests
    # can override it via app.dependency_overrides (Section 8's DI
    # principle, applied at the API layer) -- Phase 5's own Definition of
    # Done wants the API layer's auth/rate-limit contract testable
    # "independent of whether the agent logic underneath it is real or
    # stubbed."
    return await get_supervisor_graph()


@app.post("/diagnose", dependencies=[Depends(verify_api_key)])
@limiter.limit("10/minute")
async def diagnose(
    request: Request,
    body: DiagnoseRequest,
    response: Response,
    graph=Depends(get_graph_dependency),
) -> DiagnosisOutput:
    # correlation_id doubles as the LangGraph thread_id -- one ID cleanly
    # links a request's structured log lines (agent/observability.py) to
    # its checkpointed graph state, rather than tracking two separate IDs.
    correlation_id = str(uuid.uuid4())
    token = correlation_id_var.set(correlation_id)
    try:
        config = {"configurable": {"thread_id": correlation_id}}
        result = await graph.ainvoke(initial_supervisor_state(body.order_id), config=config)
        # Exposed as a response header (not folded into the DiagnosisOutput
        # body, which Phase 5 already committed to as the return type) so
        # Phase 6's eval harness can pull this one request's log lines back
        # out for the evidence-citation and tool-call-efficiency metrics.
        response.headers["X-Correlation-Id"] = correlation_id
        return result["diagnosis"]
    finally:
        correlation_id_var.reset(token)
