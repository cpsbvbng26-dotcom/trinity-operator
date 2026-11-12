#!/usr/bin/env python3
"""A wider numerical scan of the golden-window conjecture. Evidence, not proof.

    python3 games/scan.py                # the exploratory table; its output is games/scan.txt
    python3 games/scan.py --values       # the quoted values, one per line (for the check)
    python3 games/scan.py --confirmatory # the preregistered grid (games/PREREGISTRATION.md)

Standard library only. No random numbers. verification/check_games.py runs this file, compares
games/scan.txt with its output, recomputes every interval count by a separate float
computation, and fails if a quoted value is missing from games/README.md.

The object is the one of games/games.py. Player 1's continuation value w stays in [c, 3]
with c = 2 + (1 − δ)/δ, and moves backwards by w′ = (w − (1 − δ)u)/δ, u ∈ {2, 3}. The
refinement keeps the intervals of values that survive n periods. For δ < 2/3 the two
branches have disjoint images, so every interval is one admissible word of length n.

δ is a rational number p/q here, and every endpoint is kept as an integer over p·qⁿ, so
the counts are exact. games.py works in floating point; at its depth of 22 periods the two
agree on its five values of δ (the check compares them).

The exploratory grid below was run on 2026-11-12. The confirmatory grid is fixed in
advance by games/PREREGISTRATION.md. It is disjoint from the exploratory grid, and its
results are not recorded in this repository until the preregistration is filed.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from games import window_lower_bound  # noqa: E402

# The exploratory grid: δ = k/1000 for k = 619 … 666, the whole window at step 0.001.
SCAN = tuple((k, 1000) for k in range(619, 667))
SCAN_DEPTH = 30
LAST = 5            # growth and length ratio are taken over the last LAST periods

# The confirmatory grid, fixed by games/PREREGISTRATION.md. Not run by the checks.
# δ = (2k + 1)/2000 for k = 618 … 665 (the midpoints of the exploratory grid), and six
# probes near the ends of the window.
CONFIRM = tuple((2 * k + 1, 2000) for k in range(618, 666)) + tuple(
    (k, 10000) for k in (6181, 6182, 6183, 6664, 6665, 6666))
CONFIRM_DEPTH = 32


def refine_exact(p, q, depth):
    """Exact interval counts and total lengths for δ = p/q, after each period.

    An endpoint w is held as the integer W with w = W/(p·qⁿ). Then
    (1 − δ)u + δw = ((q − p)·u·p·qⁿ + p·W)/(p·qⁿ⁺¹).
    """
    if not 0 < p < q:
        raise ValueError("δ must lie in (0, 1)")
    ivs = [(q + p, 3 * p)]                  # [c, 3] over p·q⁰: c = (q + p)/p
    scale = 1                               # qⁿ
    counts, lengths = [], []
    for _ in range(depth):
        lo_c, hi_c = (q + p) * scale * q, 3 * p * scale * q
        shift = {u: (q - p) * u * p * scale for u in (2, 3)}
        new = []
        for a, b in ivs:
            for u in (2, 3):
                lo, hi = shift[u] + p * a, shift[u] + p * b
                if lo < lo_c:
                    lo = lo_c
                if hi > hi_c:
                    hi = hi_c
                if lo <= hi:
                    new.append((lo, hi))
        ivs = new
        scale *= q
        counts.append(len(ivs))
        total = sum(b - a for a, b in ivs)
        lengths.append(total / (p * scale))  # exact integer, divided once
    return counts, lengths


def row(p, q, depth):
    delta = p / q
    counts, lengths = refine_exact(p, q, depth)
    n_hi, n_lo = counts[-1], counts[-1 - LAST]
    growth = (n_hi / n_lo) ** (1 / LAST)
    ratio = (lengths[-1] / lengths[-1 - LAST]) ** (1 / LAST)
    log_beta = math.log(1 / delta)
    _, n0, lower = window_lower_bound(delta)
    return {
        "delta": delta,
        "count": n_hi,
        "length": lengths[-1],
        "growth": growth,
        "growth_delta": growth * delta,
        "ratio": ratio,
        "dim": math.log(growth) / log_beta,
        "upper": math.log(n_hi) / (depth * log_beta),
        "n0": n0,
        "lower": lower,
    }


def fmt_delta(p, q):
    digits = len(str(q)) - 1
    return "%.*f" % (digits, p / q)


def table(grid, depth):
    lines = ["| δ | intervals | total length | growth | growth × δ | length ratio "
             "| dimension estimate | upper estimate | n₀ | lower bound |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    rows = []
    for p, q in grid:
        r = row(p, q, depth)
        rows.append((p, q, r))
        lines.append("| %s | %d | %.2e | %.3f | %.3f | %.3f | %.3f | %.3f | %d | %.3f |" % (
            fmt_delta(p, q), r["count"], r["length"], r["growth"], r["growth_delta"],
            r["ratio"], r["dim"], r["upper"], r["n0"], r["lower"]))
    return lines, rows


def summary(rows, depth):
    """The values the note quotes. Each one is a plain reading of the table."""
    v = {}
    n = len(rows)
    v["scan_rows"] = "%d" % n
    v["scan_first"] = fmt_delta(rows[0][0], rows[0][1])
    v["scan_last"] = fmt_delta(rows[-1][0], rows[-1][1])
    v["scan_depth"] = "%d" % depth
    shrink = sum(1 for _, _, r in rows if r["growth"] < 1 / r["delta"])
    v["scan_shrink"] = "%d of %d" % (shrink, n)
    worst = max(rows, key=lambda x: x[2]["growth_delta"])
    v["scan_max_growth_delta"] = "%.3f" % worst[2]["growth_delta"]
    v["scan_max_growth_delta_at"] = fmt_delta(worst[0], worst[1])
    v["scan_max_ratio"] = "%.3f" % max(r["ratio"] for _, _, r in rows)
    dims = [r["dim"] for _, _, r in rows]
    v["scan_decreases"] = "%d" % sum(1 for a, b in zip(dims, dims[1:]) if b < a)
    v["scan_dim_first"] = "%.2f" % dims[0]
    v["scan_dim_last"] = "%.2f" % dims[-1]
    below = [fmt_delta(p, q) for p, q, r in rows if r["dim"] < r["lower"]]
    v["scan_below_lower"] = "%d" % len(below)
    v["scan_below_lower_at"] = ", ".join(below) if below else "none"
    upper_ok = [(p, q) for p, q, r in rows if r["upper"] < 1]
    v["scan_upper_below_one"] = "%d of %d" % (len(upper_ok), n)
    v["scan_upper_below_one_to"] = fmt_delta(*upper_ok[-1]) if upper_ok else "none"
    v["scan_upper_contiguous"] = "yes" if upper_ok == [(p, q) for p, q, _ in rows[:len(upper_ok)]] else "no"
    return v


def render(lines, v):
    """The text of games/scan.txt, from the table lines and the summary values."""
    out = ["Golden-window scan, exploratory grid: δ = %s, …, %s (%s values); depth %s periods."
           % (v["scan_first"], v["scan_last"], v["scan_rows"], v["scan_depth"]),
           "Evidence, not proof. Interval counts are exact; lengths are exact sums rounded once.",
           ""] + lines + [
        "",
        "growth < 1/δ (total length shrinks):           %s" % v["scan_shrink"],
        "largest growth × δ:                            %s at δ = %s"
        % (v["scan_max_growth_delta"], v["scan_max_growth_delta_at"]),
        "largest length ratio per period:               %s" % v["scan_max_ratio"],
        "decreases of the dimension estimate:           %s" % v["scan_decreases"],
        "dimension estimate at the first and last δ:    %s, %s" % (v["scan_dim_first"], v["scan_dim_last"]),
        "estimate below the lower bound of Prop. 6:     %s (δ = %s)"
        % (v["scan_below_lower"], v["scan_below_lower_at"]),
        "upper estimate below 1:                        %s, up to δ = %s"
        % (v["scan_upper_below_one"], v["scan_upper_below_one_to"]),
    ]
    return "\n".join(out) + "\n"


def exploratory():
    lines, rows = table(SCAN, SCAN_DEPTH)
    return lines, summary(rows, SCAN_DEPTH)


def main():
    if "--confirmatory" in sys.argv:
        lines, _ = table(CONFIRM, CONFIRM_DEPTH)
        print("Golden-window scan, confirmatory grid (games/PREREGISTRATION.md); depth %d."
              % CONFIRM_DEPTH)
        print("\n".join(lines))
        return
    lines, v = exploratory()
    if "--values" in sys.argv:
        for k, val in v.items():
            print("%s\t%s" % (k, val))
        return
    sys.stdout.write(render(lines, v))


if __name__ == "__main__":
    main()
