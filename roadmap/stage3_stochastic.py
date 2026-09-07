#!/usr/bin/env python3
"""段 3 —— 統合の仕方が偶然で決まるなら。二つの「収束」が割れる。

    python3 roadmap/stage3_stochastic.py

段 2 は「敵が最悪の順で切り替える」場合を見た。ここは「毎回くじで決まる」場合。

    x ← A_{ξₖ} x,      ξₖ は独立同分布

このとき**「収束する」に二つの意味があり、一致しない。**

    ほとんど確実な収束   λ = lim (1/k) log‖A_{ξₖ}⋯A_{ξ₁}‖ < 0
                        （リアプノフ指数。ほぼすべての道筋で 0 へ行く）
    二乗平均の収束       ρ(E[A ⊗ A]) < 1
                        （E‖xₖ‖² → 0）

二乗平均が収束すれば、ほとんど確実にも収束する。**逆は成り立たない。**
ほとんどすべての道筋が 0 へ行くのに、平均は発散する、という状態がある。
めったに起きない道筋が、起きたときに極端に大きくなるためである。

三篇は決定的な一つの作用素しか扱っていないので、この区別は現れない。
しかし「統合の仕方が状況で変わる」という読み方をした瞬間、**どちらの意味で
収束と言っているのかを決めないと、文が意味を持たなくなる。**

この段でやること。

  1. 二乗平均の判定を厳密に計算する（E[A⊗A] のスペクトル半径。近似ではない）
  2. リアプノフ指数を乱数で推定する（こちらは推定であって厳密ではない）
  3. 両者が割れる γ の窓を、実際に見つけて中を見る
  4. その窓の中で「ほとんどの道筋は 0 へ、平均は発散」を数字で出す

2 だけが推定であることを、出力にも明記する。

NumPy のみ。乱数種は固定。
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

__all__ = ["mean_square_radius", "lyapunov_exponent", "second_moment",
           "quantiles"]


def mean_square_radius(mats, probs=None):
    """ρ(E[A ⊗ A])。二乗平均で収束するかどうかは、これだけで決まる。

    E[xₖ₊₁ xₖ₊₁ᵀ] = E[A (xₖ xₖᵀ) Aᵀ] は Σ について線形なので、vec を取ると
    行列 E[A ⊗ A] の掛け算になる。**厳密な判定である。**
    """
    mats = [np.asarray(M, dtype=float) for M in mats]
    if probs is None:
        probs = np.full(len(mats), 1.0 / len(mats))
    M = sum(p * np.kron(A, A) for p, A in zip(probs, mats))
    return float(np.max(np.abs(np.linalg.eigvals(M))))


def second_moment(mats, Sigma0, steps, probs=None):
    """E[xₖ xₖᵀ] の列を厳密に回す。乱数を使わない。"""
    mats = [np.asarray(M, dtype=float) for M in mats]
    if probs is None:
        probs = np.full(len(mats), 1.0 / len(mats))
    S = np.asarray(Sigma0, dtype=float)
    out = [S.copy()]
    for _ in range(steps):
        S = sum(p * (A @ S @ A.T) for p, A in zip(probs, mats))
        out.append(S.copy())
    return out


def lyapunov_exponent(mats, probs=None, steps=200000, seed=20260907):
    """リアプノフ指数を乱数で推定する。**推定であって、厳密な値ではない。**

    各段でノルムを 1 に戻しながら log を足す。桁あふれを避けるため。
    """
    mats = [np.asarray(M, dtype=float) for M in mats]
    n = mats[0].shape[0]
    if probs is None:
        probs = np.full(len(mats), 1.0 / len(mats))
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(mats), size=steps, p=probs)
    v = np.ones(n) / np.sqrt(n)
    total = 0.0
    for i in idx:
        v = mats[i] @ v
        nv = float(np.linalg.norm(v))
        total += np.log(nv)
        v /= nv
    return total / steps


def quantiles(mats, x0, steps, paths=4000, probs=None, seed=20260907):
    """道筋を多数走らせ、‖xₖ‖ の中央値と平均を返す。両方見ないと割れが見えない。"""
    mats = [np.asarray(M, dtype=float) for M in mats]
    if probs is None:
        probs = np.full(len(mats), 1.0 / len(mats))
    rng = np.random.default_rng(seed)
    X = np.tile(np.asarray(x0, dtype=float), (paths, 1))
    med, mean_sq = [], []
    for k in range(steps + 1):
        nrm = np.linalg.norm(X, axis=1)
        med.append(float(np.median(nrm)))
        mean_sq.append(float(np.mean(nrm ** 2)))
        pick = rng.choice(len(mats), size=paths, p=probs)
        for i in range(len(mats)):
            sel = pick == i
            if sel.any():
                X[sel] = X[sel] @ mats[i].T
    return np.array(med), np.array(mean_sq)


if __name__ == "__main__":
    np.set_printoptions(precision=6, suppress=True)

    def title(s):
        print("\n" + s)
        print("-" * 72)

    S = np.array([[1.0, 1.0], [0.0, 1.0]])
    pair = lambda g: [g * S, g * S.T]      # noqa: E731

    title("1. 二つの判定は、そもそも別の量である")
    print("   γ      ρ(E[A⊗A])    二乗平均      リアプノフ指数 λ    ほとんど確実")
    for g in (0.50, 0.60, 0.6622, 0.6670, 0.6728, 0.70, 0.80):
        r = mean_square_radius(pair(g))
        lam = lyapunov_exponent(pair(g))
        print("  %.4f   %9.6f   %s   %+12.6f   %s"
              % (g, r, "収束  " if r < 1 else "発散  ",
                 lam, "収束" if lam < 0 else "発散"))
    print("""
  上から下へ見ると、二つの列の切り替わる場所がずれている。**ずれた区間が、
  「ほとんど確実には収束するのに、平均は発散する」場所である。**""")

    title("2. 境目を、それぞれの理屈から出す")
    lam1 = lyapunov_exponent(pair(1.0))
    r1 = mean_square_radius(pair(1.0))
    g_as = float(np.exp(-lam1))
    g_ms = float(1.0 / np.sqrt(r1))
    print("  γ = 1 のとき  λ = %.6f（推定）,  ρ(E[A⊗A]) = %.6f（厳密）" % (lam1, r1))
    print("  λ(γ) = log γ + λ(1) なので、ほとんど確実な境目は γ = e^(−λ(1)) = %.6f" % g_as)
    print("  ρ(γ) = γ²ρ(1)     なので、二乗平均の境目は γ = 1/√ρ(1) = %.6f" % g_ms)
    print("  窓の幅 %.6f  ← ここが割れる区間" % (g_as - g_ms))

    title("3. 窓の中を見る")
    g = 0.667
    mats = pair(g)
    r = mean_square_radius(mats)
    lam = lyapunov_exponent(mats)
    print("  γ = %.3f" % g)
    print("  ρ(E[A⊗A]) = %.6f > 1   → 二乗平均では発散する（厳密）" % r)
    print("  λ = %+.6f < 0          → ほとんど確実に 0 へ行く（推定）" % lam)

    x0 = np.array([1.0, 0.0])
    Sig = second_moment(mats, np.outer(x0, x0), 400)
    med, mean_sq = quantiles(mats, x0, 400, paths=4000)
    print("\n   段    E‖x‖²（厳密）   標本平均‖x‖²    中央値‖x‖")
    for k in (0, 50, 100, 200, 300, 400):
        print("  %3d   %13.4g   %13.4g   %12.4g"
              % (k, np.trace(Sig[k]), mean_sq[k], med[k]))
    print("""
  厳密な E‖x‖² は増え続ける。中央値は減り続ける。**同じ系である。**
  4000 本の標本平均は厳密な値のまわりで大きく振れる（第 300 段で 2 倍ずれる）。
  平均を作っているのはめったに出ない道筋なので、本数が足りないと当たらない。
  **「平均が発散する」を標本平均で確かめようとすると、こういう当てにならなさが
  出る。**厳密な漸化式を回すほうを正としているのは、そのためである。""")

    title("4. 三篇の設定では割れない")
    from trinity import cyclic_shift  # noqa: E402
    D = np.diag([0.5, 0.7, 0.3])
    Q = cyclic_shift(3)
    mats3 = [D @ Q, D @ Q.T]
    r3 = mean_square_radius(mats3)
    lam3 = lyapunov_exponent(mats3)
    print("  順方向と逆方向を等確率で引く")
    print("  ρ(E[A⊗A]) = %.6f < 1、λ = %+.6f < 0。どちらの意味でも収束する。"
          % (r3, lam3))
    print("""
  ここでも通る理由は段 2 と同じで、置換が等長だからである。
  **一般の Q に替えれば、この二つは割れうる。**""")

    print("\n" + "-" * 72)
    print("""独自性。ρ(E[A⊗A]) < 1 が二乗平均安定の必要十分条件であることも、
リアプノフ指数との食い違いも、確率的な線形系の標準的な事実である
（Kozin 1969 の総説、Bougerol–Lacroix 1985 など）。ここに新しい数学は無い。
**新しいのは、三篇の作用素を確率的に読み替えたときに、この区別が必ず要る、
という指摘と、割れる窓を数字で出したことだけ。**

合法性。実装は外部から持ち込んでいない。文献は「既知である」ことの出典として
挙げているだけで、内容を引き写してはいない。

正直に言うべき限界。λ は乱数による推定であって、厳密な値ではない。**上下から
挟んでいない。**窓の境目 %.6f も、その推定に依存している。厳密にやるには
不変測度を押さえる必要があり、それは NumPy を回すだけでは届かない。""" % g_as)
