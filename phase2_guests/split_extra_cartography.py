"""Split a SECOND round of cartography enrichment for distinctive multi-word
names without bios. The first 4 batches handled bioed guests; these extras
target rare/distinctive name patterns where a subagent has at least a chance
of finding the right LinkedIn (and can mark needs_verification:true if not).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
SCORED = ROOT / "scored"

COMMON_FIRST = {
    "mike", "matt", "alex", "alice", "anna", "andrew", "aaron", "brian", "chris",
    "daniel", "dan", "david", "emily", "eric", "jack", "jake", "james", "jason",
    "jeff", "jen", "jennifer", "john", "jon", "jordan", "joe", "joseph", "josh",
    "julie", "kate", "kevin", "lily", "lisa", "luke", "maria", "mark", "mary",
    "matt", "michael", "nick", "noah", "olivia", "paul", "peter", "rachel", "robert",
    "ryan", "sam", "sarah", "steve", "tom", "victor", "ben", "abby", "ali",
}

PLUSONE_RE = re.compile(r"\+1 of", re.I)


def is_distinctive(g: dict) -> bool:
    name = (g.get("name") or "").strip()
    if not name:
        return False
    if PLUSONE_RE.search(g.get("evidence", "") or ""):
        return False
    raw = (g.get("raw_display") or "").lower()
    if "@" in raw or "@" in name.lower():
        return False
    tokens = [t for t in name.split() if t]
    if len(tokens) < 2:
        return False
    first = tokens[0].lower().strip(".,")
    last = tokens[-1].lower().strip(".,")
    if first in COMMON_FIRST and len(last) <= 3:
        return False
    if any(len(t) >= 5 for t in tokens):
        return True
    return False


def main() -> None:
    leftover_path = SCORED / "cartography_leftover.json"
    data = json.load(leftover_path.open(encoding="utf-8"))
    leftover = data["guests"]

    distinctive = [g for g in leftover if is_distinctive(g)]
    rest = [g for g in leftover if not is_distinctive(g)]
    print(f"distinctive bioless multi-word names: {len(distinctive)}")
    print(f"rest of leftover (stay at heuristic 40): {len(rest)}")

    BATCH_SIZE = 24
    for i in range(0, len(distinctive), BATCH_SIZE):
        n = i // BATCH_SIZE + 1 + 4
        chunk = distinctive[i : i + BATCH_SIZE]
        out = SCORED / f"cartography_rescore_b{n}_input.json"
        out.write_text(
            json.dumps({"batch": n, "event": "cartography_a16z", "guests": chunk}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"Wrote batch {n}: {len(chunk)} guests -> {out.name}")

    SCORED.joinpath("cartography_leftover.json").write_text(
        json.dumps({"event": "cartography_a16z", "guests": rest}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Rewrote cartography_leftover.json with {len(rest)} guests (down from {len(leftover)})")


if __name__ == "__main__":
    main()
