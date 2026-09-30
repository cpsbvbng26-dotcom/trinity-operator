#!/usr/bin/env python3
"""意見動学の二つの標準模型を、原典の側の記号で書き直して計算する。

    python3 standard.py

trinity.py は三篇の記号（D, Q, p）で書いている。ここは文献の側の記号で書く。
自分の記号で考えていたから、既知の模型だと気づかなかった。記号を寄せて計算し直す。

    DeGroot (1974)            x(k+1) = W x(k)
    Friedkin–Johnsen (1990)   x(k+1) = Λ W x(k) + (I − Λ) u

W は行確率行列（非負で、各行の和が 1）。Λ = diag(λ) は感受性で 0 ≤ λᵢ ≤ 1。
u は各主体がもともと持っていた意見。標準形の書き方は Proskurnikov & Tempo (2017) に拠る。

ここで確かめるのは、手で証明できる古典的な事実だけである。新しい結果は無い。

    1. DeGroot。W が原始的なら、意見は vᵀx(0) に揃う。v は W の左ペロン・ベクトル
       （vᵀW = vᵀ、和が 1）。誰の初期値がどれだけ効くかは v が決める。
    2. FJ。ρ(ΛW) < 1 なら x(k) → V u、V = (I − ΛW)⁻¹ (I − Λ)。
       V は行確率行列になる。(I − ΛW)𝟙 = 𝟙 − Λ𝟙 = (I − Λ)𝟙 から V𝟙 = 𝟙、
       非負性はノイマン級数 Σ (ΛW)ᵏ (I − Λ) から出る。
    3. 両者の関係。Λ = I なら FJ は DeGroot そのもの。三篇の作用素は W を巡回置換に
       限った FJ で、Λ = D、W = Q、u = p と読める。
    4. W が巡回置換なら、V は閉じた形で書ける。三篇の σ（主体 i が i − 1 を聞く）では

           V[i, i−k] = λᵢ λᵢ₋₁ ⋯ λᵢ₋ₖ₊₁ (1 − λᵢ₋ₖ) / (1 − λ₁ λ₂ ⋯ λₙ)   （k = 0, …, n−1）

       添字は mod n。(ΛW)ᵏ が一本の道の感受性の積になり、一周ごとに積 λ₁⋯λₙ が掛かる
       ので、ノイマン級数が等比級数として足せる。主体 j の初期意見が主体 i に残る重みは、
       j から i までの道の感受性の積で決まる。

       この形は三篇には無い。検索した範囲の文献では、有向の巡回に限ってこの形を明示した
       ものは見つけていない。見つけていないことは、無いことではない。等比級数を一度足せば
       出る式であり、新しい結果とは言わない。

NumPy のみ。乱数種は固定。
"""

import numpy as np

from trinity import TrinityOperator, cyclic_shift

__all__ = ["random_stochastic", "degroot_limit", "left_perron", "fj_influence", "fj_iterate",
           "fj_cyclic_closed_form"]


def random_stochastic(n, rng):
    """正の成分を持つ n×n の行確率行列。正なので原始的でもある。"""
    W = rng.random((n, n)) + 0.05
    return W / W.sum(axis=1, keepdims=True)


def left_perron(W):
    """vᵀW = vᵀ を満たし、和が 1 の左固有ベクトル。"""
    vals, vecs = np.linalg.eig(W.T)
    v = np.real(vecs[:, int(np.argmin(np.abs(vals - 1.0)))])
    return v / v.sum()


def degroot_limit(W, x0, steps=2000):
    x = np.asarray(x0, dtype=float)
    for _ in range(steps):
        x = W @ x
    return x


def fj_influence(W, lam):
    """V = (I − ΛW)⁻¹ (I − Λ)。均衡は V u。"""
    n = W.shape[0]
    L = np.diag(lam)
    return np.linalg.solve(np.eye(n) - L @ W, np.eye(n) - L)


def fj_cyclic_closed_form(lam):
    """W = cyclic_shift(n) のときの V を、逆行列を使わずに組む（上の 4.）。"""
    lam = np.asarray(lam, dtype=float)
    n = len(lam)
    total = float(np.prod(lam))
    V = np.zeros((n, n))
    for i in range(n):
        path = 1.0
        for k in range(n):
            j = (i - k) % n
            V[i, j] = path * (1.0 - lam[j]) / (1.0 - total)
            path *= lam[j]
    return V


def fj_iterate(W, lam, u, steps=2000):
    L = np.diag(lam)
    u = np.asarray(u, dtype=float)
    x = u.copy()
    for _ in range(steps):
        x = L @ W @ x + (np.eye(len(u)) - L) @ u
    return x


if __name__ == "__main__":
    np.set_printoptions(precision=6, suppress=True)
    W = np.array([[0.5, 0.3, 0.2],
                  [0.2, 0.6, 0.2],
                  [0.1, 0.4, 0.5]])
    x0 = np.array([1.0, 0.0, 0.5])

    print("1. DeGroot")
    v = left_perron(W)
    print("   左ペロン・ベクトル v =", v)
    print("   反復の極限          =", degroot_limit(W, x0))
    print("   vᵀx(0)             = %.6f" % (v @ x0))

    print("\n2. Friedkin–Johnsen")
    lam = np.array([0.8, 0.5, 0.9])
    V = fj_influence(W, lam)
    print("   V =\n", V)
    print("   行の和 =", V.sum(axis=1), "  最小成分 = %.6f" % V.min())
    print("   反復の極限 =", fj_iterate(W, lam, x0), "  V u =", V @ x0)

    print("\n3. 三篇の作用素は W を巡回置換に限った FJ")
    op = TrinityOperator([0.5, 0.7, 0.3], [1.0, 0.0, 0.5])
    Vc = fj_influence(cyclic_shift(3), op.a)
    print("   FJ の V u      =", Vc @ op.p)
    print("   trinity の x*  =", op.fixed_point())

    print("\n4. 巡回の場合の V の閉じた形")
    Vf = fj_cyclic_closed_form(op.a)
    print("   閉じた形の V =\n", Vf)
    print("   逆行列との差 = %.1e" % float(np.abs(Vf - Vc).max()))
