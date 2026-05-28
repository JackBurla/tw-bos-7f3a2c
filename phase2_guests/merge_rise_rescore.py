"""Merge rise_rescore_b1..b4 into rise_robotics.json."""
from __future__ import annotations

import json
from pathlib import Path

SCORED = Path(__file__).parent / "scored"
EVENT = {
    "event_id": "rise_robotics",
    "event_name": "Robotics & Hard-Tech Demo Night at RISE Robotics",
    "event_partiful": "https://partiful.com/e/KP2y0vtxmdLA5FggQLlG",
    "event_host": "RISE Robotics",
    "event_date": "2026-05-28",
    "declared_count": 344,
}


def main() -> None:
    guests: list[dict] = []
    for i in range(1, 5):
        path = SCORED / f"rise_rescore_b{i}.json"
        if not path.exists():
            raise SystemExit(f"missing {path}")
        guests.extend(json.loads(path.read_text(encoding="utf-8")).get("guests", []))

    seen: set[str] = set()
    deduped: list[dict] = []
    for g in guests:
        key = (g.get("raw_display") or g.get("name") or "").lower()
        if not key or key in seen:
            continue
        seen.add(key)
        if g.get("name", "").lower() == "jack rzucidlo":
            g.update(score=100, needs_verification=False)
        deduped.append(g)

    deduped.sort(key=lambda x: x.get("score", 0), reverse=True)
    payload = {**EVENT, "parsed_count": len(deduped), "guests": deduped}
    out = SCORED / "rise_robotics.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    actionable = sum(1 for g in deduped if g.get("score", 0) >= 55)
    verified = sum(1 for g in deduped if not g.get("needs_verification"))
    print(f"Merged {len(deduped)} guests, score55+={actionable}, verified={verified}")


if __name__ == "__main__":
    main()
