#!/bin/sh
# tools/card.html を 1200x630 の game/card.png に書き出す（macOS の Google Chrome を使う）
set -eu
cd "$(dirname "$0")/.."
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars \
  --window-size=1200,630 --screenshot="$PWD/game/card.png" "file://$PWD/tools/card.html"
