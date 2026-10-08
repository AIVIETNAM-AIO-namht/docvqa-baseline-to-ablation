"""Đo từ ảnh: cách nào tách được hàng in đậm?

Đây là script ĐO (đọc cell_annotations để lấy is_bold vàng). So bốn cách trên
đúng 535 câu visual_bold_lookup:
    (a) mật độ mực      = tỉ lệ pixel tối trong ô
    (b) độ dày nét      = tỉ lệ pixel tối SỐNG SÓT sau khi bào mòn 1 vòng
    (c) như (b) nhưng lấy ô đậm nhất trong hàng thay vì trung bình hàng
    (d) như (b) nhưng bỏ phiếu theo từng cột

(b) bù được thiên lệch của (a): ô nhiều chữ thì mực nhiều, bất kể đậm hay không.

Kết quả: (a) 70,84% · (b) 81,12% · (c) 82,43% · (d) 83,55% — và (d) khớp với
con số harness đo được (82,99%), chênh 0,6 điểm do harness dựng hàng từ OCR còn
đây dựng từ chính ô evidence. Không cách nào vượt ~84% ⇒ trần của tín hiệu ảnh.

    python probe_bold.py
"""
import json
import sys
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

DATA = Path(__file__).resolve().parents[3] / "data" / "training_set"
INK = 128


def load_jsonl(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


@lru_cache(maxsize=4)
def page_gray(doc, page):
    with Image.open(DATA / "images" / f"{doc}_p{page:02d}.jpg") as im:
        return np.array(im.convert("L"))


def crop_of(doc, cell):
    """Cắt ô từ ĐÚNG trang của nó. Bản đầu cứng trang 1, mà 409/1954 ô vàng của
    dạng này nằm ở trang 2 -> bị cắt nhầm chỗ, mọi con số ở đây thấp hơn thực tế."""
    arr = page_gray(doc, cell["page"])
    h, w = arr.shape
    x0, y0, x1, y1 = cell["bbox"]
    return arr[int(y0 * h):int(np.ceil(y1 * h)), int(x0 * w):int(np.ceil(x1 * w))]


def ink(c):
    return float((c < INK).mean()) if c.size else 0.0


def stroke(c):
    """Pixel tối còn lại sau khi bào mòn 4 láng giềng (không dùng scipy)."""
    b = (c < INK)
    if b.shape[0] < 3 or b.shape[1] < 3:
        return 0.0
    core = b[1:-1, 1:-1] & b[:-2, 1:-1] & b[2:, 1:-1] & b[1:-1, :-2] & b[1:-1, 2:]
    n = b.sum()
    return float(core.sum()) / float(n) if n else 0.0


def main():
    cells = load_jsonl(DATA / "cell_annotations.jsonl")
    by_key = {(c["document_id"], c["page"], tuple(c["bbox"])): c for c in cells}

    labels = load_jsonl(DATA / "labels.jsonl")
    vbl = [l for l in labels if l.get("reasoning_type") == "visual_bold_lookup"]

    hit_a = hit_b = hit_c = hit_d = 0
    n = 0
    for lab in vbl:
        doc = lab["question_id"].rsplit("-q", 1)[0]

        rows = defaultdict(list)
        for e in lab["evidence"]:
            c = by_key.get((doc, e["page"], tuple(e["bbox"])))
            if c:
                rows[(e["page"], round(e["bbox"][1], 6))].append(c)
        if len(rows) != 2:
            continue

        gold_bold = None
        for k, g in rows.items():
            if any(c["is_bold"] for c in g):
                gold_bold = k
        if gold_bold is None:
            continue

        n += 1
        a, b = {}, {}
        for k, g in rows.items():
            cs = [crop_of(doc, c) for c in g]
            a[k] = float(np.mean([ink(c) for c in cs]))
            b[k] = float(np.mean([stroke(c) for c in cs]))
        if max(a, key=a.get) == gold_bold:
            hit_a += 1
        if max(b, key=b.get) == gold_bold:
            hit_b += 1

        # (c) so theo Ô ĐẦM NHẤT trong hàng, không lấy trung bình cả hàng
        c_score = {k: max(stroke(crop_of(doc, c)) for c in g) for k, g in rows.items()}
        if max(c_score, key=c_score.get) == gold_bold:
            hit_c += 1

        # (d) bỏ phiếu theo từng CỘT: cùng cột, hàng nào đậm hơn?
        votes = defaultdict(int)
        for k, g in rows.items():
            for c in g:
                other = [c2 for k2, g2 in rows.items() if k2 != k
                         for c2 in g2 if c2["column"] == c["column"]]
                if other:
                    votes[k] += stroke(crop_of(doc, c)) > stroke(crop_of(doc, other[0]))
        if votes and max(votes, key=votes.get) == gold_bold:
            hit_d += 1

    print(f"visual_bold_lookup đo được: {n}")
    print(f"  (a) mật độ mực, TB hàng  : {hit_a}/{n} = {100*hit_a/n:.2f}%")
    print(f"  (b) độ dày nét, TB hàng  : {hit_b}/{n} = {100*hit_b/n:.2f}%")
    print(f"  (c) độ dày nét, ô đậm nhất: {hit_c}/{n} = {100*hit_c/n:.2f}%")
    print(f"  (d) bỏ phiếu theo cột     : {hit_d}/{n} = {100*hit_d/n:.2f}%")
    assert n > 0, "không dựng được hàng nào"


if __name__ == "__main__":
    main()
