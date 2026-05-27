"""Render phase2_guests/scored/<slug>.json into phase2_guests/<slug>.html.

Usage: python phase2_guests/build_guest_page.py [slug ...]
If no slugs are given, builds every scored JSON found.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SCORED = ROOT / "scored"
TEMPLATE = ROOT / "guest_template.html"


def build(slug: str) -> Path:
    src = SCORED / f"{slug}.json"
    if not src.exists():
        raise SystemExit(f"missing scored file: {src}")
    payload = json.loads(src.read_text(encoding="utf-8"))

    payload["guests"].sort(key=lambda g: g.get("score", 0), reverse=True)

    template = TEMPLATE.read_text(encoding="utf-8")
    rendered = (
        template
        .replace("__EVENT_NAME__", payload["event_name"])
        .replace("__EVENT_HOST__", payload.get("event_host", ""))
        .replace("__EVENT_DATE__", payload.get("event_date", ""))
        .replace("__EVENT_PARTIFUL__", payload.get("event_partiful", "#"))
        .replace("__PARSED_COUNT__", str(payload.get("parsed_count", len(payload["guests"]))))
        .replace("__DECLARED_COUNT__", str(payload.get("declared_count", "?")))
        .replace("__GUESTS_JSON__", json.dumps(payload))
    )

    out = ROOT / f"guests-{slug}.html"
    out.write_text(rendered, encoding="utf-8")
    print(f"Wrote {out} ({len(payload['guests'])} guests)")
    return out


def main() -> None:
    slugs = sys.argv[1:]
    if not slugs:
        slugs = [p.stem for p in SCORED.glob("*.json")]
        if not slugs:
            raise SystemExit("no scored guest files found yet")
    for slug in slugs:
        build(slug)


if __name__ == "__main__":
    main()
