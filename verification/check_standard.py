#!/usr/bin/env python3
"""standard.py が確かめると言っていることを、乱数で当てて確かめる。

    python3 verification/check_standard.py

DeGroot の合意値、FJ の均衡と影響行列 V の行確率性、三篇の作用素との一致、
巡回の場合の V の閉じた形。
それぞれ 200 件の乱数の模型に当てる。乱数種は固定。

通るだけでは信用しない。W の行和を崩した模型では V の行和が 1 にならないことも
確かめる（否定の対照）。行確率性を見ていない検査なら、ここで通ってしまう。
"""

import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from standard import (degroot_limit, fj_cyclic_closed_form, fj_influence,  # noqa: E402
                      fj_iterate, left_perron, random_stochastic)
from trinity import TrinityOperator, cyclic_shift  # noqa: E402

SEED = 20260930
TRIALS = 200
TOL = 1e-9

passed, failures = 0, []


def check(label, ok, detail=""):
    global passed
    print("  %s  %s%s" % ("PASS" if ok else "FAIL", label, ("  " + detail) if detail else ""))
    if ok:
        passed += 1
    else:
        failures.append(label)


rng = np.random.default_rng(SEED)

print("1. DeGroot")
worst = 0.0
for _ in range(TRIALS):
    n = int(rng.integers(2, 7))
    W = random_stochastic(n, rng)
    x0 = rng.random(n)
    lim = degroot_limit(W, x0)
    worst = max(worst, float(np.abs(lim - left_perron(W) @ x0).max()))
check("原始的な W なら、意見は vᵀx(0) に揃う（%d 件）" % TRIALS, worst < TOL, "最大の差 %.1e" % worst)

print("\n2. Friedkin–Johnsen")
rowsum, negative, gap = 0.0, 0.0, 0.0
for _ in range(TRIALS):
    n = int(rng.integers(2, 7))
    W = random_stochastic(n, rng)
    lam = rng.uniform(0.0, 0.95, n)
    u = rng.random(n)
    V = fj_influence(W, lam)
    rowsum = max(rowsum, float(np.abs(V.sum(axis=1) - 1.0).max()))
    negative = min(negative, float(V.min()))
    gap = max(gap, float(np.abs(fj_iterate(W, lam, u) - V @ u).max()))
check("V の各行の和が 1（%d 件）" % TRIALS, rowsum < TOL, "最大のずれ %.1e" % rowsum)
check("V の成分が負にならない（%d 件）" % TRIALS, negative > -TOL, "最小 %.1e" % negative)
check("反復の極限が V u に一致する（%d 件）" % TRIALS, gap < TOL, "最大の差 %.1e" % gap)

W = random_stochastic(4, rng)
W[0] *= 1.3
V = fj_influence(W, np.full(4, 0.5))
check("否定の対照：W の行和を崩すと V の行和も 1 でなくなる",
      float(np.abs(V.sum(axis=1) - 1.0).max()) > 1e-3,
      "最大のずれ %.3f" % float(np.abs(V.sum(axis=1) - 1.0).max()))

print("\n3. 両者と三篇の作用素の関係")
W = random_stochastic(5, rng)
x0 = rng.random(5)
check("Λ = I の FJ は DeGroot と同じ軌道をたどる",
      bool(np.allclose(fj_iterate(W, np.ones(5), x0, steps=50), degroot_limit(W, x0, steps=50))))
worst = 0.0
for _ in range(TRIALS):
    n = int(rng.integers(2, 9))
    a = rng.uniform(0.0, 0.95, n)
    p = rng.random(n)
    op = TrinityOperator(a, p)
    worst = max(worst, float(np.abs(fj_influence(cyclic_shift(n), a) @ p - op.fixed_point()).max()))
check("三篇の不動点は、W = 巡回置換の FJ の均衡 V u と一致する（%d 件）" % TRIALS, worst < TOL,
      "最大の差 %.1e" % worst)

print("\n4. 巡回の場合の閉じた形")
worst = 0.0
for _ in range(TRIALS):
    n = int(rng.integers(2, 9))
    lam = rng.uniform(0.0, 0.95, n)
    worst = max(worst, float(np.abs(fj_cyclic_closed_form(lam) - fj_influence(cyclic_shift(n), lam)).max()))
check("閉じた形の V が、逆行列で求めた V と一致する（%d 件）" % TRIALS, worst < TOL, "最大の差 %.1e" % worst)

lam = rng.uniform(0.1, 0.9, 5)
Vf = fj_cyclic_closed_form(lam)
check("否定の対照：巡回の向きを逆にした W とは一致しない",
      float(np.abs(Vf - fj_influence(cyclic_shift(5).T, lam)).max()) > 1e-3,
      "最大の差 %.3f" % float(np.abs(Vf - fj_influence(cyclic_shift(5).T, lam)).max()))

print("\n" + "-" * 58)
if failures:
    print("%d 件が通り、%d 件が通りませんでした。" % (passed, len(failures)))
    for f in failures:
        print("  - " + f)
    sys.exit(1)
print("%d 件すべて通りました。" % passed)
