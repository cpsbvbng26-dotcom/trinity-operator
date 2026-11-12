#!/usr/bin/env python3
"""README の札・図・例、開いている問題の頁、版と DOI、依存、様式を当たる。

    python3 verification/check_docs.py

台本を走らせるのは examples/one_minute.py と、隣の trinity-infinity の
independent_check.py と claims_audit.py だけで、そこで NumPy を使う。
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
 10. games/LICENSE が lessons/LICENSE と同じ CC BY 4.0 で、README とノートがそれを指すか。
 11. games/SCOPE.md と SCOPE.ja.md（予想を続ける範囲）が、決めごと 15 の一文を引き、
     開いている部分のラベルと同じ表を持つか。
 12. SECURITY.md と、誤りの知らせの様式（erratum のラベル）。
 13. ワークフローが一番上で権限を絞り、外部のアクションをコミットの値で固定しているか。
 14. 保存版の要旨の日本語と英語が、同じ数の文で並ぶか。キーワードが引用情報と同じか。
 15. README の言語モデルの開示の表（道具・使ったところ・確かめた人）。
 16. 散文が名乗る件数。CITATION.cff が名乗る trinity-infinity の件数は、隣の
     trinity-infinity の検査を回して数える（場所は環境変数 TRINITY_INFINITY でも渡せる）。
 17. 黄金比の窓の予想の事前登録の下書き（games/PREREGISTRATION.md）。確かめの格子と深さが
     games/scan.py の定数と同じか、探索の格子と重ならないか、登録前に結果を置いていないか。
     README と続ける範囲の頁が書く、広げた走査の数も、ここで台本と突き合わせる。
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

# 広げた走査（games/scan.py）。範囲は台本の定数から読む。頁には台本の範囲だけを書く。
SCAN_PY = read(os.path.join("games", "scan.py"))
m_scan = re.search(r"^SCAN = tuple\(\(k, (\d+)\) for k in range\((\d+), (\d+)\)\)$", SCAN_PY, re.M)
m_sdepth = re.search(r"^SCAN_DEPTH = (\d+)$", SCAN_PY, re.M)
m_last = re.search(r"^LAST = (\d+) ", SCAN_PY, re.M)
m_conf = re.search(r"^CONFIRM = tuple\(\(2 \* k \+ 1, (\d+)\) for k in range\((\d+), (\d+)\)\) \+ tuple\(\n"
                   r"\s+\(k, (\d+)\) for k in \(([\d, ]+)\)\)$", SCAN_PY, re.M)
m_cdepth = re.search(r"^CONFIRM_DEPTH = (\d+)$", SCAN_PY, re.M)
check("走査の台本から SCAN・SCAN_DEPTH・LAST・CONFIRM・CONFIRM_DEPTH を読める",
      bool(m_scan and m_sdepth and m_last and m_conf and m_cdepth))
from fractions import Fraction  # noqa: E402
if m_scan and m_sdepth and m_last and m_conf and m_cdepth:
    sq, k0, k1 = (int(x) for x in m_scan.groups())
    scan_grid = [Fraction(k, sq) for k in range(k0, k1)]
    scan_depth = int(m_sdepth.group(1))
    last = int(m_last.group(1))
    cq, c0, c1, pq = (int(x) for x in m_conf.groups()[:4])
    probes = [Fraction(int(x), pq) for x in m_conf.group(5).split(",")]
    mids = [Fraction(2 * k + 1, cq) for k in range(c0, c1)]
    conf_grid = mids + probes
    conf_depth = int(m_cdepth.group(1))
    dec = len(str(sq)) - 1
    fmt = lambda x, n=dec: "%.*f" % (n, x)  # noqa: E731
    check("頁の広げた走査の範囲が台本と同じ（δ = %s〜%s、%d 通り、深さ %d）"
          % (fmt(scan_grid[0]), fmt(scan_grid[-1]), len(scan_grid), scan_depth),
          "| wider scan of the window, 2026-11-12 | δ = %s, %s, …, %s, %d values; depth %d periods; exact counts |"
          % (fmt(scan_grid[0]), fmt(scan_grid[1]), fmt(scan_grid[-1]), len(scan_grid), scan_depth) in OPEN)
    check("頁が、記録にない深さとして走査の深さを挙げている",
          "no depth beyond %d periods" % scan_depth in OPEN)
    check("頁が、広げた走査を最初の反例の探索と書き、その数を台本と同じに書いている",
          "The wider scan is the first recorded search for counterexamples. At each of its %d values"
          % len(scan_grid) in OPEN
          and "The wider scan shows the same on all %d rows" % len(scan_grid) in OPEN
          and "nor can the %d values of the wider scan" % len(scan_grid) in flat(OPEN))
    check("頁が、確かめの格子はまだ回していないと書いている",
          "That grid has not been run." in OPEN and "That grid has not been run." in NOTE)
check("頁が、学部一年次の系列の続きだと書いている",
      "first-year undergraduate self-study" in OPEN and "It does not start a new theme." in OPEN)
check("頁が Claude を著者にしていない", "Claude is not an\nauthor." in OPEN)

made = re.findall(r'gh label create "([^"]+)" --color [0-9a-f]{6} --description "([^"]+)" --force',
                  LABELS)
listed = re.findall(r"^\| `([^`]+)` \| ([^|]+?) \|$", OPEN, re.M)
check("ラベルの表がある", len(listed) > 0, "%d 行" % len(listed))
NOT_OPEN = ("bug", "erratum")   # 様式が付けるラベル。開いている部分ではない
check("頁のラベルが、ワークフローが作るラベル（bug と erratum を除く）と同じ",
      sorted(listed) == sorted(x for x in made if x[0] not in NOT_OPEN),
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
    dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", "site", "_sibling")]
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
pips = re.findall(r"run:\s*pip install ([^\n]+)", VERIFY)
check("CI が入れるのは NumPy だけ", pips == ["numpy"], repr(pips))
manifests = [f for f in ("requirements.txt", "pyproject.toml", "setup.py", "setup.cfg", "Pipfile",
                         "package.json", "environment.yml") if os.path.exists(os.path.join(ROOT, f))]
check("依存を書き足す場所（requirements.txt・package.json など）を置いていない", not manifests,
      ", ".join(manifests))

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

# ------------------------------------------------------------ 10. games/ のライセンス
print("\n10. games/ のライセンス")


def raw(rel):
    path = os.path.join(ROOT, rel)
    return io.open(path, "rb").read() if os.path.exists(path) else b""


check("games/LICENSE が lessons/LICENSE と一字一句同じ（CC BY 4.0）",
      raw("games/LICENSE") != b"" and raw("games/LICENSE") == raw("lessons/LICENSE")
      and raw("games/LICENSE").startswith(b"Creative Commons Attribution 4.0 International"))
check("README のライセンスの表が games/LICENSE を指している",
      "| [`games/`](games/) の文章 | CC BY 4.0 | [`games/LICENSE`](games/LICENSE)。" in README)
check("ノートの末尾が LICENSE を指している",
      "This note is licensed under CC BY 4.0 ([LICENSE](LICENSE))." in NOTE)

# ------------------------------------------------------------ 11. 続ける範囲
print("\n11. 黄金比の窓の予想を続ける範囲（決めごと 15）")
SCOPE_EN = read(os.path.join("games", "SCOPE.md"))
SCOPE_JA = read(os.path.join("games", "SCOPE.ja.md"))
CLAUDE = read("CLAUDE.md")
rule15 = re.search(r"^\s*(学部二年次以降に進めるのは[^\n]*。)$", CLAUDE, re.M)
check("CLAUDE.md の決めごと 15 から、続きを限る一文を読める", rule15 is not None)
for name, text in (("SCOPE.md", SCOPE_EN), ("SCOPE.ja.md", SCOPE_JA)):
    check("%s が決めごと 15 の一文を一字一句引いている" % name,
          rule15 is not None and ("\n> %s\n" % rule15.group(1)) in text)
    rows = re.findall(r"^\| `([^`]+)` \| ([^|]+?) \| [^|]+ \|$", text, re.M)
    check("%s の続きの表が、開いている部分のラベルと同じ並び" % name,
          rows == listed, "表 %s / 頁 %s" % ([r[0] for r in rows], [r[0] for r in listed]))
    check("%s が OPEN-PROBLEM.md とノートを指している" % name,
          "](OPEN-PROBLEM.md)" in text and "](README.md)" in text)
    check("%s が、ノートを書き始めた日をノートと同じに書いている" % name,
          "2026-10-04" in text and "first\nwritten on 2026-10-04" in NOTE)
    check("%s が、展望の段 2 の黄金比の例を新しい主題の側に置いている" % name,
          ("stage 2" in text or "段 2" in text) and "γ = 1/φ" in text)
    check("%s が LICENSE を指している" % name, "[LICENSE](LICENSE)" in text)
q_en = re.findall(r"^\d\. ", SCOPE_EN.split("## A test for unclear cases")[-1].split("\n## ")[0], re.M)
q_ja = re.findall(r"^\d\. ", SCOPE_JA.split("## 迷ったときの見分け方")[-1].split("\n## ")[0], re.M)
check("見分け方の問いが、日本語の「二つ」と英語の「Two」のとおり二つずつ",
      len(q_en) == 2 and len(q_ja) == 2 and "問いは二つです。" in SCOPE_JA
      and "Two questions decide it." in SCOPE_EN, "%d・%d" % (len(q_ja), len(q_en)))
check("SCOPE.ja.md が言語モデルを著作者にしていない", "言語モデルは著作者ではありません。" in SCOPE_JA)
check("SCOPE.md が Claude を著者にしていない", "Claude is not an\nauthor." in SCOPE_EN)
check("README が日本語と英語の両方の範囲の頁を指している",
      "(games/SCOPE.ja.md)" in README and "(games/SCOPE.md)" in README)

# ------------------------------------------------------------ 12. 安全の窓口と、誤りの知らせ
print("\n12. 安全の窓口（SECURITY.md）と、誤りの知らせの様式")
SECURITY = read("SECURITY.md") if os.path.exists(os.path.join(ROOT, "SECURITY.md")) else ""
check("SECURITY.md があり、日本語と英語の欄を持つ",
      SECURITY.startswith("# 安全の問題の知らせ方 / Reporting a security issue\n")
      and "\n## 日本語\n" in SECURITY and "\n## English\n" in SECURITY)
check("SECURITY.md が、非公開の報告の入口と答えの目安を書いている",
      "Report a vulnerability" in SECURITY and "7 日以内" in SECURITY and "within 7 days" in SECURITY)
ERR_PATH = os.path.join(".github", "ISSUE_TEMPLATE", "error-report.yml")
ERR = read(ERR_PATH) if os.path.exists(os.path.join(ROOT, ERR_PATH)) else ""
check("誤りの知らせの様式があり、erratum のラベルを付ける", "labels: [erratum]" in ERR)
check("erratum のラベルをワークフローが作る", any(n == "erratum" for n, _ in made))
for field in ("where", "printed", "correct", "basis", "found_by"):
    mf = re.search(r"id: %s\n(.*?)(?=\n  - type:|\Z)" % field, ERR, re.S)
    check("誤りの知らせの欄 %s があって必須" % field, mf is not None and "required: true" in mf.group(1))
check("誤りの知らせの様式が、安全の問題を SECURITY.md へ回している", "SECURITY.md" in ERR)

# ------------------------------------------------------------ 13. ワークフロー
print("\n13. ワークフローの権限と、外部のアクションの固定")
WF_DIR = os.path.join(ROOT, ".github", "workflows")
for f in sorted(os.listdir(WF_DIR)):
    if not f.endswith((".yml", ".yaml")):
        continue
    wf = read(os.path.join(".github", "workflows", f))
    top = re.search(r"^permissions:\n((?:  \S[^\n]*\n)+)", wf, re.M)
    perms = dict(re.findall(r"^  ([a-z-]+):\s*(\S+)", top.group(1), re.M)) if top else {}
    check("%s が一番上で permissions を決めている" % f, bool(perms), repr(perms))
    want = {"labels.yml": {"issues": "write"}}.get(f, {"contents": "read"})
    check("%s の権限が %s だけ" % (f, want), perms == want, repr(perms))
    check("%s は仕事の単位で権限を広げていない" % f,
          not re.search(r"^    permissions:", wf, re.M) and "write-all" not in wf)
    uses = re.findall(r"uses:\s*(\S+)([^\n]*)", wf)
    bad = [u + c for u, c in uses
           if not u.startswith("./")
           and not (re.match(r"^[\w.-]+/[\w.-]+@[0-9a-f]{40}$", u) and re.match(r"^ # v\d", c))]
    check("%s の外部のアクションが、すべてコミットの値と版の注釈で固定されている（%d 個）" % (f, len(uses)),
          not bad, "; ".join(bad))

# ------------------------------------------------------------ 14. 要旨と語
print("\n14. 保存版の要旨（日本語と英語）と、キーワード")


def paras(html):
    return re.findall(r"<p>(.*?)</p>", html, re.S)


def is_ja(t):
    return re.search(r"[぀-ヿ]", t) is not None


def math_tokens(t):
    return sorted(set(x for x in re.findall(r"[^\s　-ヿ一-鿿（）、。]+", t)
                      if re.search(r"[‖ρκγ←≤]", x)))


desc = ZENODO.get("description", "")
ja_p = [p for p in paras(desc) if is_ja(p)]
en_p = [p for p in paras(desc) if not is_ja(p)]
check("要旨の段落が日本語と英語で同じ数", len(ja_p) == len(en_p) and ja_p, "%d・%d" % (len(ja_p), len(en_p)))
for i, (j, e) in enumerate(zip(ja_p, en_p), 1):
    nj = len([x for x in j.split("。") if x.strip()])
    ne = len([x for x in re.split(r"(?<=[.!?])\s+", e.strip()) if x.strip()])
    check("要旨の第 %d 段落の文の数が日本語と英語で同じ" % i, nj == ne, "%d・%d" % (nj, ne))
    miss = [t for t in math_tokens(j) if t not in e]
    check("要旨の第 %d 段落の式が英語の側にもある" % i, not miss, " ".join(miss))
kw_block = re.search(r"^keywords:\n((?:  - [^\n]+\n)+)", CFF, re.M)
cff_kw = re.findall(r"^  - (.+)$", kw_block.group(1), re.M) if kw_block else []
check("CITATION.cff と .zenodo.json のキーワードが同じ並び",
      cff_kw and cff_kw == ZENODO.get("keywords"), "%d 語" % len(cff_kw))

# ------------------------------------------------------------ 15. 言語モデルの開示の表
print("\n15. 言語モデルの開示の表")
head = "| 道具 | 使ったところ | 確かめた人 |\n| --- | --- | --- |\n"
i = README.find(head)
disc = re.findall(r"^\| ([^|]+?) \| ([^|]+?) \| ([^|]+?) \|$", README[i + len(head):].split("\n\n")[0], re.M) \
    if i >= 0 else []
check("README の「言語モデルの利用」に、道具・使ったところ・確かめた人の表がある",
      i > README.find("## 言語モデルの利用") > 0 and len(disc) > 0, "%d 行" % len(disc))
check("表の道具が、どれも作り手を括弧で添えている",
      all(re.search(r"（[A-Za-z]+）$", r[0]) for r in disc), ", ".join(r[0] for r in disc))
check("表の行が、教材とノートの確認の状態を、それぞれの頁と同じに書いている",
      any("lessons/" in r[1] and "まだ済んでいない" in r[2] for r in disc)
      and "著者の確認はまだ済んでいません。" in README
      and any("games/" in r[1] and "記録に無い" in r[2] for r in disc)
      and "The repository records no review" in NOTE)
check("README と保存版の記録が言語モデルを著者にしていない",
      "言語モデルは著作者ではありません。" in README and "Claude is not an author." in ZENODO.get("notes", ""))

# ------------------------------------------------------------ 16. 散文の件数
print("\n16. 散文が名乗る件数（決めごと 5）")
INFINITY = os.environ.get("TRINITY_INFINITY") or os.path.join(os.path.dirname(ROOT), "trinity-infinity")
have_inf = os.path.exists(os.path.join(INFINITY, "verification", "claims_audit.py"))
check("trinity-infinity の写しが隣にある（環境変数 TRINITY_INFINITY でも渡せる）", have_inf, INFINITY)
if have_inf:
    def sibling(script, pattern):
        out = subprocess.run([sys.executable, os.path.join("verification", script)], cwd=INFINITY,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.decode("utf-8", "replace")
        mm = re.search(pattern, out)
        return int(mm.group(1)) if mm else None
    # 正規表現は、横断の検査（cpsbvbng26-dotcom の ecosystem.json）と同じもの。
    printed = sibling("claims_audit.py", r"(\d+) 項目 —— MATCH")
    theorems = sibling("independent_check.py", r"(\d+) checks, \d+ passed")
    said = re.search(r"紙面の数値を計算し直す (\d+) 項目、定理を独立に実装し直す (\d+) 項目。", CFF)
    check("CITATION.cff が名乗る trinity-infinity の件数が、実際に回した件数と合う",
          said is not None and printed and theorems
          and (int(said.group(1)), int(said.group(2))) == (printed, theorems),
          "名乗り %s / 実際 %s・%s" % (said.groups() if said else None, printed, theorems))
ci_name = re.search(r"name: 作用素 (\d+) 項目 / 証書 (\d+) 項目 / 展望 (\d+) 項目 / 引用情報 (\d+) 項目", VERIFY)
claude_n = [re.search(r"%s\s+# %s (\d+) 項目" % (re.escape(cmd), label), CLAUDE)
            for cmd, label in (("python3 check.py", "作用素"),
                               ("python3 verification/check_certificate.py", "証書"),
                               ("python3 verification/check_roadmap.py", "展望"),
                               ("python3 verification/check_citation.py", "引用情報"))]
check("CLAUDE.md の一覧が名乗る四つの件数が、CI の仕事の名前と同じ",
      ci_name is not None and all(claude_n)
      and [m.group(1) for m in claude_n] == list(ci_name.groups()),
      "CLAUDE.md %s / CI %s" % ([m.group(1) if m else None for m in claude_n],
                                list(ci_name.groups()) if ci_name else None))
CHECK_PY = read("check.py")
loop = re.search(r"for _ in range\((\d+)\):\n(?:.*\n){0,12}?check\(\"置換 (\d+) 通りで ρ が閉じた式と一致する\"",
                 CHECK_PY)
said = re.search(r"置換 (\d+) 通りで NumPy の固有値", README)
check("README の「置換 N 通り」が check.py の回す数と合う",
      loop is not None and said is not None and loop.group(1) == loop.group(2) == said.group(1),
      "README %s / check.py %s" % (said.group(1) if said else None, loop.groups() if loop else None))
trials = re.search(r"^TRIALS = (\d+)$", read(os.path.join("verification", "check_standard.py")), re.M)
said = re.search(r"逆行列で求めた V と (\d+) 件で突き合わせています。", README)
check("README の「V と N 件」が check_standard.py の TRIALS と合う",
      trials is not None and said is not None and trials.group(1) == said.group(1),
      "README %s / TRIALS %s" % (said.group(1) if said else None, trials.group(1) if trials else None))
S6 = read(os.path.join("roadmap", "stage6_general_influence.py"))
t6 = re.search(r"trials = (\d+)\n\s+pointwise = \[\]\n\s+for n in \(([^)]*)\):", S6)
total = int(t6.group(1)) * len([x for x in t6.group(2).split(",") if x.strip()]) if t6 else None
said = re.findall(r"(\d+) 件(?:に当てました|で 0 件)", ROADMAP)
check("展望の README の「均衡 N 件」が、段 6 の台本の回す数（標本 × n の数）と合う",
      total is not None and len(said) == 2 and all(int(x) == total for x in said),
      "名乗り %s / 台本 %s" % (said, total))

# ------------------------------------------------------------ 17. 事前登録の下書き
print("\n17. 黄金比の窓の予想の、事前登録の下書き（games/PREREGISTRATION.md）")
PRE_PATH = os.path.join("games", "PREREGISTRATION.md")
PRE = read(PRE_PATH) if os.path.exists(os.path.join(ROOT, PRE_PATH)) else ""
SCOPE_EN_F, SCOPE_JA_F, NOTE_F = flat(SCOPE_EN), flat(SCOPE_JA), flat(NOTE)
PRE_F = flat(PRE)
draft = "Status: draft, not registered." in PRE
check("下書きがあり、まだ登録していないと冒頭で名乗っている",
      PRE.startswith("# Preregistration draft:") and draft)
check("下書きが、利用者から受け取っていない登録の DOI を書いていない",
      "10.17605" not in PRE and "osf.io/" not in PRE.lower()
      and "No registration DOI exists yet." in PRE)
check("登録前は、確かめの格子の結果を置いていない（games/scan-confirmatory.txt が無い）",
      not (draft and os.path.exists(os.path.join(ROOT, "games", "scan-confirmatory.txt"))))
if m_scan and m_sdepth and m_last and m_conf and m_cdepth:
    check("確かめの格子が探索の格子と一つも重ならない",
          not set(conf_grid) & set(scan_grid), "%d 通りと %d 通り" % (len(conf_grid), len(scan_grid)))
    golden = Fraction(6180339887, 10 ** 10)          # 1/φ = 0.6180339887…（下から）
    check("確かめの格子が、どれも窓（1/φ と 2/3 の間）の中にある",
          all(golden + Fraction(1, 10 ** 10) < x < Fraction(2, 3) for x in conf_grid))
    check("下書きが、確かめの格子の数と深さを台本と同じに書いている（%d 通り、深さ %d）"
          % (len(conf_grid), conf_depth),
          "The confirmatory grid has %d values of δ:" % len(conf_grid) in PRE
          and "the %d midpoints of the exploratory grid, δ = (2k + 1)/%d for k = %d, …, %d, that is %s, %s, …, %s;"
          % (len(mids), cq, c0, c1 - 1, fmt(mids[0], 4), fmt(mids[1], 4), fmt(mids[-1], 4)) in PRE_F
          and "probes near the ends of the window, δ = %s and %s." % (
              ", ".join(fmt(x, 4) for x in probes[:-1]), fmt(probes[-1], 4)) in PRE_F
          and "and the depth as `CONFIRM_DEPTH`, which is %d." % conf_depth in PRE_F
          and "at depth %d. The growth is the number of surviving intervals per period over the last %d periods."
          % (conf_depth, last) in PRE_F
          and "`log N/(%d log(1/δ))`" % conf_depth in PRE)
    check("探りの数が台本と同じ（six）", len(probes) == 6 and "six probes near the ends" in PRE)
    check("下書きが、探索の格子を台本と同じに書いている",
          "It used %d values of δ, from %s to %s at step 0.001, and a depth of %d periods."
          % (len(scan_grid), fmt(scan_grid[0]), fmt(scan_grid[-1]), scan_depth) in PRE_F)
    check("README が、広げた走査の範囲と深さを台本と同じに書いている",
          "窓の中の δ を %s から %s まで 0.001 刻みの %d 通りに増やし、細分の深さを %d 段にしました"
          % (fmt(scan_grid[0]), fmt(scan_grid[-1]), len(scan_grid), scan_depth) in README)
    check("続ける範囲の頁が、最初の走査の数を台本と同じに書いている",
          "δ は %d 通り、深さは %d 段で" % (len(scan_grid), scan_depth) in SCOPE_JA
          and "with %d values of δ and a depth of %d periods" % (len(scan_grid), scan_depth) in SCOPE_EN_F)
check("下書きに、三つの仮説と、予想に反するとみなす結果の表がある",
      all("- **H%d**" % i in PRE for i in (1, 2, 3))
      and len(re.findall(r"^\| [^|]+ \| [^|]+ \(H[123]\) \|$", PRE, re.M)) == 4)
check("下書きが、一致しても証明とは呼ばないと書いている",
      "It is not reported as a proof." in PRE and "Agreement on the confirmatory grid will be" in PRE)
check("下書きが、どの結果でもノートと開いている問題の頁に載せると書いている",
      "whatever they show" in PRE_F and "(README.md)" in PRE and "(OPEN-PROBLEM.md)" in PRE)
check("下書きが LICENSE を指し、Claude を著者にしていない",
      "([LICENSE](LICENSE))" in PRE and "Claude is not an\nauthor." in PRE)
check("README・ノート・開いている問題の頁が、下書きを指している",
      "(games/PREREGISTRATION.md)" in README and "(PREREGISTRATION.md)" in NOTE
      and "(PREREGISTRATION.md)" in OPEN)
check("README と下書きが、登録を 2026-11-12 に止め、まだ登録していないと書き、著者への手順を置いていない（下書きの冒頭と同じ状態）",
      draft and "OSF への登録は、2026-11-12 に止めました。登録していないので、その格子はまだ回していません。" in README
      and "The registration on OSF was stopped on 2026-11-12, and\nnothing has been filed." in PRE
      and "## Filing" not in PRE)

print("\n" + "-" * 58)
if failures:
    print("%d 件が通り、%d 件が通りませんでした。" % (passed, len(failures)))
    for f in failures:
        print("  - " + f)
    sys.exit(1)
print("%d 件すべて通りました。" % passed)
