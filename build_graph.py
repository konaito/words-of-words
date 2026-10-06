"""OEWN 2025 から「見出し語 -> 語義(synset) -> 定義文の語」グラフを作る。"""
import gzip
import pickle
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

SRC = "data/oewn2025.xml.gz"

# 機能語: 最初から既知扱い（ユーザー指定）。閉じたクラスの語だけを手で列挙。
FUNCTION_WORDS = set("""
a an the this that these those some any each every no all both either neither
another other such what which who whom whose whatever whichever whoever
i me my mine you your yours he him his she her hers it its we us our ours they them their theirs
myself yourself himself herself itself ourselves themselves oneself one
of in on at by for with from to into onto upon about above below over under
between among through during before after since until till against without within
across along around behind beyond near off out up down toward towards via per
than as like unlike except besides despite
and or but nor so yet if then because although though while whereas whether unless
be is am are was were been being have has had having do does did done doing
can could may might must shall should will would
not n't also very too just only even still
there here how when where why
something anything everything nothing someone anyone everyone none else cannot etc whereby lest others somebody anybody everybody nobody
""".split())

TOKEN_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")

NOUN_RULES = [("ses", "s"), ("xes", "x"), ("zes", "z"), ("ches", "ch"), ("shes", "sh"),
              ("men", "man"), ("ies", "y"), ("s", "")]
VERB_RULES = [("ies", "y"), ("es", "e"), ("es", ""), ("ed", "e"), ("ed", ""),
              ("ing", "e"), ("ing", ""), ("s", "")]
ADJ_RULES = [("er", ""), ("est", ""), ("er", "e"), ("est", "e")]
ALL_RULES = NOUN_RULES + VERB_RULES + ADJ_RULES


def main():
    lemma_synsets = defaultdict(dict)  # 出現順を保つ  # 小文字の見出し語 -> synset id
    lemma_pos = defaultdict(set)
    form_to_lemma = {}                # 不規則変化形 -> 見出し語
    synset_def = {}

    for _, el in ET.iterparse(gzip.open(SRC), events=("end",)):
        if el.tag == "LexicalEntry":
            lemma = el.find("Lemma").get("writtenForm").lower()
            lemma_pos[lemma].add(el.find("Lemma").get("partOfSpeech"))
            for s in el.findall("Sense"):
                lemma_synsets[lemma].setdefault(s.get("synset"))
            for f in el.findall("Form"):
                form_to_lemma.setdefault(f.get("writtenForm").lower(), lemma)
            el.clear()
        elif el.tag == "Synset":
            d = el.find("Definition")
            synset_def[el.get("id")] = d.text if d is not None and d.text else ""
            el.clear()

    lemmas = set(lemma_synsets)

    rule_pos = [(r, {"n"}) for r in NOUN_RULES] + [(r, {"v"}) for r in VERB_RULES] + [(r, {"a", "s"}) for r in ADJ_RULES]

    def base_forms(tok):
        """変化形とみなせるときの元の語の候補（品詞が接尾辞ルールと合うものだけ）。"""
        cands = set()
        if tok in form_to_lemma:
            cands.add(form_to_lemma[tok])
        for (suf, rep), pos in rule_pos:
            if tok.endswith(suf):
                c = tok[: -len(suf)] + rep
                if len(c) >= 3 and c in lemmas and lemma_pos[c] & pos:
                    cands.add(c)
        return cands

    def lemmatize(tok):
        cands = base_forms(tok)
        best = max(cands, key=lambda c: (len(lemma_synsets[c]), len(c), c)) if cands else None
        if tok in lemmas:
            # parts / used のような独立見出し語より、語義の多い元の語を優先する
            if best and len(lemma_synsets[best]) > len(lemma_synsets[tok]):
                return best
            return tok
        return best

    import random
    changed = {}
    unresolved = Counter()
    synset_req = {}
    for sid, text in synset_def.items():
        req = set()
        for raw in TOKEN_RE.findall(text):
            parts = [raw.lower()]
            if "-" in raw and lemmatize(parts[0]) is None:
                parts = parts[0].split("-")
            for tok in parts:
                tok = tok.removesuffix("'s")
                if not tok or tok in FUNCTION_WORDS:
                    continue
                lem = lemmatize(tok)
                if lem and lem != tok: changed[tok] = lem
                if lem is None:
                    unresolved[tok] += 1
                elif lem not in FUNCTION_WORDS:
                    req.add(lem)
        synset_req[sid] = req

    words = sorted(w for w in lemmas if w not in FUNCTION_WORDS)
    print("見出し語(機能語除く):", len(words))
    print("  うち1語(空白なし):", sum(1 for w in words if " " not in w))
    print("synset:", len(synset_def))
    print("定義文で使われる異なり語:", len(set().union(*synset_req.values())))
    print("見出し語に戻せなかったトークン: 異なり", len(unresolved), "/ 延べ", sum(unresolved.values()))
    print("  上位:", unresolved.most_common(40))

    random.seed(0)
    print('戻し方サンプル:', random.sample(sorted(changed.items()), 40))
    print('2文字以下に戻ったもの:', [(t,l) for t,l in changed.items() if len(l)<=2][:40])
    with open("graph.pkl", "wb") as f:
        pickle.dump({"words": words,
                     "word_synsets": {w: list(lemma_synsets[w]) for w in words},
                     "synset_req": {k: sorted(v) for k, v in synset_req.items()},
                     "synset_def": synset_def}, f)


main()
