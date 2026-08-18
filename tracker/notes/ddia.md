# DDIA Notes

Reading "Designing Data-Intensive Applications" by Martin Kleppmann.
30 min every other Sunday. Total: 12 chapters by Day 144.

## Schedule

| Day | Chapter | Status |
|-----|---------|--------|
| 12 | Ch 1 — Reliable, Scalable, Maintainable Apps | ✅ |



| 24 | Ch 2 — Data Models & Query Languages | 🔲 |
| 36 | Ch 3 — Storage & Retrieval | 🔲 |
| 48 | Ch 4 — Encoding & Evolution | 🔲 |
| 60 | Ch 5 — Replication | 🔲 |
| 72 | Ch 6 — Partitioning | 🔲 |
| 84 | Ch 7 — Transactions | 🔲 |
| 96 | Ch 8 — Trouble with Distributed Systems | 🔲 |
| 108 | Ch 9 — Consistency & Consensus | 🔲 |
| 120 | Ch 10 — Batch Processing | 🔲 |
| 132 | Ch 11 — Stream Processing | 🔲 |
| 144 | Ch 12 — The Future of Data Systems | 🔲 |

---

## Ch 1 notes

**Reliability** — the system works correctly even when things go wrong.
- *Fault* vs *failure*: a fault is one component deviating from spec (a disk dying);
  a failure is the whole system stopping serving users. Good systems tolerate faults
  without becoming failures (fault-tolerant / resilient).
- Three sources of faults: hardware (disks, RAM, power — mitigated with redundancy),
  software bugs (correlated failures across many nodes, harder to guard against),
  human error (the most common cause in practice — mitigated by good abstractions,
  sandboxes for testing, easy rollback, monitoring/telemetry).

**Scalability** — the system's ability to cope with increased load.
- You can't say "X is scalable" in the abstract — you have to ask "scalable with
  respect to what?" (requests/sec, data volume, read/write ratio, etc.) — these are
  *load parameters*.
- Two questions once load grows: (1) how does performance change if load increases
  but resources stay fixed? (2) how much do you need to increase resources to keep
  performance the same?
- Measure performance with **percentiles**, not averages — p50 (median), p95, p99.
  A slow p99 means your slowest 1% of users are having a bad time, even if the
  average looks fine — averages hide exactly the users you'd most want to notice.

**Maintainability** — most of a system's cost is *after* it's first built (fixing
bugs, adding features, operating it). Three design principles that make this easier:
- **Operability** — make it easy for ops to keep the system running smoothly
  (good monitoring, predictable behavior, good docs).
- **Simplicity** — manage complexity by removing *accidental* complexity (complexity
  not inherent to the problem, just how it happened to get built) — good abstractions
  are the main tool here.
- **Evolvability** — make it easy to change the system later as requirements change;
  closely related to Agile practices, but at the data-system/architecture level.

**Why this matters for the AI-engineer work ahead:** RAG pipelines and vector DBs
(Phase 2 onward) are themselves data-intensive systems — the same reliability/
scalability/maintainability lens applies to a Pinecone index or a chunking pipeline
as to any other data system in this book.

## Ch 2 notes
(fill in after Day 24)
