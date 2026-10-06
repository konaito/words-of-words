# 英英辞書の種語探索（OEWN 2025）

- 辞書: Open English WordNet 2025（english-wordnet-2025.xml.gz）。見出し語 127,223 件（1語の見出し語 74,353 件）
- ルール: いずれか1つの語義の定義語がすべて既知なら、その語を既知にする。同じ synset の語はまとめて既知になる
- 機能語（約150語）は最初から既知扱い。OEWN にない固有名詞（America など、延べ約9,700トークン）は要件から外した

| k | 局所探索のセット | 到達（全見出し語） | 貪欲法の到達 |
|---|---|---|---|
| 1 | more | 444 | 92 |
| 4 | more move give use | 861 | 162 |
| 5 | give が抜け person place が入る | 1,061 | 184 |
| 7 | more move use person place cause time | 1,517（1.2%） | 227 |
| 8 | more が抜け language quality が入る | 94,836（74.5%） | 242 |
| 12 | +often european asia existing | 100,658（79.1%） | 258 |

- 7語の探索: 8語セットから1語抜いた8通りを出発点に、入れ替え探索した。最良は1,517語で、急増には届かなかった
- 100%に必要な種（貪欲法）: どれか1語義なら1,458語、最初に並んでいる語義のみなら3,961語
- 比較: Basic English 850（機能語を除くと781語）は76.8%、Thing Explainer（788語）は77.0%
- ファイル: greedy_steps.json, greedy_first.json, swap_any.json, baseline.json
