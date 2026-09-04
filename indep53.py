#!/usr/bin/env python3
"""Independent pass-2 at n=53, sharing no code with maxlr.py.

Terminal classes are enumerated DIRECTLY as the partitions of n with distinct
odd parts (the periodic set of the compression map, proved in the companion
entry and re-verified set-equal to the image of the iteration at n=46..53 in
this cycle's audit), rather than by iterating T over all p(n) sum vectors.
Reports C(53), the number of classes attaining it, and the largest class value
strictly below C(53).
"""
import sys, time
from multiprocessing import Pool
import lrcalc

N = int(sys.argv[1]) if len(sys.argv) > 1 else 53
NPROC = int(sys.argv[2]) if len(sys.argv) > 2 else 3


def parts(n, maxpart):
    if n == 0:
        yield ()
        return
    for f in range(min(n, maxpart), 0, -1):
        for r in parts(n - f, f):
            yield (f,) + r


def distinct_odd(p):
    o = [x for x in p if x & 1]
    return len(o) == len(set(o))


def job(w):
    lo = tuple(x // 2 for x in w if x // 2 > 0)
    hi = tuple((x + 1) // 2 for x in w if (x + 1) // 2 > 0)
    d = lrcalc.mult(lo, hi)
    return max(d.values()) if d else 0


if __name__ == "__main__":
    t0 = time.time()
    cls = [w for w in parts(N, N) if distinct_odd(w)]
    print(f"n={N}: {len(cls)} terminal classes enumerated directly "
          f"[{time.time()-t0:.1f}s]", flush=True)
    best = second = 0
    attain = 0
    done = 0
    with Pool(NPROC) as pool:
        for v in pool.imap_unordered(job, cls, chunksize=64):
            done += 1
            if v > best:
                second = best
                best, attain = v, 1
            elif v == best:
                attain += 1
            elif v > second:
                second = v
            if done % 2000 == 0:
                print(f"  ... {done}/{len(cls)} best={best} second={second} "
                      f"[{time.time()-t0:.0f}s]", flush=True)
    print(f"n={N}: C(n)={best}  classes attaining={attain}  "
          f"largest-below={second}  ratio={best/second:.4f}  "
          f"classes={len(cls)}  [{time.time()-t0:.0f}s]", flush=True)
