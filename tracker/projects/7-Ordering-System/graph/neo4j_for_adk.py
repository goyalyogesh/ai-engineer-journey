"""
Neo4j connection client for this project's knowledge graph (Phase 8,
02-ARCHITECTURE.md Section 5).

Vendored from `python/neo4j_for_adk.py` (the "Agentic Knowledge Graph
Construction" coursework's own connection module, itself a flattened,
portable single-file version of the official companion repo's client) --
that module's own docstring already documents it as designed to be
dropped into any project via `from neo4j_for_adk import graphdb`, so it's
copied here rather than re-implemented, per 02-ARCHITECTURE.md Section 5's
"real infrastructure reuse, not new tooling for its own sake" note. Only
change from the original: this project's `.env` points `NEO4J_URI` at a
local Docker container, not the Neo4j Aura instance the original notebook
used -- that Aura instance had been auto-paused-then-deleted from
inactivity by the time this phase started (05-DEVELOPMENT-LOG.md's Phase 8
entry has the full story); this file's own connection logic needed no
changes for that, since it already reads `NEO4J_URI`/`NEO4J_USERNAME`/
`NEO4J_PASSWORD` from the environment rather than hardcoding Aura.

This is a *synchronous* driver (`neo4j.GraphDatabase`, not the async
variant) -- call sites inside this project's async agent code
(`agent/tools.py`) wrap `graphdb.send_query(...)` in `asyncio.to_thread(...)`,
the same pattern already used for Chroma's synchronous `similarity_search`
call in Phase 2.
"""

import os
import re
import atexit
import logging
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from dotenv import load_dotenv
from neo4j import GraphDatabase, Result

load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_URI = "bolt://localhost:7687"
ALLOWED_SCHEMES = {"neo4j", "neo4j+s", "neo4j+ssc", "bolt", "bolt+s", "bolt+ssc"}


class Neo4jConfig:
    """Reads NEO4J_URI / NEO4J_USERNAME / NEO4J_PASSWORD, falling back to a
    combined NEO4J_DSN if the separate vars aren't set."""

    def __init__(
        self,
        uri: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
    ):
        if uri is None and os.environ.get("NEO4J_DSN"):
            # Fallback: parse a combined DSN string into the same fields
            parsed = urlparse(os.environ["NEO4J_DSN"])
            uri = f"{parsed.scheme}://{parsed.hostname}:{parsed.port or 7687}"
            username = username or parsed.username or "neo4j"
            password = password or parsed.password
            database = database or (parsed.path or "").lstrip("/") or "neo4j"

        self.uri = uri or os.environ.get("NEO4J_URI", DEFAULT_URI)
        self.username = username or os.environ.get("NEO4J_USERNAME", "neo4j")
        self.password = password or os.environ.get("NEO4J_PASSWORD")
        self.database = database or os.environ.get("NEO4J_DATABASE", "neo4j")

        scheme = self.uri.split("://", 1)[0] if "://" in self.uri else ""
        if scheme not in ALLOWED_SCHEMES:
            raise ValueError(
                f"Invalid Neo4j URI scheme '{scheme}'. Allowed: {sorted(ALLOWED_SCHEMES)}"
            )

    @property
    def auth(self):
        return (self.username, self.password)


def load_neo4j_config() -> Neo4jConfig:
    config = Neo4jConfig()
    logger.info(f"Neo4j expected at: {config.uri}")
    return config


def make_driver(config: Neo4jConfig):
    return GraphDatabase.driver(config.uri, auth=config.auth)


def sanitize(cypher_name: str) -> str:
    """Very basic string sanitization when a query param is not possible."""
    return re.sub(r"[.,\-:$()><{}\[\]'\"`\s]", "", cypher_name)


def is_write_query(query: str) -> bool:
    """Check if the Cypher query performs any write operations."""
    return re.search(r"\b(MERGE|CREATE|SET|DELETE|REMOVE|ADD)\b", query, re.IGNORECASE) is not None


def tool_success(key: str, result: Any) -> Dict[str, Any]:
    return {"status": "success", key: result}


def tool_error(message: str) -> Dict[str, Any]:
    return {"status": "error", "error_message": str(message) if message is not None else "Unknown error"}


def to_python(value):
    from neo4j.graph import Node, Relationship, Path
    from neo4j import Record
    import neo4j.time

    if isinstance(value, Record):
        return {k: to_python(v) for k, v in value.items()}
    elif isinstance(value, dict):
        return {k: to_python(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [to_python(v) for v in value]
    elif isinstance(value, Node):
        return {"id": value.id, "labels": list(value.labels), "properties": to_python(dict(value))}
    elif isinstance(value, Relationship):
        return {
            "id": value.id,
            "type": value.type,
            "start_node": value.start_node.id,
            "end_node": value.end_node.id,
            "properties": to_python(dict(value)),
        }
    elif isinstance(value, Path):
        return {
            "nodes": [to_python(node) for node in value.nodes],
            "relationships": [to_python(rel) for rel in value.relationships],
        }
    elif isinstance(value, neo4j.time.DateTime):
        return value.iso_format()
    elif isinstance(value, (neo4j.time.Date, neo4j.time.Time, neo4j.time.Duration)):
        return str(value)
    else:
        return value


def result_to_adk(result: Result) -> Dict[str, Any]:
    eager_result = result.to_eager_result()
    records = [to_python(record.data()) for record in eager_result.records]
    return tool_success("records", records)


class Neo4jForADK:
    """A wrapper for querying Neo4j which returns ADK-friendly responses."""

    def __init__(self, config: Optional[Neo4jConfig] = None):
        self._config = config or load_neo4j_config()
        self._driver = make_driver(self._config)
        logger.debug(f"Neo4j driver initialized at {self._config.uri}")

    def get_driver(self):
        return self._driver

    def get_config(self):
        return self._config

    def close(self):
        return self._driver.close()

    def send_query(self, cypher_query, parameters=None) -> Dict[str, Any]:
        session = self._driver.session(database=self._config.database)
        try:
            result = session.run(cypher_query, parameters or {})
            return result_to_adk(result)
        except Exception as e:
            return tool_error(str(e))
        finally:
            session.close()


# Ready-to-use singleton -- `from graph.neo4j_for_adk import graphdb`.
# Creating the driver here does NOT open a network connection yet (the neo4j
# driver is lazy) -- the first real connection attempt happens on the first
# graphdb.send_query(...) call.
graphdb = Neo4jForADK()
atexit.register(graphdb.close)
