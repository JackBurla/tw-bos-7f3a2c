"""Merge cartography_rescore_b1..bN into cartography_a16z.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

SCORED = Path(__file__).parent / "scored"
EVENT = {
    "event_id": "cartography_a16z",
    "event_name": "Platform to Pipeline: Fireside Chat with a16z and the CEO of Cartography",
    "event_partiful": "https://partiful.com/e/vQDvxdHU5dZgwJAFBzmZ",
    "event_host": "Cartography / a16z bio / Fenwick",
    "event_date": "2026-05-29",
    "declared_count": 379,
}


def main() -> None:
    num_batches = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    if not num_batches:
        files = sorted(SCORED.glob("cartography_rescore_b*.json"))
        files = [f for f in files if "_input" not in f.name]
    else:
        files = [SCORED / f"cartography_rescore_b{i}.json" for i in range(1, num_batches + 1)]
        for f in files:
            if not f.exists():
                raise SystemExit(f"missing {f}")

    guests: list[dict] = []
    for path in files:
        guests.extend(json.loads(path.read_text(encoding="utf-8")).get("guests", []))

    leftover_path = SCORED / "cartography_leftover.json"
    if leftover_path.exists():
        leftover = json.loads(leftover_path.read_text(encoding="utf-8")).get("guests", [])
        guests.extend(leftover)

    seen: set[str] = set()
    deduped: list[dict] = []
    for g in guests:
        key = (g.get("raw_display") or g.get("name") or "").lower()
        if not key or key in seen:
            continue
        seen.add(key)
        if g.get("name", "").lower() == "jack rzucidlo":
            g.update(score=100, needs_verification=False, company="Burla.dev", role="Burla.dev founder")
        deduped.append(g)

    deduped.sort(key=lambda x: x.get("score", 0), reverse=True)
    payload = {**EVENT, "parsed_count": len(deduped), "guests": deduped}
    out = SCORED / "cartography_a16z.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    actionable = sum(1 for g in deduped if g.get("score", 0) >= 55)
    verified = sum(1 for g in deduped if not g.get("needs_verification"))
    print(f"Merged {len(deduped)} guests, score55+={actionable}, verified={verified}")
    print("Top 25:")
    for g in deduped[:25]:
        print(f"  {g.get('score', 0):3d}  {g.get('name', '')[:35]:<35}  {g.get('role', '')[:50]}")


if __name__ == "__main__":
    main()
