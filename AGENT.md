# AGENT.md — Context for AI Assistants

**Purpose:** This file gives any AI assistant (Claude, ChatGPT, Cursor, etc.) full context about this project so they can help me effectively without re-asking background questions.

**Last updated:** 2026-04-25

---

## Who I am

- **Background:** .NET / C# developer (years of experience)
- **Citizenship:** Naturalized Canadian, Indian heritage
- **Currently:** Living in Canada, planning temporary relocation to **Hyderabad, India** (no fixed date)
- **Career goal:** Transition from .NET developer to **AI Engineer** focused on **Fintech AI**
- **Stack preference:** **Python only** going forward (no C#/.NET in AI work)
- **LLMs:** **API-based only** (OpenAI, Anthropic) — no local LLM hosting
- **Hardware:** Mac mini (primary dev), VPS (Project 5 hosting), Windows laptop, owned domains
- **AI dev stack:** **VS Code + Claude Code (terminal) + Claude.ai web** (Claude Pro subscription)

## What this project is

A 150-day structured curriculum + tracker for transitioning from .NET to AI Engineer. Designed around:
- 6 working days/week (Mon-Thu evenings + Sat + Sun, **Friday OFF**)
- **15 hrs/week** sustainable pace
- 5 fintech AI projects + 1 warmup
- 1 B2C SaaS treated as startup (potential YC W26 application)
- US remote OR Hyderabad GCC role as endgame

## Files in this project

```
ai-engineer/
├── ReadMe.md           — high-level strategy summary
├── CURRICULUM.md       — full 150-day day-by-day plan (v2 hybrid Musk/Altman)
├── AGENT.md            — this file (AI assistant context)
└── tracker/            — daily progress tracking (separate git repo)
    ├── README.md       — public-facing tracker overview
    ├── PROGRESS.md     — running state, phase tracker
    ├── SETUP.md        — instructions to push to GitHub
    ├── days/           — daily log files (one per working day)
    ├── projects/       — index of 5 fintech projects
    ├── blogs/          — 8 blog posts schedule
    ├── notes/          — topical learning notes
    ├── interviews/     — analyst interviews + job tracker
    ├── metrics/        — CSVs (LinkedIn, GitHub, P5, applications)
    ├── resources/      — curated reading list
    └── templates/      — daily + weekly templates
```

**Important:** When helping me, **read CURRICULUM.md first** for full plan context, then PROGRESS.md to know my current day/state.

## Strategy at a glance

### Niche
**Fintech AI**, with focus on:
- Investment Research (SEC filings, earnings analysis)
- AP / Invoice processing
- Indian Tax (specialized vertical)

### Target markets (priority order)
1. **US remote roles** (work from Canada or India) — primary, USD $120-160K
2. **Hyderabad GCCs** (Goldman Sachs, JPMorgan, Visa, Mastercard, Stripe, etc.) — secondary, ₹35-110 LPA
3. **Indian fintechs** (Razorpay, CRED, Zerodha, Smallcase, INDmoney) — tertiary

### What to skip
- **Canadian roles** — even though I'm currently in Canada (planning India move)
- **Pure ML/PhD-track research roles** — I'm an applied AI engineer
- **C#/.NET-based AI roles** (Semantic Kernel, etc.) — Python-only path
- **B2C-only consumer apps** — focusing B2B + 1 B2C SaaS

### Visa cards available
- Canadian citizenship (current)
- TN visa eligibility for US (under USMCA — easy approval)
- OCI / PIO for India

## 5 fintech projects (locked)

| # | Project | Type | Days | Tech |
|---|---------|------|------|------|
| Warmup | Email Classifier | B2B | 9-12 | Python + Instructor + Streamlit |
| 1 | SEC 10-K Analyzer | B2B | 13-37 | LangChain + Pinecone + RAG |
| 2 | Invoice AP Auditor | B2B | 38-67 | FastAPI + Next.js + Postgres + Claude vision |
| 3 | Equity Research Agent | B2B | 68-92 | LangGraph + multi-tool agents |
| 4 | Indian Tax Document Analyzer | B2B | 93-117 | RAG + India tax rules |
| 5 | Indian Earnings Digest | B2C STARTUP | 38-150 | VPS cron + Resend + Razorpay + Next.js |

**Project 5 is the centerpiece** — launches Day 45, monetizes Day 86, treated as a startup. YC application Day 100.

## Tech stack (locked)

- **Language:** Python 3.12 (only)
- **Package mgr:** uv (not pip)
- **IDE:** VS Code + Claude Code (terminal agentic coding via Claude Pro subscription)
- **LLMs:** OpenAI + Anthropic (API only for production projects)
- **Frameworks:** LangChain primary, LlamaIndex secondary
- **Validation:** Pydantic v2, Instructor
- **Backend:** FastAPI
- **Frontend:** Streamlit (demos), Next.js (production)
- **Vector DB:** Chroma local, Pinecone production
- **Relational DB:** PostgreSQL via Supabase or VPS
- **Cache:** Upstash Redis
- **Observability:** LangSmith, Ragas
- **Deploy:** HF Spaces (fast), Render (backend), Vercel (frontend), own VPS (P5)

## Schedule (locked)

| Day | Time | Hours |
|-----|------|-------|
| Mon | 7:30-9:30 PM | 2 |
| Tue | 7:30-9:30 PM | 2 |
| Wed | 7:30-9:30 PM | 2 |
| Thu | 7:30-9:30 PM | 2 |
| Fri | OFF | 0 |
| Sat | 9 AM-2 PM | 5 |
| Sun | 10 AM-12 PM | 2 (Sunday block: writing + finance + planning) |

**Total: 15 hrs/week × 25 weeks = 150 working days = ~6 months**

## Budget

$180 total over 150 days:
- $30 OpenAI credits
- $30 Anthropic credits
- $25 Render hosting
- $40 DeepLearning.AI Plus (optional)
- $30 CA consultation (India tax setup)
- $25 buffer / overages

## Cadences (run alongside daily work)

- **Build-in-public:** LinkedIn 3x/week from Day 30, daily X from Day 50
- **LeetCode:** 1/week from Day 30 (light cadence — projects > algos)
- **Finance reading:** 30 min every Sunday (Damodaran → Levine → 10-Ks → India sources)
- **User research:** 5 calls Days 8-12, 5 follow-ups Day 60, 5 founder calls Day 100
- **Mock interviews:** Day 80, 110, 140

## How I prefer to be helped

### When I ask questions:
- Be **direct and concise** — I value brevity
- Use **caveman/fragment style** for quick answers, normal English for code/security/commits
- Don't pad with "Sure! I'd be happy to help" — just answer
- If recommending changes, **show the tradeoff** — pros/cons, not just one option

### When I ask for code:
- Python only
- Type hints everywhere
- Pydantic v2 over plain dicts
- Async by default for I/O
- Tests w/ pytest
- No comments unless WHY is non-obvious

### When I ask for plans:
- Day-by-day if applicable
- Specific resources (named with links)
- Realistic time estimates
- Show risk + mitigation

### When I ask for review:
- Be brutal honest — I want to ship, not be coddled
- Channel Musk/Altman thinking when I ask for it
- Flag what's wrong, don't just praise

## What's already decided (don't re-litigate)

- Python only (not C#/.NET)
- API LLMs only (no local Llama hosting)
- Fintech AI niche (not legal, healthcare, etc.)
- B2B primary + 1 B2C side (Project 5)
- US remote + Hyderabad GCC + Indian fintech targeting
- 15 hrs/week schedule
- 150-day timeline
- VS Code + Claude Code as IDE/AI stack
- LangChain as primary framework
- Claude Pro subscription (already paid) covers AI assistant needs

If I'm reconsidering one of these, I'll explicitly say so.

## Current state

**Check `tracker/PROGRESS.md`** for current day, phase, blockers, recent wins.

If `tracker/PROGRESS.md` says "Day 0" — I'm pre-flight, not started yet.
If it says "Day NN" — I'm N days in, currently in [phase].

## Memory layer

Persistent memories about my preferences and context are stored at:
`/Users/thegoyalyogesh/.claude/projects/-Volumes-SSD-Yogesh-Study-Material-Mac-Yogesh-Projects-ai-engineer/memory/`

- `MEMORY.md` — index
- `user_background.md` — career goals + Python preference

## Common tasks I'll ask for help with

1. **Today's day plan** — read `CURRICULUM.md` for the day, give me focused steps
2. **Project code help** — debug, design, implement features
3. **Blog post drafts** — using my project work as material
4. **LinkedIn / X post drafts** — build-in-public content
5. **User research synthesis** — analyzing analyst interview notes
6. **Job application prep** — resume tweaks, cover letters, interview prep
7. **Strategic check-ins** — am I on track? Should I pivot?
8. **Cost/architecture decisions** — which vector DB, which model, which framework
9. **YC application drafting** — Project 5 startup framing
10. **Daily log writing** — turn my notes into a `tracker/days/day-NNN.md` entry

## Anti-patterns (don't do these)

- Don't suggest local LLM setups (Ollama, llama.cpp) — explicitly out of scope
- Don't suggest Canadian-only roles or relocation to US for grad school — wrong path
- Don't suggest C#/.NET AI bridges (Semantic Kernel, Azure OpenAI in C#)
- Don't recommend bootcamps ($5-15K hard NO)
- Don't pad with introductory fluff — get to the answer
- Don't over-engineer — ship over perfect, every project must have live URL
- Don't recommend more than 1 framework switch in same project
- Don't suggest skipping evals — they're the differentiator

## Quick lookup commands

When I ask "what should I do today?" or "where am I?":
1. Read `tracker/PROGRESS.md` for current day
2. Read corresponding section in `CURRICULUM.md` for that day
3. Show me the day's tasks + any blockers from previous logs

When I ask "help me with project X":
1. Read project entry in `CURRICULUM.md` for spec
2. Read `tracker/projects/README.md` for status
3. If project has its own repo, look there

When I ask "draft today's commit message":
1. Read today's `tracker/days/day-NNN.md`
2. Summarize: "Day NN: [one-line summary]"

## Useful file paths

- Strategy: `ai-engineer/ReadMe.md`
- Plan: `ai-engineer/CURRICULUM.md`
- Progress: `ai-engineer/tracker/PROGRESS.md`
- Today's log: `ai-engineer/tracker/days/day-NNN.md`
- Job tracker: `ai-engineer/tracker/interviews/job-tracker.md`
- Memory: `~/.claude/projects/-Volumes-SSD-Yogesh-Study-Material-Mac-Yogesh-Projects-ai-engineer/memory/`

## Communication tone

I prefer **caveman mode** for quick exchanges — fragments, no filler, no "Sure! I'd be happy to". Code, commits, security, and serious docs should be in normal English.

Don't end every response with a summary of what you did. I can read the diff. Don't ask "want me to do X next?" unless it's a real branching decision.

---

**TL;DR for AI assistants:**
- I'm a .NET dev going AI Engineer in 150 days
- Python only, API LLMs only, fintech niche, B2B + 1 B2C
- Read `CURRICULUM.md` for plan, `tracker/PROGRESS.md` for state
- Be direct, brief, brutal honest
- Don't re-litigate locked decisions
