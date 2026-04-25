# Architecture — [Project Name]

> System design doc for [Project Name]. Format mirrors a real system design interview answer.
> Used both as project documentation AND as interview prep material.

---

## 1. Requirements

### Functional requirements
- [What the system MUST do]
- [Core user actions]
- [Key outputs]

### Non-functional requirements
- **Latency:** [target p50, p95, p99]
- **Throughput:** [requests/sec, users concurrent]
- **Availability:** [uptime % target]
- **Consistency:** [strong / eventual / session]
- **Cost:** [target $ per request or per month]

### Scale assumptions
- Users: [N total, M active monthly]
- Data: [N documents, M GB total, growth rate]
- Traffic: [N req/sec average, M peak]
- Storage growth: [N GB/month]

### Out of scope
- [What this system explicitly doesn't do]

---

## 2. API design

### Key endpoints

```
POST /api/v1/[resource]
  request:  { ... }
  response: { ... }
  errors:   400, 401, 429, 500

GET /api/v1/[resource]/{id}
  ...
```

### Authentication
- [API key / JWT / OAuth]

### Rate limiting
- [N req/min per user/IP]

---

## 3. Data model

### Core entities

```
[Entity1]
- id: UUID (PK)
- field: type
- created_at: timestamp
- ...

[Entity2]
- id: UUID (PK)
- entity1_id: UUID (FK)
- ...
```

### Indexes
- `[entity].(field)` — for [query pattern]
- `[entity].(field1, field2)` composite — for [query pattern]

### Why this schema
- [Tradeoff explanation: normalization vs denormalization, etc.]

---

## 4. High-level architecture

```
[User] → [Frontend (Vercel/Streamlit)]
            ↓
         [API Gateway / FastAPI on Render]
            ↓
    ┌───────┼───────────┐
    ↓       ↓           ↓
[Postgres] [Redis] [Vector DB]
              ↑           ↑
              └───[LLM API]
```

### Components
- **Frontend:** [tech, why]
- **API layer:** [tech, why]
- **Business logic:** [structure]
- **Storage:** [breakdown — relational, cache, vector, blob]
- **External services:** [LLMs, payment, email, etc.]

### Data flow (key user journey)
1. User does X
2. Frontend sends request to /api/v1/...
3. API validates, fetches from DB
4. LLM call w/ context
5. Response cached in Redis
6. Returned to user

---

## 5. Deep dive — [Critical component]

### Why this component matters
[1-2 sentences on why this is the hardest/most important part]

### How it works
[Detailed explanation — algorithms, data structures, edge cases]

### Tradeoffs
- Chose X over Y because [reason]
- Cost of this choice: [downside]

---

## 6. Scaling strategy

### Current state (Day 1)
- Single FastAPI instance on Render
- Postgres free tier
- Pinecone free tier
- Handles: [N users, M req/sec]

### 10x growth (1K → 10K users)
- Add Redis cache for [hot queries]
- Postgres connection pooling (PgBouncer)
- Pinecone paid tier
- Estimated cost: $X/month

### 100x growth (10K → 100K users)
- Horizontal scaling — multiple API instances behind load balancer
- Postgres read replicas
- Background job queue (Celery/RQ)
- CDN for static assets
- Estimated cost: $X/month

### 1000x growth (100K → 1M users)
- Sharding strategy: shard by [user_id / region]
- Multi-region deployment
- Custom vector DB (Weaviate self-hosted)
- Dedicated SRE infrastructure
- Estimated cost: $X/month

---

## 7. Tradeoffs & alternatives considered

### What I chose
| Decision | Choice | Why |
|----------|--------|-----|
| LLM | Claude Sonnet | Better at structured output |
| Vector DB | Pinecone | Free tier, managed |
| Backend | FastAPI | Async, Pydantic native |
| Hosting | Render | $5 tier, easy Docker |

### What I explicitly rejected
| Alternative | Why not |
|-------------|---------|
| OpenAI GPT-4 | More expensive, weaker at long context |
| Self-hosted vector DB | Ops overhead vs benefit not worth it |
| Django | More than I need, FastAPI fits AI use case |

---

## 8. Failure modes & mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| LLM API down | LangSmith alert | Fallback to OpenAI |
| LLM rate limit | 429 response | Tenacity exponential backoff |
| Vector DB slow | p95 > 500ms | Cache top queries in Redis |
| Postgres connection exhaust | Connection error | PgBouncer pool |
| Hallucinated output | User reports | LLM-as-judge eval, ground in retrieved context |

---

## 9. Observability

- **Logging:** structured JSON, sent to [tool]
- **Tracing:** LangSmith for LLM calls, OpenTelemetry for HTTP
- **Metrics:** request rate, latency p50/p95/p99, error rate, LLM cost per req
- **Alerts:** Pagerduty for downtime, Slack for cost spikes
- **Dashboards:** [tool — Grafana, Datadog, custom Streamlit]

---

## 10. Security

- API auth: [JWT / API key / OAuth]
- Input validation: Pydantic at every boundary
- Secrets: env vars, never in code (use AWS Secrets Manager / Vault for prod)
- Rate limiting: [approach]
- HTTPS only
- For sensitive data (financial): encryption at rest + in transit, audit logs

---

## 11. Future work / known limitations

- [What you'd do with more time]
- [Known bugs / tech debt]
- [Features intentionally cut for v1]

---

**Last updated:** YYYY-MM-DD
**Maintainer:** [you]
