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
     "| `conjecture (b)` | Golden-window conjecture (b) | 命題 9 で解決済み（2026-11-18）。式は既知の定理の特別な場合。その証明の誤りを直すことと、曲線に沿った連続・狭義の増加・両端の極限の出典を探すこと |\n", "",
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

print("\n8d. 2026-11-18 に足した検査を壊す（黄金比の窓の予想の (a)・(b) を命題 8・9 で証明した）")
case("ノートの、命題 8 の筒の総長を一目盛り変える", "games/README.md",
     "goes from 0.65 to 0.00695 at δ = 0.62,", "goes from 0.65 to 0.00696 at δ = 0.62,", "verification/check_games.py")
case("台本の筒で、R の枝の引き算を外す（像が 0 から始まらなくなる）", "games/games.py",
     "pieces = ((Fraction(0), d * X, 0), (Fraction(1), X, 1))", "pieces = ((Fraction(0), d * X, 0), (Fraction(1), X, 0))",
     "verification/check_games.py")
case("ノートの表で、(a) の行を予想に戻す", "games/README.md",
     "the sustainable set has length zero | resolved (Proposition 8); a special case of known theorems |", "the sustainable set has length zero | **conjecture** |",
     "verification/check_games.py")
case("ノートの表で、(b) の行を予想に戻す", "games/README.md",
     "runs from 0 to 1 across the interval | resolved (Proposition 9); the formula is a special case of known theorems; continuity, strict increase and the end limits were not found in the texts read |", "runs from 0 to 1 across the interval | **conjecture** |",
     "verification/check_games.py")
case("ノートから、測度 0 では (b) が決まらないという文を消す", "games/README.md",
     "Part (b) is proved. It is Proposition 9, written on 2026-11-18. Measure zero does not settle\nit:",
     "Part (b) is proved. It is Proposition 9, written on 2026-11-18. Measure zero settles\nit:",
     "verification/check_games.py")
case("ノートから、命題 8 の証明を書いた者と日付の一文を消す", "games/README.md",
     "This proposition is part (a) of the golden-window conjecture below. The proof was written by\nClaude Code at the author's request on 2026-11-18. ",
     "This proposition is part (a) of the golden-window conjecture below. ", "verification/check_games.py")
case("ノートの命題 9 の表の次元を一目盛り変える", "games/README.md",
     "| 0.62 | {1, 9} | 0.404196 |", "| 0.62 | {1, 9} | 0.404197 |", "verification/check_games.py")
case("台本の強制された道で、R の歩みを β(s − 1) から βs − 1 に替える", "games/games.py",
     "            s = beta * (s - 1)\n        elif s < d * X:", "            s = beta * s - 1\n        elif s < d * X:",
     "verification/check_games.py")
case("ノートに、記憶から引いた文献の名を足す", "games/README.md",
     "the standard\ntheorem on self-similar sets under the strong separation condition,",
     "the standard\ntheorem on self-similar sets under the strong separation condition (Hutchinson 1981),",
     "verification/check_games.py")
case("開いている問題の頁で、ラベル (b) の状態を open に戻す", "games/OPEN-PROBLEM.md",
     "| Golden-window conjecture (b) | resolved: proved as Proposition 9 (2026-11-18) |",
     "| Golden-window conjecture (b) | open |", "verification/check_docs.py")
case("開いている問題の頁で、(b) を開いているに戻す", "games/OPEN-PROBLEM.md",
     "Part (b) is proved. It is Proposition 9, written on 2026-11-18.", "Part (b) is open.", "verification/check_docs.py")
case("開いている問題の頁の証明済みの表から、命題 8 の行を落とす", "games/OPEN-PROBLEM.md",
     "| Proposition 8 | inside the window 1/φ < δ < 2/3, the sustainable set has length zero | proved |\n", "",
     "verification/check_docs.py")
case("予想のサイトで、二つの部分を証明したという一文を、証明していないに戻す", "site/index.html",
     "Both are proved: part (a) is Proposition 8 and part (b) is Proposition 9 of the note.", "It has not been proved.",
     "verification/check_site.py")

print("\n8e. 2026-11-22 に足した検査を壊す（デザインに関する法的な扱いの頁と、引いた条の写し）")
CS = "verification/check_site.py"
case("日本語の頁で、商標法第25条の文を一語変える", "site/design-legal.ja.html",
     "について登録商標の使用をする権利を専有する。", "について登録商標の使用をする権利を保有する。", CS)
case("英語の頁で、切り出した障害者差別解消法第2条第七号を写しに無い文にする", "site/design-legal.html",
     "七 事業者 商業その他の事業を行う者", "七 事業者 商業を行う者", CS)
case("条の写しの文を一語変える（固めた SHA-256 と合わなくなる）", "verification/design-statutes.json",
     "思想又は感情を創作的に表現したもの", "思想又は感情を表現したもの", CS)
case("日本語の頁の部品の表で、og.png を無いファイルの名に替える", "site/design-legal.ja.html",
     '<tr><td>共有したときのカードの画像</td><td><code>og.png</code></td>', '<tr><td>共有したときのカードの画像</td><td><code>og.jpg</code></td>', CS)
case("表に挙げた画像のファイルを消す", "site/apple-touch-icon.png", None, None, CS)
case("英語の頁で、favicon.ico の中の大きさを違えて書く", "site/design-legal.html",
     '<span id="ico-sizes">16, 32, 48</span>', '<span id="ico-sizes">16, 32, 64</span>', CS)
case("日本語の頁で、ロゴの長方形の数を違えて書く", "site/design-legal.ja.html",
     '<span id="logo-rects">9</span>', '<span id="logo-rects">8</span>', CS)
case("英語の頁で、配色の比の最小を一目盛り上げて書く", "site/design-legal.html",
     '<span id="min-ratio">4.54</span>', '<span id="min-ratio">4.55</span>', CS)
case("日本語の頁で、淡い文字の色をトップの頁と違える", "site/design-legal.ja.html",
     "  --faint: #727278;", "  --faint: #929298;", CS)
case("英語の頁で、条の要旨から「訳ではない」の断りを外す", "site/design-legal.html",
     "Summary, not a translation: it defines a work", "It defines a work", CS)
case("英語の頁に、外のスタイルシートを読ませる", "site/design-legal.html",
     '<link rel="icon" href="./favicon.ico" sizes="48x48">\n',
     '<link rel="icon" href="./favicon.ico" sizes="48x48">\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2">\n', CS)
case("日本語の頁から、弁護士の確認を受けていないという一文を消す", "site/design-legal.ja.html",
     "<p>この頁は、弁護士の確認を受けていません。</p>\n", "", CS)
case("sitemap.xml から、日本語の頁を落とす", "site/sitemap.xml",
     "  <url>\n    <loc>https://golden-window-conjecture.vercel.app/design-legal.ja.html</loc>\n  </url>\n", "", CS)
case("英語の頁の下の欄から、CC BY 4.0 を外す", "site/design-legal.html",
     "<span>© 2026 Takuya Nemoto · CC BY 4.0</span>", "<span>© 2026 Takuya Nemoto</span>", CS)
case("日本語の頁で、引く条の数を違えて名乗る", "site/design-legal.ja.html",
     '<span id="statute-count">11</span>', '<span id="statute-count">10</span>', CS)
case("英語の頁の引いた条の表で、SHA-256 を一字変える", "site/design-legal.html",
     "<code>e1cd4c4290fdca9b93e0fd753c50e9fe5c6e353650609eb3f0d044c66797c405</code>",
     "<code>e1cd4c4290fdca9b93e0fd753c50e9fe5c6e353650609eb3f0d044c66797c406</code>", CS)
case("日本語の頁で、障害者差別解消法を正式の名より先に略称で書く", "site/design-legal.ja.html",
     "<p>障害を理由とする差別の解消の推進に関する法律（以下、障害者差別解消法）の第2条は、",
     "<p>障害者差別解消法の第2条は、", CS)
case("日本語の頁で、CC BY 4.0 の法的な文を一語変える", "site/design-legal.ja.html",
     "Patent and trademark rights are not licensed under this Public License.",
     "Patent and trademark rights are licensed under this Public License.", CS)
case("英語の頁で、等幅の書体の並びを入れ替える", "site/design-legal.html",
     "<li>Monospace: <code>ui-monospace, SFMono-Regular,", "<li>Monospace: <code>SFMono-Regular, ui-monospace,", CS)
case("日本語の頁で、切り出した条の前から切り出したという断りを消す", "site/design-legal.ja.html",
     "同じ法の第20条は、次のとおりです。第1項だけを切り出しました。", "同じ法の第20条は、次のとおりです。", CS)
case("日本語の頁に、創作の系列の名を書く", "site/design-legal.ja.html",
     "<p>他人の素材は使っていません。", "<p>Nusquama の素材は使っていません。", CS)
# 2026-11-23。奥行きで足した二色。面の下の色（--card-lo）と、地の左上に重ねる光（--glow）。
case("サイトの明るい側の面の下の色を、地より暗くする", "site/index.html",
     "\n  --card-lo: #fcfbf9;", "\n  --card-lo: #e2dfda;", CS)
case("サイトの明るい側の地に重ねる光を、白から墨に替える", "site/index.html",
     "--glow: rgba(255, 255, 255, .72);", "--glow: rgba(23, 23, 26, .3);", CS)

# 2026-11-23。予想のサイトの意匠（帯・渦・飾り・ロゴの二色）。形は φ の式から数え直し、色はロゴと突き合わせる。
case("帯の区間の幅を一つだけ変える", "site/index.html",
     '<rect x="90.17" y="1.5" width="55.73" height="2"/>', '<rect x="90.17" y="1.5" width="56.73" height="2"/>', CS)
case("渦の二つ目の正方形の辺を、1/φ から外す", "site/index.html",
     '<rect x="38.2" y="100" width="61.8" height="61.8" class="gw-seal-sq"', '<rect x="38.2" y="100" width="64" height="64" class="gw-seal-sq"', CS)
case("意匠の金を、ロゴの金から外す", "site/index.html",
     "  --gw-gold: #c9a13b;", "  --gw-gold: #262a33;", CS)
case("日本語の法的な扱いの頁から、写した帯を外す", "site/design-legal.ja.html",
     '<header>\n  <svg class="gw-band"', '<header>\n  <svg class="gw-band-x"', CS)
case("紙で帯と渦を刷る", "site/index.html",
     "  .gw-band, .hero .gw-seal, .hero::after { display: none; }", "  .hero::after { display: none; }", CS)

# 2026-11-24。IndexNow。鍵のファイル、ワークフローが見る sitemap、知らせる先を壊す。
INDEXNOW_KEY = "16529c1323fad834c26ee0393e5f50b8"
case("IndexNow の鍵のファイルを消す", "site/%s.txt" % INDEXNOW_KEY, None, None, CS)
case("IndexNow の鍵のファイルの中身を、名と一字違える", "site/%s.txt" % INDEXNOW_KEY,
     INDEXNOW_KEY, INDEXNOW_KEY[:-1] + "9", CS)
case("IndexNow のワークフローに、根の sitemap.xml を見させる", ".github/workflows/indexnow.yml",
     "    paths: [site/sitemap.xml]\n", "    paths: [sitemap.xml]\n", CS)
case("tools/indexnow.js の知らせる先を、ほかのホストにする", "tools/indexnow.js",
     "const BASE = 'https://golden-window-conjecture.vercel.app/';", "const BASE = 'https://golden-window.vercel.app/';", CS)
case("tools/indexnow.js に、前の head の根の sitemap.xml を読ませる", "tools/indexnow.js",
     "at + ':site/sitemap.xml'", "at + ':sitemap.xml'", CS)
case("sitemap.xml の頁を一つ、ほかのホストに替える", "site/sitemap.xml",
     "<loc>https://golden-window-conjecture.vercel.app/design-legal.html</loc>",
     "<loc>https://golden-window.vercel.app/design-legal.html</loc>", CS)

# 2026-11-24。Wayback Machine。手で起こすときだけ、読むだけの権限、site/sitemap.xml、その日の写しの確かめ、読んだ頁だけ、を壊す。
WB = ".github/workflows/wayback.yml"
case("Wayback のワークフローを push でも動かす", WB, "on:\n  workflow_dispatch:\n", "on:\n  push:\n  workflow_dispatch:\n", CS)
case("Wayback のワークフローに中身を書く権限を渡す", WB, "permissions:\n  contents: read\n", "permissions:\n  contents: write\n", CS)
case("Wayback のワークフローに、根の sitemap.xml を読ませる", WB, 'open("site/sitemap.xml", encoding="utf-8")', 'open("sitemap.xml", encoding="utf-8")', CS)
case("Wayback のワークフローが、その日の写しかを確かめない", WB, ' and c["timestamp"].startswith(today)', "", CS)
case("Wayback のワークフローが、確かめられない写しがあっても落ちない", WB, "if failed or unread:\n", "if False:\n", CS)
case("Wayback の読んだ頁から、日本語の法的な扱いの頁を外す", WB,
     '              "https://golden-window-conjecture.vercel.app/design-legal.ja.html",\n', "", CS)
case("英語の法的な扱いの頁に、PDF へのリンクを張る", "site/design-legal.html",
     'href="https://github.com/cpsbvbng26-dotcom/trinity-operator/blob/main/verification/design-statutes.json"',
     'href="https://github.com/cpsbvbng26-dotcom/trinity-operator/blob/main/verification/design-statutes.pdf"', CS)

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
