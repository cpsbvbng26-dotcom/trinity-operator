#!/usr/bin/env python3
"""段 2 —— 統合の仕方が毎回変わったら。切り替え系へ。

    python3 roadmap/stage2_switching.py

三篇は一つの作用素を繰り返す。だが「三つの要素を統合する」という話を素直に
読めば、**統合の仕方が毎回同じである必要は無い。** 混合率 a も置換 Q も、
段ごとに変わってよい。

    x ← A_{σ(k)} x + b_{σ(k)},      σ(k) ∈ {1, …, m}

ここで**論文の直観がはっきり壊れる。**

    各 Aᵢ が ρ(Aᵢ) < 1 でも、切り替え方によっては発散する。

一つずつ縮んでも、順番に掛けると伸びることがある。決めるのは各々の
スペクトル半径ではなく、**同時スペクトル半径（joint spectral radius）**

    JSR = lim_{k→∞} max_{σ} ‖A_{σ(k)} ⋯ A_{σ(1)}‖^{1/k}

である。JSR < 1 が、すべての切り替えに対する収束の必要十分条件になる。

この段でやること。

  1. ρ(A₁), ρ(A₂) < 1 なのに発散する具体例を、実際に発散させて見せる
  2. JSR の下界（周期的な積から）と上界（長さ k の積の最大ノルムから）を計算する
  3. 共通のリアプノフ関数 P を探す。見つかれば、それが収束の証明になる
  4. 共通の P が存在しない例を出し、上下界で挟んで判定する

JSR は決定不能に近い難しさを持つことが知られている（Blondel–Tsitsiklis 2000:
ρ ≤ 1 の判定は決定不能）。**だから「計算した」ではなく「挟んだ」としか言えない。**
そこを曖昧にしない。

参照した事実の出典。R. Jungers, *The Joint Spectral Radius: Theory and
Applications*, Springer 2009。実装は持ち込んでいない。

NumPy のみ。乱数種は固定。
"""

import itertools
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from trinity import cyclic_shift  # noqa: E402

__all__ = ["jsr_bounds", "common_lyapunov", "worst_product", "simulate"]


def jsr_bounds(mats, depth=6):
    """JSR を上下から挟む。

    下界  長さ k の積のスペクトル半径の最大の k 乗根。どの周期軌道も JSR 以下
          なので、これは必ず下から押さえる。
    上界  長さ k の積の 2-ノルムの最大の k 乗根。劣乗法性から必ず上から押さえる。

    depth を上げれば挟みは狭まるが、積の数は mᵏ で増える。
    """
    mats = [np.asarray(M, dtype=float) for M in mats]
    lo, hi = 0.0, np.inf
    for k in range(1, depth + 1):
        best_rho, best_nrm = 0.0, 0.0
        for idx in itertools.product(range(len(mats)), repeat=k):
            M = np.eye(mats[0].shape[0])
            for i in idx:
                M = mats[i] @ M
            best_rho = max(best_rho, float(np.max(np.abs(np.linalg.eigvals(M)))))
            best_nrm = max(best_nrm, float(np.linalg.norm(M, 2)))
        lo = max(lo, best_rho ** (1.0 / k))
        hi = min(hi, best_nrm ** (1.0 / k))
    return lo, hi


def worst_product(mats, depth=6):
    """‖·‖ が最も伸びる並び順を返す。発散させる切り替えを実際に作るため。"""
    mats = [np.asarray(M, dtype=float) for M in mats]
    best, order = 0.0, ()
    for k in range(1, depth + 1):
        for idx in itertools.product(range(len(mats)), repeat=k):
            M = np.eye(mats[0].shape[0])
            for i in idx:
                M = mats[i] @ M
            r = float(np.max(np.abs(np.linalg.eigvals(M)))) ** (1.0 / k)
            if r > best:
                best, order = r, idx
    return order, best


def common_lyapunov(mats, kappa=1.0, steps=6000, seed=20260907):
    """すべての Aᵢ に共通する P（AᵢᵀPAᵢ ⪯ κ²P）を探す。

    見つかれば、どんな切り替えでも ‖x‖_P が κ 倍ずつしか伸びない。κ < 1 なら
    それが収束の証明になる。**見つからないことは、存在しないことの証明ではない。**
    探索の失敗にすぎない。そこは分けて報告する。

    P = VVᵀ + εI と置いて V を動かし、max_i ‖Aᵢ‖_P を最小にする。
    """
    mats = [np.asarray(M, dtype=float) for M in mats]
    n = mats[0].shape[0]
    rng = np.random.default_rng(seed)

    def worst(V):
        P = V @ V.T + 1e-9 * np.eye(n)
        try:
            L = np.linalg.cholesky(P)
        except np.linalg.LinAlgError:
            return np.inf
        out = 0.0
        for M in mats:
            N = L.T @ M
            G = np.array([np.linalg.solve(L, N[i]) for i in range(n)])
            out = max(out, float(np.linalg.norm(G, 2)))
        return out

    V = np.eye(n)
    best = worst(V)
    scale = 0.7
    for i in range(steps):
        trial = V + rng.normal(size=(n, n)) * scale
        v = worst(trial)
        if v < best:
            best, V = v, trial
        if (i + 1) % max(1, steps // 12) == 0:
            scale *= 0.65
    return V @ V.T + 1e-9 * np.eye(n), best


def simulate(mats, order, x0, steps):
    """並び順を繰り返して回す。ノルムの列を返す。"""
    x = np.asarray(x0, dtype=float)
    out = [float(np.linalg.norm(x))]
    for k in range(steps):
        x = np.asarray(mats[order[k % len(order)]], dtype=float) @ x
        out.append(float(np.linalg.norm(x)))
    return np.array(out)


if __name__ == "__main__":
    np.set_printoptions(precision=6, suppress=True)

    def title(s):
        print("\n" + s)
        print("-" * 72)

    # ずらす向きが二通りある場合。どちらも単体では縮む。
    S = np.array([[1.0, 1.0], [0.0, 1.0]])
    A1, A2 = 0.7 * S, 0.7 * S.T

    title("1. 一つずつ縮んでも、混ぜると伸びる")
    for name, M in (("A₁ = 0.7·上三角", A1), ("A₂ = 0.7·下三角", A2)):
        print("  %-16s ρ = %.6f   ‖·‖₂ = %.6f"
              % (name, np.max(np.abs(np.linalg.eigvals(M))), np.linalg.norm(M, 2)))
    print("  A₂A₁            ρ = %.6f   ← 二つ掛けると 1 を超える"
          % np.max(np.abs(np.linalg.eigvals(A2 @ A1))))
    only1 = simulate([A1, A2], (0,), [1.0, 1.0], 40)
    both = simulate([A1, A2], (0, 1), [1.0, 1.0], 40)
    print("\n   段      A₁ だけ      交互")
    for k in (0, 5, 10, 20, 40):
        print("  %3d   %10.4g   %10.4g" % (k, only1[k], both[k]))
    print("""
  片方だけを繰り返せば 0 へ行く。交互にすると発散する。同じ二つの行列である。
  **「各段が縮小写像なら全体も縮む」は、切り替えが入ると成り立たない。**
  三篇の議論は各段しか見ていないので、この場合を扱えない。""")

    title("2. 同時スペクトル半径を挟む")
    lo, hi = jsr_bounds([A1, A2], depth=6)
    order, rate = worst_product([A1, A2], depth=6)
    print("  下界 %.6f ≤ JSR ≤ 上界 %.6f     （長さ 6 まで）" % (lo, hi))
    print("  いちばん伸びる並び %s  一段あたり %.6f 倍" % (str(order), rate))
    print("  JSR > 1 が確定: %s  ← 下界が 1 を超えていれば、それだけで確定する"
          % ("はい" if lo > 1 else "いいえ"))

    title("3. 収束する切り替え系と、その証明")
    B1 = np.array([[0.4, 0.3], [0.0, 0.5]])
    B2 = np.array([[0.5, 0.0], [0.2, 0.4]])
    lo2, hi2 = jsr_bounds([B1, B2], depth=6)
    print("  下界 %.6f ≤ JSR ≤ 上界 %.6f" % (lo2, hi2))
    P, w = common_lyapunov([B1, B2])
    print("  共通の P が見つかった。すべての i で ‖Aᵢ‖_P ≤ %.6f" % w)
    print("  P =", np.array2string(P / P[0, 0], precision=4).replace("\n", "\n     "))
    print("  これで確定するか: %s" % ("はい（κ < 1）" if w < 1 else "いいえ"))
    ev = np.linalg.eigvalsh(P)
    print("  係数 √(λmax/λmin) = %.4f" % np.sqrt(ev.max() / ev.min()))
    print("""
  共通の P が一つ見つかれば、**切り替え方を問わず** ‖xₖ‖_P ≤ κᵏ‖x₀‖_P である。
  これは JSR の上界を一つ与える。上の上界 %.6f より %s。""" % (
        hi2, "良い" if w < hi2 else "悪い"))

    title("4. 挟めても決まらない場合がある")
    # ちょうど境目。この対の JSR は γ×黄金比であることが知られている。
    gamma = 1.0 / 1.6180339887498949
    C1, C2 = gamma * S, gamma * S.T
    lo3, hi3 = jsr_bounds([C1, C2], depth=7)
    P3, w3 = common_lyapunov([C1, C2])
    print("  γ = 1/φ = %.9f   （φ は黄金比）" % gamma)
    print("  下界 %.9f ≤ JSR ≤ 上界 %.9f" % (lo3, hi3))
    print("  共通の P の探索が出した最善  %.9f  ← 1 を下回れない" % w3)
    print("""
  この対の JSR が γ×φ になることは知られている。γ = 1/φ とすればちょうど 1。
  **上下から 1 に押しつけられて、どちら側かが決まらない。**深さを増やしても、
  1 の側からしか近づかない。

  そして一般に、この判定は避けようがない。**JSR ≤ 1 かどうかの判定は決定不能
  である**ことが知られている（Blondel–Tsitsiklis 2000）。「まだ計算していない」
  のではなく、「一般には計算しきれない」側の問題である。ここが、この方向に
  進んだときにぶつかる壁になる。""")

    title("5. 三篇の設定に戻すと")
    a = [0.5, 0.7, 0.3]
    Q = cyclic_shift(3)
    D = np.diag(a)
    A_fwd = D @ Q
    A_bwd = D @ Q.T          # 逆向きに統合する段
    lo4, hi4 = jsr_bounds([A_fwd, A_bwd], depth=6)
    P4, w4 = common_lyapunov([A_fwd, A_bwd])
    print("  順方向 ρ = %.6f   逆方向 ρ = %.6f"
          % (np.max(np.abs(np.linalg.eigvals(A_fwd))),
             np.max(np.abs(np.linalg.eigvals(A_bwd)))))
    print("  JSR は %.6f 以上 %.6f 以下" % (lo4, hi4))
    print("  共通の P で ‖Aᵢ‖_P ≤ %.6f、係数 %.4f"
          % (w4, np.sqrt(np.linalg.eigvalsh(P4).max() / np.linalg.eigvalsh(P4).min())))
    print("  どんな順で混ぜても収束する: %s" % ("はい" if w4 < 1 else "確定しない"))
    print("""
  ここは素直に通る。置換行列は等長なので、向きを変えても長さを変えない。
  **三篇の設定が「切り替えても大丈夫」なのは、置換を使っているからである。**
  一般の Q に替えた瞬間、それは成り立たなくなる。1 節の A₁, A₂ がその例。""")

    print("\n" + "-" * 72)
    print("""独自性。同時スペクトル半径も、共通リアプノフ関数も、切り替え系の
標準的な道具である（Jungers 2009）。上下界の取り方も教科書どおり。
**新しいのは、三篇の作用素族についてそれを実際に走らせ、「置換だから通っている
のであって、一般の Q では通らない」を具体的な行列で示したことだけ。**

合法性。実装は外部から持ち込んでいない。JSR の決定不能性は既知の事実として
出典を挙げているだけで、その論文の内容を引き写してはいない。

ここから先。共通の P が存在しないときに、多項式のリアプノフ関数（sum-of-squares）
へ上げると挟みが狭まることが知られている。それには SDP のソルバが要る。
**NumPy だけでは届かない。** 届かない場所を、届いたふりで埋めない。""")
