"""Trong 197 câu B SAI ở argmax/argmin, hàng vàng có tín hiệu KHÔNG-CẦN-NHÃN nào
không? Đây là phép đo chốt Bước 2 của kế hoạch Cấu hình C.

Trần bộ lọc hàng tĩnh là 99,14% (dev) — nhưng trần đó BIẾT TRƯỚC hàng vàng. Câu
hỏi quyết định: có luật nào suy TỪ OCR tách được hàng vàng ra khỏi hàng mà B
chọn sai không? Nếu có, cài luật đó vào `audit_rule_system.py`; nếu không, dư
địa là oracle-only và Cấu hình C không có gì để học.

Phép đo: chỉ nhìn 197 câu B sai, đếm xem mỗi tín hiệu ứng viên có trỏ đúng hàng
vàng không. Một tín hiệu chỉ có giá trị nếu nó trúng ở phần LỚN của 197 câu.

Tín hiệu thử:
  - hàng in đậm đo từ ảnh (`grid_ocr.bold_row`) — tín hiệu không gian/thị giác
  - hàng vàng nằm trong KHOI ĐẦU (khối nhãn chưa lặp) — tín hiệu văn bản

Không đọc `cell_annotations.jsonl`.

    python probe_gold_signal.py --split dev
    python probe_gold_signal.py --split eval
"""
import argparse
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.stdout.reconfigure(encoding="utf-8")
from grid_ocr import DATA, build_tables, bold_row, load_jsonl, to_number
from audit_rule_system import LABEL, find_col
from row_filter_ceiling import gold_row_of, resolve

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

    st = Counter()
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

        win = sorted(sc, reverse=(rt == "argmax"))[0][1]
        st["tổng"] += 1
        st["B đúng"] += (win == grow)
        st["B SAI"] += (win != grow)
        if win == grow:
            continue

        brow = bold_row(doc, table, set(pool))
        st["  gold = hàng ĐẬM (ảnh)"] += (brow == grow)
        st["  gold != hàng ĐẬM (ảnh)"] += (brow != grow)
        st["  hàng ĐẬM = hàng B đã chọn (vô dụng)"] += (brow == win)
        st["  đo được hàng đậm nhưng sai chỗ"] += (brow is not None and brow not in (grow, win))
        st["  không đo được hàng đậm"] += (brow is None)
        # khối đầu: cắt tại chỗ nhãn lặp lần đầu
        seen, blk = set(), []
        for r in sorted(pool):
            t = gg[(r, lc)]["clean_text"] if (r, lc) in gg else ""
            if t in seen:
                break
            seen.add(t)
            blk.append(r)
        st["  gold nằm trong KHỐI ĐẦU (văn bản)"] += (grow in blk)

    n_wrong = st["B SAI"]
    print(f"===== TÍN HIỆU CỨU HÀNG VÀNG trong {n_wrong} câu B sai "
          f"(split: {args.split}, {st['tổng']} câu) =====")
    for k, v in st.items():
        if k.startswith("  ") and n_wrong:
            print(f"{k:44}{v:6d}  = {100*v/n_wrong:5.1f}% số câu sai")
        else:
            print(f"{k:44}{v:6d}")
    if n_wrong:
        bold_pc = 100 * st["  gold = hàng ĐẬM (ảnh)"] / n_wrong
        blk_pc = 100 * st["  gold nằm trong KHỐI ĐẦU (văn bản)"] / n_wrong
        print("\nkết luận: tín hiệu chỉ dùng được nếu trúng phần LỚN của số câu sai.")
        print(f"  {bold_pc:.1f}% (hàng đậm) và {blk_pc:.1f}% (khối đầu) đều không đủ "
              f"— xem docstring.")


if __name__ == "__main__":
    main()
