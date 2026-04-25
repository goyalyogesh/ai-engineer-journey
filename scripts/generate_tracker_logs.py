"""Generate 150 empty tracker log files (one per working day).

Run: python scripts/generate_tracker_logs.py
Output: tracker/days/day-001.md ... day-150.md (skips day-001 if already filled)
"""
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUT = ROOT / "tracker" / "days"
OUT.mkdir(parents=True, exist_ok=True)

# Phase ranges (day_start, day_end, phase_num, phase_name)
PHASES = [
    (1, 12, 1, "Foundations + User Research"),
    (13, 37, 2, "RAG + Project 1 (SEC 10-K Analyzer)"),
    (38, 67, 3, "Project 5 Launch + Project 2 (Invoice Auditor)"),
    (68, 92, 4, "Agents + Project 3 (Equity Research Agent)"),
    (93, 117, 5, "India Spec + Project 4 + YC App"),
    (118, 150, 6, "Job Hunt + Offer"),
]

# Day-of-week pattern: Mon, Tue, Wed, Thu, (Fri OFF), Sat, Sun
# Day 1 = Mon, Day 2 = Tue, ..., Day 5 = Sat, Day 6 = Sun, Day 7 = Mon (next week)
DOW_PATTERN = ["Mon", "Tue", "Wed", "Thu", "Sat", "Sun"]


def get_phase(day_num: int) -> tuple[int, str]:
    for start, end, pnum, pname in PHASES:
        if start <= day_num <= end:
            return pnum, pname
    return 6, "Job Hunt + Offer"  # fallback


def get_dow(day_num: int) -> str:
    # Day 1 → index 0 (Mon), Day 6 → index 5 (Sun), Day 7 → index 0 (Mon next wk)
    return DOW_PATTERN[(day_num - 1) % 6]


def get_hours_default(dow: str) -> str:
    if dow == "Sat":
        return "5"
    return "2"


def render(day_num: int) -> str:
    dow = get_dow(day_num)
    phase_num, phase_name = get_phase(day_num)
    hours = get_hours_default(dow)

    md = f"# Day {day_num:03d} — YYYY-MM-DD ({dow})\n\n"
    md += f"**Phase:** {phase_num} — {phase_name}\n"
    md += f"**Hours worked:** _ / {hours}\n"
    md += "**Energy level:** Low / Medium / High\n"
    md += "**Mood:** _\n\n"
    md += "---\n\n"
    md += "## Today's focus\n\n"
    md += f"📋 Plan: [`daily-plans/day-{day_num:03d}.md`](../../daily-plans/day-{day_num:03d}.md)\n\n"
    md += "[Copy the day's plan from daily-plans/day-{:03d}.md or summarize in 3 bullets]\n\n".format(day_num)
    md += "---\n\n"
    md += "## What I did\n\n"
    md += "- \n- \n- \n\n"
    md += "---\n\n"
    md += "## What I learned\n\n"
    md += "- \n- \n\n"
    md += "---\n\n"
    md += "## What I built / shipped\n\n"
    md += "- \n- Links: [GitHub commit, demo URL, blog post]\n\n"
    md += "---\n\n"
    md += "## Blockers / issues\n\n"
    md += "- \n\n"
    md += "---\n\n"
    md += "## Tomorrow's focus\n\n"
    md += "- \n- \n\n"
    md += "---\n\n"
    md += "## Build-in-public\n\n"
    md += "- [ ] LinkedIn post drafted/posted? Link:\n"
    md += "- [ ] X post drafted/posted? Link:\n\n"
    md += "---\n\n"
    md += "## Metrics snapshot (optional, weekly OK)\n\n"
    md += "- LinkedIn followers: \n"
    md += "- GitHub stars: \n"
    md += "- P5 users: \n"
    md += "- Apps sent: \n\n"
    md += "---\n\n"
    md += "## Notes / random thoughts\n\n"
    md += "[Free space — anything worth remembering]\n"
    return md


count_created = 0
count_skipped = 0
for day_num in range(1, 151):
    path = OUT / f"day-{day_num:03d}.md"
    # Skip Day 1 if already populated (more than just template)
    if path.exists() and day_num == 1:
        size = path.stat().st_size
        if size > 500:  # populated, not empty template
            count_skipped += 1
            continue
    path.write_text(render(day_num))
    count_created += 1

print(f"Created {count_created} tracker log files, skipped {count_skipped} (already populated)")
print(f"Output: {OUT}")
