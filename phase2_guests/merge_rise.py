"""Merge rise_robotics_b1..b4.json into rise_robotics.json."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parent
SCORED = ROOT / "scored"

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
        path = SCORED / f"rise_robotics_b{i}.json"
        if not path.exists():
            # fall back to heuristic monolith
            mono = SCORED / "rise_robotics.json"
            if mono.exists() and i == 1:
                print(f"Batch files missing; keeping {mono}")
                return
            raise SystemExit(f"missing {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        guests.extend(data.get("guests", data if isinstance(data, list) else []))

    seen: set[str] = set()
    deduped: list[dict] = []
    for g in guests:
        key = (g.get("raw_display") or g.get("name") or "").lower()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(g)

    deduped.sort(key=lambda g: g.get("score", 0), reverse=True)
    payload = {**EVENT, "parsed_count": len(deduped), "guests": deduped}
    out = SCORED / "rise_robotics.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Merged {len(deduped)} guests -> {out}")
    print("Top 10:")
    for g in deduped[:10]:
        print(f"  {g['score']:3d}  {g['name']}")


if __name__ == "__main__":
    main()
