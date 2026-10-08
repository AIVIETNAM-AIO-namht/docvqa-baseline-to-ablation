"""CHAN DOAN (tam thoi) — 197 cau B sai o argmax/argmin: hang thang khac hang
vang o cho nao? Tra loi cau hoi cua Buoc 2: co LUAT KHONG CAN NHAN nao tach
duoc hang thang ra khoi hang vang khong?

Khong doc cell_annotations.jsonl. Chi doc labels.jsonl de biet hang vang (dinh
nghia cua phep do nay).

    python probe_row_filter.py --split dev
"""
import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.stdout.reconfigure(encoding="utf-8")
from grid_ocr import DATA, build_tables, load_jsonl, to_number
from audit_rule_system import ASKED, LABEL, PAGE, TBL, find_col, groups, match_rows
from row_filter_ceiling import gold_row_of, resolve

SPLITS = HERE.parent / "splits"

# Tu khoa goi y hang tong / hang phu — ung vien cho luat "bo hang tong".
TOTAL = re.compile(r"t[oổ]ng|c[oộ]ng|to[aà]n b[oộ]|trung b[iì]nh|b[iì]nh qu[aâ]n", re.I)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="dev", choices=["all", "dev", "eval"])
    args = ap.parse_args()

    keep = None if args.split == "all" else \
        set((SPLITS / f"{args.split}_docs.txt").read_text(encoding="utf-8").split())

    labels = load_jsonl(DATA / "labels.jsonl")
    questions = {q["question_id"]: q["question"] for q in load_jsonl(DATA / "questions.jsonl")}

    tabs, docs = {}, defaultdict(set)
    for lab in labels:
        doc = lab["question_id"].rsplit("-q", 1)[0]
        if doc in tabs or (keep is not None and doc not in keep):
            continue
        mine = build_tables(doc)
        tabs[doc] = mine
        docs[doc] = set(mine)

    stat = Counter()
    n_wrong = 0
    rank_hist = Counter()
    samples = []

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
        sc = [(to_number(gg[(r, ac)]["clean_text"]), r) for r in pool]
        sc = [(v, r) for v, r in sc if v is not None]
        if not sc:
            continue
        grow = gold_row_of(table, lab["evidence"], lc)
        if grow is None or grow not in pool:
            continue
        reverse = (rt == "argmax")
        win = sorted(sc, reverse=reverse)[0][1]
        if win == grow:
            continue
        n_wrong += 1

        label = lambda r: gg[(r, lc)]["clean_text"] if (r, lc) in gg else ""
        lab_w, lab_g = label(win), label(grow)

        # thu tu cua hang thang theo khoa (0 = thang)
        order = [r for _, r in sorted(sc, reverse=reverse)]
        rank_hist[order.index(win)] += 1

        stat["hang thang la hang TONG (tu khoa)"] += bool(TOTAL.search(lab_w))
        stat["hang vang la hang TONG (tu khoa)"] += bool(TOTAL.search(lab_g))
        # nhan trung: cung text voi mot hang khac trong pool
        texts = Counter(label(r) for r in pool)
        stat["nhan hang thang bi TRUNG trong pool"] += texts[lab_w] > 1
        stat["nhan hang vang bi TRUNG trong pool"] += texts[lab_g] > 1
        # hang thang nam CUOI bang (chi so hang lon nhat cua pool)
        stat["hang thang la hang CUOI cua pool"] += win == max(pool)
        stat["hang vang la hang CUOI cua pool"] += grow == max(pool)
        # nhan hang thang dai hon / ngan hon hang vang
        stat["nhan thang DAI hon nhan vang"] += len(lab_w) > len(lab_g)
        # hang thang khong co o o cot dau (cot 0) -> hang noi tiep
        stat["hang thang THIEU o cot 0"] += (win, 0) not in gg
        stat["hang vang THIEU o cot 0"] += (grow, 0) not in gg
        # gia tri hang thang gap bao nhieu lan hang vang
        vw = to_number(gg[(win, ac)]["clean_text"])
        vg = to_number(gg[(grow, ac)]["clean_text"])
        if vw and vg:
            stat["gia tri thang >= 2 lan gia tri vang"] += vw >= 2 * vg

        if len(samples) < 8:
            hdr = {c["column"]: c["clean_text"] for c in table if c["is_header"]}
            rows_dump = [(label(r), to_number(gg[(r, ac)]["clean_text"]), r)
                         for r in sorted(pool)]
            samples.append((qid, rt, questions[qid], hdr.get(ac), hdr.get(lc),
                            lab_g, vg, lab_w, vw, rows_dump))

    print(f"===== CHAN DOAN {n_wrong} cau B sai (split: {args.split}) =====")
    print("\n--- thu tu cua hang thang theo khoa (0 = hang thang chinh la top) ---")
    for k in sorted(rank_hist):
        print(f"  hang thang o vi tri {k}: {rank_hist[k]}")
    print("\n--- tin hieu co the tach duoc hang thang khoi hang vang? ---")
    print(f"{'tin hieu':45}{'hang thang':>12}{'hang vang':>12}")
    for key in sorted(stat):
        if key.startswith("hang vang"):
            continue
        w = stat[key]
        g = stat[key.replace("hang thang", "hang vang", 1)] if key.replace("hang thang", "hang vang", 1) in stat else None
        print(f"{key:45}{w:12d}{('' if g is None else g):>12}")
    print("\n--- 8 ca dau (day du) ---")
    for qid, rt, q, hac, hlc, lg, vg, lw, vw, dump in samples:
        print(f"\n[{rt}] {qid}  cot_hoi={hac!r} cot_nhan={hlc!r}")
        print(f"   {q}")
        print(f"   vang={lg!r}({vg})   thang={lw!r}({vw})")
        for t, v, r in dump:
            mark = "  <== VANG" if t == lg else ("  <== THANG" if t == lw else "")
            print(f"      r{r:2d} {t!r} = {v}{mark}")


if __name__ == "__main__":
    main()
