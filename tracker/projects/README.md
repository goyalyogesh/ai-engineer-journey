# Projects Index

5 fintech AI projects + 1 warmup + 1 bonus. Each lives in its own GitHub repo, linked here.

| # | Project | Days | Status | Repo | Live Demo | Blog |
|---|---------|------|--------|------|-----------|------|
| Warmup | Email Classifier | 5, 9-12 | ✅ | [folder](https://github.com/goyalyogesh/ai-engineer-journey/tree/main/tracker/projects/email-class-project-1) | [live](https://yogi-ai-email.streamlit.app) | — |
| 1 | SEC 10-K Analyzer | 13-37 | 🔲 | — | — | — |
| 2 | Invoice AP Auditor | 38-67 | 🔲 | — | — | — |
| 3 | Equity Research Agent | 68-92 | 🔲 | — | — | — |
| 4 | Indian Tax Document Analyzer | 93-117 | 🔲 | — | — | — |
| 5 | Indian Earnings Digest (B2C) | 38-150 | 🔲 | — | — | — |
| 6 (Bonus) | Fine-Tuned Financial Sentiment Classifier | 151-158 | 🔲 | — | — | — |

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

### Project 6 (Bonus): Fine-Tuned Financial Sentiment Classifier
- LoRA-fine-tune a small open model (e.g. Llama 3.2 1B/3B) on financial sentiment/classification, benchmarked against the same task prompted zero-shot on the base model
- Deliverable: results table (baseline vs. fine-tuned), a FastAPI inference endpoint, a Streamlit comparison demo, deployed on Hugging Face Spaces
- Stack: Hugging Face Transformers, PEFT (LoRA), TRL, FastAPI, Streamlit
- Purpose: closes the one real gap in Projects 1-5 (all API-based — prompting/RAG/agents, zero hands-on model training). Not a second specialization — a scoped, 8-day hedge against "have you fine-tuned a model?" in broader ML Engineer interviews
- Added after Day 150 — see `CURRICULUM.md` → "Bonus: Phase 7" for the full day-by-day plan and the honest timing tradeoff of placing it here
