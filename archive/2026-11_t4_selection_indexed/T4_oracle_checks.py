"""T4 kill test: oracle checks for selection-indexed orientation. See T4_kill_test_vi.md.

Oracle only: exact d-separation on small DAGs with missingness indicators. No data, no CI tests, no finite-sample claim.

Model. O = observed variables; each O_i has one indicator R_i (rows with O_i observed have R_i = 1). Under Assumption 1 of Strobl et al. 2018 the R_i have
no children. A regime is a set U of observed variables: rows complete on U, i.e. conditioning on R_U = {R_i : i in U}. A CI query (x, y | W) can be asked in
any regime U containing {x, y} and W. Regime O is listwise deletion.

Statements checked:
  A   Monotonicity: U subset U', dependent at U implies dependent at U' (Strobl Lemma 1, restated for any pair of regimes). Control: breaking Assumption 1.
  R0  Colombo et al. Lemma 3.1 at regime U: with W minimal at U, z in W iff z in An({x,y} and R_U). Dependence premises may be tested in sub-regimes (by A).
  R1  Indexed: arrow premise at U1 and separation premise at U2 give z in An(y or R_{U2 minus U1}). Naive pure conclusion z in An(y) when U2 is not inside U1.
  R4  Colombo et al. Lemma 3.2 at regime U, with (a2) tested in sub-regimes. Naive: separation and arrow premises in smaller regimes, conclusion without indicators.
  S   Same-target impossibility: explicit pairs of DAGs agreeing on every query outside listwise but differing on the listwise target.
  H   Oracle headroom on random m-DAGs: LW (FCI at regime O, which is what Strobl Algorithm 1 outputs in the oracle) against PP (union over all regimes U of
      FCI on U) against Naive (test-wise, no confirmation) against Ideal (no missingness). Claims counted: no direct edge, non-ancestor, pure ancestor.

READING RULES, FIXED BEFORE THE FIRST RUN (project-management choices):
  K1 Same target: the card's goal of a local rule keeping M1's exact target is NO-GO if the S check finds a pair.
  K2 Soundness: PP and the indexed rules must have 0 false claims. Any false claim means the statement or the code is wrong and stops the direction until explained.
  K3 Headroom: "worth a finite-sample pilot" if in at least one MNAR cell (q in {.1, .3}) PP has at least 1.10 times the true claims of LW, averaged over graphs.
     "No-go on claims" if below 1.05 in every such cell. In between: report as weak.
  FCI here is exhaustive-separating-set FCI with R0-R4 only (no selection rules R5-R10), the same for all methods, so absolute counts understate full FCI.

CHANGE AFTER THE FIRST QUICK RUN, BEFORE ANY FULL RUN (disclosed in the report). The quick run compared PP with LW and gave a ratio above 1 at q = 0, where every regime
returns the same CI answers, so no real gain is possible. The gain there is an artifact: PP reads claims from many sub-PAGs, LW from one. Changes made:
  - new comparator LWu = union of FCI on every variable subset, every query asked in regime O. Same extraction machinery as PP, only listwise rows. K3 now compares PP with LWu.
    Threshold values in K3 are unchanged. Raw LW is still printed.
  - new negative control K5: PP must equal LWu exactly when q = 0 (no O parents of indicators and no O-R confounder).
  - non-ancestor claims now use every ordered pair with no possibly-directed path in the PAG, for all methods, which narrows the artifact and is sound with selection variables.
  - IdealU replaces Ideal as the no-missingness upper bound, same machinery.
  - R4 check added (Colombo et al. Lemma 3.2 at regime U).
  - simple baseline SepOnly = LWu plus claims needing no orientation rule: any separation x,y|W in the smallest regime {x,y}+W gives no direct edge; a marginal
    separation x,y|{} in regime {x,y} gives non-ancestor both ways. PP3 = LWu plus union of FCI over regimes with |U| <= 3.
    K6 (same thresholds as K3, fixed before seeing this split): transport of orientation premises is "worth a pilot" only if PP/SepOnly >= 1.10 in at least one MNAR cell,
    "no-go on orientation" if PP/SepOnly < 1.05 in every MNAR cell, otherwise weak. If K3 passes and K6 fails, the headroom comes from separations alone and the
    regime-indexed orientation machinery is not the mechanism.
  - targeted discriminating-path graphs added to R4, because random graphs rarely reach its premises.
  - p = 6 added to H. Quick-run ratios (the only numbers seen before this change) were 1.03-1.10 at q = 0 and up to 1.53 at q <= .3.

Run: python -P -E T4_oracle_checks.py [--quick]
"""
from __future__ import annotations

import itertools
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

QUICK = "--quick" in sys.argv
HERE = Path(__file__).resolve().parent
SEED = 20261108
results: dict = {"meta": {"quick": QUICK, "seed": SEED}}
failures: list[str] = []
n_pass = 0


def check(name, cond, detail=""):
    global n_pass
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""), flush=True)
    if cond:
        n_pass += 1
    else:
        failures.append(f"{name}: {detail}")


def bits(m):
    while m:
        b = m & -m
        yield b.bit_length() - 1
        m ^= b


class MDag:
    """Nodes: O = 0..p-1, R_i = p+i, latents after that. pa[v] = bit mask of parents."""

    def __init__(self, p, n_extra=0):
        self.p = p
        self.pa = [0] * (2 * p + n_extra)
        self.names = {}
        self._an = {}
        self._cache = {}

    def add(self, u, v):
        self.pa[v] |= 1 << u

    def R(self, i):
        return self.p + i

    def rmask(self, Umask):
        return sum(1 << (self.p + i) for i in bits(Umask))

    def ancestors_of(self, mask):
        anc = mask
        fr = mask
        while fr:
            b = fr & -fr
            fr ^= b
            new = self.pa[b.bit_length() - 1] & ~anc
            anc |= new
            fr |= new
        return anc

    def in_an(self, z, mask):
        """z is an ancestor of (or in) the node set mask."""
        return bool((self.ancestors_of(mask) >> z) & 1)

    def dsep_raw(self, x, y, Cmask):
        anc = self.ancestors_of((1 << x) | (1 << y) | Cmask)
        adj = [0] * len(self.pa)
        for v in bits(anc):
            pm = self.pa[v]
            adj[v] |= pm
            for u in bits(pm):
                adj[u] |= (1 << v) | (pm & ~(1 << u))
        allowed = anc & ~Cmask
        seen = 1 << x
        fr = seen
        while fr:
            b = fr & -fr
            fr ^= b
            nb = adj[b.bit_length() - 1] & allowed & ~seen
            if (nb >> y) & 1:
                return False
            seen |= nb
            fr |= nb
        return True

    def sep(self, x, y, Wmask, Umask):
        if x > y:
            x, y = y, x
        key = (x, y, Wmask, Umask)
        v = self._cache.get(key)
        if v is None:
            v = self.dsep_raw(x, y, Wmask | self.rmask(Umask))
            self._cache[key] = v
        return v

    def obs_edge(self, x, y):
        return bool((self.pa[y] >> x) & 1) or bool((self.pa[x] >> y) & 1)


def subsets(mask):
    s = mask
    while True:
        yield s
        if s == 0:
            break
        s = (s - 1) & mask


def random_mdag(p, dens, q, conf_o, conf_r, rng, conf_or=0.0):
    extra = 0
    plans = []
    order = rng.permutation(p)
    g_edges = [(int(order[a]), int(order[b])) for a, b in itertools.combinations(range(p), 2) if rng.random() < dens]
    if rng.random() < conf_o:
        i, j = rng.choice(p, 2, replace=False)
        plans.append([int(i), int(j)])
    if rng.random() < conf_r:
        i, j = rng.choice(p, 2, replace=False)
        plans.append([p + int(i), p + int(j)])
    if rng.random() < conf_or:
        i, j = rng.choice(p, 2, replace=False)
        plans.append([int(i), p + int(j)])
    g = MDag(p, len(plans))
    for u, v in g_edges:
        g.add(u, v)
    for i in range(p):
        for u in range(p):
            if rng.random() < q:
                g.add(u, g.R(i))
    for k, ch in enumerate(plans):
        for c in ch:
            g.add(2 * p + k, c)
    return g


# ---------------------------------------------------------------- A: monotonicity
def lemma_A(g, stats):
    p = g.p
    full = (1 << p) - 1
    for x, y in itertools.combinations(range(p), 2):
        rest = full & ~(1 << x) & ~(1 << y)
        for W in subsets(rest):
            base = (1 << x) | (1 << y) | W
            extra = full & ~base
            for E1 in subsets(extra):
                U1 = base | E1
                if g.sep(x, y, W, U1):
                    continue
                for E2 in subsets(extra & ~E1):
                    stats["n"] += 1
                    if g.sep(x, y, W, U1 | E2):
                        stats["viol"] += 1


def check_A():
    print("\n=== A: monotonicity over regimes ===", flush=True)
    rng = np.random.default_rng(SEED + 1)
    st = {"n": 0, "viol": 0}
    # exhaustive p=3: all DAGs on O, all parent sets of the indicators
    pairs = [(0, 1), (0, 2), (1, 2)]
    n_g = 0
    configs = list(itertools.product((0, 1, 2), repeat=3))
    parentsets = list(range(8))
    stride = 8 if QUICK else 1
    for cfg in configs[::1]:
        for ps in list(itertools.product(parentsets, repeat=3))[::stride]:
            g = MDag(3)
            for (a, b), c in zip(pairs, cfg):
                if c == 1:
                    g.add(a, b)
                elif c == 2:
                    g.add(b, a)
            if (cfg == (1, 2, 1)) or (cfg == (2, 1, 2)):
                continue            # the two directed cycles
            for i, pm in enumerate(ps):
                g.pa[g.R(i)] = pm
            lemma_A(g, st)
            n_g += 1
    print(f"exhaustive p=3: {n_g} m-DAGs, {st['n']} checks, {st['viol']} violations", flush=True)
    st2 = {"n": 0, "viol": 0}
    for _ in range(300 if QUICK else 3000):
        lemma_A(random_mdag(4, rng.choice([.3, .5, .7]), rng.choice([.1, .3, .6]), .5, .5, rng, .3), st2)
    print(f"random p=4 with latents: {st2['n']} checks, {st2['viol']} violations", flush=True)
    # control: break Assumption 1 by letting an indicator cause an observed variable or another indicator
    st3 = {"n": 0, "viol": 0}
    example = None
    for _ in range(300 if QUICK else 2000):
        g = random_mdag(4, rng.choice([.3, .5]), rng.choice([.1, .3]), 0, 0, rng)
        i, j = rng.choice(4, 2, replace=False)
        if rng.random() < .5:
            g.add(g.R(int(i)), int(j))       # R_i -> O_j
        else:
            g.add(g.R(int(i)), g.R(int(j)))  # R_i -> R_j
        before = st3["viol"]
        lemma_A(g, st3)
        if st3["viol"] > before and example is None:
            example = list(g.pa)
    print(f"control (Assumption 1 broken): {st3['n']} checks, {st3['viol']} violations", flush=True)
    check("A.exhaustive p=3 has no violation", st["viol"] == 0, str(st))
    check("A.random p=4 has no violation", st2["viol"] == 0, str(st2))
    check("A.control finds violations, so the check can fail", st3["viol"] > 0, str(st3))
    results["A"] = {"exhaustive_p3": st, "random_p4": st2, "control_broken_assumption": st3}


# ---------------------------------------------------------------- R0, R1
def premises_at(g, x, y, z, W, U):
    """Lemma 3.1 premises at regime U: W minimal for (x,y), and x-z, y-z dependent given W minus z."""
    if not g.sep(x, y, W, U):
        return False
    for A in subsets(W):
        if A != W and g.sep(x, y, A, U):
            return False
    Wz = W & ~(1 << z)
    return not g.sep(x, z, Wz, U) and not g.sep(y, z, Wz, U)


def check_R():
    print("\n=== R0 and R1: indexed rules, naive composition ===", flush=True)
    rng = np.random.default_rng(SEED + 2)
    r0 = {"instances": 0, "viol": 0}
    r0n = {"instances": 0, "false_pure_claims": 0}
    r1 = {"instances": 0, "indexed_viol": 0, "naive_instances": 0, "naive_false": 0, "union_instances": 0, "union_viol": 0}
    ex_r0n, ex_r1 = None, None
    for gi in range(300 if QUICK else 2500):
        p = int(rng.choice([3, 4, 5]))
        g = random_mdag(p, rng.choice([.3, .5, .7]), rng.choice([.1, .3, .6]), .4, .4, rng, .2)
        full = (1 << p) - 1
        for x, y in itertools.combinations(range(p), 2):
            for z in range(p):
                if z in (x, y):
                    continue
                rest = full & ~(1 << x) & ~(1 << y)
                for W in subsets(rest):
                    base = (1 << x) | (1 << y) | (1 << z) | W
                    for E in subsets(full & ~base):
                        U = base | E
                        if not premises_at(g, x, y, z, W, U):
                            continue
                        r0["instances"] += 1
                        zin = bool((W >> z) & 1)
                        target = (1 << x) | (1 << y) | g.rmask(U)
                        if zin != g.in_an(z, target):
                            r0["viol"] += 1
                    # naive R0: separation in {x,y}+W, dependences each in their own smallest regime, z not in W
                    if not (W >> z) & 1:
                        Uxy = (1 << x) | (1 << y) | W
                        if g.sep(x, y, W, Uxy) and all(not g.sep(x, y, A, (1 << x) | (1 << y) | A) for A in subsets(W) if A != W) \
                                and not g.sep(x, z, W, (1 << x) | (1 << z) | W) and not g.sep(y, z, W, (1 << y) | (1 << z) | W):
                            r0n["instances"] += 1
                            if g.in_an(z, (1 << x) | (1 << y)):
                                r0n["false_pure_claims"] += 1
                                if ex_r0n is None or sum(bin(v).count("1") for v in g.pa) < ex_r0n[0]:
                                    ex_r0n = (sum(bin(v).count("1") for v in g.pa), p, list(g.pa), x, y, z, W)
        # R1: arrow premise from regime U1 taken as a true statement about the DAG, separation premise at U2
        if p >= 4 or gi % 3 == 0:
            for x, y in itertools.permutations(range(p), 2):
                for z in range(p):
                    if z in (x, y) or not g.obs_edge(x, z) and g.sep(x, z, 0, (1 << x) | (1 << z)):
                        continue
                    rest = full & ~(1 << x) & ~(1 << y)
                    for W in subsets(rest):
                        if not (W >> z) & 1:
                            continue
                        U2 = (1 << x) | (1 << y) | W
                        if not premises_at(g, x, y, z, W, U2):
                            continue
                        for U1 in subsets(full):
                            if not ((U1 >> x) & 1 and (U1 >> z) & 1):
                                continue
                            if g.in_an(z, (1 << x) | g.rmask(U1)):
                                continue            # the arrow premise z not in An(x + R_U1) must hold
                            r1["instances"] += 1
                            extra = g.rmask(U2 & ~U1)
                            if not g.in_an(z, (1 << y) | extra):
                                r1["indexed_viol"] += 1
                            if U2 & ~U1:
                                r1["naive_instances"] += 1
                                if not g.in_an(z, 1 << y):
                                    r1["naive_false"] += 1
                                    c = sum(bin(v).count("1") for v in g.pa)
                                    if ex_r1 is None or c < ex_r1[0]:
                                        ex_r1 = (c, p, list(g.pa), x, y, z, W, U1, U2)
                            else:
                                r1["union_instances"] += 1
                                if not g.in_an(z, 1 << y):
                                    r1["union_viol"] += 1
    print("R0 indexed:", r0, "| naive R0:", r0n, flush=True)
    print("R1:", r1, flush=True)

    def show(ex):
        return None if ex is None else {"p": ex[1], "parents": {v: list(bits(m)) for v, m in enumerate(ex[2]) if m}, "rest": ex[3:]}

    print("smallest naive R0 false claim found:", show(ex_r0n), flush=True)
    print("smallest naive R1 false claim found:", show(ex_r1), flush=True)
    check("R0.indexed has no violation", r0["viol"] == 0 and r0["instances"] > 0, str(r0))
    check("R0.naive produces false pure claims", r0n["false_pure_claims"] > 0, str(r0n))
    check("R1.indexed has no violation", r1["indexed_viol"] == 0 and r1["instances"] > 0, str(r1["instances"]))
    check("R1.same-regime pure conclusion has no violation", r1["union_viol"] == 0 and r1["union_instances"] > 0, str(r1["union_instances"]))
    check("R1.naive pure conclusion is sometimes false", r1["naive_false"] > 0, str(r1["naive_false"]))
    results["R"] = {"R0": r0, "R0_naive": r0n, "R1": r1, "example_naive_R0": show(ex_r0n), "example_naive_R1": show(ex_r1)}


# ---------------------------------------------------------------- mini FCI, R0-R4
class Pag:
    def __init__(self, vars_):
        self.vars = list(vars_)
        self.adj = {v: set() for v in vars_}
        self.m = {}          # m[(a,b)] = mark at b on edge a-b: 'o', '>', '-'
        self.sep = {}

    def edge(self, a, b):
        self.adj[a].add(b)
        self.adj[b].add(a)
        self.m[(a, b)] = "o"
        self.m[(b, a)] = "o"

    def un(self, a, b):
        self.adj[a].discard(b)
        self.adj[b].discard(a)


def fci(vars_, indep, forbid=(), arrow_into=None):
    """indep(x, y, Wtuple) -> bool. Exhaustive separating sets, smallest first (so found sets are minimal among subsets tried).
    Optional, used only by T4L_baseline_oracle_check.py: forbid = pairs nonadjacent by assumption with an unknown separating set (no R0 or R4 from them);
    arrow_into(b) = True if every edge into b has a known arrowhead at b, applied before R0."""
    P = Pag(vars_)
    for a, b in itertools.combinations(vars_, 2):
        P.edge(a, b)
    forbid = {frozenset(pr) for pr in forbid}
    for a, b in itertools.combinations(vars_, 2):
        if frozenset((a, b)) in forbid:
            P.un(a, b)
            P.sep[(a, b)] = P.sep[(b, a)] = None
            continue
        others = [v for v in vars_ if v not in (a, b)]
        done = False
        for k in range(len(others) + 1):
            for W in itertools.combinations(others, k):
                if indep(a, b, W):
                    P.un(a, b)
                    P.sep[(a, b)] = P.sep[(b, a)] = set(W)
                    done = True
                    break
            if done:
                break
    if arrow_into is not None:
        for b in vars_:
            if arrow_into(b):
                for a in P.adj[b]:
                    P.m[(a, b)] = ">"
    for z in vars_:
        for x, y in itertools.combinations(sorted(P.adj[z]), 2):
            if y not in P.adj[x] and P.sep[(x, y)] is not None and z not in P.sep[(x, y)]:
                P.m[(x, z)] = ">"
                P.m[(y, z)] = ">"
    changed = True
    while changed:
        changed = False
        for b in vars_:
            for a in P.adj[b]:
                if P.m[(a, b)] != ">":
                    continue
                for c in P.adj[b]:
                    if c == a or c in P.adj[a]:
                        continue
                    if P.m[(c, b)] == "o":                     # R1
                        P.m[(c, b)] = "-"
                        P.m[(b, c)] = ">"
                        changed = True
        for a in vars_:
            for c in P.adj[a]:
                if P.m[(a, c)] != "o":
                    continue
                for b in P.adj[a] & P.adj[c]:                  # R2
                    ab_dir = P.m[(a, b)] == ">" and P.m[(b, a)] == "-"
                    bc_dir = P.m[(b, c)] == ">" and P.m[(c, b)] == "-"
                    if (ab_dir and P.m[(b, c)] == ">") or (P.m[(a, b)] == ">" and bc_dir):
                        P.m[(a, c)] = ">"
                        changed = True
                        break
        for b in vars_:
            nb = sorted(P.adj[b])
            for a, c in itertools.combinations(nb, 2):         # R3
                if c in P.adj[a] or P.m[(a, b)] != ">" or P.m[(c, b)] != ">":
                    continue
                for d in P.adj[b]:
                    if d in (a, c) or P.m[(d, b)] != "o":
                        continue
                    if d in P.adj[a] and d in P.adj[c] and P.m[(a, d)] == "o" and P.m[(c, d)] == "o":
                        P.m[(d, b)] = ">"
                        changed = True
        # R4: discriminating path <u, ..., a, b, c>
        for b in vars_:
            for c in P.adj[b]:
                if P.m[(c, b)] != "o":
                    continue
                for a in P.adj[b] & P.adj[c]:
                    if not (P.m[(b, a)] == ">" and P.m[(a, c)] == ">" and P.m[(c, a)] == "-"):
                        continue
                    stack = [(a, [b, a])]
                    fired = False
                    while stack and not fired:
                        cur, path = stack.pop()
                        for u in P.adj[cur]:
                            if u in path or u == c or P.m[(u, cur)] != ">":
                                continue
                            if u not in P.adj[c]:
                                if P.sep.get((u, c)) is not None:
                                    if b in P.sep[(u, c)]:
                                        P.m[(c, b)] = "-"
                                        P.m[(b, c)] = ">"
                                    else:
                                        P.m[(a, b)] = ">"
                                        P.m[(b, a)] = ">"
                                        P.m[(c, b)] = ">"
                                        P.m[(b, c)] = ">"
                                    changed = True
                                    fired = True
                                    break
                            elif P.m[(cur, u)] == ">" and P.m[(u, c)] == ">" and P.m[(c, u)] == "-":
                                stack.append((u, path + [u]))
                    if fired:
                        break
    return P


def claims(P):
    """Causal claims that hold for the DAG whatever the regime of a sound run: no direct edge, non-ancestor, pure ancestor."""
    ne, na, a = set(), set(), set()
    for x, y in itertools.combinations(P.vars, 2):
        if y not in P.adj[x]:
            ne.add((x, y))
    for z in P.vars:
        # Sound with selection: if z is a DAG ancestor of x, consecutive observed nodes on the directed path are adjacent in the MAG (the indicators are childless, so
        # never on the path), and each has no arrowhead on the edge to the next. So: no path with non-arrow marks at each source means z is not an ancestor of x.
        seen = {z}
        fr = [z]
        while fr:
            a_ = fr.pop()
            for b_ in P.adj[a_]:
                if b_ not in seen and P.m[(b_, a_)] != ">":
                    seen.add(b_)
                    fr.append(b_)
        for x in P.vars:
            if x not in seen:
                na.add((z, x))
    for (u, v), mk in P.m.items():
        if v in P.adj[u] and mk == "-":
            # tail at v on the edge u-v: v in An(u + selection). Pure if v has an arrowhead on another edge in this PAG.
            if any(P.m[(w, v)] == ">" for w in P.adj[v] if w != u):
                a.add((v, u))
    return ne, na, a


def closure(a, vars_):
    a = set(a)
    changed = True
    while changed:
        changed = False
        for (x, y), (y2, z) in itertools.product(list(a), list(a)):
            if y == y2 and x != z and (x, z) not in a:
                a.add((x, z))
                changed = True
    return a


def score(g, ne, na, a):
    true_c = false_c = 0
    fals = []
    for x, y in ne:
        if g.obs_edge(x, y):
            false_c += 1
            fals.append(("NE", x, y))
        else:
            true_c += 1
    for z, x in na:
        if g.in_an(z, 1 << x):
            false_c += 1
            fals.append(("NA", z, x))
        else:
            true_c += 1
    for z, y in a:
        if g.in_an(z, 1 << y):
            true_c += 1
        else:
            false_c += 1
            fals.append(("A", z, y))
    return true_c, false_c, fals


def run_methods(g):
    p = g.p
    O = list(range(p))
    full = (1 << p) - 1

    def m(W):
        return sum(1 << v for v in W)

    def union(regime_of):
        ne_all, na_all, a_all = set(), set(), set()
        size_of = {}
        for size in range(2, p + 1):
            for Uv in itertools.combinations(O, size):
                reg = regime_of(m(Uv))
                P = fci(list(Uv), reg)
                ne, na, a = claims(P)
                for kind, s_, store in (("NE", ne, ne_all), ("NA", na, na_all), ("A", a, a_all)):
                    for c in s_:
                        store.add(c)
                        size_of.setdefault((kind,) + tuple(c), size)
        return ne_all, na_all, closure(a_all, O), size_of

    def tag(ne, na, a):
        return {("NE",) + tuple(c) for c in ne} | {("NA",) + tuple(c) for c in na} | {("A",) + tuple(c) for c in a}

    def at_regime(Um):
        return lambda x, y, W: g.sep(x, y, m(W), Um)

    LW = claims(fci(O, at_regime(full)))
    LW = (LW[0], LW[1], closure(LW[2], O))
    sep_ne, sep_na = set(), set()
    for x, y in itertools.combinations(O, 2):
        pair = (1 << x) | (1 << y)
        if g.sep(x, y, 0, pair):
            sep_na.add((x, y))
            sep_na.add((y, x))
        for W in subsets(full & ~pair):
            if g.sep(x, y, W, pair | W):
                sep_ne.add((x, y))
                break
    nv = claims(fci(O, lambda x, y, W: g.sep(x, y, m(W), (1 << x) | (1 << y) | m(W))))
    nv = (nv[0], nv[1], closure(nv[2], O))
    LWu = union(lambda Um: at_regime(full))
    PP = union(at_regime)
    ID = union(lambda Um: (lambda x, y, W: g.dsep_raw(x, y, m(W))))
    SO = (LWu[0] | sep_ne, LWu[1] | sep_na, LWu[2])
    sz = PP[3]
    def by_size(kind, store, cap):
        return {c for c in store if sz.get((kind,) + tuple(c), 99) <= cap}
    PP3 = (LWu[0] | by_size("NE", PP[0], 3), LWu[1] | by_size("NA", PP[1], 3), closure(LWu[2] | by_size("A", PP[2], 3), O))
    out = {"LW": score(g, *LW), "Naive": score(g, *nv), "LWu": score(g, *LWu[:3]), "SepOnly": score(g, *SO), "PP3": score(g, *PP3), "PP": score(g, *PP[:3]), "IdealU": score(g, *ID[:3])}
    lwu_set, pp_set = tag(*LWu[:3]), tag(*PP[:3])
    so_set = tag(*SO)
    new = pp_set - lwu_set
    beyond = pp_set - so_set
    lw_sizes = [sz[c] for c in lwu_set if c in sz]
    new_sizes = [sz[c] for c in new if c in sz]
    info = {"lwu_not_in_pp": len(lwu_set - pp_set), "new_total": len(new),
            "new_NE": sum(c[0] == "NE" for c in new), "new_NA": sum(c[0] == "NA" for c in new), "new_A": sum(c[0] == "A" for c in new),
            "new_from_U_le_3": sum(s <= 3 for s in new_sizes), "n_new_sized": len(new_sizes),
            "sum_min_U_lwu_claims": sum(lw_sizes), "n_lwu_sized": len(lw_sizes),
            "pp_same_as_lwu": pp_set == lwu_set, "so_not_in_pp": len(so_set - pp_set), "beyond_sep_total": len(beyond),
            "beyond_NA": sum(c[0] == "NA" for c in beyond), "beyond_A": sum(c[0] == "A" for c in beyond), "beyond_NE": sum(c[0] == "NE" for c in beyond)}
    return out, info


def path_seq_premises(g, seq, S_ik, Ua1):
    """Lemma 3.2 (a1), (a2) for seq = <Xi, ..., Xl, Xj, Xk>; a2 is tested in the smallest regime of each query, a1 at Ua1."""
    xi, xk = seq[0], seq[-1]
    if not g.sep(xi, xk, S_ik, Ua1):
        return False
    for a, b in zip(seq, seq[1:]):
        pair = (1 << a) | (1 << b)
        for Y in subsets(S_ik):
            W = Y & ~pair
            if g.sep(a, b, W, pair | W):
                return False
    return True


def a3_at(g, seq, Ua):
    xk = seq[-1]
    for h in range(1, len(seq) - 2):
        if not g.in_an(seq[h], 1 << xk):
            return False
        if g.in_an(seq[h], (1 << seq[h - 1]) | (1 << seq[h + 1]) | g.rmask(Ua)):
            return False
    return True


def check_R4():
    print("\n=== R4: Colombo Lemma 3.2 at a regime, dependence premises from sub-regimes ===", flush=True)
    rng = np.random.default_rng(SEED + 4)
    st = {"instances": 0, "viol": 0, "b1": 0, "b2": 0, "naive_instances": 0, "naive_false": 0}
    ex = None
    n_rand = 200 if QUICK else 2500
    n_tgt = 200 if QUICK else 2500
    for it in range(n_rand + n_tgt):
        if it < n_rand:
            p = int(rng.choice([4, 5]))
            g = random_mdag(p, rng.choice([.5, .7, .85]), rng.choice([.1, .3]), .6, .3, rng)
        else:
            # i -> l <-> j, l -> k, and j -> k (b1) or j <-> k (b2); indicators random; optional fifth variable
            p = int(rng.choice([4, 5]))
            perm = [int(v) for v in rng.permutation(p)]
            i_, l_, j_, k_ = perm[:4]
            q_ = float(rng.choice([.05, .1, .2, .3]))
            g = MDag(p, 2)
            g.add(i_, l_)
            g.add(l_, k_)
            g.add(2 * p, l_)
            g.add(2 * p, j_)
            if rng.random() < .5:
                g.add(j_, k_)
            else:
                g.add(2 * p + 1, j_)
                g.add(2 * p + 1, k_)
            if p == 5 and rng.random() < .5:
                g.add(perm[4], k_)
            for r_ in range(p):
                for u_ in range(p):
                    if rng.random() < q_:
                        g.add(u_, g.R(r_))
        full = (1 << p) - 1
        for L in range(4, p + 1):
            for seq in itertools.permutations(range(p), L):
                rest = full & ~(1 << seq[0]) & ~(1 << seq[-1])
                Upath = sum(1 << v for v in seq)
                for Sik in subsets(rest):
                    U = Upath | Sik
                    xj, xl, xk = seq[-2], seq[-3], seq[-1]
                    if path_seq_premises(g, seq, Sik, U) and a3_at(g, seq, U):
                        st["instances"] += 1
                        R = g.rmask(U)
                        if (Sik >> xj) & 1:
                            st["b1"] += 1
                            ok = g.in_an(xj, (1 << xk) | R) and not g.in_an(xk, (1 << xj) | R)
                        else:
                            st["b2"] += 1
                            ok = not g.in_an(xj, (1 << xl) | (1 << xk) | R) and not g.in_an(xk, (1 << xj) | R)
                        st["viol"] += not ok
                    # naive: separation and arrow premises each read in their own smallest regime, conclusion stated without indicators
                    Unaive = (1 << seq[0]) | (1 << seq[-1]) | Sik
                    if path_seq_premises(g, seq, Sik, Unaive) and a3_at(g, seq, Upath):
                        st["naive_instances"] += 1
                        if (Sik >> xj) & 1:
                            ok = g.in_an(xj, 1 << xk) and not g.in_an(xk, 1 << xj)
                        else:
                            ok = not g.in_an(xj, (1 << xl) | (1 << xk)) and not g.in_an(xk, 1 << xj)
                        if not ok:
                            st["naive_false"] += 1
                            if ex is None:
                                ex = {"p": p, "parents": {v: list(bits(m)) for v, m in enumerate(g.pa) if m}, "seq": seq, "Sik": list(bits(Sik))}
    print(st, flush=True)
    print("first naive R4 false claim:", ex, flush=True)
    check("R4.indexed has no violation", st["viol"] == 0, str(st))
    check("R4.indexed has instances, so the check is not vacuous", st["instances"] > 0, str(st["instances"]))
    results["R4"] = {**st, "example_naive": ex}


def check_S():
    print("\n=== S: same-target impossibility, explicit pairs; explicit naive failure ===", flush=True)

    def build(p, edges, n_extra=0):
        g = MDag(p, n_extra)
        for u, v in edges:
            g.add(u, v)
        return g

    # Pair 1: X=0 -> Z=2 <- Y=1, T=3 isolated. g2 adds Z -> R_T.
    g1 = build(4, [(0, 2), (1, 2)])
    g2 = build(4, [(0, 2), (1, 2), (2, g1.R(3))])
    p = 4
    full = 15
    diffs_out, diffs_lw = 0, 0
    for x, y in itertools.combinations(range(p), 2):
        rest = full & ~(1 << x) & ~(1 << y)
        for W in subsets(rest):
            base = (1 << x) | (1 << y) | W
            for E in subsets(full & ~base):
                U = base | E
                d = g1.sep(x, y, W, U) != g2.sep(x, y, W, U)
                if U >> 3 & 1:
                    diffs_lw += d
                else:
                    diffs_out += d
    check("S.pair1: no query in a regime without T differs", diffs_out == 0, str(diffs_out))
    check("S.pair1: some query in a regime with T differs", diffs_lw > 0, str(diffs_lw))
    m = lambda W: sum(1 << v for v in W)
    P1 = fci([0, 1, 2, 3], lambda x, y, W: g1.sep(x, y, m(W), full))
    P2 = fci([0, 1, 2, 3], lambda x, y, W: g2.sep(x, y, m(W), full))
    check("S.pair1: listwise skeleton differs (selection-induced edge X-Y)", (1 in P2.adj[0]) and (1 not in P1.adj[0]))
    Pl = fci([0, 1, 2], lambda x, y, W: g2.sep(x, y, m(W), 0b0111))
    cl = claims(Pl)
    check("S.pair1: regime XYZ on g2 keeps the true v-structure claims", (2, 0) in cl[1] and (2, 1) in cl[1] and not g2.in_an(2, 1 << 0) and not g2.in_an(2, 1 << 1), str(cl[1]))
    # Pair 2: the difference needs two extra indicators together: X -> R_T1 <- L -> R_T2 <- Y
    g3 = build(4, [])
    g4 = build(4, [(0, 4 + 2), (1, 4 + 3), (8, 4 + 2), (8, 4 + 3)], 1)
    single, both = 0, None
    for E in subsets(0b1100):
        U = 0b0011 | E
        s = g4.sep(0, 1, 0, U)
        if E != 0b1100:
            single += not s
        else:
            both = not s
    check("S.pair2: X,Y separated unless both R_T1 and R_T2 are conditioned on", single == 0 and both is True, f"{single}, {both}")
    # Explicit naive failure: Z -> X, Y isolated, R_Z has parents Y, Z (p=3)
    g5 = build(3, [(2, 0), (1, 3 + 2), (2, 3 + 2)])
    Nv = fci([0, 1, 2], lambda x, y, W: g5.sep(x, y, m(W), (1 << x) | (1 << y) | m(W)))
    ne, na, a = claims(Nv)
    t, f, fl = score(g5, ne, na, a)
    Lw = fci([0, 1, 2], lambda x, y, W: g5.sep(x, y, m(W), 7))
    t2, f2, fl2 = score(g5, *claims(Lw))
    check("S.explicit: naive test-wise FCI asserts a false non-ancestor claim", f > 0, str(fl))
    check("S.explicit: listwise FCI asserts nothing false on the same graph", f2 == 0, str(fl2))
    results["S"] = {"pair1": "X->Z<-Y, T isolated; second DAG adds Z->R_T", "pair2": "X->R_T1<-L->R_T2<-Y", "explicit_naive": {"graph": "Z->X, Y isolated, R_Z parents Y,Z", "false_claims": fl, "listwise_false": fl2}}


def check_H():
    print("\n=== H: oracle headroom on random m-DAGs ===", flush=True)
    rng = np.random.default_rng(SEED + 3)
    rows = []
    t00 = time.time()
    keys = ("LW", "Naive", "LWu", "SepOnly", "PP3", "PP", "IdealU")
    control_ok = True
    for p, Ng in ((4, 40 if QUICK else 500), (5, 20 if QUICK else 200), (6, 6 if QUICK else 50)):
        for dens, q, cr in itertools.product((.3, .5), (0.0, .1, .3, .6), (0.0, .5)):
            agg = {k: [] for k in keys}
            bad = dict.fromkeys(keys, 0)
            nfalse = dict.fromkeys(keys, 0)
            more = dict.fromkeys(("lwu_not_in_pp", "new_total", "new_NE", "new_NA", "new_A", "new_from_U_le_3", "n_new_sized", "sum_min_U_lwu_claims", "n_lwu_sized", "so_not_in_pp", "beyond_sep_total", "beyond_NA", "beyond_A", "beyond_NE"), 0)
            ex = None
            t0 = time.time()
            for _ in range(Ng):
                g = random_mdag(p, dens, q, .5, cr, rng)
                out, info = run_methods(g)
                for k in keys:
                    agg[k].append(out[k][0])
                    bad[k] += out[k][1] > 0
                    nfalse[k] += out[k][1]
                    if k != "Naive" and out[k][1] > 0 and ex is None:
                        ex = (k, list(g.pa), out[k][2])
                for k in more:
                    more[k] += info[k]
                if q == 0 and not info["pp_same_as_lwu"]:
                    control_ok = False
            mean = {k: float(np.mean(agg[k])) for k in keys}
            row = {"p": p, "density": dens, "q": q, "latent_among_R": cr, "graphs": Ng, "true_claims": mean, "graphs_with_false_claim": dict(bad), "false_claims_total": dict(nfalse),
                   "ratio_PP_LWu": mean["PP"] / max(mean["LWu"], 1e-9), "ratio_LWu_LW": mean["LWu"] / max(mean["LW"], 1e-9), "ratio_PP_SepOnly": mean["PP"] / max(mean["SepOnly"], 1e-9),
                   "ratio_PP3_SepOnly": mean["PP3"] / max(mean["SepOnly"], 1e-9),
                   "beyond_sep_per_graph": {k: more[k] / Ng for k in ("beyond_sep_total", "beyond_NA", "beyond_A", "beyond_NE", "so_not_in_pp")},
                   "frac_graphs_PP_gt_SepOnly": float(np.mean(np.array(agg["PP"]) > np.array(agg["SepOnly"]))),
                   "gap_closed": (mean["PP"] - mean["LWu"]) / max(mean["IdealU"] - mean["LWu"], 1e-9),
                   "frac_graphs_PP_gt_LWu": float(np.mean(np.array(agg["PP"]) > np.array(agg["LWu"]))),
                   "new_per_graph": {k: more[k] / Ng for k in ("new_total", "new_NE", "new_NA", "new_A", "lwu_not_in_pp")},
                   "frac_new_from_U_le_3": more["new_from_U_le_3"] / max(more["n_new_sized"], 1),
                   "mean_min_U_of_LWu_claims": more["sum_min_U_lwu_claims"] / max(more["n_lwu_sized"], 1), "example_false": ex, "seconds": time.time() - t0}
            rows.append(row)
            print(f"H p={p} d={dens} q={q} Rc={cr}: LW={mean['LW']:.2f} LWu={mean['LWu']:.2f} Sep={mean['SepOnly']:.2f} PP3={mean['PP3']:.2f} PP={mean['PP']:.2f} Naive={mean['Naive']:.2f} IdealU={mean['IdealU']:.2f} | PP/LWu={row['ratio_PP_LWu']:.3f} PP/Sep={row['ratio_PP_SepOnly']:.3f} gap={row['gap_closed']:.2f} PP>Sep in {row['frac_graphs_PP_gt_SepOnly']:.2f} beyondNA/A {row['beyond_sep_per_graph']['beyond_NA']:.2f}/{row['beyond_sep_per_graph']['beyond_A']:.2f} soLost {row['beyond_sep_per_graph']['so_not_in_pp']:.2f} | false graphs {bad} naive false claims {nfalse['Naive']} | new NE/NA/A {row['new_per_graph']['new_NE']:.2f}/{row['new_per_graph']['new_NA']:.2f}/{row['new_per_graph']['new_A']:.2f} lost {row['new_per_graph']['lwu_not_in_pp']:.2f} U<=3 {row['frac_new_from_U_le_3']:.2f} minU {row['mean_min_U_of_LWu_claims']:.2f} | {row['seconds']:.0f}s", flush=True)
            if not QUICK:
                results["H"] = {"rows": rows, "partial": True}
                (HERE / "T4_oracle_outputs.json").write_text(json.dumps(results, indent=1, default=str), encoding="utf-8")
    for k in ("PP", "PP3", "SepOnly", "LWu", "LW", "IdealU"):
        tot = sum(r["graphs_with_false_claim"][k] for r in rows)
        check(f"H.{k} has no false claim", tot == 0, str(tot))
    check("H.K5 control: PP equals LWu on every graph with q = 0", control_ok)
    nv_false = sum(r["graphs_with_false_claim"]["Naive"] for r in rows)
    print(f"graphs where naive test-wise has a false claim: {nv_false}", flush=True)
    mnar = [r for r in rows if r["q"] in (.1, .3)]
    best = max(r["ratio_PP_LWu"] for r in mnar)
    verdict = "worth a finite-sample pilot" if best >= 1.10 else ("no-go on claims" if best < 1.05 else "weak")
    print(f"K3 verdict by the declared rule: best MNAR PP/LWu {best:.3f} -> {verdict}; cells at or above 1.10: {sum(r['ratio_PP_LWu'] >= 1.10 for r in mnar)}/{len(mnar)}; runtime {time.time() - t00:.0f}s", flush=True)
    best6 = max(r["ratio_PP_SepOnly"] for r in mnar)
    v6 = "orientation transport worth a pilot" if best6 >= 1.10 else ("no-go on orientation" if best6 < 1.05 else "weak")
    print(f"K6 verdict by the declared rule: best MNAR PP/SepOnly {best6:.3f} -> {v6}; cells at or above 1.10: {sum(r['ratio_PP_SepOnly'] >= 1.10 for r in mnar)}/{len(mnar)}", flush=True)
    results["H"] = {"rows": rows, "best_MNAR_ratio": best, "K3_verdict": verdict, "cells_ge_110": sum(r["ratio_PP_LWu"] >= 1.10 for r in mnar), "cells": len(mnar),
                    "best_MNAR_ratio_PP_SepOnly": best6, "K6_verdict": v6, "cells_K6_ge_110": sum(r["ratio_PP_SepOnly"] >= 1.10 for r in mnar)}


if __name__ == "__main__":
    t0 = time.time()
    check_A()
    check_R()
    check_R4()
    check_S()
    check_H()
    results["meta"].update({"runtime_sec": time.time() - t0, "n_pass": n_pass, "failed": failures})
    if not QUICK:
        (HERE / "T4_oracle_outputs.json").write_text(json.dumps(results, indent=1, default=str), encoding="utf-8")
    print(f"runtime {time.time() - t0:.1f}s PASS={n_pass} FAIL={len(failures)}")
    for f in failures:
        print("  FAILED:", f)
