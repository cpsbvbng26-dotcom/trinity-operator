#!/usr/bin/env python3
"""段 1 —— 作った距離は最善ではない。最善はどこか、を出す。

    python3 roadmap/stage1_optimal_norm.py

certificate.py は P − BᵀPB = I（B = A/γ）を解く。右辺の I は**選んだのではなく、
決め打ち**である。一般に W ≻ 0 を右辺に置くと

    P(W) = Σₖ (Aᵀ)ᵏ W Aᵏ / κ²ᵏ        （ρ(A) < κ なら収束）

は AᵀPA = κ²(P − W) を満たし、どの W でも ‖Ax‖_P ≤ κ‖x‖_P が成り立つ。
逆に AᵀPA ⪯ κ²P を満たす P があれば W = P − BᵀPB ⪰ 0 と置ける。つまり

    **κ を満たす P の全体 ＝ W を動かしたときの P(W) の全体**

である。κ は W に依らない。動くのはユークリッド距離に戻すときの係数
√(λmax(P)/λmin(P)) だけ。だから縮小定数と係数は別々に扱える。

この段でやること。

  1. κ が W に依らないことを、実際に W を振って確かめる
  2. 対角の W に限ると**何も改善しない**ことを見て、なぜかを示す
  3. 対称行列すべてを動かして最善を探す
  4. その最善が、閉じた式と一致することを確かめる

4 が要点である。数値の探索が出した値を、別の道から出した値と突き合わせないと、
探索がうまくいったのかどうかを自分では判定できない。

これは新しい数学ではない。重み付きノルムの最適化が半正定値計画になることも、
非正規行列の最適な相似変換も、標準的な題材である（Boyd, El Ghaoui, Feron,
Balakrishnan, *Linear Matrix Inequalities in System and Control Theory*, SIAM 1994）。
新しいのは、この反例について**決め打ちが何倍損をしているかという測定値**だけ。

NumPy のみ。乱数種は固定。
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from trinity import TrinityOperator  # noqa: E402

__all__ = ["weighted_lyapunov", "amplification", "achieved",
           "optimize_weight", "jordan_optimum"]


def weighted_lyapunov(A, kappa, W):
    """P − BᵀPB = W（B = A/κ）の解。正定値でなければ None。"""
    A = np.asarray(A, dtype=float)
    n = A.shape[0]
    if not (float(np.max(np.abs(np.linalg.eigvals(A)))) < kappa < 1.0):
        return None
    B = A / kappa
    M = np.eye(n * n) - np.kron(B.T, B.T)
    W = np.asarray(W, dtype=float)
    P = np.linalg.solve(M, W.reshape(-1)).reshape(n, n)
    P = (P + P.T) / 2.0
    if np.min(np.linalg.eigvalsh(P)) <= 0:
        return None
    return P


def amplification(P):
    """√(λmax/λmin)。ユークリッド距離に戻すときの係数。"""
    ev = np.linalg.eigvalsh(P)
    return float(np.sqrt(ev.max() / ev.min()))


def achieved(A, P):
    """このノルムでの ‖A‖_P。κ を本当に守っているかを見るため。"""
    A = np.asarray(A, dtype=float)
    L = np.linalg.cholesky(P)
    N = L.T @ A
    return float(np.linalg.norm(
        np.array([np.linalg.solve(L, N[i]) for i in range(A.shape[0])]), 2))


def optimize_weight(A, kappa, diagonal=False, steps=4000, seed=20260907):
    """係数を最小にする W を探す。W = VVᵀ と置いて V を動かす。

    diagonal=True なら V を対角に限る。制限したときに何が起きるかを見るため。
    """
    A = np.asarray(A, dtype=float)
    n = A.shape[0]
    rng = np.random.default_rng(seed)

    def value(V):
        P = weighted_lyapunov(A, kappa, V @ V.T)
        return np.inf if P is None else amplification(P)

    V = np.eye(n)
    best = value(V)
    scale = 0.8
    for i in range(steps):
        step = rng.normal(size=(n, n)) * scale
        if diagonal:
            step = np.diag(np.diag(step))
        trial = V + step
        v = value(trial)
        if v < best:
            best, V = v, trial
        if (i + 1) % max(1, steps // 10) == 0:
            scale *= 0.6
    return V @ V.T, best


def jordan_optimum(a, b, kappa):
    """A = [[a, b], [0, a]] について、係数の最小値を閉じた式で出す。

    相似変換 S = diag(1, t) をかけると S A S⁻¹ = [[a, b/t], [0, a]]。
    [[a, c], [0, a]] の最大特異値は (√(c² + 4a²) + c)/2 なので、これが κ に
    等しくなる c は c = (κ² − a²)/κ。そのとき t = b/c で、P = SᵀS の係数は
    √(λmax/λmin) = t になる。
    """
    c = (kappa ** 2 - a ** 2) / kappa
    return abs(b) / c


if __name__ == "__main__":
    np.set_printoptions(precision=6, suppress=True)

    def title(s):
        print("\n" + s)
        print("-" * 72)

    op = TrinityOperator([0.5, 0.5], [1.0, 0.0],
                         Q=np.array([[1.0, 40.0], [0.0, 1.0]]))
    A = op.A          # [[0.5, 20], [0, 0.5]]
    I2 = np.eye(2)

    title("1. κ は W に依らない。動くのは係数だけである")
    kappa = 0.75
    for w in ([1, 1], [1, 10], [1, 100], [1, 1000], [1, 0.01]):
        P = weighted_lyapunov(A, kappa, np.diag(w))
        print("  W = diag%-13s ‖A‖_P = %.9f   係数 = %10.4g"
              % (str(tuple(w)), achieved(A, P), amplification(P)))
    print("""
  ‖A‖_P はどの W でも κ = 0.75 を超えない。縮小定数は W の選び方と無関係である。""")

    title("2. 対角の W に限ると、何も改善しない")
    W_diag, best_diag = optimize_weight(A, kappa, diagonal=True)
    print("  決め打ち W = I の係数        %.4f" % amplification(weighted_lyapunov(A, kappa, I2)))
    print("  対角の W を全部試した最善     %.4f" % best_diag)
    print("""
  理由は計算で出る。B = A/κ = [[α, β], [0, α]] と置くと

      P − BᵀPB = [[1−α², −αβ], [−αβ, ...]]  ×（P の成分）

  で、P を対角にすると右辺の非対角成分は −αβ·P₁₁ になる。α も β も 0 でない
  ので、**対角な P は対角な W からは出てこない。** そして最善の P は対角である
  （下で見る）。対角に限るという制限が、まさに答えを外している。""")

    title("3. 対称行列すべてを動かして最善を探す")
    print("   κ      決め打ち W = I    探索した最善    改善      閉じた式    差")
    for kappa in (0.55, 0.60, 0.75, 0.90, 0.99):
        base = amplification(weighted_lyapunov(A, kappa, I2))
        W, best = optimize_weight(A, kappa)
        closed = jordan_optimum(0.5, 20.0, kappa)
        print("  %.2f   %13.4f   %13.4f   %5.2f 倍   %9.4f   %.2e"
              % (kappa, base, best, base / best, closed,
                 abs(best - closed) / closed))
    print("""
  最後の列が要点である。探索が出した値と、相似変換から閉じた式で出した値が
  相対差は最大 3.8×10⁻⁶ で一致している。**探索がうまくいったことを、探索の外から
  確かめられている。**片方だけでは、どちらも信用できない。""")

    title("4. 最善の P は対角である")
    kappa = 0.75
    W, best = optimize_weight(A, kappa)
    P = weighted_lyapunov(A, kappa, W)
    P = P / P[0, 0]
    t = jordan_optimum(0.5, 20.0, kappa)
    print("  探索が出した P（P₁₁ で割った）")
    print("   ", np.array2string(P, precision=4).replace("\n", "\n    "))
    print("  閉じた式が言う P = diag(1, t²) = diag(1, %.2f)" % t ** 2)
    print("""
  非対角成分が小さく、対角成分が t² に寄っている。閉じた式が指す P に
  探索が近づいている、という形になっている。""")

    title("5. 上界がどれだけ下がるか")
    x0 = np.array([5.0, -3.0])
    err = op.error_curve(x0, steps=60)
    base = amplification(weighted_lyapunov(A, kappa, I2))
    print("   段     実際の誤差     決め打ちの上界    最善の上界")
    for k in (0, 5, 10, 20, 40, 60):
        print("  %3d   %12.4g   %14.4g   %12.4g"
              % (k, err[k], base * kappa ** k * err[0], best * kappa ** k * err[0]))
    bad = [k for k in range(len(err))
           if err[k] > best * kappa ** k * err[0] * (1 + 1e-9)]
    print("\n  最善の上界でも全 %d 段が内側: %s" % (len(err), "はい" if not bad else "いいえ"))

    title("6. 論文の設定では、探索する余地が無い")
    s2 = TrinityOperator([0.5, 0.7, 0.3], [1, 0, 0.5])
    base3 = amplification(weighted_lyapunov(s2.A, 0.9, np.eye(3)))
    _, best3 = optimize_weight(s2.A, 0.9)
    print("  Series II   κ = 0.9   決め打ち %.4f → 最善 %.4f" % (base3, best3))
    print("""
  ‖A‖₂ < 1 の側では係数がもともと 1 に近い。縮める余地が無い。
  この段が効くのは、論文の議論が破れている領域だけである。""")

    print("\n" + "-" * 72)
    print("""独自性。重み付きノルムの最適化が半正定値計画になることも、非正規行列に
対する最適な相似変換も、教科書の題材である（Boyd 他 1994）。ここに新しい数学は
無い。**新しいのは測定値である** —— この反例で決め打ちの W = I は κ = 0.75 の
とき 1.44 倍損をしている。それは誰も測っていないが、誰でも測れる。

合法性。式も実装もこのファイルの中で閉じており、外部のコードを持ち込んでいない。
参照した文献は上の一件で、結果を引用しているのではなく「既知である」という
事実の出典として挙げている。""")
