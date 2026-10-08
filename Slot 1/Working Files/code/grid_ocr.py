"""Lưới bảng dựng THUẦN từ `ocr/*.json` + ảnh trang — không đọc file nhãn.

Nguồn dữ liệu chung cho mọi thứ không được phép chạm `labels.jsonl` /
`cell_annotations.jsonl`: harness trần oracle và Cấu hình B.

    text ô        <- block OCR
    row           <- gom block theo y0
    table         <- cắt tại chỗ hở dọc >= TABLE_GAP
    column        <- chỉ số trong LƯỚI CỘT của bảng (hàng nhiều ô nhất)
    is_header     <- mọi hàng TRƯỚC hàng đầu tiên chứa số
    is_bold       <- đo từ ảnh (bào mòn 1 vòng, bỏ phiếu theo cột)

`verify_grid_ocr.py` đối chiếu lưới này với lưới vàng: **0 lệch / 256.040 ô**
trên cả 5 trường.

Hai luật cuối không hiển nhiên, đo mới biết:

- `column` KHÔNG phải thứ tự trong hàng. Hàng tiêu đề phụ chỉ có 2 ô
  ('Thông tin chung', 'Số liệu báo cáo') nhưng nằm ở cột 0 và cột 4 — số cột
  lấy từ hàng nhiều ô nhất của bảng, ô nào cũng quy về đó.
- `is_header` là cả KHỐI tiêu đề: 1.872 bảng có 3 hàng (tên bảng, tiêu đề phụ,
  tên cột), 110 bảng chỉ 1 hàng. Mốc là hàng đầu tiên chứa số.
"""
import json
import re
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image

BASE = Path(__file__).resolve().parents[3]
DATA = BASE / "data" / "training_set"

# Ngưỡng tách mực/giấy. Ảnh là scan tổng hợp nền sáng nên Otsu không cần —
# 0.5*255 tách đúng trên toàn bộ mẫu đã thử.
INK_THRESHOLD = 128

# Khoảng hở dọc tách hai bảng. Đo trên train: hàng TRONG một bảng chạm hoặc
# chồng nhau (hở <= 0), hai bảng cách nhau >= 0,0256. 0,01 nằm giữa hai cụm.
TABLE_GAP = 0.01

# Dung sai gán ô về cột của lưới. Các ô cùng cột lệch x0 dưới 1e-4; cột gần
# nhất kế tiếp cách >= 0,02. 0,01 nằm giữa hai cụm.
COL_TOL = 0.01


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


# ------------------------------------------------------------------ OCR -> lưới

def load_ocr(doc_id):
    """-> {block_id: block} với 'row_key' = (page, y0) suy từ hình học."""
    path = DATA / "ocr" / f"{doc_id}.json"
    doc = json.loads(path.read_text(encoding="utf-8"))

    blocks = []
    for page in doc["pages"]:
        for b in page["blocks"]:
            b = dict(b)
            b["page"] = page["page"]
            b["row_key"] = (b["page"], round(b["bbox"][1], 6))
            blocks.append(b)
    return {b["block_id"]: b for b in blocks}


def split_tables(rows):
    """Cắt danh sách hàng (đã sắp trên->dưới) thành các bảng tại chỗ hở dọc."""
    if not rows:
        return []
    out, cur = [], [rows[0]]
    for prev, nxt in zip(rows, rows[1:]):
        gap = min(b["bbox"][1] for b in nxt) - max(b["bbox"][3] for b in prev)
        if gap >= TABLE_GAP:
            out.append(cur)
            cur = []
        cur.append(nxt)
    out.append(cur)
    return out


def _grid_columns(rows):
    """Toạ độ x0 của lưới cột = hàng nhiều ô nhất trong bảng."""
    return sorted(b["bbox"][0] for b in max(rows, key=len))


def _column_of(x0, grid, tol=COL_TOL):
    i = min(range(len(grid)), key=lambda k: abs(grid[k] - x0))
    return i if abs(grid[i] - x0) <= tol else None


def _header_depth(rows):
    """Số hàng tiêu đề = số hàng đứng TRƯỚC hàng đầu tiên chứa số."""
    for i, g in enumerate(rows):
        if any(to_number(b["text"]) is not None for b in g):
            return i
    return len(rows)


def build_tables(doc_id):
    """-> {(page, table): [cell]}. Cell mang ĐỦ trường như cell_annotations.jsonl.

    Nhờ vậy toàn bộ solver viết cho lưới vàng chạy nguyên xi trên lưới này,
    không phải sửa một dòng nào.
    """
    blocks = list(load_ocr(doc_id).values())
    out = {}
    for page in sorted({b["page"] for b in blocks}):
        by_row = defaultdict(list)
        for b in blocks:
            if b["page"] == page:
                by_row[b["row_key"]].append(b)
        rows = [by_row[k] for k in sorted(by_row, key=lambda k: k[1])]

        for t, group in enumerate(split_tables(rows), 1):
            grid = _grid_columns(group)
            depth = _header_depth(group)
            cells = []
            for r, row in enumerate(group):
                for b in row:
                    cells.append({
                        "document_id": doc_id,
                        "page": page,
                        "table": t,
                        "row": r,
                        "column": _column_of(b["bbox"][0], grid),
                        "clean_text": b["text"],
                        "bbox": b["bbox"],
                        "is_header": r < depth,
                        "is_bold": None,        # đo muộn, xem fill_bold
                    })
            out[(page, t)] = cells
    return out


# ------------------------------------------------------------------ đậm từ ảnh

@lru_cache(maxsize=8)
def page_gray(doc_id, page):
    """Trang xám. Giữ 8 trang là đủ: mỗi tài liệu tối đa 2 trang."""
    with Image.open(DATA / "images" / f"{doc_id}_p{page:02d}.jpg") as im:
        return np.array(im.convert("L"))


def stroke_ratio(crop):
    """Tỉ lệ pixel tối còn lại sau khi bào mòn 1 vòng -> dày nét.

    Mật độ mực thô chỉ được 70,84% vì ô nhiều chữ thì mực nhiều bất kể đậm.
    Phép này bù được, và bỏ phiếu theo cột (cùng cột, hàng nào dày hơn) đưa lên
    83,55%. Đã thử 5 phép đo chuẩn hoá khác (`probe_bold2.py`, tốt nhất
    core/ink = 82,99%): không phép nào vượt ~84% => đây là trần thật của tín
    hiệu ảnh, không phải cài đặt tồi.
    """
    b = crop < INK_THRESHOLD
    if b.shape[0] < 3 or b.shape[1] < 3:
        return 0.0
    core = b[1:-1, 1:-1] & b[:-2, 1:-1] & b[2:, 1:-1] & b[1:-1, :-2] & b[1:-1, 2:]
    n = b.sum()
    return float(core.sum()) / float(n) if n else 0.0


def cell_stroke(doc_id, cell):
    arr = page_gray(doc_id, cell["page"])
    h, w = arr.shape
    x0, y0, x1, y1 = cell["bbox"]
    crop = arr[int(y0 * h):int(np.ceil(y1 * h)), int(x0 * w):int(np.ceil(x1 * w))]
    return stroke_ratio(crop)


def bold_row(doc_id, cells, candidates):
    """Trong các hàng ứng viên, hàng nào in đậm? Bỏ phiếu theo từng cột.

    So sánh CHỈ giữa các hàng ứng viên — câu hỏi đã nêu tên chúng ("trong hai
    dòng X và Y"). Đo trên 535 câu: bỏ phiếu TOÀN BẢNG chỉ được 15/535 = 2,8%,
    giới hạn trong hàng ứng viên được 431/535 = 80,6%. So với một hàng mốc bất
    kỳ thì tín hiệu đậm bị chìm trong nhiễu độ dày nét giữa các hàng.

    ponytail: bỏ tín hiệu "hàng đậm luôn đứng đầu evidence" — nó đúng 100%
    nhưng chỉ vì đó là quy ước sinh dữ liệu (khi lệch với ảnh thì ảnh luôn sai,
    xem `probe_bold_order.py`). Dùng nó là học thuộc mẫu, không phải suy luận.
    """
    stroke = defaultdict(dict)
    for c in cells:
        if c["row"] in candidates:
            stroke[c["row"]][c["column"]] = cell_stroke(doc_id, c)

    votes = defaultdict(int)
    for r, g in stroke.items():
        for col, s in g.items():
            other = [s2 for r2, g2 in stroke.items() if r2 != r
                     for c2, s2 in g2.items() if c2 == col]
            if other and s > max(other):
                votes[r] += 1
    return max(votes, key=votes.get) if votes else None


def fill_bold(doc_id, cells, candidates):
    """Điền `is_bold` cho cả bảng, hàng đậm chọn trong `candidates`.

    Không nhớ đệm: hai câu khác nhau trên cùng bảng nêu hai cặp hàng khác nhau,
    nên kết quả phải tính lại theo từng câu. Chỉ đo vài ô mỗi lần, không phải
    cả 256k.
    """
    win = bold_row(doc_id, cells, candidates)
    for c in cells:
        c["is_bold"] = (c["row"] == win)


# ------------------------------------------------------------------ số

def to_number(s):
    """'1.850' -> 1850.0 (vi-VN nhóm nghìn bằng '.'), '3,5' -> 3.5. Bỏ '%' cuối."""
    s = s.strip().replace(" ", "").rstrip("%")
    if re.fullmatch(r"[+-]?\d{1,3}(\.\d{3})+", s):
        return float(s.replace(".", "").replace("+", ""))
    s2 = s.replace(",", ".")
    return float(s2) if re.fullmatch(r"[+-]?\d+(\.\d+)?", s2) else None


def fmt(v):
    if v is None:
        return None
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return f"{v:.2f}".rstrip("0").rstrip(".").replace(".", ",")
