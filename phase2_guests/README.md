# Phase 2 - Per-Event Guest Scoring

Once Partiful hosts approve our RSVPs and the guest list becomes visible,
this folder is where the per-event guest scoring lives.

## Flow

1. **Capture** - Open a Partiful event in your logged-in browser, scroll the
   guest list, then save the page (Ctrl+S) into `phase2_guests/raw/`
   as `<eventId>.html`. Or paste the visible names into
   `phase2_guests/raw/<eventId>.txt` (one guest per line).

2. **Enrich** - Run `python phase2_guests/enrich.py <eventId>`. The script
   reads the raw capture, extracts guest names, attempts public LinkedIn
   lookups (placeholder for now), and writes
   `phase2_guests/scored/<eventId>.json` with the same shape as the
   `hcls-large-data-dashboard` people list (name, company, role, score,
   linkedin, tags, evidence).

3. **Render** - The main dashboard auto-detects any
   `phase2_guests/scored/<eventId>.json` file and exposes a "View scored
   guests" button on the matching event card.

## Today

This folder is wiring only. Once you have approved RSVPs, ping me and I'll
flesh out `enrich.py` plus the dashboard hookup.
