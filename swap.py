"""k 語ごとに、貪欲法の先頭 k 語から1語入れ替えの局所探索で到達数を最大化する。"""
import json
import sys
import time

from engine import Closure, Graph

first = "--first" in sys.argv
KMAX = int(sys.argv[1])
POOL = 300  # 入れ替え候補: 貪欲法の上位 POOL 語

g = Graph(first_sense=first)
steps = json.load(open("results/greedy_first.json" if first else "results/greedy_steps.json"))
pool = [g.wid[s["seed"]] for s in steps[:POOL]]


def cov(seeds):
    c = Closure(g)
    for w in seeds:
        c.add_seed(w)
    return c.n_known


results = []
prev = None
for k in range(1, KMAX + 1):
    t0 = time.time()
    cands = [pool[:k]]
    if prev:  # 前の k の最適解に1語足した形も初期値にする
        cands.append(prev + [max((w for w in pool if w not in prev), key=lambda w: cov(prev + [w]))])
    best = max(cands, key=cov)
    best_cov = cov(best)
    improved = True
    while improved:
        improved = False
        for i in range(k):
            for w in pool:
                if w in best:
                    continue
                trial = best[:i] + [w] + best[i + 1:]
                v = cov(trial)
                if v > best_cov:
                    best, best_cov, improved = trial, v, True
    greedy_cov = steps[k - 1]["known"]
    names = sorted(g.words[w] for w in best)
    results.append({"k": k, "set": names, "known": best_cov, "greedy_known": greedy_cov})
    diff = ""
    if prev:
        p = {g.words[w] for w in prev}
        out_, in_ = sorted(p - set(names)), sorted(set(names) - p)
        diff = f" 抜け{out_} 入り{in_}" if out_ else f" 追加{in_}"
    print(f"k={k:2d} 到達 {best_cov:6d} (貪欲 {greedy_cov:6d}){diff}  {time.time()-t0:.0f}s", flush=True)
    prev = best

json.dump(results, open("results/swap_first.json" if first else "results/swap_any.json", "w"), ensure_ascii=False)
