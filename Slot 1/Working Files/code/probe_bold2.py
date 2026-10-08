"""Thử các phép đo độ đậm chuẩn hoá — tìm phép đo tốt nhất từ ảnh.

Ý tưởng: độ dày nét thô bị lẫn với cỡ chữ. Chuẩn hoá theo chiều cao chữ để
so "đậm" chứ không so "to".

Kết quả (sau khi sửa lỗi cứng trang 1 — xem probe_bold.py):
    ink/bbox 76,82% · run/h 76,26% · run 80,93% · core/ink 82,99% · core/h 81,50%
Phép tốt nhất `core/ink` trùng khít con số harness đo được (82,99%) ⇒ không
phép đo ảnh nào vượt ~84%: đây là trần của tín hiệu ảnh.

    python probe_bold2.py
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


def runs_h(b):
    """Độ dài trung bình của đoạn mực liên tiếp theo chiều ngang."""
    tot = cnt = 0
    for row in b:
        d = np.diff(np.concatenate(([0], row.view(np.int8), [0])))
        starts = np.flatnonzero(d == 1)
        ends = np.flatnonzero(d == -1)
        if len(starts):
            tot += int((ends - starts).sum())
            cnt += len(starts)
    return tot / cnt if cnt else 0.0


def metrics(c):
    """-> dict tên -> điểm 'đậm hơn thì cao hơn'."""
    b = c < INK
    if not b.any():
        return {}
    ys, xs = np.nonzero(b)
    h = ys.max() - ys.min() + 1
    w = xs.max() - xs.min() + 1
    n = int(b.sum())

    core = b[1:-1, 1:-1] & b[:-2, 1:-1] & b[2:, 1:-1] & b[1:-1, :-2] & b[1:-1, 2:] \
        if b.shape[0] > 2 and b.shape[1] > 2 else np.zeros((1, 1), bool)

    r = runs_h(b)
    return {
        "ink/bbox": n / (h * w),          # độ đặc của ô chữ
        "run/h": r / h,                   # dày nét chuẩn theo chiều cao
        "run": r,                         # dày nét thô
        "core/ink": core.sum() / n,       # tỉ lệ lõi
        "core/h": core.sum() / h,         # lõi chuẩn theo chiều cao
    }


def main():
    cells = load_jsonl(DATA / "cell_annotations.jsonl")
    by_key = {(c["document_id"], c["page"], tuple(c["bbox"])): c for c in cells}
    vbl = [l for l in load_jsonl(DATA / "labels.jsonl")
           if l.get("reasoning_type") == "visual_bold_lookup"]

    names = ["ink/bbox", "run/h", "run", "core/ink", "core/h"]
    hit = defaultdict(int)
    n = 0

    for lab in vbl:
        doc = lab["question_id"].rsplit("-q", 1)[0]

        def crop(cell):
            """Cắt từ ĐÚNG trang của ô. Bản đầu cứng trang 1 -> ô trang 2 bị cắt
            nhầm chỗ, mọi con số thấp hơn thực tế (xem probe_bold.py)."""
            arr = page_gray(doc, cell["page"])
            H, W = arr.shape
            x0, y0, x1, y1 = cell["bbox"]
            return arr[int(y0 * H):int(np.ceil(y1 * H)), int(x0 * W):int(np.ceil(x1 * W))]

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

        n += 1
        cell_m = {k: [(c, metrics(crop(c))) for c in g] for k, g in rows.items()}
        for name in names:
            votes = defaultdict(int)
            for k, g in rows.items():
                for c, m in cell_m[k]:
                    if name not in m:
                        continue
                    other = [(c2, m2) for k2 in rows if k2 != k
                             for c2, m2 in cell_m[k2] if c2["column"] == c["column"] and name in m2]
                    if other and m[name] > other[0][1][name]:
                        votes[k] += 1
            if votes and max(votes, key=votes.get) == gold:
                hit[name] += 1

    print(f"visual_bold_lookup: {n} câu\n")
    for name in names:
        print(f"  {name:10s} {hit[name]:4d}/{n} = {100*hit[name]/n:6.2f}%")
    best = max(names, key=lambda k: hit[k])
    print(f"\n  tốt nhất: {best}")


if __name__ == "__main__":
    main()
