"""Score Platform-to-Pipeline (Cartography x a16z) guest list for Burla user-fit.

Question: would this person personally write remote_parallel_map-style Python
today on multi-GB/TB clinical genomics, drug-discovery, target-ID, omics, or
ML-inference workloads?

Reads phase2_guests/raw/cartography_a16z_modal.json, writes
phase2_guests/scored/cartography_a16z.json (initial heuristic pass).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).parent
MODAL = ROOT / "raw" / "cartography_a16z_modal.json"
OUT = ROOT / "scored" / "cartography_a16z.json"

EVENT = {
    "event_id": "cartography_a16z",
    "event_name": "Platform to Pipeline: Fireside Chat with a16z and the CEO of Cartography",
    "event_partiful": "https://partiful.com/e/vQDvxdHU5dZgwJAFBzmZ",
    "event_host": "Cartography / a16z bio / Fenwick",
    "event_date": "2026-05-29",
}


@dataclass
class Bucket:
    weight: int
    tag: str
    patterns: list[str]
    reason: str


POSITIVE: list[Bucket] = [
    Bucket(95, "clinical genomics / target ID / drug discovery pipeline", [
        r"target (id|discovery)", r"drug discov", r"alphafold", r"protein design",
        r"docking", r"molecular dynamics", r"\bmd simulation",
        r"clinical genomic", r"single[- ]cell", r"\bgenom", r"proteom", r"transcript",
        r"crispr", r"rdkit", r"cheminform", r"computational biol",
        r"reflector bio", r"xsphera", r"phenotypic modeling", r"biosens8",
        r"biosequence", r"cartography",
    ], "Clinical-genomics / drug-discovery pipeline author — direct Burla user."),
    Bucket(88, "biotech founder / CSO / scientific platform", [
        r"founder.*bio", r"\bbiotech\b", r"\bbiosci", r"\bgen7\b",
        r"\bcso\b", r"\botin\.ai", r"founder.*therap",
        r"hey ara", r"engram labs", r"libgem", r"forty[- ]?guard",
        r"\bml engineer.*bio", r"foundation model.*bio",
        r"embeddings", r"phd.*bio", r"phd.*chem",
        r"protein language model", r"\besm\b",
    ], "Bio founder / CSO / scientific-platform leader — likely Python on biological data."),
    Bucket(82, "AI/ML for science / batch ML inference / data engineer", [
        r"ai.*drug", r"ai.*therap", r"ai.*scien", r"ai.*lab",
        r"ai.*research", r"ai.*talent", r"ai.*platform", r"ai.*pipeline",
        r"machine learning", r"\bml\b.*infra", r"deep learning",
        r"data engineer", r"data platform", r"data scien",
        r"foundation model", r"batch (ml|llm) inference",
        r"phd.*ml", r"phd.*\bai\b", r"\bphd\b.*cs", r"\bphd in ai",
        r"30 years at the forefront of ai research",
        r"phenotypic modeling", r"cs phd",
    ], "ML/CV/data-platform engineer — plausible heavy compute."),
    Bucket(72, "robotics / hardware / sensors / physical AI", [
        r"robotics", r"robot", r"sensor", r"physical ai", r"embodied ai",
        r"autonomous", r"flowsxr", r"ar/vr", r"slam", r"systems thinker",
        r"connected products", r"firmware", r"embedded",
    ], "Sensor/hardware builder — potential heavy compute."),
    Bucket(66, "technical founder / CTO / SWE (general)", [
        r"\bcto\b", r"co-?founder.*ai", r"founder.*ai", r"co-?founder.*tech",
        r"software engineer", r"\bswe\b", r"engineer.*ai", r"phd.*cs",
        r"building ai", r"building at the intersection",
        r"\bmit\b.*cs", r"cs new grad", r"cs/history", r"berkeley computer science",
        r"happyverse", r"max ai", r"reflect.*mental",
    ], "Technical builder — needs verification but plausible."),
    Bucket(58, "domain-adjacent (pharma R&D, biomarker)", [
        r"biomarker", r"r&d", r"commercialization", r"translational",
        r"medtech, team builder", r"strategy.*veeva", r"veeva publications",
        r"\bphd\b.*chem", r"\bphd\b.*biol",
    ], "Pharma R&D / biomarker scientist — may run batch analysis."),
]

NEGATIVE: list[Bucket] = [
    Bucket(-32, "investor / VC / a16z / fund / finance", [
        r"investor", r"venture", r"\bvc\b", r"capital", r"\bcfo\b",
        r"\bgp at", r"family office", r"goldman", r"bizdev",
        r"connecting founders to capital", r"investment manager",
        r"frontier tech investor", r"a16z", r"andreessen",
        r"\bbd\b at", r"business development", r"managing director",
        r"intersystems ventures", r"maxitech ventures", r"rdf ventures",
        r"alumni ventures", r"investor at", r"hedge fund",
        r"polaris", r"acquired by yelp",
    ], "Investor / VC / fund — networking value, not pipeline author."),
    Bucket(-30, "legal / law firm / policy / fenwick", [
        r"fenwick", r"attorney", r"\blegal\b", r"law firm",
        r"\blaw\b.*colombia", r"trust and accountability", r"policy",
    ], "Legal/policy — not a Python pipeline author."),
    Bucket(-28, "marketing / content / community / photographer", [
        r"marketing", r"growth orchestrator", r"content creator",
        r"photographer", r"public speaking", r"emcee",
        r"community", r"innovation hub", r"ecosystem", r"creative director",
    ], "Marketing/content — not big-data compute."),
    Bucket(-25, "agent / LLM-chatbot / no-data-AI", [
        r"ai copilot", r"agentic", r"llm-app", r"chatbot",
        r"ai-powered growth", r"ai agent that runs store", r"web3",
        r"crypto venture",
    ], "LLM-chatbot/agent app without big-data pipelines."),
    Bucket(-25, "clinician-only / MD without computation", [
        r"\bmd\b(?!.*(software|engineer|founder|cto|ai|ml|data))",
        r"physician(?!.*(ai|ml|data))",
        r"clinical(?!.*(ai|ml|data|software|platform))",
    ], "Clinician without compute role."),
    Bucket(-22, "professional athlete / non-tech notable", [
        r"cornerback", r"new england patriots", r"\bnfl\b",
    ], "Public figure / athlete — not a pipeline author."),
    Bucket(-15, "student / job seeker", [
        r"student@", r"seeking employment", r"grad student", r"intern @",
        r"\bnew grad\b",
    ], "Student/early-career — future user but not buyer."),
]


JACK_NAMES = {"jack rzucidlo"}

# Notable speakers / hosts to elevate (they're not Burla users, but are important context)
SPEAKERS = {
    "kevin parker": ("Cartography Biosciences", "CEO (event speaker)"),
    "heidi erlacher": ("Fenwick", "Partner — event moderator"),
}


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

    if key in SPEAKERS:
        company, role = SPEAKERS[key]
        return {
            "name": name,
            "company": company,
            "role": role,
            "score": 55,
            "linkedin": "",
            "tags": ["event speaker", "moderator/CEO"],
            "evidence": f"Confirmed event role: {role}. Not a typical Burla user but high-leverage relationship.",
            "needs_verification": False,
            "raw_display": name,
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
        "tags": list(dict.fromkeys(tags))[:5] or (["unverified"] if needs_verification else ["cartography event"]),
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
        "declared_count": data.get("declared_count", 379),
        "parsed_count": len(guests),
        "guests": guests,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT} ({len(guests)} guests)")
    print("Top 15:")
    for g in guests[:15]:
        print(f"  {g['score']:3d} {g['name'][:30]:<30} {(g.get('role') or '')[:50]}")


if __name__ == "__main__":
    main()
