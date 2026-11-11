#!/usr/bin/env python3
"""一分で試す。三篇の作用素を二つ作り、何を渡すと何が返るかを見る。

    python3 examples/one_minute.py

渡すもの：混合率 a（blend）、基準点 p（anchor）、影響行列 Q（省略すると巡回置換）。
返るもの：スペクトル半径 ρ、作用素ノルム ‖A‖₂、収束するか、不動点、誤差の山。

出力は examples/one_minute.txt と一字一句同じになる。
verification/check_docs.py が、走らせて突き合わせている。
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from trinity import TrinityOperator  # noqa: E402

print("1. Series II の設定（Q は巡回置換）")
op = TrinityOperator(blend=[0.5, 0.7, 0.3], anchor=[1, 0, 0.5])
print(op.report())
print("  不動点 = (%.6f, %.6f, %.6f)" % tuple(op.fixed_point()))

print()
print("2. 論文の条件を満たさないのに収束する例")
counter = TrinityOperator(blend=[0.5, 0.5], anchor=[1, 0],
                          Q=np.array([[1.0, 40.0], [0.0, 1.0]]))
print(counter.report())
err = counter.error_curve([5.0, -3.0], steps=40)
print("  誤差 第 0 段 = %.3f、最大は第 %d 段で %.3f、第 40 段 = %.2e"
      % (err[0], int(err.argmax()), err.max(), err[-1]))
