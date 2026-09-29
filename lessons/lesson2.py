#!/usr/bin/env python3
"""Lesson 2 — every number printed in 02-sufficient-is-not-necessary.md.

    python3 lessons/lesson2.py          # the worked examples, as a learner runs them
    python3 lessons/lesson2.py --values # the quoted values, one per line (for the check)

NumPy only. No randomness. verification/check_lessons.py runs this file and fails
if any value below is missing from the lesson text.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from trinity import TrinityOperator  # noqa: E402


def series_ii():
    """The setting of Series II: Q a cyclic permutation, rates a = (0.5, 0.7, 0.3)."""
    return TrinityOperator([0.5, 0.7, 0.3], [1.0, 0.0, 0.5])


def outside():
    """Outside the papers' assumptions: Q is not a permutation."""
    return TrinityOperator([0.5, 0.5], [1.0, 0.0], Q=np.array([[1.0, 4.0], [0.0, 1.0]]))


def exercise():
    """Exercise 2: rates (0.9, 0.9, 0.1) with the cyclic permutation."""
    return TrinityOperator([0.9, 0.9, 0.1], [1.0, 0.0, 0.0])


def errors(op, x0, steps):
    x, xs = np.asarray(x0, dtype=float), op.fixed_point()
    out = [float(np.linalg.norm(x - xs))]
    for _ in range(steps):
        x = op.step(x)
        out.append(float(np.linalg.norm(x - xs)))
    return out


def values():
    """name -> the exact string the lesson prints."""
    s2 = series_ii()
    e = errors(s2, [0.9, 0.1, 0.4], 30)
    b = outside()
    f = errors(b, [0.0, 1.0], 40)
    return {
        "ii_norm": "%.6f" % s2.operator_norm,
        "ii_radius": "%.6f" % s2.spectral_radius,
        "ii_product": "%.3f" % float(np.prod(s2.a)),
        "ii_cube_offdiag": "%.1e" % float(np.abs(np.linalg.matrix_power(s2.A, 3)
                                                 - np.prod(s2.a) * np.eye(3)).max()),
        "ii_three_steps": "%.6f" % (e[3] / e[0]),
        "ii_ratio_30": "%.2e" % (e[30] / e[0]),
        "ii_bound_30": "%.2e" % (s2.operator_norm ** 30),
        "out_norm": "%.6f" % b.operator_norm,
        "out_radius": "%.6f" % b.spectral_radius,
        "out_errors": ", ".join("%.4f" % v for v in f[:5]),
        "out_peak": "%.2f" % (max(f) / f[0]),
        "out_err_40": "%.2e" % f[40],
        "ex_norm": "%.6f" % exercise().operator_norm,
        "ex_radius": "%.6f" % exercise().spectral_radius,
    }


def main():
    if "--values" in sys.argv:
        for k, v in values().items():
            print("%s\t%s" % (k, v))
        return
    v = values()
    print("Series II setting  ‖A‖₂ = %s   ρ(A) = %s   ∏aᵢ = %s"
          % (v["ii_norm"], v["ii_radius"], v["ii_product"]))
    print("  A³ − (∏aᵢ)I, largest entry:", v["ii_cube_offdiag"])
    print("  error after 3 steps / initial error:", v["ii_three_steps"])
    print("  error after 30 steps / initial error:", v["ii_ratio_30"],
          "   the papers' bound ‖A‖₂³⁰:", v["ii_bound_30"])
    print("Outside the papers  ‖A‖₂ = %s   ρ(A) = %s" % (v["out_norm"], v["out_radius"]))
    print("  errors, first five steps:", v["out_errors"])
    print("  largest error / initial error:", v["out_peak"], "   after 40 steps:", v["out_err_40"])


if __name__ == "__main__":
    main()
