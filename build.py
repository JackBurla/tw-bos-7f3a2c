"""
Build the static dashboard.

Reads `events_scored.json` + any `phase2_guests/scored/*.json` files, decorates
each matching event with a `guests_slug` so the dashboard can surface a "View
scored guests" link, then embeds the result into `index.template.html` and
writes `index.html`. The result is a fully static page that can be opened
directly from disk (no server required).
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
template = (ROOT / "index.template.html").read_text(encoding="utf-8")
events = json.loads((ROOT / "events_scored.json").read_text(encoding="utf-8"))


def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


scored_dir = ROOT / "phase2_guests" / "scored"
guest_index: dict[str, dict] = {}
if scored_dir.exists():
    for p in scored_dir.glob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not data.get("event_name"):
            continue
        guest_index[normalize(data["event_name"])] = {
            "slug": p.stem,
            "parsed": data.get("parsed_count", 0),
            "declared": data.get("declared_count", 0),
        }

matched = 0
for ev in events:
    key = normalize(ev.get("name", ""))
    if key in guest_index:
        info = guest_index[key]
        ev["guests_slug"] = info["slug"]
        ev["guests_parsed"] = info["parsed"]
        ev["guests_declared"] = info["declared"]
        matched += 1

embedded = json.dumps(events, ensure_ascii=False).replace("</", "<\\/")
html = template.replace("__EVENTS_JSON__", embedded)
(ROOT / "index.html").write_text(html, encoding="utf-8")
print(
    f"Built index.html with {len(events)} events embedded "
    f"({matched} with scored guest lists)."
)
