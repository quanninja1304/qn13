"""P-A runner: sends the prompts built by PA_prompts.py to one locked model family, logs raw responses, enforces a cost cap.

Families and channels are fixed by PA_PB_reading_rules_vi.md section 7, items 15-18. Keys are read from the repo-root .env
(never printed). Raw responses go to artifacts/llm_prior_p17/llm_raw/<family>.jsonl (git-ignored), resumable by prompt id.
During a run only parse rate (RA0) and cost are printed; no P-A metric is computed here (rule 17).

Usage: python -P -E PA_run.py <artifacts/llm_prior_p17> --family openai|deepseek|llama --cond KEEP|PSEUDO|both
                              [--format Q-GRAPH|Q-PAIR|both] [--cap-usd 2.0] [--limit N] [--workers 4]
"""
from __future__ import annotations

import json
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# USD per 1M tokens, from the official pages read 2026-11-13 (PA_cost_estimate_vi.md); OpenRouter prices from its models API.
FAMILIES = {
    "openai": {"base_url": None, "key": "OPENAI_API_KEY", "model": "gpt-4.1-mini-2025-04-14",
               "extra": {}, "seed": None, "price": (0.40, 1.60)},
    "deepseek_official": {"base_url": "https://api.deepseek.com", "key": "DEEPSEEK_API_KEY", "model": "deepseek-flash",
                          "extra": {"thinking": {"type": "disabled"}}, "seed": None, "price": (0.30, 1.20)},
    "deepseek_openrouter": {"base_url": "https://openrouter.ai/api/v1", "key": "OPENROUTER_API_KEY",
                            "model": "deepseek/deepseek-v4.1-flash-1017",
                            "extra": {"provider": {"order": ["DeepSeek"], "allow_fallbacks": False}, "reasoning": {"enabled": False}},
                            "seed": None, "price": (0.15, 0.60)},
    "llama": {"base_url": "https://openrouter.ai/api/v1", "key": "OPENROUTER_API_KEY", "model": "meta-llama/llama-3.3-70b-instruct",
              "extra": {"provider": {"order": ["CoreWeave"], "allow_fallbacks": False}}, "seed": 20261112, "price": (0.71, 0.71)},
}
MAX_TOKENS = {"Q-GRAPH": 3000, "Q-PAIR": 5}
LETTER = re.compile(r"^\W*\(?([a-eA-E])\b")
EDGE = re.compile(r"^\s*[-*\d.)]*\s*`?([^`\s][^`]*?)`?\s*->\s*`?([^`]*?)`?\s*$")


def load_env():
    for line in (REPO / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def prompt_id(p):
    return f'{p["unit"]}|{p["cond"]}|{p["format"]}|{p.get("pair_index", "-")}'


def parse_ok(fmt, text):
    if text is None:
        return False
    if fmt == "Q-PAIR":
        return LETTER.match(text.strip()) is not None
    lines = [ln for ln in text.splitlines() if ln.strip()]
    ok = [ln for ln in lines if EDGE.match(ln)]
    return bool(ok) and len(ok) >= 0.9 * len(lines)


def main():
    root = Path(sys.argv[1])
    arg = lambda name, default: sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default  # noqa: E731
    fam_name = arg("--family", None)
    cond = arg("--cond", "both")
    fmt_sel = arg("--format", "both")
    cap = float(arg("--cap-usd", "2.0"))
    limit = int(arg("--limit", "0"))
    workers = int(arg("--workers", "4"))
    if fam_name == "deepseek":
        fam_name = os.environ.get("P17_DEEPSEEK_CHANNEL", "deepseek_official")
    fam = FAMILIES[fam_name]
    load_env()
    from openai import OpenAI
    kw = {"api_key": os.environ[fam["key"]]}
    if fam["base_url"]:
        kw["base_url"] = fam["base_url"]
    client = OpenAI(**kw)

    prompts = [json.loads(line) for line in (root / "pa_prompts.jsonl").read_text(encoding="utf-8").splitlines()]
    prompts = [p for p in prompts if (cond == "both" or p["cond"] == cond) and (fmt_sel == "both" or p["format"] == fmt_sel)]
    out_dir = root / "llm_raw"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"{fam_name}.jsonl"
    done, spent = set(), 0.0
    if out_path.exists():
        for line in out_path.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            if r.get("status") == "ok":
                done.add(r["id"])
            spent += r.get("cost_usd", 0.0)
    todo = [p for p in prompts if prompt_id(p) not in done]
    if limit:
        todo = todo[:limit]
    print(f"family={fam_name} model={fam['model']} todo={len(todo)} already_done={len(done)} spent_so_far=${spent:.4f} cap=${cap}", flush=True)
    lock = threading.Lock()
    state = {"spent": spent, "stop": False, "n": 0, "parsed": {"Q-GRAPH": [0, 0], "Q-PAIR": [0, 0]}}

    def call(p):
        if state["stop"]:
            return None
        body = {"model": fam["model"], "messages": [{"role": "user", "content": p["text"]}], "temperature": 0,
                "max_tokens": MAX_TOKENS[p["format"]]}
        if fam["seed"] is not None:
            body["seed"] = fam["seed"]
        for attempt in range(6):
            try:
                r = client.chat.completions.create(**body, extra_body=fam["extra"] or None)
                text = r.choices[0].message.content
                cost = (r.usage.prompt_tokens * fam["price"][0] + r.usage.completion_tokens * fam["price"][1]) / 1e6
                return {"id": prompt_id(p), "status": "ok", "family": fam_name, "model": r.model,
                        "provider": (r.model_extra or {}).get("provider"), "text": text,
                        "finish_reason": r.choices[0].finish_reason, "prompt_tokens": r.usage.prompt_tokens,
                        "completion_tokens": r.usage.completion_tokens, "cost_usd": cost, "ts": time.time()}
            except Exception as e:  # noqa: BLE001
                msg = f"{type(e).__name__}: {str(e)[:300]}"
                if any(s in msg for s in ("402", "credit", "Insufficient", "404", "401")):
                    return {"id": prompt_id(p), "status": "fatal", "error": msg, "ts": time.time()}
                time.sleep(2 ** attempt)
        return {"id": prompt_id(p), "status": "error", "error": msg, "ts": time.time()}

    with open(out_path, "a", encoding="utf-8") as fout, ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(call, p): p for p in todo}
        for f in as_completed(futs):
            rec = f.result()
            if rec is None:
                continue
            p = futs[f]
            with lock:
                fout.write(json.dumps(rec) + "\n")
                fout.flush()
                state["n"] += 1
                if rec["status"] == "ok":
                    state["spent"] += rec["cost_usd"]
                    pr = state["parsed"][p["format"]]
                    pr[1] += 1
                    pr[0] += parse_ok(p["format"], rec["text"])
                if rec["status"] == "fatal" or state["spent"] >= cap:
                    state["stop"] = True
                    print("STOP:", rec.get("error", f"cost cap ${cap} reached"), flush=True)
                if state["n"] % 100 == 0:
                    print(f"  {state['n']} calls, spent ${state['spent']:.4f}, parse {state['parsed']}", flush=True)
    print(f"finished: calls={state['n']} spent_total=${state['spent']:.4f} parse(ok,total)={state['parsed']}", flush=True)


if __name__ == "__main__":
    main()
