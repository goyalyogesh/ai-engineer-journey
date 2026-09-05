# Interview Prep Log — First National Financial, AI Engineer

Running log of prep work for this interview. New sessions: append here, don't
scatter notes elsewhere.

## 2026-09-03
- Job posting saved → `job-posting.md`
- Resume snapshot saved → `resume-snapshot.txt` (from `~/Downloads/AI_Developer_Yogesh_Resume.docx`)
- Full 3-day prep plan built and published as an artifact, copy saved →
  `interview-plan.html` (open directly in a browser)
  - Anchor story: Order Diagnosis Agent eval harness (21-scenario, LLM-as-judge,
    caught a false-confidence bug, insufficient-evidence recall 0%→100%) —
    maps near verbatim to the JD's "combine probabilistic AI with deterministic
    rules" and "confidence scoring / error analysis" lines.
  - Named gaps to self-address: Azure/Databricks vs. AWS-heavy experience;
    telecom (Bell) vs. regulated-lending domain (Berkadia's Loan View System
    is the bridge, underused on the resume as-is).
- Interview: Monday Sep 7, 2026, virtual, 45 min, hiring manager screen.

## 2026-09-05
- Built a reference RAG architecture to defend "AWS Bedrock" on the resume →
  `bedrock-rag-defense.md`. Scenario: "Ops Knowledge Copilot" — messy
  multi-source data (vendor PDFs/scanned docs, wiki HTML, ticket exports,
  vendor spec sheets, Slack/email threads, SQL order data) into Titan
  embeddings → Pinecone → Claude via Bedrock, with authority-ranked
  conflict resolution and citation-forced generation.
  - Key "why Bedrock" answer: data stays inside AWS network boundary
    (PrivateLink/VPC), one IAM/audit model across foundation models, native
    Guardrails — the argument a regulated shop actually wants to hear.
  - Landmine list included: be honest about NOT using Bedrock Knowledge
    Bases/Agents (used LangChain orchestration instead), keep vector store
    story consistent with resume (Pinecone/ChromaDB, not OpenSearch).

- Expanded `bedrock-rag-defense.md` with deep-dive Evals and Observability
  sections: two-layer eval metrics (retrieval hit-rate/MRR/precision-recall
  vs. LLM-as-judge generation grading incl. false-confidence rate reused
  from the Order Diagnosis Agent), CI-gated eval regression, correlation-ID
  request tracing, freshness/ingestion-failure monitoring, and an
  auditability angle (chunk IDs + doc versions stored per answer) as the
  lead point for a regulated-industry interviewer.
  - New landmines logged: be honest if no dedicated LLM-ops platform
    (LangSmith/Langfuse/Arize) was used — CloudWatch + custom logging is
    the real story; same for Bedrock's built-in Model Evaluation feature —
    custom harness is the stronger, honest answer.

- Added 4 mermaid diagrams to `bedrock-rag-defense.md` for memorization:
  system-at-a-glance (6 main nodes: Sources → Ingestion → Embeddings →
  Vector Store → Serving API → Model, wrapped by an Observability/Eval
  loop), ingestion pipeline detail, serving/request pipeline detail, and
  the eval+observability loop end to end. Render in any mermaid-aware
  viewer (VS Code w/ Mermaid extension, GitHub, Obsidian).

## Open items
- [ ] Independently verify company-specific facts (recent FNF news, what
      "AI Factory" concretely means) — flagged in the plan as unverified.
- [ ] Day 3 mock run — not yet done.
