"""既存の基礎語彙リストを種にしたときの到達率を、同じ語数の貪欲法と比べる。"""
import json
from engine import Graph, coverage

out = {}
for first in (False, True):
    g = Graph(first_sense=first)
    steps = json.load(open("results/greedy_first.json" if first else "results/greedy_steps.json"))
    tot, tot1 = len(g.words), sum(g.single)
    mode = "第1語義のみ" if first else "どれか1語義"
    for name in ("basic-english-850", "thing-explainer-1000"):
        raw = [l.strip().lower() for l in open(f"data/{name}.txt") if l.strip()]
        seeds = [g.wid[w] for w in raw if w in g.wid]
        missing = [w for w in raw if w not in g.wid]
        c = coverage(g, seeds)
        k = len(seeds)
        gs = steps[k - 1]
        out[f"{mode}/{name}"] = {"k": k, "cov": c.n_known / tot, "cov_single": c.n_single / tot1,
                                "greedy_cov": gs["cov"], "greedy_cov_single": gs["cov_single"]}
        print(f"{mode} {name}: 種{k}語(機能語・未収録{len(missing)}語を除外) "
              f"到達 全{c.n_known/tot:.2%} 1語{c.n_single/tot1:.2%} | 同じ語数の貪欲 全{gs['cov']:.2%} 1語{gs['cov_single']:.2%}")
        if not first:
            print("   除外例:", missing[:25])
json.dump(out, open("results/baseline.json", "w"), ensure_ascii=False, indent=1)
