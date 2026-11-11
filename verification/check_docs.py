#!/usr/bin/env python3
"""README の札・図・例、開いている問題の頁、版と DOI、依存、様式を当たる。

    python3 verification/check_docs.py

台本を走らせるのは examples/one_minute.py だけで、そこで NumPy を使う。
ほかは文書と設定を読むだけである。

見るもの。
  1. README の冒頭の札（種類と状態）と、英語の欄。
  2. CITATION.cff の type と、.zenodo.json の関連識別子。
  3. examples/one_minute.py の出力が examples/one_minute.txt と一字一句同じか。
     README の入力と出力の図の数値が、その出力にあるか。
  4. 展望の図の語が、README の展望の表と同じか。
  5. games/OPEN-PROBLEM.md が、ノートの表と文と、台本の範囲を写し違えていないか。
     ラベルの表が、ラベルを作るワークフローと同じか。
  6. 不具合の様式が、再現の手順と環境を必須にしているか。
  7. 全部の台本が、標準ライブラリと NumPy と、このリポジトリの台本しか読まないか。
  8. README の版と DOI の表が、CITATION.cff と合うか。
  9. verification/ の検査が、すべて CI に載っているか。
"""

import ast
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

passed, failures = 0, []


def check(label, cond, detail=""):
    global passed
    if cond:
        passed += 1
        print("  PASS  " + label + (("  " + detail) if detail else ""))
    else:
        failures.append(label)
        print("  FAIL  " + label + (("  " + detail) if detail else ""))


def read(rel):
    with io.open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def flat(s):
    return re.sub(r"\s+", " ", s).strip()


def mermaid(text, kind):
    """kind（flowchart LR など）で始まる mermaid の囲みの中身。"""
    for m in re.finditer(r"```mermaid\n(.*?)```", text, re.S):
        if m.group(1).startswith(kind):
            return m.group(1)
    return ""


README = read("README.md")
CFF = read("CITATION.cff")
ZENODO = json.loads(read(".zenodo.json"))
ROADMAP = read(os.path.join("roadmap", "README.md"))
NOTE = read(os.path.join("games", "README.md"))
OPEN = read(os.path.join("games", "OPEN-PROBLEM.md"))
GAMES = read(os.path.join("games", "games.py"))
LABELS = read(os.path.join(".github", "workflows", "labels.yml"))
BUG = read(os.path.join(".github", "ISSUE_TEMPLATE", "bug_report.yml"))
VERIFY = read(os.path.join(".github", "workflows", "verify.yml"))

# 目録（cpsbvbng26-dotcom）が決めた札。ここを変えるときは目録と一緒に変える。
TYPE_JA, STATUS_JA = "ソフトウェア", "改訂中"
TYPE_EN, STATUS_EN = "Software", "In revision"
CFF_TYPE = "software"

# ------------------------------------------------------------ 1. 札
print("\n1. README の札と英語の欄")
lines = README.split("\n")
check("見出しの直下（空行を一つ挟んで）に札がある",
      len(lines) > 2 and lines[0].startswith("# ") and lines[1] == ""
      and lines[2] == "種類：%s　状態：%s" % (TYPE_JA, STATUS_JA),
      repr(lines[2]) if len(lines) > 2 else "")
check("英語の欄にも同じ札がある", "Type: %s · Status: %s" % (TYPE_EN, STATUS_EN) in README)
check("英語の欄が、注釈と出力が日本語であることを断っている",
      "Code comments, docstrings, the\nprinted messages of the scripts and this README are in Japanese"
      in README)

# ------------------------------------------------------------ 2. 引用情報
print("\n2. CITATION.cff と .zenodo.json")
m = re.search(r"^type:\s*(\S+)\s*$", CFF, re.M)
check("CITATION.cff の type が %s" % CFF_TYPE, m is not None and m.group(1) == CFF_TYPE,
      m.group(1) if m else "type が無い")
i = README.find("## 論文が言っていること")
papers = sorted(set(re.findall(r"10\.5281/zenodo\.\d+", README[i:README.find("\n## ", i + 3)])))
rel = ZENODO.get("related_identifiers", [])
check("README の論文の表から、論文の DOI が三つ読める", len(papers) == 3, ", ".join(papers))
for doi in papers:
    check("保存版が %s を isSupplementTo で指している" % doi,
          any(r.get("identifier") == doi and r.get("relation") == "isSupplementTo" for r in rel))
for r in rel:
    check("関連識別子 %s は README に書いてある番号である" % r.get("identifier"),
          r.get("identifier", "") in README)
    check("関連識別子 %s の関係は isSupplementTo か isDerivedFrom" % r.get("identifier"),
          r.get("relation") in ("isSupplementTo", "isDerivedFrom"), r.get("relation", ""))

# ------------------------------------------------------------ 3. 例と、入力と出力の図
print("\n3. 一分で試す例と、入力と出力の図")
out = subprocess.run([sys.executable, os.path.join("examples", "one_minute.py")],
                     cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
got = out.stdout.decode("utf-8")
want = read(os.path.join("examples", "one_minute.txt"))
check("examples/one_minute.py が走る", out.returncode == 0,
      out.stderr.decode("utf-8", "replace").strip()[-160:])
check("出力が examples/one_minute.txt と一字一句同じ", got == want,
      "" if got == want else "最初に違う行: %r" % next(
          (a for a, b in zip(got.split("\n") + [""], want.split("\n") + [""]) if a != b), ""))
io_fig = mermaid(README, "flowchart LR")
check("README に入力と出力の図がある", bool(io_fig))
nums = re.findall(r"\d+\.\d{6}", io_fig)
check("図に例の数値が載っている", len(nums) > 0, ", ".join(nums))
for x in nums:
    check("図の %s が例の出力にある" % x, x in want)
src = read(os.path.join("examples", "one_minute.py"))
for label, value in re.findall(r'(混合率 a（blend）|基準点 p（anchor）)<br>([^"]+)"', io_fig):
    key = "blend" if "blend" in label else "anchor"
    check("図の %s が例に渡している値と同じ" % key,
          ("%s=[%s]" % (key, value)) in src, value)

# ------------------------------------------------------------ 4. 展望の図
print("\n4. 展望の図")
table = {}
for line in README.split("\n"):
    mm = re.match(r"^\|\s*([1-6])\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", line)
    if mm:
        table[mm.group(1)] = (mm.group(2).replace("`", ""), mm.group(3).replace("`", ""))
check("README に展望の表（段 1〜6）がある", sorted(table) == list("123456"))
fig = mermaid(ROADMAP, "flowchart TD")
check("展望の README に段の図がある", bool(fig))
edges = re.findall(r'(S\d) -->\|"外す：([^"]+)"\| S(\d)\["段 (\d)　([^"]+)"\]', fig)
check("図に段 1〜6 の矢印が一本ずつある", sorted(e[2] for e in edges) == list("123456"),
      ", ".join(sorted(e[2] for e in edges)))
for frm, removed, k, k2, body in edges:
    want_removed, want_body = table.get(k, ("", ""))
    check("段 %s の矢印の語が表と同じ" % k, removed == want_removed, "表は「%s」" % want_removed)
    check("段 %s の箱の語が表と同じ" % k, k == k2 and body == want_body, "表は「%s」" % want_body)
    check("段 %s の矢印の出どころ" % k, frm == ("S2" if k == "3" else "S0"), frm)

# ------------------------------------------------------------ 5. 開いている問題
print("\n5. games/OPEN-PROBLEM.md")
for name in ("Golden-window conjecture (a).", "Golden-window conjecture (b)."):
    mo = re.search(r"\*\*" + re.escape(name) + r"\*\*(.*?)\n\n", OPEN, re.S)
    mn = re.search(r"\*\*" + re.escape(name) + r"\*\*(.*?)\n\n", NOTE, re.S)
    check("%s の文がノートと一字一句同じ" % name[:-1],
          mo is not None and mn is not None and flat(mo.group(1)) == flat(mn.group(1)))
note_rows = {flat(l) for l in NOTE.split("\n") if l.startswith("| Proposition")}
open_rows = [flat(l) for l in OPEN.split("\n") if l.startswith("| Proposition")]
check("証明済みの表がある", len(open_rows) > 0, "%d 行" % len(open_rows))
for row in open_rows:
    check("証明済みの行がノートの表と同じ：%s" % row[2:16], row in note_rows)
    check("その行の状態が proved", row.endswith("| proved |"))
check("予想を証明済みの表に入れていない", "conjecture" not in "".join(open_rows))

depth = re.search(r"^DEPTH = (\d+)", GAMES, re.M)
gap = re.search(r"^GAP = \(([^)]*)\)", GAMES, re.M)
pure = re.search(r"def pure_ok\(t, delta, depth=(\d+)\)", GAMES)
low = re.search(r"for delta in \(([^)]*)\):\n\s+ts = \[i / (\d+) for i in range\(1, (\d+)\)", GAMES)
check("台本から DEPTH・GAP・pure_ok の深さ・格子を読める",
      bool(depth and gap and pure and low))
if depth and gap and pure and low:
    gaps = ", ".join(x.strip() for x in gap.group(1).split(","))
    check("頁の細分の範囲が台本と同じ（δ = %s、深さ %s）" % (gaps, depth.group(1)),
          "δ = %s; depth %s periods" % (gaps, depth.group(1)) in OPEN)
    lows = ", ".join(x.strip() for x in low.group(1).split(","))
    step = 1 / int(low.group(2))
    check("頁の窓の下の探索が台本と同じ（δ = %s、%s 段先）" % (lows, pure.group(1)),
          "δ = %s; grid t = %g, …, 1; %s periods ahead" % (lows, step, pure.group(1)) in OPEN)
    check("頁が、記録にない深さとして台本の深さを挙げている",
          "no depth beyond %s periods" % depth.group(1) in OPEN)
check("頁が、反例の探索は記録に無いと書いている", "No search for counterexamples is recorded." in OPEN)
check("頁が、学部一年次の系列の続きだと書いている",
      "first-year undergraduate self-study" in OPEN and "It does not start a new theme." in OPEN)
check("頁が Claude を著者にしていない", "Claude is not an\nauthor." in OPEN)

made = re.findall(r'gh label create "([^"]+)" --color [0-9a-f]{6} --description "([^"]+)" --force',
                  LABELS)
listed = re.findall(r"^\| `([^`]+)` \| ([^|]+?) \|$", OPEN, re.M)
check("ラベルの表がある", len(listed) > 0, "%d 行" % len(listed))
check("頁のラベルが、ワークフローが作るラベル（bug を除く）と同じ",
      sorted(listed) == sorted(x for x in made if x[0] != "bug"),
      "頁 %s / 作る %s" % (sorted(n for n, _ in listed), sorted(n for n, _ in made)))
for name, part in listed:
    check("ラベル「%s」の開いた部分が頁の太字の見出しにある" % name,
          ("**%s.**" % part) in OPEN)

# ------------------------------------------------------------ 6. 不具合の様式
print("\n6. 不具合の様式")
check("様式が bug のラベルを付ける", 'labels: ["bug"]' in BUG)
check("bug のラベルをワークフローが作る", any(n == "bug" for n, _ in made))
for field in ("what", "steps", "expected", "commit", "environment"):
    mf = re.search(r"id: %s\n(.*?)(?=\n  - type:|\Z)" % field, BUG, re.S)
    check("欄 %s があって必須" % field, mf is not None and "required: true" in mf.group(1))
check("環境の欄が Python と NumPy の版を求めている",
      "python3 --version" in BUG and "numpy.__version__" in BUG)

# ------------------------------------------------------------ 7. 依存
print("\n7. 台本が読み込むもの")
local = set()
pyfiles = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", "site")]
    for f in filenames:
        if f.endswith(".py"):
            local.add(f[:-3])
            pyfiles.append(os.path.join(dirpath, f))
allowed = set(sys.stdlib_module_names) | {"numpy"} | local
foreign = []
numpy_users = set()
for path in sorted(pyfiles):
    rel_path = os.path.relpath(path, ROOT)
    tree = ast.parse(read(rel_path))
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names = [node.module]
        for n in names:
            top = n.split(".")[0]
            if top not in allowed:
                foreign.append("%s: %s" % (rel_path, n))
            if top == "numpy":
                numpy_users.add(rel_path)
check("読み込むのは標準ライブラリと NumPy と、このリポジトリの台本だけ",
      not foreign, "; ".join(foreign[:4]) if foreign else "%d 本" % len(pyfiles))
for rel_path in ("verification/check_text.py", "verification/check_site.py"):
    check("%s は NumPy も読まない（README がそう書いている）" % rel_path,
          rel_path not in numpy_users and ("`%s`" % rel_path) in README)
check("README が依存は NumPy の一つだけだと書いている",
      "依存は NumPy の一つだけで、ほかは Python の標準ライブラリで動きます。" in README)

# ------------------------------------------------------------ 8. 版と DOI
print("\n8. 版と DOI の表")
i = README.find("### 版と DOI")
rows = re.findall(r"^\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|\s*\[(10\.[^\]]+)\]\(https://doi\.org/\3\)\s*\|",
                  README[i:], re.M) if i >= 0 else []
check("README に版と DOI の表がある", len(rows) >= 2, "%d 行" % len(rows))
concept = re.search(r'^doi:\s*"([^"]+)"', CFF, re.M)
version = re.search(r'^version:\s*"([^"]+)"', CFF, re.M)
date = re.search(r'^date-released:\s*"([^"]+)"', CFF, re.M)
by_version = dict(re.findall(r'value:\s*"([^"]+)"\n\s*description:\s*版 (\S+)', CFF))
by_version = {v: k for k, v in by_version.items()}
for ver, day, doi in rows:
    if ver == "すべての版":
        check("すべての版の DOI が CITATION.cff の doi と同じ", concept and doi == concept.group(1), doi)
    else:
        check("版 %s の DOI が CITATION.cff と同じ" % ver, by_version.get(ver) == doi,
              "CITATION.cff は %s" % by_version.get(ver))
        if version and ver == version.group(1):
            check("版 %s の日付が CITATION.cff の date-released と同じ" % ver,
                  date and day == date.group(1), day)
check("CITATION.cff の版が表にある", version and any(r[0] == version.group(1) for r in rows))
check("CITATION.cff が挙げる版ごとの DOI が、すべて表にある",
      all(any(r[2] == d for r in rows) for d in by_version.values()))

# ------------------------------------------------------------ 9. CI
print("\n9. 検査がすべて CI に載っている")
ci = set(re.findall(r"run:\s*python3\s+(\S+)", VERIFY))
scripts = ["check.py"] + sorted("verification/" + f for f in os.listdir(os.path.join(ROOT, "verification"))
                               if f.startswith("check_") and f.endswith(".py"))
for s in scripts:
    check("%s を CI が回す" % s, s in ci)

print("\n" + "-" * 58)
if failures:
    print("%d 件が通り、%d 件が通りませんでした。" % (passed, len(failures)))
    for f in failures:
        print("  - " + f)
    sys.exit(1)
print("%d 件すべて通りました。" % passed)
