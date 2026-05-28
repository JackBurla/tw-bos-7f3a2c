"""Split cartography_a16z scored guests into enrichment batches.

Strategy: only enrich guests where there's enough signal for the subagent
to actually verify them — i.e. those with a non-empty bio OR a distinctive
multi-word name (>=2 tokens, not just initials, not a single common first
name). Generic first-name-only or initials-only entries stay at their
heuristic score because there's nothing to search for.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parent
SCORED = ROOT / "scored"


def is_searchable(guest: dict) -> bool:
    """Enrich only guests where we have real signal to verify.

    Criteria:
      - has a Partiful bio (non-empty), OR
      - is the event speaker / moderator (kept by SPEAKERS lookup), OR
      - is Jack himself.
    Pure-name guests without bios get left at heuristic priors because
    subagents can't reliably identify a 'Mike' or 'Alice' via web search.
    """
    name = guest.get("name", "").strip().lower()
    if name in {"jack rzucidlo", "kevin parker", "heidi erlacher"}:
        return True
    evidence = guest.get("evidence", "") or ""
    if "+1 of" in evidence.lower() or evidence.startswith("+1 of"):
        return False
    if "no partiful bio" in evidence.lower():
        return False
    role = guest.get("role", "") or ""
    if role and role != name:
        return True
    return False


def main() -> None:
    src = json.load((SCORED / "cartography_a16z.json").open(encoding="utf-8"))
    guests = src["guests"]

    searchable = []
    leftover = []
    for g in guests:
        if is_searchable(g):
            searchable.append(g)
        else:
            leftover.append(g)

    BATCH_SIZE = 24
    for i in range(0, len(searchable), BATCH_SIZE):
        batch_num = i // BATCH_SIZE + 1
        chunk = searchable[i : i + BATCH_SIZE]
        out_path = SCORED / f"cartography_rescore_b{batch_num}_input.json"
        out_path.write_text(
            json.dumps(
                {"batch": batch_num, "event": "cartography_a16z", "guests": chunk},
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        print(f"Wrote batch {batch_num}: {len(chunk)} guests -> {out_path.name}")

    leftover_path = SCORED / "cartography_leftover.json"
    leftover_path.write_text(
        json.dumps({"event": "cartography_a16z", "guests": leftover}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Wrote leftover (initials/first-name-only): {len(leftover)} guests -> {leftover_path.name}")
    print(f"Total guests: {len(guests)} | searchable: {len(searchable)} | leftover: {len(leftover)}")


if __name__ == "__main__":
    main()
