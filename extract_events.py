"""
Extract events from all per-day raw_YYYY-MM-DD.html dumps of the Boston
Tech-Week calendar. Each page is server-rendered with a Next.js RSC payload
that embeds the structured event objects.
"""
import codecs
import glob
import json
import os
import re
import sys

EVENT_KEYS_PATTERN = re.compile(
    r'\{"id":\d+,"city":"[^"]+","date":"\d{4}-\d{2}-\d{2}","time":"\d{2}:\d{2}:\d{2}"'
)
PUSH_PATTERN = re.compile(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', re.DOTALL)


def scan_balanced(text: str, start: int) -> int:
    depth = 0
    i = start
    in_str = False
    escape = False
    while i < len(text):
        ch = text[i]
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return i + 1
        i += 1
    raise ValueError("Unbalanced braces")


def parse_html(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    joined = "".join(
        codecs.decode(m, "unicode_escape") for m in PUSH_PATTERN.findall(html)
    )
    events: list[dict] = []
    for m in EVENT_KEYS_PATTERN.finditer(joined):
        s = m.start()
        try:
            end = scan_balanced(joined, s)
            obj = json.loads(joined[s:end])
        except (ValueError, json.JSONDecodeError):
            continue
        if obj.get("city") != "Boston":
            continue
        events.append(obj)
    return events


all_events: dict[int, dict] = {}
for path in sorted(glob.glob("raw_*.html")):
    parsed = parse_html(path)
    print(f"{path}: {len(parsed)} events", file=sys.stderr)
    for ev in parsed:
        eid = ev.get("id")
        if eid in all_events:
            continue
        all_events[eid] = ev

print(f"Total unique events: {len(all_events)}", file=sys.stderr)


def slim(ev: dict) -> dict:
    facets = ev.get("facets", {}) or {}
    hosts = [h.get("label") for h in facets.get("hosts", []) or [] if h.get("label")]
    locations = [l.get("label") for l in facets.get("locations", []) or [] if l.get("label")]
    return {
        "id": ev.get("id"),
        "date": ev.get("date"),
        "time": ev.get("time"),
        "name": ev.get("name"),
        "company": ev.get("company"),
        "hosts": hosts,
        "location": ev.get("location"),
        "neighborhoods": locations,
        "partiful": ev.get("externalHref"),
        "isInviteOnly": bool(ev.get("isInviteOnly", False)),
        "sponsorTier": ev.get("sponsorTier") if ev.get("sponsorTier") != "$undefined" else None,
        "timeOfDay": (facets.get("time") or {}).get("label"),
    }


slim_events = [slim(e) for e in all_events.values()]
slim_events.sort(key=lambda e: (e["date"] or "", e["time"] or "", e["name"] or ""))

with open("events_raw.json", "w", encoding="utf-8") as f:
    json.dump(slim_events, f, indent=2, ensure_ascii=False)

by_day: dict[str, int] = {}
for ev in slim_events:
    by_day.setdefault(ev["date"], 0)
    by_day[ev["date"]] += 1
for day in sorted(by_day):
    print(f"  {day}: {by_day[day]}", file=sys.stderr)
print(f"Wrote events_raw.json", file=sys.stderr)
