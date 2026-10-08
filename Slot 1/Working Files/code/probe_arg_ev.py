"""argmax/argmin KHONG co bo loc: gold = o nao?

q04 (argmax, hoi c3) gold = {c0,c1,c3}
q07 (argmin, hoi c2) gold = {c0,c2}
Khong doan duoc bang mat -> do quan he giua cot vang va cot duoc hoi.
"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import audit_rule_system as A
from audit_ceiling import load


def main():
    labels = load("labels.jsonl")
    cells = load("cell_annotations.jsonl")
    questions = {q["question_id"]: q["question"] for q in load("questions.jsonl")}
    key = {(c["document_id"], c["page"], tuple(c["bbox"])): c for c in cells}
    tabs = A.defaultdict(list)
    for c in cells:
        tabs[(c["document_id"], c["page"], c["table"])].append(c)

    pat = Counter()
    for lab in labels:
        rt = lab["reasoning_type"]
        if rt not in ("argmax", "argmin"):
            continue
        qid = lab["question_id"]
        q = questions[qid]
        doc = qid.rsplit("-q", 1)[0]
        g = [key[(doc, e["page"], tuple(e["bbox"]))] for e in lab["evidence"]
             if (doc, e["page"], tuple(e["bbox"])) in key]
        if not g:
            continue
        page = g[0]["page"]
        tbl = tabs[(doc, page, g[0]["table"])]
        asked = next((a.group(1) for a in (r.search(q) for r in A.ASKED) if a), None)
        ac = A.find_col(tbl, asked)
        lm = A.LABEL.search(q)
        lc = A.find_col(tbl, lm.group(1)) if lm else None
        cols = tuple(sorted({c["column"] for c in g}))
        # gold so voi (nhan, cot duoc hoi)
        want = tuple(sorted({x for x in (ac, lc) if x is not None}))
        pat[(cols == want, ac, lc, cols)] += 1

    print("===== argmax/argmin: gold == {cot nhan, cot duoc hoi}? =====")
    hit = sum(v for (ok, _, _, _), v in pat.items() if ok)
    tot = sum(pat.values())
    print(f"  khop: {hit}/{tot} = {100*hit/tot:.1f}%")
    print("\n--- 12 truong hop sai nhieu nhat (gold_cols | asked_col | label_col) ---")
    for (ok, ac, lc, cols), v in pat.most_common(12):
        if not ok:
            print(f"  {v:5d}  gold={cols}  asked={ac}  label={lc}")


if __name__ == "__main__":
    main()
