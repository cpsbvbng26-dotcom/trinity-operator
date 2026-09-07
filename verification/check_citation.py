#!/usr/bin/env python3
"""CITATION.cff が名乗っている数値を、その場で計算し直して突き合わせる。

    python3 verification/check_citation.py

引用情報は人が読む文章なので、コードを直したときに一緒に古くなる。
古くなったことに気づく手段が無いと、引用された先で誤った数値が生き続ける。

作用素そのものの検査は check.py にある。ここは書いてあることの検査である。
"""

import io
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from trinity import TrinityOperator  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
passed = 0
failures = []


def check(label, cond, detail=""):
    global passed
    if cond:
        passed += 1
        print("  PASS  " + label + ("  " + detail if detail else ""))
    else:
        failures.append(label + ("  " + detail if detail else ""))
        print("  FAIL  " + label + ("  " + detail if detail else ""))


cff = io.open(os.path.join(ROOT, "CITATION.cff"), encoding="utf-8").read()
readme = io.open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()

counter = TrinityOperator([0.5, 0.5], [1.0, 0.0],
                          Q=np.array([[1.0, 40.0], [0.0, 1.0]]))
err = counter.error_curve([5.0, -3.0], steps=40)
s2 = TrinityOperator([0.5, 0.7, 0.3], [1, 0, 0.5])

print("\nCITATION.cff が名乗っている数値")

CLAIMS = [
    ("ρ = 0.5", abs(counter.spectral_radius - 0.5) < 5e-7,
     "反例の ρ = %.6f" % counter.spectral_radius),
    ("‖A‖₂ = 20.01", abs(counter.operator_norm - 20.01) < 5e-3,
     "反例の ‖A‖₂ = %.6f" % counter.operator_norm),
    ("第 2 段", int(err.argmax()) == 2,
     "誤差が最大になるのは第 %d 段" % int(err.argmax())),
    ("11.8 倍", abs(err.max() / err[0] - 11.8) < 0.05,
     "初期値の %.1f 倍" % (err.max() / err[0])),
    ("4.36×10⁻⁹", abs(err[-1] - 4.36e-9) < 5e-11,
     "第 40 段で %.2e" % err[-1]),
    ("ρ = 0.471769", abs(s2.spectral_radius - 0.471769) < 5e-7,
     "Series II の ρ = %.6f" % s2.spectral_radius),
    ("‖A‖₂ = 0.700000", abs(s2.operator_norm - 0.7) < 5e-7,
     "Series II の ‖A‖₂ = %.6f" % s2.operator_norm),
]

for phrase, holds, detail in CLAIMS:
    check("「%s」が CITATION.cff に書いてある" % phrase, phrase in cff)
    check("その値が実際に成り立つ", holds, detail)

# 検査の件数。check.py を増減させたら、名乗っている数も直す。
print("\n検査の件数")
n = int(os.popen("cd %s && python3 check.py 2>/dev/null | tail -1" % ROOT)
        .read().split(" ")[0] or 0)
check("check.py が実際に通す件数を数えられる", n > 0, "%d 件" % n)
for name, text in (("CITATION.cff", cff), ("README.md", readme)):
    check("%s が名乗る件数が %d 件と一致する" % (name, n),
          ("%d 項目" % n) in text,
          "本文にある「NN 項目」: " + ", ".join(
              sorted(set(w for w in text.split() if w.endswith("項目")))) or "なし")

print("\n" + "-" * 58)
if failures:
    print("%d 件が通り、%d 件が通りませんでした。" % (passed, len(failures)))
    sys.exit(1)
print("%d 件すべて通りました。" % passed)
