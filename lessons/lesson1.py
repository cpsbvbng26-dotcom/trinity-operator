#!/usr/bin/env python3
"""Lesson 1 — every number printed in 01-contractions-and-banach.md.

    python3 lessons/lesson1.py          # the worked example, as a learner runs it
    python3 lessons/lesson1.py --values # the quoted values, one per line (for the check)

NumPy only. No randomness. verification/check_lessons.py runs this file and fails
if any value below is missing from the lesson text.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from trinity import TrinityOperator, cyclic_shift  # noqa: E402

ALPHA = 0.6
ANCHOR = [1.0, 0.0, 0.0]
X0 = [0.2, 0.9, 0.5]
STEPS = 20


def series_i():
    """The setting of Series I: one rate α for every coordinate, Q the cyclic shift."""
    return TrinityOperator(ALPHA, ANCHOR)


def values():
    op = series_i()
    xs = op.fixed_point()
    closed = (1 - ALPHA) * np.linalg.solve(np.eye(3) - ALPHA * cyclic_shift(3),
                                           np.array(ANCHOR))
    x = np.asarray(X0, dtype=float)
    first_move = float(np.linalg.norm(op.step(x) - x))
    e = [float(np.linalg.norm(x - xs))]
    for _ in range(STEPS):
        x = op.step(x)
        e.append(float(np.linalg.norm(x - xs)))
    apriori = ALPHA ** STEPS / (1 - ALPHA) * first_move
    return {
        "fixed_point": "(%s)" % ", ".join("%.6f" % v for v in xs),
        "closed_form_agrees": "%.1e" % float(np.abs(closed - xs).max()),
        "ratios": ", ".join("%.6f" % (e[k + 1] / e[k]) for k in range(3)),
        "norm": "%.6f" % op.operator_norm,
        "radius": "%.6f" % op.spectral_radius,
        "actual_20": "%.2e" % e[STEPS],
        "apriori_20": "%.2e" % apriori,
    }


def main():
    if "--values" in sys.argv:
        for k, v in values().items():
            print("%s\t%s" % (k, v))
        return
    v = values()
    print("Series I setting  α = %.1f   anchor = %s" % (ALPHA, ANCHOR))
    print("  fixed point:", v["fixed_point"], "  closed form differs by", v["closed_form_agrees"])
    print("  error ratios for the first three steps:", v["ratios"])
    print("  ‖A‖₂ = %s   ρ(A) = %s" % (v["norm"], v["radius"]))
    print("  after %d steps: actual error %s, Banach's a priori bound %s"
          % (STEPS, v["actual_20"], v["apriori_20"]))


if __name__ == "__main__":
    main()
