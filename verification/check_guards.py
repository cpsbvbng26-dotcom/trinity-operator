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
    """rel の old を new に替えた写しで script を走らせ、落ちることを見る。old が None なら rel を消す。"""
    tmp = tempfile.mkdtemp()
    try:
        dst = os.path.join(tmp, "repo")
        shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        path = os.path.join(dst, rel)
        if old is None:                     # ファイルごと消す
            if not os.path.isfile(path):
                check(label, False, "消すはずの %s が無い" % rel)
                return
            os.remove(path)
        else:
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
case("公開中のサイトの見張りに、issue のほかの書き込みの権限を渡す", ".github/workflows/live.yml",
     "permissions:\n  contents: read\n  issues: write\n", "permissions:\n  contents: read\n  issues: write\n  pull-requests: write\n", "verification/check_docs.py")
case("公開中のサイトの見張りに、中身を書く権限を渡す", ".github/workflows/live.yml",
     "permissions:\n  contents: read\n  issues: write\n", "permissions:\n  contents: write\n  issues: write\n", "verification/check_docs.py")
case("CI に issue への書き込みの権限を渡す", ".github/workflows/verify.yml",
     "permissions:\n  contents: read", "permissions:\n  contents: read\n  issues: write", "verification/check_docs.py")
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
case("サイトの著者の sameAs から、人の Wikidata の項目を外す", "site/index.html",
     '"https://orcid.org/0009-0000-1406-0547",\n          "https://www.wikidata.org/wiki/Q139590485"',
     '"https://orcid.org/0009-0000-1406-0547"', "verification/check_site.py")
case("サイトの著者の sameAs で、人の Wikidata の項目を別の番号にする", "site/index.html",
     '"https://www.wikidata.org/wiki/Q139590485"', '"https://www.wikidata.org/wiki/Q139590486"',
     "verification/check_site.py")

print("\n8c. 百本ノック五で足した検査を壊す（黄金比の窓の予想の、広げた走査と事前登録と確かめの走査の結果）")
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
case("事前登録の頁の、登録した本文で、確かめの深さを台本と違えて書く", "games/PREREGISTRATION.md",
     "which is 32.", "which is 34.", "verification/check_docs.py")
case("事前登録の頁から、OSF に登録したという冒頭の一文を消す", "games/PREREGISTRATION.md",
     "Status: registered on OSF. ", "", "verification/check_docs.py")
# 2026-11-17 に登録の状態へ移した検査を壊す。違う番号はその場で組む（横断の検査が DOI の一覧と突き合わせるため）。
case("事前登録の頁の登録の DOI を、受け取っていない番号に替える", "games/PREREGISTRATION.md",
     "[10.17605/OSF.IO/6EW38](https://doi.org/10.17605/OSF.IO/6EW38)",
     "[{0}](https://doi.org/{0})".format("10.17605/" + "OSF.IO/6EW39"), "verification/check_docs.py")
case("ノートに、二つ目の登録の DOI を足す", "games/README.md",
     "the text on OSF governs.\n", "the text on OSF governs. See also " + "10.17605/" + "osf.io/7kr5n.\n",
     "verification/check_docs.py")
case("事前登録の頁の、線の下の登録した本文を一語変える", "games/PREREGISTRATION.md",
     "There is no stopping rule.", "There is a stopping rule.", "verification/check_docs.py")
case("事前登録の頁に、まだ登録していないという下書きの一文を戻す", "games/PREREGISTRATION.md",
     "The text on OSF governs.\n", "The text on OSF governs. No registration DOI exists yet.\n",
     "verification/check_docs.py")
case("確かめの格子の出力を消す", "games/scan-confirmatory.txt", None, None, "verification/check_docs.py")
case("確かめの格子の出力の一行目で、深さを 34 と名乗る", "games/scan-confirmatory.txt",
     "); depth 32.", "); depth 34.", "verification/check_docs.py")
case("確かめの格子の出力から、表の一行を落とす", "games/scan-confirmatory.txt",
     "| 0.6183 | 279 | 5.72e-06 | 1.158 | 0.716 | 0.733 | 0.305 | 0.366 | 12 | 0.314 |\n", "",
     "verification/check_docs.py")
case("確かめの格子の出力で、区間の数を一つずらす", "games/scan-confirmatory.txt",
     "| 0.6182 | 224 |", "| 0.6182 | 225 |", "verification/check_docs.py")
case("ノートの、成長率 × δ の最大を一目盛り変える", "games/README.md",
     "The largest growth × δ is 0.999695,", "The largest growth × δ is 0.999696,", "verification/check_docs.py")
case("開いている問題の頁の、次元の推定の最大を一目盛り変える", "games/OPEN-PROBLEM.md",
     "The largest is 0.999247, at", "The largest is 0.999248, at", "verification/check_docs.py")
case("開いている問題の頁の、下界を下回る値の数を変える", "games/OPEN-PROBLEM.md",
     "Proposition 6 at 17 values.", "Proposition 6 at 16 values.", "verification/check_docs.py")
case("ノートの、上からの推定が 1 以上になる値の数を変える", "games/README.md",
     "estimate is 1 or more at 6 values", "estimate is 1 or more at 5 values", "verification/check_docs.py")
case("ノートの、H1 が通った値の数を変える", "games/README.md",
     "Growth × δ is below 1 at 54 of 54 values", "Growth × δ is below 1 at 53 of 54 values",
     "verification/check_docs.py")
case("開いている問題の頁の、次元の推定が下がる箇所の数を変える", "games/OPEN-PROBLEM.md",
     "The scan counts\n  0 decreases", "The scan counts\n  1 decreases", "verification/check_docs.py")
case("ノートの、2/3 の近くの差を一桁変える", "games/README.md",
     "by about 3 × 10⁻⁴.", "by about 3 × 10⁻⁵.", "verification/check_docs.py")
case("ノートから、確かめの走査は証明ではないという一文を消す", "games/README.md",
     "This is evidence on 54 more values of δ, not a proof. ", "", "verification/check_docs.py")
case("開いている問題の頁で、証明ではないを証明だと書き換える", "games/OPEN-PROBLEM.md",
     "This is evidence on 54 more values of δ, not a proof.", "This is a proof on 54 more values of δ.",
     "verification/check_docs.py")
case("ノートの出力の SHA-256 を一字変える", "games/README.md",
     "(SHA-256 `f3c40d4b", "(SHA-256 `f3c40d4c", "verification/check_docs.py")
case("README の、確かめの格子の数を変える", "README.md",
     "確かめの格子（54 通り、深さ 32 段）", "確かめの格子（53 通り、深さ 32 段）", "verification/check_docs.py")
case("README から、確かめの走査も証明ではないという一文を消す", "README.md",
     "2/3 の近くでは 1 との差が小さく、これも根拠であって証明ではありません。\n", "",
     "verification/check_docs.py")
case("README から、記録を書いた者の一文を消す", "README.md",
     "この記録は、2026-11-17 に利用者が登録し、DOI を受け取って Claude が書きました。\n", "",
     "verification/check_docs.py")
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
