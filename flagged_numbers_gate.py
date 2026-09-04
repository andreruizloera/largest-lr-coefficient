#!/usr/bin/env python3
"""flagged_numbers_gate.py -- the five numbers the tracer flags, resolved.

WHY. On 2026-08-22 `scripts/trace_numbers.py` tagged five numbers here as
untraced. All five resolve and they resolve in four different ways, only one of
which is a real quantity. Recording that is worth a gate, because next cycle
the same five will be flagged again and re-derived from scratch.

  A  THOUSANDS-SEPARATOR FRAGMENTS, and this is a class the lab had not
     pinned before. The tracer reads `pdftotext` output, and LaTeX's thin
     space `\\,` renders as a plain space, so `44\\,919` becomes "44 919" and
     the tracer reports a number 919 that was never printed. Same for 172 out
     of `72\\,172`. These are not numbers.
  B  A SUPERSCRIPT ARTIFACT, a class already recorded in the sensitivity note:
     `10^3` renders as "103". The sentence reads "10^3 to 10^4 pairs" and the
     tracer sees 103 and 104.
  C  A DERIVED RATIO, the only real quantity of the five: C(47)/C(46) is
     printed as 1.430, and both values are in the committed logs.
  D  A CROSS-REFERENCE, "Proposition 4.1 of [6]", which is somebody else's
     numbering.

GATES, each able to fail.

  G1  For each separator fragment, the .tex must contain the full number with
      a thin space and must NOT contain the fragment as a standalone value.
      If the fragment is genuinely printed, the artifact story is wrong.
  G2  The superscript form must be in the .tex and the flattened form must not.
  G3  The ratio must RECOMPUTE from the two C values in the logs, to the
      precision printed. Recomputing rather than matching means that changing
      a C value breaks this.
  G4  The cross-reference must appear as a proposition number attributed to
      another work.
  G5  NEGATIVE CONTROL: a wrong pair of C values must fail G3.

Usage: python3 flagged_numbers_gate.py
"""
import os
import re
import subprocess
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))


def _find(name):
    """Two layouts must both work or this gate is repo-only and cannot travel.

    repo          entry/flagged_numbers_gate.py beside paper.tex
    arXiv extract anc/flagged_numbers_gate.py with paper.tex one level up
    """
    for cand in (os.path.join(HERE, name), os.path.join(HERE, "..", name)):
        if os.path.exists(cand):
            return cand
    return os.path.join(HERE, name)

SEPARATOR_FRAGMENTS = [("919", r"44\,919"), ("172", r"72\,172")]
SUPERSCRIPTS = [("103", "10^3"), ("104", "10^4")]
RATIOS = [("1.430", 47, 46), ("1.170", 48, 47)]


def tex():
    return open(_find("paper.tex"), errors="replace").read()


def pdf():
    return " ".join(subprocess.run(
        ["pdftotext", _find("paper.pdf"), "-"],
        capture_output=True, text=True).stdout.split())


def logged_C():
    """C(n) values as the committed logs report them."""
    out = {}
    roots = [HERE, os.path.join(HERE, "..")]
    for root in roots:
        if not os.path.isdir(root):
            continue
        for f in os.listdir(root):
            if not f.endswith(".log"):
                continue
            # NEVER READ YOUR OWN OUTPUT. This gate ships its log, and its own
            # PASS lines print ratios like "C(47)/C(46) = 8481/5932", which the
            # assignment pattern below happily misreads as "C(46) = 8481". Run
            # from the clean extract, where numeric_trace.log is not shipped,
            # that circularity was the only source of C values and the gate
            # contradicted itself.
            if f.startswith("flagged_numbers_gate"):
                continue
            body = open(os.path.join(root, f), errors="replace").read()
            # A ratio line is not an assignment, but it CARRIES both values:
            # "C(47)/C(46) = 8481/5932" means C(47) = 8481 and C(46) = 5932.
            # The first fix here simply skipped such lines, and from the clean
            # extract, where numeric_trace.log is not shipped, that left no C
            # values at all and the gate refused. Parsing them is better than
            # discarding them.
            for line in body.splitlines():
                for rm in re.finditer(
                        r"C\((\d+)\)\s*/\s*C\((\d+)\)\s*=\s*"
                        r"(\d+)\s*/\s*(\d+)", line):
                    for nn, vv in ((int(rm.group(1)), int(rm.group(3))),
                                   (int(rm.group(2)), int(rm.group(4)))):
                        if nn in out and out[nn] != vv:
                            print(f"  WARNING: {f} disagrees on C({nn}): "
                                  f"{out[nn]} vs {vv}")
                        out[nn] = vv
                if re.search(r"C\(\d+\)\s*/\s*C\(\d+\)", line):
                    continue
                for m in re.finditer(r"C\((\d+)\)\s*=\s*(\d+)\b(?!\s*/)",
                                     line):
                    n, v = int(m.group(1)), int(m.group(2))
                    if n in out and out[n] != v:
                        print(f"  WARNING: {f} disagrees on C({n}): "
                              f"{out[n]} vs {v}")
                    out[n] = v
    return out


def main():
    t, pt = tex(), pdf()
    C = logged_C()
    print("COVERAGE, stated before any verdict")
    print(f"  paper.tex          : {len(t):,} chars")
    print(f"  paper.pdf as text  : {len(pt):,} chars")
    print(f"  C values in the logs: {len(C)} ({sorted(C)[:8]}...)")
    if not t or not pt or not C:
        print("\nFAIL: an input is missing.")
        return 1
    print()
    ok = True

    print("G1  THOUSANDS-SEPARATOR FRAGMENTS: pdftotext split these")
    for frag, full in SEPARATOR_FRAGMENTS:
        in_tex_full = full in t
        # the fragment must not stand alone as a printed value in the source
        alone = re.search(r"(?<![0-9\\,]) " + frag + r"(?![0-9])", t)
        good = in_tex_full and alone is None
        ok &= good
        print(f"  [{'PASS' if good else 'FAIL'}] '{frag}': source has "
              f"'{full}' = {in_tex_full}; fragment standing alone = "
              f"{alone is not None}")
    print()

    print("G2  SUPERSCRIPT ARTIFACTS")
    for flat, sup in SUPERSCRIPTS:
        good = (sup in t) and (flat not in t)
        ok &= good
        print(f"  [{'PASS' if good else 'FAIL'}] '{flat}': source has "
              f"'{sup}' = {sup in t}; flattened form in source = "
              f"{flat in t}")
    print()

    print("G3  THE DERIVED RATIO, recomputed from the logged C values")
    for printed, a, b in RATIOS:
        if a not in C or b not in C:
            print(f"  [FAIL] C({a}) or C({b}) not in any log")
            ok = False
            continue
        d = len(printed.split(".")[1])
        got = f"{float(F(C[a], C[b])):.{d}f}"
        good = got == printed and printed in pt
        ok &= good
        print(f"  [{'PASS' if good else 'FAIL'}] C({a})/C({b}) = "
              f"{C[a]}/{C[b]} = {got}, paper prints {printed}")
    print()

    print("G4  THE CROSS-REFERENCE")
    m = re.search(r"Proposition~?4\.1 of", t)
    ok &= bool(m)
    print(f"  [{'PASS' if m else 'FAIL'}] '4.1' appears as a proposition "
          f"number attributed to another work")
    print()

    print("G5  NEGATIVE CONTROL: a wrong pair must fail G3")
    bad = f"{float(F(C[47] + 100, C[46])):.3f}"
    caught = bad != "1.430"
    ok &= caught
    print(f"  [{'PASS' if caught else 'FAIL'}] perturbing C(47) gives {bad}, "
          f"not 1.430")

    print()
    print("=" * 70)
    print("ALL FIVE FLAGGED NUMBERS RESOLVE" if ok
          else "FAILED. At least one does not.")
    print("=" * 70)
    print("SCOPE: this says what each flagged string IS. The C values")
    print("themselves are gated by the paper's own verification section.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
