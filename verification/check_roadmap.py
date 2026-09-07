#!/usr/bin/env python3
"""roadmap/ の各段が主張していることを、その場で確かめる。

    python3 verification/check_roadmap.py

展望は、書けばいくらでも大きく書ける。**書いたことが実際に成り立つかどうかを
分ける手立てが無いと、展望は願望と区別がつかない。**そこでここに置く。

各段について、本文が名乗っている性質を計算し直す。特に次を分けて見る。

    厳密に決まること      スペクトル半径、E[A⊗A]、冪零性、閉じた式との一致
    推定でしかないこと    リアプノフ指数、標本による ‖Df‖ の最大
    決まらないこと        JSR がちょうど 1 の場合

三つ目を「通った」と数えないことが、この検査の要点である。

NumPy のみ。乱数種は固定。
"""

import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "roadmap"))

from trinity import TrinityOperator, cyclic_shift            # noqa: E402
from stage1_optimal_norm import (weighted_lyapunov, amplification,  # noqa: E402
                                 achieved, optimize_weight, jordan_optimum)
from stage2_switching import (jsr_bounds, common_lyapunov,   # noqa: E402
                              simulate)
from stage3_stochastic import (mean_square_radius, lyapunov_exponent,  # noqa: E402
                               second_moment)
from stage4_nonlinear import (make_operator, jacobian,       # noqa: E402
                              sampled_contraction, find_fixed_points)
from stage5_infinite import weighted_shift, transient_profile  # noqa: E402

passed, failures = 0, []


def check(label, cond, detail=""):
    global passed
    if cond:
        passed += 1
        print("  PASS  " + label + (("  " + detail) if detail else ""))
    else:
        failures.append(label)
        print("  FAIL  " + label + (("  " + detail) if detail else ""))


def section(s):
    print("\n" + s)


S = np.array([[1.0, 1.0], [0.0, 1.0]])

# ------------------------------------------------------------------ 段 1
section("段 1 —— 最善の重み付きノルム")

op = TrinityOperator([0.5, 0.5], [1.0, 0.0], Q=np.array([[1.0, 40.0], [0.0, 1.0]]))
A = op.A
check("反例の A が [[0.5, 20], [0, 0.5]] である",
      np.allclose(A, [[0.5, 20.0], [0.0, 0.5]]))

kappa = 0.75
worst_over = 0.0
for w in ([1, 1], [1, 10], [1, 100], [1, 1000], [1, 0.01], [3, 0.2]):
    P = weighted_lyapunov(A, kappa, np.diag(w))
    worst_over = max(worst_over, achieved(A, P) - kappa)
check("どの W でも ‖A‖_P ≤ κ", worst_over <= 1e-9,
      "最大の超過 %.2e" % worst_over)

amps = [amplification(weighted_lyapunov(A, kappa, np.diag(w)))
        for w in ([1, 1], [1, 1000])]
check("係数のほうは W で動く", abs(amps[0] - amps[1]) > 1e-3,
      "%.4f と %.4f" % tuple(amps))

_, best_diag = optimize_weight(A, kappa, diagonal=True)
base = amplification(weighted_lyapunov(A, kappa, np.eye(2)))
check("対角の W に限ると改善しない", best_diag > base * 0.999,
      "決め打ち %.4f / 対角の最善 %.4f" % (base, best_diag))

for k in (0.55, 0.60, 0.75, 0.90, 0.99):
    _, best = optimize_weight(A, k)
    closed = jordan_optimum(0.5, 20.0, k)
    check("κ = %.2f で探索が閉じた式と一致する" % k,
          abs(best - closed) / closed < 1e-4,
          "探索 %.6f / 閉じた式 %.6f" % (best, closed))

# 閉じた式そのものを、相似変換の側から確かめる
for k in (0.55, 0.75, 0.99):
    t = jordan_optimum(0.5, 20.0, k)
    T = np.diag([1.0, t])
    check("閉じた式の t で ‖SAS⁻¹‖₂ = κ（κ = %.2f）" % k,
          abs(np.linalg.norm(T @ A @ np.linalg.inv(T), 2) - k) < 1e-9,
          "%.9f" % np.linalg.norm(T @ A @ np.linalg.inv(T), 2))

_, best = optimize_weight(A, 0.75)
err = op.error_curve([5.0, -3.0], steps=60)
bad = [i for i in range(len(err)) if err[i] > best * 0.75 ** i * err[0] * (1 + 1e-9)]
check("最善の上界でも全 61 段が内側", not bad, "破れた段 %s" % (bad[:3] or "なし"))
check("最善の上界は決め打ちより小さい", best < base, "%.4f < %.4f" % (best, base))

# ------------------------------------------------------------------ 段 2
section("段 2 —— 切り替え系")

A1, A2 = 0.7 * S, 0.7 * S.T
check("A₁ と A₂ はどちらも ρ < 1",
      max(np.max(np.abs(np.linalg.eigvals(M))) for M in (A1, A2)) < 1,
      "ρ = %.6f" % np.max(np.abs(np.linalg.eigvals(A1))))
check("積 A₂A₁ は ρ > 1", np.max(np.abs(np.linalg.eigvals(A2 @ A1))) > 1,
      "ρ = %.6f" % np.max(np.abs(np.linalg.eigvals(A2 @ A1))))
solo = simulate([A1, A2], (0,), [1.0, 1.0], 40)
alt = simulate([A1, A2], (0, 1), [1.0, 1.0], 40)
check("片方だけなら 0 へ行く", solo[-1] < 1e-3, "第 40 段 %.3e" % solo[-1])
check("交互にすると発散する", alt[-1] > 100, "第 40 段 %.4g" % alt[-1])

lo, hi = jsr_bounds([A1, A2], depth=6)
check("JSR の下界が上界を超えない", lo <= hi + 1e-12, "%.6f ≤ %.6f" % (lo, hi))
check("下界が 1 を超えるので発散が確定する", lo > 1, "下界 %.6f" % lo)

B1 = np.array([[0.4, 0.3], [0.0, 0.5]])
B2 = np.array([[0.5, 0.0], [0.2, 0.4]])
lo2, hi2 = jsr_bounds([B1, B2], depth=6)
_, w2 = common_lyapunov([B1, B2])
check("収束する対では JSR の上界が 1 未満", hi2 < 1, "上界 %.6f" % hi2)
check("共通の P が κ < 1 を出す", w2 < 1, "κ = %.6f" % w2)
check("共通の P が与える上界は JSR の下界を下回らない", w2 >= lo2 - 1e-9,
      "κ = %.6f / 下界 %.6f" % (w2, lo2))

phi = (1 + 5 ** 0.5) / 2
C1, C2 = S / phi, S.T / phi
lo3, hi3 = jsr_bounds([C1, C2], depth=7)
check("黄金比の対では JSR が 1 に挟まれる",
      abs(lo3 - 1) < 1e-6 and abs(hi3 - 1) < 1e-6,
      "%.9f ≤ JSR ≤ %.9f" % (lo3, hi3))
check("その場合に「収束する」と言わない（κ < 1 が出ない）",
      common_lyapunov([C1, C2])[1] >= 1 - 1e-6)

D3 = np.diag([0.5, 0.7, 0.3])
Q3 = cyclic_shift(3)
_, w4 = common_lyapunov([D3 @ Q3, D3 @ Q3.T])
check("三篇の設定は順逆どちらでも共通の P を持つ", w4 < 1, "κ = %.6f" % w4)

# ------------------------------------------------------------------ 段 3
section("段 3 —— 確率的な切り替え")

pair = lambda g: [g * S, g * S.T]      # noqa: E731
r1 = mean_square_radius(pair(1.0))
check("ρ(E[A⊗A]) が γ² に比例する",
      all(abs(mean_square_radius(pair(g)) - g * g * r1) < 1e-9
          for g in (0.5, 0.667, 0.9)),
      "ρ(1) = %.6f" % r1)

# 二乗平均の判定が、厳密な漸化式の伸び方と一致すること
g = 0.667
mats = pair(g)
x0 = np.array([1.0, 0.0])
Sig = second_moment(mats, np.outer(x0, x0), 300)
grow = (np.trace(Sig[300]) / np.trace(Sig[200])) ** (1 / 100.0)
check("E‖x‖² の伸び率が ρ(E[A⊗A]) に一致する",
      abs(grow - mean_square_radius(mats)) < 1e-6,
      "実測 %.9f / 理論 %.9f" % (grow, mean_square_radius(mats)))

lam1 = lyapunov_exponent(pair(1.0), steps=120000)
check("λ(γ) = log γ + λ(1) が成り立つ",
      all(abs(lyapunov_exponent(pair(gg), steps=120000)
              - (np.log(gg) + lam1)) < 1e-9 for gg in (0.5, 0.667)),
      "λ(1) = %.6f（推定）" % lam1)

g_as, g_ms = float(np.exp(-lam1)), float(1 / np.sqrt(r1))
check("窓が空でない（ほとんど確実の境目 > 二乗平均の境目）", g_as > g_ms,
      "%.6f > %.6f、幅 %.6f" % (g_as, g_ms, g_as - g_ms))
check("窓の中では二乗平均が発散し、ほとんど確実には収束する",
      mean_square_radius(pair(0.667)) > 1
      and lyapunov_exponent(pair(0.667), steps=120000) < 0,
      "γ = 0.667")
check("窓の外（γ = 0.5）ではどちらも収束する",
      mean_square_radius(pair(0.5)) < 1
      and lyapunov_exponent(pair(0.5), steps=120000) < 0)
check("三篇の設定では割れない",
      mean_square_radius([D3 @ Q3, D3 @ Q3.T]) < 1
      and lyapunov_exponent([D3 @ Q3, D3 @ Q3.T], steps=60000) < 0)

# ------------------------------------------------------------------ 段 4
section("段 4 —— 非線形な統合")

a4, p4 = [0.9, 0.9, 0.9], [0.0, 0.0, 0.0]
for beta, want in ((0.5, 1), (1.0, 1), (1.2, 3), (2.0, 3), (5.0, 3)):
    f, n = make_operator(a4, p4, beta)
    fps = find_fixed_points(f, n)
    check("β = %.1f で不動点が %d 個" % (beta, want), len(fps) == want,
          "見つかったのは %d 個" % len(fps))

f, n = make_operator(a4, p4, 5.0)
fps = find_fixed_points(f, n)
check("見つかった点はすべて f(x) = x を満たす",
      all(np.linalg.norm(f(x) - x) < 1e-8 for x in fps),
      "最大の残差 %.2e" % max(np.linalg.norm(f(x) - x) for x in fps))
rho0 = float(np.max(np.abs(np.linalg.eigvals(jacobian(f, np.zeros(3))))))
check("原点の ρ(Df) が a·β に一致する", abs(rho0 - 0.9 * 5.0) < 1e-6,
      "%.6f" % rho0)
check("原点はもう引き寄せない（ρ ≥ 1）", rho0 >= 1)
off = [x for x in fps if np.linalg.norm(x) > 1e-6]
check("原点以外の不動点は局所的に縮小する",
      all(np.max(np.abs(np.linalg.eigvals(jacobian(f, x)))) < 1 for x in off),
      "%d 点" % len(off))

w_small, _ = sampled_contraction(f, off[0], 0.1, samples=200, seed=1)
w_big, _ = sampled_contraction(f, off[0], 0.1, samples=4000, seed=1)
check("標本を増やすと最大値は下がらない", w_big >= w_small - 1e-12,
      "%.6f → %.6f" % (w_small, w_big))
check("β ≤ 1 の側では箱全体で縮小する",
      sampled_contraction(make_operator(a4, p4, 1.0)[0],
                          np.zeros(3), 2.0, samples=400)[0] < 1)

# ------------------------------------------------------------------ 段 5
section("段 5 —— 無限次元へ")

a5 = 0.9
for n in (2, 3, 5, 10, 50):
    Ao = weighted_shift(n, a5, cyclic=False)
    Ac = weighted_shift(n, a5, cyclic=True)
    check("n = %d：端で切ると ρ = 0" % n,
          np.max(np.abs(np.linalg.eigvals(Ao))) < 1e-12)
    check("n = %d：輪を閉じると ρ = a" % n,
          abs(np.max(np.abs(np.linalg.eigvals(Ac))) - a5) < 1e-9)
check("どちらも ‖A‖₂ = a",
      all(abs(np.linalg.norm(weighted_shift(n, a5, c), 2) - a5) < 1e-9
          for n in (3, 10, 50) for c in (True, False)))
n = 12
Ao = weighted_shift(n, a5, cyclic=False)
check("端で切った行列は冪零（Aⁿ = 0）",
      np.abs(np.linalg.matrix_power(Ao, n)).max() < 1e-12)
prof = transient_profile(Ao, n + 2)
check("‖Aᵏ‖ は第 n 段でちょうど 0 になる",
      prof[n - 2] > 1e-3 and prof[n - 1] < 1e-12,
      "第 %d 段 %.3e、第 %d 段 %.3e" % (n - 1, prof[n - 2], n, prof[n - 1]))
check("輪を閉じた側は n に依らず a²⁰ を返す",
      all(abs(transient_profile(weighted_shift(n, a5, True), 20)[-1]
              - a5 ** 20) < 1e-9 for n in (3, 5, 10, 50)))

# ------------------------------------------------------------- 実演が走る
section("実演が最後まで走るか")

import subprocess  # noqa: E402
for name in sorted(os.listdir(os.path.join(ROOT, "roadmap"))):
    if not name.startswith("stage") or not name.endswith(".py"):
        continue
    r = subprocess.run([sys.executable, os.path.join(ROOT, "roadmap", name)],
                       capture_output=True)
    check(name + " が終了コード 0 で終わる", r.returncode == 0,
          r.stderr.decode()[-160:] if r.returncode else "")

print("\n" + "-" * 58)
if failures:
    print("%d 件が通り、%d 件が通りませんでした。" % (passed, len(failures)))
    for f in failures:
        print("  - " + f)
    sys.exit(1)
print("%d 件すべて通りました。" % passed)
