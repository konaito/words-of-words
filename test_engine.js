const fs = require("fs");
require("./game/engine.js");
const t0 = Date.now();
const g = DictEngine.parseGraph(fs.readFileSync("game/graph.txt", "utf8"));
console.log("parse", Date.now() - t0, "ms", g.nw, g.ns);
const ids = (ws) => ws.map((w) => { const i = g.index.get(w); if (i === undefined) throw w; return i; });
const cases = [[[], 71], [["more"], 444], [["move","use","person","place","cause","time","language","quality"], 94836], [["move","use","person","place","cause","time","language","water"], 1172]];
for (const [ws, exp] of cases) {
  const t = Date.now(); const r = DictEngine.closure(g, ids(ws));
  console.log(ws.join(" ") || "(空)", r.count, exp, r.count === exp ? "OK" : "NG", "near", r.nearCount, Date.now() - t, "ms");
}
const r = DictEngine.closure(g, ids(["skin"])); console.log("skinless", r.known[g.index.get("skinless")]);
const r2 = DictEngine.closure(g, ids(["cheap","cigar"])); console.log("stogie", r2.known[g.index.get("stogie")], DictEngine.closure(g, ids(["cheap"])).known[g.index.get("stogie")]);
