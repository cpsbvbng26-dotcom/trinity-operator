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

print("\n" + "-" * 58)
if failures:
    print("%d 件が通り、%d 件が通りませんでした。" % (passed, len(failures)))
    sys.exit(1)
print("%d 件すべて通りました。" % passed)
