# AI Engineer 150-Day Curriculum — Fintech AI Track (v2 — Hybrid Musk/Altman)

**Target:** .NET → AI Engineer (Fintech focus)
**Profile:** Canadian citizen, Indian heritage, planning Hyderabad relocation
**Schedule:** 15 hrs/week, 6 working days (Mon-Thu + Sat + Sun, Fri OFF)
**Duration:** 150 working days = 25 weeks ≈ 6 months
**Stack:** Python only, API-based LLMs (no local LLM)

## v2 Changes (vs v1)
1. **Phase 1 compressed 25 → 12 days** — Python is fast for .NET dev. Stop padding intro days.
2. **Project 5 (B2C) moved to Phase 3 parallel** — gets ~110 days of growth, not 14
3. **Real user research Days 8-12** — interview 5 fintech analysts before building
4. **Content cadence 3x** — 3 LinkedIn/wk from Day 30, daily X from Day 50
5. **YC application Day 100** — even if you take a job, the app forces clarity

---

## Day Numbering Convention

**6 working days/week. Friday OFF. 25 weeks = 150 days.**

Day 1=Mon wk1, Day 5=Sat wk1, Day 6=Sun wk1, Day 7=Mon wk2, ... Day 150=Sun wk25.

| Day in week | Weekday | Hours |
|-------------|---------|-------|
| 1st | Mon | 2 (eve) |
| 2nd | Tue | 2 (eve) |
| 3rd | Wed | 2 (eve) |
| 4th | Thu | 2 (eve) |
| (Fri) | OFF | 0 |
| 5th | Sat | 5 (deep work) |
| 6th | Sun | 2 (Sunday block) |

---

## Sunday Block (2 hrs every Sunday)

| Time | Activity |
|------|----------|
| 1 hr | Blog draft / writing / review |
| 30 min | Finance domain reading (Damodaran, Levine, India sources) |
| 30 min | Week ahead planning + retrospective |

---

## Strategy Recap

- **Niche:** Fintech AI (Investment Research + AP/Invoice + Tax)
- **Type:** B2B (4 projects) + B2C (1 project, treated as startup)
- **Markets:** US remote (#1) + Hyderabad GCCs (#2) + Indian fintechs (#3)
- **Backup ambition:** YC W26 application Day 100
- **Salary target:** USD $120-160K remote / ₹35-110 LPA Hyderabad

---

## 5 Locked Projects (revised order)

| # | Project | Type | Days | Build Window |
|---|---------|------|------|--------------|
| Warmup | Email Classifier | B2B | 9-12 | 4 days |
| 1 | SEC 10-K Analyzer | B2B | 13-37 | 25 days |
| 5 (early!) | Indian Earnings Digest | B2C | 50-62 + ongoing | 13 days build, 90+ days growth |
| 2 | Invoice AP Auditor | B2B | 38-67 | 30 days (overlaps w/ P5) |
| 3 | Equity Research Agent | B2B | 68-92 | 25 days |
| 4 | Indian Tax Document Analyzer | B2B | 93-112 | 20 days |

**Project 5 is now the centerpiece, not afterthought.** Launch early, grow throughout, monetize, use as YC app + resume gold.

---

## Toolchain

### Dev environment
- **IDE:** Cursor
- **Terminal:** iTerm2 + Oh My Zsh
- **Python:** 3.12 via Homebrew
- **Package manager:** `uv`
- **Git/GitHub**

### AI / LLM stack
- LangChain (primary), LlamaIndex (one project)
- Pydantic v2, Instructor
- OpenAI SDK + Anthropic SDK
- Hugging Face Hub

### Data + storage
- ChromaDB (local), Pinecone (prod)
- PostgreSQL (Supabase free tier OR own VPS)
- Redis (Upstash free tier)

### Web + deployment
- FastAPI, Streamlit, Next.js
- Docker
- HF Spaces, Render, Vercel
- **Self-VPS for Project 5** (cron + DB + email)

### Observability + evals
- LangSmith, Langfuse, Ragas, DeepEval

### Productivity
- Notion, GitHub Projects, Airtable

---

## Ongoing Cadences

### Content (build-in-public — START EARLY)
- **Day 1:** First LinkedIn post — "Starting AI Engineer transition today"
- **Day 8-30:** 1 LinkedIn post/week
- **Day 30+:** 3 LinkedIn posts/week (project updates, learnings, hot takes)
- **Day 50+:** Daily X post (build-in-public, threads)
- **Engagement:** 5 AI posts/day on LinkedIn from Day 30; 5/day on X from Day 50

### LeetCode (light cadence — projects > algos)
- 1 problem/week from Day 30 (40 problems by Day 140)
- Skip if pressure or fatigue — projects matter more

### Finance domain reading (every Sunday — 30 min)
- Months 1-2: Damodaran intro lectures + Money Stuff newsletter
- Month 3: Stratechery + 10-K deep reads
- Months 4-6: India sources (RBI, NPCI, Zerodha Varsity)

### User research interviews
- **Days 8-12:** 5 fintech analyst/PM interviews (LinkedIn cold outreach)
- **Day 60:** 5 follow-up interviews on Project 5 + Project 1 users
- **Day 100:** 5 founder conversations (YC prep + warm leads)

### Mock interviews
- Day 80, 110, 140

---

# PHASE 1: Speedrun Foundations + User Research (Days 1-12, 2 weeks)

**Goal:** Python + LLM basics in 8 days. Email classifier shipped Day 12. Talk to 5 real users.

## Week 1 — Setup + Build

### Day 1 (Mon): Install everything + first LLM call SAME DAY
- Install Homebrew, Python 3.12, uv, Git, Cursor — 30 min
- Create GitHub repo `ai-engineer-journey`
- $30 OpenAI + $30 Anthropic credits topped up
- First OpenAI chat completion working
- **Build-in-public:** LinkedIn post "Day 1 of AI Engineer transition. First Claude API call live."
- **Resource:** platform.openai.com/docs/quickstart

### Day 2 (Tue): Python idioms in 2 hrs
- For .NET dev: list/dict comprehensions, f-strings, type hints, async, virtual envs
- Skip "what is a variable" — you know
- Resource: realpython.com (skim, don't deep-read)
- Practice: rewrite 1 small .NET utility in Python

### Day 3 (Wed): Pydantic + FastAPI in 2 hrs
- Pydantic v2 BaseModel, validators
- FastAPI endpoint w/ Pydantic request/response
- Resource: fastapi.tiangolo.com/tutorial (skim first 5 sections)
- Build: TODO API w/ 4 endpoints

### Day 4 (Thu): Instructor + structured LLM output
- Install Instructor library
- LLM → Pydantic objects in 5 lines
- Resource: jxnl.github.io/instructor
- Build: extract person info from email → Person model

### Day 5 (Sat — 5 hrs): Email classifier MVP shipped
- Repo: `fintech-email-classifier`
- Email → JSON {category, urgency, sentiment, action_items, summary}
- Streamlit UI in 1 hr
- Deploy Streamlit Cloud
- Demo GIF in README
- **Build-in-public:** LinkedIn post w/ live demo link

### Day 6 (Sun — 2 hrs): Sunday block
- 1 hr: Identify 20 fintech analysts/PMs on LinkedIn — save to Airtable
- 30 min: Damodaran "What is Valuation?" intro (YouTube)
- 30 min: Plan Week 2

---

## Week 2 — User Research + Polish

### Day 7 (Mon): Cold outreach to 20 analysts
- Send 20 personalized LinkedIn DMs
- Template: "I'm a software engineer building AI tools for finance. Could I ask 3 questions about your workflow? 15-min call?"
- Goal: 5 yes responses
- **Resource:** LinkedIn Sales Nav free trial helpful

### Day 8 (Tue): Analyst interview #1 + #2
- 15-min calls (Zoom/phone)
- Questions: What docs do you read daily? What's most painful? What would 10x your output?
- Note insights in Notion
- LinkedIn post: "Talked to 2 fintech analysts today. Here's what surprised me..."

### Day 9 (Wed): Email classifier polish + evals
- 30 hand-labeled emails for accuracy testing
- Pytest-style evals
- README polish — architecture, lessons, live link

### Day 10 (Thu): Analyst interview #3 + #4
- More calls
- Synthesize patterns across all 4 calls
- Identify which Project (1, 2, 3, 4) addresses biggest pain

### Day 11 (Sat — 5 hrs): Analyst interview #5 + first blog post
- Final call
- Write blog post: "I Talked to 5 Fintech Analysts About AI. Here's What They Want."
- Publish on Medium + LinkedIn + Dev.to
- **HUGE distribution play** — analysts will share

### Day 12 (Sun — 2 hrs): Sunday block + Phase 1 retrospective
- 1 hr: Phase 1 retrospective in Notion
- 30 min: Damodaran video #2
- 30 min: Plan Phase 2 — adjust Project 1 scope based on user feedback
- **Phase 1 complete.** Email classifier shipped. 5 user interviews done. Blog post live. 12 days.

---

# PHASE 2: RAG + Project 1 — SEC 10-K Analyzer (Days 13-37, 4 weeks)

**Goal:** Master RAG. Ship SEC 10-K Analyzer. Incorporate user feedback from interviews.

**Project 1 scope refined by user interviews:**
- (Add features analysts asked for in calls)
- Default: ticker → fetch 10-K → Q&A w/ citations
- YoY comparison, multi-doc, section filtering

---

## Week 3 — Embeddings + Vector DBs

### Day 13 (Mon): Embeddings concepts
- DeepLearning.AI: "Vector Databases: Embeddings to Applications"
- text-embedding-3-small basics
- Cosine similarity intuition

### Day 14 (Tue): ChromaDB + Pinecone
- Both setups in same day
- Sign up Pinecone, create index (verify free tier)
- Build: semantic search over 100 sentences

### Day 15 (Wed): SEC EDGAR + PDF parsing
- sec.gov/edgar tour
- Download AAPL, MSFT, JPM 10-Ks
- pypdf, pdfplumber comparison
- Read 1 10-K Risk Factors section fully

### Day 16 (Thu): LangChain RAG fundamentals
- DeepLearning.AI: "LangChain for LLM App Development" (skim, you know basics now)
- LCEL, document loaders, text splitters
- Build: tiny RAG over 1 PDF

### Day 17 (Sat — 5 hrs): Project 1 setup + ingestion pipeline
- Repo: `sec-10k-analyzer`
- FastAPI + Streamlit skeleton
- sec-edgar-downloader integration
- PDF → chunk → embed → Pinecone (metadata: company, date, section)
- Test: ingest AAPL 10-K end-to-end

### Day 18 (Sun — 2 hrs): Sunday block
- 1 hr: Outline blog post #2 — "Building Production RAG"
- 30 min: Money Stuff newsletter (subscribe + read 2)
- 30 min: Week 4 plan
- **Build-in-public:** LinkedIn post #3 — "Day 18: Building SEC 10-K analyzer. Here's the architecture." + diagram

---

## Week 4 — Project 1 Build

### Day 19 (Mon): Basic Q&A endpoint
- FastAPI POST /query — ticker + question
- Top-K retrieve → Claude → answer + sources
- Test: "What are AAPL's risk factors?"

### Day 20 (Tue): Frontend connection
- Streamlit: ticker dropdown, question input, answer
- Citations w/ chunk previews
- Loading states

### Day 21 (Wed): Multi-section retrieval — START 3 LinkedIn posts/week
- Filter by section (Risk Factors, MD&A, etc.)
- Section-aware retrieval
- LinkedIn post #4 — RAG architecture diagram

### Day 22 (Thu): Multi-doc + YoY comparison
- Compare 2 companies' 10-Ks
- Ingest 3 years of 1 company → YoY queries

### Day 23 (Sat — 5 hrs): Caching + cost + chunking experiments
- Redis cache (Upstash)
- Cost dashboard
- Test 3 chunking strategies, pick best
- LinkedIn post #5 — chunking experiments results

### Day 24 (Sun — 2 hrs): Sunday block
- 1 hr: Continue blog post #2
- 30 min: Damodaran finance lecture
- 30 min: Plan Week 5

---

## Week 5 — Project 1 Polish

### Day 25 (Mon): Eval suite
- 20 hand-graded Q&A pairs across 3 companies
- Pytest-style evals, scoring over time

### Day 26 (Tue): LangSmith tracing
- Add tracing to ingestion + query
- Inspect failures

### Day 27 (Wed): Deploy production
- Backend: Render Docker
- Frontend: Streamlit Cloud
- Pinecone prod index
- Custom domain
- LinkedIn post #6 — live demo announcement

### Day 28 (Thu): README + demo polish
- Architecture diagram
- 30-sec demo GIF
- Lessons learned section

### Day 29 (Sat — 5 hrs): Reach back to 5 analysts (user feedback)
- Send Project 1 demo link to 5 interviewees
- Schedule 5-min check-ins for next week
- Collect feedback, fix top 3 issues live

### Day 30 (Sun — 2 hrs): Sunday block — START LeetCode (1/wk)
- 1 hr: Finalize blog post #2
- 30 min: 10-K reading
- 30 min: 1 LeetCode medium problem
- **CADENCE LIVE:** 3 LinkedIn/wk + 1 LeetCode/wk

---

## Week 6 — Project 1 Launch + Project 5 Prep

### Day 31 (Mon): Blog #2 publish
- Submit to Towards Data Science (Medium)
- Cross-post Dev.to, LinkedIn, X
- Show HN

### Day 32 (Tue): Analyst feedback iteration
- Incorporate top 3 fixes from feedback
- Push v1.1
- Re-share with analysts

### Day 33 (Wed): Project 5 spec — Indian Earnings Digest
- Spec doc: features, monetization, growth plan
- Pricing: free weekly, ₹199/mo daily + alerts
- Treat as STARTUP not side project

### Day 34 (Thu): Project 5 data sources research
- BSE/NSE corporate filings (RSS/API)
- moneycontrol.com (scrape carefully, robots.txt)
- screener.in API research
- Pick 3 reliable sources

### Day 35 (Sat — 5 hrs): Project 5 architecture + VPS setup
- Repo: `nifty-earnings-digest`
- VPS setup: Python 3.12, Docker, nginx
- Configure subdomain on owned domain
- Architecture: VPS cron → fetch → analyze → email + DB

### Day 36 (Sun — 2 hrs): Sunday block
- 1 hr: Project 5 landing page copy draft
- 30 min: India fintech landscape reading (Razorpay blog)
- 30 min: Week 7 plan

### Day 37 (Mon): Phase 2 retrospective + Project 1 LinkedIn launch post
- Notion retrospective
- LinkedIn carousel post — Project 1 deep dive

**Phase 2 Deliverable:** SEC 10-K Analyzer live + iterated. Blog #2 published. User feedback loop active.

---

# PHASE 3: Project 5 LAUNCH + Project 2 Build (Days 38-67, 5 weeks)

**Goal:** SHIP Project 5 (B2C startup mode). Build Project 2 (Invoice Auditor) in parallel. Get first 50 newsletter signups by Day 62.

---

## Week 7 — Project 5 Build (priority)

### Day 38 (Tue): Project 5 — data fetch pipeline
- BSE/NSE filing fetcher
- Earnings transcript scraper
- Store in PostgreSQL on VPS

### Day 39 (Wed): Project 5 — LLM summary engine
- Per-filing: summary + sentiment + key takeaways
- Use Claude Haiku (cheap)
- Store outputs in DB

### Day 40 (Thu): Project 5 — email generation
- Resend.com free tier (verify limits)
- Responsive HTML email template
- Test send to 3 friend emails

### Day 41 (Sat — 5 hrs): Project 5 — landing page
- Next.js + Tailwind
- Hero, value prop, signup form
- Vercel deploy w/ owned domain
- PostHog analytics

### Day 42 (Sun — 2 hrs): Sunday block
- 1 hr: Project 5 launch tweet + LinkedIn copy
- 30 min: Indian fintech reading
- 30 min: Week 8 plan
- LinkedIn post #7 — "Building a fintech newsletter SaaS in 2 weeks"

---

## Week 8 — Project 5 LAUNCH + Project 2 Start

### Day 43 (Mon): Project 5 — VPS cron setup
- systemd timer
- Weekly trigger first
- Failure alerts to email

### Day 44 (Tue): Project 5 — first manual newsletter
- Manual trigger to 10 testers
- Iterate on quality
- Get feedback

### Day 45 (Wed): Project 5 — PUBLIC LAUNCH
- Reddit: r/IndianStockMarket, r/IndiaInvestments (timed for max visibility)
- LinkedIn announcement
- X thread
- Indie Hackers post
- Goal: 50 signups Week 1

### Day 46 (Thu): Project 5 — handle launch traffic + Project 2 spec
- Monitor signups
- Fix bugs from real users
- Write Project 2 spec doc — `invoice-ap-auditor`

### Day 47 (Sat — 5 hrs): Project 2 — extraction pipeline
- Repo created
- PyMuPDF, pdfplumber comparison
- Multimodal extraction (Claude vision API)
- Pydantic Invoice schema (nested w/ line items)
- Test on 30 sample invoices

### Day 48 (Sun — 2 hrs): Sunday block
- 1 hr: Blog post #3 outline — "Shipping a Newsletter SaaS in 2 Weeks"
- 30 min: Money Stuff
- 30 min: Plan Week 9
- LinkedIn post #8 — Project 5 launch results

---

## Week 9 — Project 2 Build + Project 5 Iterate

### Day 49 (Mon): Project 2 — DB schema + ORM
- Supabase OR VPS Postgres
- SQLAlchemy ORM, Alembic
- Tables: invoices, line_items, vendors, audit_flags

### Day 50 (Tue): Project 2 — audit rules engine — START daily X posting
- Rule: duplicate, math error, tax mismatch, missing fields
- Each rule = function returning AuditFlag
- **Daily X cadence starts:** build-in-public threads

### Day 51 (Wed): Project 5 — feedback iteration
- Address top 3 user complaints
- Add unsubscribe handling
- Improve email quality

### Day 52 (Thu): Project 2 — LLM-powered audit
- Beyond rules: "Does this look suspicious?"
- Hybrid: rules + LLM second opinion

### Day 53 (Sat — 5 hrs): Project 2 — Next.js frontend
- Next.js 14 App Router
- Upload, list, detail views
- Connect to FastAPI

### Day 54 (Sun — 2 hrs): Sunday block
- 1 hr: Blog post #3 publish — Project 5 launch story
- 30 min: 10-K reading (start India: RELIANCE annual report)
- 30 min: Plan Week 10

---

## Week 10 — Project 2 Polish + Project 5 Growth

### Day 55 (Mon): Project 2 — bulk upload + background tasks
- Drag-drop, progress bar
- FastAPI BackgroundTasks
- LinkedIn post #10 — Project 2 progress

### Day 56 (Tue): Project 2 — error handling + retries
- Tenacity for LLM retries
- Graceful degradation

### Day 57 (Wed): Project 5 — push to 100 signups
- Post on Twitter Spaces about Indian markets
- DM 20 finance influencers
- Submit to Product Hunt? (consider timing)

### Day 58 (Thu): Project 2 — cost optimization
- Claude Haiku for extraction, Sonnet for ambiguous
- Track cost per invoice

### Day 59 (Sat — 5 hrs): Project 2 — admin dashboard + LangSmith
- Stats: invoices processed, flags, $ savings
- LangSmith tracing
- Vendor leaderboard

### Day 60 (Sun — 2 hrs): Sunday block — USER RESEARCH ROUND 2
- 1 hr: Reach 5 newsletter users + 5 Project 1 users for feedback calls
- 30 min: Stratechery
- 30 min: Plan Week 11

---

## Week 11 — Project 2 Ship + User Feedback

### Day 61 (Mon): Project 2 — eval suite
- 50 invoices w/ ground truth
- Field-level extraction accuracy
- Flag precision/recall

### Day 62 (Tue): Project 2 — deploy
- Backend: Render
- Frontend: Vercel
- DB: Supabase
- Live + tested

### Day 63 (Wed): User feedback calls (5 calls today)
- Project 5 + Project 1 users
- Synthesize insights
- LinkedIn post #12 — "10 user calls taught me..."

### Day 64 (Thu): Project 2 demo video + README polish
- Loom 2-min walkthrough
- Architecture diagram
- LinkedIn post #13 — Project 2 launch teaser

### Day 65 (Sat — 5 hrs): Project 2 launch + blog #4
- Publish blog #4 — "I Built an AI Invoice Auditor"
- Medium + Dev.to + LinkedIn
- Show HN

### Day 66 (Sun — 2 hrs): Sunday block
- 1 hr: Phase 3 retrospective
- 30 min: India fintech reading
- 30 min: Plan Phase 4

### Day 67 (Mon): Phase 3 wrap
- 2 projects shipped (1 + 2)
- Project 5 at 100+ signups (target)
- 4 blog posts live
- LinkedIn post #14 — phase milestone

**Phase 3 Deliverable:** Project 5 launched + growing. Project 2 shipped. 4 blog posts. Real users on B2C product.

---

# PHASE 4: Agents + Project 3 + Project 5 Growth (Days 68-92, 4 weeks)

**Goal:** Ship Equity Research Agent. Push Project 5 to 250+ users. Prep for YC.

**Project 3: Equity Research Agent**
- Multi-tool agent: SEC EDGAR + news + transcripts + ratios + peers
- LangGraph state machine
- Output: PDF research report w/ citations

---

## Week 12 — Function Calling + Tools

### Day 68 (Tue): Function calling deep dive
- OpenAI + Anthropic tool use
- Parallel tool calls

### Day 69 (Wed): Build 3 simple tools
- fetch_stock_price (yfinance)
- fetch_news (NewsAPI free tier)
- calculator (LangChain built-in)

### Day 70 (Thu): ReAct pattern from scratch
- Manual loop, no framework
- Understand internals
- LinkedIn post #15 — agents explainer

### Day 71 (Sat — 5 hrs): LangGraph intro
- DeepLearning.AI: "AI Agents in LangGraph" (1.5 hrs)
- Nodes, edges, state
- Build: 3-tool agent in LangGraph

### Day 72 (Sun — 2 hrs): Sunday block
- 1 hr: Blog post #5 outline — "LLM Agents That Don't Suck"
- 30 min: Damodaran
- 30 min: Plan Week 13

---

## Week 13 — Project 3 Tools

### Day 73 (Mon): Project 3 setup + SEC tool (reuse from P1)
- Repo: `equity-research-agent`
- LangGraph state machine
- SEC EDGAR tool

### Day 74 (Tue): News + earnings transcript tools
- NewsAPI integration
- Financial Modeling Prep API for transcripts

### Day 75 (Wed): Peer lookup + ratios tools
- yfinance + SIC codes
- P/E, P/B, ROE, gross margin, FCF yield functions
- LinkedIn post #16 — agent tools demo

### Day 76 (Thu): Multi-agent patterns
- Supervisor pattern
- Sequential agents
- Resource: langchain-ai.github.io/langgraph/tutorials

### Day 77 (Sat — 5 hrs): Project 3 — research workflow
- Nodes: plan → fetch → analyze → write
- State: question, gathered_data, analysis, report
- Test: "Is NVIDIA overvalued?"

### Day 78 (Sun — 2 hrs): Sunday block
- 1 hr: Continue blog #5
- 30 min: Levine
- 30 min: Plan Week 14

---

## Week 14 — Project 3 Output + Project 5 Growth Push

### Day 79 (Mon): Project 5 — paid tier prep (Razorpay)
- Razorpay test mode setup
- Premium feature: daily emails + alerts + custom watchlists
- Don't ship yet — prep only

### Day 80 (Tue): Project 3 — output formatting + FIRST MOCK INTERVIEW
- Markdown report template
- Sections: Summary, Financials, Risks, Peers, Verdict
- Pramp/interviewing.io mock (1 hr)

### Day 81 (Wed): Project 3 — PDF export
- markdown → PDF (weasyprint)
- Polished look

### Day 82 (Thu): Project 3 — Streamlit UI w/ streaming
- Stream agent steps (show thinking)
- Final report preview + download

### Day 83 (Sat — 5 hrs): Project 3 — eval suite + deploy
- 10 research questions w/ gold answers
- Measure factual accuracy, completeness
- Deploy to HF Space
- LinkedIn post #18 — Project 3 launch teaser

### Day 84 (Sun — 2 hrs): Sunday block
- 1 hr: Blog #5 polish
- 30 min: India fintech reading (RBI annual)
- 30 min: Plan Week 15
- **Project 5 check:** Should be at 200+ signups by now

---

## Week 15 — Project 3 Launch + Project 5 Monetize

### Day 85 (Mon): Project 3 — launch + blog #5 publish
- Medium (Towards Data Science)
- Show HN
- LinkedIn carousel
- X thread

### Day 86 (Tue): Project 5 — Razorpay integration LIVE
- Premium tier launches
- Email existing users with offer
- Goal: 5 paid in week 1

### Day 87 (Wed): YC application research starts
- Read YC's "How to Apply" guide
- Watch YC partner videos
- Outline Project 5 as YC application

### Day 88 (Thu): Project 5 — first paid customer celebration
- LinkedIn post #20 — "Got my first paying customer"
- This is RESUME GOLD

### Day 89 (Sat — 5 hrs): User feedback round 3
- 5 calls w/ paid customers (if any) + 5 free users
- Identify what made them pay (or not)
- Adjust pricing/features

### Day 90 (Sun — 2 hrs): Sunday block
- 1 hr: YC application draft (Question 1: What does company do?)
- 30 min: Damodaran valuation deep dive
- 30 min: Plan Week 16

---

## Week 16 — Pre-YC Application Sprint

### Day 91 (Mon): YC application — questions 2-5
- Why this team? Why now? What are you building?
- Draft, refine

### Day 92 (Tue): YC application — metrics + traction
- Document Project 5 numbers: signups, MRR, growth rate
- LinkedIn post #21 — Phase 4 milestone (3 projects, 1 startup)

**Phase 4 Deliverable:** Research Agent live. Project 5 monetizing. YC app drafted. 5 blog posts.

---

# PHASE 5: India Specialization + Project 4 + YC Submission (Days 93-117, 4 weeks)

**Goal:** Ship Project 4 (India tax). Submit YC W26 application. Project 5 to 500+ users.

---

## Week 16 cont.

### Day 93 (Wed): Project 4 plan
- Spec: Indian Tax Document Analyzer
- Reuse extraction code from P2
- Repo: `india-tax-analyzer`

### Day 94 (Thu): India tax research
- Old vs new regime FY 2024-25
- Deductions: 80C, 80D, HRA, LTA
- ClearTax guides

### Day 95 (Sat — 5 hrs): Project 4 — extraction + calculator
- Pydantic schemas: SalarySlip, Form16, ITR
- Old + new regime calculator
- Test w/ sample Form 16

### Day 96 (Sun — 2 hrs): Sunday block
- 1 hr: YC app polish
- 30 min: NPCI/UPI architecture
- 30 min: Plan Week 17

---

## Week 17 — Project 4 + YC Application

### Day 97 (Mon): Project 4 — LLM tax Q&A (RAG)
- RAG over Income Tax Act sections
- Citations to sections

### Day 98 (Tue): Project 4 — Streamlit UI
- Upload Form 16 → summary
- Regime comparison
- Q&A chat

### Day 99 (Wed): Project 4 — privacy + security
- Documents NOT stored
- Privacy policy
- Rate limiting

### Day 100 (Thu): 🎯 YC W26 APPLICATION SUBMITTED
- Final review of YC app
- Submit before deadline
- LinkedIn post #23 — "Just submitted to YC. Here's why."
- **HUGE distribution moment**

### Day 101 (Sat — 5 hrs): Project 4 — eval + deploy
- 10 sample Form 16s w/ known correct calculations
- HF Spaces deploy
- Demo GIF + README

### Day 102 (Sun — 2 hrs): Sunday block
- 1 hr: Blog post #6 outline — "Building India-Specific AI"
- 30 min: India fintech reading
- 30 min: Plan Week 18

---

## Week 18 — Project 4 Launch + Evals/Caching Across Projects

### Day 103 (Mon): Project 4 launch
- Blog #6 publish — Medium + LinkedIn
- Tag #IndianStartups #FinTechIndia
- LinkedIn post #24

### Day 104 (Tue): Add Ragas evals to Project 1
- Faithfulness, answer relevancy, context precision
- Track metrics over time

### Day 105 (Wed): Anthropic prompt caching across all projects
- Add to P1, P2, P3 — huge cost savings
- Document savings in blog post draft

### Day 106 (Thu): GitHub Actions CI for evals
- Run evals on every PR
- Block merges on regression

### Day 107 (Sat — 5 hrs): Cost optimization deep dive blog
- Document cost-cutting across all projects
- Blog post #7 draft — "How I Cut LLM Costs 80%"

### Day 108 (Sun — 2 hrs): Sunday block
- 1 hr: Blog #7 finalize
- 30 min: 10-K reading
- 30 min: Plan Week 19

---

## Week 19 — Project 5 Scale + YC Decision Wait

### Day 109 (Mon): Project 5 — push to 500 users
- Reddit AMAs in Indian investing subs
- Twitter/X live spaces
- Influencer outreach (5 finance creators)

### Day 110 (Tue): SECOND MOCK INTERVIEW + LeetCode
- Pramp 1 hr
- Note weak areas

### Day 111 (Wed): Blog #7 publish
- "How I Cut LLM Costs 80% Across 4 Production Projects"
- Hacker News submission

### Day 112 (Thu): Phase 5 retrospective
- 4 B2B projects shipped + 1 B2C startup w/ paying users + YC application submitted
- LinkedIn post #26 — milestone celebration

### Day 113 (Sat — 5 hrs): Portfolio polish — all 5 READMEs
- Architecture diagrams (excalidraw)
- Demo GIFs
- Tech stack tables
- Lessons learned

### Day 114 (Sun — 2 hrs): Sunday block
- 1 hr: Personal site build start (Astro template)
- 30 min: Reading
- 30 min: Plan Week 20

---

## Week 20 — Personal Brand Polish

### Day 115 (Mon): Personal site v1 deployed
- Astro + Tailwind
- Sections: hero, projects, blog, contact
- Owned domain
- Vercel deploy

### Day 116 (Tue): Cross-post all blogs to personal site
- 7 blog posts on own site
- Update Medium/Dev.to bio with site link

### Day 117 (Wed): YC interview prep (if invited) or pivot
- If YC invite: prep Demo Day pitch
- If rejected: take learnings into job apps
- Either way: Project 5 stays alive

**Phase 5 Deliverable:** All 5 projects live. YC submitted. 7 blog posts. Personal site live. Project 5 at 500+ users.

---

# PHASE 6: Job Hunt + YC Decision + Offer (Days 118-150, 5+ weeks)

**Goal:** Apply, interview, get offer. Or take YC if accepted.

---

## Week 20 cont.

### Day 118 (Thu): Resume rewrite
- Single-page
- Top: 3-line summary — "AI Engineer | Fintech | Built 5 production apps + 1 B2C SaaS w/ paying users"
- Projects FIRST (5 projects + Project 5 startup metrics)
- Skills, then .NET background condensed

### Day 119 (Sat — 5 hrs): Target list + Airtable
- 75 companies (was 50 — be more aggressive):
  - 30 US fintechs hiring globally remote
  - 20 GCCs (Goldman, JPMorgan, Visa, Mastercard, Stripe, etc.)
  - 15 Indian fintechs (Razorpay, CRED, Zerodha, INDmoney, Smallcase)
  - 10 AI-first startups (regardless of fintech)

### Day 120 (Sun — 2 hrs): Sunday block
- 1 hr: TN visa docs gather, OCI check, schedule CA call
- 30 min: Negotiation prep (Levels.fyi research)
- 30 min: Plan Week 21

---

## Week 21 — Application Blitz Week

### Day 121 (Mon): LinkedIn overhaul
- Banner: AI/fintech themed
- Headline: "AI Engineer | Fintech | YC W26 Applicant | Building Production LLM Apps"
- About: story-driven w/ Project 5 metrics
- Featured: top 4 projects + Project 5
- "Open to Work" private mode

### Day 122 (Tue): First wave applications (25 roles)
- Customize cover letter for top 5
- Generic for rest

### Day 123 (Wed): Cold outreach — 15 founders/AI leads
- Personalized DMs on LinkedIn + X
- Lead with Project 5 metrics

### Day 124 (Thu): Second wave (25 more applications)

### Day 125 (Sat — 5 hrs): Referral hunting + Project 5 update
- Ping LinkedIn 1st-degree connections at targets (15 messages)
- Push Project 5 update to existing users
- Blog post #8 — "5 Months In: Lessons from Building AI Fintech"

### Day 126 (Sun — 2 hrs): Sunday block
- 1 hr: Interview prep — LLM system design (3 YouTube vids)
- 30 min: Reading
- 30 min: Plan Week 22

---

## Week 22 — Interview Prep + Mock Loops

### Day 127 (Mon): LLM system design practice
- Design a RAG system
- Design an agent system
- Practice w/ partner or mock service

### Day 128 (Tue): Behavioral prep
- STAR format for top 10 questions
- Practice each project pitch in 2 min

### Day 129 (Wed): THIRD MOCK INTERVIEW + 25 more applications
- Pramp/interviewing.io
- Continue applying

### Day 130 (Thu): Coding practice
- 5 LeetCode mediums (Python)
- Focus: arrays, strings, hash maps

### Day 131 (Sat — 5 hrs): Take-home practice
- Build a sample take-home in 4 hrs
- Public repo for prep

### Day 132 (Sun — 2 hrs): Sunday block
- 1 hr: Final blog draft — ".NET to AI Engineer in 6 Months"
- 30 min: Negotiation tactics review
- 30 min: Plan Week 23

---

## Week 23 — Live Interview Loop

### Day 133-136: Interview rounds across companies
- Recruiter screens
- Coding screens
- LLM system design
- Behavioral
- Take-homes

### Day 137 (Sat — 5 hrs): Take-home projects this weekend
- Quality > speed
- Deploy live, write tests, polish README

### Day 138 (Sun — 2 hrs): Sunday block
- 1 hr: Compare offers (if any incoming)
- 30 min: Negotiation prep
- 30 min: Plan Week 24

---

## Week 24 — Final Rounds + Negotiation

### Day 139-142: Final rounds + onsite/virtual loops
- Final interviews
- Reference checks
- Compete offers in flight

### Day 143 (Sat — 5 hrs): Negotiate
- Always negotiate (10-25% room)
- Use competing offers as leverage
- Compare: comp, equity, learning, team, mission, location flexibility

### Day 144 (Sun — 2 hrs): Sunday block
- 1 hr: Decision matrix for offers
- 30 min: Final blog post polish
- 30 min: Plan Week 25

---

## Week 25 — Decision + Announcement

### Day 145 (Mon): Decision day
- Accept offer (if multiple, pick best fit)
- OR: If YC accepted → take YC (different path)
- OR: If no offers yet → continue interviewing, extend timeline

### Day 146 (Tue): Announce + sign
- Sign offer letter
- Plan transition from .NET job

### Day 147 (Wed): Final blog publish
- ".NET to AI Engineer in 6 Months — Full Playbook"
- Medium feature submission
- Hacker News
- LinkedIn carousel

### Day 148 (Thu): Personal site update
- Add new role to header
- Final polish

### Day 149 (Sat — 5 hrs): Knowledge transfer at .NET job
- Document handover
- Train replacement / colleagues
- Maintain professionalism

### Day 150 (Sun — 2 hrs): VICTORY
- Reflect on 6 months
- LinkedIn celebration post
- Plan first 90 days at new role
- Project 5 transition plan (sell? maintain? grow?)
- **🎯 TRANSITION COMPLETE**

**Phase 6 Deliverable:** Offer accepted. 5 projects shipped. 1 B2C SaaS w/ revenue. 8 blog posts. YC submitted. ~40 LeetCode. Optionality maximized.

---

# Resource Hub

## Paid Spend Plan ($180 budget)

| Item | Cost | Why |
|------|------|-----|
| OpenAI API credits | $30 | All projects |
| Anthropic API credits | $30 | All projects |
| Pinecone | $0 | Free tier |
| Render or replacement | $25 | P1 + P2 backend |
| Razorpay (no fee, transaction-based) | $0 | P5 monetization |
| DeepLearning.AI Plus (optional) | $40 | Most courses free anyway |
| LangSmith free tier | $0 | Free for personal |
| Resend overage | $10 | If P5 grows beyond free |
| CA consultation (India tax) | $30 | Pre-offer setup |
| YC application | $0 | Free to apply |
| Buffer | $15 | Vector DB, extra compute |
| **Total** | **$180** | |

## Free Resources

**Courses:** DeepLearning.AI, Hugging Face Learn, Kaggle Learn

**Docs:** LangChain, LlamaIndex, OpenAI, Anthropic, HuggingFace

**YouTube:** AI Jason, James Briggs, Sam Witteveen, Andrej Karpathy, Aswath Damodaran

**Newsletters:** The Batch, Latent Space, Ahead of AI, Money Stuff, Stratechery free

**Communities:** Discord (LangChain, LlamaIndex, HF), Reddit (r/LocalLLaMA, r/MachineLearning), LinkedIn AI hashtag, X AI Engineers list

## India-Specific

- Zerodha Varsity, INDmoney/Smallcase blogs, Razorpay engineering blog, ClearTax, RBI annual report, NPCI docs, BSE/NSE filings

## Job Boards

- **US remote:** Wellfound (remote-global), YC Work at Startup, Hired, Otta
- **India:** Cutshort, Instahyre, Wellfound India, Naukri
- **GCCs:** Direct company sites + LinkedIn referrals

---

# Tracking + Metrics

## Per-month checklist (revised)

| Month | Projects | Blog Posts | LinkedIn Followers | P5 Users | Apps Sent |
|-------|----------|------------|-------------------|----------|-----------|
| 1 | Email classifier + 5 user interviews | 1 | +200 | — | 0 |
| 2 | SEC Analyzer | 2 | +500 | — | 0 |
| 3 | Project 5 LAUNCHED + Invoice Auditor | 4 | +1000 | 100+ | 0 |
| 4 | Research Agent + P5 monetize | 5 | +1500 | 250+ | 0 |
| 5 | Tax Analyzer + YC submitted | 7 | +2500 | 500+ | 25 |
| 6 | Polish + interviews + offer | 8 | +3500 | 750+ | 75 |

**LinkedIn followers 3x targets** — content cadence makes this realistic.

## Daily journal (Notion)
- Date, hours, learned, built, blockers, tomorrow

## Weekly review (Sunday)
- Shipped? Blocked? Underestimated? Adjustments?

---

# Adjustments + Risk Management

## If YC accepts (Day 100+):
- Take YC. Different path entirely.
- Project 5 becomes the company.
- Continue applying as backup until SAFE/SAFEs signed.

## If Project 5 hits 1000+ users / $1K MRR by Day 100:
- Consider going full startup mode
- Apply to YC + raise pre-seed
- Job hunt becomes optional

## If ahead of schedule:
- Open-source contributions to LangChain/LlamaIndex
- 6th project (multimodal, voice AI for finance)
- Speak at AI meetups

## If behind schedule:
- Drop Project 4 (India tax)
- Compress Phase 6 — apply Day 110

## If lose motivation (Month 3-4):
- Switch to user-facing work (Project 5)
- Take 3-day break
- Find study partner

## If get offer early:
- Take it. Continue Project 5 in spare time.

## If no interest by Month 5:
- 1-1 portfolio review (paid mentor if needed)
- Consider 2-month contract as bridge
- Increase content output 2x

---

# Critical Success Factors (revised)

1. **Ship over perfect.** Every project must have live URL.
2. **Talk to users from Day 1.** Build with them, not for them.
3. **Build in public from Day 1.** LinkedIn + X compound over months.
4. **Project 5 is your moat.** Real users + revenue = unfair advantage.
5. **Document everything.** READMEs sell. Blog posts compound.
6. **Fintech-flavor everything.** SEC > Wikipedia for portfolio.
7. **Evals + costs = differentiator.** 90% skip these.
8. **One framework, deep.** LangChain mastery > shallow on 5.
9. **Network from Day 1.** First LinkedIn post Day 1, not Day 25.
10. **Optionality > optimization.** YC + jobs + freelance = multiple paths.

---

# Pre-Flight Checklist (do before Day 1)

- [ ] Mac mini available with admin access
- [ ] $180 budget set aside
- [ ] VPS credentials accessible + SSH working
- [ ] Domain DNS access ready (will use for Project 5 + portfolio)
- [ ] Notion + Airtable accounts ready
- [ ] Calendar blocks set: Mon-Thu 7:30-9:30 PM, Sat 9 AM-2 PM, Sun 10 AM-12 PM
- [ ] Friday OFF protected
- [ ] Inform family/partner about 6-month commitment
- [ ] Verify no major life events Days 1-150
- [ ] LinkedIn cleaned up (current photo, polish profile basics)
- [ ] X/Twitter account ready (create if needed)
- [ ] OpenAI + Anthropic accounts created
- [ ] 20 fintech analyst LinkedIn profiles saved (pre-Day 7 outreach)

---

# Summary

**v2 Highlights:**
- Phase 1: 25 → 12 days (compressed Python intro)
- Project 5: side project → centerpiece startup w/ 110-day growth runway
- User research: Day 1 instead of never
- Content: 3x cadence (3 LinkedIn/wk + daily X)
- YC application: Day 100 — forces strategic clarity, opens optionality
- Total: 150 days. 5 projects. 8 blog posts. 1 B2C SaaS w/ revenue. 1 YC application. 1 offer.

**This is the hybrid plan: your safety + Musk's speed + Altman's leverage.**

Ready when you set Day 1.
