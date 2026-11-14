# 手を入れるときに

Issue も pull request も歓迎する。登録は要らない。

## この道具が何をするか

作用素についての計算と、その結果に証書を付ける。数値が正しいことを、その場で
確かめられる形で出す。依存は NumPy だけである。

```
python3 demo.py
```

## 何を知らせてほしいか

<https://github.com/cpsbvbng26-dotcom/trinity-operator/issues> に立てる。

1. 入力（行列、次元、設定）
2. 出た値と証書
3. 期待していた値と、その根拠

数値が合わない報告は最優先である。再現できる最小の入力を添えてほしい。

## 変更を出す

```
pip install numpy
python3 verification/check_text.py         # 誤変換とバッジ記法
python3 check.py                           # 作用素
python3 verification/check_certificate.py  # 証書
python3 verification/check_roadmap.py      # 展望
python3 verification/check_citation.py     # 引用情報
python3 verification/check_secrets.py      # 秘密情報と個人の連絡先
python3 verification/check_docs.py         # 札・様式・件数（要: 隣の trinity-infinity）
python3 verification/run_all.py            # CI が回すものを全部
```

通ってから出す。乱数を使う検査は種を固定してある。

## 検査を足すときは、壊す試験も一緒に足す

通ることでは信用できない。通る状態を壊して、その検査がちょうど落ちることを
確かめる。そして、名乗っている数を直す。項目数はワークフローの仕事の名前と
README が名乗っており、ずれると落ちる。

## 証書を弱めない

この道具の設計上の約束である。出した数値には、確かめ直すための情報を付ける。
証書を省く高速化は受け付けない。速さのために確かめられなさを増やすなら、
確かめる道具である意味が無い。

## 展望を実績として書かない

`roadmap/` にあるのはこれからの見込みであって、できていることではない。
できていないものを「できている」と読める形に書き換える変更は受けられない。
`verification/check_roadmap.py` がそこを見ている。

## 通らない変更

- **検査の期待値や乱数種を、通すために変えること**
- **証書を省くこと**
- **展望を実績として書くこと**
- **NumPy 以外の依存を足すこと**（理由が示されれば相談する）

## 支えの範囲と、これからの見込み

- **維持しているのは著者一人である**（根本卓哉）。組織の後ろ盾は無い
- issue への返答は**数日から一週間**を目安とする。約束ではない
- 範囲。この作用素についての計算と、その証書に限る。一般の線形代数の道具に
  育てる予定は無い
- 後方互換。関数の名前と引数は、既にある呼び出しが壊れる形では変えない

## ライセンス

[MIT](LICENSE)。手を入れたぶんも同じ条件で扱われる。

## 突き合わせの受付 / Checked intake

2026-12-01 から、誤りの知らせ（`error-report.yml`）は「突き合わせの受付」で確かめる。
人が嘘をつくこと一般は、仕組みでは止められない。受けるのは、申し立てた人がその場で書けない出どころと突き合わせられる申し立てだけで、通らないものと確かめられないものは自動で退ける。
確かめるのは一つだけである。「書いてあること」の語が、「どこか」の欄に書いた所（このリポジトリのファイル、配っている頁、このリポジトリが写しを持つ DOI の PDF か翻刻）に、そのとおりにあること。空白の違いと文字の幅は見ない。頁や節は確かめず、文書の全体を探す。
あればラベル「quote verified」を付ける。それが誤りかどうかは、人が読んで決める。なければ、決まった文のコメントを付けて閉じる。新しい issue で出し直せる。
削除・権利・個人の情報・氏名・人についての記述・同意の撤回を求めると読める issue は、自動では閉じない。ラベル「needs a person」を付け、人が読む。
コメントと実行の記録は、決まった語と issue の番号だけを書き、issue に書かれたことを写さない。
道具は `.github/checked-intake/verify.js`、確かめる先は `.github/checked-intake/config.json` にある。

From 2026-12-01, error reports (`error-report.yml`) are checked by the checked intake.
No system can stop a person from lying in general. Only claims that can be checked against a source that the claimant does not write at the moment of claiming are accepted; a claim that fails, or cannot be checked, is turned away automatically.
One thing is checked: that the words under "What it says" occur, as written, at the location under "Where" (a file of this repository, a page that it serves, or the PDF or transcription of a DOI of which it holds a copy). Differences of white space and character width are ignored. The page or section is not checked; the whole document is searched.
If they occur, the label "quote verified" is added, and whether it is an error is decided by a person. If they do not, the issue is closed with a fixed comment, and a new issue can be opened.
An issue that reads as asking for removal, or concerning rights, personal data, a name, a statement about a person or the withdrawal of a consent, is never closed automatically; it gets the label "needs a person", and a person reads it.
Comments and logs carry only fixed words and the issue number, never what the issue says.
The script is `.github/checked-intake/verify.js`; what it checks against is in `.github/checked-intake/config.json`.
