"""Merge rise_enrich_b1..b4 into rise_robotics.json with quality gates."""
from __future__ import annotations

import json
import re
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


def quality_gate(g: dict) -> dict:
    """Tighten verification flags — don't mark verified without evidence."""
    linkedin = (g.get("linkedin") or "").strip()
    company = (g.get("company") or "").strip()
    bio_evidence = len((g.get("evidence") or "")) > 80
    score = g.get("score", 40)
    name = g.get("name") or ""
    full_name = len(name.split()) >= 2

    if g.get("name", "").lower() == "jack rzucidlo":
        g["needs_verification"] = False
        g["score"] = 100
        return g

    has_id = bool(linkedin) or (bool(company) and company.lower() not in {"", "unknown", "company unknown"})
    ambiguous = "ambiguous" in (g.get("evidence") or "").lower() or "likely match" in (g.get("evidence") or "").lower()
    generic = "searched, no match" in (g.get("evidence") or "").lower() or "no public profile" in (g.get("evidence") or "").lower()

    if ambiguous or generic or (score <= 45 and not has_id):
        g["needs_verification"] = True
    elif has_id and bio_evidence:
        g["needs_verification"] = False
    elif has_id and full_name and score >= 50:
        g["needs_verification"] = False
    else:
        g["needs_verification"] = True

    return g


def main() -> None:
    guests: list[dict] = []
    for i in range(1, 5):
        path = SCORED / f"rise_enrich_b{i}.json"
        if not path.exists():
            raise SystemExit(f"waiting on {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        guests.extend(data.get("guests", []))

    seen: set[str] = set()
    deduped: list[dict] = []
    for g in guests:
        key = (g.get("raw_display") or g.get("name") or "").lower()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(quality_gate(g))

    deduped.sort(key=lambda x: x.get("score", 0), reverse=True)
    payload = {**EVENT, "parsed_count": len(deduped), "guests": deduped}
    out = SCORED / "rise_robotics.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    verified = sum(1 for g in deduped if not g.get("needs_verification"))
    linkedin = sum(1 for g in deduped if g.get("linkedin"))
    actionable = sum(1 for g in deduped if g.get("score", 0) >= 55)
    print(f"Merged {len(deduped)} -> {out}")
    print(f"verified={verified} linkedin={linkedin} score55+={actionable}")


if __name__ == "__main__":
    main()
