# Burla x a16z Tech Week Boston dashboard

Score every a16z Tech Week Boston event for fit with Burla.dev's ICP
(Python-at-scale teams: ML/AI engineers, embeddings/inference/ETL pipelines,
genomics + multi-omics + scientific compute), apply to the strongest ones,
then score the people who actually show up.

## What's here

```
events_raw.json        334 events scraped from tech-week.com/calendar/boston
events_scored.json     same events with score, tier, tags, evidence
extract_events.py      RSC-payload parser (re-run if site updates)
score_events.py        keyword-driven Burla-ICP scoring (transparent, audit-friendly)
build.py               injects events_scored.json into index.html
index.template.html    static template
index.html             the dashboard (open this in any browser)
styles.css             dashboard styles, matched to the HCLS large-data layout
app.js                 render + filter + decision persistence
phase2_guests/         scaffolding for per-event guest scoring (see below)
```

## Burla.dev one-paragraph ICP

Burla scales Python to 1,000+ VMs in <1 second via `remote_parallel_map`,
with adaptive hardware per call, custom containers, and cloud-storage mounts.
Sweet-spot users are ML/data engineers who today hand-roll batch jobs
(embeddings, inference, simulation, ETL, scientific compute) and are getting
hurt by YAML, container rebuilds, and poor utilization. Heavy concentration
in genomics, single-cell / multi-omics, drug discovery, vision / imaging,
RAG / embedding pipelines, and any "embarrassingly parallel" workload.

## Phase 1 - events dashboard (done)

1. Pulled all events via `extract_events.py` (Next.js RSC payload parser).
2. Scored each one 0-100 with `score_events.py`, asking ONE question:
   "Will people who actually work with big datasets be in this room?"
   - **Top Burla Target** (80-100): bio / multi-omics, healthcare/clinical, real
     data-infra hosts (Modal, CoreWeave, Baseten, Snowflake, Elastic, Datadog),
     scientific compute, federal-funded health/biotech.
   - **Strong Fit** (60-79): healthcare hackathons, healthtech, life sciences
     showcases, vLLM / inference deep-dives, Cartography-style data graphs.
   - **Worth Trying** (40-59): defense / aerospace / robotics / quantum /
     materials / hard tech - heavy sensor or simulation data.
   - **Soft / Adjacent** (20-39): one weak signal, mostly low-fit context.
   - **Off-Topic** (0-19): generic AI-agent / LLM-app / marketing / sales /
     career / VC-LP / social events - very low chance of Burla audience.
3. Generic AI-agent / LLM-app builder framings are penalised (-30) unless a
   strong-positive bucket (bio / healthcare / data-infra / scientific compute)
   fires alongside, in which case 70% of the agent penalty is forgiven. The
   VC / LP penalty is *never* forgiven - investor breakfasts are still buyer
   rooms, not builder rooms.
3. Run `python build.py` to embed scored events into `index.html`.
4. Open `index.html` and click "Apply on Partiful" on every Interested event.
   Your Interested / Maybe / Not decisions persist in browser localStorage.

To re-pull and re-score after the calendar updates:

```bash
python extract_events.py   # only if you re-download raw_*.html pages
python score_events.py
python build.py
```

## Phase 2 - per-event guest scoring (wired, not yet active)

Partiful guest lists are only viewable after host approval (and phone-verified
login). Once you've RSVP'd and been approved:

1. Open the Partiful event in your logged-in browser, save it into
   `phase2_guests/raw/<eventId>.html` (or paste names into a `.txt`).
2. Run `python phase2_guests/enrich.py <eventId>` to extract names, enrich
   with LinkedIn signal, and score each guest with the same scheme as the
   HCLS large-data dashboard.
3. The main dashboard will auto-detect the resulting JSON and add a
   "View scored guests" button to the matching event card.

The enrichment + scoring script is a stub today - it'll be fleshed out the
moment you have any approved guest list ready to feed in.
