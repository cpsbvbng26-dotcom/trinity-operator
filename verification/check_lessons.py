#!/usr/bin/env python3
"""教材の頁が書いている数値が、その回の台本が出す数値と一字一句合うかを見る。

    python3 verification/check_lessons.py

lessons/lessonN.py --values が「名前<TAB>値」を一行ずつ出す。対応する
lessons/0N-*.md に、その値がそのまま書かれていなければ落とす。

頁は「どの数値も台本から出ている」と名乗っている。名乗る以上、機械で確かめる。
台本を直して頁を直し忘れると、ここで落ちる。
"""

import glob
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LESSONS = os.path.join(ROOT, "lessons")

passed, failures = 0, []


def check(name, ok, detail=""):
    global passed
    print("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""))
    if ok:
        passed += 1
    else:
        failures.append(name)


scripts = sorted(glob.glob(os.path.join(LESSONS, "lesson[0-9]*.py")))
check("教材の台本がある", len(scripts) > 0, "%d 本" % len(scripts))

for script in scripts:
    num = re.search(r"lesson(\d+)\.py$", script).group(1)
    pages = glob.glob(os.path.join(LESSONS, "%02d-*.md" % int(num)))
    print("\n第 %s 回" % num)
    check("第 %s 回の頁が一つだけある" % num, len(pages) == 1,
          ", ".join(os.path.basename(p) for p in pages) or "無い")
    if len(pages) != 1:
        continue
    page = open(pages[0], encoding="utf-8").read()
    out = subprocess.run([sys.executable, script, "--values"], capture_output=True,
                         text=True, cwd=ROOT)
    check("第 %s 回の台本が走る" % num, out.returncode == 0, out.stderr.strip()[-200:])
    rows = [line.split("\t", 1) for line in out.stdout.splitlines() if "\t" in line]
    check("第 %s 回の台本が値を出す" % num, len(rows) > 0, "%d 個" % len(rows))
    for key, value in rows:
        check("頁に %s = %s がある" % (key, value), value in page)

print("\n" + "-" * 58)
if failures:
    print("%d 件が通り、%d 件が通りませんでした。" % (passed, len(failures)))
    for f in failures:
        print("  - " + f)
    sys.exit(1)
print("%d 件すべて通りました。" % passed)
