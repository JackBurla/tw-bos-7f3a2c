import json
from collections import Counter
from pathlib import Path

d = json.load(open(Path(__file__).parent / "scored/rise_robotics.json", encoding="utf-8"))
g = d["guests"]
verified = [x for x in g if not x.get("needs_verification")]
unverified = [x for x in g if x.get("needs_verification")]
with_linkedin = [x for x in g if x.get("linkedin")]
score40 = [x for x in g if x.get("score") == 40]
score55plus = [x for x in g if x.get("score", 0) >= 55]
initials_like = [
    x for x in g
    if len(x.get("name") or "") <= 3 and (x.get("name") or "").replace(".", "").isalpha()
]
short_names = [x for x in g if len((x.get("name") or "").split()) == 1]

print("declared", d.get("declared_count"), "parsed", d.get("parsed_count"))
print("verified:", len(verified))
print("unverified:", len(unverified))
print("with linkedin:", len(with_linkedin))
print("score exactly 40:", len(score40))
print("score 55+:", len(score55plus))
print("initials-like names:", len(initials_like))
print("single-token names:", len(short_names))
print()
print("Score distribution (top buckets):")
for s, c in sorted(Counter(x["score"] for x in g).items(), reverse=True)[:15]:
    print(f"  {s}: {c}")
print()
print("UNVERIFIED sample:")
for x in unverified[:8]:
    print(f"  {x['score']:3d} {x['name']!r}")
print()
print("VERIFIED with linkedin sample:")
for x in [x for x in verified if x.get("linkedin")][:8]:
    print(f"  {x['score']:3d} {x['name']}")
