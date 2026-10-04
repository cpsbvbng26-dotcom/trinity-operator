#!/usr/bin/env python3
"""Every number printed in games/README.md.

    python3 games/games.py          # the computations, as a reader runs them
    python3 games/games.py --values # the quoted values, one per line (for the check)

NumPy only. No random numbers. verification/check_games.py runs this file and fails
if any value below is missing from the note, and checks the propositions
independently.

The stage game G_n: n players choose C or D. With k the number of a player's
co-players who choose C, the payoffs are πC(k) = k + 1 and πD(k) = k + 2.
G_3 is Table 1 of Series I. Payoffs of the repeated game are normalised:
(1 − δ) Σ δᵗ uₜ.
"""

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from trinity import TrinityOperator, cyclic_shift  # noqa: E402

PHI_INV = (math.sqrt(5.0) - 1.0) / 2.0
DEPTH = 22          # depth of the interval refinement for the conjectures
GAP = (0.62, 0.63, 0.64, 0.65, 0.66)
TOL = 1e-9


# ------------------------------------------------------------------ the bridge
def continuation_values(p, delta):
    """Continuation values of a cyclic path, as the fixed point of the operator.

    Phase k pays p[k] and is followed by phase k + 1 (mod m). Then
    V = (1 − δ) p + δ S V, with (S V)_k = V_{k+1}. This is x ← DQx + (I − D)p
    with D = δI and Q = S, the transpose of the papers' shift σ.
    """
    m = len(p)
    op = TrinityOperator(delta, p, Q=cyclic_shift(m).T)
    return op.fixed_point()


def direct_sum(p, delta, terms=2000):
    m = len(p)
    return np.array([sum((1 - delta) * delta ** s * p[(k + s) % m] for s in range(terms))
                     for k in range(m)])


# ------------------------------------------------------------ rotation scheme
def rotation_ok(n, delta):
    """One player defects each period; the role moves round the cycle.

    Phase 0: this player defects and gets πD(n − 1) = n + 1.
    Other phases: this player cooperates, gets πC(n − 2) = n − 1, and could get
    πD(n − 2) = n by deviating, followed by the minmax 2 for ever.
    """
    p = np.full(n, n - 1.0)
    p[0] = n + 1.0
    V = continuation_values(p, delta)
    return all(V[k] >= (1 - delta) * n + 2 * delta - 1e-12 for k in range(1, n))


def rotation_threshold(n):
    lo, hi = 0.0, 1.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if rotation_ok(n, mid):
            hi = mid
        else:
            lo = mid
    return hi


# ------------------------------------------------- the segment (2+t, 4−t, 2+t)
def c_of(delta):
    """Smallest continuation value that keeps a cooperating player from deviating."""
    return 2.0 + (1.0 - delta) / delta


def survives(w, delta, depth):
    """Can the continuation value w be continued for `depth` periods, pure strategies?"""
    if depth == 0:
        return True
    c = c_of(delta)
    for u in (2.0, 3.0):
        w2 = (w - (1 - delta) * u) / delta       # the scalar operator, run backwards
        if c - TOL <= w2 <= 3.0 + TOL and survives(w2, delta, depth - 1):
            return True
    return False


def pure_ok(t, delta, depth=40):
    """Is (2+t, 4−t, 2+t) a pure-strategy SPE payoff (to `depth` periods)?"""
    c = c_of(delta)
    w0 = 2.0 + t
    for u in (2.0, 3.0):
        w1 = (w0 - (1 - delta) * u) / delta
        if c - TOL <= w1 <= 3.0 + TOL and survives(w1, delta, depth):
            return True
    return False


def refine(delta, depth=DEPTH):
    """Intervals of continuation values that survive `depth` periods.

    Returns a list of (count, total length) after each period. For δ < 2/3 the two
    branches have disjoint images, so the intervals do not overlap.
    """
    c = c_of(delta)
    ivs = [(c, 3.0)]
    out = []
    for _ in range(depth):
        new = []
        for a, b in ivs:
            for u in (2.0, 3.0):
                lo = max((1 - delta) * u + delta * a, c)
                hi = min((1 - delta) * u + delta * b, 3.0)
                if lo <= hi + 1e-15:
                    new.append((lo, hi))
        ivs = new
        out.append((len(ivs), sum(b - a for a, b in ivs)))
    return out


def dimension_estimate(delta):
    r = refine(delta)
    n_lo, n_hi = r[DEPTH - 6][0], r[DEPTH - 1][0]
    growth = (n_hi / n_lo) ** (1 / 5)
    return r[-1][0], r[-1][1], growth, math.log(growth) / math.log(1 / delta)


# ---------------------------------------------------------------------- values
def values():
    v = {}
    p = np.array([4.0, 2.0, 2.0])
    err = float(np.abs(continuation_values(p, 0.7) - direct_sum(p, 0.7)).max())
    v["bridge_err"] = "below 1e-14" if err < 1e-14 else "%.1e" % err
    V = continuation_values(p, 0.7)
    v["bridge_V"] = "(%.6f, %.6f, %.6f)" % tuple(V)

    d3 = rotation_threshold(3)
    v["delta3"] = "%.6f" % d3
    v["phi_inv"] = "%.6f" % PHI_INV
    for n in range(4, 11):
        v["delta%d" % n] = "%.6f" % rotation_threshold(n)

    for delta in (0.5, 0.55, 0.6):
        ts = [i / 100 for i in range(1, 101) if pure_ok(i / 100, delta)]
        v["pure_low_%g" % delta] = "{%s}" % ", ".join("%g" % t for t in ts)

    for delta in GAP:
        count, length, growth, dim = dimension_estimate(delta)
        v["gap_%g" % delta] = "| %.2f | %d | %.2e | %.3f | %.2f |" % (
            delta, count, length, growth, dim)
    v["depth"] = "%d" % DEPTH
    return v


def main():
    if "--values" in sys.argv:
        for k, val in values().items():
            print("%s\t%s" % (k, val))
        return
    v = values()
    print("Bridge  rotation payoffs (4, 2, 2), δ = 0.7: V = %s, error %s"
          % (v["bridge_V"], v["bridge_err"]))
    print("Rotation thresholds  n = 3: %s  (1/φ = %s)" % (v["delta3"], v["phi_inv"]))
    for n in range(4, 11):
        print("  n = %d: %s   1/(n−2) = %.6f" % (n, v["delta%d" % n], 1 / (n - 2)))
    for delta in (0.5, 0.55, 0.6):
        print("Pure, δ = %g: t in %s" % (delta, v["pure_low_%g" % delta]))
    print("Gap regime, depth %s:  δ | intervals | total length | growth | dimension"
          % v["depth"])
    for delta in GAP:
        print("  " + v["gap_%g" % delta])


if __name__ == "__main__":
    main()
