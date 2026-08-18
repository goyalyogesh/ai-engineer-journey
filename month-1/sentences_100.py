"""
100 finance/10-K-flavored sentences across 10 topics (10 each), used by both
14ChromaDb.py and 14Pinecone.py so the two tools search the exact same data.
Topics deliberately mirror what a real SEC 10-K covers (revenue, buybacks,
supply chain risk, litigation, cybersecurity, layoffs, executive pay, debt,
M&A) plus one unrelated "weather" topic as a control group to prove semantic
search separates topics, not just keywords.
"""

SENTENCES = [
    # revenue_growth
    {"id": "rev-1", "topic": "revenue_growth", "text": "Revenue increased significantly this quarter due to strong consumer demand."},
    {"id": "rev-2", "topic": "revenue_growth", "text": "Quarterly sales grew as a result of higher customer order volumes."},
    {"id": "rev-3", "topic": "revenue_growth", "text": "Net sales rose year-over-year driven by expansion into new markets."},
    {"id": "rev-4", "topic": "revenue_growth", "text": "The company reported a substantial increase in top-line revenue."},
    {"id": "rev-5", "topic": "revenue_growth", "text": "Total revenue climbed on the back of robust holiday season sales."},
    {"id": "rev-6", "topic": "revenue_growth", "text": "Sales figures improved markedly compared to the same period last year."},
    {"id": "rev-7", "topic": "revenue_growth", "text": "The business saw accelerated revenue growth across all product segments."},
    {"id": "rev-8", "topic": "revenue_growth", "text": "Income from operations increased as customer demand strengthened."},
    {"id": "rev-9", "topic": "revenue_growth", "text": "Annual revenue exceeded expectations due to strong subscription growth."},
    {"id": "rev-10", "topic": "revenue_growth", "text": "The company posted record quarterly sales driven by new product launches."},

    # buybacks
    {"id": "buy-1", "topic": "buybacks", "text": "The board approved a new share repurchase program worth $500 million."},
    {"id": "buy-2", "topic": "buybacks", "text": "Management returned capital to shareholders through stock buybacks."},
    {"id": "buy-3", "topic": "buybacks", "text": "The company repurchased a significant number of outstanding shares."},
    {"id": "buy-4", "topic": "buybacks", "text": "A stock buyback program was authorized to boost shareholder value."},
    {"id": "buy-5", "topic": "buybacks", "text": "The firm increased its dividend and expanded its repurchase authorization."},
    {"id": "buy-6", "topic": "buybacks", "text": "Capital return to investors increased via buybacks and dividend hikes."},
    {"id": "buy-7", "topic": "buybacks", "text": "The company continued to reduce share count through repurchases."},
    {"id": "buy-8", "topic": "buybacks", "text": "Excess cash was used to fund an accelerated share buyback plan."},
    {"id": "buy-9", "topic": "buybacks", "text": "Shareholders benefited from an increased quarterly dividend payout."},
    {"id": "buy-10", "topic": "buybacks", "text": "The repurchase program was expanded following strong free cash flow."},

    # supply_chain
    {"id": "sup-1", "topic": "supply_chain", "text": "The company faces risks related to disruptions in its global supply chain."},
    {"id": "sup-2", "topic": "supply_chain", "text": "Supply chain constraints could adversely affect production capacity."},
    {"id": "sup-3", "topic": "supply_chain", "text": "Dependence on a limited number of suppliers poses operational risk."},
    {"id": "sup-4", "topic": "supply_chain", "text": "Component shortages have delayed manufacturing timelines."},
    {"id": "sup-5", "topic": "supply_chain", "text": "Geopolitical tensions may disrupt the sourcing of critical materials."},
    {"id": "sup-6", "topic": "supply_chain", "text": "The company is exposed to risks from single-source supplier relationships."},
    {"id": "sup-7", "topic": "supply_chain", "text": "Logistics disruptions have increased shipping costs and delivery delays."},
    {"id": "sup-8", "topic": "supply_chain", "text": "Raw material shortages could impact the company's production schedule."},
    {"id": "sup-9", "topic": "supply_chain", "text": "Supplier concentration risk remains a key concern for operations."},
    {"id": "sup-10", "topic": "supply_chain", "text": "Global shipping delays have affected the timely delivery of inventory."},

    # litigation
    {"id": "lit-1", "topic": "litigation", "text": "The company is currently involved in several ongoing legal proceedings."},
    {"id": "lit-2", "topic": "litigation", "text": "A class action lawsuit was filed against the company by shareholders."},
    {"id": "lit-3", "topic": "litigation", "text": "Litigation costs increased due to multiple pending legal disputes."},
    {"id": "lit-4", "topic": "litigation", "text": "The firm faces potential liability from an intellectual property lawsuit."},
    {"id": "lit-5", "topic": "litigation", "text": "Regulatory investigations could result in significant legal expenses."},
    {"id": "lit-6", "topic": "litigation", "text": "The company settled a long-standing legal dispute with a former partner."},
    {"id": "lit-7", "topic": "litigation", "text": "Pending litigation may have a material adverse effect on operations."},
    {"id": "lit-8", "topic": "litigation", "text": "The company is defending itself against allegations of patent infringement."},
    {"id": "lit-9", "topic": "litigation", "text": "Legal reserves were increased in anticipation of litigation outcomes."},
    {"id": "lit-10", "topic": "litigation", "text": "An adverse court ruling could result in substantial monetary damages."},

    # cybersecurity
    {"id": "cyb-1", "topic": "cybersecurity", "text": "The company faces ongoing risks related to cybersecurity threats."},
    {"id": "cyb-2", "topic": "cybersecurity", "text": "A data breach could expose sensitive customer information."},
    {"id": "cyb-3", "topic": "cybersecurity", "text": "Cyberattacks on the company's systems could disrupt operations."},
    {"id": "cyb-4", "topic": "cybersecurity", "text": "Investments in cybersecurity infrastructure were increased this year."},
    {"id": "cyb-5", "topic": "cybersecurity", "text": "The firm experienced a security incident affecting internal systems."},
    {"id": "cyb-6", "topic": "cybersecurity", "text": "Ransomware attacks pose a growing threat to business continuity."},
    {"id": "cyb-7", "topic": "cybersecurity", "text": "Unauthorized access to company data could result in reputational harm."},
    {"id": "cyb-8", "topic": "cybersecurity", "text": "The company strengthened its network security following a recent incident."},
    {"id": "cyb-9", "topic": "cybersecurity", "text": "Data privacy regulations require enhanced cybersecurity measures."},
    {"id": "cyb-10", "topic": "cybersecurity", "text": "A successful cyberattack could lead to significant financial losses."},

    # layoffs
    {"id": "lay-1", "topic": "layoffs", "text": "The company announced a workforce reduction as part of cost-cutting efforts."},
    {"id": "lay-2", "topic": "layoffs", "text": "Layoffs were implemented to streamline operations and reduce expenses."},
    {"id": "lay-3", "topic": "layoffs", "text": "The firm reduced headcount across several business units."},
    {"id": "lay-4", "topic": "layoffs", "text": "Restructuring efforts resulted in the elimination of certain positions."},
    {"id": "lay-5", "topic": "layoffs", "text": "Employee attrition increased amid broader industry-wide layoffs."},
    {"id": "lay-6", "topic": "layoffs", "text": "The company initiated a reduction in force to improve efficiency."},
    {"id": "lay-7", "topic": "layoffs", "text": "Severance costs were recorded in connection with staff reductions."},
    {"id": "lay-8", "topic": "layoffs", "text": "Hiring was paused as part of a broader cost containment strategy."},
    {"id": "lay-9", "topic": "layoffs", "text": "The workforce was reduced by approximately ten percent this year."},
    {"id": "lay-10", "topic": "layoffs", "text": "Management implemented layoffs to align staffing with lower demand."},

    # executive_pay
    {"id": "exe-1", "topic": "executive_pay", "text": "The CEO's compensation package was approved by the board of directors."},
    {"id": "exe-2", "topic": "executive_pay", "text": "Executive pay increased in line with company performance targets."},
    {"id": "exe-3", "topic": "executive_pay", "text": "Shareholders voted on executive compensation at the annual meeting."},
    {"id": "exe-4", "topic": "executive_pay", "text": "The compensation committee reviewed executive pay structures this year."},
    {"id": "exe-5", "topic": "executive_pay", "text": "Stock-based compensation for executives rose significantly."},
    {"id": "exe-6", "topic": "executive_pay", "text": "The proxy statement disclosed details of senior management pay."},
    {"id": "exe-7", "topic": "executive_pay", "text": "Performance-based bonuses were awarded to top executives."},
    {"id": "exe-8", "topic": "executive_pay", "text": "Executive compensation is tied to long-term shareholder value creation."},
    {"id": "exe-9", "topic": "executive_pay", "text": "The board approved a new incentive plan for senior leadership."},
    {"id": "exe-10", "topic": "executive_pay", "text": "Say-on-pay votes reflected shareholder views on executive compensation."},

    # debt
    {"id": "debt-1", "topic": "debt", "text": "The company increased its total debt to fund recent acquisitions."},
    {"id": "debt-2", "topic": "debt", "text": "Leverage ratios rose following the issuance of new senior notes."},
    {"id": "debt-3", "topic": "debt", "text": "The firm refinanced a portion of its outstanding debt this quarter."},
    {"id": "debt-4", "topic": "debt", "text": "Interest expense increased due to higher borrowing costs."},
    {"id": "debt-5", "topic": "debt", "text": "The company's credit rating was downgraded due to elevated leverage."},
    {"id": "debt-6", "topic": "debt", "text": "Debt covenants restrict the company's ability to take on additional borrowing."},
    {"id": "debt-7", "topic": "debt", "text": "The company issued long-term bonds to strengthen its balance sheet."},
    {"id": "debt-8", "topic": "debt", "text": "Total indebtedness grew as the company financed expansion plans."},
    {"id": "debt-9", "topic": "debt", "text": "Rising interest rates increased the cost of servicing existing debt."},
    {"id": "debt-10", "topic": "debt", "text": "The firm used proceeds from a bond offering to repay maturing debt."},

    # mergers_acquisitions
    {"id": "ma-1", "topic": "mergers_acquisitions", "text": "The company completed the acquisition of a smaller competitor."},
    {"id": "ma-2", "topic": "mergers_acquisitions", "text": "A merger agreement was announced between the two companies."},
    {"id": "ma-3", "topic": "mergers_acquisitions", "text": "The acquisition is expected to close by the end of the fiscal year."},
    {"id": "ma-4", "topic": "mergers_acquisitions", "text": "The company acquired a technology startup to expand its product line."},
    {"id": "ma-5", "topic": "mergers_acquisitions", "text": "Integration costs related to the recent acquisition were higher than expected."},
    {"id": "ma-6", "topic": "mergers_acquisitions", "text": "The board approved a definitive merger agreement with a strategic partner."},
    {"id": "ma-7", "topic": "mergers_acquisitions", "text": "The company divested a non-core business unit as part of its strategy."},
    {"id": "ma-8", "topic": "mergers_acquisitions", "text": "Regulatory approval is pending for the proposed merger."},
    {"id": "ma-9", "topic": "mergers_acquisitions", "text": "The acquisition added new capabilities to the company's product portfolio."},
    {"id": "ma-10", "topic": "mergers_acquisitions", "text": "Synergies from the merger are expected to reduce operating costs."},

    # weather (unrelated control group)
    {"id": "wx-1", "topic": "weather", "text": "It was raining heavily in Seattle yesterday afternoon."},
    {"id": "wx-2", "topic": "weather", "text": "A winter storm brought several inches of snow to the region."},
    {"id": "wx-3", "topic": "weather", "text": "Temperatures rose sharply over the weekend across the Midwest."},
    {"id": "wx-4", "topic": "weather", "text": "Coastal areas experienced strong winds ahead of the storm."},
    {"id": "wx-5", "topic": "weather", "text": "The weather forecast predicts clear skies for the upcoming week."},
    {"id": "wx-6", "topic": "weather", "text": "Flooding was reported in low-lying areas after days of rain."},
    {"id": "wx-7", "topic": "weather", "text": "A heatwave is expected to affect the southern United States."},
    {"id": "wx-8", "topic": "weather", "text": "Snowfall totals broke records in several mountain towns this winter."},
    {"id": "wx-9", "topic": "weather", "text": "Thunderstorms rolled through the valley late in the evening."},
    {"id": "wx-10", "topic": "weather", "text": "Sunny conditions are expected to continue through the weekend."},
]

QUERIES = [
    "Did the company have any employee layoffs?",
    "How is the company managing legal risk?",
    "Did the company return money to shareholders?",
]

assert len(SENTENCES) == 100, f"expected 100 sentences, got {len(SENTENCES)}"
