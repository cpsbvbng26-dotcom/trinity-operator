#!/usr/bin/env python3
"""三元の再帰作用素を、論文が置いた仮定の外まで一般化して扱う。

（ファイル名は trinity.py。operator.py にすると標準ライブラリの operator を
 覆い隠して、import が壊れる。）

Trinity-Infinity の三本が扱うのは、次の形の反復である。

    x ← D Q x + (I − D) p          D = diag(a),  Q = 巡回置換行列

三本が到達した条件は次のとおり。

    Series I    Q は巡回置換（等長写像）、a は一様なスカラ α ∈ (0,1)
                → ‖f(x) − f(y)‖ = α‖x − y‖ なので縮小写像
    Series II   a を座標ごとに変える → 縮小定数 maxᵢ aᵢ
    Series III  三要素である必要はない。任意の n ≥ 2 で同じ

**三本はいずれも「作用素ノルムが 1 未満」までしか言っていない。** これは
十分条件であって、必要条件ではない。この実装はそこを分ける。

    収束（任意の初期値から一意の不動点へ）  ⟺  ρ(DQ) < 1     ← スペクトル半径
    単調な幾何減衰                          ⟸  ‖DQ‖₂ < 1    ← 作用素ノルム

    ρ(DQ) ≤ ‖DQ‖₂ なので、後者は前者を含む。等号は Q が正規行列のとき。
    論文の設定（Q が置換 ＝ 直交）はちょうど等号の場合で、だから区別が
    表に出てこなかった。

区別が効くのは、ρ < 1 ≤ ‖DQ‖₂ の場合である。収束はするが、**誤差はいったん
増えてから減る。** 論文の「初手から幾何的に減衰する」という描像は、そこでは
成り立たない。demo.py がその例を出す。

これは新しい数学ではない。非正規行列の過渡的増幅は数値線形代数の標準的な事実
であり、この実装が主張するのは「三本が置いた仮定は必要以上に強い」という一点
だけである。
"""

import numpy as np

__all__ = ["TrinityOperator", "cyclic_shift"]


def cyclic_shift(n):
    """(σ(x))ᵢ = x₍ᵢ₋₁ mod n₎ を表す n×n の巡回置換行列。論文の σ。"""
    Q = np.zeros((n, n))
    for i in range(n):
        Q[i, (i - 1) % n] = 1.0
    return Q


def permutation_cycles(Q):
    """Q が置換行列なら、その巡回を返す。置換でなければ None。

    (Qx)ᵢ = x_σ(ᵢ) と読む。σ の巡回に分ける。
    """
    Q = np.asarray(Q, dtype=float)
    n = Q.shape[0]
    if Q.shape != (n, n):
        return None
    if not np.allclose(np.sort(Q, axis=1)[:, :-1], 0):
        return None
    if not np.allclose(np.max(Q, axis=1), 1) or not np.allclose(Q.sum(axis=0), 1):
        return None
    sigma = [int(np.argmax(Q[i])) for i in range(n)]
    seen, out = set(), []
    for i in range(n):
        if i in seen:
            continue
        cycle, j = [], i
        while j not in seen:
            seen.add(j)
            cycle.append(j)
            j = sigma[j]
        out.append(cycle)
    return out


class TrinityOperator:
    """x ← D Q x + (I − D) p。

    Q      任意の正方行列。既定は巡回置換（論文の設定）
    blend  スカラ、または座標ごとの配列 a
    anchor 統合の基準点 p

    論文は Q を置換に、a を (0,1) に限っているが、ここでは制限しない。
    どこまで成り立つかを見るための実装だからである。
    """

    def __init__(self, blend, anchor, Q=None):
        self.p = np.asarray(anchor, dtype=float)
        self.n = self.p.size
        self.Q = cyclic_shift(self.n) if Q is None else np.asarray(Q, dtype=float)
        if self.Q.shape != (self.n, self.n):
            raise ValueError("Q は %d×%d でなければなりません" % (self.n, self.n))
        a = np.asarray(blend, dtype=float)
        self.a = np.full(self.n, float(a)) if a.ndim == 0 else a
        if self.a.size != self.n:
            raise ValueError("blend の長さが anchor と合いません")
        self.A = np.diag(self.a) @ self.Q          # 線形部分
        self.b = (np.eye(self.n) - np.diag(self.a)) @ self.p   # 定数部分

    # ------------------------------------------------------------------ 反復
    def step(self, x):
        return self.A @ np.asarray(x, dtype=float) + self.b

    def iterate(self, x0, steps):
        """各段の状態を返す（長さ steps+1）。"""
        x = np.asarray(x0, dtype=float)
        out = [x.copy()]
        for _ in range(steps):
            x = self.step(x)
            out.append(x.copy())
        return np.array(out)

    # -------------------------------------------------------------- 判定
    @property
    def spectral_radius(self):
        """ρ(A)。収束するかどうかは、ここだけで決まる。"""
        return float(np.max(np.abs(np.linalg.eigvals(self.A))))

    @property
    def operator_norm(self):
        """‖A‖₂。論文が縮小定数として挙げているもの。"""
        return float(np.linalg.norm(self.A, 2))

    @property
    def converges(self):
        """任意の初期値から一意の不動点へ行くか。"""
        return self.spectral_radius < 1.0

    @property
    def monotone(self):
        """誤差が初手から単調に減るか。論文が仮定している状況。"""
        return self.operator_norm < 1.0

    @property
    def is_normal(self):
        """A が正規行列か。このとき ρ = ‖A‖₂ で、両者の区別が消える。"""
        return bool(np.allclose(self.A @ self.A.T.conj(), self.A.T.conj() @ self.A))

    # -------------------------------------------------- 論文の設定の閉じた式
    #
    # 論文は Q を置換に限っている。その範囲なら、固有値も特異値も手で書ける。
    # **論文はこの構造を使っていない。**縮小定数として挙げたのは max aᵢ で、
    # それは ‖A‖₂ ちょうどであって、収束率ではない。
    #
    #   ‖DQ‖₂ = maxᵢ |aᵢ|                     Q が直交なので特異値は |aᵢ| そのもの
    #   ρ(DQ) = max_c (∏_{i∈c} |aᵢ|)^(1/|c|)  c は σ の巡回。巡回内の幾何平均
    #
    # 幾何平均 ≤ 最大値。等号は巡回の中の aᵢ がすべて等しいときだけ。
    # Series I は aᵢ を一様なスカラに取っているので、そこで等号が立つ。
    # **区別の存在しない設定から始めたため、区別が要ることが見えなかった。**

    @property
    def cycles(self):
        """Q の巡回。Q が置換でなければ None。"""
        return permutation_cycles(self.Q)

    @property
    def closed_form_norm(self):
        """置換の場合の ‖A‖₂ = maxᵢ |aᵢ|。置換でなければ None。"""
        if self.cycles is None:
            return None
        return float(np.max(np.abs(self.a)))

    @property
    def closed_form_radius(self):
        """置換の場合の ρ(A)。巡回ごとの幾何平均の最大値。置換でなければ None。"""
        cs = self.cycles
        if cs is None:
            return None
        return float(max(np.prod(np.abs(self.a[c])) ** (1.0 / len(c)) for c in cs))

    # -------------------------------------------------------------- 不動点
    def fixed_point(self):
        """x* = (I − A)⁻¹ b。ρ(A) < 1 でなければ意味を持たない。"""
        if not self.converges:
            raise ValueError("ρ(A) = %.6f ≥ 1 なので不動点へは収束しません"
                             % self.spectral_radius)
        return np.linalg.solve(np.eye(self.n) - self.A, self.b)

    # ------------------------------------------------------ 過渡的な増幅
    def transient_growth(self, steps=200):
        """maxₖ ‖Aᵏ‖₂ / ‖A⁰‖₂。1 を超えるなら、誤差はいったん増える。

        ‖A‖₂ < 1 なら常に 1（増えようがない）。ρ < 1 ≤ ‖A‖₂ のときに
        大きくなりうる。この値がこの実装の眼目である。
        """
        M = np.eye(self.n)
        peak = 1.0
        for _ in range(steps):
            M = self.A @ M
            peak = max(peak, float(np.linalg.norm(M, 2)))
        return peak

    def error_curve(self, x0, steps=60):
        """‖xₖ − x*‖ の列。"""
        xs = self.iterate(x0, steps)
        return np.linalg.norm(xs - self.fixed_point(), axis=1)

    def report(self):
        lines = [
            "n = %d,  Q は %s,  a = %s" % (
                self.n,
                "巡回置換" if np.allclose(self.Q, cyclic_shift(self.n)) else "任意の行列",
                np.array2string(self.a, precision=3)),
            "  ρ(A)  = %.6f   ← 収束するかどうかはここで決まる" % self.spectral_radius,
            "  ‖A‖₂  = %.6f   ← 論文が縮小定数として挙げているもの" % self.operator_norm,
            "  正規行列: %s" % ("はい（ρ = ‖A‖₂）" if self.is_normal else "いいえ"),
            "  収束: %s / 単調減衰: %s" % (
                "する" if self.converges else "しない",
                "する" if self.monotone else "しない"),
        ]
        if self.converges:
            lines.append("  過渡的増幅 maxₖ‖Aᵏ‖₂ = %.3f%s" % (
                self.transient_growth(),
                "" if self.monotone else "   ← 誤差はいったん増えてから減る"))
        return "\n".join(lines)
