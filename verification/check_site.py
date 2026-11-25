#!/usr/bin/env python3
"""黄金比の窓の予想の英語サイト（site/）を検査する。

    python3 verification/check_site.py

標準ライブラリのみ。

site/index.html は生成物である。researcher-profile の golden-window.en.json に
golden-window.site.json を重ねて build.js で出し、ここへ写す。本文を直すときは
生成もとを直す。この検査は、写したものが配信先として壊れていないかを見る。

配信先は Vercel の golden-window プロジェクトで、このディレクトリを根にしている。
"""

import base64
import hashlib
import io
import json
import os
import re
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
URL = "https://golden-window-conjecture.vercel.app/"
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


def read(name):
    p = os.path.join(SITE, name)
    return io.open(p, encoding="utf-8").read() if os.path.exists(p) else ""


html = read("index.html")
svg = read("favicon.svg")
robots = read("robots.txt")
sitemap = read("sitemap.xml")

print("\n1. 置いてあるもの")
for name in ("index.html", "favicon.svg", "robots.txt", "sitemap.xml"):
    check(name + " がある", bool(read(name)))

print("\n2. 正の URL がひとつ")
canon = re.findall(r'<link rel="canonical" href="([^"]+)">', html)
check("canonical が一つで、配信先を指す", canon == [URL], repr(canon))
og = re.findall(r'<meta property="og:url" content="([^"]+)">', html)
check("og:url が canonical と同じ", og == [URL], repr(og))
# 2026-11-22 から、デザインに関する法的な扱いの頁を二つ（英語と日本語）配る。site/ の頁は、どれも一度ずつ並べる。
DESIGN_PAGES = ["design-legal.html", "design-legal.ja.html"]
# 2026-11-25 から、サイトに無い所在に Vercel が返す頁（404.html）も配る。索引に載せない頁なので、sitemap には入れない。
NOT_FOUND = "404.html"
check("sitemap.xml の loc が、トップの canonical と、デザインの扱いの頁の二つだけ",
      re.findall(r"<loc>([^<]+)</loc>", sitemap) == [URL] + [URL + n for n in DESIGN_PAGES])
check("site/ の頁（.html）が、404.html のほかはどれも sitemap.xml にあり、404.html は sitemap に無い",
      sorted(f for f in os.listdir(SITE) if f.endswith(".html")) == sorted(["index.html"] + DESIGN_PAGES + [NOT_FOUND])
      and "404" not in sitemap)
check("robots.txt が sitemap.xml を指す",
      ("Sitemap: " + URL + "sitemap.xml") in robots)

# 構造化データは JSON として読めなければ、検索エンジンは黙って捨てる。
ld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
try:
    graph = json.loads(ld[0])["@graph"] if len(ld) == 1 else []
except ValueError:
    graph = []
site_ld = [g for g in graph if g.get("@type") == "WebSite"]
page_ld = [g for g in graph if g.get("@type") == "WebPage"]
check("構造化データの WebSite が配信先を指す",
      len(site_ld) == 1 and site_ld[0].get("url") == URL)
check("構造化データの WebPage が配信先を指す",
      len(page_ld) == 1 and page_ld[0].get("url") == URL)

# 2026-11-17。著者の Person は、ORCID と人の Wikidata の項目（Q139590485）を sameAs に持つ。
# 人の項目は著者のところに一度だけ置き、ほかの Wikidata の項目は置かない。
ORCID = "https://orcid.org/0009-0000-1406-0547"
WD_PERSON = "Q139590485"
author = page_ld[0].get("author") if len(page_ld) == 1 else None
same = author.get("sameAs", []) if isinstance(author, dict) else []
check("構造化データの著者が、ORCID と人の Wikidata の項目（%s）を sameAs に持つ" % WD_PERSON,
      isinstance(author, dict) and author.get("@type") == "Person"
      and ORCID in same and "https://www.wikidata.org/wiki/" + WD_PERSON in same, repr(same))
wd_others = sorted(set(re.findall(r"wikidata\.org/(?:wiki|entity)/(Q\d+)", html)) - {WD_PERSON})
check("人の項目は頁に一度だけあり、ほかの Wikidata の項目が無い",
      html.count(WD_PERSON) == 1 and not wd_others, ", ".join(wd_others) or "%d 回" % html.count(WD_PERSON))

print("\n3. 検索結果に出るロゴ")
# Google は、トップページから rel="icon" で指された正方形の画像を使う。
# 大きさは 48px の倍数を求める。SVG は viewBox で見る。
icons = re.findall(r'<link rel="icon" href="([^"]+)"', html)
check("rel=\"icon\" が favicon.svg と、その画素の版を指す",
      icons == ["./favicon.svg", "./favicon.ico", "./favicon-192.png"], repr(icons))
check("apple-touch-icon が apple-touch-icon.png を指す",
      re.findall(r'<link rel="apple-touch-icon" href="([^"]+)"', html) == ["./apple-touch-icon.png"])


def png_size(b):
    if b[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", b[16:24])


def raw(name):
    p = os.path.join(SITE, name)
    return io.open(p, "rb").read() if os.path.exists(p) else b""


# SVG を読まない検索結果もあるので、同じロゴを画素にした版を並べる。
ico = raw("favicon.ico")
ico_sizes = []
if ico[:4] == b"\x00\x00\x01\x00":
    for i in range(struct.unpack("<H", ico[4:6])[0]):
        size, off = struct.unpack("<II", ico[6 + 16 * i + 8:6 + 16 * i + 16])
        ico_sizes.append(png_size(ico[off:off + size]))
check("favicon.ico に 16・32・48 px のロゴが入っている",
      ico_sizes == [(16, 16), (32, 32), (48, 48)], repr(ico_sizes))
check("favicon-192.png が 192 × 192", png_size(raw("favicon-192.png")) == (192, 192))
check("apple-touch-icon.png が 180 × 180", png_size(raw("apple-touch-icon.png")) == (180, 180))
vb = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg)
check("ロゴが正方形で、一辺が 48 の倍数",
      bool(vb) and vb.group(1) == vb.group(2) and int(vb.group(1)) % 48 == 0,
      vb.group(0) if vb else "viewBox が無い")
check("ロゴが外から何も読まない", "href" not in svg and "url(" not in svg)

print("\n3b. 共有したときに出るロゴ")
# SNS のカードは SVG を読まないので、PNG を絶対 URL で指す。
# summary のカードは正方形の画像を小さく出す。X は一辺 144px 以上を求める。
cards = re.findall(r'<meta name="twitter:card" content="([^"]+)">', html)
check("カードの型が summary", cards == ["summary"], repr(cards))
ogi = re.findall(r'<meta property="og:image" content="([^"]+)">', html)
check("og:image が配信先の og.png を指す", ogi == [URL + "og.png"], repr(ogi))
# X は og:image で補うと書いているが、補われずに画像が出なかった。明示する。
twi = re.findall(r'<meta name="twitter:image" content="([^"]+)">', html)
check("twitter:image が og:image と同じ", twi == ogi and bool(twi), repr(twi))
png = b""
if os.path.exists(os.path.join(SITE, "og.png")):
    png = io.open(os.path.join(SITE, "og.png"), "rb").read()
size = struct.unpack(">II", png[16:24]) if png[:8] == b"\x89PNG\r\n\x1a\n" else (0, 0)
check("og.png が正方形の PNG で、一辺が 144px 以上",
      size[0] == size[1] and size[0] >= 144, "%d×%d" % size)

print("\n4. 外へリクエストを出さない")
csp = re.search(r'<meta http-equiv="Content-Security-Policy" content="([^"]+)">', html)
csp = csp.group(1) if csp else ""
check("CSP が default-src 'none' から始まる", csp.startswith("default-src 'none'"))
check("CSP に 'unsafe-inline' が無い", bool(csp) and "'unsafe-inline'" not in csp)
check("外部のスクリプトを読まない", not re.search(r'<script[^>]+src=', html))
check("外部のスタイルシートを読まない", not re.search(r'<link[^>]+rel="stylesheet"', html))


def sha(text):
    d = hashlib.sha256(text.encode("utf-8")).digest()
    return "'sha256-" + base64.b64encode(d).decode() + "'"


# 生成のあとで本文を手で直すと、ハッシュが合わなくなってブラウザが黙って止める。
scripts = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", html, re.S)
styles = re.findall(r"<style[^>]*>(.*?)</style>", html, re.S)
check("インラインのスクリプトがすべて CSP のハッシュと合う",
      bool(scripts) and all(sha(s) in csp for s in scripts), "%d 個" % len(scripts))
check("インラインのスタイルがすべて CSP のハッシュと合う",
      bool(styles) and all(sha(s) in csp for s in styles), "%d 個" % len(styles))

print("\n5. 予想の状態を、ノートと同じに出している")
# 2026-11-18 に、ノートが (a) と (b) を命題 8 と 9 として証明した。証明を足してから頁の状態を動かした。
# 「It has not been proved.」を、二つの部分を証明したことと、状態（解決済み。(a) と (b) の式は既知の定理の特別な場合で、δ についての連続・狭義の増加・両端の極限は読んだ文献に見つからない）の文に移した。
# 同じ日の照合のあと、「It has not been checked against the literature.」は「命題 1〜7 は照合していない」に移した。
for phrase in ("Both are proved: part (a) is Proposition 8 and part (b) is Proposition 9 of the note.",
               "Status: resolved (part (a) and the formula of part (b) are special cases of known theorems; continuity and strict increase in ",
               "and the limits at both ends were not found in the texts read).",
               "Propositions 1–7 have not been checked against the literature.",
               "It is a preprint and has not been peer-reviewed.",
               "The posted version is frozen, and it still states both parts as conjectures."):
    check("本文に「" + phrase + "」がある", phrase in html)
check("論文の DOI へのリンクがある",
      'href="https://doi.org/10.6084/m9.figshare.34419198"' in html)

print("\n6. <meta> では出せない安全のヘッダー")
# frame-ancestors は <meta> の CSP では効かない。よその頁の枠に埋め込まれないように、Vercel にヘッダーで出させる。
# ヘッダーの CSP は frame-ancestors だけを名乗る。読み込みを絞るのは、これまでどおり頁の <meta> である。
try:
    vcfg = json.loads(read("vercel.json"))
except ValueError:
    vcfg = {}
allp = [h for h in vcfg.get("headers", []) if h.get("source") == "/(.*)"]
hdr = {}
for h in (allp[0].get("headers", []) if allp else []):
    hdr.setdefault(h.get("key"), []).append(h.get("value"))
# 2026-11-08 から、main 以外の枝を配信しない決まりも持つ（無料の枠の一日の上限を作業の枝で使い切ったため）。
check("vercel.json はヘッダーと main だけを配信する決まりを持ち、ヘッダーをすべての経路に付ける", list(vcfg.keys()) == ["headers", "git"] and len(allp) == 1 and vcfg["git"] == {"deploymentEnabled": {"**": False, "main": True}})
check("枠への埋め込みを二通りで断る", hdr.get("Content-Security-Policy") == ["frame-ancestors 'none'"] and hdr.get("X-Frame-Options") == ["DENY"])
check("型の推測をさせず、参照元を送らず、ブラウザの機能を求めず、窓を切り離し、HTTPS を覚えさせる",
      hdr.get("X-Content-Type-Options") == ["nosniff"] and hdr.get("Referrer-Policy") == ["no-referrer"]
      and "camera=()" in (hdr.get("Permissions-Policy") or [""])[0] and hdr.get("Cross-Origin-Opener-Policy") == ["same-origin"]
      and re.match(r"max-age=\d{8,}", (hdr.get("Strict-Transport-Security") or [""])[0]) is not None)

# ここから下は、全サイトで揃える読みやすさの決め（百本ノック四の 321〜328）。
# site/index.html は生成物なので、落ちたら researcher-profile の生成もとを直して作り直す。
css = "\n".join(styles)

print("\n7. 文字を大きくしても、狭い画面でも崩れない（200% と 360px）")
vp = re.findall(r'<meta name="viewport" content="([^"]+)">', html)
check("viewport が一つで、拡大を止めていない",
      len(vp) == 1 and "width=device-width" in vp[0]
      and "user-scalable=no" not in vp[0].replace(" ", "") and "maximum-scale" not in vp[0], repr(vp))
px_font = re.findall(r"font-size:\s*[\d.]+px", css)
check("文字の大きさを px で決めていない（ブラウザの文字の拡大が効く）", not px_font, ", ".join(px_font[:3]))
px_width = [w for w in re.findall(r"(?<![-\w])(?:min-)?width:\s*([\d.]+)px", css) if float(w) > 320]
check("幅を 320px を超える px で決めていない", not px_width, ", ".join(px_width[:3]))
check("表が頁を押し広げず、自分の中で横へ流れる",
      re.search(r"\.prose table\s*\{[^}]*max-width:\s*100%[^}]*overflow-x:\s*auto", css) is not None)
svgs = re.findall(r"<svg\b[^>]*>", html)
wide_svg = [s for s in svgs if re.search(r'\bwidth="(\d+)"', s) and int(re.search(r'\bwidth="(\d+)"', s).group(1)) > 320]
check("図（svg）が viewBox で縮み、320px を超える幅を属性で持たない",
      all("viewBox=" in s for s in svgs) and not wide_svg, "%d 個" % len(svgs))
check("狭い画面でナビを折り返す決めがある",
      re.search(r"@media \(max-width: 30rem\)\s*\{\s*\.head-row\s*\{\s*flex-wrap:\s*wrap", css) is not None)

print("\n8. 色の対比（WCAG 2.1、本文 4.5:1）")


def lum(hexv):
    h = hexv.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    rgb = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def tokens(block):
    return dict(re.findall(r"--([a-z-]+):\s*(#[0-9a-fA-F]{3,6})\s*;", block))


light = re.search(r":root\s*\{(.*?)\}", css, re.S)
dark = re.search(r':root\[data-theme="dark"\]\s*\{(.*?)\}', css, re.S)
auto = re.search(r'@media \(prefers-color-scheme: dark\)\s*\{\s*:root:not\(\[data-theme="light"\]\)\s*\{(.*?)\}', css, re.S)
themes = [("ライト", tokens(light.group(1)) if light else {}),
          ("ダーク", tokens(dark.group(1)) if dark else {})]
# 2026-11-23。面の下の色（--card-lo）。面は上から下へ --card から --card-lo へ暗くなるので、字はその両端に載る。
for name, t in themes:
    for base in ("bg", "card", "card-lo"):
        for tok in ("text", "muted", "faint", "accent"):
            if t.get(base) and t.get(tok):
                r = ratio(t[tok], t[base])
                check("%s --%s / --%s が 4.5:1 以上" % (name, tok, base), r >= 4.5, "%.2f:1" % r)


# 2026-11-23。地の左上に重ねる光（--glow、rgba）。光を最も濃く重ねた地の色で、本文の四色の比を測る。
def glow_over(block, base):
    m = re.search(r"--glow:\s*rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)", block)
    if not m or not base:
        return None
    c, a = [int(m.group(i)) for i in (1, 2, 3)], float(m.group(4))
    g = [int(base.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join("%02x" % int(round(c[k] * a + g[k] * (1 - a))) for k in range(3))


for name, t, blk in (("ライト", themes[0][1], light), ("ダーク", themes[1][1], dark)):
    lit = glow_over(blk.group(1) if blk else "", t.get("bg"))
    low = min(ratio(t[tok], lit) for tok in ("text", "muted", "faint", "accent") if t.get(tok)) if lit else 0
    check("%s 本文の四色が、光（--glow）を重ねた地 %s に対して 4.5:1 以上" % (name, lit), lit is not None and low >= 4.5, "%.2f:1" % low)
check("配色の定義がライトとダークの両方にある（本文の四色と地の色）",
      all(t.get("bg") and t.get("text") and t.get("muted") and t.get("faint") and t.get("accent") for _, t in themes))

print("\n9. ダークテーマ")
check("切り替えのボタンがある", 'id="themeToggle"' in html and 'aria-label="Toggle theme"' in html)
check("JS が動かなくても、OS の設定で暗い側が出る", auto is not None)
check("OS の設定で出る暗い側が、切り替えの暗い側と同じ色",
      auto is not None and dark is not None and tokens(auto.group(1)) == tokens(dark.group(1)))
check("ブラウザの枠の色を、明るい側と暗い側で一つずつ渡している",
      len(re.findall(r'<meta name="theme-color" content="#[0-9a-f]{6}" media="\(prefers-color-scheme: (?:light|dark)\)">', html)) == 2)

print("\n10. 画像の代替テキスト")
imgs = re.findall(r"<img\b[^>]*>", html)
check("<img> がどれも alt を持つ", all(re.search(r'\balt="', i) for i in imgs), "%d 個" % len(imgs))
check("意味を持つ図（role=img の svg）がどれも aria-label で中身を言う",
      all(re.search(r'aria-label="[^"]{12,}"', s) for s in svgs if 'role="img"' in s))
check("それ以外の svg は読み上げから外している",
      all('aria-hidden="true"' in s for s in svgs if 'role="img"' not in s))

print("\n11. 頁の重さ")
WEIGHT_CAP = 100 * 1024      # 頁と、頁が読む画像（アイコンとカード）を合わせた上限
weight = sum(os.path.getsize(os.path.join(SITE, f)) for f in
             ("index.html", "favicon.svg", "favicon.ico", "favicon-192.png", "apple-touch-icon.png", "og.png")
             if os.path.exists(os.path.join(SITE, f)))
check("頁と画像を合わせて %d KB 以下" % (WEIGHT_CAP // 1024), 0 < weight <= WEIGHT_CAP, "%d バイト" % weight)

print("\n12. 言語の切り替えと、頁の下の欄")
nav = re.search(r'<nav class="nav">(.*?)</nav>', html, re.S)
links = re.findall(r'<a href="([^"]+)">([^<]+)</a>', nav.group(1)) if nav else []
check("ナビの最後の行き先が、日本語の頁への切り替え（テーマのボタンの直前）",
      bool(links) and links[-1] == ("https://cpsbvbng26-dotcom.vercel.app/notes/golden-window.html", "日本語")
      and nav.group(1).rstrip().endswith("</button>"), repr(links[-1:]))
foot = re.search(r"<footer>(.*?)</footer>", html, re.S)
foot = foot.group(1) if foot else ""
check("頁の下の欄が、運営者の名とライセンスを書いている", "© 2026 Takuya Nemoto" in foot and "CC BY 4.0" in foot)
check("研究の系列のサイトは、創作の系列へつながない（site/ の頁のどれも）",
      all(re.search(r"nusquama|ヌスクァマ|無何有|騎士王国", read(n), re.I) is None
          for n in ["index.html"] + DESIGN_PAGES + [NOT_FOUND]))

print("\n13. デザインに関する法的な扱いの頁（design-legal.html・design-legal.ja.html）")
# 2026-11-22。サイトの見た目の部品（ロゴ・画像・図・配色・配置・書体・外の素材）について、作り手と出所、
# 権利と許諾、関わる条を書いた頁を、英語と日本語で置いた。どちらも手で置いた頁で、生成物ではない。
# 頁が書く事実（ファイルの一覧、大きさ、長方形の数、書体の名、配色の比、許諾）と、引いた条の文を、ここで突き合わせる。
#
# 条の文は verification/design-statutes.json にある。e-Gov 法令 API から 2026-11-22 に取り寄せた写しを、
# 一字一句そのまま写したもの。SHA-256 は、写しの出所が記した値をここにも固めておく（二か所で持つ）。
# 文を直すときは、取り寄せた写しから写し直す。記憶から書かない。
import html as _html

STATUTE_SOURCE_COMMIT = "85dd68091ce06598f55740428d3f1a927448523c"
STATUTE_SHA = {
    "著作権法 第2条第1項第1号": "0f88f7f03918f732cfd781dbb99e4866384cea43aa62ca7e592ba493fe25cdf9",
    "著作権法 第10条第1項第4号": "1b51b19db7203d4b06a5c38df46175351f6ec7066007c6e7fc656dbbb655d184",
    "著作権法 第19条": "e544aec935d1d2d11c98e1f90407335be874712ae20f88a90ea4ff100d8bf042",
    "著作権法 第20条": "fd3c3f660c5bc41d424736d468def4f29f0f65d368f3a8c7be334dc9294e21c9",
    "意匠法 第2条": "1269a8ef67318251bacfa8d8e3e21c068c595c209bcf8b75a44b30c155dfcc0a",
    "意匠法 第23条": "9b5f05ea19a53e1d43811f6be3cf4d311e1e97e59667fdfad36e4ab19917bc3e",
    "商標法 第25条": "e1cd4c4290fdca9b93e0fd753c50e9fe5c6e353650609eb3f0d044c66797c405",
    "不正競争防止法 第2条第1項第1号・第2号": "900c33bc3c6d3b7db92cc13678d27b03af57f0dfdab5215edabbea437fb08484",
    "不正競争防止法 第2条第1項第3号": "252a66b5a09d62812203a03b27a15a835de6216b0b8059f044519dd7b2ad28a9",
    "障害者差別解消法 第2条": "3c5f4837cb368517ec9d236bc43ea08bfdb8b190f228e0f27800623c6a23522f",
    "障害者差別解消法 第8条": "0a058f1f4e2e5968d50afd70576a381409a1e62d19e629036114dea9139934f2",
}
LAW_TITLE = "障害を理由とする差別の解消の推進に関する法律"

try:
    statutes = json.loads(io.open(os.path.join(ROOT, "verification", "design-statutes.json"), encoding="utf-8").read())
except (IOError, ValueError):
    statutes = {}
arts = statutes.get("articles", {})
src = statutes.get("source", {})
check("条の写しの出所が、固めたコミットと取り寄せの日を名乗る",
      src.get("commit") == STATUTE_SOURCE_COMMIT and src.get("fetched") == "2026-11-22"
      and src.get("path") == "verification/statutes-texts.json", repr(src.get("commit")))
check("条の写しが、固めた %d の条をちょうど持つ" % len(STATUTE_SHA), sorted(arts) == sorted(STATUTE_SHA),
      ", ".join(sorted(set(arts) ^ set(STATUTE_SHA))))
bad_sha = [k for k in STATUTE_SHA if k not in arts
           or hashlib.sha256(arts[k].get("text", "").encode("utf-8")).hexdigest() != STATUTE_SHA[k]
           or arts[k].get("sha256") != STATUTE_SHA[k]]
check("写しの条の文が、どれも固めた SHA-256 と合う", not bad_sha, ", ".join(bad_sha))
check("障害者差別解消法の写しが、e-Gov の答えた正式の名を持つ",
      all(arts.get(k, {}).get("title") == LAW_TITLE for k in STATUTE_SHA if k.startswith("障害者差別解消法")))


def inner(text):
    """タグを外し、文字参照を戻す。"""
    return _html.unescape(re.sub(r"<[^>]+>", "", text))


def tokens_all(block):
    return dict(re.findall(r"--([a-z-]+):\s*(#[0-9a-fA-F]{3,6})\s*;", block))


def font_vars(text):
    return dict(re.findall(r"--font-(sans|serif|mono):\s*([^;]+);", text))


index_fonts = font_vars(css)
index_light = tokens_all(light.group(1)) if light else {}
index_dark = tokens_all(dark.group(1)) if dark else {}
LICENSE_CC = read(os.path.join("..", "lessons", "LICENSE"))
README_TXT = read(os.path.join("..", "README.md"))
IMAGE_EXT = (".svg", ".png", ".ico", ".jpg", ".jpeg", ".gif", ".webp", ".avif")
FONT_EXT = (".woff", ".woff2", ".ttf", ".otf", ".eot")
site_files = sorted(f for f in os.listdir(SITE) if not f.startswith("."))
image_files = sorted(f for f in site_files if f.endswith(IMAGE_EXT))
part_files_expected = sorted(f for f in site_files if f.endswith(IMAGE_EXT + (".html", ".css", ".js") + FONT_EXT))

# 比はトップの頁の配色から数え直す。頁は、その最小の値を名乗る。
pairs = [ratio(t[tok], t[base]) for _, t in themes for base in ("bg", "card")
         for tok in ("text", "muted", "faint", "accent") if t.get(base) and t.get(tok)]
min_ratio = "%.2f" % (int(min(pairs) * 100) / 100.0) if pairs else ""

check("site/ に書体のファイルが無く、トップの頁が @font-face を持たない",
      not [f for f in site_files if f.endswith(FONT_EXT)] and "@font-face" not in html)
check("トップの頁が、動きを減らす設定で動きを止める",
      re.search(r"@media \(prefers-reduced-motion: reduce\)\s*\{\s*\*, \*::before, \*::after\s*\{[^}]*animation-duration:\s*\.01ms[^}]*transition-duration:\s*\.01ms", css) is not None)
check("トップの頁に、本文へ飛ぶリンクと、焦点の輪郭がある",
      '<a class="skip-link" href="#main">' in html and '<main id="main"' in html
      and re.search(r":focus-visible\s*\{[^}]*outline:\s*2px solid", css) is not None)
check("トップの頁が、本文のリンクを下線でも示す",
      re.search(r"\.notes-list a[^{]*\{[^}]*text-decoration:\s*underline", css) is not None
      and re.search(r"\.foot a[^{]*\{[^}]*text-decoration:\s*underline", css) is not None)
check("トップの頁の図が、状態を文でも書く（aria-live の段落）",
      '<p id="gw-state" aria-live="polite"></p>' in html and "TXT.window" in html)
index_imgs = re.findall(r"<img\b[^>]*>", html)
check("トップの頁の画像の要素は、ロゴの一つだけ",
      len(index_imgs) == 1 and 'src="./favicon.svg"' in index_imgs[0], "%d 個" % len(index_imgs))

# ロゴの中身。題と長方形だけで組み、文字も書体も持たない。
svg_tags = re.findall(r"<([a-zA-Z][\w:-]*)", svg)
rects = svg_tags.count("rect")
check("ロゴ（favicon.svg）の要素が svg・title・rect だけ", set(svg_tags) <= {"svg", "title", "rect"}, ",".join(sorted(set(svg_tags))))


def span(page, ident):
    m = re.search(r'<span id="%s">([^<]*)</span>' % re.escape(ident), page)
    return m.group(1) if m else None


for name in DESIGN_PAGES:
    lang = "ja" if name.endswith(".ja.html") else "en"
    page = read(name)
    tag = "%s：" % name
    check(tag + "置いてあり、言語が %s" % lang, bool(page) and ('<html lang="%s">' % lang) in page)
    check(tag + "canonical が自分の URL を一つだけ指す",
          re.findall(r'<link rel="canonical" href="([^"]+)">', page) == [URL + name])
    alt = sorted(re.findall(r'<link rel="alternate" hreflang="(ja|en)" href="([^"]+)">', page))
    check(tag + "言語の版を、英語と日本語の二つで名指す",
          alt == [("en", URL + "design-legal.html"), ("ja", URL + "design-legal.ja.html")], repr(alt))
    other = "design-legal.ja.html" if lang == "en" else "design-legal.html"
    check(tag + "トップの頁と、もう一つの言語の頁へつなぐ",
          '<a href="./">' in page and ('<a href="./%s"' % other) in page)
    pcsp = re.search(r'<meta http-equiv="Content-Security-Policy" content="([^"]+)">', page)
    pcsp = pcsp.group(1) if pcsp else ""
    pstyles = re.findall(r"<style[^>]*>(.*?)</style>", page, re.S)
    pcss = "\n".join(pstyles)
    check(tag + "CSP が default-src 'none' から始まり、'unsafe-inline' を使わない",
          pcsp.startswith("default-src 'none'") and "'unsafe-inline'" not in pcsp)
    check(tag + "台本を持たず、外のスタイルシートも読まない",
          "<script" not in page and not re.search(r'<link[^>]+rel="stylesheet"', page))
    check(tag + "インラインのスタイルが CSP のハッシュと合う",
          len(pstyles) == 1 and sha(pstyles[0]) in pcsp)
    pvp = re.findall(r'<meta name="viewport" content="([^"]+)">', page)
    check(tag + "viewport が拡大を止めていない",
          len(pvp) == 1 and "user-scalable=no" not in pvp[0].replace(" ", "") and "maximum-scale" not in pvp[0])
    check(tag + "文字の大きさを px で決めず、320px を超える px の幅も持たない",
          not re.findall(r"font-size:\s*[\d.]+px", pcss)
          and not [w for w in re.findall(r"(?<![-\w])(?:min-)?width:\s*([\d.]+)px", pcss) if float(w) > 320])
    check(tag + "表が頁を押し広げず、自分の中で横へ流れる",
          re.search(r"\.prose table\s*\{[^}]*max-width:\s*100%[^}]*overflow-x:\s*auto", pcss) is not None)
    pl = re.search(r":root\s*\{(.*?)\}", pcss, re.S)
    pd = re.search(r'@media \(prefers-color-scheme: dark\)\s*\{\s*:root:not\(\[data-theme="light"\]\)\s*\{(.*?)\}', pcss, re.S)
    pl, pd = (tokens_all(pl.group(1)) if pl else {}), (tokens_all(pd.group(1)) if pd else {})
    need = ("bg", "card", "text", "muted", "faint", "accent")
    check(tag + "配色の値が、明るい側も暗い側もトップの頁と同じ",
          all(k in pl and k in pd for k in need)
          and all(index_light.get(k) == v for k, v in pl.items())
          and all(index_dark.get(k) == v for k, v in pd.items()),
          "明 %s / 暗 %s" % (sorted(k for k, v in pl.items() if index_light.get(k) != v),
                           sorted(k for k, v in pd.items() if index_dark.get(k) != v)))
    check(tag + "書体の名の並びがトップの頁と同じで、@font-face も url( も持たない",
          font_vars(pcss) == index_fonts and len(index_fonts) == 3 and "@font-face" not in pcss and "url(" not in pcss)
    check(tag + "動きを減らす設定で動きを止め、本文へ飛ぶリンクと焦点の輪郭がある",
          "@media (prefers-reduced-motion: reduce)" in pcss and '<a class="skip-link" href="#main">' in page
          and '<main id="main"' in page and re.search(r":focus-visible\s*\{[^}]*outline:\s*2px solid", pcss) is not None)
    check(tag + "本文と頁の下の欄のリンクを下線で示す",
          re.search(r"\.prose a, \.foot a\s*\{[^}]*text-decoration:\s*underline", pcss) is not None)
    pimgs = re.findall(r"<img\b[^>]*>", page)
    check(tag + "画像の要素はロゴの一つだけで、代替文を持つ",
          len(pimgs) == 1 and 'src="./favicon.svg"' in pimgs[0] and 'alt="The golden-window conjecture"' in pimgs[0])
    pfoot = re.search(r"<footer>(.*?)</footer>", page, re.S)
    pfoot = pfoot.group(1) if pfoot else ""
    check(tag + "頁の下の欄が、運営者の名と CC BY 4.0 を書く", "© 2026 Takuya Nemoto · CC BY 4.0" in pfoot)

    # 引いた条。全文を置いたものは一字一句同じ、切り出したものは写しの部分文字列。
    quotes = re.findall(r'<blockquote lang="([a-z]+)" data-statute="([^"]+)" data-cut="(whole|excerpt)"><p>(.*?)</p></blockquote>',
                        page, re.S)
    wrong = []
    for qlang, key, cut, body in quotes:
        full = arts.get(key, {}).get("text", "")
        body = _html.unescape(body)
        if qlang != "ja" or not full or (cut == "whole" and body != full) \
                or (cut == "excerpt" and (body not in full or len(body) >= len(full))):
            wrong.append(key)
    check(tag + "置いた条の文が、写しと一字一句同じか、写しから切り出したもの", bool(quotes) and not wrong, ", ".join(wrong))
    check(tag + "写しの条を、どれも一度ずつ引く", sorted(k for _, k, _, _ in quotes) == sorted(STATUTE_SHA),
          "%d 回" % len(quotes))
    check(tag + "引く条の数を、実際の数で名乗る", span(page, "statute-count") == str(len(quotes)), repr(span(page, "statute-count")))
    cut_note = "切り出しました" if lang == "ja" else "cut to"
    unmarked = [k for k in re.findall(r'<p>([^\n]*)</p>\n<blockquote lang="ja" data-statute="([^"]+)" data-cut="excerpt">', page)
                if cut_note not in k[0]]
    n_ex = len([1 for _, _, c, _ in quotes if c == "excerpt"])
    check(tag + "切り出した条の %d か所が、どれも直前の文で切り出したところを書く" % n_ex,
          n_ex == 4 and not unmarked
          and len(re.findall(r'<p>[^\n]*</p>\n<blockquote lang="ja" data-statute="[^"]+" data-cut="excerpt">', page)) == n_ex)
    rows = re.findall(r"<tr><td>([^<]+)</td><td>([^<]+)</td><td><code>(\w+)</code></td><td><code>([0-9a-f]{64})</code></td></tr>", page)
    check(tag + "引いた条の表が、写しの法令名・条・法令 ID・SHA-256 と同じ",
          rows == [(v.get("title"), k.split(" ", 1)[1], v.get("law_id"), v.get("sha256")) for k, v in arts.items()],
          "%d 行" % len(rows))
    lic = re.findall(r'<blockquote lang="en" data-license="(\w+)"><p>(.*?)</p></blockquote>', page)
    check(tag + "CC BY 4.0 の法的な文から引いた二つの文が、lessons/LICENSE の文と同じ",
          [k for k, _ in lic] == ["moral", "trademark"]
          and all(_html.unescape(t) in LICENSE_CC for _, t in lic) and LICENSE_CC.startswith("Creative Commons Attribution 4.0"))

    # 部品の一覧。表のファイルと、表の外に挙げたファイルを合わせると、site/ のファイルと過不足なく一致する。
    parts = re.search(r'<table id="parts-table">(.*?)</table>', page, re.S)
    part_rows = re.findall(r"<tr><td>[^<]*</td><td><code>([^<]+)</code></td><td>.*?</td><td>([^<]*)</td>", parts.group(1)) if parts else []
    part_files = [f for f, _ in part_rows]
    others = re.search(r'<p id="others">(.*?)</p>', page, re.S)
    other_files = [f for f in re.findall(r"<code>([^<]+)</code>", others.group(1)) if f != "site/"] if others else []
    check(tag + "部品の表のファイルが、site/ の頁と画像と過不足なく一致する",
          sorted(part_files) == part_files_expected and len(set(part_files)) == len(part_files),
          "表 %s / site %s" % (sorted(set(part_files) - set(part_files_expected)), sorted(set(part_files_expected) - set(part_files))))
    check(tag + "表のファイルと表の外に挙げたファイルを合わせると、site/ のファイルと過不足なく一致する",
          sorted(part_files + other_files) == site_files and not set(part_files) & set(other_files),
          ", ".join(sorted(set(site_files) ^ set(part_files + other_files))))
    check(tag + "名乗るファイルの数と、表の部品の数が、実際の数と合う",
          span(page, "file-count") == str(len(site_files)) and span(page, "part-count") == str(len(part_files)),
          "%s・%s" % (span(page, "file-count"), span(page, "part-count")))
    check(tag + "名乗る画像の数が、site/ の画像の数と合う", span(page, "image-count") == str(len(image_files)),
          "%s / %d" % (span(page, "image-count"), len(image_files)))
    check(tag + "ロゴの長方形の数が、favicon.svg の数と合う", span(page, "logo-rects") == str(rects), "%s / %d" % (span(page, "logo-rects"), rects))
    check(tag + "favicon.ico の大きさが、中の三枚と合う",
          bool(ico_sizes) and span(page, "ico-sizes") == ("・" if lang == "ja" else ", ").join(str(w) for w, _ in ico_sizes) and all(w == h for w, h in ico_sizes))
    for img in ("favicon-192.png", "apple-touch-icon.png", "og.png"):
        sz = png_size(raw(img))
        check(tag + "%s の大きさが、名乗る一辺と合う正方形" % img,
              sz is not None and sz[0] == sz[1] and span(page, "size-" + img) == str(sz[0]), "%s / %r" % (span(page, "size-" + img), sz))
    fl = re.search(r'<ul id="fonts">(.*?)</ul>', page, re.S)
    fonts_listed = [_html.unescape(f) for f in re.findall(r"<li>[^<]*<code>([^<]+)</code></li>", fl.group(1))] if fl else []
    check(tag + "名を並べた書体が、トップの頁の font-family の三つと同じ",
          fonts_listed == [index_fonts.get(k) for k in ("sans", "serif", "mono")], repr(fonts_listed[:1]))
    check(tag + "名乗る配色の比の最小が、トップの頁の配色から数え直した値と合う",
          span(page, "min-ratio") == min_ratio and float(min_ratio) >= 4.5, "%s / %s" % (span(page, "min-ratio"), min_ratio))

    # 運営者の側の理解であって、助言ではないこと。弁護士の確認を受けていないこと。
    must = ({"ja": ["法的な助言ではありません。", "この頁は、弁護士の確認を受けていません。",
                    "e-Gov 法令 API から 2026-11-22 に取り寄せた写しのとおりに引きます。",
                    "登録の有無を、特許庁の記録で確かめてはいません。", "似たものが無いかは、確かめていません。",
                    "運営者が、この法の「事業者」に当たるかどうかは、条の文からは決まりません。",
                    "窓の枠の中に、穴を挟んで二つに分かれる帯を三段重ねた図", "部品を変えたら、この頁と検査を同じ PR で直します。"],
             "en": ["It is not legal advice.", "No lawyer has reviewed this page.",
                    "Articles are quoted as fetched from the e-Gov law API on 2026-11-22.",
                    "The English after it is a summary, not a translation.",
                    "Registration has not been checked in the Japan Patent Office’s records.",
                    "Whether something similar exists has not been checked.",
                    "Whether the operator is a business operator under this Act is not settled by the text of the articles.",
                    "When a part changes, this page and its check are changed in the same pull request."]}[lang])
    missing = [m for m in must if m not in page]
    check(tag + "決めた文を %d 持つ（助言ではない・弁護士の確認なし・取り寄せの日・確かめていないこと）" % len(must),
          not missing, missing[0] if missing else "")
    if lang == "en":
        gist = re.findall(r'</blockquote>\n<p class="gist">Summary, not a translation: ', page)
        check(tag + "日本語の条の文のあとに、どれも「訳ではなく要旨」と断った英語を置く", len(gist) == len(quotes), "%d / %d" % (len(gist), len(quotes)))
    else:
        body_txt = inner(page[page.find("<main"):])
        first = body_txt.find("障害者差別解消法")
        check(tag + "障害者差別解消法を、初めに正式の名で書く",
              first > 0 and body_txt.find(LAW_TITLE + "（以下、障害者差別解消法）") == first - len(LAW_TITLE + "（以下、"))
        check(tag + "ロゴの作りの説明が、README と同じ語で書く",
              "ロゴ（`site/favicon.svg`）は、窓の枠の中に、穴を挟んで二つに分かれる帯を三段重ねた図です。" in README_TXT)
    check(tag + "許諾が、README のライセンスの表のとおり（頁は CC BY 4.0、そのほかは MIT）",
          "| [`site/`](site/) の頁 | CC BY 4.0 | 頁の末尾の表示。" in README_TXT and "| 全体（次の行以降を除く） | MIT |" in README_TXT
          and bool(part_rows) and all(r == ({"ja": "頁の末尾の表示により CC BY 4.0", "en": "CC BY 4.0, by the notice at its foot"}[lang]
                                            if f.endswith(".html") else
                                            {"ja": "リポジトリの LICENSE により MIT", "en": "MIT, by the repository’s LICENSE"}[lang])
                                       for f, r in part_rows))

print("\n14. 予想のサイトの意匠（帯・渦・飾り・ロゴの二色）")
# 2026-11-23。予想のサイトだけの意匠を、researcher-profile の golden-window-design.js が描く。決まりはその README の「予想のサイトの意匠」にある。
# ここでは、頁に入った形を、φ の式から数え直す。帯と飾りの各段は、区間の両端の二つを長さの 1/φ² ずつ残す操作を n 回当てた 2^n 個の区間である。
# ロゴの二色は favicon.svg の塗りと同じで、明暗どちらでも同じ。デザインに関する法的な扱いの頁は、帯と題の下の飾りをトップの頁から写す。
PHI = (1 + 5 ** 0.5) / 2
KEEP = 2 - PHI


def cantor(n):
    cur = [(0.0, 1.0)]
    for _ in range(n):
        nxt = []
        for a, b in cur:
            d = (b - a) * KEEP
            nxt += [(a, a + d), (b - d, b)]
        cur = nxt
    return cur


def cantor_rows(svgtext):
    """viewBox の幅と、y ごとに並べた区間の行を返す。墨の地の長方形（class を持つもの）は除く。"""
    vb = re.search(r'viewBox="([-\d.]+) ([-\d.]+) ([\d.]+) ([\d.]+)"', svgtext)
    by = {}
    for x, y, w in re.findall(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="[\d.]+"/>', svgtext):
        by.setdefault(float(y), []).append((float(x), float(w)))
    return (float(vb.group(3)) if vb else 0), [sorted(by[y]) for y in sorted(by)]


def rows_ok(svgtext):
    """各行が、ある n について cantor(n) を幅に伸ばしたものと 0.006 の内で同じか。段は上から一つずつ深くなる。"""
    width, rows = cantor_rows(svgtext)
    if not rows or width <= 0:
        return False
    ns = []
    for row in rows:
        n = len(row).bit_length() - 1
        ref = cantor(n)
        if len(row) != 2 ** n or any(abs(x - a * width) > 0.006 or abs(w - (b - a) * width) > 0.006 for (x, w), (a, b) in zip(row, ref)):
            return False
        ns.append(n)
    return all(ns[i + 1] == ns[i] + 1 for i in range(len(ns) - 1))


band = re.findall(r'<svg class="gw-band"[^>]*>.*?</svg>', html, re.S)
seal = re.findall(r'<svg class="gw-seal"[^>]*>.*?</svg>', html, re.S)
orn_long = re.findall(r'<svg class="gw-orn gw-orn-long"[^>]*>.*?</svg>', html, re.S)
orn_short = re.findall(r'<svg class="gw-orn gw-orn-short"[^>]*>.*?</svg>', html, re.S)
heads = html.count('<div class="sec-head reveal">')
check("トップの頁に、帯が一本（頁の上の欄の先頭）・渦が一つ・題の下の飾りが一つ・節の見出しごとに飾りが一つ（%d）ある" % heads,
      len(band) == 1 and re.search(r'<header>\n  <svg class="gw-band"', html) is not None and len(seal) == 1
      and len(orn_long) == 1 and len(orn_short) == heads and heads > 0)
check("帯と飾りの各段が、両端の二つを長さの 1/φ² ずつ残す 2^n 個の区間で、段は上から一つずつ深くなる（φ の式から数え直す）",
      bool(band) and bool(orn_long) and bool(orn_short)
      and rows_ok(re.sub(r'<rect width="[^"]*" height="[^"]*" class="gw-band-ink"/>', "", band[0]))
      and rows_ok(orn_long[0]) and all(rows_ok(o) for o in orn_short))
sq = [float(w) for w in re.findall(r'<rect x="[\d.]+" y="[\d.]+" width="([\d.]+)" height="\1" class="gw-seal-sq"', seal[0])] if seal else []
svb = re.search(r'viewBox="([-\d.]+) ([-\d.]+) ([\d.]+) ([\d.]+)"', seal[0]) if seal else None
check("渦の正方形の辺が 1/φ ずつ縮み、外の長方形の縦と横の比が φ である",
      len(sq) >= 4 and all(abs(sq[i + 1] / sq[i] - 1 / PHI) < 0.002 for i in range(len(sq) - 1))
      and svb is not None and abs((float(svb.group(4)) - 1) / (float(svb.group(3)) - 1) - PHI) < 0.001,
      "%d 個" % len(sq))
deco = band + seal + orn_long + orn_short
check("帯・渦・飾りが、長方形と道だけで描かれ、字も外への参照も持たず、読み上げない",
      bool(deco) and all(set(re.findall(r"<([a-zA-Z]+)", d)) <= {"svg", "g", "rect", "path"} and 'aria-hidden="true"' in d
                         and not re.search(r"href|https?:|<text|font", d) for d in deco))

# ロゴの二色。favicon.svg の地（rx を持つ長方形の塗り）と枠（stroke）の色と同じで、明暗どちらでも同じ一組だけを置く。
logo_ink = re.search(r'<rect width="48" height="48" rx="\d+" fill="(#[0-9A-Fa-f]{6})"/>', svg)
logo_gold = re.search(r'stroke="(#[0-9A-Fa-f]{6})"', svg)
# 紙の段は二色を #000 に替えるが、六桁の値だけを拾うので、ここには入らない。
gw_tok = re.findall(r"--gw-(ink|gold):\s*(#[0-9a-fA-F]{6});", css)
check("意匠の色（--gw-ink・--gw-gold）が、ロゴ（favicon.svg）の墨と金と同じで、明暗で一組だけ",
      logo_ink is not None and logo_gold is not None
      and sorted((k, v.lower()) for k, v in gw_tok) == sorted([("ink", logo_ink.group(1).lower()), ("gold", logo_gold.group(1).lower())]),
      repr(gw_tok))
gw = dict((k, v) for k, v in gw_tok)
r_gold = ratio(gw["gold"], gw["ink"]) if "gold" in gw and "ink" in gw else 0
check("帯の金と墨の比が 3:1 以上（字でない図形）", r_gold >= 3, "%.2f:1" % r_gold)
bars = sorted({float(w) for w in re.findall(r'<rect x="[\d.]+" y="[\d.]+" width="([\d.]+)" height="6"', svg)}, reverse=True)
check("ロゴの帯の段の比は 0.38 に丸めた 1/φ² で、意匠は丸めない 1/φ² を使う",
      len(bars) == 3 and all(round(bars[i + 1] / bars[i], 2) == 0.38 for i in range(2)) and abs(0.38 - KEEP) < 0.005,
      ", ".join("%.4g" % b for b in bars))
check("紙では、帯と渦を刷らない",
      re.search(r"@media print \{[^@]*\.gw-band, \.hero \.gw-seal, \.hero::after \{ display: none; \}", css) is not None)
copies = []
for name in DESIGN_PAGES:
    page = read(name)
    pcss = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", page, re.S))
    ptok = re.findall(r"--gw-(ink|gold):\s*(#[0-9a-fA-F]{6});", pcss)
    if not (band and orn_long and page.count(band[0]) == 1 and re.search(r'<header>\n  <svg class="gw-band"', page)
            and page.count(orn_long[0]) == 1 and re.search(r"</h1>\n<svg class=\"gw-orn gw-orn-long\"", page)
            and sorted(ptok) == sorted(gw_tok) and re.search(r"@media print \{[^@]*\.gw-band \{ display: none; \}", pcss)):
        copies.append(name)
check("デザインに関する法的な扱いの頁（英日）が、帯と題の下の飾りをトップの頁と一字一句同じに写し、同じ二色を置き、紙では帯を刷らない",
      not copies, ", ".join(copies))

# 2026-11-24。IndexNow。鍵は site/<鍵>.txt で、Vercel はこれをサイトの根で配る。中身は鍵そのもので、秘密ではない。
# 知らせるのは tools/indexnow.js で、.github/workflows/indexnow.yml が site/sitemap.xml の変わった push のあとに回す。
# Google は IndexNow を読まず、sitemap を読む。
print("\n15. IndexNow の鍵・ワークフロー・知らせる先")
KEY_RE = re.compile(r"^[0-9a-f]{32}\.txt$")
keys = sorted(f for f in os.listdir(SITE) if KEY_RE.match(f))
key = keys[0][:-4] if len(keys) == 1 else ""
check("site/ に、16 進 32 字の名の鍵のファイルが一つだけある", len(keys) == 1, repr(keys))
check("鍵のファイルの中身が、名の鍵そのもの（改行も空白も持たない）", bool(key) and raw(keys[0]) == key.encode("ascii"))
stray = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", "node_modules")]
    stray += [os.path.relpath(os.path.join(dirpath, f), ROOT) for f in filenames
              if KEY_RE.match(f) and os.path.abspath(dirpath) != SITE]
check("鍵のファイルは配られる根（site/）にあり、配られない場所にほかの鍵のファイルが無い", not stray, ", ".join(stray))
INX = os.path.join(ROOT, ".github", "workflows", "indexnow.yml")
inx = io.open(INX, encoding="utf-8").read() if os.path.isfile(INX) else ""
check("ワークフロー indexnow.yml が、main への push の site/sitemap.xml だけで起き、手で起こすときに all を取る",
      re.search(r"^on:\n  push:\n    branches: \[main\]\n    paths: \[site/sitemap\.xml\]\n  workflow_dispatch:\n    inputs:\n      all:\n", inx, re.M) is not None)
check("ワークフローが tools/indexnow.js を回し、前の head と all を渡す",
      re.search(r"^      - run: node tools/indexnow\.js\n        env:\n          BEFORE: \$\{\{ github\.event\.before \}\}\n          ALL: \$\{\{ inputs\.all \}\}\n", inx, re.M) is not None)
TOOL = os.path.join(ROOT, "tools", "indexnow.js")
tool = io.open(TOOL, encoding="utf-8").read() if os.path.isfile(TOOL) else ""
tool_base = re.findall(r"^const BASE = '([^']+)';$", tool, re.M)
check("tools/indexnow.js の知らせる先が一つで、配信先（canonical）と同じ", tool_base == [URL], repr(tool_base))
check("tools/indexnow.js が site/ の鍵と site/sitemap.xml を読む",
      "const SITE = path.join(ROOT, 'site');" in tool and "path.join(SITE, 'sitemap.xml')" in tool
      and "at + ':site/sitemap.xml'" in tool and "fs.readdirSync(SITE)" in tool)
hosts = sorted({re.sub(r"^https://([^/]+)/.*$", r"\1", u) for u in re.findall(r"<loc>([^<]+)</loc>", sitemap)})
check("sitemap.xml の頁のホストが一つで、tools/indexnow.js の知らせる先のホストと同じ",
      bool(tool_base) and hosts == [re.sub(r"^https://([^/]+)/$", r"\1", tool_base[0])], repr(hosts))

# 2026-11-24。Wayback Machine。写しはこちらから消せないので、頼むのは全文を読んだ頁（READ）だけにする。
# 手で起こすときだけ動き、読むだけの権限で、site/sitemap.xml の頁を頼み、その日の写しを確かめる。
print("\n16. Wayback Machine に写しを頼むワークフロー")
WBY = os.path.join(ROOT, ".github", "workflows", "wayback.yml")
wby = io.open(WBY, encoding="utf-8").read() if os.path.isfile(WBY) else ""
wb_on = re.search(r"^on:\n((?:  .*\n|\s*\n)*)", wby, re.M)
check("wayback.yml があり、手で起こすとき（workflow_dispatch）だけ動く",
      bool(wby) and wb_on is not None and re.findall(r"^  (\w+):", wb_on.group(1), re.M) == ["workflow_dispatch"])
wb_perm = re.search(r"^permissions:\n((?:  \S[^\n]*\n)+)", wby, re.M)
check("wayback.yml の権限が contents: read だけで、仕事の単位で広げない",
      wb_perm is not None and wb_perm.group(1) == "  contents: read\n"
      and not re.search(r"^    permissions:", wby, re.M) and not re.search(r":\s*write\b|write-all", wby))
check("wayback.yml が site/sitemap.xml の頁を読み、配信先の頁だけを頼む",
      'open("site/sitemap.xml", encoding="utf-8")' in wby and ('BASE = "%s"' % URL) in wby
      and "web.archive.org/save/" in wby and "if u not in READ or not u.startswith(BASE)" in wby)
check("wayback.yml が、その日の写しを archive.org/wayback/available で確かめ、確かめられないものがあれば落ちる",
      "https://archive.org/wayback/available?timestamp=%s&url=%s" in wby
      and 'c["timestamp"].startswith(today)' in wby
      and "if failed or unread:\n              raise SystemExit(" in wby)
wb_read = re.search(r"^          READ = \[\n((?:              \"[^\"]+\",\n)+)          \]\n", wby, re.M)
wb_read = re.findall(r'"([^"]+)"', wb_read.group(1)) if wb_read else []
check("全文を読んだ頁（READ）が、sitemap.xml の頁とちょうど同じ（読んでいない頁は頼まない）",
      wb_read == re.findall(r"<loc>([^<]+)</loc>", sitemap), repr(wb_read))
pdf_links = [n for n in ["index.html"] + DESIGN_PAGES if re.search(r'href="[^"]*\.pdf(?:[#?][^"]*)?"', read(n), re.I)]
check("サイトの頁が PDF を張っていない（張れば、Wayback に頼むかを読んで決め直す）", not pdf_links, ", ".join(pdf_links))

# 2026-11-25。サイトに無い所在には、Vercel が site/404.html を状態 404 で返す（設定は置かない。Vercel の決まり）。
# それまでは Vercel の素の NOT_FOUND が出ていた。頁は手で置いたもので、生成物ではない。
# Vercel が返すのは 404.html の一つだけなので、英語と日本語を一つの頁に置く（言語ごとに頁を分けると、片方は 404 の答えに出ない）。
# 書くのは、頁が無いことと、トップの頁へのつなぎだけ。入れ子の所在（/a/b/c）でも切れないよう、つなぎと素材は根から書く。
print("\n17. サイトに無い所在の頁（404.html）")
nf = read(NOT_FOUND)
check("404.html がある", bool(nf))
check("404.html の言語が en で、日本語の節を lang=\"ja\" で一つ持つ",
      '<html lang="en">' in nf and nf.count('<section lang="ja">') == 1)
check("404.html を索引に載せず（noindex が一つ）、canonical も言語の版も名乗らない",
      re.findall(r'<meta name="robots" content="([^"]+)">', nf) == ["noindex"]
      and 'rel="canonical"' not in nf and 'rel="alternate"' not in nf)
nmain = re.search(r'<main id="main"[^>]*>(.*?)</main>', nf, re.S)
nmain = nmain.group(1) if nmain else ""
check("404.html の本文が、頁が無いことと、トップの頁へのつなぎだけを書く（英語と日本語）",
      [inner(x).strip() for x in re.findall(r"<(?:h1|h2|p)>(.*?)</(?:h1|h2|p)>", nmain, re.S)]
      == ["Page not found", "There is no page at this address.", "Go to the top page",
          "頁が見つかりません", "このアドレスに頁はありません。", "トップの頁へ"])
nhref = re.findall(r'\bhref="([^"]*)"', nf)
nsrc = re.findall(r'\bsrc="([^"]*)"', nf)
check("404.html のつなぎはトップの頁（/）と本文へ飛ぶリンクだけで、素材は根から読む（入れ子の所在でも切れない）",
      sorted(set(nhref)) == ["#main", "/", "/favicon.ico", "/favicon.svg"]
      and nmain.count('<a href="/">') == 2 and nsrc == ["/favicon.svg"], repr(sorted(set(nhref))))
ncsp = re.search(r'<meta http-equiv="Content-Security-Policy" content="([^"]+)">', nf)
ncsp = ncsp.group(1) if ncsp else ""
nstyles = re.findall(r"<style[^>]*>(.*?)</style>", nf, re.S)
ncss = "\n".join(nstyles)
check("404.html の CSP が default-src 'none' から始まり、'unsafe-inline' を使わず、一つのスタイルをハッシュで許す",
      ncsp.startswith("default-src 'none'") and "'unsafe-inline'" not in ncsp
      and len(nstyles) == 1 and sha(nstyles[0]) in ncsp)
check("404.html が台本を持たず、外のスタイルシートも読まず、外へつながない",
      "<script" not in nf and not re.search(r'<link[^>]+rel="stylesheet"', nf) and "http://" not in nf
      and not re.search(r'(?:href|src)="https?:', nf))
nvp = re.findall(r'<meta name="viewport" content="([^"]+)">', nf)
check("404.html の viewport が拡大を止めず、文字の大きさを px で決めず、320px を超える px の幅も持たない",
      len(nvp) == 1 and "user-scalable=no" not in nvp[0].replace(" ", "") and "maximum-scale" not in nvp[0]
      and not re.findall(r"font-size:\s*[\d.]+px", ncss)
      and not [w for w in re.findall(r"(?<![-\w])(?:min-)?width:\s*([\d.]+)px", ncss) if float(w) > 320])
nl = re.search(r":root\s*\{(.*?)\}", ncss, re.S)
nd = re.search(r'@media \(prefers-color-scheme: dark\)\s*\{\s*:root:not\(\[data-theme="light"\]\)\s*\{(.*?)\}', ncss, re.S)
nl, nd = (tokens_all(nl.group(1)) if nl else {}), (tokens_all(nd.group(1)) if nd else {})
check("404.html の配色の値が、明るい側も暗い側もトップの頁と同じ",
      all(k in nl and k in nd for k in ("bg", "card", "text", "muted", "faint", "accent"))
      and all(index_light.get(k) == v for k, v in nl.items()) and all(index_dark.get(k) == v for k, v in nd.items()),
      "明 %s / 暗 %s" % (sorted(k for k, v in nl.items() if index_light.get(k) != v),
                       sorted(k for k, v in nd.items() if index_dark.get(k) != v)))
check("404.html の書体の名の並びがトップの頁と同じで、@font-face も url( も持たない",
      font_vars(ncss) == index_fonts and "@font-face" not in ncss and "url(" not in ncss)
check("404.html が、帯と題の下の飾りをトップの頁と一字一句同じに写し、同じ二色を置き、紙では帯を刷らない",
      bool(band) and bool(orn_long) and nf.count(band[0]) == 1 and re.search(r'<header>\n  <svg class="gw-band"', nf) is not None
      and nf.count(orn_long[0]) == 1 and re.search(r'</h1>\n<svg class="gw-orn gw-orn-long"', nf) is not None
      and sorted(re.findall(r"--gw-(ink|gold):\s*(#[0-9a-fA-F]{6});", ncss)) == sorted(gw_tok)
      and re.search(r"@media print \{[^@]*\.gw-band \{ display: none; \}", ncss) is not None)
nimgs = re.findall(r"<img\b[^>]*>", nf)
check("404.html の画像の要素はロゴの一つだけで、代替文を持つ",
      len(nimgs) == 1 and 'alt="The golden-window conjecture"' in nimgs[0])
check("404.html に、本文へ飛ぶリンクと焦点の輪郭があり、動きを減らす設定で動きを止める",
      '<a class="skip-link" href="#main">' in nf and '<main id="main"' in nf
      and re.search(r":focus-visible\s*\{[^}]*outline:\s*2px solid", ncss) is not None
      and "@media (prefers-reduced-motion: reduce)" in ncss
      and re.search(r"\.prose a, \.foot a\s*\{[^}]*text-decoration:\s*underline", ncss) is not None)
nfoot = re.search(r"<footer>(.*?)</footer>", nf, re.S)
check("404.html の頁の下の欄が、運営者の名と CC BY 4.0 を書く",
      nfoot is not None and "© 2026 Takuya Nemoto · CC BY 4.0" in nfoot.group(1))
check("vercel.json が 404 の頁を経路で指さない（Vercel の決まりで、根の 404.html を返す）",
      "404" not in read("vercel.json") and "routes" not in vcfg and "rewrites" not in vcfg)

print("\n" + "-" * 58)
if failures:
    print("%d 件が通り、%d 件が通りませんでした。" % (passed, len(failures)))
    sys.exit(1)
print("%d 件すべて通りました。" % passed)
