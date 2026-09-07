#!/usr/bin/env python3
"""論文が使いたかったバナッハの議論を、成り立つ形で組み直す。

    python3 certificate.py

trinity.py は「論文の条件は必要以上に強い」ことを**測る**。ここはその続きで、
**足りなくなった分を作り直す**。

    論文の議論      ‖A‖₂ < 1  なので f は縮小写像  →  バナッハの不動点定理
    実際に必要      ρ(A) < 1

ρ < 1 ≤ ‖A‖₂ の領域では、結論（一意の不動点へ収束する）は正しいまま、
**議論だけが壊れる。** ユークリッド距離で測るかぎり f は縮小写像ではないので、
バナッハの定理をそのまま当てることができない。

やることは一つである。**f が縮小写像になる距離を、その場で作る。**

    P を  P − BᵀPB = I   （B = A/γ、ρ < γ < 1）の解とすると
    ‖x‖_P = √(xᵀPx) は ℝⁿ 上のノルムで、この距離のもとで

        ‖Ax‖_P ≤ κ‖x‖_P,      κ = γ√(1 − 1/λmax(P)) < γ < 1

    が全ての x で成り立つ。しかも κ はこのノルムでの ‖A‖_P と**厳密に一致する**
    （上からの評価ではない）。‖x‖_P はユークリッド距離と同値なので (ℝⁿ, d_P) は
    完備であり、バナッハの定理が字義どおり適用できる。

    ユークリッド距離に戻すと

        ‖xₖ − x*‖ ≤ √(λmax(P)/λmin(P)) · κᵏ · ‖x₀ − x*‖

    右辺の係数が 1 を超えるぶんが、trinity.py が測っていた過渡的増幅である。
    誤差はいったん増えてよい。増えたうえで κ のレートに乗る、という形になる。

γ は目盛りである。γ を ρ に近づけると κ も ρ に近づくが、係数（増幅）が大きくなる。
どんな ρ < 1 に対しても κ < 1 の距離が取れる、というのがこの構成の内容である。

**これは新しい数学ではない。** 「任意の ε > 0 に対して ‖A‖ ≤ ρ(A) + ε となる
ノルムが存在する」は Ostrowski / Householder の古典的な結果で、教科書に載っている。
リアプノフ方程式（Stein 方程式）を解いてそのノルムを作るのも標準的な手順である。
ここでやっているのは、**存在証明で終わっている構成を、実際に走らせて出力させる**
ことだけである。

そのうえで、このリポジトリの文脈では意味がある。三本の論文の議論は
ρ < 1 ≤ ‖A‖₂ で壊れるが、**壊れたまま放置する必要はない**。同じ結論に、
同じバナッハの定理で到達できる。論文を否定するのではなく、論文が使った道具を
そのまま使って、届いていなかった範囲まで届かせる。

NumPy のみ。scipy は使わない（solve_discrete_lyapunov も schur も使わずに済ませる）。
"""

import numpy as np

__all__ = ["ContractionCertificate", "certify", "sweep"]


class ContractionCertificate:
    """f(x) = Ax + b が縮小写像になるノルムと、その縮小定数。

    直接作らず、certify() から受け取る。

    属性
        A          対象の線形部分
        rho        ρ(A)。これが 1 未満であることだけが前提
        euclidean  ‖A‖₂。論文が縮小定数として挙げているもの
        gamma      目盛り。ρ < γ < 1
        kappa      構成したノルムでの縮小定数。κ < γ < 1
        P          ノルムを定める正定値行列。‖x‖_P = √(xᵀPx)
        amplification  √(λmax/λmin)。ユークリッド距離に戻すときの係数
    """

    def __init__(self, A, gamma, P, rho, euclidean):
        self.A = A
        self.n = A.shape[0]
        self.gamma = float(gamma)
        self.P = P
        self.rho = float(rho)
        self.euclidean = float(euclidean)
        w = np.linalg.eigvalsh(P)
        self.eig_min = float(w.min())
        self.eig_max = float(w.max())
        self.kappa = float(gamma * np.sqrt(1.0 - 1.0 / self.eig_max))
        self.amplification = float(np.sqrt(self.eig_max / self.eig_min))
        self.L = np.linalg.cholesky(P)          # P = L Lᵀ、‖x‖_P = ‖Lᵀx‖

    # ------------------------------------------------------------ ノルム
    def norm(self, x):
        """‖x‖_P = √(xᵀPx)。この距離のもとで f は縮小写像になる。"""
        x = np.asarray(x, dtype=float)
        return float(np.linalg.norm(self.L.T @ x))

    def distance(self, x, y):
        """d_P(x, y) = ‖x − y‖_P。"""
        return self.norm(np.asarray(x, dtype=float) - np.asarray(y, dtype=float))

    def bound(self, k, initial_error):
        """第 k 段の誤差の上界（ユークリッド距離で測ったもの）。"""
        return self.amplification * self.kappa ** k * float(initial_error)

    # -------------------------------------------------- 証書そのものの検査
    def achieved(self):
        """構成したノルムでの ‖A‖_P を、定義から計算し直す。

        ‖x‖_P = ‖Lᵀx‖ なので、y = Lᵀx と置くと作用素は Lᵀ A L⁻ᵀ になる。
        その 2-ノルムが ‖A‖_P である。κ と一致するはずで、
        一致することがこの証書が上からの評価ではないことの意味になる。
        """
        M_T = np.linalg.solve(self.L, (self.L.T @ self.A).T)
        return float(np.linalg.norm(M_T.T, 2))

    def residual(self):
        """P − BᵀPB − I の大きさ。0 でなければ P が方程式の解になっていない。"""
        B = self.A / self.gamma
        return float(np.abs(self.P - B.T @ self.P @ B - np.eye(self.n)).max())

    def audit(self, trials=2000, seed=20260907):
        """証書が名乗っていることを、乱数で実際に当たって確かめる。

        返すのは辞書。真偽値の項目がすべて True でなければ証書は無効である。
        """
        rng = np.random.default_rng(seed)
        X = rng.normal(size=(trials, self.n))
        nP = np.linalg.norm(X @ self.L, axis=1)              # ‖xᵢ‖_P
        nPA = np.linalg.norm(X @ self.A.T @ self.L, axis=1)  # ‖Axᵢ‖_P
        n2 = np.linalg.norm(X, axis=1)                       # ‖xᵢ‖₂
        ratio = nPA / nP
        return {
            "P が正定値": bool(self.eig_min > 0),
            "P が方程式を満たす": bool(self.residual() < 1e-9),
            "κ < 1": bool(self.kappa < 1.0),
            "ρ ≤ κ < γ < 1": bool(self.rho <= self.kappa + 1e-12
                                  and self.kappa < self.gamma < 1.0),
            "全ての試行で縮小": bool((ratio <= self.kappa + 1e-9).all()),
            "κ は ‖A‖_P に一致": bool(abs(self.achieved() - self.kappa) < 1e-9),
            "√λmin ‖x‖₂ ≤ ‖x‖_P": bool(
                (nP >= np.sqrt(self.eig_min) * n2 - 1e-9).all()),
            "‖x‖_P ≤ √λmax ‖x‖₂": bool(
                (nP <= np.sqrt(self.eig_max) * n2 + 1e-9).all()),
            "最悪の比 ‖Ax‖_P/‖x‖_P": float(ratio.max()),
        }

    def report(self):
        gap = "  （論文の条件を満たしていない）" if self.euclidean >= 1 else ""
        return "\n".join([
            "  ρ(A) = %.6f    ‖A‖₂ = %.6f%s" % (self.rho, self.euclidean, gap),
            "  γ    = %.6f    ← 目盛り。ρ < γ < 1 の範囲で選ぶ" % self.gamma,
            "  κ    = %.6f    ← このノルムでの縮小定数（‖A‖_P と厳密に一致）"
            % self.kappa,
            "  増幅 = %-10.4g ← ユークリッド距離に戻すときの係数 √(λmax/λmin)"
            % self.amplification,
            "  ‖xₖ − x*‖ ≤ %.4g × %.6f^k × ‖x₀ − x*‖"
            % (self.amplification, self.kappa),
        ])

    def __repr__(self):
        return "<ContractionCertificate n=%d ρ=%.4f γ=%.4f κ=%.6f 増幅=%.4g>" % (
            self.n, self.rho, self.gamma, self.kappa, self.amplification)


def certify(operator, gamma=None):
    """f が縮小写像になるノルムを構成して返す。

    operator  TrinityOperator、または正方行列 A そのもの
    gamma     ρ < γ < 1 の目盛り。既定は (ρ + 1) / 2

    ρ(A) ≥ 1 なら ValueError。そもそも収束しないので、構成するものが無い。
    """
    A = np.asarray(getattr(operator, "A", operator), dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("正方行列が要ります")
    n = A.shape[0]
    rho = float(np.max(np.abs(np.linalg.eigvals(A))))
    if rho >= 1.0:
        raise ValueError(
            "ρ(A) = %.6f ≥ 1 です。収束しないので、縮小になる距離は存在しません。"
            % rho)
    if gamma is None:
        gamma = (rho + 1.0) / 2.0
    gamma = float(gamma)
    if not (rho < gamma < 1.0):
        raise ValueError("γ は ρ = %.6f と 1 のあいだで選んでください（γ = %.6f）"
                         % (rho, gamma))

    # P − BᵀPB = I を解く。行優先の vec では vec(BᵀPB) = (Bᵀ ⊗ Bᵀ) vec(P)。
    # ρ(B) = ρ/γ < 1 なので I − Bᵀ⊗Bᵀ は正則で、解は一意かつ正定値。
    B = A / gamma
    M = np.eye(n * n) - np.kron(B.T, B.T)
    P = np.linalg.solve(M, np.eye(n).reshape(-1)).reshape(n, n)
    P = (P + P.T) / 2.0                      # 対称性は理論上のもの。丸めを落とす
    return ContractionCertificate(A, gamma, P, rho,
                                  float(np.linalg.norm(A, 2)))


def sweep(operator, gammas=None):
    """γ を振って、κ と増幅の釣り合いを並べる。

    γ を ρ に近づけるほど κ は小さくなるが、増幅は大きくなる。
    どちらか一方だけを良くすることはできない。
    """
    A = np.asarray(getattr(operator, "A", operator), dtype=float)
    rho = float(np.max(np.abs(np.linalg.eigvals(A))))
    if gammas is None:
        gammas = [rho + (1.0 - rho) * t for t in (0.1, 0.2, 0.5, 0.8, 0.98)]
    return [certify(A, g) for g in gammas]


# --------------------------------------------------------------------- 実演
if __name__ == "__main__":
    from trinity import TrinityOperator

    np.set_printoptions(precision=6, suppress=True)

    def title(s):
        print("\n" + s)
        print("-" * 70)

    # 論文の議論が壊れる例。trinity.py と同じ反例を使う。
    op = TrinityOperator([0.5, 0.5], [1.0, 0.0],
                         Q=np.array([[1.0, 40.0], [0.0, 1.0]]))

    title("1. 論文の議論が壊れる場所")
    print(op.report())
    print("""
  論文は「‖A‖₂ < 1 だから縮小写像、よってバナッハの定理」と進む。
  ここでは ‖A‖₂ = %.4f なので、その一行目が成り立たない。
  ただし ρ(A) = %.2f < 1 なので、**結論のほうは正しい。**
  壊れているのは議論だけである。""" % (op.operator_norm, op.spectral_radius))

    title("2. 縮小になる距離を作る")
    cert = certify(op)
    print(cert.report())
    print("""
  この距離のもとで f は縮小写像である。(ℝⁿ, d_P) は完備なので、
  バナッハの不動点定理が**そのまま**当たる。論文が使いたかった議論が、
  論文の条件を満たさないこの例でも通る。""")

    title("3. 証書そのものを検査する")
    for label, value in cert.audit().items():
        if isinstance(value, bool):
            print("  %s   %s" % ("はい  " if value else "いいえ", label))
        else:
            print("  %.9f   %s" % (value, label))
    print("""
  最後の行が κ = %.9f と一致している。κ はこのノルムでの ‖A‖_P の
  上界ではなく、達成される値そのものである。""" % cert.kappa)

    title("4. 保証した上界が、実際の誤差を本当に覆っているか")
    x0 = np.array([5.0, -3.0])
    err = op.error_curve(x0, steps=60)
    print("   段     実際の誤差        保証した上界     覆っている")
    for k in (0, 1, 2, 3, 5, 10, 20, 40, 60):
        b = cert.bound(k, err[0])
        print("  %3d   %14.6g   %14.6g       %s"
              % (k, err[k], b, "はい" if err[k] <= b * (1 + 1e-9) else "いいえ"))
    ok = all(err[k] <= cert.bound(k, err[0]) * (1 + 1e-9) for k in range(len(err)))
    print("\n  全 %d 段で上界の内側: %s" % (len(err), "はい" if ok else "いいえ"))

    title("5. γ を振ると何が釣り合うか")
    print("  （実際の誤差は γ に依らない。上界だけが動く）")
    print("   γ          κ           増幅        第 20 段の上界     実際")
    for c in sweep(op):
        print("  %.4f   %.6f   %10.4g   %14.4g   %10.4g"
              % (c.gamma, c.kappa, c.amplification,
                 c.bound(20, err[0]), err[20]))
    print("""
  γ を ρ = %.2f に近づけるほど κ は小さくなるが、増幅は大きくなる。
  「どんな ρ < 1 でも κ < 1 の距離が取れる」が構成の内容であって、
  「良い定数が取れる」ではない。そこは取り違えないほうがいい。""" % cert.rho)

    title("6. 論文の設定では、この構成は何もしない")
    s2 = TrinityOperator([0.5, 0.7, 0.3], [1, 0, 0.5])
    c2 = certify(s2)
    print("  Series II   ρ = %.6f   ‖A‖₂ = %.6f   κ = %.6f   増幅 = %.4f"
          % (c2.rho, c2.euclidean, c2.kappa, c2.amplification))
    print("""
  ‖A‖₂ < 1 なので、論文の議論はそのまま通る。作り直す必要が無い。
  この構成が効くのは ρ < 1 ≤ ‖A‖₂ の領域だけである。""")

    print("\n" + "-" * 70)
    print("""これは新しい数学ではない。ρ に任意に近いノルムが存在することは
Ostrowski / Householder の古典的な結果で、リアプノフ方程式を解いてそれを
構成するのも標準的な手順である。ここでやったのは、存在で終わっている
構成を実際に出力させ、出したものが本当に主張どおりかを検査したことだけ。

意味があるのは文脈のほうである。三本の論文の議論は ρ < 1 ≤ ‖A‖₂ で
壊れるが、壊れたままにしておく必要はない。""")
