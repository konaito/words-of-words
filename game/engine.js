// 定義グラフの到達計算。語は、いずれかの語義の定義語がすべて既知なら既知になる。
(function (root) {
  function csr(lists, n) {
    const off = new Int32Array(n + 1);
    for (let i = 0; i < n; i++) off[i + 1] = off[i] + lists[i].length;
    const data = new Int32Array(off[n]);
    for (let i = 0; i < n; i++) data.set(lists[i], off[i]);
    return { off, data };
  }

  function parseGraph(text) {
    const cut = text.indexOf("\n%%\n");
    const words = text.slice(0, cut).split("\n");
    const lines = text.slice(cut + 4).split("\n");
    const nw = words.length, ns = lines.length;
    const mem = new Array(ns), req = new Array(ns);
    const revLists = Array.from({ length: nw }, () => []);
    const ids = (s) => (s ? s.split(",").map((x) => parseInt(x, 36)) : []);
    for (let s = 0; s < ns; s++) {
      const bar = lines[s].indexOf("|");
      mem[s] = ids(lines[s].slice(0, bar));
      req[s] = ids(lines[s].slice(bar + 1));
      for (const w of req[s]) revLists[w].push(s);
    }
    const index = new Map(words.map((w, i) => [w, i]));
    const single = new Uint8Array(nw);
    for (let i = 0; i < nw; i++) single[i] = words[i].includes(" ") ? 0 : 1;
    return { words, index, single, nw, ns, mem: csr(mem, ns), req: csr(req, ns), rev: csr(revLists, nw) };
  }

  // seeds から到達計算する。order は既知になった順の語 id
  function closure(g, seeds) {
    const known = new Uint8Array(g.nw);
    const unk = new Int32Array(g.ns);
    for (let s = 0; s < g.ns; s++) unk[s] = g.req.off[s + 1] - g.req.off[s];
    const order = [];
    const stack = [];
    const learn = (w) => {
      known[w] = 1;
      order.push(w);
      for (let i = g.rev.off[w]; i < g.rev.off[w + 1]; i++) {
        const s = g.rev.data[i];
        if (--unk[s] === 0) stack.push(s);
      }
    };
    const drain = () => {
      while (stack.length) {
        const s = stack.pop();
        for (let i = g.mem.off[s]; i < g.mem.off[s + 1]; i++) {
          const m = g.mem.data[i];
          if (!known[m]) learn(m);
        }
      }
    };
    for (let s = 0; s < g.ns; s++) if (unk[s] === 0) stack.push(s);
    drain();
    const base = order.length;
    for (const w of seeds) {
      if (!known[w]) learn(w);
      drain();
    }
    // あと1語で書ける語: 未知語が1つだけ残った語義の、まだ知らないメンバー
    const near = new Uint8Array(g.nw);
    let nearCount = 0;
    for (let s = 0; s < g.ns; s++) {
      if (unk[s] !== 1) continue;
      for (let i = g.mem.off[s]; i < g.mem.off[s + 1]; i++) {
        const m = g.mem.data[i];
        if (!known[m] && !near[m]) { near[m] = 1; nearCount++; }
      }
    }
    return { known, order, base, count: order.length, nearCount };
  }

  root.DictEngine = { parseGraph, closure };
})(typeof window !== "undefined" ? window : globalThis);
