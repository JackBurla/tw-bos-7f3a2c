"""Recalibrate guest scores with a sharper Burla 'Big Data?' lens.

Reviewing burla.dev + GitHub README clarified the ICP:
  - Concrete workloads: 2.4TB Parquet ETL, XGBoost HP sweeps on 1,000 CPUs,
    genome alignments on 1,300 CPUs, batch embeddings, batch LLM inference.
  - Pain it solves: people hitting OOM, waiting on VM reboots, juggling YAML
    for cluster config. People who already script Python over big data and
    want fan-out without thinking about infra.

A guest only deserves 85+ if there's specific evidence they author
multi-GB+ Python data pipelines TODAY:
  - single-cell / spatial omics (Reflector Bio, Romix, Cartography itself)
  - genome alignment / NGS / pooled screening (Broad-style)
  - batch LLM inference / training infra (DGX Blackwell-class work)
  - protein-structure / docking / MD at scale
  - GPU/HPC cluster authors (Anduril, SpaceX, ex-Quantum-Si)

LLM-wrapper / agent-runtime / on-device CNN / wearable-sensor / hardware
plays should NOT be above ~60. Consultants/strategists/PMs cap ~55.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parent
SCORED = ROOT / "scored"

# Adjustments: name -> (new_score, optional_reason_suffix)
AIBIO_ADJUSTMENTS: dict[str, tuple[int, str]] = {
    # ---- UPGRADES (clear big-data Python today) ----
    "Jessup Jong": (90, "Set DeepSeek R1 to 303 tok/s on NVIDIA DGX Blackwell with custom TRTLLM — peak batch LLM inference infra. Burla's exact workload."),
    "Giota Kyriakou": (92, "Tessera Therapeutics: AI/ML + physics-guided protein/RNA design at scale — protein language models, MD, gene-editing therapeutics. Spot-on ICP."),
    "Becca Carlson": (90, "Co-developed Optical Pooled Screening at Broad (Blainey/Hacohen) — multi-TB image+genomics workload. Now building Deliverome (AI cell-surface atlas). Quintessential Burla user."),
    "Jessica Bryant": (84, "Cambridge MA comp-bio at Seres (microbiome multi-omics). VOWST Phase 3 contributor. Multi-omics + ML on microbiome = real big-data pipeline."),
    "Tejal Patwari": (80, "PhD on optogenetic CRISPR / SELEX / NGS for RNA aptamer screening — NGS pipelines = multi-GB+. Moving to Boston."),
    "Sarala Sharma": (72, "Used UCLA Hoffman2 HPC for histone-modification chromatin profiling. Now AI Engineer (LLM apps) at UCLA Health. Already running batch comp-bio on HPC."),
    "Pranay Baid": (78, "LibGem Analytics — pooled industry data + synthetic training data infra. Data engineering core is Burla-adjacent."),

    # ---- DOWNGRADES (LLM-wrapper / agent / advisor without big data) ----
    "chris marstall": (55, "Translation pipeline runs on OpenAI/Claude APIs — LLM wrapper, not batch compute. Bio domain knowledge but not the workload Burla solves."),
    "Prasanth Sasikumar": (58, "FlowsXR AR/VR + NUS XR research. Sensor/perception data possible but no current Python batch pipeline evidence; mostly AR/VR product work."),
    "elan pavlov": (52, "MIT postdoc theoretical CS + Good Judgment superforecaster. Comp-bio publication adjacency but no big-data workload."),
    "Charles Mbata": (52, "MyMonitor.AI does ON-DEVICE CNN/RNN/GNN — on-device implies small models, not Burla scale. MetalDrug.com side is more interesting but unclear."),
    "Nicholas Zolton": (48, "SWE at Max AI / ex-Happyverse (AI avatars / video chat). Product code, not big-data Python."),
    "Siddhartha Bhattacharya": (35, "PwC Partner & GenAI Leader — consultant/advisor, not pipeline author. Network value only."),
    "Wesley Suen": (48, "Biology PhD just starting at MIT + biotech-investing background. Future user possible but no current pipeline."),
    "James Sinka": (38, "Repeat founder (Hypnos sleep, Orange DAO YC fund). DeSci/Web3 investor blend. Not authoring Python pipelines."),
    "Babak Kia": (38, "BU Senior Lecturer + solo angel + mentor. Educator/investor, not builder."),
    "Ackshay Nagamallu Rajasekar": (50, "NEU grad student / data scientist — plausible future user but early."),
    "Ryan Nie": (48, "BU physics+stats undergrad → GT MSCS. Student hackathon builder, future user."),
    "Phillips Le": (42, "Northeastern undergrad. Hackathon CV builder (YOLOv8). Student-level."),
    "Nghia Trang": (42, "Northeastern undergrad teammate of Phillips Le. Student-level."),
    "Erika Francoeur": (40, "REALM Bio Project Manager (CGT access). Biotech ops, not coder."),
    "Sanjay Goel": (25, "NachoNacho B2B SaaS marketplace CEO/Founder. Investor signal."),
    "Brian O'Neill": (28, "Designing for Analytics — UX/analytics consulting. Not Python pipeline author."),
    "Krish Sahijwani": (15, "C10 Labs VC analyst. Pure investor."),
    "Nate Macht": (15, "BrightEdge ACS investor."),
    "Caroline Pepek": (22, "MassBio BD. Industry org BD, not coder."),
    "Robert Gottlieb": (18, "RMG Associates PR/comms."),
    "Eleanor Kolossovski": (28, "Life-sci commercial consultant."),
    "Naoko Lammers": (28, "Mitsubishi Corporate Americas — corporate scout."),
    "Ryan Luginbuhl, MD": (25, "Chief Health AI — MD-led healthcare-AI strategy, not pipeline coder."),
    "Loretta TIOIELA": (28, "Next Sequence TechBio VC + ex-Scaleway VP AI/Cloud — investor lens with tech depth."),
    "Sergei Chislov": (15, "01 Foundry venture studio."),
    "Shannon Bean": (15, "CEI Ventures investor."),
    "Alexy Joven": (12, "Modjo growth/marketing — confirmed non-fit."),
    "Alcamo Ventures": (10, "Investor fund entity."),
    "Katia Ameri": (15, "a16z Partner + Boston Tech Week host. Pure VC."),
    "Masaru Nagura": (32, "CIC Tokyo / FoundersNation — ecosystem builder."),
    "John Ikudaisi": (38, "MotionArc agentic healthcare AI + growth. LA. LLM-agent + marketing."),
    "Francesca Grippa": (42, "Northeastern Sr Assoc Dean of Research — academic, business-innovation networks. Not Python pipeline."),

    # ---- mild downgrades for verified-but-not-ICP technical roles ----
    "Ziqiang Xu": (40, "Hokdo B2B customer-success SaaS — technical founder but SaaS not big-data."),
    "Tatsiana Kirimava": (38, "Orangesoft outsourcing — services agency."),
    "Sofi Le": (40, "BC freshman HCE+CS. Early student."),
    "Phillips Le, Lawrence Weru": (40, ""),  # noop unless matched
    "Lawrence Weru": (42, "MA State Accessibility Officer / ex-HMS HiDIVE Lab — policy + accessibility focus."),
    "Yuvanguru B": (48, "Nashua HS sophomore + ISEF finalist Alzheimer's screener — impressive but student."),
    "Ameya Kharade": (48, "Nashua HS junior + ISEF finalist fMRI CNN — impressive but student."),
}

CARTOGRAPHY_ADJUSTMENTS: dict[str, tuple[int, str]] = {
    # ---- mild UPGRADES for verified big-data evidence ----
    "Andrew Zorn": (82, "GRIK Therapeutics uses AWS + GPU clusters per NIH STTR proposal — confirmed cloud HPC author."),
    "Nikolay Vyahhi": (78, "Co-author of SPAdes genome assembler — built a flagship multi-GB bioinformatics pipeline. Now building Egbe (AI-native autonomous companies)."),
    "Andy Cosgrove": (75, "Paradigm4 CRO — sells the scalable DBMS for multimodal genomics data. Knows every Burla buyer."),
    "Bobby Hollingsworth": (75, "Arena BioWorks Sr Scientist (target discovery & validation, Harvard PhD). Proteomics/multi-omics at scale."),
    "Lokkit Sanjay Babu Narayanan": (75, "Anduril SWE + ex-SpaceX Starship flight software + AWS AI/ML + CUDA/Kokkos. Robotics-perception HPC."),
    "Becca Carlson": (90, "Optical Pooled Screening at Broad — multi-TB image+genomics. Now Deliverome. Quintessential Burla user."),

    # ---- DOWNGRADES (LLM-wrapper, hardware-only, wearable, agent-runtime) ----
    "Uros Kuzmanovic": (60, "BioSens8 = wearable continuous biosensor hardware. Time-series signal processing, hardware co — not Burla-scale Python pipeline."),
    "Zane El Kilany": (60, "TorchStack = graph-based NN platform. Python/PyTorch-heavy but unclear if customers run big-data workloads through it. Speculative."),
    "Aileen Mastouri": (65, "RevivBio microfluidic+AI biologics discovery — fit but speculative; hardware-heavy assay platform."),
    "Jack O'Brien": (50, "Subconscious = agent runtime layer. LLM agent infra, not batch big data."),
    "Farshid Ghasemi": (55, "Weddell Technologies = photonic instruments. Ex-Quantum-Si single-molecule HW. Hardware-co, not pipeline coder."),
    "Bahar Bilgen": (55, "EQLabs lab science tools + Brown ortho research. Bio domain but no specific pipeline evidence."),
    "Alicia Chong Rodriguez": (52, "Bloomer Tech = smart-textile ECG wearable. Some ML on biomarkers, mostly hardware co."),
    "Dr. Adam Crego": (55, "Brown adjunct + ex-Alloy COS. Teaches Applied AI/ML in Biotech — network buyer, not pipeline author."),
    "Salim Malakouti": (58, "NOMA AI clinical decision support — real-time on EHR, not multi-TB."),
    "Cihan Cayli": (48, "Duke CS/Econ undergrad. Early-career."),
    "Snehal Verma": (55, "NatureDots aquaculture digital twin — sensor data, real-time. Plausible but adjacent."),
    "Harshit Chellani": (55, "Columbia BME PhD + Nucleate NY — academic + ecosystem."),
    "Florian Finn Fuchs": (50, "MIT IPC + TUM AI/Robotics MSc — academic researcher."),
    "Alana Mazzei": (55, "WHOOP Sr PM Research/Algos/Data — manages ML org, not personally pipeline coder."),
    "Patrick Thayer": (52, "Aster Biofabrication = 3D cell culture automation hardware tooling."),
    "James Sinka": (45, "BIO Protocol deep-tech accelerator + DeSci/Web3 history. Builder-adjacent investor."),
    "Levente Fazekas": (45, "AIRA Health Colligo = LLM agents for clinical trial protocols. Agent infra, not big data."),
    "Julie Zhang": (45, "Stealth biologics drug delivery (unverified). Lower confidence."),
    "Jena Jordahl": (45, "Multi-agent LLM deployment focus — not multi-TB batch."),
    "Jinkuk Choi": (50, "Elisigen CSO = strategy/corp-dev role, not engineer."),
    "Hannan Shah": (45, "Beagle Labs / ex-Browserbase — AI agent workflow infra, not big data."),
    "Andrea Liao": (50, "OpenGraph AI solo founder + Data Engineer @ TELUS. Adjacent but solo/side."),
    "Giridhar Kalpathy Narayanan": (45, "Healthcare AI agents (calling payers, IVRs). LLM agent infra, not big data."),
    "Cathy Kuang": (52, "Takeda Sr Director Research Tech & Lab Systems — buyer/decision-maker, not coder."),
    "Matthew Mottola": (38, "Human Cloud — book/talent platform. Not pipeline coder."),
    "Stephen Remondi": (78, "Xsphera ex-vivo tumor microenvironment cloud analytics CEO. Patient-tumor data pipelines plausible, but he's CEO — team runs Burla, not him personally. Light downgrade from 85."),
    "Kinga Matula": (88, "QurieGen single-cell oncology drug-response prediction. Was CEO + scientist, droplet microfluidics papers. Strong."),
    "Robin Guo": (62, "Ex-a16z speedrun founding team, now stealth metabolic-health. Network value > pipeline author."),
    "Jose F. Rodriguez-Orengo": (62, "MBQ Pharma CEO — biotech relationship but he's a CEO/academic, team runs comp-bio."),

    # Speakers / negatives
    "Kevin Parker": (60, "Cartography Biosciences CEO speaker. Comp-bio target discovery / tumor antigen mapping. Team almost certainly runs single-cell / genomics pipelines — high-leverage relationship even if Kevin doesn't code."),
    "Heidi Erlacher": (28, "Fenwick Partner / event moderator — law firm. Not a pipeline user; relationship value only."),

    # confirmed non-fits
    "Sasha Grinshpun": (22, "Executive coach. Not a fit."),
    "Mae Kass, MPH, UN, OLY": (28, "Angel + Olympian. Network, not coder."),
    "Nora Kased": (30, "Stealth biotech COO + luxury goods background. Not pipeline coder."),
    "Carlton Davis": (5, "Cornerback NE Patriots. Not in scope."),
    "Brad Bowery": (22, "Deel VC Partnerships. Investor/BD."),
    "Jordan Golson": (25, "Article III AI-governance / ex-WIRED. Policy/legal."),
    "Eric Haywood": (22, "InterSystems Ventures investor."),
    "Christopher Gilbert": (28, "Operator AI SaaS, acquired by Yelp. Starting a VC fund. Investor."),
    "Rush Hogan": (22, "Investor."),
    "Casey Bangs": (22, "PNC Managing Director — banker."),
    "Mose Cassaro": (22, "Solo GP RDF Ventures — VC."),
    "berk ozer": (22, "2x YC founder + former VC + invested in 150+ startups."),
    "Niajee Washington": (35, "Stealth AI venture + ex-Point72 healthcare research. Investor-leaning."),
    "Sanjay Goel": (25, "NachoNacho B2B SaaS marketplace. Investor signal."),
    "Sasha Grinshpun ": (22, ""),  # safe duplicate
}


def apply_adjustments(slug: str, adjustments: dict[str, tuple[int, str]]) -> None:
    path = SCORED / f"{slug}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    n = 0
    for g in data["guests"]:
        name = g.get("name", "").strip()
        if name in adjustments:
            new_score, reason = adjustments[name]
            old = g.get("score", 0)
            g["score"] = new_score
            if reason:
                ev = g.get("evidence", "") or ""
                marker = "Burla big-data re-cal:"
                if marker not in ev:
                    g["evidence"] = f"{ev} [{marker} {reason}]".strip()
            tags = g.setdefault("tags", [])
            if "bigdata-recal" not in tags:
                tags.append("bigdata-recal")
            n += 1
            print(f"  {old:3d} -> {new_score:3d}  {name}")
    data["guests"].sort(key=lambda g: g.get("score", 0), reverse=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Recalibrated {n}/{len(data['guests'])} {slug} guests.")


def main() -> None:
    print("== AI/Bio Hackathon ==")
    apply_adjustments("aibio_hackathon", AIBIO_ADJUSTMENTS)
    print()
    print("== Cartography x a16z ==")
    apply_adjustments("cartography_a16z", CARTOGRAPHY_ADJUSTMENTS)


if __name__ == "__main__":
    main()
