# 法令の点検（2026-11-12）

この頁は、2026-11-12 に Claude が行った法令の点検のうち、trinity-operator の分の記録です。
対象は、README のライセンスの表と、lessons/・games/・site/ の CC BY 4.0、ゲーム理論のノートが教科書の公式を使う箇所です。
10 のリポジトリに掛かる免責事項の点検と、条文の取り寄せ方は、cpsbvbng26-dotcom の[点検の記録](https://github.com/cpsbvbng26-dotcom/cpsbvbng26-dotcom/blob/main/docs/legal-audit-2026-11-12.md)にあります。
この頁は運営者の立場を記録するもので、読む人への法的な助言ではありません。

## やり方

法令が出てくる箇所を一つずつ挙げ、挙げた条の文を、取り寄せた条文と照らしました。
条文は記憶から書いていません。
Sophaxis の取り寄せの仕事を走らせて e-Gov から取り寄せ、cpsbvbng26-dotcom の [verification/statutes.json](https://github.com/cpsbvbng26-dotcom/cpsbvbng26-dotcom/blob/main/verification/statutes.json) に写しました。
この頁が挙げる条がどれもその表にあることは、cpsbvbng26-dotcom の `check_ecosystem.js` が確かめます。
判定は、誤り・根拠不足・漏れ・表現・問題なしの五つです。

## 点検の表

| 箇所 | 法令と条 | 要件 | 事実 | 判定 | 対応 |
| --- | --- | --- | --- | --- | --- |
| README「ライセンス」の表、LICENSE、lessons/LICENSE、games/LICENSE、site/ の頁の末尾、CITATION.cff、.zenodo.json | 著作権法第21条、著作権法第23条 | 複製と公衆送信は著作者の権利で、他人に許す範囲は許す者の表示で決まる | 全体が MIT。lessons/ と games/ は中の LICENSE、site/ は頁の末尾の表示で CC BY 4.0。CITATION.cff と .zenodo.json は MIT。README の表は四つの置き場を全部書く | 問題なし | なし |
| 免責事項（cpsbvbng26-dotcom）の「再利用」と作品の目録 | 著作権法第21条、著作権法第23条 | 複製と公衆送信は著作者の権利で、他人に許す範囲は許す者の表示で決まる | 免責事項は site/ を書かず、目録は「MIT（全体）」と書いていた | 誤り | cpsbvbng26-dotcom と researcher-profile で直した。cpsbvbng26-dotcom の `check_ecosystem.js` が、site/ の頁の末尾の表示と免責事項と目録を突き合わせる |
| games/ のノートが使う繰り返しゲームの公式 | 著作権法第2条 | 著作物は思想又は感情を創作的に表現したもの | 公式と考え方は表現ではない。文は自分で書いている | 問題なし | なし |

## 2026-11-12 の続き：リスクを締めた

同じ日に、利用者が「法的リスクをさらにシメて」と求めました。
上の表で根拠不足としたところと、取り寄せた文だけでは読みが決まらないところを、厳しいほうの読みで見直しました。
厳しいほうの読みでも成り立つ形があり、費用が掛からないときは、その形を採りました。
決めたことは、行ごとに理由と一緒に書きます。
取り寄せられなかった文に頼るところは、この節では扱っていません。

| 箇所 | 法令と条 | 要件 | 事実 | 判定 | 対応 |
| --- | --- | --- | --- | --- | --- |
| site/（golden-window-conjecture.vercel.app） | Vercel の Fair use Guidelines、Vercel の利用規約 第4節 | Hobby は個人の非営利の利用に限る。商用の例は、支払いの受け付け、商品や役務の販売の広告、広告の掲載など | 予想を述べる英語の頁で、支払い・販売の広告・広告は無い。頁の下の欄は連絡と免責事項だけ。配る頁の設定に受注の場への道が無いことを、researcher-profile の `check_build.js` が今日から見る | 問題なし | なし |
| roadmap/ と games/ が名を挙げる研究者 | 刑法第230条 | 公然と事実を摘示して名誉を毀損すること | 名は既知の結果の帰属を述べる文に出る。予想に人名を付けていない | 問題なし | なし |
| README の責任の一文 | 民法第709条 | 故意又は過失で他人の権利又は法律上保護される利益を侵害した者は、生じた損害を賠償する | 「責任の範囲は、免責事項に定めています」と書いていた。免責事項は契約ではなく、責任の範囲は法令が決める。今日、免責事項は責任を免除する文をやめた | 表現 | 「責任は、法令の定めるとおりです。説明は免責事項にあります。」に直した。10 のリポジトリで同じ一文にそろえ、cpsbvbng26-dotcom の `check_ecosystem.js` が一字一句を見る。2026-11-12 に Claude が決めました。免責事項が範囲を決めると読める言い方は、どちらの読みでも成り立たないからです |

## 2026-11-12 の続き：取り寄せた周辺の文

上の表で取り寄せられなかった文のうち、同じ日に Sophaxis の取り寄せの仕事が取り寄せたものがあります。
置き場は Sophaxis の main（コミット 6b40d77、PR #218）の `verification/sources-raw.json` です。
取り寄せた文で、上の結論を一つずつ確かめ直しました。
条の文は cpsbvbng26-dotcom の `verification/statutes.json` に写し、`check_ecosystem.js` が Sophaxis の文と一字一句を突き合わせます。
規約は著作物なので、頼った句だけをこの表に引きます。

| 箇所 | 法令と条 | 要件 | 事実 | 判定 | 対応 |
| --- | --- | --- | --- | --- | --- |
| site/ を配る Vercel の計画 | Vercel の Fair use Guidelines、Vercel の利用規約 第4節 | Hobby は個人の非営利の利用に限る | Vercel の API はチームを一つ、プロジェクトを四つ返した。計画の名は返さない。2026-06-01 から 2026-11-12 までの請求を引くと `costs_not_found` が返った。docs/canonical-sources.md（cpsbvbng26-dotcom）は、このサイトを Hobby と記録している | 問題なし | Hobby に当たるとして扱う。頁に支払い・販売の広告・広告は無い |

## 2026-11-12 の続き：二度目の見落とし

同じ日に、読むだけの点検を、さらに別の手でもう一度行いました。
上の節が見落としていたものが見つかりました。
前の行は、そのとき何を確かめたかの記録なので、消していません。
法令の文は、cpsbvbng26-dotcom の `verification/statutes.json` に写した取り寄せた文から引きます。
10 のリポジトリに同じものを置く文書の点検は、[cpsbvbng26-dotcom の記録](https://github.com/cpsbvbng26-dotcom/cpsbvbng26-dotcom/blob/main/docs/legal-audit-2026-11-12.md)の同じ見出しの節にもあります。

| 箇所 | 法令と条 | 要件 | 事実 | 判定 | 対応 |
| --- | --- | --- | --- | --- | --- |
| SECURITY.md | 民法第709条 | 取り寄せた文は「故意又は過失によって他人の権利又は法律上保護される利益を侵害した者は、これによって生じた損害を賠償する責任を負う」と定める。無い窓口を約して、頼った人に損を生じさせないこと | SECURITY.md は、安全の問題を GitHub の非公開の報告で受けると約していた。GitHub の API は、2026-11-12 に、このリポジトリの非公開の報告を `enabled: false` と返した。これはリポジトリの設定であり、Claude の持つ道具では変えられない | 誤り | 運営者の ORCID の記録にあるメールアドレスで受けると書き直し、GitHub の非公開の報告は有効になっていないと、確かめた日と一緒に書いた。写しは 10 のリポジトリと deposit-check で一字一句同じで、cpsbvbng26-dotcom の `check_ecosystem.js` の 12j が中身を確かめる。2026-11-12 に Claude が決めました。在る窓口は、免責事項がすでに使っている一つだけだからです |
| `verification/check_docs.py` の SECURITY.md の検査 | 民法第709条 | 同上 | 検査は「Report a vulnerability」の語があることを求めていた。無い入口を求める検査だった | 誤り | 検査を、ORCID の記録のメールと、非公開の報告が有効でないことを求め、「Report a vulnerability」が戻れば落ちる向きに替えた。もとの SECURITY.md に戻して、落ちることを確かめた。2026-11-12 に Claude が決めました。検査が求める文を、在る窓口の文に移すためです |

## 2026-11-12 の続き：四度目の見落とし

同じ日に、読むだけの点検を、四度目に別の手で行いました。
上の節が見落としていたものが見つかりました。
前の行は、そのとき何を確かめたかの記録なので、消していません。
誤っていた前の行は、新しい行の中でそう書き、理由を添えます。
法令の文は、cpsbvbng26-dotcom の `verification/statutes.json` に写した取り寄せた文から引きます。
10 のリポジトリと deposit-check に同じ形で置く文の点検は、[cpsbvbng26-dotcom の記録](https://github.com/cpsbvbng26-dotcom/cpsbvbng26-dotcom/blob/main/docs/legal-audit-2026-11-12.md)の同じ見出しの節にもあります。

| 箇所 | 法令と条 | 要件 | 事実 | 判定 | 対応 |
| --- | --- | --- | --- | --- | --- |
| README「ライセンス」 | 著作権法第21条 | 取り寄せた文は「著作者は、その著作物を複製する権利を専有する。」と定める（cpsbvbng26-dotcom の `verification/statutes.json`、SHA-256 `a85d04f2fd20d7867d5579bee40676b13405c58ea7fd7eb27f1e7a5a03bda100`）。許せるのは、許す者が権利を持つものだけである。ライセンスの文が、他人の文まで許すと読めないこと | README のライセンスの節は、置き場ごとの MIT と CC BY 4.0 だけを書き、引いた他人の文の扱いを書いていなかった。Sophaxis は、最初の見落としの節で同じ一文を足していたが、10 のリポジトリと deposit-check には届いていなかった。上の点検の表の「README「ライセンス」の表、LICENSE、lessons/LICENSE、games/LICENSE、site/ の頁の末尾、CITATION.cff、.zenodo.json」の行は問題なしとしていたが、他人の文の扱いを見ていなかった | 漏れ | README のライセンスの節に「このリポジトリが引き、または引用を確かめるために置いている他人の文は、CC BY 4.0 でも MIT でも許諾しておらず、それぞれの権利者のものです。」を足した。`check_ecosystem.js` の 12l が、10 のリポジトリと deposit-check の README（英語の README を含む）にこの一文があることを見る。2026-11-12 に Claude が決めました。Sophaxis の README と同じ範囲を、同じ形で書くためです |
| CITATION.cff の message と .zenodo.json の notes | 著作権法第21条 | 同上。引用情報の license の欄は、どの部分に掛かるかを書けないので、その範囲を別の欄で書くこと | CITATION.cff と .zenodo.json の license の欄は MIT で、notes はコードが MIT、lessons の文章が CC BY 4.0 とだけ書き、games/ と site/ を落としていた。四度目の点検は、この欄がコードの MIT しか言わないことを挙げた。上の点検の表の「README「ライセンス」の表、LICENSE、lessons/LICENSE、games/LICENSE、site/ の頁の末尾、CITATION.cff、.zenodo.json」の行は問題なしとしていたが、欄の掛かる範囲と他人の文を見ていなかった | 表現 | message と notes に、リポジトリが MIT で、lessons/ と games/ の文章と site/ の頁が CC BY 4.0 であり、license の欄（MIT）はその三つに掛からないことを書いた。他人の文は許諾していないとも、和英で書いた。`check_ecosystem.js` の 12l が、二つのファイルにこの文があり、置き方が目録の licenceLayout と同じことを見る。2026-11-12 に Claude が決めました。Sophaxis の CITATION.cff が三度目の見落としの節で書いた範囲の文に、10 のリポジトリと deposit-check を揃えるためです |

## 調べた法令

- 著作権法（第2条、第21条、第23条）
- 刑法（第230条）
- 民法（第709条）
- Vercel の利用規約 第4節と Fair use Guidelines

## 取り寄せられなかった文

- 教科書の著作権の扱いは、公式を写していないので取り寄せの対象にしていません。
- Vercel のどの計画で配っているかは、Vercel の API が計画の名を返さないので、確かめていません。

## 弁護士について

この点検は Claude が行いました。
弁護士は、この点検を見ていません。
