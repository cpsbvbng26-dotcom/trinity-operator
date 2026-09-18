#!/usr/bin/env python3
"""段 6 —— 影響行列を一般に取ったら。落ちるのは次元である。

    python3 roadmap/stage6_general_influence.py

三篇の作用素は `x ← DQx + (I−D)p` で、`Q` は巡回置換である。
社会学の Friedkin–Johnsen は `x ← ΛWx + (I−Λ)u` で、`W` は行確率行列である。
**巡回置換はその特殊例にすぎない** —— 各主体がちょうど一人だけを、重み 1 で
聴く輪である。

ここで測るのは、その特殊例が**何に届かないか**である。二つに分ける。

一。**一点の均衡では、区別がつかない。**
二。**作用素として見ると、次元が落ちる。**

一のほうを先に置く。こちらは分離しなかった。

`Q` が置換なら `DQ` の各行は非零要素を一つしか持たない。よって不動点は
座標ごとに `x*ᵢ = aᵢ x*_{σ(i)} + (1 − aᵢ) pᵢ` を満たし、`aᵢ` を解くと

    aᵢ = (x*ᵢ − pᵢ) / (x*_{σ(i)} − pᵢ)

**これが全座標で (0,1) に入る巡回 σ が無ければ、その均衡は再現できない。**
必要条件である。ところが一般の `W` から作った均衡は、**ほぼ必ず満たす。**
FJ の均衡は凸結合なので、`x*ᵢ` は自分の `pᵢ` と他のどれかの `x*ⱼ` の間に
必ず落ちる。巡回の選び方は `(n−1)!` 通りあり、どれか一つが当たってしまう。

**一本の軌道だけを見て「合っている」と言えてしまう。**三篇がそう見えた理由が
ここにある。

二が本体である。同じ `(Q,a)` が**あらゆる `p`** について一般の均衡を再現できるか
を問うと、比較は行列どうしになる。

    M(W,λ) = (I − ΛW)⁻¹ (I − Λ)        一般
    M(σ,a) = (I − DQ)⁻¹ (I − D)        三篇の設定

**像の次元をヤコビ行列の階数で測る。**巡回のほうは `a` の `n` 個しか自由度が
無く、`σ` を変えても `(n−1)!` 枚の `n` 次元の面が並ぶだけである。一般のほうは
`W` の各行が和 1 の拘束のもとで `n−2` 自由、`λ` が `n` 個で、合わせて
`n(n−1)` である。

    n = 3   巡回 3 / 一般 6
    n = 4   巡回 4 / 一般 12
    n = 5   巡回 5 / 一般 20
    n = 6   巡回 6 / 一般 30

**比は 1/(n−1) である。**そして `n ≥ 3` では、巡回の像は一般の像の中で
測度零である。**ほとんどすべての Friedkin–Johnsen 作用素が、三篇の設定では
再現できない。**

落ちている `n(n−2)` 次元が、**誰が誰にどれだけ影響するか**である。

NumPy のみ。乱数種は固定。
"""

import itertools
import numpy as np

SEED = 20260918
EPS = 1e-9
TOL = 1e-6


def cycles(n):
    """n 個の座標を一巡する置換を全部返す。(n−1)! 通り。"""
    out = []
    for rest in itertools.permutations(range(1, n)):
        order = (0,) + rest
        sigma = [0] * n
        for k in range(n):
            sigma[order[k]] = order[(k + 1) % n]
        out.append(tuple(sigma))
    return out


def row_stochastic(rng, n):
    """対角が零の行確率行列。置換行列と同じ土俵に置くため、自分は聴かない。"""
    out = np.zeros((n, n))
    for i in range(n):
        cols = [j for j in range(n) if j != i]
        out[i, cols] = rng.dirichlet(np.ones(n - 1))
    return out


def resolvent(W, lam):
    """M = (I − ΛW)⁻¹ (I − Λ)。均衡は x* = M p である。"""
    n = len(lam)
    L = np.diag(lam)
    return np.linalg.solve(np.eye(n) - L @ W, np.eye(n) - L)


def perm_matrix(sigma):
    n = len(sigma)
    Q = np.zeros((n, n))
    for i, j in enumerate(sigma):
        Q[i, j] = 1.0
    return Q


def pointwise_reachable(x, p, sigmas):
    """一点の均衡について、必要条件を満たす巡回があるか。"""
    for s in sigmas:
        a = np.empty(len(p))
        ok = True
        for i, j in enumerate(s):
            d = x[j] - p[i]
            if abs(d) < EPS:
                ok = False
                break
            a[i] = (x[i] - p[i]) / d
        if ok and np.all(a > EPS) and np.all(a < 1 - EPS):
            return True
    return False


def jac_rank_cyclic(sigma, a, h=1e-6):
    """a ↦ vec M(σ,a) のヤコビ行列の階数。"""
    Q = perm_matrix(sigma)
    n = len(a)

    def M(v):
        D = np.diag(v)
        return np.linalg.solve(np.eye(n) - D @ Q, np.eye(n) - D).ravel()

    base = M(a)
    J = []
    for k in range(n):
        b = a.copy()
        b[k] += h
        J.append((M(b) - base) / h)
    return int(np.linalg.matrix_rank(np.array(J), tol=TOL))


def jac_rank_general(rng, n, h=1e-6):
    """(W, λ) ↦ vec M のヤコビ行列の階数。行の和 1 を保って動かす。"""
    lam = rng.uniform(0.2, 0.8, size=n)
    W = row_stochastic(rng, n)
    base = resolvent(W, lam).ravel()
    J = []
    for i in range(n):
        cols = [j for j in range(n) if j != i]
        for t in range(len(cols) - 1):
            W2 = W.copy()
            W2[i, cols[t]] += h
            W2[i, cols[-1]] -= h
            J.append((resolvent(W2, lam).ravel() - base) / h)
    for k in range(n):
        l2 = lam.copy()
        l2[k] += h
        J.append((resolvent(W, l2).ravel() - base) / h)
    return int(np.linalg.matrix_rank(np.array(J), tol=TOL)), len(J)


def main():
    rng = np.random.default_rng(SEED)
    print('段 6 —— 一般の影響行列と、巡回置換が届く範囲')
    print()

    print('一. 一点の均衡では区別がつかない')
    print()
    print('  n   標本   必要条件を満たさない   巡回の数')
    print('  --  -----  --------------------  --------')
    trials = 2000
    pointwise = []
    for n in (3, 4, 5, 6):
        sig = cycles(n)
        miss = 0
        for _ in range(trials):
            W = row_stochastic(rng, n)
            lam = rng.uniform(0.05, 0.95, size=n)
            p = rng.normal(size=n)
            x = resolvent(W, lam) @ p
            if not pointwise_reachable(x, p, sig):
                miss += 1
        pointwise.append((n, trials, miss))
        print('  %2d  %5d  %20d  %8d' % (n, trials, miss, len(sig)))
    print()
    print('  **分離しない。**一本の軌道だけを見て「合っている」と言えてしまう。')
    print()

    print('二. 作用素として見ると、次元が落ちる')
    print()
    print('  n   巡回の像   一般の像   周囲   比')
    print('  --  --------  --------  -----  ------')
    dims = []
    for n in (3, 4, 5, 6):
        sigma = tuple((i + 1) % n for i in range(n))
        a = rng.uniform(0.2, 0.8, size=n)
        rc = jac_rank_cyclic(sigma, a)
        rg, _ = jac_rank_general(rng, n)
        dims.append((n, rc, rg, n * n))
        print('  %2d  %8d  %8d  %5d  1/%d' % (n, rc, rg, n * n, n - 1))
    print()
    print('  巡回は n 次元、一般は n(n−1) 次元。**比は 1/(n−1)。**')
    print('  n ≥ 3 では、巡回の像は一般の像のなかで測度零である。')
    print()
    print('  落ちている n(n−2) 次元が、誰が誰にどれだけ影響するかである。')
    print()

    print('三. 判定が壊れていないことを、逆から見る')
    bad = 0
    for n in (3, 4, 5, 6):
        sig = cycles(n)
        for _ in range(200):
            s = sig[int(rng.integers(len(sig)))]
            a = rng.uniform(0.05, 0.95, size=n)
            p = rng.normal(size=n)
            x = resolvent(perm_matrix(s), a) @ p
            if not pointwise_reachable(x, p, sig):
                bad += 1
    print('  巡回置換から作った 800 件のうち、届かないと判定されたもの: %d' % bad)
    print('  ここが 0 でなければ、判定のほうが壊れている。')
    return pointwise, dims, bad


if __name__ == '__main__':
    main()
