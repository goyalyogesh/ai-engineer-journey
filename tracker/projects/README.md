# Projects Index

5 fintech AI projects + 1 warmup. Each lives in its own GitHub repo, linked here.

| # | Project | Days | Status | Repo | Live Demo | Blog |
|---|---------|------|--------|------|-----------|------|
| Warmup | Email Classifier | 9-12 | 🔲 | — | — | — |
| 1 | SEC 10-K Analyzer | 13-37 | 🔲 | — | — | — |
| 2 | Invoice AP Auditor | 38-67 | 🔲 | — | — | — |
| 3 | Equity Research Agent | 68-92 | 🔲 | — | — | — |
| 4 | Indian Tax Document Analyzer | 93-117 | 🔲 | — | — | — |
| 5 | Indian Earnings Digest (B2C) | 38-150 | 🔲 | — | — | — |

**Status legend:** 🔲 Not started · 🟡 In progress · ✅ Shipped · 💰 Monetized

## Project specs

### Warmup: Email Classifier
- Email → JSON {category, urgency, sentiment, action_items, summary}
- Stack: Python + Instructor + Pydantic + Streamlit
- Goal: prove I can ship in 4 days

### Project 1: SEC 10-K Analyzer
- Q&A over SEC filings with citations, multi-doc, YoY comparison
- Stack: FastAPI + Streamlit + LangChain + Pinecone + Anthropic Claude
- Customer: investment analysts

### Project 2: Invoice AP Auditor
- Extract invoices, audit for fraud/errors/duplicates, savings dashboard
- Stack: FastAPI + Next.js + PostgreSQL + Instructor + Claude vision
- Customer: AP teams, controllers

### Project 3: Equity Research Agent
- Multi-tool agent: SEC + news + transcripts + ratios → research report PDF
- Stack: LangGraph + FastAPI + Streamlit + multiple data APIs
- Customer: hedge funds, analysts

### Project 4: Indian Tax Document Analyzer
- Form 16 / ITR analysis + old vs new regime comparison + tax Q&A
- Stack: FastAPI + Streamlit + Indian tax rules engine + RAG over Income Tax Act
- Customer: Indian salaried professionals (CA-adjacent SaaS)

### Project 5: Indian Earnings Digest (B2C STARTUP)
- Newsletter on Nifty 50 earnings — sentiment, key takeaways, alerts
- Free weekly, ₹199/mo daily + custom watchlists
- Stack: VPS cron + Postgres + Resend + Next.js + Razorpay
- Customer: Indian retail investors
- **Treat as startup — apply to YC W26 Day 100**
