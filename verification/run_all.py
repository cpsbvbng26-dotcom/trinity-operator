#!/usr/bin/env python3
"""CI が回す検証を、手元で一度に全部回す。

    python3 verification/run_all.py

並びは .github/workflows/verify.yml から読む。ここに一覧を書き写さない。
書き写すと、CI に足した検査がここから漏れても気づけない。

読むのは `run: python3 …` の行だけである。pip の行は回さない
（依存は NumPy だけである。入れるのは手元の判断に任せる）。

一つでも落ちたら終了コードは 1。落ちても最後まで回し、最後に一覧で出す。
"""

import io
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW = os.path.join(ROOT, ".github", "workflows", "verify.yml")

steps = []
with io.open(WORKFLOW, encoding="utf-8") as fh:
    for line in fh:
        m = re.match(r"^\s*run:\s*python3\s+(\S+)\s*$", line)
        if m:
            steps.append(m.group(1))

if not steps:
    print("verify.yml から検査を一つも読めませんでした。")
    sys.exit(1)

print("verify.yml から %d 本を読みました。" % len(steps))
results = []
for script in steps:
    t0 = time.time()
    proc = subprocess.run([sys.executable, script], cwd=ROOT,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = proc.stdout.decode("utf-8", "replace").strip().split("\n")
    results.append((script, proc.returncode, time.time() - t0, out[-1] if out else ""))
    print("  %s  %-40s %5.1f s  %s" % ("通" if proc.returncode == 0 else "落",
                                       script, time.time() - t0, out[-1][:60] if out else ""))

bad = [r for r in results if r[1] != 0]
print("-" * 58)
if bad:
    print("%d 本のうち %d 本が落ちました。" % (len(results), len(bad)))
    for script, code, _, last in bad:
        print("  - %s（終了コード %d）%s" % (script, code, last))
    sys.exit(1)
print("%d 本すべて通りました。" % len(results))
