"""Do vai luat LOC HANG khong dung nhan cho argmax/argmin — tra loi Buoc 2.

Cau hoi: trong 197 cau B sai, hang vang nam trong mot KHOI CON cua bang (gold
khong phai cuc tri toan bang). Khoi do co suy ra duoc tu OCR khong?

Cach do: voi moi luat, loc pool roi chay lai dung khoa sap xep cua solver, cham
ANLS + EvF1 nhu audit_rule_system.py. Cau ma luat lam MAT hang vang tinh la sai
(khong duoc cuu) — dung tinh than.

Khong doc cell_annotations.jsonl.

    python probe_dedup.py --split dev
"""
import argparse
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.stdout.reconfigure(encoding="utf-8")
from grid_ocr import DATA, build_tables, load_jsonl, to_number
from audit_rule_system import LABEL, find_col, groups, match_rows
from anls import anls
from evidence_f1 import evidence_f1
from row_filter_ceiling import gold_row_of, resolve

SPLITS = HERE.parent / "splits"


def rules(gg, pool, lc, table):
    """-> {ten luat: tap hang giu lai} (luon la tap con cua pool)."""
    label = lambda r: gg[(r, lc)]["clean_text"] if (r, lc) in gg else ""
    texts = Counter(label(r) for r in pool)
    dup = {r for r in pool if texts[label(r)] > 1}
    first = {}
    for r in sorted(pool):
        first.setdefault(label(r), r)
    # khoi dau: cat tai cho nhan lap lai lan dau
    blk, seen = [], set()
    for r in sorted(pool):
        if label(r) in seen:
            break
        seen.add(label(r))
        blk.append(r)
    return {
        "baseline (khong loc)": set(pool),
        "bo moi hang nhan TRUNG trong pool": set(pool) - dup,
        "chi giu lan xuat hien DAU cua moi nhan": set(first.values()),
        "chi giu KHOI DAU (cat tai nhan lap dau)": set(blk),
    }


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

    names = None
    agg = {}                       # ten luat -> [dung, tong, anls, f1]
    n_arg = 0
    for lab in labels:
        rt, qid = lab["reasoning_type"], lab["question_id"]
        if rt not in ("argmax", "argmin"):
            continue
        doc = qid.rsplit("-q", 1)[0]
        if keep is not None and doc not in keep:
            continue
        n_arg += 1

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
        if not pool:
            continue
        grow = gold_row_of(table, lab["evidence"], lc)
        cand = rules(gg, pool, lc, table)
        if names is None:
            names = list(cand)
            agg = {k: [0, 0, 0.0, 0.0] for k in names}

        reverse = (rt == "argmax")
        for k in names:
            sel = cand[k]
            if not sel:
                a, ef = 0.0, 0.0
            else:
                r = sorted(sel, key=lambda x: (to_number(gg[(x, ac)]["clean_text"]), x),
                           reverse=reverse)[0]
                pred_ans = gg[(r, lc)]["clean_text"]
                pred_ev = [gg[x] for x in {(r, ac), (r, lc), (r, lc + 1)} if x in gg]
                a = anls(pred_ans, lab["answers"])
                ef = evidence_f1(pred_ev, lab["evidence"])
            agg[k][0] += (r == grow) if sel else 0
            agg[k][1] += 1
            agg[k][2] += a
            agg[k][3] += ef

    print(f"===== LUAT LOC HANG KHONG NHAN — argmax/argmin (split: {args.split}, "
          f"{n_arg} cau) =====")
    print(f"{'luat':42}{'dung hang':>12}{'ANLS':>8}{'EvF1':>8}{'diem':>8}")
    for k in names:
        c, n, a, e = agg[k]
        print(f"{k:42}{c/n:11.3f}{a/n:8.3f}{e/n:8.3f}{(0.85*a+0.15*e)/n:8.4f}")


if __name__ == "__main__":
    main()
