"""
Parse a saved Partiful event page and pull out the guest list.

Partiful renders each guest avatar as
    <img class="ptf-YHgvF ptf-Vy3V8" alt="<Name>" src="...">
plus a richer block in the rendered HTML for the host(s). We collect every
unique `alt` and write them to `phase2_guests/raw/<eventId>.guests.json`.
"""
import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
RAW = HERE / "raw"


def parse_html(html: str) -> dict:
    title_m = re.search(r"<title>([^<]+)</title>", html)
    title = title_m.group(1).strip() if title_m else "Partiful event"
    title = re.sub(r"\s*\|\s*Partiful\s*$", "", title)

    count_m = re.search(r"(\d+)\s*&nbsp;on&nbsp;the&nbsp;list", html)
    if not count_m:
        count_m = re.search(r"(\d+)\s+on\s+the\s+list", html)
    declared = int(count_m.group(1)) if count_m else None

    guest_re = re.compile(
        r'<img\s+class="ptf-YHgvF\s+ptf-Vy3V8"\s+alt="([^"]+)"',
        re.IGNORECASE,
    )
    names = guest_re.findall(html)

    seen: set[str] = set()
    guests: list[str] = []
    for raw_name in names:
        clean = re.sub(r"\s+", " ", raw_name).strip()
        if not clean:
            continue
        if clean in seen:
            continue
        seen.add(clean)
        guests.append(clean)

    return {
        "title": title,
        "declared_count": declared,
        "parsed_count": len(guests),
        "guests": guests,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("event_id", help="Filename stem under phase2_guests/raw, e.g. data_swamp")
    args = parser.parse_args()

    src = RAW / f"{args.event_id}.html"
    if not src.exists():
        print(f"Not found: {src}", file=sys.stderr)
        return 1

    html = src.read_text(encoding="utf-8", errors="ignore")
    result = parse_html(html)

    out = RAW / f"{args.event_id}.guests.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Title: {result['title']}")
    print(f"Declared on Partiful: {result['declared_count']}")
    print(f"Parsed: {result['parsed_count']}")
    print(f"Wrote: {out}")
    print()
    print("First 15 guests:")
    for g in result["guests"][:15]:
        print(f"  - {g}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
