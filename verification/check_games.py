#!/usr/bin/env python3
"""games/README.md の数値と命題を確かめる。

    python3 verification/check_games.py

NumPy のみ。乱数は使わない。

四つのことを見る。
1. 頁が書いている数値が、games/games.py --values の出す数値と一字一句合うか。
2. 各命題を、台本とは別の計算で確かめる。台本の関数は使わない。
   台本が間違っていれば、頁と台本は一致したまま両方とも間違う。それを止める。
3. games/scan.py の広げた走査。games/scan.txt が台本の出力と同じか。区間の数を、台本とは
   別の座標と浮動小数点で数え直して同じになるか。ノートが書く走査の値が台本と同じか。

予想（黄金比の窓の予想、Golden-window conjecture の (a)・(b)）は、2026-11-18 に命題 8 と 9 として
証明を足した。ここでは証明そのものは確かめない。証明が言う構成と式を、台本とは別の計算で当たり直す。
4. 命題 8 の証明の段 1（筒の像がどれも 0 から始まる）を、台本とは別の座標（w）と有理数で回し直し、
   総長が期ごとに縮むことと、頁の数・窓の表の総長と合うことを見る。表の status が (a) を命題 8、
   (b) を命題 9 で証明済みとし、予想の印が残っていないことも見る。
5. 命題 9 の強制された道と A_δ を、台本とは別の座標（w）と有理数で作り直し、根を z の側の二分法で
   解き直して、頁の表の次元と合うか見る。初回帰の分け方から出る筒の数が、走査の台本の整数の数と
   一致するか（生成関数の恒等式）。δ = k/10000 の格子で、次元が真に増え、1 未満で、命題 6 の下界を
   下回らないか。
"""

import itertools
import math
import os
import re
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

# 2026-11-19 に足した。差 1/m − δ_n（m = n − 2）の一次の大きさは 2(m − 1)/m^(n+1)。
# Figshare 10.6084/m9.figshare.35050300 の Proposition 8.10 の r = 1 の場合（査読なし）。
# f_n の根を有理数の二分法で 2^-260 の幅まで挟み、相対誤差が O(n m^-(n-1)) で縮むことを見る。
def root_exact(n, steps=260):
    lo, hi = Fr(0), Fr(1, n - 2)
    for _ in range(steps):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if f_exact(n, mid) < 0 else (lo, mid)
    return lo, hi


gap_rel = []
for n in (6, 8, 10, 12, 16, 20):
    m = n - 2
    lo, hi = root_exact(n)
    pred = Fr(2 * (m - 1), m ** (n + 1))
    rel = max(abs((Fr(1, m) - x) / pred - 1) for x in (lo, hi))
    gap_rel.append((n, float(rel), float(4 * n * Fr(1, m ** (n - 1)))))
check("差 1/m − δ_n が 2(m − 1)/m^(n+1)·(1 + O(n m^-(n-1))) に合う（n = 6〜20、有理数の二分法）",
      all(r < b for _, r, b in gap_rel)
      and all(a[1] > b[1] for a, b in zip(gap_rel, gap_rel[1:]))
      and "1/m − δ_n  =  2(m − 1)/m^(n+1) · (1 + O(n m^(−(n−1))))." in page
      and "Proposition 8.10 of the resolution paper" in page,
      " / ".join("n=%d %.1e" % (n, r) for n, r, _ in gap_rel))

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

# ------------------------------------------------------------ 命題 7
print("\n命題 7（便益 b・費用 c に広げる）")


def rot_bc_ok(n, delta, r):
    """便益 1・費用 r。価値を有限和で直接出して、逸脱（n − 2 のあと 0）と比べる。"""
    coop, defect = n - 2 - r, n - 1
    S = 1 - delta ** n
    for j in range(1, n):
        V = (coop * S + (defect - coop) * (1 - delta) * delta ** j) / S
        if V < (1 - delta) * (n - 2) - 1e-13:
            return False
    return True


def bc_threshold(n, r):
    if not rot_bc_ok(n, 1 - 1e-12, r):
        return None
    lo, hi = 0.0, 1 - 1e-12
    for _ in range(90):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if rot_bc_ok(n, mid, r) else (mid, hi)
    return hi


def g_exact(n, r, x):
    """g(δ) = (n−2)δ − r + (1+r)δⁿ⁻¹/(1 + δ + … + δⁿ⁻¹) を有理数で。"""
    return (n - 2) * x - r + (1 + r) * x ** (n - 1) / sum(x ** k for k in range(n))


closed = lambda r: (math.sqrt(1 + 4 * r) - 1) / 2
check("三人では δ_3(r) = (√(1+4r) − 1)/2（r = 0.1〜1.9 の 19 点）",
      all(abs(bc_threshold(3, k / 10) - closed(k / 10)) < 1e-9 for k in range(1, 20)))
check("r = 1 で 1/φ に戻る", abs(closed(1) - phi_inv) < 1e-12)
feas_ok, harder_ok, bounds_ok = True, True, True
for n in range(3, 13):
    for r in [Fr(1, 10), Fr(1, 2), Fr(1), Fr(3, 2), Fr(n - 1) * Fr(9, 10), Fr(n - 1) * Fr(99, 100),
              Fr(n - 1), Fr(n - 1) * Fr(101, 100)]:
        t = bc_threshold(n, float(r))
        if (t is not None) != (r < n - 1):
            feas_ok = False
        if t is None:
            continue
        # 全員の協力の閾値 r/(n−1) では g < 0（有理数で）。g は増加なので δ_n(r) はその上。
        if not g_exact(n, r, r / (n - 1)) < 0 or not t > float(r) / (n - 1):
            harder_ok = False
        up = r / (n - 2)
        lo = up - (1 + r) * r ** (n - 1) / Fr(n - 2) ** n
        if up < 1 and not (g_exact(n, r, max(lo, Fr(0))) < 0 < g_exact(n, r, up)):
            bounds_ok = False
check("n = 3〜12 で、巡回が成り立つ δ < 1 があるのは r < n − 1 のときだけ", feas_ok)
check("n = 3〜12 で、δ_n(r) は全員の協力の閾値 r/(n−1) より大きい（有理数で）", harder_ok)
check("n = 3〜12 で、δ_n(r) が命題 7 の上下の界の間にある（有理数で）", bounds_ok)
check("δ_3(0.5)・δ_3(1.5) が台本と合う",
      "%.6f" % closed(0.5) == vals.get("bc3_r0.5") and "%.6f" % closed(1.5) == vals.get("bc3_r1.5"))
check("頁が、この線形のゲームは交代の協力を説明しないと書いている",
      "So the game does not\nexplain turn-taking." in page
      and "The literature on turn-taking has not been checked." in page)

# ------------------------------------------------------------ 1/φ が二度出る
print("\n1/φ が二度出る")
check("δ² = 1 − δ なら 1 − δ³ = 2δ²（δ = 1/φ）", abs((1 - phi_inv ** 3) - 2 * phi_inv ** 2) < 1e-12)
check("頁が、これを予想ではなく問いとして置き、利得への依存を書いている",
      "may depend on the defector's bonus being 2" in page)

# ------------------------------------------------------------ 命題 8
print("\n命題 8（窓の中で長さ 0。予想 (a)）")


def w_cylinders(k, depth):
    """台本とは別の計算。w の座標で、有理数で、証明の段 1 の筒を作る。

    台本は x = (3 − w)/(1 − δ) の座標で前へ写す。ここは w のまま、後ろ向きの枝
    w′ = (w − (1 − δ)u)/δ（u = 2 は [c, 2 + δ]、u = 3 は [4 − 2δ, 3]）で筒 I とその像 J を持つ。
    x の 0 は w の 3 なので、証明が言う「像は 0 から始まる」は、ここでは「像は 3 で終わる」になる。
    """
    d = Fr(k, 100)
    c = 2 + (1 - d) / d
    branches = ((Fr(2), c, 2 + d), (Fr(3), 4 - 2 * d, Fr(3)))
    cyl = [(c, Fr(3), c, Fr(3))]
    ends, lengths = set(), []
    for n in range(depth):
        new = []
        for i0, i1, j0, j1 in cyl:
            for u, lo, hi in branches:
                l, h = max(j0, lo), min(j1, hi)
                if l > h:
                    continue
                k0, k1 = (l - (1 - d) * u) / d, (h - (1 - d) * u) / d
                ends.add(k1)
                new.append((i0 + (l - j0) * d ** n, i0 + (h - j0) * d ** n, k0, k1))
        cyl = new
        lengths.append(sum(b - a for a, b, _, _ in cyl))
    return ends, lengths


CYL_DEPTH, CYL_K = 16, (62, 64, 66)
cyl_ok, shrink_ok, quoted_ok, table_ok = True, True, True, True
for k in CYL_K:
    d = k / 100
    ends, lens = w_cylinders(k, int(vals.get("depth", "0")))
    cyl_ok = cyl_ok and ends == {Fr(3)}
    shrink_ok = shrink_ok and all(a > b for a, b in zip(lens, lens[1:]))
    x0, x16 = float(lens[0]) / (1 - d), float(lens[CYL_DEPTH - 1]) / (1 - d)
    quoted_ok = quoted_ok and vals.get("cyl_%g" % d) == "from %.3g to %.3g at δ = %g" % (x0, x16, d)
    row = gap_rows.get(d)
    table_ok = table_ok and row is not None and "%.2e" % float(lens[-1]) == row[2]
check("δ = 0.62・0.64・0.66 で、どの筒の像も 0 から始まる（w では 3 で終わる。有理数で、深さ %s）"
      % vals.get("depth"), cyl_ok)
check("同じ三つの δ で、筒の総長が期ごとに真に縮む", shrink_ok)
check("台本が名乗る範囲が、ここで回した範囲と同じ（%d 期、δ = 0.62・0.64・0.66）" % CYL_DEPTH,
      vals.get("cyl_run") == "for %d periods at δ = 0.62, 0.64 and 0.66" % CYL_DEPTH
      and "for %d periods at δ = 0.62, 0.64 and 0.66" % CYL_DEPTH in page)
check("1 期目と 16 期目の総長（x の長さ）が、台本の値と同じ", quoted_ok)
check("筒の総長が、窓の表の総長（深さ %s、w の長さ）と同じ" % vals.get("depth"), table_ok)
flat_p8 = re.sub(r"\s+", " ", page)
check("頁が、命題 8 を書いた者・日付・責任と、照合で既知の定理の特別な場合（ゼロ）と数えたことを書いている",
      "This proposition is part (a) of the golden-window conjecture below. The proof was written by Claude Code at the author's request on 2026-11-18. The author is responsible for it."
      in flat_p8
      and "The literature was checked on the same day. Proposition 8 is known. It is an immediate special case of Lu, Steiner and Zou (2026), Proposition 2.5 and its proof,"
      in flat_p8
      and "(Rényi 1957; Parry 1960); that statement is recalled, not read." in flat_p8
      and "Under the counting of this note, Proposition 8 is zero: checked, and not new." in flat_p8)
check("頁に命題 8 の節と言明と、証明の末尾の ∎ がある（証明を足してから表を動かす）",
      "\n## Proposition 8 — length zero inside the window\n" in page
      and "**Proposition 8.** For 1/φ < δ < 2/3, `S` has Lebesgue measure zero, and so does `T_δ`." in page
      and "has measure zero. ∎" in page)
check("頁が、凍結したプレプリントは (a)・(b) を予想のまま載せていると書いている",
      "The preprint states both parts of the conjecture as conjectures, and it stays that way." in flat_p8)
check("頁が、命題 9 を書いた者・日付・責任・式は既知の定理の特別な場合・連続と単調と極限は見つからずまだ数えないことと、強い単調性を書き、文献を記憶から足していない",
      "## Proposition 9 — the dimension inside the window" in page
      and "This proposition is part (b) of the golden-window conjecture below. The proof was written by Claude Code at the author's request on 2026-11-18. The author is responsible for it. The literature was checked on the same day. The formula of Proposition 9 is a special case of Lu, Steiner and Zou (2026), Theorem 1.2 with Lemma 2.7."
      in flat_p8
      and "were not found in the texts read. They are not yet counted." in flat_p8
      and "That is the inference of the literature check, not a statement of the paper." in flat_p8
      and "Strictly increasing is stronger than the \"non-decreasing\" of conjecture (b)." in flat_p8
      and "the standard theorem on self-similar sets under the strong separation condition" in flat_p8
      and "Hutchinson" not in page and "Falconer" not in page)

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
# 2026-11-18 に (a) を命題 8 で証明した。証明を足してから表を動かした。(a) の行は名前を残して
# 「proved (Proposition 8)」に、予想の印は (b) の一つだけに。どちらかが崩れれば落ちる。
check("頁が黄金比の窓の予想を名前つきで置き、(a) を命題 8、(b) を命題 9 で解決済み（既知の定理の特別な場合と、見つからない部分）と書き、予想の印を残していない",
      "**Golden-window conjecture (a).**" in page and "**Golden-window conjecture (b).**" in page
      and page.count("| **conjecture** |") == 0
      and "\n| Golden-window conjecture (a) | for 1/φ < δ < 2/3, the sustainable set has length zero | resolved (Proposition 8); a special case of known theorems |\n" in page
      and "\n| Golden-window conjecture (b) | its dimension is below 1, continuous and non-decreasing, and runs from 0 to 1 across the interval | resolved (Proposition 9); the formula is a special case of known theorems; continuity, strict increase and the end limits were not found in the texts read |\n" in page
      and "\n| Proposition 8 | inside the window 1/φ < δ < 2/3, the sustainable set has length zero | proved |\n" in page
      and "\n| Proposition 9 | inside the window, the dimension of the sustainable set is the root `s` of `Σ_{n ∈ A_δ} δ^(ns) = 1`; it is below 1, continuous and strictly increasing, and runs from 0 to 1 across the interval | proved |\n" in page
      and "It is not named after a person." in page)
check("頁が、測度 0 では (b) が決まらないこと、(b) は命題 9 で別に証明したこと、名前を問題の名として残すことを書いている",
      "Part (b) is proved. It is Proposition 9, written on 2026-11-18. Measure zero does not settle it:" in re.sub(r"\s+", " ", page)
      and "Both parts are proved, so the conjecture is resolved. Its status is resolved (part (a) and the formula of part (b) are special cases of known theorems; continuity and strict increase in δ and the limits at both ends were not found in the texts read). The name stays as the name of the problem."
      in re.sub(r"\s+", " ", page))
# 2026-11-18 に命題 8 と 9 だけを要旨まで照合した。命題 1〜7 は照合していないと書く文に移した。
check("頁が、命題 1〜7 は文献と照合していないと書いている",
      "Propositions 1–7 have not been checked against the literature." in page)
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
      and "| Propositions 1–7 | proved; literature not checked | not yet counted |" in page
      and "| Proposition 8 | proved; a special case of known theorems | zero |" in page
      and "| Proposition 9 | proved; the formula and the bound below 1 are special cases of known theorems; continuity, strict increase and the end limits were not found in the texts read | the formula: zero; the rest: not yet counted |" in page
      and "| golden-window conjecture | resolved (part (a) and the formula of part (b) are special cases of known theorems; continuity and strict increase in δ and the limits at both ends were not found in the texts read) | part (a) zero; part (b) partly zero, partly not yet counted |" in page
      and "That is not the same as zero." in page)

# ------------------------------------------------------------ 広げた走査
print("\n広げた走査（games/scan.py。証拠であって証明ではない）")
# 台本は一度だけ回す（深さ 30 で 48 通り。数秒かかる）。表と値は同じ計算から出る。
sys.path.insert(0, os.path.join(ROOT, "games"))
import scan as scan_mod  # noqa: E402
import games as games_mod  # noqa: E402

scan_lines, sv = scan_mod.exploratory()
scan_txt = open(os.path.join(ROOT, "games", "scan.txt"), encoding="utf-8").read()
check("games/scan.txt が台本の出力と一字一句同じ（生成物）", scan_mod.render(scan_lines, sv) == scan_txt)
check("走査の台本が値を出す", len(sv) > 0, "%d 個" % len(sv))

scan_rows = []
for line in scan_txt.splitlines():
    cells = [x.strip() for x in line.strip("|").split("|")]
    if line.startswith("| 0.") and len(cells) == 10:
        scan_rows.append(cells)
check("走査の表が台本の名乗る行数だけある", str(len(scan_rows)) == sv.get("scan_rows"),
      "%d 行" % len(scan_rows))


def x_counts(d, depth):
    """台本とは別の計算。x = (3 − w)/(1 − δ) の座標で、浮動小数点で数える。

    台本は w の座標で、端点を整数に持って数える。座標も算術も違う二つが同じ数を出すか見る。
    x = a + δx′（a ∈ {0, 1}）を [0, X] の中で前へ写し、[0, X] からはみ出す分を切る。
    """
    X = (2 * d - 1) / (d * (1 - d))
    ivs = [(0.0, X)]
    out = []
    for _ in range(depth):
        nxt = []
        for a, b in ivs:
            for s in (0.0, 1.0):
                lo, hi = max(s + d * a, 0.0), min(s + d * b, X)
                if lo <= hi + 1e-12:
                    nxt.append((lo, hi))
        ivs = nxt
        out.append(len(ivs))
    return out


depth_s = int(sv.get("scan_depth", "0"))
mine = {}
for cells in scan_rows:
    d = float(cells[0])
    c = x_counts(d, depth_s)
    mine[d] = c
same = all(str(mine[float(cells[0])][-1]) == cells[1] for cells in scan_rows)
check("区間の数を、別の座標と浮動小数点で数え直すと、%d 行すべてで表と同じ" % len(scan_rows), same)
grid = sorted(mine)
step_ok = len(grid) > 1 and all(abs((b - a) - 0.001) < 1e-9 for a, b in zip(grid, grid[1:]))
check("走査の δ が窓の中にあり、0.001 刻みで並ぶ",
      step_ok and phi_inv < grid[0] and grid[-1] < 2 / 3, "%s〜%s" % (grid[0], grid[-1]))

LAST_S = 5
g = {d: (mine[d][-1] / mine[d][-1 - LAST_S]) ** (1 / LAST_S) for d in grid}
dimest = [math.log(g[d]) / math.log(1 / d) for d in grid]
upper = [math.log(mine[d][-1]) / (depth_s * math.log(1 / d)) for d in grid]
shrink = sum(1 for d in grid if g[d] < 1 / d)
check("数え直した数で、総長が縮む行（成長率 < 1/δ）の数が台本と同じ",
      "%d of %d" % (shrink, len(grid)) == sv.get("scan_shrink"), sv.get("scan_shrink", ""))
check("数え直した数で、成長率 × δ の最大が台本と同じ",
      "%.3f" % max(g[d] * d for d in grid) == sv.get("scan_max_growth_delta"))
check("数え直した数で、次元の推定が下がる箇所の数が台本と同じ",
      "%d" % sum(1 for a, b in zip(dimest, dimest[1:]) if b < a) == sv.get("scan_decreases"))
check("数え直した数で、次元の推定の両端が台本と同じ",
      "%.2f" % dimest[0] == sv.get("scan_dim_first") and "%.2f" % dimest[-1] == sv.get("scan_dim_last"))
below1 = [d for d, u in zip(grid, upper) if u < 1]
check("数え直した数で、上からの推定が 1 を下回る行の数と、その範囲が台本と同じ",
      "%d of %d" % (len(below1), len(grid)) == sv.get("scan_upper_below_one")
      and below1 == grid[:len(below1)] and "%.3f" % below1[-1] == sv.get("scan_upper_below_one_to"))


def lower_closed(d):
    """命題 6 の下界。n₀ は定義どおり最小の n を探し、s は閉じた式を二分法で解く。"""
    X = (2 * d - 1) / (d * (1 - d))
    n0 = next(n for n in range(1000) if (1 / d) ** (n + 1) >= X / (X - 1))
    lo_s, hi_s = 1e-12, 1.0
    for _ in range(100):
        sm = (lo_s + hi_s) / 2
        lo_s, hi_s = (sm, hi_s) if d ** ((n0 + 1) * sm) > 1 - d ** sm else (lo_s, sm)
    return n0, (lo_s + hi_s) / 2


lows = {d: lower_closed(d) for d in grid}
check("表の n₀ と下界の列が、命題 6 を解き直した値と合う",
      all(int(cells[8]) == lows[float(cells[0])][0] and abs(float(cells[9]) - lows[float(cells[0])][1]) < 5e-4
          for cells in scan_rows))
check("数え直した推定が命題 6 の下界を下回る行の数が、台本と同じ",
      "%d" % sum(1 for d, e in zip(grid, dimest) if e < lows[d][1]) == sv.get("scan_below_lower"))

agree = all([n for n, _ in games_mod.refine(dd)] == scan_mod.refine_exact(round(dd * 100), 100, games_mod.DEPTH)[0]
            for dd in games_mod.GAP)
check("整数で数えた区間の数が、games.py の浮動小数点の細分（深さ 22、五つの δ）と同じ", agree)

flat_note = re.sub(r"\s+", " ", page)
quotes = [
    "It takes δ = %s, …, %s, which is %s values at step 0.001" % (sv["scan_first"], sv["scan_last"], sv["scan_rows"]),
    "and refines for %s periods." % sv["scan_depth"],
    "Growth is below `1/δ` in %s rows" % sv["scan_shrink"],
    "The largest value of growth × δ is %s, at δ = %s." % (sv["scan_max_growth_delta"], sv["scan_max_growth_delta_at"]),
    "The scan counts %s decreases." % sv["scan_decreases"],
    "The estimate runs from %s at the first δ to %s at the last." % (sv["scan_dim_first"], sv["scan_dim_last"]),
    "In %s rows the estimate is below the lower bound of Proposition 6" % sv["scan_below_lower"],
    "It is below 1 in %s rows, for every δ up to %s." % (sv["scan_upper_below_one"], sv["scan_upper_below_one_to"]),
    "Five values cannot settle it, and the %s values of the wider scan below cannot either." % sv["scan_rows"],
    "A grid of %s values cannot rule out a δ between its points" % sv["scan_rows"],
]
for q in quotes:
    check("ノートに走査の値がある：%s" % q[:48], q in flat_note)
check("走査の範囲が上から続いている（「every δ up to」と書ける）", sv.get("scan_upper_contiguous") == "yes")
check("ノートが、走査は証明ではないと書き、上からの推定を根拠としてだけ扱っている",
      "None of this is a proof." in flat_note
      and "so the column is reported as evidence only." in flat_note)

# ------------------------------------------------------------ 命題 9
print("\n命題 9（窓の中の次元。予想 (b)）")


def w_first_returns(k, q, steps=400):
    """台本とは別の計算。w の座標で、有理数で、強制された道を辿る。

    筒の像は x では [0, b]、w では [v, 3]（v = 3 − (1 − δ)b）。満ちた状態は v = c。
    v ≤ 2 + δ なら R（u = 2）へ進み、v > 4 − 2δ なら L（u = 3）へ進み、その間なら止まる。
    v ≤ 4 − 2δ の段で、L を取れば満ちた状態へ戻る。その段の番号 + 1 が A_δ に入る。
    """
    d = Fr(k, q)
    v, out = 2 + (1 - d) / d, []
    for j in range(steps):
        if v <= 4 - 2 * d:
            out.append(j + 1)
        if v <= 2 + d:
            v = (v - 2 * (1 - d)) / d
        elif v > 4 - 2 * d:
            v = (v - 3 * (1 - d)) / d
        else:
            break
    stopped = j + 1 if v > 2 + d and v <= 4 - 2 * d else None
    return out, stopped


def dim_by_z(A, d):
    """G(z) = Σ_{n ∈ A} zⁿ = 1 を z の側で二分法で解き、dim = log z / log δ。"""
    lo, hi = 0.0, 1.0
    for _ in range(100):
        z = (lo + hi) / 2
        lo, hi = (lo, z) if sum(z ** n for n in A) > 1 else (z, hi)
    return math.log((lo + hi) / 2) / math.log(d)


p9_rows = [cells for cells in (line.strip("|").split("|") for line in page.splitlines()
                               if re.match(r"^\| 0\.\d+ \| \{", line))]
p9_rows = [[c.strip() for c in r] for r in p9_rows]
check("頁に命題 9 の表がある", len(p9_rows) == 7, "%d 行" % len(p9_rows))
tab_ok, ident_ok = True, True
for cells in p9_rows:
    dd = Fr(cells[0])
    A, stopped = w_first_returns(dd.numerator, dd.denominator)
    shown = "{" + ", ".join("%d" % n for n in A[:4]) + (", …" if len(A) > 4 else "") + "}"
    tab_ok = tab_ok and shown == cells[1] and "%.6f" % dim_by_z(A, float(dd)) == cells[2]
    # 生成関数の恒等式：N_n = q_n + Σ_{a ∈ A} N_{n−a}。走査の台本の整数の数（深さ 22）と比べる。
    dep = int(vals.get("depth", "0"))
    N = [0] * (dep + 1)
    for n in range(dep + 1):
        N[n] = (1 if stopped is None or n <= stopped - 1 else 0) + sum(N[n - a] for a in A if a <= n)
    ident_ok = ident_ok and N[1:] == scan_mod.refine_exact(dd.numerator, dd.denominator, dep)[0]
check("表の A_δ と次元が、w の座標で作り直した道と z の側の根から出る値と同じ（7 行）", tab_ok)
check("初回帰の分け方から数えた筒の数が、走査の台本の整数の数と、深さ %s まで全部一致する（7 つの δ）"
      % vals.get("depth"), ident_ok)
g_dims, g_low = [], []
for kk in range(6181, 6667):
    A, _ = w_first_returns(kk, 10000)
    g_dims.append(dim_by_z(A, kk / 10000))
    g_low.append(lower_closed(kk / 10000)[1])
check("δ = 0.6181〜0.6666（0.0001 刻み、486 通り）で、次元が真に増え、1 未満で、命題 6 の下界を下回らない",
      len(g_dims) == 486 and all(a < b for a, b in zip(g_dims, g_dims[1:])) and all(0 < x < 1 for x in g_dims)
      and all(x >= lo - 1e-9 for x, lo in zip(g_dims, g_low)), "%.4f〜%.6f" % (g_dims[0], g_dims[-1]))
check("台本が名乗る格子の数が、ここで数え直した数と同じ",
      vals.get("dim_grid_rises") == "the dimension rises at %d of the %d steps" % (
          sum(1 for a, b in zip(g_dims, g_dims[1:]) if b > a), len(g_dims) - 1)
      and vals.get("dim_grid_ends") == "It runs from %.4f to %.6f" % (g_dims[0], g_dims[-1]))

# 2026-11-18 の文献の照合。DOI と arXiv の番号は Crossref・DataCite・arXiv の API が返したものだけで、照合の報告にある番号に限る。
# 各行は「Read in part:」「Abstract read.」「Recalled, not read.」のどれかを持つ。記憶から文献を足せば、番号が表に無くて落ちる。
# Allaart と Kong は arXiv 2109.10012v2 の Remark 1.10 で、出版された「同時には連続でない」を取り下げた。頁は「壊れる」と書かない。
CHECKED_DOIS = {"10.1017/etds.2022.24", "10.48550/arxiv.2109.10012", "10.1142/s0218348x14500169",
                "10.1016/j.aim.2016.03.047", "10.48550/arxiv.2604.23737", "10.1112/blms.70344",
                "10.48550/arxiv.2509.04227", "10.1006/game.2001.0901", "10.1007/bf02020954",
                "10.1007/bf02020331", "10.1007/s10955-024-03265-0", "10.48550/arxiv.2311.02465"}
lit = page.split("\n## The literature check of 2026-11-18\n")[-1].split("\n## ")[0] \
    if "\n## The literature check of 2026-11-18\n" in page else ""
lit_f = re.sub(r"\s+", " ", lit)
items = re.findall(r"^- (.*?)(?=\n- |\Z)", lit.split("Sources of the check:")[-1], re.S | re.M)
dois = re.findall(r"doi:([0-9A-Za-z./_()-]*[0-9A-Za-z])", lit)
marks = [bool(re.search(r"(Read in part: |Abstract read\.|Recalled, not read\.)", re.sub(r"\s+", " ", it))) for it in items]
check("文献の照合の節があり、読んだところを印で分け、出典の %d 行がどれも印を持つ" % len(items),
      "Each source is marked \"read in part\", \"abstract read\" or \"recalled, not read\"." in lit_f
      and len(items) == 9 and all(marks))
check("節の DOI が、照合の報告にある番号だけで、どれも一度ずつ", sorted(dois) == sorted(CHECKED_DOIS),
      ", ".join(sorted(set(dois) ^ CHECKED_DOIS)))
check("定理の番号を報告のとおりに引き、Rényi と Parry は思い出したもの、同時の連続は「壊れる」と書かない",
      all(x in lit_f for x in ("Lu, Steiner and Zou (2026), Theorem 1.2 with Lemma 2.7",
                               "Kuang, Li and Xiao (2026), Theorem 4.3 with `t = 0^∞`",
                               "The bound below 1 is Lu, Steiner and Zou (2026), Proposition 2.5.",
                               "Theorem 1.4", "Lemma 3.16", "Corollary 1.5", "Remark 1.10 of arXiv 2109.10012v2",
                               "(Rényi 1957; Parry 1960), recalled, not read."))
      and all(re.search(n + r".{0,200}?Recalled, not read\.", lit, re.S) for n in (r"Parry, W\. \(1960\)", r"Rényi, A\. \(1957\)"))
      and "fails in general" not in page and "known to fail" not in page.replace("is not known to fail", ""))
flat_A = [w_first_returns(kk, 10000)[0] for kk in range(6400, 6451)]
flat_d = [dim_by_z(A, kk / 10000) for A, kk in zip(flat_A, range(6400, 6451))]
_lo, _hi = 0.0, 1.0                     # z + z⁴ = 1 を z の側で解く。h = log(1/z)
for _ in range(100):
    _z = (_lo + _hi) / 2
    _lo, _hi = (_lo, _z) if _z + _z ** 4 > 1 else (_z, _hi)
flat_h = math.log(2 / (_lo + _hi))
check("δ = 0.6400〜0.6450（51 通り）で A_δ = {1, 4} が変わらず、エントロピーは一定で、次元は真に増える（台本の値と同じ）",
      all(A == [1, 4] for A in flat_A) and all(a < b for a, b in zip(flat_d, flat_d[1:]))
      and vals.get("flat") == "at every δ = 0.6400, 0.6401, …, 0.6450: `A_δ = {1, 4}`,"
      and vals.get("flat_h") == "the entropy is %.6f throughout, and the dimension rises from %.6f to %.6f" % (
          flat_h, flat_d[0], flat_d[-1]), "%.6f・%.6f〜%.6f" % (flat_h, flat_d[0], flat_d[-1]))

# 命題 9 の節が引く確かめの走査の推定は、確かめの結果の節が書く最大の推定と同じ数（check_docs.py が出力の表から数え直す）。
_est = re.search(r"At δ = 0\.6666 the confirmatory scan estimated (\d\.\d+)\.", flat_p8)
_max = re.search(r"The dimension estimate is below 1 at \d+ of \d+ values\. The largest is (\d\.\d+), at δ = 0\.6666\.", flat_p8)
check("命題 9 の節が引く δ = 0.6666 の推定が、確かめの走査の節の最大の推定と同じ",
      _est is not None and _max is not None and _est.group(1) == _max.group(1),
      "%s / %s" % (_est.group(1) if _est else "無し", _max.group(1) if _max else "無し"))

print("\n" + "-" * 58)
if failures:
    print("%d 件が通り、%d 件が通りませんでした。" % (passed, len(failures)))
    for f in failures:
        print("  - " + f)
    sys.exit(1)
print("%d 件すべて通りました。" % passed)
