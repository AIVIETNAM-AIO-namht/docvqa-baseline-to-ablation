"""In ra vai hang THAT voi o vang duoc danh dau -> doc ra luat cua nhan.

Bo dem truoc cho thay: gold LUON la tap con cua du doan cua toi (khong thieu
o nao), nhung toi thua 6.293 o o cac cot < cot tra loi. Vay gold = o tra loi
+ MOT TAP CON nao do cua cac o bo loc. Tap con nao?

Thay vi doan tiep, in hang that ra doc.
"""
import sys, re
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from audit_ceiling import load

WANT = {"argmax": 5, "argmin": 4, "lookup": 2, "sum": 2,
        "compare": 5, "count": 2, "visual_bold_lookup": 2, "cross_page_sum": 4}


def main():
    labels = load("labels.jsonl")
    cells = load("cell_annotations.jsonl")
    questions = {q["question_id"]: q["question"] for q in load("questions.jsonl")}
    key = {(c["document_id"], c["page"], tuple(c["bbox"])): c for c in cells}
    tabs = defaultdict(list)
    for c in cells:
        tabs[(c["document_id"], c["page"], c["table"])].append(c)

    shown = defaultdict(int)
    for lab in labels:
        rt = lab["reasoning_type"]
        if shown[rt] >= WANT[rt]:
            continue
        qid = lab["question_id"]
        doc = qid.rsplit("-q", 1)[0]
        g = [key[(doc, e["page"], tuple(e["bbox"]))] for e in lab["evidence"]
             if (doc, e["page"], tuple(e["bbox"])) in key]
        if not g:
            continue
        shown[rt] += 1
        gset = {(c["page"], c["table"], c["row"], c["column"]) for c in g}
        tbl = tabs[(doc, g[0]["page"], g[0]["table"])]
        body = [c for c in tbl if not c["is_header"]]
        hdr = {c["column"]: c["clean_text"] for c in tbl if c["is_header"]}
        rows = sorted({c["row"] for c in g})
        # in MOI hang cua bang (khong chi hang vang) -> thay duoc hang nao bi bo sot
        allrows = sorted({c["row"] for c in body})
        rows = sorted(set(rows) | set(allrows[:12]))

        print(f"\n{'='*100}\n[{rt}] {qid}")
        print(f"  CÂU: {questions[qid]}")
        print(f"  ĐÁP ÁN: {lab['answers']}")
        print(f"  header: " + " | ".join(f"c{c}:{t[:12]}" for c, t in sorted(hdr.items())))
        for r in rows:
            rc = sorted([c for c in body if c["row"] == r], key=lambda c: c["column"])
            if not rc:
                continue
            marks = "".join("█" if (c["page"], c["table"], c["row"], c["column"]) in gset else "·"
                            for c in rc)
            print(f"  r{r:<3} {marks}  " + " | ".join(f"{c['clean_text'][:12]}" for c in rc))


if __name__ == "__main__":
    main()
