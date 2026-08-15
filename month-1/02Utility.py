"""
Day 2 practice: rewriting a small .NET-style utility in Python.

The utility: parse raw log lines, filter/aggregate them, and print a report,
fetching from multiple "sources" concurrently. Each section below is
annotated with the C# idiom it replaces.

Run it: python 02Utility.py  (no extra pip installs needed — stdlib only)
"""

from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass
from datetime import datetime


# ---------------------------------------------------------------------------
# 1. Type-hinted dataclass  ==  C# record / POCO
# ---------------------------------------------------------------------------
# C#:  public record LogEntry(DateTime Timestamp, string Level, string Source, string Message);

@dataclass
class LogEntry:
    timestamp: datetime
    level: str  # "INFO" | "WARN" | "ERROR"
    source: str
    message: str


RAW_LOGS = [
    "2026-08-15T09:01:12|INFO|auth-service|User 42 logged in",
    "2026-08-15T09:02:03|WARN|payments-service|Retrying charge for order 991",
    "2026-08-15T09:02:05|ERROR|payments-service|Charge failed for order 991: card declined",
    "2026-08-15T09:03:44|INFO|auth-service|User 17 logged in",
    "2026-08-15T09:05:10|ERROR|inventory-service|SKU 4471 not found",
    "2026-08-15T09:06:00|WARN|auth-service|Rate limit approaching for user 42",
    "2026-08-15T09:07:22|INFO|inventory-service|Restocked SKU 4471 (qty 50)",
    "2026-08-15T09:08:41|ERROR|payments-service|Charge failed for order 992: timeout",
]


def parse_log_line(line: str) -> LogEntry:
    """Turn one raw '|'-delimited line into a LogEntry."""
    raw_ts, level, source, message = line.split("|", maxsplit=3)
    return LogEntry(
        timestamp=datetime.fromisoformat(raw_ts),
        level=level,
        source=source,
        message=message,
    )


# ---------------------------------------------------------------------------
# 2. List comprehension  ==  C# LINQ .Select()
# ---------------------------------------------------------------------------
# C#:  var entries = rawLines.Select(ParseLogLine).ToList();

def parse_all(raw_lines: list[str]) -> list[LogEntry]:
    return [parse_log_line(line) for line in raw_lines]


# ---------------------------------------------------------------------------
# 3. List comprehension with a condition  ==  C# LINQ .Where()
# ---------------------------------------------------------------------------
# C#:  var errors = entries.Where(e => e.Level == "ERROR").ToList();

def filter_by_level(entries: list[LogEntry], level: str) -> list[LogEntry]:
    return [entry for entry in entries if entry.level == level]


# ---------------------------------------------------------------------------
# 4. Dict comprehension (+ a set comprehension along the way)
#    ==  C# entries.GroupBy(e => e.Level).ToDictionary(g => g.Key, g => g.Count())
# ---------------------------------------------------------------------------

def count_by_level(entries: list[LogEntry]) -> dict[str, int]:
    levels = {entry.level for entry in entries}  # set comprehension: unique levels
    return {level: len(filter_by_level(entries, level)) for level in levels}


# ---------------------------------------------------------------------------
# 5. f-strings  ==  C# interpolated strings ($"...")
# ---------------------------------------------------------------------------

def print_report(entries: list[LogEntry]) -> None:
    counts = count_by_level(entries)
    print(f"--- Log report ({len(entries)} entries) ---")
    for level in sorted(counts):
        print(f"  {level:<5} : {counts[level]}")

    print("\n--- ERROR details ---")
    for entry in filter_by_level(entries, "ERROR"):
        print(f"  [{entry.timestamp:%H:%M:%S}] {entry.source}: {entry.message}")


# ---------------------------------------------------------------------------
# 6. async/await  ==  C# async Task<T> + await + Task.WhenAll
# ---------------------------------------------------------------------------
# C#:
#   async Task<List<LogEntry>> FetchLogsAsync(string source) {
#       await Task.Delay(latencyMs);
#       return ...;
#   }
#   var results = await Task.WhenAll(sources.Select(FetchLogsAsync));
#
# Note: Python's asyncio is single-threaded (one event loop, cooperative
# multitasking) rather than .NET's thread-pool-backed Task model. The
# syntax looks nearly identical; the execution model underneath isn't.

async def fetch_logs_from_source(source: str, latency_seconds: float) -> list[LogEntry]:
    """Pretend this source is a network call — simulate I/O with a sleep."""
    await asyncio.sleep(latency_seconds)
    return [entry for entry in parse_all(RAW_LOGS) if entry.source == source]


async def fetch_all_sources() -> list[LogEntry]:
    sources = ["auth-service", "payments-service", "inventory-service"]

    # asyncio.gather == Task.WhenAll: runs all three "fetches" concurrently,
    # so total wait time is ~the slowest one, not the sum of all three.
    results = await asyncio.gather(
        *(fetch_logs_from_source(source, random.uniform(0.1, 0.5)) for source in sources)
    )

    return [entry for group in results for entry in group]  # flatten list[list[...]] -> list[...]


async def main() -> None:
    print("Fetching logs from 3 sources concurrently...\n")
    entries = await fetch_all_sources()
    entries.sort(key=lambda e: e.timestamp)
    print_report(entries)


if __name__ == "__main__":
    asyncio.run(main())
