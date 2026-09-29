#!/usr/bin/env python3
"""Lesson 4 — every number printed in 04-errors-that-grow.md.

    python3 lessons/lesson4.py          # the worked examples, as a learner runs them
    python3 lessons/lesson4.py --values # the quoted values, one per line (for the check)

NumPy only. No randomness. verification/check_lessons.py runs this file and fails
if any value below is missing from the lesson text.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from certificate import certify, sweep  # noqa: E402
from trinity import TrinityOperator  # noqa: E402


def non_normal():
    """A = 0.5 I + 20 N with N nilpotent. The same example as demo.py and certificate.py."""
    return TrinityOperator([0.5, 0.5], [1.0, 0.0], Q=np.array([[1.0, 40.0], [0.0, 1.0]]))


def series_ii():
    """The papers' setting, for contrast."""
    return TrinityOperator([0.5, 0.7, 0.3], [1.0, 0.0, 0.5])


X0 = [5.0, -3.0]
STEPS = 60


def values():
    """name -> the exact string the lesson prints."""
    op = non_normal()
    A = op.A
    err = op.error_curve(X0, steps=STEPS)
    powers = [np.linalg.matrix_power(A, k) for k in range(1, 6)]
    s2 = series_ii()
    cert = certify(op)
    covered = all(err[k] <= cert.bound(k, err[0]) * (1 + 1e-9) for k in range(len(err)))
    table = sweep(op)
    v = {
        "nn_norm": "%.6f" % op.operator_norm,
        "nn_radius": "%.6f" % op.spectral_radius,
        "nn_offdiag": ", ".join("%g" % P[0, 1] for P in powers),
        "nn_power_norms": ", ".join("%.2f" % np.linalg.norm(P, 2) for P in powers),
        "nn_errors": ", ".join("%.3f" % e for e in err[:5]),
        "nn_peak": "%.1f" % (err.max() / err[0]),
        "nn_peak_step": "%d" % int(np.argmax(err)),
        "nn_worst": "%.2f" % op.transient_growth(),
        "ii_power_norms": ", ".join("%.4f" % np.linalg.norm(np.linalg.matrix_power(s2.A, k), 2)
                                    for k in range(1, 5)),
        "cert_gamma": "%.2f" % cert.gamma,
        "cert_kappa": "%.6f" % cert.kappa,
        "cert_amp": "%.2f" % cert.amplification,
        "cert_covered": "all %d steps" % STEPS if covered else "NOT COVERED",
        "actual_20": "%.2e" % err[20],
    }
    for c in table:
        g = "%.2f" % c.gamma
        v["sweep_%s" % g] = "| %s | %.6f | %.2f | %.2e |" % (
            g, c.kappa, c.amplification, c.bound(20, err[0]))
    return v


def main():
    if "--values" in sys.argv:
        for k, val in values().items():
            print("%s\t%s" % (k, val))
        return
    v = values()
    print("Non-normal example  ‖A‖₂ = %s   ρ(A) = %s" % (v["nn_norm"], v["nn_radius"]))
    print("  off-diagonal entry of Aᵏ, k = 1..5:", v["nn_offdiag"])
    print("  ‖Aᵏ‖₂, k = 1..5:", v["nn_power_norms"])
    print("  errors from (5, −3), first five:", v["nn_errors"])
    print("  peak: %s times the start, at step %s; worst case over all starts: %s"
          % (v["nn_peak"], v["nn_peak_step"], v["nn_worst"]))
    print("Papers' setting  ‖Aᵏ‖₂, k = 1..4:", v["ii_power_norms"])
    print("Certificate  γ = %s   κ = %s   amplification = %s   bound holds for %s"
          % (v["cert_gamma"], v["cert_kappa"], v["cert_amp"], v["cert_covered"]))
    print("| γ | κ | amplification | bound at step 20 |")
    for k, val in v.items():
        if k.startswith("sweep_"):
            print(val)
    print("actual error at step 20:", v["actual_20"])


if __name__ == "__main__":
    main()
