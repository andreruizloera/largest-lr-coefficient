ANCILLARY FILES
New values of the largest Littlewood-Richardson coefficient via iterated
Okounkov compression

Everything in this directory is code and raw output. Every number printed in
the paper is produced by one of these scripts and appears in one of these
logs. Nothing here is needed to compile the paper.


ENVIRONMENT
-----------
Python 3.9.6, macOS (Apple M-series). The only third-party dependency is
lrcalc, the Littlewood-Richardson calculator of A. S. Buch, version 2.1:

    python3 -m pip install lrcalc

crosscheck.py and the terminal-class enumeration inside indep53.py do not use
lrcalc at all; crosscheck.py needs nothing but the standard library.

All scripts take a degree or a degree range on the command line, print one
line per degree to stdout, and read no input files. Run them from inside this
directory (bruteforce_gate.py and top2_gap.py import maxlr.py by name).


SCRIPTS
-------
maxlr.py
    The algorithm of the paper, in three passes: compress every partition of n
    under the map T, expand the distinct terminal pairs with lrcalc to get
    C(n), then expand every decomposition of every suspect sum vector to
    recover all maximal triples and test both parts of the Pak-Soskin
    conjecture on them.
        python3 maxlr.py 46 47 48 49 50 51 52 53
    Reproduces: Table 1 (values, terminal vector counts, suspect pair counts,
    maximal triple counts, orbit counts) and the orbit representatives.
    Runtime: about 6 minutes at n = 46 rising to about 3.7 hours at n = 53 on
    one core.

crosscheck.py
    An independent Littlewood-Richardson coefficient counter: direct
    enumeration of semistandard skew tableaux of shape lambda/mu with content
    nu whose reverse reading word is a lattice word. It shares no code and no
    algorithm with lrcalc. Four textbook values plus the n = 46 maximal triple.
        python3 crosscheck.py
    Reproduces: gate (V4). Runtime: under a second.

bruteforce_gate.py
    The exhaustive gate. For each n in the given range it computes C(n) AND
    the complete list of maximal triples by direct search over every pair
    (mu |- k, nu |- n-k) with k <= n/2, and compares both against what
    maxlr.py returns. The comparison of the two maximal-triple lists is the
    direct test of the completeness claim (Corollary 2.4 of the paper).
        python3 bruteforce_gate.py 2 28
    Reproduces: gate (V1). Runtime: about 4 minutes for 2 to 28; the brute
    force roughly doubles in cost every degree, so 30 takes a few times longer
    and 34 is already impractical.

indep53.py
    An independent rerun of pass 2 alone. It enumerates the terminal vectors
    directly, as the partitions of n whose odd parts are pairwise distinct,
    rather than by iterating T over all p(n) sum vectors, and shares no code
    with maxlr.py. Prints C(n), the number of terminal vectors attaining it,
    and the largest value strictly below it.
        python3 indep53.py 53 3          # degree 53, 3 worker processes
    Reproduces: gate (V5), and Table 2. Runtime: hours at the top of the
    range; scales down with the worker count.

top2_gap.py
    The original single-process version of the Table 2 computation, reusing
    maxlr.py's machinery.
        python3 top2_gap.py 46 47 48 49 50 51 52
    Reproduces: Table 2.


LOGS
----
results_46_50.log      maxlr.py runs at n = 46 to 50   (Table 1)
results_51_52.log      maxlr.py runs at n = 51 and 52  (Table 1)
results_53.log         maxlr.py run at n = 53          (Table 1)
revalidate_24_45.log   maxlr.py over the whole published range 24 to 45,
                       the run behind gate (V2) and the runtime table
bruteforce_gate.log    gate (V1), degrees 2 to 28
crosscheck.log         gate (V4)
indep53.log            gate (V5) at n = 53
indep_46_52.log        gate (V5) at n = 46 to 52
top2_gap.log           Table 2. The first three lines of this log come from an
                       earlier version of the script that reported the second
                       largest terminal value including ties; the lines
                       starting "C(n)=... (k classes attain)" are the ones the
                       paper quotes.

A note on the reported wall-clock times: the machine was carrying unrelated
load throughout, so the runtimes in the logs are indicative rather than
benchmarks. This is why n = 51 took longer than n = 52.


WHAT IS AND IS NOT INDEPENDENTLY CONFIRMED
------------------------------------------
Lower bounds. That the printed triples really achieve the printed
coefficients is confirmed twice over: by lrcalc, and by the from-scratch
tableau enumeration in crosscheck.py.

Upper bounds. That nothing at degree n beats the printed value rests, for
46 <= n <= 53, on the completeness proposition of the paper together with
runs of pass 2 over the terminal vectors: two scripts (maxlr.py and
indep53.py) with independent enumerations of the terminal vectors, but the
same underlying Littlewood-Richardson library. At 2 <= n <= 28 the upper
bound is instead confirmed by exhaustive search (bruteforce_gate.py), and at
24 <= n <= 45 it agrees with the independently published table of Pak and
Soskin.
