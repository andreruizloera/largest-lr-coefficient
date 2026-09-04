#!/usr/bin/env python3
"""
maxlr.py — compute C(n) = max Littlewood-Richardson coefficient over
|mu| + |nu| = n, and verify Pak-Soskin Conjecture 1.1 (arXiv:2608.03281),
via Okounkov-inequality compression.

Method. Okounkov's inequality (LPP 2007, Thm 11) gives, pointwise in lambda:
    c^lam_{mu,nu} <= c^lam_{floor((mu+nu)/2), ceil((mu+nu)/2)}
and LR coefficients are invariant under simultaneous conjugation.
The averaged pair depends only on the pointwise sum w = mu + nu (a partition
of n), so define on sum-vectors the step
    w  ->  conj(floor(w/2)) + conj(ceil(w/2))
and iterate until a sum-vector repeats; the terminal pair
    (floor(w*/2), ceil(w*/2))
dominates max_lam c^lam_{mu,nu} for EVERY pair (mu,nu) with mu+nu = w.
Hence
    C(n) = max over w |- n of maxcoeff( s_{floor(w*/2)} * s_{ceil(w*/2)} )
and the expensive LR expansions run over the (small) set of distinct terminal
pairs instead of all p(k)p(n-k) pairs (the bottleneck in arXiv:2608.03281,
where n = 45 took 20 hours on 32 cores).

Verification of Conjecture 1.1 (every maximum is nested with nu/mu a disjoint
union of squares; for n >= 28 unique up to transposition + conjugation): any
maximal pair's sum-vector must compress to a terminal pair attaining C(n), so
it suffices to expand the decompositions (mu, nu) of the few sum-vectors whose
terminal pair attains C(n).

Usage: python3 maxlr.py N [N2 ...]
"""

import sys
import time
from functools import lru_cache

import lrcalc


# ---------------------------------------------------------------- partitions

def partitions(n, maxpart=None):
    """Generate partitions of n as weakly decreasing tuples."""
    if maxpart is None:
        maxpart = n
    if n == 0:
        yield ()
        return
    for first in range(min(n, maxpart), 0, -1):
        for rest in partitions(n - first, first):
            yield (first,) + rest


def conj(p):
    """Conjugate partition."""
    if not p:
        return ()
    m = p[0]
    return tuple(sum(1 for x in p if x >= j) for j in range(1, m + 1))


def strip(p):
    """Drop trailing zeros."""
    return tuple(x for x in p if x > 0)


def halves(w):
    """(floor(w/2), ceil(w/2)) pointwise, zeros stripped."""
    lo = strip(tuple(x // 2 for x in w))
    hi = strip(tuple((x + 1) // 2 for x in w))
    return lo, hi


def step(w):
    """Sum-vector transform: conj(floor(w/2)) + conj(ceil(w/2))."""
    lo, hi = halves(w)
    clo, chi = conj(lo), conj(hi)
    L = max(len(clo), len(chi))
    clo += (0,) * (L - len(clo))
    chi += (0,) * (L - len(chi))
    return strip(tuple(a + b for a, b in zip(clo, chi)))


@lru_cache(maxsize=None)
def terminal(w):
    """Iterate step() until a sum-vector repeats; return that sum-vector."""
    seen = {w}
    cur = w
    while True:
        nxt = step(cur)
        if nxt in seen:
            return nxt
        seen.add(nxt)
        cur = nxt


# ------------------------------------------------------- decompositions of w

def decompositions(w):
    """All (mu, nu) with mu, nu weakly decreasing, pointwise mu + nu = w,
    |mu| <= |nu|.  Recursive with feasibility pruning."""
    out = []
    n = sum(w)
    L = len(w)

    def rec(i, mu, nu, mu_prev, nu_prev):
        if i == L:
            m = sum(mu)
            if m * 2 <= n:
                out.append((strip(tuple(mu)), strip(tuple(nu))))
            return
        wi = w[i]
        lo = max(0, wi - nu_prev)
        hi = min(wi, mu_prev)
        for mi in range(hi, lo - 1, -1):
            mu.append(mi)
            nu.append(wi - mi)
            rec(i + 1, mu, nu, mi, wi - mi)
            mu.pop()
            nu.pop()

    rec(0, [], [], 10 ** 9, 10 ** 9)
    return out


# ------------------------------------------------------------- square check

def is_square_union(mu, nu):
    """mu subseteq nu and every edge-connected component of the skew shape
    nu/mu is a full c x c square (this makes diagonally touching unit boxes
    four separate squares, matching the n=40 example in arXiv:2608.03281)."""
    L = max(len(mu), len(nu))
    a = tuple(mu) + (0,) * (L - len(mu))
    b = tuple(nu) + (0,) * (L - len(nu))
    if any(x > y for x, y in zip(a, b)):
        return False
    # row i occupies columns [a[i], b[i]); split rows into edge-connected
    # components: consecutive nonempty rows whose column intervals overlap
    rows = [(i, a[i], b[i]) for i in range(L) if b[i] > a[i]]
    comp = []
    for i, lo, hi in rows:
        if comp and comp[-1][-1][0] == i - 1 and \
                max(lo, comp[-1][-1][1]) < min(hi, comp[-1][-1][2]):
            comp[-1].append((i, lo, hi))
        else:
            comp.append([(i, lo, hi)])
    for c in comp:
        width = c[0][2] - c[0][1]
        if len(c) != width:
            return False
        if any(lo != c[0][1] or hi != c[0][2] for _, lo, hi in c):
            return False
    return True


def maxcoeff(mu, nu):
    """Max LR coefficient in s_mu * s_nu, with the set of maximizing lambda."""
    prod = lrcalc.mult(mu, nu)
    if not prod:
        return 0, []
    best = max(prod.values())
    lams = [lam for lam, c in prod.items() if c == best]
    return best, lams


# --------------------------------------------------------------------- main

def run(n, verbose=True):
    t0 = time.time()

    # Pass 1: compress all sum-vectors
    images = {}  # terminal sum-vector -> list of source w
    for w in partitions(n):
        images.setdefault(terminal(w), []).append(w)
    t1 = time.time()
    if verbose:
        print(f"n={n}: p(n) sum-vectors compressed to {len(images)} "
              f"terminal classes  [{t1 - t0:.1f}s]")

    # Pass 2: expand terminal pairs
    Cn = 0
    winners = []  # terminal sum-vectors attaining Cn
    for i, wstar in enumerate(images):
        lo, hi = halves(wstar)
        best, _ = maxcoeff(lo, hi)
        if best > Cn:
            Cn = best
            winners = [wstar]
        elif best == Cn:
            winners.append(wstar)
    t2 = time.time()
    if verbose:
        print(f"n={n}: C(n) = {Cn} from terminal classes "
              f"({len(winners)} attain it)  [{t2 - t1:.1f}s]")

    # Pass 3: suspects = decompositions of any w compressing to a winner
    winner_set = set(winners)
    suspect_ws = [w for wstar in winners for w in images[wstar]]
    maximal_triples = []
    n_suspect_pairs = 0
    for w in suspect_ws:
        for mu, nu in decompositions(w):
            n_suspect_pairs += 1
            best, lams = maxcoeff(mu, nu)
            if best == Cn:
                for lam in lams:
                    maximal_triples.append((lam, mu, nu))
    t3 = time.time()
    if verbose:
        print(f"n={n}: checked {n_suspect_pairs} suspect pairs from "
              f"{len(suspect_ws)} sum-vectors; {len(maximal_triples)} maximal "
              f"triples  [{t3 - t2:.1f}s]")

    # Conjecture 1.1 part 1: every maximal triple square-union nested
    part1 = all(is_square_union(mu, nu) or is_square_union(nu, mu)
                for _, mu, nu in maximal_triples)

    # Conjecture 1.1 part 2: unique up to transposition + conjugation
    canon = set()
    for lam, mu, nu in maximal_triples:
        orbit = set()
        for (l, m, v) in [(lam, mu, nu), (lam, nu, mu)]:
            orbit.add((l, m, v))
            orbit.add((conj(l), conj(m), conj(v)))
            orbit.add((conj(l), conj(v), conj(m)))
        canon.add(min(orbit))
    part2 = len(canon) == 1

    if verbose:
        print(f"n={n}: C(n)={Cn}  conj part1 (all square-union): {part1}  "
              f"part2 (unique up to transp+conj): {part2} "
              f"[{len(canon)} orbit(s)]")
        for lam, mu, nu in maximal_triples[:6]:
            print(f"    lam={lam} mu={mu} nu={nu} "
                  f"square-union={is_square_union(mu, nu) or is_square_union(nu, mu)}")
        print(f"n={n}: total {time.time() - t0:.1f}s")
    return Cn, maximal_triples, part1, part2


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        run(int(arg))
        print()
