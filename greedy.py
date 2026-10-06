"""前向き貪欲法: Σ 1/(定義文の未知語数) が最大の語を1語ずつ種に足す。"""
import heapq
import json
import sys
import time

from engine import Closure, Graph


def run(max_steps, first_sense):
    g = Graph(first_sense=first_sense)
    c = Closure(g)
    print(f"種0語での既知: 全{c.n_known} / 1語{c.n_single}", flush=True)
    print("  例:", [g.words[w] for w, _ in c.log[:20]])

    # 語義 s が「効く」のは、未充足で、まだ未知のメンバーがいるとき
    unknown_members = [sum(1 for m in g.members[s] if not c.known[m]) for s in range(len(g.req))]
    score = [0.0] * len(g.words)

    def active(s):
        return c.unk[s] > 0 and unknown_members[s] > 0

    for s in range(len(g.req)):
        if active(s):
            for w in g.req[s]:
                if not c.known[w]:
                    score[w] += 1.0 / c.unk[s]

    heap = [(-score[w], w) for w in range(len(g.words)) if not c.known[w]]
    heapq.heapify(heap)

    def bump(s, delta):
        for w in g.req[s]:
            if not c.known[w]:
                score[w] += delta
                heapq.heappush(heap, (-score[w], w))

    def on_unk(s, old, new):
        # 語義 s の未知語数が old -> new に減った
        if unknown_members[s] == 0:
            return
        if new == 0:
            bump(s, -1.0 / old)
        else:
            bump(s, 1.0 / new - 1.0 / old)

    def on_learn(w):
        for s in g.wsyn[w]:
            unknown_members[s] -= 1
            if unknown_members[s] == 0 and c.unk[s] > 0:
                bump(s, -1.0 / c.unk[s])

    c.on_unk = on_unk
    c.on_learn = on_learn

    total, total1 = len(g.words), sum(g.single)
    steps = []
    t0 = time.time()
    while heap and len(steps) < max_steps and c.n_known < total:
        negs, w = heapq.heappop(heap)
        if c.known[w] or -negs != score[w]:
            continue
        mark = len(c.log)
        gain = c.add_seed(w)
        unlocked = [g.words[x] for x, _ in c.log[mark + 1:]]
        steps.append({"k": len(steps) + 1, "seed": g.words[w], "score": round(-negs, 3),
                      "gain": gain, "known": c.n_known, "known_single": c.n_single,
                      "cov": c.n_known / total, "cov_single": c.n_single / total1,
                      "unlocked_sample": unlocked[:15]})
        k = len(steps)
        if k <= 30 or k in (50, 100, 200, 300, 500, 850, 1000, 2000, 3000, 5000) or k % 1000 == 0:
            print(f"k={k:5d} +{g.words[w]!r:18} gain={gain:6d} 全{c.n_known/total:6.2%} 1語{c.n_single/total1:6.2%}"
                  f"  ({time.time()-t0:.0f}s)", flush=True)
    print(f"終了 k={len(steps)} 全{c.n_known}/{total} 1語{c.n_single}/{total1}")
    json.dump(steps, open("results/greedy_first.json" if first_sense else "results/greedy_steps.json", "w"), ensure_ascii=False)


run(10**9, "--first" in sys.argv)
