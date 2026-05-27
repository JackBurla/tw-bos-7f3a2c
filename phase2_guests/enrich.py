"""
Phase 2 entry point - turn a raw Partiful guest-list capture into a scored
people JSON that the dashboard can render.

Right now this is a STUB. Once you have approved RSVPs we'll:
  1. Parse names + handles out of the saved Partiful HTML (or pasted text)
  2. Use LinkedIn / web search to enrich each name with company + role
  3. Score each guest 0-100 with the same big-data heuristic as the HCLS
     dashboard (computational biology, ML infra, data pipelines, etc.)
  4. Write `phase2_guests/scored/<eventId>.json`

Usage (once implemented):
    python phase2_guests/enrich.py <eventId>
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
RAW = HERE / "raw"
SCORED = HERE / "scored"
SCORED.mkdir(exist_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("event_id", help="Tech-Week internal id, e.g. 4760")
    args = parser.parse_args()

    raw_html = RAW / f"{args.event_id}.html"
    raw_txt = RAW / f"{args.event_id}.txt"
    if not raw_html.exists() and not raw_txt.exists():
        print(f"No raw capture found at {raw_html} or {raw_txt}.", file=sys.stderr)
        print("Save the Partiful page (Ctrl+S) or paste guest names into a .txt and try again.", file=sys.stderr)
        return 1

    print("Phase 2 enrichment is not yet implemented.", file=sys.stderr)
    print("This stub exists so the wiring is ready the moment you give the go-ahead.", file=sys.stderr)

    placeholder = {
        "event_id": args.event_id,
        "guests": [],
        "note": "Stub - enrichment + scoring not yet wired up.",
    }
    out = SCORED / f"{args.event_id}.json"
    out.write_text(json.dumps(placeholder, indent=2), encoding="utf-8")
    print(f"Wrote placeholder {out}.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
