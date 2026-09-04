#!/usr/bin/env python3
"""derived_gate.py -- check the paper's DERIVED numbers against the primary logs.

WHY. The eight values C(46) to C(53) each appear verbatim in three or more
committed logs, and a SHIP pass confirmed that. But the paper also prints
quantities that are computed FROM those values and never appear literally
anywhere: consecutive ratios, a percentage gap, and a rounded wall-clock total.
A numeric-trace sweep on 2026-08-19 flagged five such numbers as unbacked. None
was wrong, but nothing in the entry could have shown that, so they are checked
here and the log is committed.

Every figure below is recomputed from the primary logs rather than from the
paper, so a transcription error in the paper would fail the gate.

  1.430   C(47)/C(46)
  1.170   C(48)/C(47)
  1.037   smallest consecutive ratio over 24 <= n <= 45
  1.576   largest  consecutive ratio over 24 <= n <= 45
  18.6%   runner-up gap at n = 47
  1.2%    runner-up gap at n = 51
  590 s   n = 47 total, printed rounded from the logged 589.9 s

NOT CHECKED HERE, because they are not claims: "10^3 to 10^4" renders through
pdftotext as "103 to 104"; "72 172 s" and "44 919 s" split at their thin-space
separators; "387" is a fragment of the OEIS identifier A387851; and "4.1" is a
cross-reference to Proposition 4.1 of reference [6]. Those five were read in
context and dismissed by hand, not by this script.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOL = 0.001


def anc(name):
    for p in (os.path.join(HERE, "anc", name), os.path.join(HERE, name)):
        if os.path.exists(p):
            return open(p, errors="replace").read()
    raise SystemExit(f"missing log {name}, cannot check anything")


def parse_C():
    """C(n) for every n the logs establish, from the primary run logs."""
    vals = {}
    for f in ("revalidate_24_45.log", "results_46_50.log", "results_51_52.log",
              "results_53.log"):
        for m in re.finditer(r"n=(\d+):\s*C\(n\)\s*=\s*(\d+)", anc(f)):
            vals[int(m.group(1))] = int(m.group(2))
    return vals


def main():
    C = parse_C()
    print("CHECK 0: coverage, stated before any verdict")
    print(f"  C(n) parsed from primary logs for {len(C)} values of n, "
          f"n = {min(C)} to {max(C)}")
    need = set(range(24, 54))
    missing = sorted(need - set(C))
    if missing:
        print(f"  [FAIL] missing n: {missing}")
        return 1
    print(f"  [PASS] every n in 24..53 present")

    ok = True

    print("\nCHECK 1: the two extended consecutive ratios")
    for a, b, printed in ((47, 46, 1.430), (48, 47, 1.170)):
        r = C[a] / C[b]
        good = abs(r - printed) < TOL
        ok &= good
        print(f"  [{'PASS' if good else 'FAIL'}] C({a})/C({b}) = {C[a]}/{C[b]}"
              f" = {r:.4f}, paper prints {printed}")

    print("\nCHECK 2: the range of consecutive ratios over 24 <= n <= 45")
    rs = [(C[n + 1] / C[n], n) for n in range(24, 45)]
    lo, hi = min(rs), max(rs)
    for val, printed, label in ((lo, 1.037, "smallest"), (hi, 1.576, "largest")):
        good = abs(val[0] - printed) < TOL
        ok &= good
        print(f"  [{'PASS' if good else 'FAIL'}] {label} is "
              f"C({val[1]+1})/C({val[1]}) = {val[0]:.4f}, paper prints {printed}")

    print("\nCHECK 3: the runner-up gaps, from top2_gap.log")
    t = anc("top2_gap.log")
    gaps = {}
    for m in re.finditer(r"n=(\d+): C\(n\)=\d+ \(\d+ classes attain\)\s+"
                         r"largest-below=(\d+)\s+ratio=([\d.]+)", t):
        gaps[int(m.group(1))] = float(m.group(3))
    print(f"  runner-up ratios parsed for n = {sorted(gaps)}")
    for n, printed, kind in ((47, 18.6, "gap"), (51, 1.2, "within")):
        if n not in gaps:
            print(f"  [FAIL] no runner-up ratio logged at n={n}")
            ok = False
            continue
        pct = (gaps[n] - 1.0) * 100
        good = abs(pct - printed) < 0.06
        ok &= good
        print(f"  [{'PASS' if good else 'FAIL'}] n={n}: ratio {gaps[n]} gives "
              f"{pct:.2f}%, paper prints {printed}% as the {kind}")

    print("\nCHECK 4: the n=47 total printed as 590 s")
    m = re.search(r"n=47: total ([\d.]+)s", anc("results_46_50.log"))
    if not m:
        print("  [FAIL] no logged total for n=47")
        ok = False
    else:
        logged = float(m.group(1))
        good = round(logged) == 590
        ok &= good
        print(f"  [{'PASS' if good else 'FAIL'}] logged {logged} s rounds to "
              f"{round(logged)}, paper prints 590 s")

    print("\n" + ("ALL DERIVED NUMBERS VERIFIED AGAINST THE PRIMARY LOGS"
                  if ok else "DERIVED NUMBER CHECK FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
