# Code and logs for: New values of the largest Littlewood-Richardson coefficient via iterated Okounkov compression

Andre Ruiz Loera, Department of Mathematics, University of Illinois
Urbana-Champaign.

This repository is the code-and-logs half of the paper

> Andre Ruiz Loera, *New values of the largest Littlewood-Richardson
> coefficient via iterated Okounkov compression*, 2026.
> Published as a Zenodo record; this repository and the record carry the manuscript (paper.pdf) alongside the code.

It contains, byte for byte, the ancillary directory `anc/` of the submission
submission: every script the paper cites and the raw log of every run it
reports. File names are unchanged, so the paper's reproducibility table
(Section "Reproducibility") maps one to one onto this directory.

## What the code computes

Let C(n) be the largest Littlewood-Richardson coefficient in degree n
(OEIS A387851). Pak and Soskin computed C(n) for 24 <= n <= 45; this code
extends the table by eight new values and verifies both parts of their
conjecture on the maximizers at each new degree:

| n  | C(n)  |
|----|-------|
| 46 | 5932  |
| 47 | 8481  |
| 48 | 9926  |
| 49 | 12828 |
| 50 | 15762 |
| 51 | 18570 |
| 52 | 22982 |
| 53 | 31264 |

The algorithm compresses every sum vector of degree n under the iterated
Okounkov compression map T, reduces the search to the terminal vectors
(partitions with pairwise distinct odd parts), expands the surviving
products, and then recovers the complete list of maximal triples from the
suspect sum vectors. The paper proves the reduction is lossless; the
brute-force gate below tests that claim exhaustively for 2 <= n <= 28.

## Environment

Per the paper's Reproducibility section: CPython 3.9.6 on macOS 15.7.1,
one core of an Apple M4 laptop, single process, single thread (except
`indep53.py`, which takes a worker count). The only third-party dependency
is lrcalc, the Littlewood-Richardson calculator of A. S. Buch, version
2.1, through its Python bindings:

    python3 -m pip install lrcalc

`crosscheck.py` needs nothing but the standard library, and the
terminal-class enumeration inside `indep53.py` does not use lrcalc either.
All scripts read no input files and print one line per degree to stdout.
Run them from inside this directory (`bruteforce_gate.py` and
`top2_gap.py` import `maxlr.py` by name).

## Quickstart, with the smoke test this repository actually passed

In a fresh virtual environment:

    python3 -m venv venv
    venv/bin/pip install lrcalc
    venv/bin/python crosscheck.py     # under a second, no lrcalc needed
    venv/bin/python maxlr.py 24       # about a second, exercises lrcalc

Expected: `crosscheck.py` prints five `[OK]` lines ending with the n = 46
maximal triple at 5932, matching `crosscheck.log`; `maxlr.py 24` prints
C(24) = 41 with 2 terminal classes attaining it, 350 terminal classes,
2 maximal triples, both conjecture parts True, matching the n = 24 block
of `revalidate_24_45.log`.

Smoke test on record, run 2026-09-03 before the v1.0.0 tag, in a fresh
venv (CPython 3.9.6, `pip install lrcalc` clean): `crosscheck.py`
finished in 0.12 s with all five `[OK]` verdicts identical to
`crosscheck.log`, and `maxlr.py 24` finished in 0.42 s reproducing the
n = 24 block of `revalidate_24_45.log` line for line modulo wall-clock
timings: 350 terminal classes, C(24) = 41 with 2 attaining, 576 suspect
pairs, the same 2 maximal triples, both conjecture parts True, 1 orbit.
The long runs (Table 1 at n = 46 to 53, gates V1/V2/V5, Table 2) were
not re-run for this smoke test; their committed logs are the record.

## Scripts, what each reproduces, and expected runtimes

Wall-clock times below are from the committed logs; the machine was
carrying unrelated load throughout, so read them as indicative upper
bounds (this is why n = 51 took longer than n = 52 in one run).

- **`maxlr.py`**, the paper's three-pass algorithm. `python3 maxlr.py 46
  47 48 49 50 51 52 53` reproduces Table 1 (values, terminal vector
  counts, suspect pair counts, maximal triples, orbit counts):
  `results_46_50.log` (n = 46 to 50, about 6 to 26 min per degree),
  `results_51_52.log` (about 2.7 and 2.4 h), `results_53.log` (about
  3.5 h). `python3 maxlr.py 24 25 ... 45` reproduces
  `revalidate_24_45.log`, the gate (V2) run over the reported Pak-Soskin
  range, about 34 min end to end.
- **`crosscheck.py`**, an independent LR coefficient counter by direct
  lattice-word tableau enumeration, no lrcalc, no arguments. Reproduces
  gate (V4), `crosscheck.log`. Under a second.
- **`bruteforce_gate.py`**, the exhaustive gate: recomputes C(n) AND the
  complete maximal-triple list by direct search and compares both against
  `maxlr.py`. `python3 bruteforce_gate.py 2 28` reproduces gate (V1),
  `bruteforce_gate.log`, about 4 minutes; the cost roughly doubles per
  degree beyond that.
- **`indep53.py`**, an independent rerun of pass 2 alone, enumerating the
  terminal vectors directly rather than by iterating T. `python3
  indep53.py 53 3` (3 workers) reproduces gate (V5) at n = 53,
  `indep53.log`, about 4 h; the runs behind `indep_46_52.log` are the
  same script at n = 46 to 52, 19 min to 2.7 h per degree.
- **`top2_gap.py`**, the runner-up gap computation. `python3 top2_gap.py
  46 47 48 49 50 51 52` reproduces Table 2, `top2_gap.log` (13 min to
  2.3 h per degree); `top2_gap_53.log` is the same at n = 53, about
  3.4 h.
- **`derived_gate.py`**, checks the paper's derived numbers (consecutive
  ratios, runner-up gaps, a rounded runtime) by recomputing them from the
  primary logs in this directory. `python3 derived_gate.py` reproduces
  `derived_gate.log`, seconds.
- **`flagged_numbers_gate.py`** resolves the five strings a numeric
  tracer flags in the paper. It reads `paper.tex` and `paper.pdf`, which
  are not in this repository, so it is NOT runnable from here alone; run
  it from inside the arXiv package. Its log,
  `flagged_numbers_gate.log`, is committed for the record.

## What is and is not independently confirmed

Lower bounds (the printed triples achieve the printed coefficients):
confirmed twice, by lrcalc and by the from-scratch enumeration in
`crosscheck.py`. Upper bounds at 46 <= n <= 53: two scripts with
independent terminal-vector enumerations (`maxlr.py`, `indep53.py`) but
the same underlying LR library; at 2 <= n <= 28 the upper bound is
confirmed by exhaustive search, and at 24 <= n <= 45 it agrees with the
independently reported Pak-Soskin table. See `README.txt` (the arXiv
ancillary README, kept verbatim) and the paper's verification section.

## Citing

Cite the paper by its Zenodo DOI (minted on release; see the repository page after
posting) and, once minted, the Zenodo DOI of this repository's v1.0.0
release. See `CITATION.cff`.

## License

MIT, see `LICENSE`.
