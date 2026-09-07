#!/usr/bin/env python3
"""certificate.py が作る「縮小になる距離」を、名乗りどおりか確かめる。

    python3 verification/check_certificate.py

NumPy のみ。乱数種は固定。各項目が PASS / FAIL の 1 行を印字し、
すべて通ると終了コード 0 を返す。

check.py（22 項目）は trinity.py の主張を確かめる。ここは別立てである。
証書は「論文の議論を組み直した」と名乗るので、**組み直したものが本当に
バナッハの定理の条件を満たしているか**を、定義に戻って当たる必要がある。

具体的には次を確かめる。

    P は本当に方程式の解か（残差）
    ‖·‖_P は本当にノルムか（正値性・斉次性・三角不等式）
    f は本当にその距離で縮小写像か（二点間の距離で、乱数で当たる）
    κ は上界ではなく達成される値か（定義から計算し直して一致するか）
    保証した誤差の上界は、実際の反復を本当に覆っているか
    ρ ≥ 1 のときに、作れないものを作ったと言わないか
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from trinity import TrinityOperator, cyclic_shift        # noqa: E402
from certificate import certify, sweep                   # noqa: E402

rng = np.random.default_rng(20260907)
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


# 論文の条件（‖A‖₂ < 1）を満たさないのに収束する例。README と同じもの。
counter = TrinityOperator([0.5, 0.5], [1.0, 0.0],
                          Q=np.array([[1.0, 40.0], [0.0, 1.0]]))
cert = certify(counter)
A, P, n = cert.A, cert.P, cert.n

# ------------------------------------------------------- A. 前提の確認
section("A. そもそも論文の議論が壊れている例かどうか")

check("ρ(A) < 1（収束はする）", cert.rho < 1.0, "ρ = %.6f" % cert.rho)
check("‖A‖₂ ≥ 1（論文の条件は満たさない）", cert.euclidean >= 1.0,
      "‖A‖₂ = %.6f" % cert.euclidean)
check("ユークリッド距離では縮小写像ではない",
      not counter.monotone)

# ------------------------------------------------------- B. P が解である
section("B. P はリアプノフ方程式（Stein 方程式）の解か")

check("P が対称", np.abs(P - P.T).max() < 1e-12,
      "非対称成分 %.2e" % np.abs(P - P.T).max())
B = A / cert.gamma
res = np.abs(P - B.T @ P @ B - np.eye(n)).max()
check("P − BᵀPB = I", res < 1e-9, "残差 %.2e" % res)
check("residual() が同じ値を返す", abs(cert.residual() - res) < 1e-15)
w = np.linalg.eigvalsh(P)
check("P が正定値", w.min() > 0, "λmin = %.6f" % w.min())
check("P ⪰ I（P = Σ (Bᵀ)ᵏBᵏ なので）", w.min() >= 1.0 - 1e-9,
      "λmin = %.6f" % w.min())
try:
    np.linalg.cholesky(P)
    check("コレスキー分解が通る", True)
except np.linalg.LinAlgError:
    check("コレスキー分解が通る", False)
check("P = LLᵀ", np.abs(cert.L @ cert.L.T - P).max() < 1e-9)

# ------------------------------------------------------- C. ノルムである
section("C. ‖x‖_P はノルムか")

X = rng.normal(size=(500, n))
Y = rng.normal(size=(500, n))
check("‖0‖_P = 0", cert.norm(np.zeros(n)) == 0.0)
check("x ≠ 0 なら ‖x‖_P > 0",
      all(cert.norm(x) > 0 for x in X))
c = rng.normal(size=500)
check("斉次性 ‖cx‖_P = |c|‖x‖_P",
      max(abs(cert.norm(ci * x) - abs(ci) * cert.norm(x)) for ci, x in zip(c, X))
      < 1e-9)
check("三角不等式 ‖x+y‖_P ≤ ‖x‖_P + ‖y‖_P",
      all(cert.norm(x + y) <= cert.norm(x) + cert.norm(y) + 1e-9
          for x, y in zip(X, Y)))
n2 = np.linalg.norm(X, axis=1)
nP = np.array([cert.norm(x) for x in X])
check("√λmin ‖x‖₂ ≤ ‖x‖_P", (nP >= np.sqrt(w.min()) * n2 - 1e-9).all())
check("‖x‖_P ≤ √λmax ‖x‖₂", (nP <= np.sqrt(w.max()) * n2 + 1e-9).all())
check("ユークリッド距離と同値（∴ 完備、∴ バナッハが使える）",
      np.sqrt(w.min()) > 0 and np.isfinite(np.sqrt(w.max())))

# ------------------------------------------------------- D. 縮小写像である
section("D. その距離で f は縮小写像か")

check("κ < 1", cert.kappa < 1.0, "κ = %.6f" % cert.kappa)
check("κ < γ", cert.kappa < cert.gamma, "γ = %.6f" % cert.gamma)
check("ρ ≤ κ（これより小さくはできない）", cert.rho <= cert.kappa + 1e-12)
ratio = np.array([cert.norm(A @ x) / cert.norm(x) for x in X])
check("‖Ax‖_P ≤ κ‖x‖_P（500 本）", (ratio <= cert.kappa + 1e-9).all(),
      "最悪 %.9f" % ratio.max())
# バナッハの条件は A ではなく f についてのもの。二点間の距離で当たる。
d_before = np.array([cert.distance(x, y) for x, y in zip(X, Y)])
d_after = np.array([cert.distance(counter.step(x), counter.step(y))
                    for x, y in zip(X, Y)])
check("d_P(f(x), f(y)) ≤ κ d_P(x, y)（500 対）",
      (d_after <= cert.kappa * d_before + 1e-9).all(),
      "最悪 %.9f" % (d_after / d_before).max())
check("κ は上界ではなく ‖A‖_P そのもの",
      abs(cert.achieved() - cert.kappa) < 1e-9,
      "定義から %.9f / 名乗り %.9f" % (cert.achieved(), cert.kappa))
check("audit() の項目がすべて通る",
      all(v for v in cert.audit().values() if isinstance(v, bool)))

# ------------------------------------------------- E. バナッハの結論が出る
section("E. 出てくる結論は、論文が言っていたものと同じか")

x_star = counter.fixed_point()
starts = rng.normal(size=(20, n)) * 100
ends = []
for x in starts:
    for _ in range(500):
        x = counter.step(x)
    ends.append(x)
ends = np.array(ends)
check("どの初期値からも同じ点へ（一意性）",
      np.abs(ends - ends[0]).max() < 1e-9,
      "ばらつき %.2e" % np.abs(ends - ends[0]).max())
check("その点が (I − A)⁻¹b と一致",
      np.abs(ends[0] - x_star).max() < 1e-9)
check("f(x*) = x*", np.abs(counter.step(x_star) - x_star).max() < 1e-12)

# --------------------------------------------------- F. 上界が実際を覆う
section("F. 保証した誤差の上界は、実際の反復を覆うか")

# 上界は κᵏ で落ちるので、段を伸ばせば倍精度で表せる下限を割る。そこから先で
# ‖xₖ − x*‖ が上界を超えるのは、k 回の反復に溜まった丸め誤差が残るからであって、
# 不等式が破れたのではない。**その分だけは明示して許す。**
#
#     許容 = 16 ε (1 + ‖x*‖)(k + 1)      ε は倍精度の機械イプシロン
#
# 正規行列では上界が等号になるので、この項が無いと第 40 段あたりから落ちる。
# 逆に、この項を使わずに済んでいる段数も一緒に数えて出す。緩めた範囲が
# 見えないと、緩めたことにならない。

EPS = float(np.finfo(float).eps)


def covers(op_or_A, x0, steps, cert, b=None, x_star=None):
    """各段で上界を確かめる。返すのは (破れた段, 丸めの項が要った最初の段, 総段数)。"""
    if x_star is None:
        x_star = op_or_A.fixed_point()
    scale = 1.0 + float(np.linalg.norm(x_star))
    x = np.asarray(x0, dtype=float)
    e0 = float(np.linalg.norm(x - x_star))
    broke, first_noise = [], None
    for k in range(steps + 1):
        e = float(np.linalg.norm(x - x_star))
        bound = cert.bound(k, e0)
        if e > bound * (1 + 1e-9) and first_noise is None:
            first_noise = k
        if e > bound * (1 + 1e-9) + 16 * EPS * scale * (k + 1):
            broke.append(k)
        x = (op_or_A.step(x) if b is None else op_or_A @ x + b)
    return broke, first_noise, steps + 1


broke, noise_k, total = covers(counter, [5.0, -3.0], 60, cert)
err = counter.error_curve([5.0, -3.0], steps=60)
check("反例で全 %d 段が上界の内側" % total, not broke,
      "破れた段: %s" % (broke[:5] if broke else "なし"))
check("第 1 段では実際の誤差が初期値より大きい（増えてよい）",
      err[1] > err[0], "%.4f → %.4f" % (err[0], err[1]))
check("反例では丸めの項を使わずに全段が通る", noise_k is None,
      "丸めの項が要った最初の段: %s" % (noise_k if noise_k is not None else "なし"))

for label, op in (("Series I", TrinityOperator(0.6, [1, 0, 0])),
                  ("Series II", TrinityOperator([0.5, 0.7, 0.3], [1, 0, 0.5]))):
    c = certify(op)
    bad, nk, tot = covers(op, rng.normal(size=op.n), 60, c)
    check("%s でも全 %d 段が上界の内側" % (label, tot), not bad,
          "κ = %.6f  増幅 = %.4f  丸めの項が要った最初の段 %s"
          % (c.kappa, c.amplification, nk if nk is not None else "なし"))

bad_any, tried = 0, 0
for _ in range(20):
    m = int(rng.integers(2, 6))
    M = rng.normal(size=(m, m))
    M = M / (np.max(np.abs(np.linalg.eigvals(M))) / rng.uniform(0.2, 0.95))
    c = certify(M)
    bvec = rng.normal(size=m)
    xs = np.linalg.solve(np.eye(m) - M, bvec)
    bad, _, _ = covers(M, rng.normal(size=m) * 10, 80, c, b=bvec, x_star=xs)
    tried += 1
    if bad:
        bad_any += 1
check("乱数行列 %d 本（n = 2〜5、ρ ∈ [0.2, 0.95]）でも破れない" % tried,
      bad_any == 0, "破れた本数 %d" % bad_any)

# 正規行列では上界が等号になる。緩めていないことの裏取りとして、
# 「実際 ≤ 上界」だけでなく「上界が実際より桁違いに大きくはない」も見る。
c1 = certify(TrinityOperator(0.6, [1, 0, 0]))
check("正規行列では増幅が 1（上界が等号になる）",
      abs(c1.amplification - 1.0) < 1e-9, "増幅 = %.12f" % c1.amplification)
check("そのとき κ は ρ = ‖A‖₂ と一致",
      abs(c1.kappa - 0.6) < 1e-9, "κ = %.9f" % c1.kappa)

# ------------------------------------------------------------ G. γ の目盛り
section("G. γ を振ったときの釣り合い")

cs = sweep(counter)
ks = [c.kappa for c in cs]
amps = [c.amplification for c in cs]
check("γ が大きいほど κ も大きい（この例）",
      all(ks[i] < ks[i + 1] for i in range(len(ks) - 1)),
      "κ: " + ", ".join("%.4f" % k for k in ks))
check("γ が大きいほど増幅は小さい（この例）",
      all(amps[i] > amps[i + 1] for i in range(len(amps) - 1)),
      "増幅: " + ", ".join("%.1f" % a for a in amps))
check("どの γ でも κ < γ < 1",
      all(c.kappa < c.gamma < 1.0 for c in cs))
near = certify(counter, cert.rho + 0.01)
check("γ を ρ に寄せると κ は ρ に近づく（Ostrowski）",
      near.kappa <= cert.rho + 0.01,
      "γ = ρ + 0.01 で κ = %.6f（ρ = %.6f）" % (near.kappa, cert.rho))
check("そのぶん増幅は大きくなる", near.amplification > cert.amplification,
      "%.1f → %.1f" % (cert.amplification, near.amplification))

# ------------------------------------------------------- H. 作れないものは作らない
section("H. 適用範囲の外で、作れたと言わないか")

for label, M in (("ρ = 1（巡回置換そのもの）", cyclic_shift(3)),
                 ("ρ > 1", np.array([[1.5, 0.0], [0.0, 0.3]])),
                 ("ρ = 1 の非正規行列", np.array([[1.0, 5.0], [0.0, 1.0]]))):
    try:
        certify(M)
        check("%s で断る" % label, False, "作れたと言ってしまった")
    except ValueError:
        check("%s で断る" % label, True)

for label, kwargs in (("γ ≤ ρ", dict(gamma=0.4)),
                      ("γ ≥ 1", dict(gamma=1.0)),
                      ("γ が負", dict(gamma=-0.5))):
    try:
        certify(counter, **kwargs)
        check("%s を断る" % label, False)
    except ValueError:
        check("%s を断る" % label, True)

try:
    certify(np.zeros((2, 3)))
    check("非正方行列を断る", False)
except ValueError:
    check("非正方行列を断る", True)

check("TrinityOperator をそのまま渡せる",
      np.allclose(certify(counter).A, counter.A))
check("行列を直接渡しても同じ", np.allclose(certify(counter.A).P, cert.P))

# --------------------------------------------------------- I. 再現性
section("I. 再現性")

check("同じ入力から同じ κ", certify(counter).kappa == cert.kappa)
check("audit() が種を固定して同じ結果",
      cert.audit()["最悪の比 ‖Ax‖_P/‖x‖_P"]
      == cert.audit()["最悪の比 ‖Ax‖_P/‖x‖_P"])

print("\n" + "-" * 58)
if failures:
    print("%d 件が通り、%d 件が通りませんでした。" % (passed, len(failures)))
    for f in failures:
        print("  - " + f)
    sys.exit(1)
print("%d 件すべて通りました。" % passed)
