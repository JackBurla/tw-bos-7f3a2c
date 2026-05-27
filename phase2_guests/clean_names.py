"""Normalize the parsed guests for enrichment.

Splits any inline company / URL / role hint out of the display name (some
Partiful users embed company info in their display name, e.g.
"David building gethouston.ai"). Fixes ALL-CAPS / lower-case names. Drops the
known non-guest tiles ("Tech Week", "Partiful logo", thumbnail ids).
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
RAW = ROOT / "raw"


def clean_name(raw: str) -> dict:
    """Return {name, hint, raw}."""
    name = raw
    hint = ""

    # Pull any URL out of the display
    url_m = re.search(r"https?://\S+|www\.\S+|[a-z0-9-]+\.(?:ai|com|dev|io|co|xyz)", name, re.IGNORECASE)
    if url_m:
        hint = url_m.group(0)
        name = name.replace(hint, "")

    # Strip emojis and common decorations
    name = re.sub(r"[\U0001F300-\U0001FAFF\U00002600-\U000027BF\u2728\u26A1]", "", name)
    name = re.sub(r"\s+(building|at|@|w/|with|founder|ceo|cto|of)\b.*", "", name, flags=re.IGNORECASE)

    # Collapse whitespace
    name = re.sub(r"\s+", " ", name).strip(" -|,")

    # Fix all-caps and all-lower first names (keep mixed case alone)
    parts = name.split(" ")
    fixed = []
    for p in parts:
        if not p:
            continue
        if p.isupper() or p.islower():
            fixed.append(p[0].upper() + p[1:].lower() if len(p) > 1 else p.upper())
        else:
            fixed.append(p)
    name = " ".join(fixed)

    return {"name": name, "hint": hint.strip(), "raw": raw}


def main() -> None:
    src = RAW / "data_swamp.guests.json"
    data = json.loads(src.read_text(encoding="utf-8"))

    drop_alts = {
        "Partiful logo",
        "Tech Week",
        "Theme background",
        "video-thumbnail",
        "photo-album-image",
    }

    cleaned: list[dict] = []
    seen_names: set[str] = set()
    for raw in data["guests"]:
        if raw in drop_alts:
            continue
        if re.fullmatch(r"[A-Za-z0-9_-]{10,30}", raw):
            continue  # thumbnail id
        rec = clean_name(raw)
        key = rec["name"].lower().strip()
        if not key or key in seen_names:
            continue
        seen_names.add(key)
        cleaned.append(rec)

    out = ROOT / "raw" / "data_swamp.cleaned.json"
    out.write_text(
        json.dumps(
            {
                "title": data["title"],
                "declared_count": data["declared_count"],
                "parsed_count": len(cleaned),
                "guests": cleaned,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"Cleaned guests: {len(cleaned)} -> {out}")
    for g in cleaned:
        suffix = f"  [{g['hint']}]" if g["hint"] else ""
        print(f"  - {g['name']}{suffix}")


if __name__ == "__main__":
    main()
