"""
Score every Tech-Week Boston event by ONE question:

    "Will people working with actual big datasets be in this room?"

Burla is a self-hostable Python compute platform. Its real users are teams who
already have many TB of data and a Python pipeline that fans out across
hundreds or thousands of machines: genomics + multi-omics, drug discovery
screens, medical / brain / spatial imaging, batch inference, embeddings at
corpus scale, scientific simulations, materials / molecular discovery, climate
+ geospatial, aerospace / defense sensor data, robotics fleet data, large
ETL / data engineering, vector / retrieval infrastructure.

Almost no `AI agent` / `LLM app` / `voice AI` / `vibe coding` builder runs into
this pain - their per-call data is tiny. So those events are penalised heavily,
even when they look "AI-flavoured".

The score is a transparent sum of bucket weights, capped at 100. Each bucket
specifies a tag, an evidence reason, and a list of regex patterns (compiled
with case-insensitive, word-boundary matching against `title | hosts`).
"""
import json
import re
from dataclasses import dataclass, field

with open("events_raw.json", "r", encoding="utf-8") as f:
    EVENTS = json.load(f)


@dataclass
class Bucket:
    weight: int
    tag: str
    reason: str
    patterns: list[str] = field(default_factory=list)


def regex_alt(patterns: list[str]) -> re.Pattern:
    expanded = []
    for p in patterns:
        if p.startswith("^"):
            expanded.append(p)
        else:
            expanded.append(r"\b" + p + r"\b")
    return re.compile("|".join(expanded), re.IGNORECASE)


# ----------------------------------------------------------------------------
# POSITIVE buckets - the rooms most likely to contain people who actually own
# a big-data Python pipeline today.
# ----------------------------------------------------------------------------
POSITIVE_BUCKETS: list[Bucket] = [
    Bucket(
        weight=80,
        tag="bio / multi-omics",
        reason="bio / genomics / multi-omics / drug discovery — the canonical big-data Python audience",
        patterns=[
            r"biotech",
            r"bio[\s\-+x/]*health",
            r"bio[\s\-+x/]*hack",
            r"ai\s*[x×]\s*bio",
            r"aix?bio",
            r"life\s+sciences?",
            r"drug\s+discover",
            r"models?\s+to\s+medicines?",
            r"pharma",
            r"genomic",
            r"single[\s\-]?cell",
            r"multi[\s\-]?omic",
            r"omics",
            r"proteomic",
            r"transcriptomic",
            r"metabolomic",
            r"spatial",
            r"sequencing",
            r"bioinformatic",
            r"computational\s+biolog",
            r"virtual\s+cell",
            r"crispr",
            r"perturb",
            r"protein\s+design",
            r"in[\s\-]?silico",
            r"organ\s+engineer",
            r"biofabrication",
            r"longevity",
            r"aging\s+code",
            r"biopharma",
            r"medtech",
            r"women\s+in\s+biotech",
            r"flagship\s+pioneering",
            r"ginkgo",
            r"concerto\s+bio",
            r"absentia",
            r"bayer",
            r"eli\s+lilly",
            r"massbio",
            r"a16z\s+bio",
            r"biolabs",
            r"labcentral",
            r"nucleate",
            r"formation\s+bio",
            r"converge\s+bio",
            r"scientific\s+discover",
            r"automata",
            r"ai\s*-?\s*native\s+labs?",
        ],
    ),
    Bucket(
        weight=62,
        tag="healthcare / clinical AI",
        reason="clinical / EHR / medical imaging / hospital data — real biomedical data at scale",
        patterns=[
            r"healthcare",
            r"health\s+systems?",
            r"clinical",
            r"clinic",
            r"hospital",
            r"computing\s+in\s+the\s+clinic",
            r"ehr",
            r"electronic\s+health\s+record",
            r"medical\s+imaging",
            r"brain\s+(health|recover|imaging|mri)",
            r"radiolog",
            r"patholog",
            r"oncolog",
            r"trials?\s+in\s+motion",
            r"clinical\s+trials?",
            r"medical\s+ai",
            r"athenahealth",
            r"dana[\s\-]?farber",
            r"dfci",
            r"hcc\s+cure",
            r"mgh\s+biobank",
            r"biobank",
            r"healthtech",
            r"digital\s+twin",
            r"longevitytech",
            r"computing\s+in\s+the\s+clinic",
            r"women['']?s\s+health",
            r"phasev",
        ],
    ),
    Bucket(
        weight=55,
        tag="scientific compute",
        reason="scientific simulation / materials / quantum / molecular data — heavy parallel Python",
        patterns=[
            r"quantum",
            r"materials?\s+intelligence",
            r"materials?\s+discover",
            r"new\s+materials?",
            r"molecular",
            r"molecule",
            r"computational\s+chemistry",
            r"simulation",
            r"digital\s+twin",
            r"mit\.?\s*nano",
            r"hard[\s\-]?tech",
            r"deep[\s\-]?tech",
            r"scientific\s+discover",
            r"ses\s+ai",
            r"flagship",
            r"reindustrial",
            r"hardest\s+problems?",
        ],
    ),
    Bucket(
        weight=70,
        tag="data infra (Burla-direct)",
        reason="hosts and venues that build the Python-at-scale stack itself",
        patterns=[
            r"\bcoreweave\b",
            r"\bbaseten\b",
            r"\bmodal\b",
            r"anyscale",
            r"\bcoiled\b",
            r"\bdask\b",
            r"\bray\b",
            r"databricks",
            r"snowflake",
            r"\belastic\b",
            r"\bdatadog\b",
            r"\bvllm\b",
            r"\bspark\b",
            r"\bduckdb\b",
            r"weights\s*(&|and)\s*biases",
            r"\bwandb\b",
            r"data\s+pipeline",
            r"data\s+platform",
            r"data\s+infrastructure",
            r"data\s+engineering",
            r"data\s+lake",
            r"data\s+warehouse",
            r"data\s+swamp",
            r"data[\s\-]+ready",
            r"ai[\s\-]?ready\s+data",
            r"ai\s+infrastructure",
            r"ai\s+infra",
            r"compute\s+platform",
            r"compute\s+infrastructure",
            r"big\s+data",
            r"petabyte",
            r"terabyte",
            r"parquet",
            r"docling",
            r"high\s+performance\s+computing",
            r"\bhpc\b",
            r"data.*moat",
            r"data\s+foundation",
            r"performance[\s\-]?first\s+ai",
            r"\bcartography\b",
            r"platform\s+to\s+pipeline",
        ],
    ),
    Bucket(
        weight=52,
        tag="aerospace / defense / geospatial",
        reason="aerospace / defense / geospatial sensor data — multi-TB telemetry, real Python pipelines",
        patterns=[
            r"aerospace",
            r"defen[cs]e",
            r"national\s+security",
            r"dual[\s\-]?use",
            r"geospatial",
            r"earth\s+observation",
            r"satellite",
            r"air\s+space\s+intelligence",
            r"\basi\b",
            r"fourth\s+dimension",
            r"safran",
            r"\bqlab\b",
            r"federal\s+funding",
            r"autonomous\s+system",
            r"out[\s\-]?of[\s\-]?the[\s\-]?loop",
        ],
    ),
    Bucket(
        weight=42,
        tag="robotics / physical AI",
        reason="robotics fleet / sensor / vision data — Python-at-scale audience",
        patterns=[
            r"robotic",
            r"\brobots?\b",
            r"physical\s+ai",
            r"boston\s+dynamics",
            r"massrobotics",
            r"rise\s+robotics",
            r"pickle\s+robot",
            r"\btdk\b",
            r"toyota\s+ventures",
            r"frontier.*robotics",
        ],
    ),
    Bucket(
        weight=38,
        tag="climate / energy / industrial",
        reason="climate / energy / manufacturing data — heavy sensor + simulation workloads",
        patterns=[
            r"climate",
            r"\benergy\b",
            r"manufactur",
            r"industrial",
            r"\bnet[\s\-]?zero\b",
            r"\bsmart\s+grid\b",
            r"reframe\s+systems",
            r"mcj",
            r"sabanci\s+climate",
            r"hard\s+tech\s+demo",
            r"converging.*energy.*defense",
        ],
    ),
    Bucket(
        weight=30,
        tag="ML / inference / embeddings",
        reason="explicit inference / embedding / RAG / training infra signal",
        patterns=[
            r"\binference\b",
            r"\btraining\b",
            r"embeddings?",
            r"\bvector\b",
            r"vector\s+db",
            r"vectordb",
            r"\brag\b",
            r"retrieval",
            r"beyond\s+rag",
            r"fine[\s\-]?tun",
            r"model\s+(serving|evaluation|eval)",
            r"\bevals?\b",
            r"\bdspy\b",
            r"\bgpu\b",
            r"\bgpus\b",
            r"ml\s+pipeline",
            r"ml[\s\-]?ops",
            r"\bmlops\b",
            r"ml\s+platform",
            r"\bml\s+engineer",
        ],
    ),
    Bucket(
        weight=16,
        tag="wearable / IoT / analytics",
        reason="real-world telemetry / wearable / sports data — meaningful volumes",
        patterns=[
            r"\bwhoop\b",
            r"wearable",
            r"sensor",
            r"\bdraftkings\b",
            r"sports\s+ai",
            r"ai[\s\-]?enabled\s+analytics",
        ],
    ),
    Bucket(
        weight=10,
        tag="data Q&A / talks",
        reason="explicit data-as-topic event (the room self-selects for data-minded people)",
        patterns=[
            r"\bdata\b.*\bmoat\b",
            r"\bsecure\s+ai\s+for\s+your\s+data\b",
            r"\bdata\s+and\s+ai\b",
            r"\bdata\s+gap\b",
        ],
    ),
]

# ----------------------------------------------------------------------------
# NEGATIVE buckets - rooms full of audiences that almost never have a big-data
# Python pipeline today, even when the title sounds AI-coloured. Penalties are
# only applied to the event TITLE so a strong infra event isn't dragged down
# by a co-host's name.
# ----------------------------------------------------------------------------
NEGATIVE_BUCKETS: list[Bucket] = [
    Bucket(
        weight=-30,
        tag="agent hype",
        reason="agents / agentic / LLM-app builder framing — usually small-data app developers",
        patterns=[
            r"\bagentic\b",
            r"ai\s+agent",
            r"ai\s+agents",
            r"\bagents?\s+(meet|live|build|unleashed|reshap)",
            r"agentic\s+web",
            r"agentic\s+voice",
            r"agent\s+hack",
            r"multi[\s\-]?agent",
            r"autonomous\s+agents?",
            r"agent\s+swarms?",
            r"agent\s+development",
            r"build\s+(your\s+)?(first\s+)?ai\s+agent",
            r"agents?\s+for\s+your\s+business",
            r"agent\s+orchestrat",
            r"always[\s\-]?on\s+agent",
            r"soft\s+agents?",
            r"digital\s+coworker",
            r"\bsundai\b",
            r"vibe\s+coding",
            r"voice\s+ai",
            r"voice\s+dispatcher",
            r"agentic\s+ai",
        ],
    ),
    Bucket(
        weight=-20,
        tag="GTM / marketing / sales",
        reason="GTM / marketing / sales / CX AI — almost never a big-data Python audience",
        patterns=[
            r"\bgtm\b",
            r"marketing",
            r"brand\s+discoverab",
            r"sales\s+(on|in)",
            r"founder[\s\-]?led\s+(sales|marketing)",
            r"\bcx\b",
            r"customer\s+experience",
            r"customer\s+service",
            r"chatbot",
            r"sales\s+leader",
            r"\bb2b\s+sales\b",
            r"workflow\s+automation",
            r"workflow\s+delivery",
            r"automate\s+your\s+work",
            r"closing\s+the\s+ai\s+monetiz",
        ],
    ),
    Bucket(
        weight=-18,
        tag="career / talent / HR",
        reason="career / talent / HR / leadership framing — wrong audience",
        patterns=[
            r"\bcareer\b",
            r"\btalent\b",
            r"jobseeker",
            r"resume",
            r"hr\s+leader",
            r"ai\s+workforce",
            r"borderless\s+(life|tech\s+career)",
            r"leadership\s+vision",
            r"leading\s+through",
            r"founders?[''\s]+mind",
            r"founder\s+reset",
            r"morning\s+reset",
            r"founder\s+reality",
        ],
    ),
    Bucket(
        weight=-22,
        tag="VC / LP / investor-only",
        reason="VC / LP / investor-only — buyers / signal-givers, not pipeline builders",
        patterns=[
            r"\blp\b\s+(perspective|breakfast|dinner)",
            r"\blps\b",
            r"limited\s+partner",
            r"vc\s+(only|talent|investor|reverse|happy\s+hour|poker)",
            r"investor\s+happy\s+hour",
            r"reverse\s+(vc\s+)?pitch",
            r"investor\s+dinner",
            r"investor\s+networking",
            r"investor\s+office\s+hours",
            r"investor\s+breakfast",
            r"\bcvc\b",
            r"corporate\s+venture\s+capital",
            r"venture\s+capital\s+for",
            r"family\s+office",
            r"investing\s+in\s+ai\s+with\s+ai",
            r"how\s+to\s+raise",
            r"raise\s+a\s+series",
            r"raise\s+your\s+seed",
            r"\bm[\s&\-]?a\b\s+in\s+the\s+ai",
            r"allocating\s+to\s+atoms",
            r"\blp\s+dinner\b",
            r"gp\s*<?>?\s*lp",
            r"co[\s\-]?founder\s+match",
            r"founders?\s+&\s+funders?",
            r"founders?\s+(and|n['\u2019])\s+funders?",
            r"venture\s+troubl",
            r"reverse\s+pitch",
            r"pitch\s+competition",
        ],
    ),
    Bucket(
        weight=-12,
        tag="social / wellness",
        reason="social / wellness / sports / poker event — wrong context for technical pitch",
        patterns=[
            r"wakeup\s+run",
            r"wake[\s\-]?up",
            r"yacht",
            r"basketball",
            r"\bpoker\b",
            r"\byoga\b",
            r"wellness",
            r"\bfitness\b",
            r"\bpic\s?nic\b",
            r"pickleball",
            r"pushup\s+challenge",
            r"prayer\s+walk",
            r"\bskin\b",
            r"coffee\s+cart",
            r"donut",
            r"ball\s+game",
            r"barry['']?s",
            r"\bsoundcheck\b",
            r"chai\s+chats",
            r"founders?\s+pic",
        ],
    ),
    Bucket(
        weight=-10,
        tag="policy / ethics / governance",
        reason="policy / ethics / governance framing — strategy crowd, not builders",
        patterns=[
            r"\bpolicy\b",
            r"governance",
            r"governing\s+the\s+ai",
            r"\bethics\b",
            r"responsible\s+ai",
            r"trustworthy\s+ai",
            r"trusted\s+humans",
            r"compliance",
            r"\baia?\s+act\b",
            r"\beu\s+cra\b",
            r"geopolitic",
            r"sovereignty",
            r"intersection\s+of\s+ai\s+(&|and)\s+government",
        ],
    ),
    Bucket(
        weight=-8,
        tag="general AI hype",
        reason="generic AI-builder framing without bio / scientific / infra hook",
        patterns=[
            r"applied\s+ai\s+founder",
            r"ai\s+builder",
            r"ai\s+block\s+party",
            r"ai[\s\-]?native\s+(company|enterprise|playbook)",
            r"ai\s+playbook",
            r"showcase",
            r"ai\s+demo",
            r"ai\s+showcase",
            r"ai\s+with\s+impact",
            r"ai[\s\-]?enabled\s+leader",
            r"ai\s+ethics",
            r"ai\s+age",
            r"ai\s+strategy",
            r"redrawing\s+the\s+lines",
            r"in\s+the\s+age\s+of\s+ai",
            r"ai\s+era",
            r"ai\s+(monetiz|workforce|table)",
            r"q2\s+2026.*ai",
            r"state\s+of\s+ai",
            r"ai\s+poker",
            r"breakfast.*ai",
            r"\bai\s+block\b",
        ],
    ),
]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def host_text(ev: dict) -> str:
    hosts = ev.get("hosts") or []
    if not hosts:
        hosts = [ev.get("company") or ""]
    return " | ".join(h for h in hosts if h)


def bucket_hits(bucket: Bucket, text: str) -> bool:
    pattern = regex_alt(bucket.patterns)
    return bool(pattern.search(text))


def score_event(ev: dict) -> dict:
    title = normalize(ev.get("name") or "")
    hosts = normalize(host_text(ev))
    combined = f"{title} | {hosts}"

    score = 0
    matched_positive: list[Bucket] = []
    matched_negative: list[Bucket] = []

    for bucket in POSITIVE_BUCKETS:
        if bucket_hits(bucket, combined):
            matched_positive.append(bucket)
            score += bucket.weight

    for bucket in NEGATIVE_BUCKETS:
        if bucket_hits(bucket, title):
            matched_negative.append(bucket)
            score += bucket.weight

    strong_positive_tags = {
        b.tag
        for b in matched_positive
        if b.tag in {
            "bio / multi-omics",
            "healthcare / clinical AI",
            "data infra (Burla-direct)",
            "scientific compute",
        }
    }
    if strong_positive_tags and matched_negative:
        forgiven = 0
        for neg in matched_negative:
            if neg.tag == "VC / LP / investor-only":
                continue
            forgiven += int(round(neg.weight * 0.7))
        score -= forgiven

    if ev.get("isInviteOnly"):
        score -= 4

    if ev.get("partiful"):
        score += 2

    score = max(0, min(100, score))

    if score >= 80:
        tier = "Top Burla Target"
    elif score >= 60:
        tier = "Strong Fit"
    elif score >= 40:
        tier = "Worth Trying"
    elif score >= 20:
        tier = "Soft / Adjacent"
    else:
        tier = "Off-Topic"

    tags: list[str] = []
    for b in matched_positive:
        if b.tag and b.tag not in tags:
            tags.append(b.tag)
    for b in matched_negative:
        label = f"-{b.tag}"
        if label not in tags:
            tags.append(label)

    evidence_parts: list[str] = []
    if matched_positive:
        positives = []
        for b in matched_positive:
            if b.reason not in positives:
                positives.append(b.reason)
        evidence_parts.append("Positive: " + "; ".join(positives) + ".")
    if matched_negative:
        negatives = []
        for b in matched_negative:
            if b.reason not in negatives:
                negatives.append(b.reason)
        evidence_parts.append("Penalty: " + "; ".join(negatives) + ".")
    if not matched_positive and not matched_negative:
        evidence_parts.append(
            "No strong signal. Generic Tech-Week networking room - unlikely to contain big-data Python builders."
        )

    if ev.get("isInviteOnly"):
        evidence_parts.append("Invite only - applying may not get you in.")
    if not ev.get("partiful"):
        evidence_parts.append("No public Partiful link.")

    return {
        **ev,
        "score": score,
        "tier": tier,
        "tags": tags,
        "evidence": " ".join(evidence_parts),
    }


scored = [score_event(ev) for ev in EVENTS]
scored.sort(key=lambda e: (-e["score"], e["date"] or "", e["time"] or ""))

with open("events_scored.json", "w", encoding="utf-8") as f:
    json.dump(scored, f, indent=2, ensure_ascii=False)

print(f"Wrote events_scored.json with {len(scored)} events.")
tier_counts: dict[str, int] = {}
for ev in scored:
    tier_counts.setdefault(ev["tier"], 0)
    tier_counts[ev["tier"]] += 1
for tier in [
    "Top Burla Target",
    "Strong Fit",
    "Worth Trying",
    "Soft / Adjacent",
    "Off-Topic",
]:
    print(f"  {tier}: {tier_counts.get(tier, 0)}")
