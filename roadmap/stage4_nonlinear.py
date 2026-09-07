#!/usr/bin/env python3
"""段 4 —— 統合が線形でなくなったら。「唯一の不動点」は線形の性質である。

    python3 roadmap/stage4_nonlinear.py

三篇の作用素は線形である。だが「三つの要素を統合する」を素直に読めば、統合が
線形でなければならない理由は無い。飽和があってもよいし、正規化があってもよい。

    x ← D g(Q x) + (I − D) p,      g は成分ごとの非線形写像

ここで三篇の結論のうち**一つが落ちる。**

    収束する            条件つきで残る（局所的な縮小として）
    不動点が唯一である  **落ちる。** 複数の不動点を持ちうる

「唯一性」はバナッハの定理が全空間で使えるときの帰結であって、統合という
考え方そのものから出てくるものではない。g が急になると、同じ作用素が
複数の落ち着き先を持つ。

この段でやること。

  1. g が非拡大（|g'| ≤ 1）なら、線形の結論がそのまま残ることを確かめる
  2. g を急にすると不動点が増えることを、実際に数え上げて見せる
  3. 増えた不動点それぞれのまわりで、局所的な縮小を段 1 の道具で証明する
  4. **その証明が「標本による評価」であって「証明」ではない**ことを明示する

4 が重要である。箱の中で ‖Df‖ の最大を標本で取っても、標本の外は分からない。
区間演算か、Df のリプシッツ定数の評価が要る。**そこまでは NumPy を回すだけでは
届かない。**届かないことを、届いたふりで埋めない。

NumPy のみ。乱数種は固定。
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from trinity import cyclic_shift  # noqa: E402
from certificate import certify  # noqa: E402

__all__ = ["make_operator", "jacobian", "sampled_contraction",
           "find_fixed_points"]


def make_operator(a, p, beta, Q=None):
    """f(x) = D tanh(β Q x) + (I − D) p を返す。

    β は統合の「急さ」である。ヤコビ行列は Df(x) = D · diag(β sech²(β Qx)) · Q
    なので、原点では D(βQ)。**β ≤ 1 なら g は非拡大**で、線形の場合と同じ
    ことしか起きない。β を上げると原点が不安定になり、落ち着き先が割れる。
    """
    a = np.asarray(a, dtype=float)
    p = np.asarray(p, dtype=float)
    n = a.size
    Q = cyclic_shift(n) if Q is None else np.asarray(Q, dtype=float)
    D = np.diag(a)
    const = (np.eye(n) - D) @ p

    def f(x):
        return D @ np.tanh(beta * (Q @ np.asarray(x, dtype=float))) + const

    return f, n


def jacobian(f, x, h=1e-6):
    """数値微分でヤコビ行列を取る。中心差分。"""
    x = np.asarray(x, dtype=float)
    n = x.size
    J = np.zeros((n, n))
    for j in range(n):
        e = np.zeros(n)
        e[j] = h
        J[:, j] = (f(x + e) - f(x - e)) / (2 * h)
    return J


def sampled_contraction(f, center, radius, P=None, samples=4000, seed=20260907):
    """箱の中で ‖Df‖_P の最大を**標本で**取る。

    返すのは (最大値, 使った P)。標本の外は見ていないので、**上界ではない。**
    名前に sampled と入れてあるのは、そこを取り違えないため。
    """
    center = np.asarray(center, dtype=float)
    n = center.size
    if P is None:
        J0 = jacobian(f, center)
        cert = certify(J0)
        P = cert.P
    L = np.linalg.cholesky(P)
    rng = np.random.default_rng(seed)
    worst = 0.0
    pts = np.vstack([center, center + rng.uniform(-radius, radius, size=(samples, n))])
    for x in pts:
        J = jacobian(f, x)
        N = L.T @ J
        G = np.array([np.linalg.solve(L, N[i]) for i in range(n)])
        worst = max(worst, float(np.linalg.norm(G, 2)))
    return worst, P


def find_fixed_points(f, n, trials=600, spread=3.0, seed=20260907, tol=1e-10):
    """f(x) = x を多点から Newton 法で解き、重複を潰して返す。

    見つかった点は**見つかったものだけ**である。全部見つけた保証は無い。
    """
    rng = np.random.default_rng(seed)
    found = []
    # 原点は必ず起点に入れる。反発的な不動点は乱数の起点からは拾えないため。
    starts = [np.zeros(n)] + [rng.uniform(-spread, spread, size=n)
                              for _ in range(trials)]
    for x in starts:
        x = np.array(x, dtype=float)
        for _ in range(200):
            r = f(x) - x
            if np.linalg.norm(r) < tol:
                break
            J = jacobian(f, x) - np.eye(n)
            try:
                step = np.linalg.solve(J, -r)
            except np.linalg.LinAlgError:
                break
            x = x + step
            if not np.all(np.isfinite(x)) or np.linalg.norm(x) > 1e6:
                break
        else:
            continue
        if np.linalg.norm(f(x) - x) > 1e-8:
            continue
        if not any(np.linalg.norm(x - y) < 1e-6 for y in found):
            found.append(x)
    return sorted(found, key=lambda v: tuple(np.round(v, 6)))


if __name__ == "__main__":
    np.set_printoptions(precision=6, suppress=True)

    def title(s):
        print("\n" + s)
        print("-" * 72)

    a = [0.9, 0.9, 0.9]
    p = [0.0, 0.0, 0.0]

    title("1. β ≤ 1 なら g は非拡大で、線形の結論がそのまま残る")
    for beta in (0.2, 0.5, 1.0):
        f, n = make_operator(a, p, beta)
        fps = find_fixed_points(f, n)
        worst, _ = sampled_contraction(f, np.zeros(n), 2.0)
        print("  β = %.1f   不動点 %d 個   箱 |xᵢ| ≤ 2 での標本最大 ‖Df‖_P = %.6f"
              % (beta, len(fps), worst))
    print("""
  |d tanh(βx)/dx| ≤ β なので、β ≤ 1 なら g は非拡大である。ヤコビ行列は
  ‖Df‖ ≤ max aᵢ · β ≤ 0.9 で、**箱のどこでも縮小**。不動点は一つのまま。
  ここまでは三篇の結論がそのまま生き残る。""")

    title("2. 急にすると、不動点が増える")
    print("   β    不動点   原点の ρ(Df)   見つかった不動点の第 1 成分")
    for beta in (1.0, 1.2, 2.0, 3.0, 5.0):
        f, n = make_operator(a, p, beta)
        fps = find_fixed_points(f, n)
        rho0 = float(np.max(np.abs(np.linalg.eigvals(jacobian(f, np.zeros(n))))))
        firsts = "  ".join("%+.4f" % v[0] for v in fps[:5])
        print("  %.1f  %6d   %11.4f    %s" % (beta, len(fps), rho0, firsts))
    print("""
  β を上げると原点の ρ(Df) が 1 を跨ぐ。**原点は不動点のまま残るが、もう
  引き寄せない。**代わりに ±0.9 付近の二点が現れ、初期値によってどちらへ行くかが
  決まる。同じ作用素が、複数の落ち着き先を持つ。

  三篇の「任意の初期値から唯一の不動点へ収束する」は、統合という考え方から
  出てくる結論ではない。**線形だから出ていた。**""")

    title("3. 増えた不動点のまわりで、局所的な縮小を証明する")
    beta = 5.0
    f, n = make_operator(a, p, beta)
    fps = find_fixed_points(f, n)
    print("  β = %.1f、不動点 %d 個。それぞれのまわりの箱で見る。" % (beta, len(fps)))
    print("\n   不動点                     ρ(Df)     ‖Df‖₂    箱の半径   標本最大 ‖Df‖_P")
    for x in fps:
        J = jacobian(f, x)
        rho = float(np.max(np.abs(np.linalg.eigvals(J))))
        nrm = float(np.linalg.norm(J, 2))
        if rho >= 1:
            print("  %-24s  %.6f  %.6f      —        （縮小にならない）"
                  % (np.array2string(x, precision=3), rho, nrm))
            continue
        for radius in (0.30, 0.10, 0.03):
            worst, _ = sampled_contraction(f, x, radius, samples=800)
            if worst < 1:
                print("  %-24s  %.6f  %.6f    %.2f       %.6f"
                      % (np.array2string(x, precision=3), rho, nrm, radius, worst))
                break
        else:
            print("  %-24s  %.6f  %.6f      —        （箱を縮めても 1 未満にならず）"
                  % (np.array2string(x, precision=3), rho, nrm))
    print("""
  ρ(Df) < 1 の不動点のまわりでは、段 1 で作った距離を使えば縮小になる。
  **その距離は不動点ごとに違う。**一つの距離で全部を覆うことはできない。
  覆えるなら不動点は一つしかないはずだからである。""")

    title("4. いま出したものは、証明ではない")
    x = fps[0]
    for radius, samples in ((0.1, 200), (0.1, 2000), (0.1, 20000)):
        worst, _ = sampled_contraction(f, x, radius, samples=samples, seed=1)
        print("  標本 %6d 点   最大 ‖Df‖_P = %.6f" % (samples, worst))
    print("""
  標本を増やすと最大値は上がる。**上がり続けるのか、どこかで止まるのかは、
  標本からは分からない。**箱の中の本当の最大を押さえるには

    区間演算で ‖Df(x)‖ の上界を箱ごと評価する、または
    Df のリプシッツ定数 M を出して「中心の値 + M×半径」で押さえる

  のどちらかが要る。**どちらも NumPy を回すだけでは出ない。**
  ここが、この方向での「コードで言い切れる」の限界線である。""")

    print("\n" + "-" * 72)
    print("""独自性。非線形写像の局所的な縮小も、不動点の分岐も、力学系の教科書の
題材である。tanh を使った多安定も、神経回路の文脈でよく知られている
（Hopfield 1984 以来）。ここに新しい数学は無い。**新しいのは、三篇の作用素を
非線形に読み替えると「唯一性」が最初に落ちる、と具体的に示したことだけ。**

合法性。実装は外部から持ち込んでいない。文献は「既知である」ことの出典として
挙げているだけである。

限界。上の 4 節のとおり、局所的な縮小は**標本による評価**であって証明ではない。
論文にするなら区間演算が要る。ここでそれを「証明した」と書けば、それは誇張に
なる。書かない。""")
