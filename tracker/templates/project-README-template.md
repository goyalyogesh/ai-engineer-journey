# [Project Name]

> [One-sentence value prop. Example: "AI auditor for accounts payable. Catches fraud, errors, and policy violations in every invoice."]

[![Live demo](https://img.shields.io/badge/demo-live-brightgreen)](https://your-demo-url.com)
[![Blog post](https://img.shields.io/badge/blog-medium-blue)](https://medium.com/your-post)

![Demo GIF](docs/demo.gif)

---

## Problem

[2-3 sentences. Who has the problem? What does it cost them? Why hasn't it been solved?]

## Solution

[2-3 sentences. What this does. How it's different from alternatives.]

## Live demo

🔗 **[Try it now →](https://your-demo-url.com)**

## Tech stack

| Layer | Tech |
|-------|------|
| Frontend | Streamlit / Next.js |
| Backend | FastAPI |
| LLM | Anthropic Claude Sonnet (primary), GPT-4o (fallback) |
| Vector DB | Pinecone |
| Database | PostgreSQL (Supabase) |
| Cache | Redis (Upstash) |
| Observability | LangSmith |
| Evals | Ragas |
| Deploy | Render (backend), Vercel (frontend) |

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for full system design.

```
[Quick ASCII diagram or screenshot]
```

## Key features

- ✨ [Feature 1 — what's special about it]
- 🚀 [Feature 2]
- 🔒 [Feature 3]
- 📊 [Feature 4]

## How it works (technical)

1. [Step 1 — e.g., User uploads PDF]
2. [Step 2 — e.g., Claude vision extracts structured data]
3. [Step 3 — e.g., Audit rules + LLM second opinion]
4. [Step 4 — e.g., Results stored in Postgres + dashboard]

## Quick start (local dev)

```bash
git clone https://github.com/[user]/[repo]
cd [repo]
uv sync
cp .env.example .env  # add API keys
uv run uvicorn src.main:app --reload
```

Open http://localhost:8000

## Project structure

```
src/
  main.py           # FastAPI entry
  models.py         # Pydantic models
  llm.py            # LLM clients
  retrievers.py     # RAG/vector logic
  audit_rules.py    # Business logic
tests/
  test_*.py         # Pytest
evals/
  eval_dataset.json # Ground truth
  run_evals.py      # Eval runner
docs/
  demo.gif
  architecture.png
```

## Evals

| Metric | Score | Date |
|--------|-------|------|
| Faithfulness (Ragas) | 0.92 | YYYY-MM-DD |
| Answer relevancy | 0.88 | YYYY-MM-DD |
| Extraction accuracy | 95% | YYYY-MM-DD |

Run evals: `uv run python evals/run_evals.py`

## Cost analysis

- Per request: ~$0.XX
- Monthly @ 10K requests: ~$XX
- Optimizations: prompt caching saves ~70%, Haiku for ambiguous-only saves ~40%

## Lessons learned

1. **[Lesson 1]** — what surprised you, what you'd do differently
2. **[Lesson 2]** — production vs demo gap
3. **[Lesson 3]** — cost or performance insight

## Roadmap

- [ ] [Next feature]
- [ ] [Performance improvement]
- [ ] [Integration]

## Built by

[Your name] — building AI engineer journey publicly at [github.com/you/ai-engineer-journey](https://github.com/goyalyogesh/ai-engineer-journey)

## License

MIT
