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
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
URL = "https://golden-window.vercel.app/"
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
check("rel=\"icon\" が favicon.svg を指す", icons == ["./favicon.svg"], repr(icons))
vb = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg)
check("ロゴが正方形で、一辺が 48 の倍数",
      bool(vb) and vb.group(1) == vb.group(2) and int(vb.group(1)) % 48 == 0,
      vb.group(0) if vb else "viewBox が無い")
check("ロゴが外から何も読まない", "href" not in svg and "url(" not in svg)

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
