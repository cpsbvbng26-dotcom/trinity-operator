#!/usr/bin/env python3
"""検査を壊して確かめる。通る状態の写しを壊し、その検査がちょうど落ちることを見る。

    python3 verification/check_guards.py

壊しても落ちない検査は、何も見ていない。ここでは一通りごとに、リポジトリを
一時ディレクトリへ写し、一か所だけ書き換え、その場所を見ているはずの検査を
走らせて、終了コード 1 で落ちることを確かめる。元のファイルには触らない。

時間の掛かる二本（check_roadmap.py と check_citation.py）はここでは壊さない。
どちらも一回に一分ほど掛かる。

README は、壊す先の数を名乗っている。名乗る以上、ここで数えて突き合わせる。
"""

import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

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


# check_docs.py は隣の trinity-infinity を回して件数を数える。写しは一時ディレクトリに
# あって隣を持たないので、元の場所の隣を環境変数で渡す。
ENV = dict(os.environ)
ENV.setdefault("TRINITY_INFINITY", os.path.join(os.path.dirname(ROOT), "trinity-infinity"))


def run(where, script):
    """終了コードと、FAIL の行を返す。check_text.py は FAIL の行を出さず、見つけた件を並べる。"""
    proc = subprocess.run([sys.executable, script], cwd=where, env=ENV,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = proc.stdout.decode("utf-8", "replace")
    return proc.returncode, [l.strip() for l in out.split("\n")
                             if l.strip().startswith("FAIL") or l.strip().startswith("[")]


def case(label, rel, old, new, script):
    """rel の old を new に替えた写しで script を走らせ、落ちることを見る。"""
    tmp = tempfile.mkdtemp()
    try:
        dst = os.path.join(tmp, "repo")
        shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        path = os.path.join(dst, rel)
        with io.open(path, encoding="utf-8") as fh:
            text = fh.read()
        if text.count(old) != 1:
            check(label, False, "壊す場所が %s に一つだけあるはずが %d か所" % (rel, text.count(old)))
            return
        with io.open(path, "w", encoding="utf-8") as fh:
            fh.write(text.replace(old, new))
        code, fails = run(dst, script)
        check(label, code == 1,
              ("%s が落ちた: %s" % (script, fails[0][6:70] if fails else "終了コード 1"))
              if code == 1 else "%s は落ちなかった（終了コード %d）" % (script, code))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# 壊す先に使う語。そのまま書くと、この台本自身が check_text.py に掛かる。
MISCONVERTED = "\u6368\u9020"                      # 「捏造」の誤変換
SELF_TITLE = "\u72ec\u7acb\u7814\u7a76\u8005"   # 使わないと決めた自称

# 存在しない番号も、その場で組む。そのまま書くと、横断の検査（DOI の一覧と突き合わせる）に掛かる。
FAKE_FIGSHARE = "10.6084/m9.figshare." + "9" * 8
FAKE_ZENODO = "10.5281/zenodo." + str(24033459 - 2)

print("\n1. 壊していない状態")
for script in ("check.py", "verification/check_certificate.py", "verification/check_text.py",
               "verification/check_games.py", "verification/check_lessons.py",
               "verification/check_site.py", "verification/check_standard.py",
               "verification/check_docs.py", "verification/check_secrets.py"):
    code, fails = run(ROOT, script)
    check("そのままなら %s が通る" % script, code == 0 and not fails,
          fails[0] if fails else "")

print("\n2. 台本の式を壊す")
case("ρ の閉じた式を、幾何平均から最大値に替える", "trinity.py",
     "return float(max(np.prod(np.abs(self.a[c])) ** (1.0 / len(c)) for c in cs))",
     "return float(max(np.max(np.abs(self.a[c])) for c in cs))", "check.py")
case("証書の κ から √ を外す", "certificate.py",
     "self.kappa = float(gamma * np.sqrt(1.0 - 1.0 / self.eig_max))",
     "self.kappa = float(gamma * (1.0 - 1.0 / self.eig_max))", "verification/check_certificate.py")
case("巡回の Friedkin–Johnsen の閉じた式で、分母を外す", "standard.py",
     "V[i, j] = path * (1.0 - lam[j]) / (1.0 - total)",
     "V[i, j] = path * (1.0 - lam[j])", "verification/check_standard.py")

print("\n3. 頁の数値と文を壊す")
case("ノートの窓の表の区間の数を一つずらす", "games/README.md",
     "| 0.62 | 134 |", "| 0.62 | 135 |", "verification/check_games.py")
case("ノートから「Claude is not an author.」を消す", "games/README.md",
     "proofs and the conjectures. The author is responsible for it. Claude is not an author.",
     "proofs and the conjectures. The author is responsible for it.", "verification/check_games.py")
case("教材第 1 回の不動点を一桁変える", "lessons/01-contractions-and-banach.md",
     "(0.510204, 0.306122, 0.183673)", "(0.510204, 0.306122, 0.183674)",
     "verification/check_lessons.py")
case("サイトの robots.txt の sitemap の行を、別の場所に向ける", "site/robots.txt",
     "vercel.app/sitemap.xml", "vercel.app/site-map.xml", "verification/check_site.py")

print("\n4. 使わないと決めた語と誤変換を混ぜる")
case("README に誤変換を混ぜる", "README.md",
     "## 著者\n", "## 著者\n\n" + MISCONVERTED + "\n", "verification/check_text.py")
case("README に使わないと決めた自称を混ぜる", "README.md",
     "## 著者\n", "## 著者\n\n" + SELF_TITLE + "\n", "verification/check_text.py")

print("\n5. 札・引用情報・関連識別子を壊す")
case("札の状態を変える", "README.md",
     "種類：ソフトウェア　状態：改訂中", "種類：ソフトウェア　状態：凍結", "verification/check_docs.py")
case("英語の欄から、注釈が日本語だという断りを消す", "README.md",
     "Code comments, docstrings, the\nprinted messages", "Docstrings, the\nprinted messages",
     "verification/check_docs.py")
case("CITATION.cff の type を dataset にする", "CITATION.cff",
     "type: software\nauthors:", "type: dataset\nauthors:", "verification/check_docs.py")
case("関連識別子に README に無い番号を足す", ".zenodo.json",
     '"identifier": "10.6084/m9.figshare.34419198"', '"identifier": "%s"' % FAKE_FIGSHARE,
     "verification/check_docs.py")
case("関連識別子の関係を references にする", ".zenodo.json",
     '"identifier": "10.5281/zenodo.22058624",\n      "relation": "isSupplementTo"',
     '"identifier": "10.5281/zenodo.22058624",\n      "relation": "references"',
     "verification/check_docs.py")

print("\n6. 例と図を壊す")
case("例の期待する出力を一桁変える", "examples/one_minute.txt",
     "不動点 = (0.754190,", "不動点 = (0.754191,", "verification/check_docs.py")
case("入力と出力の図の ρ を一桁変える", "README.md",
     "ρ(A) = 0.471769\"]", "ρ(A) = 0.471770\"]", "verification/check_docs.py")
case("展望の図の、段 4 の矢印の語を変える", "roadmap/README.md",
     '"外す：統合が線形"', '"外す：統合が非線形"', "verification/check_docs.py")

print("\n7. 開いている問題の頁を壊す")
case("予想 (a) の文を変える", "games/OPEN-PROBLEM.md",
     "`T_δ` has Lebesgue measure zero.", "`T_δ` has Lebesgue measure zero or one.",
     "verification/check_docs.py")
case("細分の深さを台本と違えて書く", "games/OPEN-PROBLEM.md",
     "depth 22 periods", "depth 24 periods", "verification/check_docs.py")
case("証明済みの表の状態を書き換える", "games/OPEN-PROBLEM.md",
     "positive Hausdorff dimension | proved |", "positive Hausdorff dimension | conjecture |",
     "verification/check_docs.py")
case("ラベルの名前をワークフローの側だけ変える", ".github/workflows/labels.yml",
     'gh label create "conjecture (b)"', 'gh label create "conjecture b"',
     "verification/check_docs.py")

print("\n8. 様式・依存・版・CI を壊す")
case("不具合の様式で、再現の手順を必須から外す", ".github/ISSUE_TEMPLATE/bug_report.yml",
     "        python3 check.py\n    validations:\n      required: true",
     "        python3 check.py\n    validations:\n      required: false",
     "verification/check_docs.py")
case("台本に、標準ライブラリでも NumPy でもないものを読ませる", "demo.py",
     "import numpy as np\n", "import numpy as np\nimport scipy\n", "verification/check_docs.py")
case("NumPy を使わないはずの check_text.py に NumPy を読ませる", "verification/check_text.py",
     "import os\n", "import os\nimport numpy\n", "verification/check_docs.py")
case("版と DOI の表の、版 1.0.0 の番号を変える", "README.md",
     "| 1.0.0 | 2026-11-07 | [10.5281/zenodo.24033459](https://doi.org/10.5281/zenodo.24033459) |",
     "| 1.0.0 | 2026-11-07 | [%s](https://doi.org/%s) |" % (FAKE_ZENODO, FAKE_ZENODO),
     "verification/check_docs.py")
case("CI から check_docs.py を外す", ".github/workflows/verify.yml",
     "run: python3 verification/check_docs.py", "run: echo skipped",
     "verification/check_docs.py")

print("\n8b. 百本ノック四で足した検査を壊す")
case("games/LICENSE の末尾を一語変える", "games/LICENSE",
     "Creative Commons may be contacted at creativecommons.org.",
     "Creative Commons may be contacted at creativecommons.net.", "verification/check_docs.py")
case("CITATION.cff の trinity-infinity の件数を古い 31 に戻す", "CITATION.cff",
     "紙面の数値を計算し直す 32 項目", "紙面の数値を計算し直す 31 項目", "verification/check_docs.py")
case("CLAUDE.md の一覧の、作用素の件数だけを変える", "CLAUDE.md",
     "# 作用素 29 項目", "# 作用素 28 項目", "verification/check_docs.py")
case("続ける範囲の頁から、開いている部分を一行落とす", "games/SCOPE.ja.md",
     "| `conjecture (b)` | Golden-window conjecture (b) | `T_δ` の次元についての証明か反例（単調性を含む） |\n", "",
     "verification/check_docs.py")
case("続ける範囲の頁が引く決めごと 15 の一文を変える", "games/SCOPE.md",
     "> 学部二年次以降に進めるのは、学部一年次の成果の続きか修正に限る",
     "> 学部二年次以降に進めるのは、学部一年次の成果の続きに限る", "verification/check_docs.py")
case("CI の checkout を版の名前に戻す（コミットの値で固定しない）", ".github/workflows/verify.yml",
     "- uses: actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0 # v7",
     "- uses: actions/setup-python@v7", "verification/check_docs.py")
case("CI に書き込みの権限を渡す", ".github/workflows/verify.yml",
     "permissions:\n  contents: read", "permissions:\n  contents: write", "verification/check_docs.py")
case("CI に NumPy のほかのパッケージを入れさせる", ".github/workflows/verify.yml",
     "run: pip install numpy", "run: pip install numpy scipy", "verification/check_docs.py")
case("誤りの知らせの様式で、根拠を必須から外す", ".github/ISSUE_TEMPLATE/error-report.yml",
     "a reference that others can check\n    validations:\n      required: true",
     "a reference that others can check\n    validations:\n      required: false", "verification/check_docs.py")
case("保存版の英語の要旨から、文を一つ落とす", ".zenodo.json",
     " All of these are known tools, and no new mathematics is included.", "",
     "verification/check_docs.py")
case("開示の表の見出しを変える", "README.md",
     "| 道具 | 使ったところ | 確かめた人 |", "| 道具 | 使ったところ | 確認 |", "verification/check_docs.py")
case("README に、許していないメールアドレスを混ぜる", "README.md",
     "## 著者\n", "## 著者\n\nsomeone" + "@" + "example.org\n", "verification/check_secrets.py")
case("サイトの viewport で拡大を止める", "site/index.html",
     'content="width=device-width, initial-scale=1.0"',
     'content="width=device-width, initial-scale=1.0, maximum-scale=1"', "verification/check_site.py")
case("サイトの暗い側の切り替えで、淡い文字の色を地に近づける", "site/index.html",
     "\n  --faint: #81818b;", "\n  --faint: #3a3a40;",
     "verification/check_site.py")

print("\n8c. 百本ノック五で足した検査を壊す（黄金比の窓の予想の、広げた走査と事前登録の下書き）")
case("走査の出力の写しで、区間の数を一つずらす", "games/scan.txt",
     "| 0.619 | 461 |", "| 0.619 | 462 |", "verification/check_games.py")
# 切り捨てそのものを外すと区間が 2³⁰ 個に増え、記憶が尽きる。端を一目盛りだけずらす。
case("走査の台本で、最初の区間の上端 3 を一目盛りだけ下げる", "games/scan.py",
     "ivs = [(q + p, 3 * p)]", "ivs = [(q + p, 3 * p - 1)]", "verification/check_games.py")
case("ノートの、総長が縮む行の数を変える", "games/README.md",
     "Growth is below `1/δ` in 48 of 48 rows", "Growth is below `1/δ` in 47 of 48 rows",
     "verification/check_games.py")
case("ノートから、走査は証明ではないという一文を消す", "games/README.md",
     "None of this is a proof. A grid of 48 values", "A grid of 48 values",
     "verification/check_games.py")
case("開いている問題の頁で、走査の深さを台本と違えて書く", "games/OPEN-PROBLEM.md",
     "depth 30 periods; exact counts", "depth 32 periods; exact counts", "verification/check_docs.py")
case("事前登録の下書きで、確かめの深さを台本と違えて書く", "games/PREREGISTRATION.md",
     "which is 32.", "which is 34.", "verification/check_docs.py")
case("事前登録の下書きから、まだ登録していないという冒頭の一文を消す", "games/PREREGISTRATION.md",
     "Status: draft, not registered. ", "", "verification/check_docs.py")
case("走査の台本で、確かめの格子の端の探りを探索の格子と重ねる", "games/scan.py",
     "for k in (6181, 6182, 6183, 6664, 6665, 6666))", "for k in (6181, 6182, 6183, 6664, 6665, 6660))",
     "verification/check_docs.py")
case("README の、広げた走査の δ の数を変える", "README.md",
     "0.001 刻みの 48 通りに増やし", "0.001 刻みの 47 通りに増やし", "verification/check_docs.py")
case("続ける範囲の頁の、最初の走査の深さを変える", "games/SCOPE.ja.md",
     "深さは 30 段で", "深さは 22 段で", "verification/check_docs.py")

print("\n9. 名乗っている壊し方の数が、実際の数と合う")
with io.open(os.path.abspath(__file__), encoding="utf-8") as fh:
    BREAKS = len(re.findall(r"^case\(", fh.read(), re.M))
with io.open(os.path.join(ROOT, "README.md"), encoding="utf-8") as fh:
    named = re.search(r"通る状態の写しを (\d+) 通りに壊し、(\d+) 通りとも落ちることを見ます。", fh.read())
check("README が名乗る壊し方の数が、実際の %d 通りと合う" % BREAKS,
      named is not None and int(named.group(1)) == BREAKS and int(named.group(2)) == BREAKS,
      ("名乗り %s・%s" % named.groups()) if named else "名乗っている箇所が見つからない")

print("\n" + "-" * 58)
if failures:
    print("%d 件が通り、%d 件が通りませんでした。" % (passed, len(failures)))
    for f in failures:
        print("  - " + f)
    sys.exit(1)
print("%d 件すべて通りました。" % passed)
