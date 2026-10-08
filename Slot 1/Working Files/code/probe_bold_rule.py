"""Tin hieu IN DAM co phai mot LUAT khong-can-nhan cho argmax/argmin khong?

Buoc 2 cua ke hoach. Tran bo loc hang do duoc la 99,14% (dev) — vuot 94,2% —
nhung chi trien khai duoc neu co luat SUY TU OCR. Ung vien con lai duy nhat:
do day net tu ANH TRANG (`grid_ocr.bold_row`), khong doc nhan.

Hai phep do, phai lam CA HAI:

  1. LUAT: candidates = toan bo pool (dung thiet lap ma `bold_row` da do la
     chi duoc 15/535 = 2,8% tren `visual_bold_lookup`). Cham nhu solver.

  2. PHAN KY voi quy uoc sinh du lieu: "hang in dam luon dung dau danh sach
     evidence" dung 100% nhung la hoc thuoc mau (`probe_bold_order.py`: khi
     lech voi anh thi anh dung 0/88, thu tu dung 88/88). Neu luat (1) TRUNG
     voi thu tu nay o moi ca thi no chi la doc lai quy uoc, khong phai suy luan.

Khong doc cell_annotations.jsonl.

    python probe_bold_rule.py --split dev
"""
import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.stdout.reconfigure(encoding="utf-8")
from grid_ocr import DATA, build_tables, bold_row, load_jsonl, to_number
from audit_rule_system import LABEL, find_col
from anls import anls
from evidence_f1 import evidence_f1
from row_filter_ceiling import gold_row_of, resolve, same_bbox

SPLITS = HERE.parent / "splits"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="dev", choices=["all", "dev", "eval"])
    args = ap.parse_args()

    keep = None if args.split == "all" else \
        set((SPLITS / f"{args.split}_docs.txt").read_text(encoding="utf-8").split())

    labels = load_jsonl(DATA / "labels.jsonl")
    questions = {q["question_id"]: q["question"] for q in load_jsonl(DATA / "questions.jsonl")}

    tabs, docs = {}, {}
    for lab in labels:
        doc = lab["question_id"].rsplit("-q", 1)[0]
        if doc in tabs or (keep is not None and doc not in keep):
            continue
        mine = build_tables(doc)
        tabs[doc] = mine
        docs[doc] = set(mine)

    n = 0
    acc = Counter()                    # ten luat -> so cau dung hang
    score = defaultdict(lambda: [0.0, 0.0])   # ten luat -> [anls, f1]
    diverge = Counter()                # phan ky: luat vs thu tu evidence
    for lab in labels:
        rt, qid = lab["reasoning_type"], lab["question_id"]
        if rt not in ("argmax", "argmin"):
            continue
        doc = qid.rsplit("-q", 1)[0]
        if keep is not None and doc not in keep:
            continue
        sol = resolve(doc, questions[qid], docs, tabs[doc])
        if sol is None:
            continue
        table, ac, rows, G = sol
        lm = LABEL.search(questions[qid])
        lc = find_col(table, lm.group(1)) if lm else None
        if ac is None or lc is None:
            continue

        gg = {(c["row"], c["column"]): c for c in table if not c["is_header"]}
        pool = [r for r in (set(rows) if rows is not None else {r for (r, c) in gg if c == ac})
                if (r, ac) in gg and (r, lc) in gg]
        pool = [r for r in pool if to_number(gg[(r, ac)]["clean_text"]) is not None]
        if len(pool) < 2:
            continue
        grow = gold_row_of(table, lab["evidence"], lc)
        if grow is None or grow not in pool:
            continue
        n += 1

        # hang cua o evidence DAU TIEN = quy uoc sinh du lieu (khong duoc dung lam luat)
        first = next((c for c in table
                      if any(same_bbox(c["bbox"], e["bbox"]) and c["page"] == e["page"]
                             for e in lab["evidence"])), None)
        conv = first["row"] if first else None

        win = bold_row(doc, table, set(pool))
        for name, r in (("bold_row(pool)", win), ("evidence[0] (quy uoc)", conv)):
            if r is None:
                continue
            acc[name] += (r == grow)
            pred_ans = gg[(r, lc)]["clean_text"] if (r, lc) in gg else ""
            pred_ev = [gg[k] for k in {(r, ac), (r, lc), (r, lc + 1)} if k in gg]
            score[name][0] += anls(pred_ans, lab["answers"])
            score[name][1] += evidence_f1(pred_ev, lab["evidence"]) if pred_ev else 0.0
        if win is not None and conv is not None:
            diverge["lech nhau"] += (win != conv)
            if win != conv:
                diverge["  -> bold_row dung"] += (win == grow)
                diverge["  -> quy uoc dung"] += (conv == grow)
                diverge["  -> ca hai sai"] += (win != grow and conv != grow)

    print(f"===== TIN HIEU IN DAM — argmax/argmin (split: {args.split}, {n} cau) =====")
    print(f"{'luat':26}{'dung hang':>12}{'ANLS':>8}{'EvF1':>8}{'diem':>8}")
    for name in ("bold_row(pool)", "evidence[0] (quy uoc)"):
        if name not in acc:
            continue
        a, e = score[name]
        print(f"{name:26}{acc[name]/n:11.3f}{a/n:8.3f}{e/n:8.3f}{(0.85*a+0.15*e)/n:8.4f}")
    print("\n--- phan ky voi quy uoc sinh du lieu ---")
    for k in ("lech nhau", "  -> bold_row dung", "  -> quy uoc dung", "  -> ca hai sai"):
        print(f"  {k:24}{diverge[k]:6d}")


if __name__ == "__main__":
    main()
