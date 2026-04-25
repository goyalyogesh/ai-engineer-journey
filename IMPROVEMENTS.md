# IMPROVEMENTS — Top 5 Additions + Top 3 Cuts

**Purpose:** Productivity multipliers + risk reductions identified after v2 curriculum review. Apply during pre-flight (before Day 1) and as ongoing cadences.

---

## 🟢 Top 5 Additions

### 1. `CLAUDE.md` template (HUGEST productivity multiplier)

**Setup once before Day 1.** Save 30 min/day forever.

**Stack note:** Using VS Code + Claude Code (Claude Pro subscription) instead of Cursor. Claude Code reads `CLAUDE.md` from project root for context. Same concept as `.cursorrules`, different filename.

Create `CLAUDE.md` in each project root:

```
# Project context for Claude Code

You are pair-programming with a .NET dev learning Python AI.

Tech stack:
- Python 3.12, type hints everywhere, Pydantic v2, async by default
- uv (not pip), VS Code as editor
- LangChain primary, Instructor for structured output
- LangSmith for tracing, Ragas for evals
- FastAPI backend, Streamlit demos, Next.js production

Style:
- Tests with pytest, no comments unless WHY non-obvious
- Concise responses, fragments OK
- Don't pad with "Sure! I'd be happy to"

Domain:
- I'm building fintech AI — bias toward financial document patterns
- Use Anthropic Claude as default, OpenAI as fallback

Anti-patterns:
- Don't suggest local LLMs (Ollama, llama.cpp)
- Don't suggest C#/.NET bridges
- Don't over-engineer — ship over perfect
```

**Add to pre-flight:** copy template to each new project repo Day 1 of project.

**Bonus — if you also want VS Code inline AI completions** (optional):
- Add Cline extension (free, BYOK Anthropic API) — uses your $30 API credits
- Or skip — Claude Code in terminal handles most coding tasks already

---

### 2. Project starter template repo

**Create once Day 13. Saves 2-3 hrs per project = 10-15 hrs total.**

Repo: `python-ai-starter` with:
- `pyproject.toml` (Python 3.12, uv, ruff, pytest)
- `.cursorrules` (above)
- `.env.example`
- `src/main.py` (FastAPI skeleton)
- `src/streamlit_app.py` (Streamlit skeleton)
- `src/models.py` (Pydantic v2 base models)
- `src/llm.py` (OpenAI + Anthropic clients with Instructor)
- `tests/` (pytest setup with LLM mocking)
- `evals/` (Ragas + custom eval framework)
- `.github/workflows/ci.yml` (run tests + evals on PR)
- `Dockerfile` + `docker-compose.yml`
- `README.md` template (problem, solution, demo, lessons sections)

Use as: `gh repo create new-project --template python-ai-starter`.

---

### 3. Family / Partner Conversation Day 0

**Single biggest dropout risk for 6-month commitments.**

Conversation script:
- "I'm transitioning careers — .NET to AI Engineer, 6 months"
- "Need 15 hrs/week: Mon-Thu evenings 7:30-9:30 PM, Sat 9 AM-2 PM, Sun 10 AM-12 PM"
- "Friday is fully ours / family time — non-negotiable"
- "Goal: $120K-160K AI Engineer role by Month 6"
- "Asking for explicit support — your buy-in matters"
- "If burnout shows up, you have permission to pull me off it"

**Document agreement** in your Notion. Re-confirm Month 3 (mid-burnout zone).

---

### 4. Pre-flight personal site + LinkedIn banner (Day 0, not Day 115)

**Compounds backlinks for 6 months.**

Setup BEFORE Day 1 (1 hour Saturday):
- Buy/clone Astro template (astro.build/themes — many free)
- Deploy to Vercel + custom domain
- Placeholder content: "Building 5 fintech AI projects — follow at /journey"
- Link to GitHub tracker repo + LinkedIn

LinkedIn banner (Canva, 30 min):
- Theme: AI/fintech
- Text: "AI Engineer | Fintech | Building Production LLM Apps"
- Update headline: same

**Why early:** every blog post, every comment, every DM links back to a polished profile. Day 30 networking starts hot.

---

### 5. Discord / Twitter accountability partner

**Quit rate drops 3x with one accountability partner.**

Setup pre-flight:
- Post in r/learnmachinelearning: "Looking for AI Engineer transition partner, 6-month plan, daily check-ins"
- Or join: Build in Public Discord, AI Engineers Discord, Latent Space Discord
- Find 1 person with similar timeline

Daily ritual:
- 1-line check-in: "Day 23 done, blocked on Pinecone setup, fixing tomorrow"
- 5 sec to send, accountability is psychological

Weekly call (15 min Sunday):
- What shipped? What's stuck? Encouragement?

---

## 🔴 Top 3 Cuts

### 1. Daily X posting from Day 50 → 3x/week

**Original:** daily X posts from Day 50
**Cut to:** 3 posts/week (Mon, Wed, Sat)
**Saved:** 30 min/day = 3.5 hrs/week
**Reason:** content fatigue is real, quality > quantity

LinkedIn 3x/wk + X 3x/wk + 8 blog posts is plenty. Don't burn out.

---

### 2. Drop blog post #6 (India-specific)

**Original:** 8 blog posts
**Cut to:** 7 blog posts
**Removed:** "Building India-Specific AI: Tax + Compliance" (Day 103)
**Replace with:** LinkedIn post (1 hr instead of 4)
**Reason:** India-specific reach is narrower; consolidate effort into broader topics

Keep: blog #1, #2, #3, #4, #5, #7, #8 (7 total).

---

### 3. YC application Day 100 — make conditional

**Original:** YC W26 application Day 100 (mandatory)
**Cut to:** Apply ONLY if Project 5 has traction (100+ users OR $100+ MRR by Day 95)
**Reason:** YC application takes ~12 hrs, distracts from job hunt if no traction yet

**Decision tree Day 95:**
- IF Project 5 ≥ 100 users OR ≥ $100 MRR → apply YC
- ELSE → skip, focus job hunt

---

## 🟢 Bonus Addition: System Design Track (added per review)

**Why:** Senior-level (5+ yrs experience) AI Engineer roles weight system design 30-40% of interview signal. Without it, you cap at junior offers ($90-130K) instead of senior ($160-220K). This is the single biggest leverage gap in the original plan.

### Integration (low overhead, high impact)

**Saturday block (already 5 hrs):**
- Hour 1: System design problem (1 hr)
- Hours 2-5: Project work (was 5 hrs, now 4)

**Sunday block (already 2 hrs):**
- 30 min DDIA reading every OTHER Sunday (alternates with Damodaran)

**Per project:**
- Ship `ARCHITECTURE.md` design doc alongside README
- Format: real SD interview answer (requirements, scale, components, tradeoffs, future)

### 18 SD problems (specific schedule)

| Day | Problem | Type |
|-----|---------|------|
| 41 | Design URL shortener | Generic warmup |
| 47 | Design Twitter feed | Generic |
| 53 | Design Uber / ride matching | Generic |
| 59 | Design Slack / messaging | Generic |
| 65 | Design payment processor | Fintech |
| 71 | **Design RAG system at scale (10M docs)** | LLM |
| 77 | Design distributed cache | Generic |
| 83 | **Design AI customer support system** | LLM |
| 89 | Design real-time fraud detection | Fintech |
| 95 | **Design eval pipeline for LLM** | LLM |
| 101 | Design transaction processing (1M TPS) | Fintech |
| 107 | **Design multi-tenant LLM gateway** | LLM |
| 113 | Design recommendation system | Generic |
| 119 | Design notification system | Generic |
| 125 | **Design agent orchestration system** | LLM |
| 131 | Design backtesting infrastructure | Fintech |
| 137 | Design reconciliation pipeline | Fintech |
| 143 | **Real 45-min mock SD interview** | All |

### DDIA reading schedule (12 chapters)

Every OTHER Sunday: Days 12, 24, 36, 48, 60, 72, 84, 96, 108, 120, 132, 144

### Cost
- DDIA book: $30 (add to budget)
- Time: 1 hr/Saturday + 30 min every other Sunday = ~25 hrs over 150 days

### Expected outcome
- 18 SD problems practiced
- 5 ARCHITECTURE.md docs in portfolio
- DDIA completed
- Offer ceiling raised by ~30-40%
- Senior-level interview pass rate dramatically up

---

## 🛡️ Risk Mitigations Added

### Burnout prevention (Months 3-4 zone)

- Weekly: 1 hour exercise minimum
- 8-hour sleep non-negotiable (track w/ phone or watch)
- Friday FULLY off — no LinkedIn checking
- Month 3: take 1 full day completely off
- Track energy 1-10 in daily log, not just hours

### Cost overrun prevention

- Set OpenAI/Anthropic budget alerts at $20 and $25 thresholds
- Use Anthropic prompt caching from Day 15 (NOT Day 105)
- Fallback if budget hits: Groq free tier (Llama 3.1 70B, very fast, free for dev)

### Free tier deprecation watch

Verify week-of-use:
- Pinecone (Day 28)
- Render (Day 51)
- Resend (Day 119)

Backup plans:
- Pinecone → pgvector on Supabase
- Render → Fly.io or own VPS
- Resend → Mailgun, Sendgrid free tiers

---

## 📋 Application Checklist (do during pre-flight)

- [ ] VS Code installed + Claude Code CLI installed (`npm install -g @anthropic-ai/claude-code`)
- [ ] `claude login` done (uses Claude Pro subscription)
- [ ] `CLAUDE.md` template saved as snippet
- [ ] `python-ai-starter` template repo created (Day 13 ideally)
- [ ] Family/partner conversation completed + agreement documented
- [ ] Personal site live with placeholder
- [ ] LinkedIn banner + headline updated
- [ ] Accountability partner found (Discord/Twitter)
- [ ] X posting cadence updated (3/wk, not daily)
- [ ] Blog post count revised to 7
- [ ] YC decision tree noted in `daily-plans/day-095.md`
- [ ] Budget alerts configured on OpenAI + Anthropic
- [ ] Anki deck created (optional but recommended)

---

## 📊 Updated Targets

| Metric | Original v2 | Improved |
|--------|-------------|----------|
| Blog posts | 8 | 7 |
| X posts/week | 7 (daily Day 50+) | 3 |
| LinkedIn posts/week | 3 (Day 30+) | 3 (unchanged) |
| YC application | Mandatory Day 100 | Conditional Day 95 |
| Burnout prevention | Not explicit | Hard rules |
| Pre-flight items | 12 | 22 |

---

## Why these specific picks

**Additions:** all are HIGH leverage / LOW effort. Cursor rules = 30 min setup, 30 min/day saved forever. Family conversation = 1 hour, prevents 30% dropout risk.

**Cuts:** all targeted content/distractions that show diminishing returns. Daily X = grindy. India-specific blog = narrow reach. YC w/o traction = waste.

**Risk mitigations:** address the 3 most common ways AI engineer transitions fail (burnout, cost shock, free tier surprise).

---

**Apply during pre-flight, then forget about it. The plan executes itself once these are in place.**
