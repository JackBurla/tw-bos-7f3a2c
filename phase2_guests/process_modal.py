"""Capture full Partiful guest modal via browser CDP.

Run from a context where cursor-ide-browser MCP can execute JS on the
logged-in Partiful tab. This file documents the extraction logic used
during automation; the actual capture is done interactively.

Output shape matches data_swamp_modal.json:
  { declared_count, captured_count, guests: [{displayName, imgAlt, initials, bio, hasPhoto}] }
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
RAW = ROOT / "raw"

DROP_ALTS = {
    "Partiful logo",
    "Tech Week",
    "Theme background",
    "video-thumbnail",
    "photo-album-image",
}


def linkedin_from_bio(bio: str) -> str:
    m = re.search(r"https?://(?:www\.)?linkedin\.com/in/[^\s\"']+", bio, re.I)
    return m.group(0).rstrip("/") if m else ""


def clean_guest(row: dict) -> dict:
    display = (row.get("displayName") or row.get("imgAlt") or row.get("initials") or "").strip()
    bio = (row.get("bio") or "").strip()
    hint = ""
    url_m = re.search(r"https?://\S+|www\.\S+|[a-z0-9-]+\.(?:ai|com|dev|io|co|xyz)", display + " " + bio, re.I)
    if url_m:
        hint = url_m.group(0)
    return {
        "name": display or row.get("initials", ""),
        "displayName": display,
        "bio": bio,
        "linkedin_hint": linkedin_from_bio(bio),
        "hint": hint,
        "hasPhoto": bool(row.get("hasPhoto")),
        "initials_only": not display and bool(row.get("initials")),
    }


def load_modal(slug: str) -> dict:
    path = RAW / f"{slug}_modal.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    cleaned = []
    seen: set[str] = set()
    for row in data.get("guests", []):
        g = clean_guest(row)
        key = g["name"].lower()
        if not key or key in DROP_ALTS or key in seen:
            continue
        if re.fullmatch(r"[A-Za-z0-9_-]{10,30}", g["name"]):
            continue
        seen.add(key)
        cleaned.append(g)
    return {
        "slug": slug,
        "declared_count": data.get("declared_count"),
        "parsed_count": len(cleaned),
        "guests": cleaned,
    }


def main() -> None:
    import sys

    slug = sys.argv[1] if len(sys.argv) > 1 else "rise_robotics"
    out = load_modal(slug)
    dest = RAW / f"{slug}.cleaned.json"
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Cleaned {out['parsed_count']} guests -> {dest}")


if __name__ == "__main__":
    main()
