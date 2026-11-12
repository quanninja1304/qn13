"""P-A prompt builder (rules section 4.1-4.3). Builds units, pair samples, pseudowords and the exact prompt texts for
Q-GRAPH and Q-PAIR, writes them to artifacts/llm_prior_p17/pa_prompts.jsonl and counts tokens locally (no API call).

Usage: python -P -E PA_prompts.py <artifacts/llm_prior_p17>
"""
from __future__ import annotations

import json
import random
import string
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from p17_common import classify_pairs, hide_variables, mag_from_dag, parse_bif  # noqa: E402

NETWORKS = ["asia", "cancer", "earthquake", "survey", "sachs", "child", "insurance", "alarm", "hailfinder", "hepar2"]
HIDE_SEEDS = [1, 2, 3]
SEED = 20261112
MAX_PAIRS = 60

# One sentence per network, identical under KEEP and PSEUDO (rules 4.2). Written from the bnlearn repository's
# descriptions as remembered; to be checked against bnlearn.com before the locking commit.
DOMAIN = {
    # Domain only; never name a concept that is itself a variable (would leak meaning under PSEUDO).
    "asia": "a small model used in medical diagnosis",
    "cancer": "a small model used in medical diagnosis",
    "earthquake": "a small model of a household situation",
    "survey": "a survey of people living in a city",
    "sachs": "a model of a biological system measured in human cells",
    "child": "a model used in medical diagnosis of newborn babies",
    "insurance": "a model used by a car insurance company",
    "alarm": "a model used for monitoring patients in intensive care",
    "hailfinder": "a model used in weather forecasting",
    "hepar2": "a model used in medical diagnosis",
}

Q_GRAPH = (
    "The following variables come from {domain}.\n\n"
    "Variables:\n{var_lines}\n\n"
    "Propose the causal graph among these variables as a directed acyclic graph. List every direct causal "
    "relationship as one line of the form `X -> Y`, meaning that X directly causes Y. Use the variable names exactly "
    "as written above. Output only the list of edges, one per line, with no other text."
)

Q_PAIR = (
    "The following variables come from {domain}. The list may not contain every relevant variable of the system.\n\n"
    "Variables: {var_inline}\n\n"
    "What is the causal relationship between \"{a}\" and \"{b}\"?\n"
    "(a) \"{a}\" directly causes \"{b}\", not through any other variable in the list.\n"
    "(b) \"{b}\" directly causes \"{a}\", not through any other variable in the list.\n"
    "(c) One of them causes the other only indirectly, through other variables in the list.\n"
    "(d) Neither causes the other, but they share a common cause that is not in the list.\n"
    "(e) They are not causally related.\n\n"
    "You may reason briefly first. End your reply with a final line of the form `ANSWER: x`, where x is one of "
    "a, b, c, d or e."
)  # v2 (13/11): v1 ended with "Answer with a single letter: a, b, c, d or e." and failed RA0 (rules section 7, item 27)

VOWELS, CONS = "aeiou", "bcdfghjklmnprstvwz"


ENGLISH: set = set()
REJECTED = {"english_word": 0, "real_name": 0}


def pseudowords(names, seed):
    """Deterministic pronounceable 4-6 letter pseudowords, unique per unit, never in the 10 000-word English list
    (rules 4.2) and never equal to any real variable name of the unit (case-insensitive)."""
    rng = random.Random(seed)
    real = {n.lower() for n in names}
    out, used = {}, set()
    for n in names:
        while True:
            L = rng.choice([4, 5, 6])
            w = "".join(rng.choice(CONS) if i % 2 == 0 else rng.choice(VOWELS) for i in range(L))
            if w in ENGLISH:
                REJECTED["english_word"] += 1
                continue
            if w in real:
                REJECTED["real_name"] += 1
                continue
            if w not in used:
                used.add(w)
                out[n] = w
                break
    return out


def sample_pairs(classes, rng):
    by = {c: sorted(tuple(sorted(p)) for p, cc in classes.items() if cc == c) for c in "DBIN"}
    nB = len(by["B"])
    q = min(15, max(5, nB))
    take = {c: rng.sample(by[c], min(q, len(by[c]))) for c in "DIN"}
    room = MAX_PAIRS - sum(len(v) for v in take.values())
    take["B"] = rng.sample(by["B"], min(nB, room))
    pairs = [(c, p) for c in "DBIN" for p in take[c]]
    rng.shuffle(pairs)
    return pairs, {c: len(by[c]) for c in "DBIN"}


def build(root):
    units, prompts = [], []
    for name in NETWORKS:
        g = parse_bif(Path(root) / "bnlearn" / f"{name}.bif")
        seen = set()
        for s in HIDE_SEEDS:
            h = hide_variables(g, s)
            if h["latent"] is None or frozenset(h["latent"]) in seen:
                continue
            seen.add(frozenset(h["latent"]))
            obs = h["observed"]
            mag = mag_from_dag(g, obs)
            classes = classify_pairs(g, obs, mag)
            uid = f"{name}_{s}"
            rng = random.Random(SEED + 31 * s + sum(map(ord, name)))
            var_order = obs[:]
            rng.shuffle(var_order)
            pairs, avail = sample_pairs(classes, rng)
            pw = pseudowords(obs, SEED + 97 * s + sum(map(ord, name)))
            units.append({"unit": uid, "network": name, "hide_seed": s, "n_observed": len(obs), "latent": sorted(h["latent"]),
                          "pairs_available": avail, "pairs_sampled": {c: sum(1 for cc, _ in pairs if cc == c) for c in "DBIN"}})
            for cond in ("KEEP", "PSEUDO"):
                nm = (lambda v: v) if cond == "KEEP" else (lambda v, pw=pw: pw[v])
                names = [nm(v) for v in var_order]
                prompts.append({"unit": uid, "cond": cond, "format": "Q-GRAPH",
                                "text": Q_GRAPH.format(domain=DOMAIN[name], var_lines="\n".join(f"- {v}" for v in names)),
                                "name_map": {v: nm(v) for v in obs}})
                for i, (c, (x, y)) in enumerate(pairs):
                    a, b = (x, y) if rng.random() < 0.5 else (y, x)
                    prompts.append({"unit": uid, "cond": cond, "format": "Q-PAIR", "pair_index": i, "true_class": c,
                                    "a": a, "b": b,
                                    "text": Q_PAIR.format(domain=DOMAIN[name], var_inline=", ".join(names), a=nm(a), b=nm(b))})
    return units, prompts


def main():
    root = Path(sys.argv[1])
    wl = root / "wordlist" / "google-10000-english.txt"
    if not wl.exists():
        raise SystemExit(f"missing English word list {wl} (rules 4.2)")
    ENGLISH.update(w.strip().lower() for w in wl.read_text(encoding="utf-8").splitlines() if w.strip())
    units, prompts = build(root)
    print("pseudoword candidates rejected:", REJECTED, "| word list size:", len(ENGLISH))
    out = root / "pa_prompts.jsonl"
    with open(out, "w", encoding="utf-8") as f:
        for p in prompts:
            f.write(json.dumps(p) + "\n")
    import tiktoken
    enc = tiktoken.get_encoding("o200k_base")
    overhead = 7  # chat formatting tokens per single-message request (approximate)
    stats = {}
    for p in prompts:
        k = (p["cond"], p["format"])
        n = len(enc.encode(p["text"])) + overhead
        s = stats.setdefault(k, {"calls": 0, "input_tokens": 0, "max_input": 0})
        s["calls"] += 1
        s["input_tokens"] += n
        s["max_input"] = max(s["max_input"], n)
    graph_true_edges = {}
    for u in units:
        g = parse_bif(root / "bnlearn" / f"{u['network']}.bif")
        graph_true_edges[u["unit"]] = g.number_of_edges()
    summary = {"n_units": len(units), "units": units, "token_stats": {f"{a}|{b}": v for (a, b), v in stats.items()},
               "sum_true_edges_over_units": sum(graph_true_edges.values()), "prompts_file": str(out)}
    (HERE / "PA_prompt_stats.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print("units", len(units))
    for u in units:
        print(" ", u["unit"], "obs", u["n_observed"], "sampled", u["pairs_sampled"], "available", u["pairs_available"])
    for k, v in summary["token_stats"].items():
        print(k, v)
    print("sum of true DAG edges over units (to size Q-GRAPH output):", summary["sum_true_edges_over_units"])
    ex = next(p for p in prompts if p["format"] == "Q-PAIR" and p["unit"] == "asia_1" and p["cond"] == "KEEP")
    print("\n--- example Q-PAIR (asia_1, KEEP) ---\n" + ex["text"])
    ex = next(p for p in prompts if p["format"] == "Q-GRAPH" and p["unit"] == "asia_1" and p["cond"] == "PSEUDO")
    print("\n--- example Q-GRAPH (asia_1, PSEUDO) ---\n" + ex["text"])


if __name__ == "__main__":
    main()
