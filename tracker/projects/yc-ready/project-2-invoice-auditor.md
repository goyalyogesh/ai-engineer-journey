# YC Application — Invoice AP Auditor (Backup B2B Pitch)

**Working name:** [TBD — suggestions: Audit.ai, InvoiceCheck, FlagAI, PayWise]

**Tagline:** "AI auditor for accounts payable. Catches fraud, errors, and policy violations in every invoice."

---

## When to use this pitch instead of P5

Use as primary YC pitch if:
- Project 5 fails to gain traction (< 100 users by Day 95)
- You land an enterprise pilot for P2 ($1K+ MRR)
- You want B2B SaaS path (higher salaries, slower growth)

Otherwise, P5 is preferred.

---

## Problem

**Companies waste 1-3% of accounts payable spend on errors and fraud:**
- Duplicate invoices (same vendor sends invoice twice)
- Math errors (line items don't sum to total)
- Tax mismatches (wrong tax rate applied)
- Policy violations (over-budget, unauthorized vendor, suspicious amounts)
- Genuine fraud (fake invoices, employee-vendor collusion)

**Current solutions:**
- Manual review by AP clerk (slow, misses 60%+ of issues)
- Rule-based ERP modules (rigid, false positives, no LLM intelligence)
- Enterprise tools (AppZen, Stampli) — $50K-200K/yr, only big companies

**SMBs ($10M-$500M revenue) have no good option.** They lose 0.5-2% of AP spend annually.

---

## Solution

**Upload invoices → AI audits in 30 seconds:**
- Extracts all fields (vendor, line items, totals, tax, payment terms)
- Runs 12+ rule checks (duplicates, math, tax, policy)
- LLM second-opinion: "Does this look suspicious in context?"
- Dashboard: flagged invoices, savings estimate, vendor risk scores
- Slack/email alerts for high-risk invoices
- Export to QuickBooks/Xero/SAP

**Stack:**
- FastAPI backend, Next.js dashboard, PostgreSQL
- Claude vision API for extraction + analysis
- Pinecone for vendor pattern matching

---

## Why now (2026)

1. **Multimodal LLMs** finally good enough for messy invoice PDFs (Claude 3.5+ vision)
2. **API costs** dropped enough to run on $1-5/invoice profitably
3. **Remote AP teams** post-COVID = standardization push, less paper
4. **Fraud rising:** vendor fraud up 40% YoY (ACFE 2024 report)
5. **No SMB-priced incumbent** — AppZen ($50K+) too expensive, manual is too slow

---

## Market

- **TAM:** US AP automation market $4.5B (2025), growing 12% YoY
- **SAM:** US SMB segment ($1B-$1B revenue) = ~200K companies × $5K/yr ARR = $1B
- **SOM (year 1):** 100 customers × $5K = $500K ARR realistic
- **Year 3:** 1500 customers × $8K = $12M ARR

International expansion year 2: India (massive AP fraud issue, no automation), Europe.

---

## Competition

| Competitor | Price | Where we win |
|------------|-------|--------------|
| AppZen | $50K-200K/yr | We're 1/10 the price for SMB |
| Stampli | $1K-5K/mo | We have better AI accuracy + no integration friction |
| Ramp | Free for cards | We work for ALL invoices, not just card transactions |
| Manual AP clerk | $50K/yr salary | We catch 3x more issues, 24/7 |
| QuickBooks built-in | Free w/ subscription | They have rules, we have intelligence |

**Defensible because:**
- Vendor fraud network: more customers = better fraud detection (network effect)
- Industry-specific models: trained on retail vs healthcare vs manufacturing invoices
- Workflow integration: not just SaaS, embedded in approval flow

---

## Business model

| Tier | Price | Features |
|------|-------|----------|
| Starter | $99/mo | 100 invoices/mo, basic audit |
| Growth | $499/mo | 1000 invoices/mo, all rules, Slack alerts |
| Scale | $2000/mo | 10K invoices/mo, custom rules, API access, SOC2 |
| Enterprise | Custom | White-glove, integrations, dedicated CSM |

**Unit economics:**
- CAC: $500-2000 (B2B sales takes time)
- LTV: $20K-50K (B2B SaaS retention 3+ years)
- LTV/CAC: 10-25x
- Gross margin: 75% (LLM costs scale w/ volume)

---

## Traction milestones

| Day | Target |
|-----|--------|
| 65 | Public launch |
| 75 | 5 free trials |
| 85 | First paid pilot ($99/mo) |
| 95 | 3 paying customers, $300 MRR |
| 117 | 10 paying customers, $1.5K MRR |

---

## Founder-market fit

- **Years building enterprise software** (.NET) — understand how enterprises buy + resist change
- **Built P1 (SEC 10-K Analyzer)** — proven I can extract + reason on financial docs
- **Indian + Canadian + US time zones** — can serve global SMBs
- **Direct experience w/ AP pain** — ex-employer or freelance work (frame this true to your story)

---

## Risks

1. **Long sales cycles:** SMB B2B = 3-6 month deals. YC wants fast growth.
2. **Trust threshold:** AP teams won't switch to AI without proof of accuracy. Need case studies.
3. **Integration nightmares:** Every customer has different ERP. Need open API.
4. **Compliance:** SOC2, GDPR — table stakes for enterprise. ~$30K to certify.
5. **Manual review overhead:** Year 1, you'll review every flagged invoice yourself for trust.

---

## YC fit assessment

**Strengths:**
- Big TAM ($4.5B)
- Clear ROI (saves money = easy sale)
- Defensible w/ network effects
- B2B SaaS = predictable revenue

**Weaknesses:**
- Slow growth vs B2C
- Need enterprise sales chops (not your strength yet)
- Crowded space (Stampli, AppZen, Tipalti, Bill.com)
- Hard to demo at YC interview without paying customers

**Verdict:** B+ YC fit. P5 (B2C) is A. Use this if P5 fails.

---

## YC Application Q&A drafts

### Q: Describe what your company does in 50 characters.
**A:** "AI invoice auditor for SMB accounts payable"

### Q: 1-2 sentences.
**A:** "We're an AI-powered audit layer for SMB accounts payable. Companies upload invoices, our AI catches fraud, errors, and policy violations in 30 seconds — saving 1-3% of AP spend annually for $99-2000/mo, vs $50K+ for enterprise alternatives."

### Q: Unfair advantage.
**A:** "I'm a former enterprise developer (.NET) who pivoted to building production AI systems. I shipped 5 fintech AI products in 6 months — extraction quality + cost optimization are my technical edge. I also know how SMBs buy software (slow, ROI-driven, no IT team) — I'll sell to them via Loom demos and free trials, not enterprise sales motions."

---

## Pre-application checklist (Day 95)

- [ ] Live product
- [ ] 3+ paying customers (or 1 enterprise pilot)
- [ ] Case study: documented savings for 1 customer
- [ ] $300+ MRR
- [ ] 30-day customer retention proof

---

**Use this if Project 5 doesn't hit traction. Pivot YC application focus accordingly.**
