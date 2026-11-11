#!/usr/bin/env python3
"""秘密情報と個人の連絡先が混ざっていないかを走査する。

    python3 verification/check_secrets.py

標準ライブラリのみ。決めごと 9（秘密情報・個人の連絡先を新規に公開しない）を、
push のたびに機械で見る。

見るもの。
  1. 鍵の形。秘密鍵の見出し、GitHub・AWS・Slack・Google などの鍵の書式、
     api_key = "…" のような代入。
  2. メールアドレス。許すのは、横断の検査（cpsbvbng26-dotcom の
     verification/check_ecosystem.js）と同じ二つだけ。
  3. 電話番号の形（日本の番号と +81）。

見つけたら、ファイルと行と、値の頭の四文字だけを出して落ちる。値そのものは出さない。

型は、この台本自身に掛からないように、文字列をつないで組む。
組んだ型がちゃんと拾うかは、走るたびに見本を当てて確かめる（4 の節）。
拾わない型は、何も見ていない。

同じ台本を trinity-infinity と trinity-operator に置いている。直すときは両方を直す。
"""

import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", "__pycache__", "node_modules", "venv", "_sibling"}
TEXT_EXT = (".md", ".py", ".yml", ".yaml", ".json", ".cff", ".txt", ".toml",
            ".html", ".js", ".css", ".svg", ".xml", ".gitignore", ".gitattributes")

# 横断の検査（ecosystem.json の「許すメールアドレス」）と同じ二つ。
ALLOWED_MAIL = {"noreply@anthropic.com", "you@example.com"}

BEGIN = "-" * 5 + "BEGIN "
KEYS = [
    ("秘密鍵の見出し", re.compile(re.escape(BEGIN) + r"(?:RSA |EC |DSA |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY")),
    ("GitHub の鍵", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_" + r"pat_[A-Za-z0-9_]{40,})")),
    ("AWS の鍵", re.compile(r"\b(?:AK" + r"IA|AS" + r"IA)[0-9A-Z]{16}\b")),
    ("Slack の鍵", re.compile(r"\bxox[abprs]" + r"-[A-Za-z0-9-]{10,}")),
    ("Google の鍵", re.compile(r"\bA" + r"Iza[0-9A-Za-z_\-]{35}")),
    ("言語モデルの API の鍵", re.compile(r"\bsk" + r"-(?:ant-|proj-)?[A-Za-z0-9_\-]{32,}")),
    ("鍵や合い言葉の代入", re.compile(
        r"(?i)\b(?:api[_-]?key|secret|password|passwd|access[_-]?token)\s*[:=]\s*[\"'][^\"'\s]{8,}[\"']")),
]
MAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
PHONE = re.compile(r"(?<![\d-])(?:0\d{1,3}-\d{2,4}-\d{4}|0[789]0\d{8}|\+81[ -]?\d{1,4}[ -]?\d{1,4}[ -]?\d{4})(?![\d-])")

passed, failures = 0, []


def check(label, cond, detail=""):
    global passed
    if cond:
        passed += 1
        print("  PASS  " + label + (("  " + detail) if detail else ""))
    else:
        failures.append(label)
        print("  FAIL  " + label + (("  " + detail) if detail else ""))


def files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if name.startswith("LICENSE"):
                continue
            if name.endswith(TEXT_EXT) or name in (".gitignore", ".gitattributes"):
                yield os.path.join(dirpath, name)


def masked(value):
    return value[:4] + "…（%d 字）" % len(value)


hits = {"key": [], "mail": [], "phone": []}
count = 0
for path in files():
    rel = os.path.relpath(path, ROOT)
    try:
        with io.open(path, encoding="utf-8") as fh:
            lines = fh.read().split("\n")
    except UnicodeDecodeError:
        continue
    count += 1
    for n, line in enumerate(lines, 1):
        for label, pat in KEYS:
            for m in pat.finditer(line):
                hits["key"].append("%s:%d %s %s" % (rel, n, label, masked(m.group(0))))
        for m in MAIL.finditer(line):
            if m.group(0) not in ALLOWED_MAIL:
                hits["mail"].append("%s:%d %s" % (rel, n, masked(m.group(0))))
        for m in PHONE.finditer(line):
            hits["phone"].append("%s:%d %s" % (rel, n, masked(m.group(0))))

print("\n%d ファイルを見ました。" % count)
check("走査するファイルがある", count > 0)

print("\n1〜3. 見つかったもの")
check("鍵の形が無い", not hits["key"], "; ".join(hits["key"][:5]))
check("許した二つのほかに、メールアドレスが無い", not hits["mail"], "; ".join(hits["mail"][:5]))
check("電話番号の形が無い", not hits["phone"], "; ".join(hits["phone"][:5]))

# 型が死んでいないかを、見本で確かめる。見本も、ここで組む。
print("\n4. 型が見本を拾う")
SAMPLES = [
    ("秘密鍵の見出し", BEGIN + "OPENSSH PRIVATE KEY" + "-" * 5),
    ("GitHub の鍵", "gh" + "p_" + "A1b2" * 9),
    ("AWS の鍵", "AK" + "IA" + "ABCDEFGHIJKLMNOP"),
    ("Slack の鍵", "xo" + "xb-" + "1234567890-abcdef"),
    ("Google の鍵", "A" + "Iza" + "B" * 35),
    ("言語モデルの API の鍵", "sk" + "-ant-" + "x" * 40),
    ("鍵や合い言葉の代入", "api_" + "key = \"" + "q" * 12 + "\""),
]
for label, sample in SAMPLES:
    pat = dict(KEYS)[label]
    check("「%s」の型が見本を拾う" % label, pat.search(sample) is not None)
check("メールアドレスの型が見本を拾い、許した二つは拾わない",
      MAIL.search("someone" + "@" + "example.org") is not None
      and all(MAIL.search(a).group(0) in ALLOWED_MAIL for a in ALLOWED_MAIL))
check("電話番号の型が見本を拾う",
      all(PHONE.search(s) for s in ("0" + "3-1234-5678", "0" + "90" + "12345678", "+" + "81 90 1234 5678")))
check("電話番号の型が ORCID と日付を拾わない",
      PHONE.search("0009-0000-1406-0547") is None and PHONE.search("2026-11-11") is None)

print("\n" + "-" * 58)
if failures:
    print("%d 件が通り、%d 件が通りませんでした。" % (passed, len(failures)))
    for f in failures:
        print("  - " + f)
    sys.exit(1)
print("%d 件すべて通りました。" % passed)
