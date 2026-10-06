"""定義グラフ上の到達計算。語は、いずれかの語義の定義語がすべて既知なら既知になる。"""
import pickle


class Graph:
    def __init__(self, path="graph.pkl", first_sense=False):
        g = pickle.load(open(path, "rb"))
        self.words = g["words"]
        self.wid = {w: i for i, w in enumerate(self.words)}
        sids = sorted(g["synset_req"])
        self.sdef = [g["synset_def"][s] for s in sids]
        sidx = {s: i for i, s in enumerate(sids)}
        # 機能語だけの見出し語は words から除いてあるので、要件にもメンバーにも出てこない
        self.req = [[self.wid[w] for w in g["synset_req"][s] if w in self.wid] for s in sids]
        self.members = [[] for _ in sids]
        self.wsyn = [[] for _ in self.words]
        for w, ss in g["word_synsets"].items():
            i = self.wid[w]
            for s in (ss[:1] if first_sense else ss):
                self.members[sidx[s]].append(i)
                self.wsyn[i].append(sidx[s])
        self.rev = [[] for _ in self.words]  # 語 -> その語を要件に含む語義
        for s, r in enumerate(self.req):
            for w in r:
                self.rev[w].append(s)
        self.single = [" " not in w for w in self.words]


class Closure:
    """種を1語ずつ足しながら、既知の語を増やしていく。"""

    def __init__(self, g):
        self.g = g
        self.known = [False] * len(g.words)
        self.unk = [len(r) for r in g.req]
        self.n_known = 0
        self.n_single = 0
        self.log = []  # (語, 由来の語義 or None)
        self.on_learn = None
        self.on_unk = None
        queue = [s for s, u in enumerate(self.unk) if u == 0]
        self._drain(queue)

    def _learn(self, w, via, queue):
        self.known[w] = True
        self.n_known += 1
        self.n_single += self.g.single[w]
        self.log.append((w, via))
        if self.on_learn:
            self.on_learn(w)
        for s in self.g.rev[w]:
            old = self.unk[s]
            self.unk[s] = old - 1
            if self.on_unk:
                self.on_unk(s, old, old - 1)
            if old == 1:
                queue.append(s)

    def _drain(self, queue):
        while queue:
            s = queue.pop()
            for m in self.g.members[s]:
                if not self.known[m]:
                    self._learn(m, s, queue)

    def add_seed(self, w):
        """種を足し、新しく既知になった語の数（種自身を含む）を返す。"""
        if self.known[w]:
            return 0
        before = self.n_known
        queue = []
        self._learn(w, None, queue)
        self._drain(queue)
        return self.n_known - before


def coverage(g, seeds):
    c = Closure(g)
    for w in seeds:
        c.add_seed(w)
    return c
