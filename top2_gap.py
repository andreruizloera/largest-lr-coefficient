#!/usr/bin/env python3
"""top2_gap.py — data for the Pak-Soskin Prop 4.1 uniqueness-heuristic
addendum: for each n, the largest and second-largest values over terminal
classes, and their ratio. Reuses maxlr.py's machinery; pass 2 only (no
suspect scan), so ~half the full runtime.

Usage: python3 top2_gap.py N [N2 ...]
"""

import sys
import time

sys.path.insert(0, ".")
from maxlr import partitions, terminal, halves, maxcoeff


def top2(n):
    t0 = time.time()
    seen = set()
    for w in partitions(n):
        seen.add(terminal(w))
    # the informative quantity for the Prop 4.1 heuristic is the largest
    # terminal-class value STRICTLY below C(n); several classes may attain
    # C(n) itself (they collapse to one maximal orbit in the suspect pass)
    best, second_strict, n_attain = 0, 0, 0
    for wstar in seen:
        lo, hi = halves(wstar)
        val, _ = maxcoeff(lo, hi)
        if val > best:
            second_strict = best
            best, n_attain = val, 1
        elif val == best:
            n_attain += 1
        elif val > second_strict:
            second_strict = val
    ratio = best / second_strict if second_strict else float("inf")
    print(f"n={n}: C(n)={best} ({n_attain} classes attain)  "
          f"largest-below={second_strict}  ratio={ratio:.4f}  "
          f"classes={len(seen)}  [{time.time()-t0:.0f}s]", flush=True)
    return best, second_strict


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        top2(int(arg))
