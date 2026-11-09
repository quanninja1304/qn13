"""Forward-citation audit through the Semantic Scholar graph API. No credentials and no personal data are sent."""
import json
import re
import sys
import time
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OUT = sys.argv[1]
SEEDS = {
    "M1 Strobl 2018": "ARXIV:1705.09031",
    "Tu 2019 MVPC": "ARXIV:1807.04010",
    "Witte 2022": "ARXIV:2108.13331",
    "Didelez 2010": "ARXIV:1101.0901",
    "Mohan Pearl 2021 review": "ARXIV:1801.03583",
    "Nabi Bhattacharya 2022": "ARXIV:2203.00132",
    "Qiao 2024": "ARXIV:2312.12206",
}
KEY = re.compile(r"missing|incomplete|selection|test-?wise|deletion|attrition|collider|mnar|complete.?case|imputation", re.I)
DISC = re.compile(r"discover|structure learning|structural learning|\bPC\b|\bFCI\b|causal graph|DAG|conditional independence|graph", re.I)
allrows = {}
report = {}
for name, pid in SEEDS.items():
    rows, off = [], 0
    while off < 1000:
        url = "https://api.semanticscholar.org/graph/v1/paper/" + urllib.parse.quote(pid, safe=":") + f"/citations?fields=title,year,venue,externalIds,abstract&limit=200&offset={off}"
        data = None
        for attempt in range(6):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "literature-audit-script"})
                with urllib.request.urlopen(req, timeout=40) as r:
                    data = json.load(r)
                break
            except Exception as e:  # rate limiting is expected without a key
                print(name, "retry", attempt, str(e)[:80], flush=True)
                time.sleep(8 * (attempt + 1))
        if data is None:
            print(name, "FAILED at offset", off, flush=True)
            break
        batch = [d["citingPaper"] for d in data.get("data", [])]
        rows += batch
        if "next" not in data or not batch:
            break
        off = data["next"]
        time.sleep(4)
    report[name] = len(rows)
    print(name, "citations returned:", len(rows), flush=True)
    for p in rows:
        pid2 = p.get("paperId")
        if pid2:
            allrows.setdefault(pid2, {**p, "seeds": []})["seeds"].append(name)
    time.sleep(4)
keep = []
for p in allrows.values():
    text = (p.get("title") or "") + " " + (p.get("abstract") or "")
    if KEY.search(text) and DISC.search(text):
        keep.append(p)
keep.sort(key=lambda p: (-(p.get("year") or 0), p.get("title") or ""))
json.dump({"counts": report, "unique": len(allrows), "kept": keep}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("unique citing papers", len(allrows), "kept after keyword filter", len(keep))
