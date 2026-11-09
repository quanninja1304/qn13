"""Forward-citation audit through OpenAlex. No credentials and no personal data are sent."""
import json
import re
import sys
import time
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OUT = sys.argv[1]
SEEDS = {
    "M1 Strobl 2018": "doi:10.1007/s41060-017-0094-6",
    "Witte 2022": "doi:10.1002/sim.9535",
    "Didelez 2010": "doi:10.1214/10-sts340",
    "Tu 2019 MVPC": "title:Causal Discovery in the Presence of Missing Data",
    "Mohan Pearl 2021": "doi:10.1080/01621459.2021.1874961",
    "Gain Shpitser 2018": "title:Structure Learning Under Missing Data",
    "Foraita 2020": "title:Causal discovery of gene regulation with incomplete data",
}
KEY = re.compile(r"missing|incomplete data|selection bias|test-?wise|listwise|attrition|complete.?case|imputation", re.I)
DISC = re.compile(r"causal discovery|structure learning|structural learning|\bPC algorithm\b|\bFCI\b|causal graph|conditional independence|graphical model|bayesian network", re.I)


def get(url):
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "literature-audit-script"})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.load(r)
        except Exception as e:
            print("retry", attempt, str(e)[:80], flush=True)
            time.sleep(5 * (attempt + 1))
    return None


def abstract(inv):
    if not inv:
        return ""
    pos = {}
    for w, ps in inv.items():
        for p in ps:
            pos[p] = w
    return " ".join(pos[k] for k in sorted(pos))


rows = {}
counts = {}
for name, spec in SEEDS.items():
    if spec.startswith("doi:"):
        w = get("https://api.openalex.org/works/https://doi.org/" + spec[4:])
    else:
        r = get("https://api.openalex.org/works?per-page=5&search=" + urllib.parse.quote(spec[6:]))
        cand = [x for x in (r or {}).get("results", []) if (x.get("title") or "").lower().strip() == spec[6:].lower()]
        cand.sort(key=lambda x: -x.get("cited_by_count", 0))
        w = cand[0] if cand else None
    if not w:
        print(name, "seed not found", flush=True)
        counts[name] = None
        continue
    wid = w["id"].rsplit("/", 1)[-1]
    print(name, "->", wid, w.get("title"), w.get("cited_by_count"), flush=True)
    cursor, n = "*", 0
    while cursor and n < 1200:
        u = f"https://api.openalex.org/works?filter=cites:{wid}&per-page=200&cursor={urllib.parse.quote(cursor)}&select=id,title,publication_year,primary_location,doi,abstract_inverted_index,cited_by_count"
        r = get(u)
        if not r:
            break
        for x in r["results"]:
            rows.setdefault(x["id"], {**x, "seeds": []})["seeds"].append(name)
            n += 1
        cursor = r["meta"].get("next_cursor")
        if not r["results"]:
            break
        time.sleep(.5)
    counts[name] = n
    print(name, "citing:", n, flush=True)
keep = []
for x in rows.values():
    ab = abstract(x.get("abstract_inverted_index"))
    text = (x.get("title") or "") + " " + ab
    if KEY.search(text) and DISC.search(text):
        src = ((x.get("primary_location") or {}).get("source") or {}).get("display_name")
        keep.append({"title": x.get("title"), "year": x.get("publication_year"), "venue": src, "doi": x.get("doi"), "cited_by": x.get("cited_by_count"), "seeds": x["seeds"], "abstract": ab})
keep.sort(key=lambda p: (-(p.get("year") or 0), p.get("title") or ""))
json.dump({"counts": counts, "unique": len(rows), "kept": keep}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("unique citing", len(rows), "kept", len(keep))
