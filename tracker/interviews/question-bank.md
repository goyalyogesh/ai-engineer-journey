# Interview Question Bank

Comprehensive prep for AI Engineer interviews. Updated as you do real interviews — log every question asked.

## Categories

1. [LLM System Design](#llm-system-design)
2. [Coding (Python + LLM)](#coding-python--llm)
3. [Behavioral STAR examples](#behavioral-star-examples)
4. [Project deep-dive questions](#project-deep-dive-questions)
5. [General system design](#general-system-design)
6. [Domain (Fintech)](#domain-fintech)
7. [Curveballs / take-homes](#curveballs--take-homes)

---

## LLM System Design

### High-frequency questions

1. **Design a RAG system for 10M documents**
   - Discuss: chunking strategy, embedding model, vector DB choice, retrieval pipeline (hybrid?), reranking, citation handling, eval framework, cost/latency tradeoffs
   - Watch for: hallucination handling, multi-tenancy, freshness (when docs update)

2. **Design an LLM-powered customer support system at Stripe scale**
   - Discuss: routing (AI vs human), context retrieval (past tickets), tool calling (refunds, account changes), guardrails, escalation logic, human-in-loop, fallback to humans, eval pipeline

3. **Design an eval pipeline for an LLM product**
   - Discuss: ground truth dataset creation, metrics (Ragas, custom), LLM-as-judge, regression detection, A/B testing infra, dashboards, alert thresholds

4. **Design a multi-tenant LLM API gateway**
   - Discuss: rate limiting per tenant, model routing (Haiku vs Sonnet), prompt caching, cost attribution, observability per tenant, billing integration

5. **Design a code-review AI bot (like CodeRabbit or Greptile)**
   - Discuss: codebase ingestion, PR diff analysis, comment posting, false positive handling, repo-specific context, GitHub App vs API, scaling

6. **Design an LLM agent for personal productivity (calendar/email)**
   - Discuss: tool use, OAuth integrations, action confirmation, undo logic, memory persistence, security (data isolation), trust boundaries

### Patterns to know cold

- **RAG architecture:** ingestion pipeline → chunking → embedding → vector store → retrieval (k-NN + filters) → reranking → context assembly → LLM → response w/ citations
- **Agent loop:** plan → tool call → observe → re-plan → answer (ReAct, plan-and-execute, supervisor patterns)
- **Eval pipeline:** dataset → run → score (Ragas/LLM-judge) → compare to baseline → alert on regression
- **Cost optimization:** caching (semantic + prompt), model routing (Haiku → Sonnet on confidence), batching, fine-tuning small models

---

## Coding (Python + LLM)

### Common live-coding questions

1. **Write a function that calls Claude with retries and exponential backoff**
   - Use Tenacity or write manual loop. Handle 429, 500, timeout. Async preferred.

2. **Implement a Pydantic model for an SEC filing extraction**
   - Nested fields (CompanyInfo, FinancialData[], RiskFactor[]). Validators for dates, currency.

3. **Write a RAG retrieval function w/ Pinecone + reranking**
   - Embed query → Pinecone query w/ metadata filter → Cohere rerank → return top-K.

4. **Build a streaming LLM endpoint in FastAPI**
   - Use `StreamingResponse` + Anthropic streaming SDK. Send chunks as SSE.

5. **Write a function calling tool definition for OpenAI/Anthropic**
   - JSON schema for tool, handler function, parsing the LLM's tool call response.

6. **Implement semantic caching**
   - Hash query embedding, lookup in Redis, return if similarity > 0.95, else call LLM.

### LeetCode-style (for FAANG/GCC interviews)

Practice 30 mediums, focus on:
- Arrays / strings (sliding window, two pointers)
- Hash maps (anagrams, lookups)
- Trees / graphs (BFS, DFS, traversals)
- Dynamic programming (basic — coin change, longest substring)
- Heap / priority queue (top K)

Skip: hard DP, hard graphs, segment trees (not needed for AI Engineer roles).

---

## Behavioral STAR examples

Prep 5-10 stories. Use STAR format: Situation, Task, Action, Result.

### "Tell me about a difficult bug you fixed"

- **Situation:** [.NET project — stuck on async deadlock OR AI project — RAG returning wrong docs]
- **Task:** [What needed to be fixed, deadline]
- **Action:** [Steps taken — debugging, hypotheses, what worked]
- **Result:** [Outcome — measurable if possible]

### "Tell me about a time you disagreed with a manager"
[Your story — be diplomatic, focus on outcome, show you can navigate conflict]

### "Tell me about a project where you took ownership"
[Pick Project 5 — built solo, found niche, monetized]

### "Why are you transitioning from .NET to AI?"
- I see AI as the next platform shift (like web 2.0 was for me)
- My .NET work taught me production systems thinking — applies directly to LLM ops
- Built 5 production AI projects in 6 months to prove I can ship in this space
- Long-term I want to build, not maintain

### "Why this company specifically?"
[Tailor per company — research their product, mention specific technical decisions you'd want to work on]

### "Tell me about a time you failed"
- Be honest, focus on what you learned
- Good example: chose wrong framework early in Project X, had to migrate at Day 30
- Bad example: anything that makes you look like a victim

### "Where do you see yourself in 5 years?"
- Senior AI Engineer or founder
- Either lead a team building production AI at fintech scale, OR run my own AI fintech company
- (Tailor based on whether interviewing for IC track vs leadership)

---

## Project deep-dive questions

For EACH of your 5 projects, prep:

### Project deep-dive checklist
1. **Problem & users:** Who uses this? What's the pain? How big is the market?
2. **Architecture:** Walk me through the system end-to-end (have ARCHITECTURE.md memorized)
3. **Technical decisions:** Why X over Y? What did you reject?
4. **Hardest problem:** What was the biggest technical challenge?
5. **Failures:** What did you try that didn't work? What would you do differently?
6. **Scale:** How would this handle 10x / 100x users?
7. **Eval:** How do you know it actually works? Show me numbers.
8. **Cost:** What's the unit economics?
9. **Production:** What broke in prod? How did you fix it?
10. **What's next:** Roadmap, what's the v2?

**Practice each deep-dive in 5 min** — if you can't pitch a project clearly in 5 min, you don't understand it well enough.

---

## General System Design

If interviewing at FAANG/GCCs, you'll get classic SD problems too:

1. Design Twitter / Instagram feed
2. Design URL shortener
3. Design Uber / DoorDash
4. Design Slack / WhatsApp
5. Design YouTube
6. Design Dropbox
7. Design Tinder
8. Design Yelp / Google Maps

For each, know:
- Functional + non-functional requirements
- API design
- Data model + sharding
- Caching strategy
- Load balancing
- CAP theorem tradeoffs
- Failure modes

Resource: github.com/donnemartin/system-design-primer

---

## Domain (Fintech)

Expect questions specific to fintech roles:

1. **Compliance:** What's PCI-DSS? GDPR? SOC2? How would you architect for compliance from day 1?
2. **Data sensitivity:** How do you handle PII / financial data in LLM context? (Tokenization, redaction, on-prem inference)
3. **Audit logging:** How do you log every LLM decision for regulatory audits?
4. **Hallucination risk:** How do you prevent an LLM from giving wrong financial advice?
5. **Settlement systems:** Basic understanding of T+1, T+2 settlement, FX, OTC vs exchange-traded
6. **Indian fintech:** UPI architecture, NPCI, RBI, KYC norms
7. **US fintech:** ACH, wire, FedNow, real-time payments
8. **Regulation 101:** SEC, FINRA, Dodd-Frank basics for US; SEBI for India

**Tip:** You don't need to be an expert — show you understand the questions and can ramp fast.

---

## Curveballs / take-homes

### Common take-homes (4-8 hr scope)

1. **Build a RAG over [their company's docs]** — show eval, deployment, README
2. **Build an LLM agent that does X** — show tool design, error handling
3. **Improve their existing prompt for higher accuracy** — show A/B method
4. **Design + implement an eval framework for X** — show metrics, dataset creation
5. **Reduce the cost of their LLM usage by 50%** — show before/after

### Take-home rules

- **Quality > speed.** Polish README, ship live demo, write tests.
- **Document your decisions.** Why X over Y. Show thought process.
- **Identify the trap.** Most take-homes have one — find it.
- **Don't overengineer.** They want to see you SHIP.
- **Time-box honestly.** If you spent 10 hrs not 4, say so in README.

---

## Questions YOU should ask THEM (every interview)

End every interview w/ 2-3 questions. Shows you're evaluating them:

1. **For engineers:** "What's the biggest technical challenge the team is wrestling with right now?"
2. **For managers:** "What does success look like for this role in 6 months?"
3. **For founders:** "What's keeping you up at night about the product?"
4. **For everyone:** "What's the worst part of working here? Be honest." (signals confidence)
5. **About AI maturity:** "Where is the team on the eval-driven development curve? Are you doing offline evals, online evals, both?"
6. **About culture:** "How does the team handle disagreement on technical decisions?"
7. **About growth:** "What does the AI Engineer career path look like here? IC or management track?"

---

## Real interview log

Track every question asked in real interviews. Build the corpus over time.

| Date | Company | Round | Question | How I answered | What I learned |
|------|---------|-------|----------|---------------|----------------|
| | | | | | |

---

## Resources

- **Hello Interview** (YouTube + paid course) — modern + AI focused
- **System Design Primer** — github.com/donnemartin/system-design-primer
- **DDIA book** — Designing Data-Intensive Applications (read alongside)
- **chiphuyen.com** — ML system design specifically
- **AI Engineering** by Chip Huyen (book) — comprehensive
- **Pramp / interviewing.io** — free mock interviews (do 3 minimum)
- **Levels.fyi** — comp benchmarks
- **Glassdoor / Blind** — company-specific question logs
