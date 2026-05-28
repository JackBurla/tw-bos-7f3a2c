"""Score AI/Bio Hackathon Awards guest list for Burla user-fit.

Question: would this person personally write remote_parallel_map-style Python
today on multi-GB/TB bio, drug-discovery, or ML-pipeline workloads?

Reads phase2_guests/raw/aibio_hackathon_modal.json, writes
phase2_guests/scored/aibio_hackathon.json (initial heuristic pass).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).parent
MODAL = ROOT / "raw" / "aibio_hackathon_modal.json"
OUT = ROOT / "scored" / "aibio_hackathon.json"

EVENT = {
    "event_id": "aibio_hackathon",
    "event_name": "AI/Bio Hackathon Awards and Lightning Pitches",
    "event_partiful": "https://partiful.com/e/XtABb8m1oJkDVZ81Ahxj",
    "event_host": "C10 Labs / Evolved Technology / Bayer Co.Lab / Nebius / LabCentral",
    "event_date": "2026-05-28",
}


@dataclass
class Bucket:
    weight: int
    tag: str
    patterns: list[str]
    reason: str


POSITIVE: list[Bucket] = [
    Bucket(92, "comp-bio / drug discovery / genomics", [
        r"alphafold", r"docking", r"molecular dynamics", r"\bmd simulation",
        r"target (id|discovery)", r"drug discov", r"protein design",
        r"single[- ]cell", r"\bgenom", r"proteom", r"crispr", r"rdkit",
        r"computational biolog", r"bioinformatic", r"cheminform",
        r"reflector bio", r"xsphera", r"phenotypic modeling",
        r"rare disease", r"auditable\.ai",
    ], "Hands-on comp-bio or drug-discovery pipeline author — direct Burla user."),
    Bucket(85, "ML for bio / foundation models / embeddings", [
        r"protein language model", r"\besm\b", r"diffusion model.*bio",
        r"ai.*drug", r"ai.*therap", r"ai.*scien", r"ai.*lab",
        r"ml engineer.*bio", r"foundation model", r"embeddings",
        r"batch (ml|llm) inference", r"libgem", r"max ai", r"reflect.*mental",
        r"otin\.ai", r"forty[- ]?guard",
    ], "ML/embeddings infra for bio or scientific data."),
    Bucket(80, "robotics / physical AI / sensors / AR-VR perception", [
        r"robotics", r"robot", r"slam", r"physical ai", r"embodied ai",
        r"autonomous", r"manipulation", r"flowsxr", r"ar/vr", r"papers in ar",
        r"happyverse", r"engram labs", r"self-adapti",
    ], "Sensor/perception/AR-VR researcher — likely big compute."),
    Bucket(75, "ML / CV / sensor data pipelines", [
        r"computer vision", r"machine learning", r"deep learning", r"ml research",
        r"data platform", r"data engineer", r"analytics engineer",
        r"building ai systems", r"ai-?powered automation",
        r"engineering workflows", r"semiconductor and sensor",
    ], "ML/CV or data-pipeline builder."),
    Bucket(68, "software / CTO / founder (technical)", [
        r"software engineer", r"\bswe\b", r"\bcto\b", r"founder.*ai",
        r"building at the intersection", r"connected products", r"firmware",
        r"embedded", r"cs new grad", r"berkeley computer science",
        r"uc berkeley computer", r"\bphd\b.*ai", r"\bphd\b.*ml",
        r"systems thinker", r"private ai",
    ], "Technical builder — plausible pipeline author if role is hands-on."),
    Bucket(58, "engineering-adjacent / product technical", [
        r"product manager.*ai", r"engineer", r"phd in robotics",
        r"aerospace engineer", r"mechanical engineer",
        r"computer engineering", r"r&d", r"commercialization",
    ], "Engineering-adjacent — might run batch jobs."),
]

NEGATIVE: list[Bucket] = [
    Bucket(-35, "investor / VC / finance / legal", [
        r"investor", r"venture", r"\bvc\b", r"capital", r"\bcfo\b",
        r"\bgp at", r"family office", r"goldman", r"bizdev", r"\bcro\b",
        r"connecting founders to capital", r"investment manager",
        r"frontier tech investor", r"legal", r"attorney",
        r"advisor pllc", r"scout", r"mentor",
        r"alumni ventures", r"cei ventures", r"managing director.*pnc",
        r"hedge fund", r"fund director",
    ], "Investor/GTM/legal — not a pipeline author."),
    Bucket(-30, "marketing / growth / content / community", [
        r"marketing", r"growth orchestrator", r"content creator",
        r"photographer", r"public speaking", r"emcee", r"moderator",
        r"community", r"innovation hub", r"ecosystem",
        r"\bbd\b at", r"business development", r"strategy and business",
    ], "Marketing/content/community — not big-data compute."),
    Bucket(-25, "agent / LLM-chatbot / web3", [
        r"ai copilot", r"agentic", r"llm-app", r"chatbot",
        r"ai-powered growth", r"web3", r"crypto venture",
        r"nft", r"ai agent that runs store",
    ], "LLM-app/agent hype without large batch data."),
    Bucket(-22, "clinician / MD without computation", [
        r"\bmd\b(?!.*(software|engineer|founder|cto|ai))",
        r"physician(?!.*ai)", r"clinical(?!.*(ai|ml|data))",
        r"medtech, team builder",
    ], "Clinician/medical without compute role."),
    Bucket(-15, "student / job seeker / no signal", [
        r"student@", r"seeking employment", r"grad student", r"intern @",
        r"\bnew grad\b",
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
    at = re.search(r"([^|@\n]{3,60})\s+@\s+([^|@\n]{2,60})", bio)
    if at:
        return at.group(2).strip(), at.group(1).strip()
    founder = re.search(r"(?:ceo|cto|cofounder|co-founder|founder)[^|@\n]{0,20}[,@]\s*([^|@\n]{2,80})", bio, re.I)
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
            "linkedin": "https://www.linkedin.com/in/jack-rzucidlo/",
            "tags": ["Burla", "remote_parallel_map"],
            "evidence": "This is the analyst running the scoring.",
            "needs_verification": False,
            "raw_display": name or g.get("initials", ""),
        }

    pos = match_buckets(text, POSITIVE)
    neg = match_buckets(text, NEGATIVE)

    score = 40
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

    if bio and pos and not neg:
        score = min(95, score + 5)

    initials_only = not (g.get("displayName") or g.get("imgAlt")) and bool(g.get("initials"))
    first_name_only = bool(name) and len(name.split()) == 1 and name[0].isupper() and len(name) < 12
    needs_verification = initials_only or (not bio and score >= 55) or (first_name_only and not bio)

    if (initials_only or first_name_only) and not bio:
        score = min(score, 42)
        needs_verification = True

    score = max(0, min(100, score))

    company, role = company_role_from_bio(bio)
    linkedin = linkedin_from_bio(bio)

    if not reasons:
        if bio:
            reasons.append(f"Partiful bio: {bio[:160]}{'…' if len(bio) > 160 else ''}")
        else:
            reasons.append("No Partiful bio — default unverified prior. Needs web/LinkedIn lookup.")

    evidence = " ".join(reasons)
    if pos and neg:
        evidence += " Score reflects user-fit for remote_parallel_map, not networking value."

    return {
        "name": name or g.get("initials", "Unknown"),
        "company": company,
        "role": role,
        "score": score,
        "linkedin": linkedin,
        "tags": list(dict.fromkeys(tags))[:5] or (["unverified"] if needs_verification else ["aibio event"]),
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
        "declared_count": data.get("declared_count", 100),
        "parsed_count": len(guests),
        "guests": guests,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT} ({len(guests)} guests)")
    print("Top 15:")
    for g in guests[:15]:
        print(f"  {g['score']:3d} {g['name']} — {(g.get('role') or '')[:50]}")


if __name__ == "__main__":
    main()
