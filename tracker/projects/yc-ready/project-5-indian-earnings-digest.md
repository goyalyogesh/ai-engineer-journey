# YC Application — Indian Earnings Digest

**Working name:** [TBD — suggestions: NiftyDigest, EarningsAI, BharatEarnings, MoatNotes]

**Tagline:** "AI-curated earnings insights for Indian retail investors. 5 minutes. Daily."

---

## Problem

**India has 100M+ retail investors. Most don't read earnings reports because:**
- Earnings calls are 60-90 min long, in English with finance jargon
- 200+ Nifty/Mid-cap companies report quarterly = 800+ events/year
- No quality vernacular content (Hindi/Tamil retail investors underserved)
- Existing tools (Moneycontrol, Screener) show data, not *insights*
- Bloomberg/Reuters cost $2000+/mo (institutional-only)

**Result:** Indian retail investors trade on news headlines + Telegram tips, not actual fundamentals. They underperform institutional investors by 8-12% annually (SEBI data).

---

## Solution

**5-minute AI-generated daily email covering:**
- Top 10 earnings reports from yesterday
- Each: 3-bullet summary, sentiment, key risk/opportunity, stock price reaction
- 1-click "deep dive" link to full LLM analysis
- Custom watchlist alerts (paid tier)
- Weekly: thematic analysis (e.g., "PSU bank earnings trends")

**Stack:**
- BSE/NSE filings → LLM (Claude) → curated digest
- VPS cron → email delivery (Resend) → Razorpay subscriptions
- Next.js landing + dashboard

---

## Why now (2026)

1. **LLM costs dropped 100x** (2022 → 2025) — finally feasible at consumer pricing
2. **Indian retail investing exploded:** 12M Demat accounts (2020) → 150M (2025)
3. **Discount brokers have no content moat** — Zerodha, Groww serve the trade, not the research
4. **English-language LLMs work for Indian financial docs** (NSE filings are in English)
5. **No incumbent owns this niche** (Bloomberg too expensive, Moneycontrol too generic)

---

## Market

- **TAM:** 150M Indian Demat accounts × ₹500/yr avg = ₹7,500 Cr ($900M) addressable annually
- **SAM:** 30M actively-investing retail users × ₹2,400/yr ($30/yr) = ₹720 Cr ($86M) servicable
- **SOM (year 1):** 10K paid users × ₹2,400 = ₹2.4 Cr ($290K ARR) realistic
- **Year 3 target:** 100K paid users = ₹24 Cr ($3M ARR)

Comparable: Robinhood Snacks (US) → 40M readers → acquired into Robinhood. We're the equivalent for India.

---

## Competition

| Competitor | What they do | Where we win |
|------------|--------------|--------------|
| Moneycontrol | News portal, ad-supported | We're personalized + AI summary, not noise |
| Screener.in | Data aggregator | We give insights, not raw numbers |
| Smallcase | Curated portfolios | We're upstream — research before they buy |
| Bloomberg | Institutional research | We're 1/200 the price, retail-targeted |
| INDmoney | Wealth app | We're cross-broker, not vertically-integrated |
| Substack newsletters | Manual finance writers | We cover 200+ companies, they cover 10 |

**Defensible because:**
- Real-time LLM pipeline = expensive moat (compute + prompt engineering)
- India-specific data sources, RBI compliance handled
- Network effect via shared watchlists (future)
- Brand = "trusted analyst friend" (paid for retention, not arbitrage)

---

## Business model

| Tier | Price | Features | Target audience |
|------|-------|----------|----------------|
| Free | ₹0 | Weekly digest (10 companies) | Lead generation |
| Pro | ₹199/mo (~$2.40) | Daily digest, alerts, custom watchlist (50 companies), historical archive | Serious retail investor |
| Premium | ₹999/mo (~$12) | Pro + LLM Q&A on any company, model portfolios, early reports | Active traders |

**Unit economics:**
- CAC: ₹50 (organic via newsletter virality)
- LTV: ₹4,800 (₹199 × 24 months avg subscription)
- LTV/CAC: 96x (insane for a SaaS — newsletter referrals make it free)
- Gross margin: 85% after LLM costs (~₹30/user/mo in API costs at scale)

---

## Traction milestones (Day 38 - Day 117)

| Day | Target | Status |
|-----|--------|--------|
| 45 | Public launch | 🔲 |
| 50 | 50 signups | 🔲 |
| 67 | 100 signups | 🔲 |
| 86 | First paying customer | 🔲 |
| 92 | $50 MRR | 🔲 |
| 109 | 500 signups, $250 MRR | 🔲 |
| 117 | YC application submission | 🔲 |
| 150 | 1000 signups, $500 MRR (post-YC) | 🔲 |

**These are conservative.** With LinkedIn/X distribution from Day 30 + Reddit launch + Indie Hackers — 1000 signups by Day 117 is realistic.

---

## Founder-market fit

**Why me:**
- **Indian heritage:** Born/raised in India, native cultural understanding, Hindi-speaker
- **Diaspora perspective:** Live in Canada, see what's broken about US fintech vs India
- **Technical depth:** Years building production .NET systems → can scale this beyond toy demo
- **AI engineering:** 5 production LLM apps shipped in 150 days (proven shipping ability)
- **Domain learning:** Spent 6 months building 4 fintech AI products before this — domain isn't shallow
- **Distribution proven:** 3500+ LinkedIn followers built during journey, real audience
- **Incentive alignment:** Indian retail investor myself, building for problem I have

**Why not someone else:**
- Bloomberg won't do retail (margin too low)
- Moneycontrol won't do AI (legacy ad business)
- Indian fintechs (Razorpay, CRED) focus on payments, not research
- US AI engineers don't understand Indian market nuances
- Indian engineers without LLM-native skills can't ship this fast

---

## Vision

### Year 1 (10K users, $300K ARR)
Daily earnings digest, India-only, English

### Year 2 (50K users, $1.5M ARR)
- Hindi + Tamil + Telugu LLM-translated versions
- Mobile app (React Native)
- Pro features: portfolio analysis, tax optimization integration

### Year 3 (200K users, $5M+ ARR)
- Expand to broader markets: Singapore SGX, Indonesian IDX (Asian retail investors)
- B2B API for fintechs (Smallcase, Groww integrate our research)
- Acquisition target by Zerodha, Groww, Smallcase, INDmoney

### Long-term moat
- **Brand:** "The financial analyst in your inbox" — high trust = price-insensitive
- **Data:** Proprietary historical sentiment + price-reaction dataset (future ML training)
- **Network:** Shared watchlists, social discussions on calls (Reddit + WhatsApp groups)

---

## Risks (be honest, YC respects this)

1. **SEBI regulation risk:** "AI-generated investment commentary" gray area — disclaimer-heavy, no recommendations
2. **LLM hallucination:** Wrong financial summaries → reputation risk → manual review for first 6 months
3. **Distribution dependency:** Newsletter virality vs paid ads — viral isn't guaranteed
4. **Saturation:** Substack writers + AI tools could replicate quickly — speed + quality matters
5. **India payment infrastructure:** Razorpay handles, but Indian users hate subscriptions — annual plans + free trial mitigation

---

## YC Application Q&A drafts

### Q: Describe what your company does in 50 characters or less.
**A:** "AI earnings digest for 150M Indian investors"

### Q: Describe what you do in 1-2 sentences.
**A:** "We send a 5-minute daily email summarizing earnings reports from Indian companies, written by AI. We turn 60-minute earnings calls into actionable insights for retail investors who don't have time or expertise to read raw filings."

### Q: What's new about your idea?
**A:** "Indian retail investing has 10x'd to 150M accounts but content tools haven't caught up — Bloomberg costs $24K/yr, Moneycontrol is ad-driven noise, and existing newsletters cover 10 companies, not 200. We use LLMs to scale quality research from 'one analyst, ten companies' to 'one editor, 200 companies, daily.' This wasn't possible 18 months ago — Claude/GPT-4 finally make financial document understanding affordable enough for ₹199/mo consumer pricing."

### Q: What's your unfair advantage?
**A:** "Three things: (1) I'm Indian-Canadian, technical, and bridge two markets natively. (2) I shipped 5 production AI fintech apps in 6 months before starting this — domain expertise + speed are proven, not promised. (3) I built distribution while building product — 3500+ LinkedIn followers + 1000+ newsletter signups before YC application = real users, not vaporware."

### Q: How will you make money?
**A:** "Freemium subscription. Free weekly digest, ₹199/mo Pro (daily + alerts), ₹999/mo Premium (LLM Q&A + portfolios). Indian fintech subscriptions have 18-24 month avg LTV at this price point. Path to $5M ARR by Year 3 with 200K paid users (out of 30M serviceable Indian retail investors)."

### Q: How do you know people want this?
**A:** "Days 38-100: launched, hit 1000+ signups via Reddit + LinkedIn organic, $XYZ MRR with X paying users, talked to 15 retail investors who confirmed pain. (Fill exact numbers Day 95.)"

---

## 1-min video script

**[Founder on camera, sitting at desk]**

"I'm [Name]. Until 6 months ago I was a .NET developer. I'm now applying to YC with my product, [name].

Here's the problem: India has 150 million retail stock investors. Most of them trade on news headlines because no one has time to read 200 quarterly earnings reports. Bloomberg costs $24,000 a year. Moneycontrol is ad-driven noise.

We send a 5-minute AI-generated email every day with the most important earnings insights. Free weekly tier, ₹199/mo for daily.

We launched [X days] ago. We have [N] signups, [N] paying customers, $[N] MRR. Growing [X]% week over week.

I'm uniquely positioned: I'm Indian-Canadian, understand both markets, shipped 5 production AI products in 6 months, and built distribution before product. This is a bigger opportunity than just India — we're building the AI-native financial research layer for emerging-market retail investors. Asia is next.

Here's our demo: [demo link]. Thanks YC."

**[End on camera with logo]**

---

## Pre-application checklist (Day 95)

- [ ] Working product live + demo URL
- [ ] 100+ users (or higher)
- [ ] 5+ paying customers
- [ ] $100+ MRR
- [ ] Founder LinkedIn polished
- [ ] 1-min video recorded
- [ ] Application Q1-12 drafted
- [ ] 3 user testimonials documented
- [ ] Architecture diagram (technical depth signal)
- [ ] Growth chart (signups over time)
- [ ] Press: any media coverage, even small (Indie Hackers, Reddit threads)

---

## Post-application checklist (Day 100+)

- [ ] Submitted on time
- [ ] LinkedIn announcement: "Just applied to YC W26"
- [ ] Continue building (YC interview odds higher with growth post-app)
- [ ] If invited: 10-min Zoom interview prep
- [ ] If accepted: $500K + 3 months in SF + decision: take YC or take job?
- [ ] If rejected: feedback often given — apply again next batch w/ more traction

---

**This document = your YC application skeleton. Fill in real numbers Day 95. Submit Day 100.**
