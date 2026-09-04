#!/usr/bin/env python3
"""bruteforce_gate.py — validate the compression method against exhaustive
search on the degrees where exhaustive search is still cheap.

For each n in the given range this computes, by brute force over EVERY pair
(mu |- k, nu |- n-k) with k <= n/2:

  * C(n) itself, and
  * the complete list of maximal triples (lam, mu, nu) with c^lam_{mu,nu} = C(n),

and compares both against what maxlr.py's three-pass compression method
returns. The second comparison is the one that matters: it is a direct test of
the completeness claim behind pass 3, namely that every maximal pair sits over
a terminal class attaining C(n), so that the suspect scan misses nothing.

Usage: python3 bruteforce_gate.py NLO NHI
"""

import sys
import time

import lrcalc

from maxlr import partitions, run, is_square_union, conj


def brute(n):
    """(C(n), sorted list of all maximal triples with |mu| <= |nu|)."""
    best = 0
    triples = []
    for k in range(0, n // 2 + 1):
        for mu in partitions(k):
            for nu in partitions(n - k):
                prod = lrcalc.mult(mu, nu)
                if not prod:
                    continue
                loc = max(prod.values())
                if loc < best:
                    continue
                if loc > best:
                    best = loc
                    triples = []
                for lam, c in prod.items():
                    if c == best:
                        triples.append((lam, mu, nu))
    triples = sorted(t for t in triples
                     if lrcalc.mult(t[1], t[2]).get(t[0], 0) == best)
    return best, triples


def canon_orbits(triples):
    out = set()
    for lam, mu, nu in triples:
        orbit = set()
        for (l, m, v) in [(lam, mu, nu), (lam, nu, mu)]:
            orbit.add((l, m, v))
            orbit.add((conj(l), conj(m), conj(v)))
            orbit.add((conj(l), conj(v), conj(m)))
        out.add(min(orbit))
    return out


def main(lo, hi):
    allok = True
    for n in range(lo, hi + 1):
        t0 = time.time()
        bC, btr = brute(n)
        t1 = time.time()
        mC, mtr, part1, part2 = run(n, verbose=False)
        t2 = time.time()
        mtr = sorted(set(mtr))
        btr = sorted(set(btr))
        ok_val = bC == mC
        ok_set = btr == mtr
        bp1 = all(is_square_union(mu, nu) or is_square_union(nu, mu)
                  for _, mu, nu in btr)
        bp2 = len(canon_orbits(btr)) == 1
        allok = allok and ok_val and ok_set and bp1 == part1 and bp2 == part2
        print(f"n={n}: brute C={bC} [{t1-t0:.1f}s]  compressed C={mC} "
              f"[{t2-t1:.1f}s]  values agree={ok_val}  "
              f"maximal-triple SETS agree={ok_set} "
              f"({len(btr)} brute vs {len(mtr)} compressed)  "
              f"part1 {bp1}/{part1}  part2 {bp2}/{part2}", flush=True)
        if not ok_set:
            print("   brute only:", [t for t in btr if t not in mtr][:5], flush=True)
            print("   compressed only:", [t for t in mtr if t not in btr][:5], flush=True)
    print("ALL GATES PASS" if allok else "GATE FAILURE")
    return 0 if allok else 1


if __name__ == "__main__":
    a = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    b = int(sys.argv[2]) if len(sys.argv) > 2 else 26
    sys.exit(main(a, b))
