#!/usr/bin/env python3
"""Every number printed in games/README.md, except the wider scan (games/scan.py).

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
from fractions import Fraction

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from trinity import TrinityOperator, cyclic_shift  # noqa: E402

PHI_INV = (math.sqrt(5.0) - 1.0) / 2.0
DEPTH = 22          # depth of the interval refinement for the conjectures
GAP = (0.62, 0.63, 0.64, 0.65, 0.66)
CYL_DEPTH = 16      # depth of the exact cylinder check of Proposition 8
CYL = (62, 64, 66)  # δ = k/100 for the cylinder check
DIM = ((6181, 10000), (62, 100), (63, 100), (64, 100), (65, 100), (66, 100), (6666, 10000))
DIM_GRID = (6181, 6667, 10000)   # δ = k/10000, k = 6181 … 6666: the grid of Proposition 9
FLAT = (6400, 6451, 10000)       # δ = k/10000, k = 6400 … 6450: a flat stretch of the entropy
FORCED_STEPS = 400  # steps of the forced path that are followed
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


# ------------------------------------------------ general benefit and cost
def rotation_bc_ok(n, delta, r):
    """Proposition 7. A cooperator pays r and gives 1 to every co-player.

    Stage payoffs: cooperator n − 2 − r, defector n − 1, deviating cooperator n − 2.
    The minmax payoff is 0.
    """
    p = np.full(n, n - 2.0 - r)
    p[0] = n - 1.0
    V = continuation_values(p, delta)
    return all(V[k] >= (1 - delta) * (n - 2) - 1e-12 for k in range(1, n))


def rotation_bc_threshold(n, r):
    lo, hi = 0.0, 1.0 - 1e-12
    if not rotation_bc_ok(n, hi, r):
        return None
    for _ in range(80):
        mid = (lo + hi) / 2
        if rotation_bc_ok(n, mid, r):
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


def boundary_points(count=8, depth=60):
    """At δ = 1/φ: the points 3 − (3 − c)δⁿ, n = 0 … count − 1, all continue for ever."""
    delta = PHI_INV
    c = c_of(delta)

    def reaches_three(w):
        # 3 is a fixed point of the branch u = 3, so reaching it means surviving for ever.
        # Rounding error grows by 1/δ per period, so the orbit is followed only until then.
        for _ in range(depth):
            if abs(w - 3.0) < TOL:
                return True
            for u in (2.0, 3.0):
                w2 = (w - (1 - delta) * u) / delta
                if c - TOL <= w2 <= 3.0 + TOL:
                    w = w2
                    break
            else:
                return False
        return False

    pts = [3.0 - (3.0 - c) * delta ** n for n in range(count)]
    return sum(1 for w in pts if reaches_three(w))


def window_lower_bound(delta):
    """Positive dimension inside the window (Proposition 6).

    With x = (3 − w)/(1 − δ) the recursion is x = a + δx′, a ∈ {0, 1}, on [0, X] with
    X = (2δ − 1)/(δ(1 − δ)) and the hole (δX, 1). For n ≥ n₀ the branch "1, then 0 n
    times" maps [1 + δ^{n+1}, 1 + Xδ^{n+1}] onto [1, X] with ratio 1/δ^{n+1}. Those
    intervals are disjoint, so their limit set has dimension s with
    Σ_{n ≥ n₀} δ^{(n+1)s} = 1, i.e. δ^{(n₀+1)s} = 1 − δ^s.
    """
    X = (2 * delta - 1) / (delta * (1 - delta))
    n0 = math.ceil(math.log(X / (X - 1)) / math.log(1 / delta)) - 1
    lo, hi = 1e-12, 1.0
    for _ in range(200):
        s = (lo + hi) / 2
        if delta ** ((n0 + 1) * s) - (1 - delta ** s) > 0:
            lo = s
        else:
            hi = s
    return X, n0, (lo + hi) / 2


def dimension_estimate(delta):
    r = refine(delta)
    n_lo, n_hi = r[DEPTH - 6][0], r[DEPTH - 1][0]
    growth = (n_hi / n_lo) ** (1 / 5)
    return r[-1][0], r[-1][1], growth, math.log(growth) / math.log(1 / delta)


def cylinders(p, q, depth=CYL_DEPTH):
    """Step 1 of the proof of Proposition 8, in exact arithmetic, for δ = p/q.

    With x = (3 − w)/(1 − δ), β = 1/δ and X = (2δ − 1)/(δ(1 − δ)), the map is
    T(x) = βx on L = [0, δX] and T(x) = β(x − 1) on R = [1, X]. Each cylinder I of
    depth n is kept with its image J = Tⁿ(I). The proof says J = [0, b] every time;
    the function raises if an image does not start at 0. Returns the total length of
    the cylinders (in x) after each period, as fractions.
    """
    d = Fraction(p, q)
    beta, X = 1 / d, (2 * d - 1) / (d * (1 - d))
    if not d * X < 1 < X:
        raise ValueError("δ = %s is not inside the window" % d)
    pieces = ((Fraction(0), d * X, 0), (Fraction(1), X, 1))
    cyl = [(Fraction(0), X, Fraction(0), X)]   # I = [i0, i1] and its image J = Tⁿ(I) = [j0, j1]
    lengths = []
    for n in range(depth):
        slope = beta ** n                       # Tⁿ is increasing and affine of this slope on I
        new = []
        for i0, i1, j0, j1 in cyl:
            for lo, hi, a in pieces:
                l, h = max(j0, lo), min(j1, hi)
                if l > h:
                    continue
                k0, k1 = beta * (l - a), beta * (h - a)
                if k0 != 0:
                    raise AssertionError("δ = %s, period %d: an image does not start at 0" % (d, n + 1))
                new.append((i0 + (l - j0) / slope, i0 + (h - j0) / slope, k0, k1))
        cyl = new
        lengths.append(sum(i1 - i0 for i0, i1, _, _ in cyl))
    return lengths


def first_returns(p, q, steps=FORCED_STEPS):
    """The set A_δ of Proposition 9, in exact arithmetic, for δ = p/q.

    The forced path starts at s₀ = X. From s ≥ 1 it goes to β(s − 1), from s < δX to βs,
    and it stops at a state in [δX, 1). A_δ holds k + 1 for every state s_k ≥ δX. Only the
    first `steps` states are followed; a path that has not stopped by then is cut there.
    """
    d = Fraction(p, q)
    beta, X = 1 / d, (2 * d - 1) / (d * (1 - d))
    s, out = X, []
    for k in range(steps):
        if s >= d * X:
            out.append(k + 1)
        if s >= 1:
            s = beta * (s - 1)
        elif s < d * X:
            s = beta * s
        else:
            break
    return out


def dimension(p, q, steps=FORCED_STEPS):
    """Proposition 9: the s in (0, 1) with Σ_{n ∈ A_δ} δ^{ns} = 1, by bisection in floats."""
    A, d = first_returns(p, q, steps), p / q
    lo, hi = 0.0, 1.0
    for _ in range(100):
        s = (lo + hi) / 2
        if sum(d ** (n * s) for n in A) > 1:
            lo = s
        else:
            hi = s
    return (lo + hi) / 2, A


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
        _, n0, lower = window_lower_bound(delta)
        v["gap_%g" % delta] = "| %.2f | %d | %.2e | %.3f | %.2f | %d | %.3f |" % (
            delta, count, length, growth, dim, n0, lower)
    for r in (0.5, 1.5):
        v["bc3_r%g" % r] = "%.6f" % rotation_bc_threshold(3, r)
    v["bc_full3_r1"] = "%g" % (1 / 2)
    v["phi_points"] = "%d" % boundary_points()
    v["phi_identity"] = "%.6f" % (1 - PHI_INV ** 3)
    v["phi_identity_2"] = "%.6f" % (2 * PHI_INV ** 2)
    v["depth"] = "%d" % DEPTH
    v["cyl_run"] = "for %d periods at δ = %s and %s" % (
        CYL_DEPTH, ", ".join("%g" % (k / 100) for k in CYL[:-1]), "%g" % (CYL[-1] / 100))
    for k in CYL:
        lengths = cylinders(k, 100)
        v["cyl_%g" % (k / 100)] = "from %.3g to %.3g at δ = %g" % (lengths[0], lengths[-1], k / 100)
    for p, q in DIM:
        dim, A = dimension(p, q)
        _, _, lower = window_lower_bound(p / q)
        shown = ", ".join("%d" % n for n in A[:4]) + (", …" if len(A) > 4 else "")
        v["dim_%s" % (p / q)] = "| %s | {%s} | %.6f | %.3f |" % (p / q, shown, dim, lower)
    k0, k1, q = DIM_GRID
    grid = [dimension(k, q)[0] for k in range(k0, k1)]
    lows = [window_lower_bound(k / q)[2] for k in range(k0, k1)]
    rises = sum(1 for a, b in zip(grid, grid[1:]) if b > a)
    v["dim_grid"] = "On the %d values δ = %s, %s, …, %s" % (
        len(grid), k0 / q, (k0 + 1) / q, (k1 - 1) / q)
    v["dim_grid_rises"] = "the dimension rises at %d of the %d steps" % (rises, len(grid) - 1)
    # Where A_δ = {1, n₀ + 1}, the self-similar set of Proposition 6 is the whole first-return
    # system, and the bound equals the dimension; the two bisections then differ by rounding only.
    v["dim_grid_below"] = "it is below the lower bound of Proposition 6 at %d of them and equal to it, to 9 decimals, at %d" % (
        sum(1 for a, b in zip(grid, lows) if a < b - 1e-9), sum(1 for a, b in zip(grid, lows) if abs(a - b) <= 1e-9))
    v["dim_grid_ends"] = "It runs from %.4f to %.6f" % (grid[0], grid[-1])
    k0, k1, q = FLAT
    flat = [dimension(k, q) for k in range(k0, k1)]
    sets = {tuple(A) for _, A in flat}
    A = flat[0][1]
    lo, hi = 0.0, 1.0                            # h = log(1/z*) with Σ_{n ∈ A} z^n = 1
    for _ in range(100):
        z = (lo + hi) / 2
        lo, hi = (lo, z) if sum(z ** n for n in A) > 1 else (z, hi)
    rises = all(b[0] > a[0] for a, b in zip(flat, flat[1:]))
    v["flat"] = "at every δ = %s, %s, …, %s: `A_δ = {%s}`," % (
        "%.4f" % (k0 / q), "%.4f" % ((k0 + 1) / q), "%.4f" % ((k1 - 1) / q),
        ", ".join("%d" % n for n in A) if len(sets) == 1 else "?")
    v["flat_h"] = "the entropy is %.6f throughout, and the dimension %s from %.6f to %.6f" % (
        math.log(2 / (lo + hi)), "rises" if rises else "does not rise", flat[0][0], flat[-1][0])
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
    print("Benefit 1, cost r, three players: δ_3(0.5) = %s, δ_3(1.5) = %s; full cooperation at r = 1: δ ≥ %s"
          % (v["bc3_r0.5"], v["bc3_r1.5"], v["bc_full3_r1"]))
    print("δ = 1/φ: %s of the first 8 points 3 − (3 − c)δⁿ reach 3" % v["phi_points"])
    print("Gap regime, depth %s:  δ | intervals | total length | growth | dimension | n0 | lower bound"
          % v["depth"])
    for delta in GAP:
        print("  " + v["gap_%g" % delta])
    print("Proposition 8, exact cylinders %s: every image starts at 0; total length (in x) %s"
          % (v["cyl_run"], "; ".join(v["cyl_%g" % (k / 100)] for k in CYL)))
    print("Proposition 9:  δ | A_δ | dimension | lower bound of Proposition 6")
    for p, q in DIM:
        print("  " + v["dim_%s" % (p / q)])
    print("%s: %s, and %s. %s." % (v["dim_grid"], v["dim_grid_rises"], v["dim_grid_below"], v["dim_grid_ends"]))


if __name__ == "__main__":
    main()
