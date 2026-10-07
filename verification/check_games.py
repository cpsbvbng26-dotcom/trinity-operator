#!/usr/bin/env python3
"""games/README.md の数値と命題を確かめる。

    python3 verification/check_games.py

NumPy のみ。乱数は使わない。

二つのことを見る。
1. 頁が書いている数値が、games/games.py --values の出す数値と一字一句合うか。
2. 各命題を、台本とは別の計算で確かめる。台本の関数は使わない。
   台本が間違っていれば、頁と台本は一致したまま両方とも間違う。それを止める。

予想（黄金比の窓の予想、Golden-window conjecture の (a)・(b)）は証明しない。頁が根拠として書いていること
（成長率が 1/δ を下回る、次元の推定が δ とともに増える）だけを確かめる。
"""

import itertools
import math
import os
import subprocess
import sys
from fractions import Fraction as Fr

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
passed, failures = 0, []


def check(name, ok, detail=""):
    global passed
    print("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""))
    if ok:
        passed += 1
    else:
        failures.append(name)


def pay(profile):
    """G_n の利得。profile は 'C'/'D' の並び。"""
    out = []
    for i, a in enumerate(profile):
        k = sum(1 for j, b in enumerate(profile) if j != i and b == "C")
        out.append(k + 1 if a == "C" else k + 2)
    return tuple(out)


page = open(os.path.join(ROOT, "games", "README.md"), encoding="utf-8").read()

# ------------------------------------------------------------ 頁と台本
print("頁と台本")
out = subprocess.run([sys.executable, os.path.join(ROOT, "games", "games.py"), "--values"],
                     capture_output=True, text=True, cwd=ROOT)
check("台本が走る", out.returncode == 0, out.stderr.strip()[-200:])
rows = [line.split("\t", 1) for line in out.stdout.splitlines() if "\t" in line]
check("台本が値を出す", len(rows) > 0, "%d 個" % len(rows))
for key, value in rows:
    check("頁に %s = %s がある" % (key, value), value in page)
vals = dict(rows)

# ------------------------------------------------------------ 利得表
print("\n利得表（Series I の Table 1）")
table = {p: pay(p) for p in itertools.product("CD", repeat=3)}
check("(C,D,C) の利得は (2,4,2)", table[("C", "D", "C")] == (2, 4, 2))
check("4 を得るのは表の最大値で、プレイヤー 2 に 4 を与えるのは (C,D,C) だけ",
      max(max(v) for v in table.values()) == 4
      and [p for p, v in table.items() if v[1] == 4] == [("C", "D", "C")])
face = {p: Fr(v[1]) + Fr(v[0] + v[2], 2) for p, v in table.items()}
check("どの結果も v₂ + (v₁+v₃)/2 ≤ 6", all(x <= 6 for x in face.values()))
check("等号は (C,C,C) と (C,D,C) だけ",
      sorted(p for p, x in face.items() if x == 6) == [("C", "C", "C"), ("C", "D", "C")])
check("ミニマックスは 2（他が全員 D のとき最善の応答で 2）",
      max(pay(("C", "D", "D"))[0], pay(("D", "D", "D"))[0]) == 2)

# ------------------------------------------------------------ 補題 1
print("\n補題 1（継続価値は作用素の不動点）")
sys.path.insert(0, ROOT)
from trinity import TrinityOperator, cyclic_shift  # noqa: E402

worst = 0.0
for m in range(2, 7):
    for delta in (0.3, 0.6, 0.9):
        p = np.arange(1.0, m + 1.0) ** 2
        fp = TrinityOperator(delta, p, Q=cyclic_shift(m).T).fixed_point()
        V = np.zeros(m)
        for _ in range(4000):                      # 後ろ向きに V_k = (1−δ)p_k + δV_{k+1}
            V = (1 - delta) * p + delta * np.roll(V, -1)
        worst = max(worst, float(np.abs(fp - V).max()))
check("作用素の不動点と、価値の再帰を回した値が一致する（m = 2〜6、δ = 0.3・0.6・0.9）",
      worst < 1e-12, "最大差 %.1e" % worst)

# ------------------------------------------------------------ 命題 1
print("\n命題 1（三人の巡回は δ ≥ 1/φ）")
phi_inv = (math.sqrt(5) - 1) / 2


def rotation3_ok(delta):
    """利得表から直接。各位相で協調している者の逸脱を、明示的に足して比べる。"""
    path = [("D", "C", "C"), ("C", "D", "C"), ("C", "C", "D")]
    for start in range(3):
        for i in range(3):
            prof = path[start]
            if prof[i] == "D":
                continue
            on = sum((1 - delta) * delta ** s * pay(path[(start + s) % 3])[i] for s in range(3000))
            dev = list(prof)
            dev[i] = "D"
            off = (1 - delta) * pay(tuple(dev))[i] + delta * 2
            if on < off - 1e-12:
                return False
    return True


check("1/φ の少し上で成り立つ", rotation3_ok(phi_inv + 1e-6))
check("1/φ の少し下で成り立たない", not rotation3_ok(phi_inv - 1e-6))
for x in (Fr(1, 3), Fr(1, 2), Fr(5, 7), Fr(2)):
    lhs = x ** 3 + 2 * x ** 2 - 1
    rhs = (x + 1) * (x ** 2 + x - 1)
    if lhs != rhs:
        break
check("δ³ + 2δ² − 1 = (δ + 1)(δ² + δ − 1)（有理数の四点で恒等）", lhs == rhs)
check("1/φ は δ² + δ − 1 の根", abs(phi_inv ** 2 + phi_inv - 1) < 1e-15)

# ------------------------------------------------------------ 命題 2
print("\n命題 2（n 人の巡回の閾値）")


def rot_ok(n, delta):
    """全位相・全員について、価値を有限和で直接出して逸脱と比べる。"""
    stage_c, stage_d, dev = n - 1, n + 1, n
    S = 1 - delta ** n
    for j in range(1, n):            # 自分が D になるまで j 期
        V = (stage_c * (1 - delta ** n) + (stage_d - stage_c) * (1 - delta) * delta ** j) / S
        if V < (1 - delta) * dev + 2 * delta - 1e-13:
            return False
    return True


def threshold(n):
    lo, hi = 0.0, 1.0
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if rot_ok(n, mid) else (mid, hi)
    return hi


def f_exact(n, x):
    """f_n(δ) = (n−2)δ − 1 + 2δⁿ⁻¹/(1 + δ + … + δⁿ⁻¹) を有理数で。"""
    return (n - 2) * x - 1 + 2 * x ** (n - 1) / sum(x ** k for k in range(n))


bounds_ok, mono_ok = True, True
for n in range(3, 31):
    # 差は n = 13 で倍精度の幅を割る。区間の両端で f_n の符号を有理数で見る。
    # f_n は狭義増加なので、符号が −/+ なら根はその間にある。
    upper = Fr(1, n - 2)
    lower = max(Fr(0), upper - Fr(2, (n - 2) ** n))
    if not (f_exact(n, lower) < 0 < f_exact(n, upper)):
        bounds_ok = False
    grid = [rot_ok(n, k / 2000) for k in range(1, 2000)]
    if any(a and not b for a, b in zip(grid, grid[1:])):   # 一度成り立てば以後も
        mono_ok = False
check("n = 3〜30 で f_n(1/(n−2) − 2/(n−2)ⁿ) < 0 < f_n(1/(n−2))（有理数で厳密に）", bounds_ok)
check("n = 3〜30 で、成り立つ δ の集合は区間 [δ_n, 1)", mono_ok)
check("δ_3 は 1/φ", abs(threshold(3) - phi_inv) < 1e-9)
for n in range(4, 11):
    check("δ_%d が台本と合う" % n, "%.6f" % threshold(n) == vals.get("delta%d" % n))

# ------------------------------------------------------------ 命題 3
print("\n命題 3（(2,4,2) は持続しない）")
ok3 = True
for k in range(1, 1000):
    delta = k / 1000
    on = 2.0                                          # (C,D,C) が続けばプレイヤー 1 は毎期 2
    off = (1 - delta) * pay(("D", "D", "C"))[0] + delta * 2
    ok3 = ok3 and off > on
check("δ = 0.001〜0.999 のどれでも、プレイヤー 1 の逸脱が得になる", ok3)
check("D はいつでも 2 以上を保証する",
      min(pay(("D",) + o)[0] for o in itertools.product("CD", repeat=2)) == 2)

# ------------------------------------------------------------ 命題 4
print("\n命題 4（公開の乱数があるとき、δ ≥ max(1/2, 1 − t)）")


def lottery_value(t, delta):
    """明示の構成。状態 w ∈ [3−δ, 3] で、確率 q で (C,C,C)→3、1−q で (C,D,C)→c。

    状態は w0、c、3 の三つに閉じる。この戦略のもとでの価値を線形方程式で解き、
    名乗った値と一致するか、各実現で誘因が満たされるかを返す。
    """
    c = 2 + (1 - delta) / delta
    states = [2 + t, c, 3.0]
    q = [(w - (3 - delta)) / delta for w in states]            # w = q·3 + (1−q)(3−δ)
    if any(x < -1e-12 or x > 1 + 1e-12 for x in q):
        return False
    # V_s = q_s[(1−δ)3 + δV_3] + (1−q_s)[(1−δ)2 + δV_c]
    A = np.eye(3)
    b = np.zeros(3)
    for s in range(3):
        A[s, 2] -= q[s] * delta
        A[s, 1] -= (1 - q[s]) * delta
        b[s] = q[s] * (1 - delta) * 3 + (1 - q[s]) * (1 - delta) * 2
    V = np.linalg.solve(A, b)
    labels_ok = np.allclose(V, states, atol=1e-10)
    ic1 = V[2] >= c - 1e-12 and V[1] >= c - 1e-12             # 実現した継続値 ≥ c
    ic2 = 6 - V[2] >= c - 1e-12                                 # (C,C,C) でのプレイヤー 2
    return labels_ok and ic1 and ic2


ok_suff, ok_nec = True, True
for i in range(1, 100):
    for j in range(1, 100):
        t, delta = i / 99, j / 100
        bound = max(0.5, 1 - delta)
        if delta >= bound + 1e-9 or (delta >= 0.5 and t >= 1 - delta + 1e-9):
            if delta >= 0.5 and t >= 1 - delta + 1e-9:
                ok_suff = ok_suff and lottery_value(t, delta)
        if delta < 0.5 or t < 1 - delta - 1e-9:
            c = 2 + (1 - delta) / delta
            ok_nec = ok_nec and (c > 3 or 2 * (1 - delta) + delta * c > 2 + t)
check("十分性: δ ≥ max(1/2, 1−t) の格子点で、明示の構成が価値と誘因を満たす", ok_suff)
check("必要性: それ以外の格子点で、必要条件のどれかが破れる", ok_nec)
check("t = 1 で閾値は Series I の 1/2", max(0.5, 1 - 1) == 0.5)

# ------------------------------------------------------------ 命題 5
print("\n命題 5（純粋戦略、乱数なし）")


def survive(w, delta, depth):
    if depth == 0:
        return True
    c = 2 + (1 - delta) / delta
    return any(c - 1e-9 <= (w - (1 - delta) * u) / delta <= 3 + 1e-9
               and survive((w - (1 - delta) * u) / delta, delta, depth - 1) for u in (2, 3))


def T(delta, depth=40):
    c = 2 + (1 - delta) / delta
    out = []
    for i in range(1, 101):
        t = i / 100
        w0 = 2 + t
        if any(c - 1e-9 <= (w0 - (1 - delta) * u) / delta <= 3 + 1e-9
               and survive((w0 - (1 - delta) * u) / delta, delta, depth) for u in (2, 3)):
            out.append(t)
    return out


check("(1) δ = 0.45 で空", T(0.45) == [])
for delta in (0.5, 0.55, 0.6):
    check("(2) δ = %g で {δ, 1}" % delta, T(delta) == [delta, 1.0], str(T(delta)))
for delta in (0.67, 0.7, 0.8, 0.9):
    want = [i / 100 for i in range(1, 101) if i / 100 >= 1 - delta - 1e-9]
    check("(3) δ = %g で [1 − δ, 1]（格子上）" % delta, T(delta) == want)
check("u = 2 の枝が使える条件 c ≤ 2 + δ は δ ≥ 1/φ",
      all((2 + (1 - d) / d <= 2 + d + 1e-12) == (d >= phi_inv)
          for d in [k / 1000 for k in range(500, 1000)]))
check("二つの枝が [c, 3] を覆う条件 2 + δ ≥ 4 − 2δ は δ ≥ 2/3",
      all((2 + d >= 4 - 2 * d - 1e-12) == (d >= 2 / 3 - 1e-12)
          for d in [k / 1000 for k in range(500, 1000)]))

# ------------------------------------------------------------ 命題 5 (3)
print("\n命題 5 (3)（δ = 1/φ ちょうどでは可算無限）")
d = phi_inv
c = 2 + (1 - d) / d
check("δ = 1/φ で c = 2 + δ", abs(c - (2 + d)) < 1e-12)


def orbit_reaches_three(w, d, steps=80):
    """3 は u = 3 の不動点。着いたら生き残る。丸めの誤差は 1/δ 倍ずつ育つので、そこで止める。"""
    cc = 2 + (1 - d) / d
    for _ in range(steps):
        if abs(w - 3) < 1e-9:
            return True
        nxt = [(w - (1 - d) * u) / d for u in (2, 3)]
        nxt = [x for x in nxt if cc - 1e-9 <= x <= 3 + 1e-9]
        if not nxt:
            return False
        w = nxt[0]
    return False


ok_pts = all(orbit_reaches_three(3 - (3 - c) * d ** n, d) for n in range(12))
check("点列 3 − (3 − c)δⁿ（n = 0〜11）がどれも 3 に着く", ok_pts)
mid = [3 - (3 - c) * d ** (n + 0.5) for n in range(12)]
check("点列の間の点（n + 1/2）はどれも生き残らない", not any(orbit_reaches_three(w, d) for w in mid))

# ------------------------------------------------------------ 命題 6
print("\n命題 6（窓の中で次元は正）")


def check_window(d):
    """台本の関数を使わずに、枝の区間と下界を当たり直す。"""
    X = (2 * d - 1) / (d * (1 - d))
    beta = 1 / d
    if not (d * X < 1 < X):
        return False, "δX < 1 < X が崩れる"
    n0 = next(n for n in range(1000) if beta ** (n + 1) >= X / (X - 1))
    prev = None
    for n in range(n0, n0 + 40):
        # x = 1 + ε と置いて ε のまま扱う。1 + ε から 1 を引くと桁が落ちる。
        e_lo, e_hi = d ** (n + 1), X * d ** (n + 1)
        if not (0 < e_lo < e_hi <= X - 1):
            return False, "J_%d が [1, X] に入らない" % n
        f = lambda e: beta ** (n + 1) * e
        if abs(f(e_lo) - 1) > 1e-9 or abs(f(e_hi) - X) > 1e-9:
            return False, "J_%d が [1, X] へ写らない" % n
        for e in (e_lo, (e_lo + e_hi) / 2, e_hi):
            for j in range(n):                     # 途中の値は穴に落ちない
                if beta ** (j + 1) * e > d * X * (1 + 1e-12):
                    return False, "途中で穴に入る"
        if prev is not None and not (e_hi < prev[0]):
            return False, "J_%d と J_%d が重なる" % (n, n - 1)
        prev = (e_lo, e_hi)
    # 下界 s を級数で（台本は閉じた式で解く）
    lo_s, hi_s = 1e-9, 1.0
    for _ in range(100):
        sm = (lo_s + hi_s) / 2
        total = sum(d ** ((n + 1) * sm) for n in range(n0, n0 + 20000))
        lo_s, hi_s = (sm, hi_s) if total > 1 else (lo_s, sm)
    return True, (n0, (lo_s + hi_s) / 2)


bounds = {}
ok6 = True
for dd in (0.62, 0.63, 0.64, 0.65, 0.66):
    good, info = check_window(dd)
    if not good:
        ok6 = False
        print("    ", dd, info)
    else:
        bounds[dd] = info
check("五つの δ で、枝の区間が [1, X] に入り、互いに素で、穴を通らない", ok6)
gap_rows = {float(r.strip("|").split("|")[0]): [x.strip() for x in r.strip("|").split("|")]
            for k, r in rows if k.startswith("gap_")}
check("下界 s と n₀ を級数で求め直すと台本と合う",
      all(abs(float(gap_rows[dd][6]) - s_) < 5e-4 and int(gap_rows[dd][5]) == n0
          for dd, (n0, s_) in bounds.items()))
check("下界はどれも正", all(s_ > 0 for _, s_ in bounds.values()))
check("δ = 0.62 では、有限の深さの推定が下界を下回る（頁がそう書いている）",
      float(gap_rows[0.62][4]) < float(gap_rows[0.62][6])
      and "the finite-depth estimate is too low there" in page)

# ------------------------------------------------------------ 1/φ が二度出る
print("\n1/φ が二度出る")
check("δ² = 1 − δ なら 1 − δ³ = 2δ²（δ = 1/φ）", abs((1 - phi_inv ** 3) - 2 * phi_inv ** 2) < 1e-12)
check("頁が、これを予想ではなく問いとして置き、利得への依存を書いている",
      "may depend on the defector's bonus being 2" in page)

# ------------------------------------------------------------ 予想の根拠
print("\n予想の根拠（証明ではない）")
growth = {}
for line in [v for k, v in rows if k.startswith("gap_")]:
    cells = [x.strip() for x in line.strip("|").split("|")]
    growth[float(cells[0])] = (float(cells[3]), float(cells[4]))
check("五つの δ がある", len(growth) == 5)
check("どの行も成長率 < 1/δ（総長が縮む）",
      all(g < 1 / d for d, (g, _) in growth.items()))
dims = [growth[d][1] for d in sorted(growth)]
check("次元の推定が δ とともに増える", all(a < b for a, b in zip(dims, dims[1:])))
check("次元の推定が 0 と 1 の間", all(0 < x < 1 for x in dims))
check("頁が黄金比の窓の予想を、名前つきで予想と名乗っている",
      "**Golden-window conjecture (a).**" in page and "**Golden-window conjecture (b).**" in page
      and page.count("| **conjecture** |") == 2
      and "It is not named after a person." in page)
check("頁が文献と照合していないと書いている",
      "None of the propositions has been checked against the literature." in page)
check("頁が Claude を著者にしていない", "Claude is not an author." in page)
check("頁が名乗る貢献を、理論でない・未照合・第三者の公認なしの条件つきで書いている",
      "This is not a theory. The proofs have not been checked against the literature, and no\nthird party has recognised them." in page
      and "| a mathematical contribution as mathematical proof |" in page
      and "| a mathematical contribution as a mathematical conjecture |" in page
      and "| a contribution as a case study in the philosophy of science |" in page)
check("頁が数学的意義を文献照合の条件つきで書き、科学哲学的意義を残している",
      "Everything in the first half of this section is conditional on the literature check." in page
      and "None of this makes the operator new, and none of it is a new theory." in page
      and "10.2139/ssrn.7537983" in page)
check("頁が、予想が解けても枠組みは新理論にならないと書き、1/φ の重なりを問いとして置いている",
      "The framework does not become a new theory." in page
      and "It is recorded as a question, not as a\nconjecture." in page)
check("頁が、三篇はゼロ、命題はまだ数えていない、と分けて書いている",
      "| the three papers | a special case of a known model | zero |" in page
      and "| Propositions 1–6 | proved; literature not checked | not yet counted |" in page
      and "That is not the same as zero." in page)

print("\n" + "-" * 58)
if failures:
    print("%d 件が通り、%d 件が通りませんでした。" % (passed, len(failures)))
    for f in failures:
        print("  - " + f)
    sys.exit(1)
print("%d 件すべて通りました。" % passed)
