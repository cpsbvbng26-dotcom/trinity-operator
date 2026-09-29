#!/usr/bin/env python3
"""Lesson 3 — every number printed in 03-permutations-by-hand.md.

    python3 lessons/lesson3.py          # the worked examples, as a learner runs them
    python3 lessons/lesson3.py --values # the quoted values, one per line (for the check)

NumPy only. No randomness. verification/check_lessons.py runs this file and fails
if any value below is missing from the lesson text.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from trinity import TrinityOperator  # noqa: E402

SWAPS = np.array([[0, 1, 0, 0],
                  [1, 0, 0, 0],
                  [0, 0, 0, 1],
                  [0, 0, 1, 0]], dtype=float)


def series_ii():
    return TrinityOperator([0.5, 0.7, 0.3], [1.0, 0.0, 0.5])


def two_cycles():
    """Four agents in two pairs, each listening only to its partner."""
    return TrinityOperator([0.9, 0.4, 0.5, 0.8], [1.0, 0.0, 0.0, 1.0], Q=SWAPS)


def values():
    s2 = series_ii()
    A, b = s2.A, s2.b
    c = float(np.prod(s2.a))
    by_hand = (b + A @ b + A @ A @ b) / (1 - c)
    t = two_cycles()
    geo = [float(np.prod(t.a[cyc])) ** (1.0 / len(cyc)) for cyc in t.cycles]
    return {
        "ii_fixed_point": "(%s)" % ", ".join("%.6f" % v for v in s2.fixed_point()),
        "ii_by_hand_differs": "%.1e" % float(np.abs(by_hand - s2.fixed_point()).max()),
        "tc_cycles": " and ".join("{%s}" % ", ".join(str(i + 1) for i in cyc)
                                  for cyc in t.cycles),
        "tc_geo": " and ".join("%.6f" % g for g in geo),
        "tc_radius": "%.6f" % t.spectral_radius,
        "tc_norm": "%.6f" % t.operator_norm,
        "tc_closed_norm": "%.6f" % t.closed_form_norm,
        "tc_closed_radius": "%.6f" % t.closed_form_radius,
    }


def main():
    if "--values" in sys.argv:
        for k, v in values().items():
            print("%s\t%s" % (k, v))
        return
    v = values()
    print("Series II  fixed point:", v["ii_fixed_point"],
          "  by-hand formula differs by", v["ii_by_hand_differs"])
    print("Two pairs  cycles:", v["tc_cycles"], "  geometric means:", v["tc_geo"])
    print("  ρ(A) = %s (closed form %s)   ‖A‖₂ = %s (closed form %s)"
          % (v["tc_radius"], v["tc_closed_radius"], v["tc_norm"], v["tc_closed_norm"]))


if __name__ == "__main__":
    main()
