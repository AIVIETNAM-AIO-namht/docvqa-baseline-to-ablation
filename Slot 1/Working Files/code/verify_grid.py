"""Đối chiếu lưới tái dựng từ hình học OCR với lưới vàng cell_annotations.

Đây là script ĐO, không phải script suy luận — được phép đọc cell_annotations.
Câu hỏi cần trả lời: gom block theo y0 và sắp theo x0 có tái dựng đúng
(table, row, column) mà không cần file nhãn hay không?

    python verify_grid.py
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DATA = Path(__file__).resolve().parents[3] / "data" / "training_set"
CELLS = DATA / "cell_annotations.jsonl"

# Lệch dưới mức này coi như cùng một hàng (sai số làm tròn toạ độ).
Y_TOL = 1e-6


def main():
    by_doc = defaultdict(list)
    with open(CELLS, encoding="utf-8") as f:
        for line in f:
            c = json.loads(line)
            by_doc[c["document_id"]].append(c)

    n_cells = 0
    n_rows = 0
    mixed_table = []   # một hàng hình học chứa 2 bảng khác nhau -> gom y0 hỏng
    bad_order = []     # sắp theo x0 không ra thứ tự column

    for doc, cells in by_doc.items():
        n_cells += len(cells)
        rows = defaultdict(list)
        for c in cells:
            rows[(c["page"], round(c["bbox"][1], 6))].append(c)

        n_rows += len(rows)
        for key, g in rows.items():
            if len({c["table"] for c in g}) > 1:
                mixed_table.append((doc, key))
            cols = [c["column"] for c in sorted(g, key=lambda c: c["bbox"][0])]
            if cols != sorted(cols):
                bad_order.append((doc, key, cols))

    print(f"tài liệu      : {len(by_doc)}")
    print(f"ô            : {n_cells}")
    print(f"hàng hình học: {n_rows}")
    print()
    print(f"hàng trộn 2 bảng : {len(mixed_table)}")
    print(f"hàng sai thứ tự  : {len(bad_order)}")

    for doc, key in mixed_table[:5]:
        print(f"  trộn bảng: {doc} {key}")
    for doc, key, cols in bad_order[:5]:
        print(f"  sai cột  : {doc} {key} -> {cols}")

    assert not bad_order, "sắp theo x0 không tái dựng được thứ tự column"


if __name__ == "__main__":
    main()
