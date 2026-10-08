"""O THUA nam o dau: trong hang vang, hay o HANG KHAC?

precision 0,685 nghia la toi dua thua o. Hai kha nang:
  (a) thua o NGAY TRONG hang vang  -> luat "o nao" sai
  (b) thua o o HANG KHAC           -> luat "hang nao" sai (gia tri bo loc
                                      khop nhieu hang, toi lay het)
Phan biet duoc hai cai nay thi biet sua cho nao.
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

    ex = Counter()
    samples = []
    for lab in labels:
        rt = lab["reasoning_type"]
        q = questions[lab["question_id"]]
        doc = lab["question_id"].rsplit("-q", 1)[0]
        g = [key[(doc, e["page"], tuple(e["bbox"]))] for e in lab["evidence"]
             if (doc, e["page"], tuple(e["bbox"])) in key]
        if not g:
            continue
        Ggold = {(c["row"], c["column"]) for c in g}
        grow = {c["row"] for c in g}

        pages = [int(x) for x in A.PAGE.findall(q)]
        mt = A.TBL.search(q)
        if not mt or not pages:
            continue
        table = tabs.get((doc, pages[0], int(mt.group(1))))
        if not table:
            continue
        asked = next((a.group(1) for a in (r.search(q) for r in A.ASKED) if a), None)
        ac = A.find_col(table, asked)
        G = A.groups(q, table)
        if not G:
            continue
        rows, fcells = A.match_rows(table, G[0])
        if rows is None:
            continue
        gg = A.grid(table)
        allrows, allfc = set(rows), list(fcells)
        for grp in G[1:]:
            rr, ff = A.match_rows(table, grp)
            if rr:
                allrows |= rr
                allfc += ff
        pe = allfc + [gg[k] for k in gg if k[0] in allrows and k[1] == ac]
        P = {(c["row"], c["column"]) for c in pe}

        extra = P - Ggold
        miss = Ggold - P
        if not extra and not miss:
            ex["KHOP CHINH XAC"] += 1
            continue
        for (r, c) in extra:
            ex["thua: CUNG HANG vang" if r in grow else "thua: HANG KHAC"] += 1
        for (r, c) in miss:
            ex["thieu: CUNG HANG vang" if r in grow else "thieu: HANG KHAC"] += 1
        if len(samples) < 8 and rt in ("compare", "argmax", "argmin", "cross_page_sum") and extra:
            samples.append((rt, lab["question_id"], sorted(grow), sorted(allrows),
                            len(extra), len(miss)))

    print("===== O THUA / O THIEU NAM O DAU =====")
    for k, v in ex.most_common():
        print(f"  {v:7d}  {k}")

    print("\n===== vi du: hang vang vs hang toi chon =====")
    for rt, qid, grow, mine, ne, nm in samples:
        print(f"  [{rt}] {qid}  hang vang={grow}  hang toi={mine}"
              f"  thua {ne} o / thieu {nm} o")


if __name__ == "__main__":
    main()
