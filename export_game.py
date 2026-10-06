"""graph.pkl からゲーム用の game/graph.txt と game/defs.txt を書き出す。

graph.txt: 見出し語を1行1語で並べ、"%%" の行のあとに語義を1行ずつ "メンバー|定義語" で並べる。
           語は見出し語の行番号を36進数にした id で、カンマ区切り。
defs.txt:  graph.txt の語義と同じ順で、定義文を1行ずつ。
"""
from engine import Graph


def b36(n):
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    out = ""
    while True:
        n, r = divmod(n, 36)
        out = digits[r] + out
        if n == 0:
            return out


g = Graph()
assert not any(w == "%%" or "\n" in w for w in g.words)
with open("game/graph.txt", "w") as f:
    f.write("\n".join(g.words) + "\n%%\n")
    f.write("\n".join(",".join(map(b36, g.members[s])) + "|" + ",".join(map(b36, g.req[s]))
                      for s in range(len(g.req))))
with open("game/defs.txt", "w") as f:
    f.write("\n".join(d.replace("\n", " ") for d in g.sdef))
print("語", len(g.words), "語義", len(g.req))
