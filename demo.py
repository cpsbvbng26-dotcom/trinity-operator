#!/usr/bin/env python3
"""論文が置いた仮定の、どこまでが本質だったかを実行して見せる。

    python3 demo.py

NumPy のみ。乱数種は固定。
"""

import numpy as np
from trinity import TrinityOperator, cyclic_shift

np.set_printoptions(precision=6, suppress=True)
rng = np.random.default_rng(20260906)


def title(s):
    print("\n" + s)
    print("-" * 68)


# ---------------------------------------------------------------- 1
title("1. 論文の数値を再現する")

s1 = TrinityOperator(0.6, [1, 0, 0])
print("Series I   x* =", s1.fixed_point(), " 論文 [0.510204 0.306122 0.183673]")
s2 = TrinityOperator([0.5, 0.7, 0.3], [1, 0, 0.5])
print("Series II  x* =", s2.fixed_point(), " 論文 [0.754190 0.527933 0.508380]")
print("Series III n = 2〜8 で同じ形が成り立つ:")
for n in range(2, 9):
    op = TrinityOperator(0.6, rng.random(n))
    x = rng.random(n)
    for _ in range(400):
        x = op.step(x)
    print("   n=%d  ρ=%.4f  ‖A‖₂=%.4f  収束先との差 %.1e"
          % (n, op.spectral_radius, op.operator_norm,
             np.abs(x - op.fixed_point()).max()))

# ---------------------------------------------------------------- 2
title("2. 論文の条件は十分条件であって、必要条件ではない")

print("三本が使う条件は ‖A‖₂ < 1（Q が置換で a < 1 なら自動的に成り立つ）。")
print("だが収束を決めているのは ρ(A) < 1 のほうである。ρ ≤ ‖A‖₂ なので、")
print("論文の条件は必要以上に強い。両者が離れる例を作る。\n")

# Q を置換から外す。上三角のずれを大きくすると、非正規性が効く。
Q = np.array([[1.0, 40.0],
              [0.0, 1.0]])
op = TrinityOperator([0.5, 0.5], [1.0, 0.0], Q=Q)
print(op.report())
print("\n論文の条件（‖A‖₂ < 1）を満たさない。それでも収束する。")
print("  x* =", op.fixed_point())
x = np.array([5.0, -3.0])
for _ in range(200):
    x = op.step(x)
print("  200 段後 =", x, "  差 %.1e" % np.abs(x - op.fixed_point()).max())

# ---------------------------------------------------------------- 3
title("3. その場合、誤差は初手から減らない —— いったん増える")

print("論文は「初手から幾何的に減衰する」と読める書き方をしている。")
print("‖A‖₂ < 1 のときはそのとおりだが、ρ < 1 ≤ ‖A‖₂ では成り立たない。\n")

for label, o in (("Series II（論文の設定）", s2), ("上の非正規な例", op)):
    err = o.error_curve([5.0, -3.0] if o.n == 2 else [0.9, 0.1, 0.4], steps=40)
    grew = int(np.argmax(err)) if err[0] < err.max() else 0
    print("%s" % label)
    print("   ‖A‖₂ = %.3f   誤差 %.3f → %.3f → %.3f → … → %.2e"
          % (o.operator_norm, err[0], err[1], err[2], err[-1]))
    print("   最大は第 %d 段（初期値の %.1f 倍）  過渡的増幅 maxₖ‖Aᵏ‖₂ = %.2f\n"
          % (grew, err.max() / err[0], o.transient_growth()))

# ---------------------------------------------------------------- 4
title("4. 境界は ρ(A) = 1 にある")

print("ρ を 1 の前後でまたぐと、挙動が切り替わる。")
print("‖A‖₂ はどちらの側でも 1 を超えたままで、判定には使えない。\n")
for r in (0.90, 0.99, 1.00, 1.01, 1.10):
    Qr = np.array([[r, 30.0], [0.0, r]])
    o = TrinityOperator([1.0, 1.0], [1.0, 0.0], Q=Qr)   # a=1 で A = Q
    x = np.array([1.0, 1.0])
    for _ in range(300):
        x = o.step(x)
    size = np.linalg.norm(x)
    print("   ρ = %.2f   ‖A‖₂ = %6.2f   300 段後の大きさ %s"
          % (o.spectral_radius, o.operator_norm,
             ("%.4f" % size) if np.isfinite(size) and size < 1e6 else "発散"))

# ---------------------------------------------------------------- 5
title("5. 「三」でも「置換」でも「等長」でもなくてよい")

print("Series III は 3 → n を示した。等長性まで外せる。")
print("必要なのは ρ(DQ) < 1 の一点だけである。\n")
for label, Qx in (
    ("巡回置換（論文）", cyclic_shift(4)),
    ("ランダムな直交行列", np.linalg.qr(rng.standard_normal((4, 4)))[0]),
    ("非正規・非直交", rng.standard_normal((4, 4)) * 0.35),
    ("特異行列（rank 1）", np.outer(rng.random(4), rng.random(4))),
):
    o = TrinityOperator(0.6, rng.random(4), Q=Qx)
    if o.converges:
        x = rng.random(4)
        for _ in range(500):
            x = o.step(x)
        note = "収束（差 %.1e）" % np.abs(x - o.fixed_point()).max()
    else:
        note = "収束しない"
    print("   %-20s ρ=%.4f  ‖A‖₂=%.4f  %s" % (label, o.spectral_radius, o.operator_norm, note))

print("\n" + "=" * 68)
print("この系列が本当に必要としていた条件は ρ(DQ) < 1 だけである。")
print("Q が置換であること、a が (0,1) にあること、要素が三つであることは、")
print("いずれもその十分条件を作るための道具にすぎない。")
