# System Design Practice Notes

18 system design problems over 150 days. 1 hr each Saturday (first hour of 5-hr block).

## Problem log

| Day | Problem | Type | Status | Notes |
|-----|---------|------|--------|-------|
| 41 | Design URL shortener | Generic | 🔲 | sd-day041.md |
| 47 | Design Twitter / Instagram feed | Generic | 🔲 | sd-day047.md |
| 53 | Design Uber / ride matching | Generic | 🔲 | sd-day053.md |
| 59 | Design Slack / messaging system | Generic | 🔲 | sd-day059.md |
| 65 | Design payment processor | Fintech | 🔲 | sd-day065.md |
| 71 | Design RAG system at scale (10M docs) | LLM | 🔲 | sd-day071.md |
| 77 | Design distributed cache | Generic | 🔲 | sd-day077.md |
| 83 | Design AI customer support system | LLM | 🔲 | sd-day083.md |
| 89 | Design real-time fraud detection | Fintech | 🔲 | sd-day089.md |
| 95 | Design eval pipeline for LLM apps | LLM | 🔲 | sd-day095.md |
| 101 | Design transaction processing (1M TPS) | Fintech | 🔲 | sd-day101.md |
| 107 | Design multi-tenant LLM gateway | LLM | 🔲 | sd-day107.md |
| 113 | Design recommendation system | Generic | 🔲 | sd-day113.md |
| 119 | Design notification system | Generic | 🔲 | sd-day119.md |
| 125 | Design agent orchestration system | LLM | 🔲 | sd-day125.md |
| 131 | Design backtesting infrastructure | Fintech | 🔲 | sd-day131.md |
| 137 | Design reconciliation pipeline | Fintech | 🔲 | sd-day137.md |
| 143 | Real 45-min mock SD interview | Mock | 🔲 | sd-day143.md |

## Format per problem (1-page design doc)

1. **Requirements** (functional + non-functional, scale assumptions)
2. **API design** (key endpoints, request/response)
3. **Data model** (schemas, relationships)
4. **High-level architecture** (components + data flow diagram)
5. **Deep dive** (1-2 critical components — caching, sharding, etc.)
6. **Tradeoffs** (what you chose, what you didn't, why)
7. **Scaling** (how this evolves at 10x, 100x, 1000x)

## Resources

- **DDIA book** — `tracker/notes/ddia.md`
- **ByteByteGo** — bytebytego.com (newsletter free)
- **Hello Interview YouTube** — modern + AI focused
- **System Design Primer** — github.com/donnemartin/system-design-primer
- **chiphuyen.com** — ML system design specifically
- **Anthropic engineering blog** — production LLM patterns
