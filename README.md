# Words of Words

英英辞書の中で、何語を「指差しで」覚えれば残りを言葉だけで定義できるかを調べるプロジェクトです。Open English WordNet 2025の定義文をグラフにして、少ない種語で到達できる語の数を最大化します。結果をもとにしたブラウザゲームも入っています。

## 結果

| 種語 | 到達した見出し語（127,223語中） |
|---|---|
| move, use, person, place, cause, time, language, qualityの8語 | 94,836語（74.5%） |
| 局所探索で見つかった最良の7語 | 1,517語（1.2%） |
| 貪欲法で1語ずつ選んだ8語 | 242語 |
| Basic English（機能語を除く781語） | 97,689語（76.8%） |
| Thing Explainerの語彙（機能語と変化形を除く788語） | 97,924語（77.0%） |
| 全語に届く種語（貪欲法） | 1,458語 |

8語のどれか1語を抜くと、到達数は1,318語以下に落ちます。条件を「最初に並んでいる語義のみ」に絞ると、全語に届くには3,961語が必要です。

## 到達のルール

- 見出し語は、いずれか1つの語義の定義文に出てくる語がすべて既知になると既知になります
- 同じ語義（synset）に属する見出し語は、まとめて既知になります
- the、of、haveなどの機能語は最初から既知として扱います。一覧は`build_graph.py`の`FUNCTION_WORDS`にあります
- 定義文の語のうち、WordNetの見出し語に戻せないもの（America、Africaなどの固有名詞）は条件から外します。延べ約9,700語です

多義語のどれか1語義で足りるため、到達は語義を乗り換えながら進みます。たとえばdogは「go after with the intent to catch」の語義で到達します。到達は「定義の文字列をたどれた」ことを示すもので、意味が分かったことを示すものではありません。

## 必要なもの

- [uv](https://docs.astral.sh/uv/)（Pythonは標準ライブラリだけを使います）
- [bun](https://bun.sh/)（JS版の到達計算のテストに使います）

## 手順

辞書データは`data/oewn2025.xml.gz`に入っています。取り直す場合は次のコマンドを実行します。

```sh
curl -L -o data/oewn2025.xml.gz https://github.com/globalwordnet/english-wordnet/releases/download/2025-edition/english-wordnet-2025.xml.gz
```

比較に使う語彙リストは、ライセンスが確認できないためリポジトリに入れていません。`baseline.py`を実行する前に取得します。

```sh
B=https://raw.githubusercontent.com/ChristopherA/iambic-mnemonic/master/word-lists
curl -L -o data/basic-english-850.txt $B/basic-english-850.txt
curl -L -o data/thing-explainer-1000.txt $B/thing-explainer-1000.txt
```

コマンドはすべてリポジトリのルートで実行します。

```sh
uv run --no-project python build_graph.py      # 定義グラフを作り graph.pkl に保存する
uv run --no-project python greedy.py           # 貪欲法（どれか1語義）を results/greedy_steps.json に保存する
uv run --no-project python greedy.py --first   # 貪欲法（最初の語義のみ）を results/greedy_first.json に保存する
uv run --no-project python baseline.py         # Basic EnglishとThing Explainerを評価し results/baseline.json に保存する
uv run --no-project python swap.py 12          # k=1から12まで1語入れ替えの局所探索をする（約10分かかる）
uv run --no-project python export_game.py      # ゲーム用の game/graph.txt と game/defs.txt を書き出す
bun test_engine.js                              # JS版の到達計算がPython版と同じ数を返すか確かめる
```

`baseline.py`と`swap.py`は`results/greedy_*.json`を読むので、`greedy.py`のあとに実行します。

`results/swap_any.json`は、`swap.py`をk=12で止めたときのログから組み立て直したものです。各kのセットの到達数は`coverage()`で再計算して確かめてあります。`swap.py`を最初から実行し直して同じ結果になるかは確かめていません。

## ゲーム

`game/`がブラウザゲームです。[konaito.github.io/words-of-words](https://konaito.github.io/words-of-words/)で遊べます。画面は扉、選ぶ、広がる、結果の4面です。候補30語か検索で種語を8語選ぶと、種語1語ずつの波で到達した語が点になって広がります。結果では、自分の到達数を上の結果の表の値と並べます。表示は日本語と英語を切り替えられ、日本語表示では候補30語に日本語の第一原義を（）で添えます。

マウスだけでも、キーボードだけでも最後まで遊べます。選ぶ画面では矢印キーで候補を移動し、Enterで出し入れし、Backspaceで最後の語を外します。検索欄ではEnterで先頭の候補を選びます。Escでどの画面からでも扉に戻ります。

到達数はengine.jsの戻り値をそのまま表示します。点の数と位置は演出用で、点の数だけ到達数より間引いています。

ローカルで開く場合は、`game/`で静的サーバーを立てます。`index.html`は`graph.txt`と`defs.txt`をfetchで読むため、ファイルを直接開くと動きません。

```sh
cd game && python3 -m http.server 8765
```

mainに`game/`の変更をpushすると、`.github/workflows/pages.yml`がGitHub Pagesへ配信します。リンクのプレビューに使うカード画像`game/card.png`は、`tools/card.html`から`./tools/render_card.sh`で作り直せます。macOSのGoogle Chromeが必要です。

## ファイル

| パス | 内容 |
|---|---|
| `build_graph.py` | XMLを読み、定義文の語を見出し語に戻してグラフを作る |
| `engine.py` | 到達計算（Python版） |
| `greedy.py` / `swap.py` / `baseline.py` | 種語の探索と比較 |
| `export_game.py` | ゲーム用データの書き出し |
| `game/engine.js` | 到達計算（JS版）。ゲームとテストで共用する |
| `results/results.md` | 解析結果のまとめ |
| `data/` | 辞書データ。比較用の語彙リストは手順で取得する |
| `tools/` | カード画像の元のHTMLと書き出しスクリプト |

## 出典

- 辞書: [Open English WordNet 2025](https://github.com/globalwordnet/english-wordnet)（CC BY 4.0）
- Basic English 850語とThing Explainerの語彙: [ChristopherA/iambic-mnemonic](https://github.com/ChristopherA/iambic-mnemonic/tree/master/word-lists)
