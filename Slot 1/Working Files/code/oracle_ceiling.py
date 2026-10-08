"""Trần oracle — bản KHÔNG đọc file nhãn cấu trúc.

Bản cũ (audit_ceiling.py) tra text ô bằng cell_annotations.jsonl — file NHÃN.
File đó không tồn tại trên public_test/private_test, nên con số "trần oracle"
đo được không dùng được cho tập đích. Bản này thay bằng:

    text ô        <- ocr/*.json          (block text, tra theo bbox)
    (table, row)  <- gom block theo y0   (đã kiểm: 0 lỗi / 11.000 câu)
    thứ tự column <- sắp theo x0         (đã kiểm: 0 lỗi)
    is_bold       <- ĐO TỪ ẢNH (mật độ mực trong ô)

Chỉ còn đọc labels.jsonl để lấy gold evidence + đáp án — đó là ĐỊNH NGHĨA của
trần oracle ("điểm tối đa khi biết trước ô đúng"), không phải rò nhãn cấu trúc.

Tự kiểm tính hợp lệ: đổi tên cell_annotations.jsonl rồi chạy lại — phải ra
cùng kết quả.

Bảng in ra đếm KHỚP TUYỆT ĐỐI (chẩn đoán: dạng nào hỏng). Con số so được với
mốc baseline 95,45 là dòng ĐIỂM CUỘC THI ở cuối: trần oracle trả đúng ô vàng
nên F1 = 1,0, điểm = 0,85·ANLS + 0,15.

    python oracle_ceiling.py            # toàn bộ training_set
    python oracle_ceiling.py --split eval
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image

from anls import anls

sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parents[3]
DATA = BASE / "data" / "training_set"
SPLITS = Path(__file__).resolve().parent.parent / "splits"

# Ngưỡng tách mực/giấy khi đo độ đậm. Ảnh là scan tổng hợp nền sáng, nên
# Otsu không cần — 0.5*255 tách đúng trên toàn bộ mẫu đã thử.
INK_THRESHOLD = 128


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


# ------------------------------------------------------------------ OCR -> grid

def load_ocr(doc_id):
    """-> {block_id: block} với block đã thêm 'row'/'col' suy từ hình học."""
    path = DATA / "ocr" / f"{doc_id}.json"
    doc = json.loads(path.read_text(encoding="utf-8"))

    blocks = []
    for page in doc["pages"]:
        for b in page["blocks"]:
            b = dict(b)
            b["page"] = page["page"]
            blocks.append(b)

    # row: gom theo y0 (đỉnh ô). column: thứ tự theo x0 trong cùng một row.
    by_y = defaultdict(list)
    for b in blocks:
        by_y[(b["page"], round(b["bbox"][1], 6))].append(b)
    for row_key, row_blocks in by_y.items():
        for col, b in enumerate(sorted(row_blocks, key=lambda b: b["bbox"][0])):
            b["row_key"] = row_key
            b["col"] = col

    return {b["block_id"]: b for b in blocks}


def build_grid(ocr, evidence):
    """Gom các ô evidence thành các hàng logic, trái -> phải."""
    rows = defaultdict(list)
    for e in evidence:
        b = ocr.get(e["block_id"])
        if b is None:
            continue
        rows[b["row_key"]].append(b)
    return {k: sorted(v, key=lambda b: b["col"]) for k, v in rows.items()}


# ------------------------------------------------------------------ bold từ ảnh

@lru_cache(maxsize=4)
def _page_gray(doc_id, page):
    """Trang xám. Giữ 4 trang là đủ: mỗi tài liệu tối đa 2 trang."""
    path = DATA / "images" / f"{doc_id}_p{page:02d}.jpg"
    with Image.open(path) as im:
        return np.array(im.convert("L"))


def _stroke_ratio(crop):
    """Tỉ lệ pixel tối còn lại sau khi bào mòn 1 vòng -> dày nét.

    Mật độ mực thô chỉ được 70,84% vì ô nhiều chữ thì mực nhiều bất kể đậm.
    Phép này bù được, và bỏ phiếu theo cột (cùng cột, hàng nào dày hơn) đưa
    lên 83,55%. Đã thử 5 phép đo chuẩn hoá khác (probe_bold2.py, tốt nhất
    core/ink = 82,99%): không phép nào vượt ~84% => đây là trần thật của tín
    hiệu ảnh, không phải cài đặt tồi.
    """
    b = crop < INK_THRESHOLD
    if b.shape[0] < 3 or b.shape[1] < 3:
        return 0.0
    core = b[1:-1, 1:-1] & b[:-2, 1:-1] & b[2:, 1:-1] & b[1:-1, :-2] & b[1:-1, 2:]
    n = b.sum()
    return float(core.sum()) / float(n) if n else 0.0


def _cell_stroke(doc_id, cell):
    arr = _page_gray(doc_id, cell["page"])
    h, w = arr.shape
    x0, y0, x1, y1 = cell["bbox"]
    crop = arr[int(y0 * h):int(np.ceil(y1 * h)), int(x0 * w):int(np.ceil(x1 * w))]
    return _stroke_ratio(crop)


def pick_bold_row(doc_id, rows):
    """Hàng nào in đậm? Bỏ phiếu theo từng cột: cùng cột, hàng nào dày nét hơn.

    ponytail: bỏ tín hiệu "hàng đậm luôn đứng đầu evidence" — nó đúng 100%
    nhưng chỉ vì đó là quy ước sinh dữ liệu (khi lệch với ảnh thì ảnh luôn sai,
    xem probe_bold_order.py). Dùng nó là học thuộc mẫu, không phải suy luận.
    """
    stroke = {k: [(c, _cell_stroke(doc_id, c)) for c in g] for k, g in rows.items()}
    votes = defaultdict(int)
    for k, g in stroke.items():
        for c, s in g:
            other = [s2 for k2, g2 in stroke.items() if k2 != k
                     for c2, s2 in g2 if c2["col"] == c["col"]]
            if other and s > other[0]:
                votes[k] += 1
    return max(votes, key=votes.get) if votes else None


# ------------------------------------------------------------------ số & solver

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


def label_of(cells):
    """Tên hàng = ô trái nhất không phải số."""
    for c in cells:
        if to_number(c["text"]) is None:
            return c["text"]
    return cells[0]["text"] if cells else None


def solve(rt, question, rows, doc_id):
    if rt in ("sum", "cross_page_sum"):
        vals = [to_number(cs[-1]["text"]) for cs in rows.values()]
        vals = [v for v in vals if v is not None]
        return fmt(sum(vals)) if vals else None

    if rt == "lookup":
        return list(rows.values())[0][-1]["text"] if len(rows) == 1 else None

    if rt == "visual_bold_lookup":
        k = pick_bold_row(doc_id, rows)
        return rows[k][-1]["text"] if k is not None else None

    if rt == "count":
        return fmt(len(rows))

    if rt in ("argmax", "argmin"):
        # evidence chỉ chứa hàng thắng -> đáp án là tên hàng đó
        only = list(rows.values())[0]
        return label_of(only)

    if rt == "compare":
        if len(rows) != 2:
            return None
        (_, c1), (_, c2) = list(rows.items())
        v1, v2 = to_number(c1[-1]["text"]), to_number(c2[-1]["text"])
        if v1 is None or v2 is None:
            return None
        smaller = bool(re.search(r"nhỏ hơn|thấp hơn|ít hơn", question, re.I))
        return label_of(c1 if ((v1 < v2) == smaller) else c2)

    return None


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="all", choices=["all", "dev", "eval"])
    args = ap.parse_args()

    if args.split != "all":
        keep = set((SPLITS / f"{args.split}_docs.txt").read_text(encoding="utf-8").split())
    else:
        keep = None

    labels = load_jsonl(DATA / "labels.jsonl")
    questions = {q["question_id"]: q["question"] for q in load_jsonl(DATA / "questions.jsonl")}

    ocr_cache = {}
    stats = defaultdict(lambda: [0, 0])
    anls_sum = 0.0
    misses = []

    for lab in labels:
        doc_id = lab["question_id"].rsplit("-q", 1)[0]
        if keep is not None and doc_id not in keep:
            continue

        if doc_id not in ocr_cache:
            ocr_cache[doc_id] = load_ocr(doc_id)
        ocr = ocr_cache[doc_id]

        rt = lab.get("reasoning_type")
        rows = build_grid(ocr, lab["evidence"])
        got = solve(rt, questions[lab["question_id"]], rows, doc_id)
        gold = lab["answers"][0]

        stats[rt][1] += 1
        anls_sum += anls(got or "", lab["answers"])
        if got is not None and got.strip().lower() == gold.strip().lower():
            stats[rt][0] += 1
        else:
            misses.append((rt, lab["question_id"], gold, got))

    print(f"===== TRẦN ORACLE — không đọc cell_annotations  (split: {args.split}) =====")
    print(f"{'type':22s}{'exact':>12s}{'rate':>9s}{'n':>8s}")
    ok_t = n_t = 0
    for rt, (ok, n) in sorted(stats.items(), key=lambda kv: -kv[1][1]):
        ok_t += ok
        n_t += n
        print(f"{rt:22s}{ok:6d}/{n:<5d}{100*ok/n:8.2f}%{n:8d}")
    print(f"{'ALL':22s}{ok_t:6d}/{n_t:<5d}{100*ok_t/n_t:8.2f}%{n_t:8d}")

    # Trần oracle biết trước ô vàng => evidence luôn khớp => F1 = 1,0.
    anls_avg = anls_sum / n_t
    print(f"\nĐIỂM CUỘC THI (trần oracle): 0,85·ANLS + 0,15·F1 = "
          f"0,85·{anls_avg:.4f} + 0,15·1,0 = {100*(0.85*anls_avg + 0.15):.2f}")
    print(f"ANLS trung bình = {anls_avg:.4f}  (khớp tuyệt đối {100*ok_t/n_t:.2f}%)")

    print(f"\n===== misses ({len(misses)}) =====")
    for rt, qid, gold, got in misses[:20]:
        print(f"  [{rt}] {qid} gold={gold!r} got={got!r}")


if __name__ == "__main__":
    main()
