# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Open English WordNet 2025の定義文をグラフにして、少ない種語で到達できる見出し語の数を最大化するプロジェクトです。結果をもとにしたブラウザゲームが`game/`にあります。結果と手順は`README.md`にまとめてあります。

## コマンド

すべてリポジトリのルートで実行します。スクリプトは相対パスでファイルを読み書きします。

```sh
uv run --no-project python build_graph.py      # data/oewn2025.xml.gz から graph.pkl を作る（約3秒）
uv run --no-project python greedy.py [--first] # results/greedy_steps.json か results/greedy_first.json を作る
uv run --no-project python baseline.py         # results/greedy_*.json が先に必要
uv run --no-project python swap.py 12          # 約10分かかる。到達数が急に増えたあとは評価1回が重くなる
uv run --no-project python export_game.py      # game/graph.txt と game/defs.txt を作る
bun test_engine.js                              # JS版の到達計算の回帰テスト
```

Pythonは標準ライブラリだけを使い、依存パッケージはありません。

## 構成

処理は`build_graph.py`、`graph.pkl`、`engine.Graph`の順に進み、探索スクリプトと`export_game.py`がその上に乗ります。

- `build_graph.py`は、定義文のトークンを見出し語に戻し、機能語を外して`graph.pkl`に保存します。戻し方は品詞つきの接尾辞ルールと、XMLの`<Form>`（不規則変化）を使います。`parts`や`used`のような独立した見出し語でも、元の語のほうが語義が多ければ元の語（part、use）に戻します。
- `engine.Graph`は、語義ごとの定義語（`req`）、メンバー（`members`）、逆引き（`rev`）を持ちます。`engine.Closure`は語義ごとの未知語数を数え、0になった語義の全メンバーを既知にして連鎖させます。`first_sense=True`のときは、各語の最初の語義だけをメンバーに入れます。
- `game/engine.js`は`engine.Closure`をJSに移したもので、同じ数を返す必要があります。どちらかを変えたら`bun test_engine.js`を実行します。期待値は、種0語で71、`more`で444、8語のセットで94,836です。
- `game/index.html`は、扉、選ぶ、広がる、結果の4面を960x540の固定ステージで切り替えます。到達計算は`DictEngine.closure()`を呼ぶだけで、自前の計算は持ちません。「広がる」の波は、種語の先頭i語で`closure()`を呼んだ到達数で区切ります。点の位置は見た目だけで意味を持たず、点の数は波ごとの到達数から決めます。下の1行に出す「開いた定義」は到達順から逆算した表示専用の値です。種語は候補30語`CANDS`のほか、検索で全見出し語から選べます。
- ページ内の`BEST`、`REFS`（94,836、97,689、97,924、全語に届く種語1,458語）、候補30語`CANDS`と日本語の第一原義`GLOSS`は、`results/`の値を手で書き写したものです。データを作り直したら、これらも合わせて直します。

## 注意点

- `build_graph.py`の出力は、PYTHONHASHSEEDによらず同じになる必要があります。同点の候補をsetの順で選ぶと、実行ごとに結果が変わります（過去にskiesがskyとskiのどちらに戻るかで揺れました）。
- 機能語の一覧（`FUNCTION_WORDS`）を変えると、すべての数値が変わります。
- ゲームの見た目は白に近い地#f7f5f1と白いパネルに、種語ごとのパステル8色`COLORS`を使います。角丸と薄い影は使ってよく、グラデーションは使いません。外部のCDN、フォント、画像は読み込みません（マスコットはインラインSVGです）。
- 画面の文言はすべて`index.html`の`T`（ja、en）に置き、片方の言語だけに書きません。例外は`GLOSS`で、日本語表示のときだけ候補30語に（）で添えます。日本語の文言は、和文と欧文のあいだに半角空白を入れずに書きます。
- 結果画面には「到達は定義の文字列をたどれたことで、意味が分かったことではない」という一文を残します。
- ゲームは[konaito.github.io/words-of-words](https://konaito.github.io/words-of-words/)に公開しています。mainへのpushで`.github/workflows/pages.yml`が`game/`をそのまま配信します。`game/index.html`はdoctypeとheadを持つ完全なHTML文書で、og/twitterタグの画像URLは公開先の絶対URLです。カード画像は`tools/render_card.sh`で作り直します。
- `data/basic-english-850.txt`と`data/thing-explainer-1000.txt`はライセンスが確認できないため、コミットしません。取得手順はREADMEにあります。
