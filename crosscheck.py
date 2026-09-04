#!/usr/bin/env python3
"""crosscheck.py — independent verification of a single LR coefficient by
direct enumeration of Littlewood-Richardson skew tableaux (no lrcalc).

c^lam_{mu,nu} = number of semistandard fillings of lam/mu with content nu
whose reverse reading word (right-to-left, top-to-bottom) is a lattice word.

Enumeration is cell-by-cell in reading order, so the lattice and content
constraints prune as we go; semistandardness is checked against the left
neighbour (weak) and the cell above (strict).
"""

import sys
import time


def lr_coefficient(lam, mu, nu):
    L = len(lam)
    mu = tuple(mu) + (0,) * (L - len(mu))
    k = len(nu)

    # cells of lam/mu in reading order: rows top to bottom, right to left
    cells = []
    for i in range(L):
        for j in range(lam[i] - 1, mu[i] - 1, -1):
            cells.append((i, j))

    if len(cells) != sum(nu):
        return 0

    entry = {}          # (i, j) -> value 1..k
    remaining = list(nu)  # how many of each value still to place
    count_so_far = [0] * (k + 1)  # lattice prefix counts, 1-indexed
    total = 0

    def rec(idx):
        nonlocal total
        if idx == len(cells):
            total += 1
            return
        i, j = cells[idx]
        above = entry.get((i - 1, j), 0)          # must be strictly less than entry
        right = entry.get((i, j + 1), k + 1) if j + 1 < lam[i] else k + 1
        # semistandard: row weakly increases left->right, so entry <= right;
        # column strictly increases, so entry > above
        for v in range(above + 1, right + 1):
            if v > k or remaining[v - 1] == 0:
                continue
            # lattice: after placing v, #v's <= #(v-1)'s in the prefix
            if v > 1 and count_so_far[v] + 1 > count_so_far[v - 1]:
                continue
            entry[(i, j)] = v
            remaining[v - 1] -= 1
            count_so_far[v] += 1
            rec(idx + 1)
            count_so_far[v] -= 1
            remaining[v - 1] += 1
            del entry[(i, j)]

    rec(0)
    return total


if __name__ == "__main__":
    cases = [
        # sanity: c^{(2,1)}_{(1),(1,1)} = 1, c^{(2,1)}_{(2),(1)} = 1
        ((2, 1), (1,), (1, 1), 1),
        ((2, 1), (2,), (1,), 1),
        # sanity: c^{(4,2)}_{(2,1),(2,1)} = 1; c^{(3,2,1)}_{(2,1),(2,1)} = 2
        ((4, 2), (2, 1), (2, 1), 1),
        ((3, 2, 1), (2, 1), (2, 1), 2),
        # the paper's n=40 example is checked by maxlr.py; here the new value:
        # n=46 unique maximal triple, expected coefficient C(46) = 5932
        ((10, 8, 7, 6, 4, 4, 3, 2, 1, 1),
         (7, 5, 4, 3, 2, 1, 1),
         (7, 5, 4, 3, 2, 1, 1), 5932),
    ]
    ok = True
    for lam, mu, nu, expected in cases:
        t0 = time.time()
        got = lr_coefficient(lam, mu, nu)
        status = "OK" if got == expected else "MISMATCH"
        if got != expected:
            ok = False
        print(f"c^{lam}_{{{mu},{nu}}} = {got}  expected {expected}  "
              f"[{status}, {time.time() - t0:.1f}s]", flush=True)
    sys.exit(0 if ok else 1)
