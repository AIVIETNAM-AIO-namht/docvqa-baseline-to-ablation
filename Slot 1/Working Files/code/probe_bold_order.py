"""Hai tín hiệu nhận biết hàng in đậm có trùng nhau không?

Tín hiệu 1 (hợp lệ): đo độ dày nét từ ảnh.
Tín hiệu 2 (nghi vấn): hàng đậm luôn đứng đầu danh sách evidence.

Nếu hai tín hiệu trùng khít ở cả 535 câu thì tín hiệu 2 chỉ là quy ước sinh dữ
liệu — dùng nó là học thuộc mẫu, không phải suy luận. Nếu chúng KHÁC nhau thì
tín hiệu 2 là thông tin thật, và trần oracle được phép dùng.

    python probe_bold_order.py
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


def stroke(c):
    b = (c < INK)
    if b.shape[0] < 3 or b.shape[1] < 3:
        return 0.0
    core = b[1:-1, 1:-1] & b[:-2, 1:-1] & b[2:, 1:-1] & b[1:-1, :-2] & b[1:-1, 2:]
    n = b.sum()
    return float(core.sum()) / float(n) if n else 0.0


def main():
    cells = load_jsonl(DATA / "cell_annotations.jsonl")
    by_key = {(c["document_id"], c["page"], tuple(c["bbox"])): c for c in cells}
    vbl = [l for l in load_jsonl(DATA / "labels.jsonl")
           if l.get("reasoning_type") == "visual_bold_lookup"]

    agree = differ = n = 0
    img_ok_all = ord_ok_all = 0
    examples = []
    for lab in vbl:
        doc = lab["question_id"].rsplit("-q", 1)[0]

        def crop(cell):
            """Cắt từ ĐÚNG trang của ô. Bản đầu cứng trang 1 -> ô trang 2 bị cắt
            nhầm chỗ, mọi con số thấp hơn thực tế (xem probe_bold.py)."""
            arr = page_gray(doc, cell["page"])
            h, w = arr.shape
            x0, y0, x1, y1 = cell["bbox"]
            return arr[int(y0 * h):int(np.ceil(y1 * h)), int(x0 * w):int(np.ceil(x1 * w))]

        rows = defaultdict(list)
        for e in lab["evidence"]:
            c = by_key.get((doc, e["page"], tuple(e["bbox"])))
            if c:
                rows[(e["page"], round(e["bbox"][1], 6))].append(c)
        if len(rows) != 2:
            continue

        gold = next((k for k, g in rows.items() if any(c["is_bold"] for c in g)), None)
        if gold is None:
            continue

        # tín hiệu 1: bỏ phiếu theo cột
        votes = defaultdict(int)
        for k, g in rows.items():
            for c in g:
                other = [c2 for k2, g2 in rows.items() if k2 != k
                         for c2 in g2 if c2["column"] == c["column"]]
                if other:
                    votes[k] += stroke(crop(c)) > stroke(crop(other[0]))
        img_pick = max(votes, key=votes.get) if votes else None

        # tín hiệu 2: hàng của ô evidence ĐẦU TIÊN
        first = (lab["evidence"][0]["page"], round(lab["evidence"][0]["bbox"][1], 6))

        n += 1
        if img_pick == first:
            agree += 1
        else:
            differ += 1
            img_ok = img_pick == gold
            ord_ok = first == gold
            img_ok_all += img_ok
            ord_ok_all += ord_ok
            if len(examples) < 5:
                examples.append((lab["question_id"], img_ok, ord_ok))

    print(f"câu đo được            : {n}")
    print(f"ảnh và thứ tự TRÙNG    : {agree} = {100*agree/n:.2f}%")
    print(f"ảnh và thứ tự KHÁC     : {differ} = {100*differ/n:.2f}%")
    print()
    print(f"trong {differ} ca khác nhau: ảnh đúng {img_ok_all} ({100*img_ok_all/differ:.2f}%)"
          f" · thứ tự đúng {ord_ok_all} ({100*ord_ok_all/differ:.2f}%)")
    print()
    print("5 ca đầu (ảnh đúng?, thứ tự đúng?):")
    for qid, img_ok, ord_ok in examples:
        print(f"  {qid}  ảnh={img_ok}  thứ tự={ord_ok}")


if __name__ == "__main__":
    main()
