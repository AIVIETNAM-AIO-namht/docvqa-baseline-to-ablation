"""Lưới dựng từ OCR có khớp lưới vàng ở đủ 5 trường Cấu hình B cần không?

Script ĐO — được phép đọc cell_annotations.jsonl. `verify_grid.py` cũ chỉ kiểm
`row`/`column` trên lưới VÀNG (tự đối chiếu chính nó). Script này kiểm lưới
THẬT SỰ dựng từ `ocr/*.json`:

    clean_text · table · row · column · is_header

    python verify_grid_ocr.py
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from grid_ocr import DATA, build_tables, load_jsonl

sys.stdout.reconfigure(encoding="utf-8")

FIELDS = ("clean_text", "table", "row", "column", "is_header")


def main():
    gold = defaultdict(list)
    for c in load_jsonl(DATA / "cell_annotations.jsonl"):
        gold[c["document_id"]].append(c)

    bad = {f: [] for f in FIELDS}
    n_cells = 0
    unmatched = 0
    n_tables_gold = n_tables_ocr = 0

    for doc, cells in gold.items():
        n_cells += len(cells)
        n_tables_gold += len({(c["page"], c["table"]) for c in cells})

        mine = build_tables(doc)
        n_tables_ocr += len(mine)

        # Tra ô của mình theo bbox — cùng nguồn hình học nên bbox phải khớp khít.
        index = {(c["page"], tuple(c["bbox"])): c for t in mine.values() for c in t}

        for g in cells:
            m = index.get((g["page"], tuple(g["bbox"])))
            if m is None:
                unmatched += 1
                continue
            for f in FIELDS:
                if m[f] != g[f]:
                    if len(bad[f]) < 3:
                        bad[f].append((doc, g["page"], g["row"], g["column"], g[f], m[f]))
                    bad[f].append(None)          # đếm, không giữ

    print(f"ô vàng        : {n_cells}")
    print(f"bảng vàng/ocr : {n_tables_gold} / {n_tables_ocr}")
    print(f"ô không khớp bbox: {unmatched}")
    print()
    print(f"{'trường':12}{'số ô lệch':>12}")
    for f in FIELDS:
        n = sum(1 for x in bad[f] if x is None)
        print(f"{f:12}{n:12d}{'' if n == 0 else '   <-- LỆCH'}")
    print()
    for f in FIELDS:
        ex = [x for x in bad[f] if x is not None]
        if ex:
            print(f"ví dụ lệch {f}:")
            for doc, page, r, c, gv, mv in ex:
                print(f"  {doc} p{page} r{r}c{c}  vàng={gv!r}  ocr={mv!r}")

    assert unmatched == 0, "có ô vàng không tìm thấy trong lưới OCR"
    assert not any(x is None for f in FIELDS for x in bad[f]), "lưới OCR lệch lưới vàng"


if __name__ == "__main__":
    main()
