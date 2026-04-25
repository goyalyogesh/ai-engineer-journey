# Claude Code project context

> Copy this file to the root of every project repo. Claude Code reads it automatically.

You are pair-programming with a .NET dev learning Python AI for fintech.

## Tech stack (locked)

- **Python 3.12** with type hints everywhere
- **Pydantic v2** for all data models (no plain dicts at boundaries)
- **uv** for package management (not pip)
- **VS Code** as editor
- **FastAPI** for backends, **Streamlit** for fast demos, **Next.js** for production frontends
- **LangChain** primary framework, **LlamaIndex** secondary
- **Instructor** for structured LLM outputs
- **LangSmith** for tracing, **Ragas** for RAG evals
- **Anthropic Claude** as default LLM, OpenAI as fallback
- **Pinecone** for vector DB (production), **Chroma** local
- **PostgreSQL** via Supabase or VPS, **Redis** via Upstash
- **Docker** for containers, **GitHub Actions** for CI

## Code style

- Type hints on every function signature and Pydantic model
- Async by default for I/O (httpx, asyncpg, async LLM clients)
- Tests with pytest — small, fast, focused
- No comments unless WHY is non-obvious. Don't restate what code does.
- Functions short, single-purpose. Prefer composition over inheritance.
- Errors at boundaries (validate input), trust internals.

## Communication style

- Be direct and concise. Fragments OK.
- Don't pad with "Sure! I'd be happy to help"
- Don't summarize what you did at end of every response
- If proposing changes, show the tradeoff briefly

## Domain context

I'm building **fintech AI** — bias toward financial document patterns:
- SEC filings (10-K, 10-Q, 8-K)
- Earnings call transcripts
- Invoices (PDFs, multimodal)
- Indian tax docs (Form 16, ITR)
- BSE/NSE filings
- Income statements, balance sheets, cash flow

Use Anthropic Claude as default — better at long context + structured output.

## Anti-patterns (don't suggest these)

- ❌ Local LLMs (Ollama, llama.cpp, vLLM) — out of scope
- ❌ C#/.NET bridges (Semantic Kernel, Azure OpenAI in C#) — Python only
- ❌ Over-engineering — ship over perfect, MVP first
- ❌ Premature optimization — measure first, optimize later
- ❌ Multiple frameworks for same job — LangChain mastery > 5 frameworks shallow
- ❌ Comments restating code
- ❌ Long docstrings — single-line max unless really needed
- ❌ Mocking LLMs in tests when integration test is feasible

## Specific guidance

- **For RAG:** chunk size 512-1024 tokens w/ overlap 100. Use Pinecone metadata filters. Always cite sources in response.
- **For agents:** LangGraph state machines > raw tool-calling loops. Max 10 iterations. Always add human-in-the-loop for destructive actions.
- **For extraction:** Instructor + Claude vision for PDFs. Pydantic validation on output. Retry with exponential backoff via Tenacity.
- **For cost:** Claude Haiku for high-volume cheap tasks, Sonnet for ambiguous/complex. Use prompt caching for repeated context.
- **For deployment:** FastAPI + Docker → Render/Fly.io. Streamlit → Streamlit Cloud or HF Spaces. Always set up health check endpoint.

## Current project

[Edit this section per project]
- **Project:** [name]
- **Goal:** [one sentence]
- **Phase:** [1-6 from CURRICULUM.md]
- **Day window:** [e.g., Days 13-37]
- **Live demo:** [URL once deployed]

## Reference files

- Curriculum: `../CURRICULUM.md`
- Daily plans: `../daily-plans/`
- Tracker: `../tracker/`
