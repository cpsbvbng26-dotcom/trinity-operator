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

## 調べた法令

- 著作権法（第2条、第21条、第23条）

## 取り寄せられなかった文

- 教科書の著作権の扱いは、公式を写していないので取り寄せの対象にしていません。

## 弁護士について

この点検は Claude が行いました。
弁護士は、この点検を見ていません。
