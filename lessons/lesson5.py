#!/usr/bin/env python3
"""Lesson 5 — every number printed in 05-switching.md.

    python3 lessons/lesson5.py          # the worked examples, as a learner runs them
    python3 lessons/lesson5.py --values # the quoted values, one per line (for the check)

NumPy only. The random switching uses a fixed seed. verification/check_lessons.py
runs this file and fails if any value below is missing from the lesson text.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from trinity import TrinityOperator, cyclic_shift  # noqa: E402

SEED = 20260930
STEPS = 40
TRIALS = 1000


def shear_pair():
    """Two stable matrices whose alternation diverges. Not Friedkin–Johnsen matrices."""
    A1 = 0.7 * np.array([[1.0, 1.0], [0.0, 1.0]])
    A2 = 0.7 * np.array([[1.0, 0.0], [1.0, 1.0]])
    return A1, A2


def cyclic_pair():
    """The papers' setting, switching between the forward and backward shift."""
    fwd = TrinityOperator([0.5, 0.7, 0.3], [1.0, 0.0, 0.5])
    bwd = TrinityOperator([0.9, 0.2, 0.6], [0.0, 1.0, 0.0], Q=cyclic_shift(3).T)
    return fwd.A, bwd.A


def radius(M):
    return float(np.max(np.abs(np.linalg.eigvals(M))))


def values():
    A1, A2 = shear_pair()
    x0 = np.array([1.0, 1.0])
    one = x0.copy()
    alt = x0.copy()
    for k in range(STEPS):
        one = A1 @ one
        alt = (A1 if k % 2 == 0 else A2) @ alt

    F, B = cyclic_pair()
    rng = np.random.default_rng(SEED)
    worst = 0.0
    for _ in range(TRIALS):
        M = np.eye(3)
        for _ in range(STEPS):
            M = (F if rng.random() < 0.5 else B) @ M
        worst = max(worst, float(np.linalg.norm(M, 2)))
    lam_max = 0.9

    # General Friedkin–Johnsen: random row-stochastic W, susceptibilities at most 0.9.
    fj_worst = 0.0
    for _ in range(TRIALS):
        M = np.eye(4)
        for _ in range(STEPS):
            W = rng.random((4, 4))
            W /= W.sum(axis=1, keepdims=True)
            L = np.diag(rng.uniform(0.0, lam_max, 4))
            M = L @ W @ M
        fj_worst = max(fj_worst, float(np.linalg.norm(M, np.inf)))

    return {
        "sh_radius": "%.1f" % radius(A1),
        "sh_norm": "%.6f" % float(np.linalg.norm(A1, 2)),
        "sh_one": "%.2e" % float(np.linalg.norm(one)),
        "sh_alt": "%.1f" % float(np.linalg.norm(alt)),
        "sh_product_radius": "%.6f" % radius(A2 @ A1),
        "cy_norms": "%.1f and %.1f" % (np.linalg.norm(F, 2), np.linalg.norm(B, 2)),
        "cy_worst": "%.2e" % worst,
        "cy_bound": "%.2e" % (lam_max ** STEPS),
        "fj_worst": "%.2e" % fj_worst,
    }


def main():
    if "--values" in sys.argv:
        for k, v in values().items():
            print("%s\t%s" % (k, v))
        return
    v = values()
    print("Shear pair  ρ = %s each, ‖A₁‖₂ = %s" % (v["sh_radius"], v["sh_norm"]))
    print("  %d steps of A₁ alone: %s    alternating: %s    ρ(A₂A₁) = %s"
          % (STEPS, v["sh_one"], v["sh_alt"], v["sh_product_radius"]))
    print("Papers' setting  ‖F‖₂, ‖B‖₂ = %s" % v["cy_norms"])
    print("  worst ‖product‖₂ over %d random switchings of %d steps: %s   bound 0.9^%d = %s"
          % (TRIALS, STEPS, v["cy_worst"], STEPS, v["cy_bound"]))
    print("General FJ  worst ‖product‖∞ over %d random runs: %s   bound %s"
          % (TRIALS, v["fj_worst"], v["cy_bound"]))


if __name__ == "__main__":
    main()
