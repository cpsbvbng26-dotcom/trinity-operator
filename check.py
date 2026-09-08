#!/usr/bin/env python3
"""trinity.py の主張を確かめる。

    python3 check.py

NumPy のみ。乱数種は固定。各項目が PASS / FAIL の 1 行を印字し、
すべて通ると終了コード 0 を返す。
"""

import sys
import numpy as np
from trinity import TrinityOperator, cyclic_shift

rng = np.random.default_rng(20260906)
passed, failures = 0, []


def check(label, cond, detail=""):
    global passed
    if cond:
        print("  PASS  " + label + (("  " + detail) if detail else ""))
        passed += 1
    else:
        print("  FAIL  " + label + (("  " + detail) if detail else ""))
        failures.append(label)


def section(s):
    print("\n" + s)


# ------------------------------------------------- 論文の数値を再現する
section("A. 論文の数値")

s1 = TrinityOperator(0.6, [1, 0, 0])
want1 = np.array([0.510204, 0.306122, 0.183673])
check("Series I の不動点", np.abs(s1.fixed_point() - want1).max() < 5e-7,
      np.array2string(s1.fixed_point(), precision=6))

s2 = TrinityOperator([0.5, 0.7, 0.3], [1, 0, 0.5])
want2 = np.array([0.754190, 0.527933, 0.508380])
check("Series II の不動点", np.abs(s2.fixed_point() - want2).max() < 5e-7,
      np.array2string(s2.fixed_point(), precision=6))
check("Series II の縮小定数は max aᵢ", abs(s2.operator_norm - 0.7) < 1e-12,
      "‖A‖₂ = %.12f" % s2.operator_norm)

ok_n = True
for n in range(2, 9):
    op = TrinityOperator(0.6, rng.random(n))
    x = rng.random(n)
    for _ in range(400):
        x = op.step(x)
    ok_n &= np.abs(x - op.fixed_point()).max() < 1e-12
check("Series III: n = 2〜8 で同じ形が成り立つ", ok_n)

# ------------------------------------------------------ 閉形式と反復
section("B. 閉形式と反復の一致")

agree = True
for _ in range(20):
    n = int(rng.integers(2, 7))
    op = TrinityOperator(rng.uniform(0.1, 0.9, n), rng.random(n))
    x = rng.standard_normal(n) * 10
    for _ in range(600):
        x = op.step(x)
    agree &= np.abs(x - op.fixed_point()).max() < 1e-10
check("閉形式 (I−A)⁻¹b と反復の極限が一致する（20 例）", agree)

# ------------------------------------------ 論文の条件は必要条件ではない
section("C. 収束を決めているのは ρ(A) であって ‖A‖₂ ではない")

le = True
for _ in range(50):
    n = int(rng.integers(2, 6))
    op = TrinityOperator(rng.uniform(0.1, 1.5, n), rng.random(n),
                         Q=rng.standard_normal((n, n)))
    le &= op.spectral_radius <= op.operator_norm + 1e-9
check("常に ρ(A) ≤ ‖A‖₂", le)

perm = TrinityOperator(0.6, rng.random(5))
check("Q が置換かつ a 一様なら ρ = ‖A‖₂（論文の設定では区別が消える）",
      abs(perm.spectral_radius - perm.operator_norm) < 1e-12,
      "ρ = ‖A‖₂ = %.6f" % perm.spectral_radius)

check("Series II でも既に ρ < ‖A‖₂ になっている",
      s2.spectral_radius < s2.operator_norm - 1e-3,
      "ρ = %.6f < ‖A‖₂ = %.6f" % (s2.spectral_radius, s2.operator_norm))

# ρ < 1 ≤ ‖A‖₂ の例。論文の条件を満たさないが収束する。
counter = TrinityOperator([0.5, 0.5], [1.0, 0.0], Q=np.array([[1.0, 40.0], [0.0, 1.0]]))
check("論文の条件 ‖A‖₂ < 1 を満たさない例が作れる", counter.operator_norm > 1,
      "‖A‖₂ = %.4f" % counter.operator_norm)
check("それでも ρ < 1 なので収束する", counter.converges,
      "ρ = %.4f" % counter.spectral_radius)
x = np.array([5.0, -3.0])
for _ in range(200):
    x = counter.step(x)
check("実際に不動点へ行く", np.abs(x - counter.fixed_point()).max() < 1e-12,
      "差 %.1e" % np.abs(x - counter.fixed_point()).max())

# ------------------------------------------------------ 過渡的な増幅
section("D. ρ < 1 ≤ ‖A‖₂ では誤差がいったん増える")

err = counter.error_curve([5.0, -3.0], steps=40)
check("誤差の最大が初期値を上回る", err.max() > err[0] * 2,
      "初期 %.3f → 最大 %.3f（第 %d 段）" % (err[0], err.max(), int(np.argmax(err))))
check("最終的には減衰する", err[-1] < 1e-6, "最終 %.2e" % err[-1])
check("過渡的増幅が 1 を超える", counter.transient_growth() > 1,
      "maxₖ‖Aᵏ‖₂ = %.2f" % counter.transient_growth())
check("論文の設定では過渡的増幅が起きない",
      abs(s2.transient_growth() - 1.0) < 1e-9, "maxₖ‖Aᵏ‖₂ = 1")

# ---------------------------------------------------------- 境界
section("E. 境界は ρ(A) = 1")

below = TrinityOperator([1.0, 1.0], [1.0, 0.0], Q=np.array([[0.99, 30.0], [0.0, 0.99]]))
above = TrinityOperator([1.0, 1.0], [1.0, 0.0], Q=np.array([[1.01, 30.0], [0.0, 1.01]]))
check("ρ < 1 側は収束すると判定される", below.converges, "ρ = %.4f" % below.spectral_radius)
check("ρ > 1 側は収束しないと判定される", not above.converges, "ρ = %.4f" % above.spectral_radius)
check("‖A‖₂ は両側でほぼ同じで、判定に使えない",
      abs(below.operator_norm - above.operator_norm) < 0.1,
      "%.2f と %.2f" % (below.operator_norm, above.operator_norm))
xa = np.array([1.0, 1.0])
for _ in range(300):
    xa = above.step(xa)
check("ρ > 1 では実際に発散する", not np.all(np.isfinite(xa)) or np.linalg.norm(xa) > 1e5,
      "300 段後の大きさ %.3g" % np.linalg.norm(xa))

# ------------------------------------------------ 等長性も置換も要らない
section("F. 置換であることも等長であることも本質ではない")

for label, Qx in (("ランダムな直交行列", np.linalg.qr(rng.standard_normal((4, 4)))[0]),
                  ("非正規・非直交", rng.standard_normal((4, 4)) * 0.35),
                  ("特異行列（rank 1）", np.outer(rng.random(4), rng.random(4)))):
    op = TrinityOperator(0.6, rng.random(4), Q=Qx)
    if not op.converges:
        check(label + " でも収束する", False, "ρ = %.4f" % op.spectral_radius)
        continue
    x = rng.random(4)
    for _ in range(500):
        x = op.step(x)
    check(label + " でも収束する", np.abs(x - op.fixed_point()).max() < 1e-10,
          "ρ = %.4f  ‖A‖₂ = %.4f" % (op.spectral_radius, op.operator_norm))

# ------------------------------------------- 論文の設定での閉じた式
section("F. 置換の場合の閉じた式")

# 論文は Q を置換に限っている。その範囲なら固有値も特異値も手で書ける。
# 論文はこの構造を使わず、縮小定数として max aᵢ を挙げた。それは ‖A‖₂
# ちょうどであって、収束率ではない。収束率は巡回ごとの幾何平均である。

check("Series II で ρ が巡回内の幾何平均と一致する",
      abs(s2.spectral_radius - s2.closed_form_radius) < 1e-12,
      "ρ = %.12f / 幾何平均 = %.12f" % (s2.spectral_radius, s2.closed_form_radius))
check("Series II で ‖A‖₂ が max aᵢ と一致する",
      abs(s2.operator_norm - s2.closed_form_norm) < 1e-12,
      "‖A‖₂ = %.12f / max aᵢ = %.12f" % (s2.operator_norm, s2.closed_form_norm))
check("Series II では幾何平均が最大値より真に小さい",
      s2.closed_form_radius < s2.closed_form_norm - 1e-9,
      "%.6f < %.6f  比 %.4f 倍" % (s2.closed_form_radius, s2.closed_form_norm,
                                    s2.closed_form_norm / s2.closed_form_radius))
check("Series I では両者が一致する（a が一様だから）",
      abs(s1.closed_form_radius - s1.closed_form_norm) < 1e-12,
      "どちらも %.6f。**区別の存在しない設定から始めている**" % s1.closed_form_radius)

# 巡回が一つとは限らない。置換一般で成り立つことを、乱数で確かめる。
bad_r, bad_n, worst = [], [], 0.0
for _ in range(200):
    n = int(rng.integers(2, 8))
    Qx = np.eye(n)[rng.permutation(n)]
    a = rng.uniform(0.05, 0.95, n)
    op = TrinityOperator(a, rng.random(n), Q=Qx)
    dr = abs(op.spectral_radius - op.closed_form_radius)
    dn = abs(op.operator_norm - op.closed_form_norm)
    worst = max(worst, dr, dn)
    if dr > 1e-10:
        bad_r.append(dr)
    if dn > 1e-10:
        bad_n.append(dn)
check("置換 200 通りで ρ が閉じた式と一致する", not bad_r,
      "最大差 %.1e" % worst)
check("置換 200 通りで ‖A‖₂ が max aᵢ と一致する", not bad_n,
      "最大差 %.1e" % worst)

# 置換でないものには、この式を当ててはならない。
non_perm = TrinityOperator(0.6, rng.random(4),
                           Q=np.linalg.qr(rng.standard_normal((4, 4)))[0])
check("置換でない Q には閉じた式を返さない",
      non_perm.closed_form_radius is None and non_perm.cycles is None)

# ---------------------------------------------------------------- 結果
print("\n" + "-" * 60)
if failures:
    print("%d 件が通り、%d 件が通りませんでした。" % (passed, len(failures)))
    for f in failures:
        print("  - " + f)
    sys.exit(1)
print("%d 件すべて通りました。" % passed)
