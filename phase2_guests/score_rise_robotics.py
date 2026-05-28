"""Score RISE Robotics guest list for Burla user-fit.

Question: would this person personally write remote_parallel_map-style Python
today on multi-GB/TB robotics, sensor, simulation, or vision workloads?

Reads phase2_guests/raw/rise_robotics_modal.json, writes
phase2_guests/scored/rise_robotics.json (initial heuristic pass).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).parent
MODAL = ROOT / "raw" / "rise_robotics_modal.json"
OUT = ROOT / "scored" / "rise_robotics.json"

EVENT = {
    "event_id": "rise_robotics",
    "event_name": "Robotics & Hard-Tech Demo Night at RISE Robotics",
    "event_partiful": "https://partiful.com/e/KP2y0vtxmdLA5FggQLlG",
    "event_host": "RISE Robotics",
    "event_date": "2026-05-28",
}


@dataclass
class Bucket:
    weight: int
    tag: str
    patterns: list[str]
    reason: str


POSITIVE: list[Bucket] = [
    Bucket(85, "robotics / perception / physical AI", [
        r"robotics", r"robot", r"slam", r"physical ai", r"embodied ai",
        r"autonomous", r"fleet", r"manipulation", r"locomotion", r"boston dynamics",
        r"spatial data layer", r"iot.*robot", r"technical product manager.*robot",
    ], "Hands-on robotics perception, fleet, or physical-AI compute."),
    Bucket(82, "simulation / digital twin / hard-tech R&D", [
        r"simulation", r"digital twin", r"computational", r"materials founder",
        r"energy/materials", r"aerospace", r"geospatial", r"earth observation",
        r"satellite", r"subsurface", r"hydrogeolog", r"geophys", r"climate-tech",
        r"hard-?tech", r"meddev", r"embedded firmware",
    ], "Simulation, materials, geospatial, or hard-tech R&D with heavy compute."),
    Bucket(78, "ML / CV / sensor data pipelines", [
        r"computer vision", r"machine learning", r"deep learning", r"ml research",
        r"data platform", r"data engineer", r"analytics engineer", r"flipside",
        r"libgem", r"building ai systems", r"ai-powered automation",
        r"engineering workflows", r"sensor", r"semiconductor and sensor",
    ], "ML/CV or data-pipeline builder on sensor or engineering data."),
    Bucket(72, "software engineer (generic tech)", [
        r"software engineer", r"swe", r"cto", r"founder.*ai", r"building at the intersection of hardware",
        r"connected products", r"firmware", r"embedded",
    ], "Software/firmware builder — plausible pipeline author if role is hands-on."),
    Bucket(55, "engineering-adjacent", [
        r"product manager.*physical", r"product manager.*iot", r"engineer",
        r"phd in robotics", r"aerospace engineer", r"mechanical engineer",
        r"computer engineering",
    ], "Engineering-adjacent — might run batch jobs but unconfirmed."),
]

NEGATIVE: list[Bucket] = [
    Bucket(-35, "investor / VC / finance", [
        r"investor", r"venture", r"capital", r"cfo at orbit", r"gp at", r"family office",
        r"goldman", r"bizdev", r"cro @", r"connecting founders to capital",
        r"investment manager", r"frontier tech investor", r"legal", r"attorney",
        r"advisor pllc", r"scout", r"mentor", r"accelerator program",
    ], "Investor/GTM/legal — not a pipeline author."),
    Bucket(-30, "marketing / growth / content", [
        r"marketing", r"growth orchestrator", r"content creator", r"photographer",
        r"public speaking", r"emcee", r"moderator", r"freelance software consultant & educator",
        r"community", r"innovation hub", r"ecosystem",
    ], "Marketing/content/community — not big-data compute."),
    Bucket(-28, "agent / LLM-app / chatbot", [
        r"ai copilot", r"ai-native asset management", r"agentic", r"llm-app",
        r"local-first ai servers", r"ai-powered growth", r"web3", r"crypto venture",
    ], "LLM-app/agent hype without large batch data."),
    Bucket(-22, "startup programs / BD", [
        r"solidworks for startups", r"3dexperience lab", r"business development",
        r"strategy and business development", r"early engagement",
    ], "Ecosystem/BD role, not hands-on pipeline builder."),
    Bucket(-15, "student / job seeker", [
        r"student@", r"seeking employment", r"grad student", r"intern @",
    ], "Student/intern — possible future user but not buyer today."),
]

JACK_NAMES = {"jack rzucidlo"}


def text_blob(g: dict) -> str:
    parts = [
        g.get("displayName", ""),
        g.get("imgAlt", ""),
        g.get("bio", ""),
        g.get("initials", ""),
    ]
    return " ".join(parts).lower()


def match_buckets(text: str, buckets: list[Bucket]) -> list[Bucket]:
    hits = []
    for b in buckets:
        for p in b.patterns:
            if re.search(p, text, re.I):
                hits.append(b)
                break
    return hits


def linkedin_from_bio(bio: str) -> str:
    m = re.search(r"https?://(?:www\.)?linkedin\.com/in/[^\s\"']+", bio, re.I)
    return m.group(0).rstrip("/") if m else ""


def company_role_from_bio(bio: str) -> tuple[str, str]:
    if not bio.strip():
        return "", ""
    # common patterns: "Role @ Company", "CEO/Founder, X", "Title at Y"
    at = re.search(r"([^|@\\n]{3,60})\s+@\s+([^|@\\n]{2,60})", bio)
    if at:
        return at.group(2).strip(), at.group(1).strip()
    founder = re.search(r"(?:ceo|cto|cofounder|co-founder|founder)[^|@\\n]{0,20}[,@]\\s*([^|@\\n]{2,80})", bio, re.I)
    if founder:
        return founder.group(1).strip(), "Founder"
    return "", bio.split("\n")[0][:80]


def score_guest(g: dict) -> dict:
    name = (g.get("displayName") or g.get("imgAlt") or g.get("initials") or "").strip()
    bio = (g.get("bio") or "").strip()
    text = text_blob(g)
    key = name.lower()

    if key in JACK_NAMES or (g.get("initials") == "JR" and "jack" in text):
        return {
            "name": "Jack Rzucidlo",
            "company": "Burla.dev",
            "role": "Burla.dev founder",
            "score": 100,
            "linkedin": "",
            "tags": ["Burla", "remote_parallel_map"],
            "evidence": "This is the analyst running the scoring.",
            "needs_verification": False,
            "raw_display": name or g.get("initials", ""),
        }

    pos = match_buckets(text, POSITIVE)
    neg = match_buckets(text, NEGATIVE)

    score = 40  # default for unknown
    tags: list[str] = []
    reasons: list[str] = []

    if pos:
        score = max(b.weight for b in pos)
        tags.extend(b.tag for b in pos[:3])
        reasons.append(pos[0].reason)
    if neg:
        score += sum(b.weight for b in neg)
        tags.extend(b.tag for b in neg[:2])
        reasons.append(f"Penalty: {neg[0].reason}")

    # Bio-rich guests get confidence boost when positive
    if bio and pos and not neg:
        score = min(95, score + 5)

    # Initials-only with no bio stays unverified
    initials_only = not (g.get("displayName") or g.get("imgAlt")) and bool(g.get("initials"))
    first_name_only = bool(name) and len(name.split()) == 1 and name[0].isupper() and len(name) < 12
    needs_verification = initials_only or (not bio and score >= 55) or (first_name_only and not bio)

    if initials_only and not bio:
        score = min(score, 42)
        needs_verification = True

    score = max(0, min(100, score))

    company, role = company_role_from_bio(bio)
    linkedin = linkedin_from_bio(bio)

    if not reasons:
        if bio:
            reasons.append(f"Partiful bio: {bio[:160]}{'…' if len(bio)>160 else ''}")
        else:
            reasons.append("No Partiful bio and no strong public signal in name alone — default robotics-event prior.")

    evidence = " ".join(reasons)
    if pos and neg:
        evidence += " Score reflects user-fit for remote_parallel_map, not networking value."

    return {
        "name": name or g.get("initials", "Unknown"),
        "company": company,
        "role": role,
        "score": score,
        "linkedin": linkedin,
        "tags": list(dict.fromkeys(tags))[:5] or (["unverified"] if needs_verification else ["robotics event"]),
        "evidence": evidence,
        "needs_verification": needs_verification,
        "raw_display": g.get("displayName") or g.get("imgAlt") or g.get("initials", ""),
    }


def main() -> None:
    data = json.loads(MODAL.read_text(encoding="utf-8"))
    guests = []
    seen: set[str] = set()
    for row in data["guests"]:
        key = (row.get("displayName") or row.get("imgAlt") or row.get("initials") or "").lower()
        if not key or key in seen:
            continue
        seen.add(key)
        guests.append(score_guest(row))

    guests.sort(key=lambda g: g["score"], reverse=True)
    payload = {
        **EVENT,
        "declared_count": data.get("declared_count", 344),
        "parsed_count": len(guests),
        "guests": guests,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    top = guests[:15]
    print(f"Wrote {OUT} ({len(guests)} guests)")
    print("Top 15:")
    for g in top:
        print(f"  {g['score']:3d}  {g['name']} — {g.get('role','')[:50]}")


if __name__ == "__main__":
    main()
