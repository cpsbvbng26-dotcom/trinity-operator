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
check("sitemap.xml の loc が canonical と同じ",
      re.findall(r"<loc>([^<]+)</loc>", sitemap) == [URL])
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

print("\n5. 予想を予想のまま出している")
for phrase in ("It has not been proved.",
               "It has not been checked against the literature.",
               "It is a preprint and has not been peer-reviewed."):
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
for name, t in themes:
    for base in ("bg", "card"):
        for tok in ("text", "muted", "faint", "accent"):
            if t.get(base) and t.get(tok):
                r = ratio(t[tok], t[base])
                check("%s --%s / --%s が 4.5:1 以上" % (name, tok, base), r >= 4.5, "%.2f:1" % r)
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
check("研究の系列のサイトは、創作の系列へつながない", "nusquama" not in html.lower())

print("\n" + "-" * 58)
if failures:
    print("%d 件が通り、%d 件が通りませんでした。" % (passed, len(failures)))
    sys.exit(1)
print("%d 件すべて通りました。" % passed)
