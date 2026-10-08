"""Probe CPU (KHÔNG cần GPU): tín hiệu đậm có sống sót qua phép gộp patch 14x14?

BỐI CẢNH
Qwen2.5-VL cắt ảnh thành patch 14x14 px rồi chiếu tuyến tính từng patch. sanity3
kết luận âm (model không đọc nổi nhãn trong ảnh). Còn lại hai nguyên nhân, dẫn
tới hai việc TRÁI NGƯỢC nhau:
  (a) PHÂN GIẢI — dòng chữ cao 48 px, nét ngang 2 px; một patch 14 px nuốt trọn
      cấu trúc nét, chênh đậm/nhạt chìm trong phép lấy trung bình.
      -> sửa bằng BIỂU DIỄN ĐẦU VÀO (phóng to). QLoRA không cần.
  (b) ViT VỨT NÉT — thông tin còn trong patch nhưng ViT không giữ.
      -> QLoRA đóng băng ViT cũng vô ích, cả Cấu hình D đổ.

PHÉP THỬ
Câu hỏi tách được ở tầng ảnh thuần, không cần nạp model: sau khi gộp thành khối
p x p, hai hàng ứng viên còn phân biệt được không?

Với mỗi cột có mặt ở CẢ HAI hàng ứng viên, cắt ô của hai hàng từ ảnh trang, gộp
thành khối 14x14 (và 28x28 = một token sau merge), rồi hỏi: thống kê của hàng
ĐẬM có lớn hơn hàng thường không? Chạy ở 1x và 4x.

    d' = |mean_A - mean_B| / sqrt((var_A + var_B)/2)

là mức tách được của hai phân bố mật độ patch — đo bằng chính đại lượng mà một
bộ đọc tuyến tính trên patch nhìn thấy. d' ~ 0 nghĩa là không bộ đọc nào tách nổi.

ĐỌC KẾT QUẢ (chốt TRƯỚC khi chạy, để không tự lừa)
  d' ở 1x ~ 0, ở 4x lớn hơn hẳn  -> PHÂN GIẢI là nút thắt. Đi tiếp Cấu hình D,
                                    nhưng phải phóng to ảnh đầu vào.
  d' ở 1x đã lớn, 4x y hệt      -> thông tin CÓ trong patch; nút thắt nằm SAU
                                    ViT (hoặc ở harness), không phải phân giải.
  d' ~ 0 ở CẢ HAI               -> gộp patch xoá tín hiệu, phóng to cũng vô ích
                                    => ghi kết luận âm cho Cấu hình D.

ponytail: chỉ đọc ảnh trang + OCR để GIẢI; `gold_bold` chỉ dùng để CHẤM điểm —
đúng ràng buộc ghi ở đầu `grid_ocr.py` và `audit_rule_system.py`.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from grid_ocr import INK_THRESHOLD, build_tables, page_gray, stroke_ratio  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "probe_d"

# 14 = patch ViT của Qwen2.5-VL; 28 = một token thị giác sau khi merge 2x2.
# (1, 1) là mốc thô: từng pixel một, tức mật độ mực nguyên bản.
KEYS = [(1, 1), (1, 14), (4, 14), (1, 28), (4, 28)]

STATS = {
    "mean": lambda t: float(t.mean()),
    "median": lambda t: float(np.median(t)),
    "q90": lambda t: float(np.quantile(t, 0.90)),
}


# ------------------------------------------------------------------ ảnh -> patch

def cell_gray(doc, page, bbox):
    """Ô cắt từ ảnh trang xám. Cùng phép cắt `grid_ocr.cell_stroke` đang dùng."""
    arr = page_gray(doc, page)
    h, w = arr.shape
    x0, y0, x1, y1 = bbox
    return arr[int(y0 * h):int(np.ceil(y1 * h)), int(x0 * w):int(np.ceil(x1 * w))]


def zoom(g, z):
    """Phóng `z` lần, LANCZOS — đúng phép `_load_pic` của harness chạy trên Colab.

    LANCZOS chứ không NEAREST: phép đo là mật độ mực, nội suy tuyến tính giữ được
    gradient mực/giấy, NEAREST thì nhân bản pixel thành khối vuông cứng.
    """
    if z == 1:
        return g
    from PIL import Image
    im = Image.fromarray(g)
    return np.array(im.resize((im.width * z, im.height * z), Image.LANCZOS))


def patch_ink(g, p):
    """-> mật độ mực từng khối p x p (bỏ phần lẻ ở mép). None nếu ô nhỏ hơn 1 khối."""
    b = g < INK_THRESHOLD
    ny, nx = b.shape[0] // p, b.shape[1] // p
    if ny < 1 or nx < 1:
        return None
    return b[:ny * p, :nx * p].reshape(ny, p, nx, p).mean(axis=(1, 3)).ravel()


# ------------------------------------------------------------------ phép đo

def collect(items):
    """-> [(pairs, gold)] với pairs = [(ô hàng 0, ô hàng 1)] theo từng cột chung."""
    out = []
    for it in items:
        gold = it["gold_bold"]
        if gold not in (0, 1) or len(it["cand"]) != 2:
            continue
        table = build_tables(it["doc"]).get((it["page"], it["table"]))
        if not table:
            continue
        rows = [c["row"] for c in it["cand"]]
        by_row = [{c["column"]: c for c in table
                   if c["row"] == r and not c["is_header"]} for r in rows]
        pairs = []
        for col in sorted(set(by_row[0]) & set(by_row[1])):
            a = cell_gray(it["doc"], it["page"], by_row[0][col]["bbox"])
            b = cell_gray(it["doc"], it["page"], by_row[1][col]["bbox"])
            if a.size and b.size:
                pairs.append((a, b))
        if pairs:
            out.append((pairs, gold))
    return out


def measure(samples):
    """Bỏ phiếu theo cột y như `grid_ocr.bold_row`, nhưng trên mật độ patch."""
    col_ok = {(k, s): 0 for k in KEYS for s in STATS}
    col_n = {(k, s): 0 for k in KEYS for s in STATS}
    it_ok = {(k, s): 0 for k in KEYS for s in STATS}
    it_n = {(k, s): 0 for k in KEYS for s in STATS}
    ds = {k: [] for k in KEYS}

    for pairs, gold in samples:
        for k in KEYS:
            z, p = k
            votes = {s: [0, 0] for s in STATS}
            for ga, gb in pairs:
                ta, tb = patch_ink(zoom(ga, z), p), patch_ink(zoom(gb, z), p)
                if ta is None or tb is None:
                    continue
                noise = float(np.sqrt((ta.var() + tb.var()) / 2))
                if noise > 0:
                    ds[k].append(abs(float(ta.mean()) - float(tb.mean())) / noise)
                for s, f in STATS.items():
                    va, vb = f(ta), f(tb)
                    if va > vb:
                        votes[s][0] += 1
                        col_n[(k, s)] += 1
                        col_ok[(k, s)] += (gold == 0)
                    elif vb > va:
                        votes[s][1] += 1
                        col_n[(k, s)] += 1
                        col_ok[(k, s)] += (gold == 1)
            for s in STATS:
                if votes[s][0] == votes[s][1]:
                    continue                      # hoà -> không mang thông tin
                it_n[(k, s)] += 1
                it_ok[(k, s)] += ((0 if votes[s][0] > votes[s][1] else 1) == gold)
    return col_ok, col_n, it_ok, it_n, ds


def stroke_baseline(samples):
    """Mốc so: chính `stroke_ratio` mà Cấu hình B đang dùng, trên cùng mẫu 120 câu."""
    ok = n = 0
    for pairs, gold in samples:
        votes = [0, 0]
        for ga, gb in pairs:
            sa, sb = stroke_ratio(ga), stroke_ratio(gb)
            if sa > sb:
                votes[0] += 1
                n += 1
                ok += (gold == 0)
            elif sb > sa:
                votes[1] += 1
                n += 1
                ok += (gold == 1)
        # không cộng vào n: mốc chỉ để so độ lớn, không phải bộ giải
    return ok, n


# ------------------------------------------------------------------ tự kiểm

def _demo():
    """Nét dày phải thắng nét mảnh ở MỌI mức phóng và mọi cỡ khối.

    Không kiểm được gì về model, chỉ chốt rằng phép đo không tự đảo dấu.
    """
    from PIL import Image, ImageDraw

    def bars(w):
        im = Image.new("L", (140, 56), 255)
        d = ImageDraw.Draw(im)
        for x in range(8, 132, 12):
            d.rectangle([x, 10, x + w - 1, 45], fill=0)
        return np.array(im)

    for z in (1, 4):
        for p in (1, 14, 28):
            thick = patch_ink(zoom(bars(4), z), p)
            thin = patch_ink(zoom(bars(2), z), p)
            assert thick is not None and thin is not None, (z, p)
            assert thick.mean() > thin.mean(), (z, p, thick.mean(), thin.mean())
    print("demo OK: nét dày > nét mảnh ở mọi (phóng, khối)")


# ------------------------------------------------------------------ main

def main():
    path = OUT / "items.jsonl"
    items = [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    samples = collect(items)
    print(f"{len(samples)}/{len(items)} câu dùng được (có >=1 cột chung giữa hai hàng)\n")

    col_ok, col_n, it_ok, it_n, ds = measure(samples)

    print("Bỏ phiếu theo CỘT (mỗi cột chung một phiếu) và theo CÂU (đa số cột thắng):\n")
    print(f"{'phóng':>6} {'khối':>5} | {'thống kê':>7} | {'cột đúng':>14} | {'câu đúng':>12} | {'d′ (trung vị)':>13}")
    print("-" * 78)
    for k in KEYS:
        z, p = k
        for s in STATS:
            c = f"{col_ok[(k,s)]}/{col_n[(k,s)]}"
            i = f"{it_ok[(k,s)]}/{it_n[(k,s)]}"
            pc = 100 * col_ok[(k, s)] / col_n[(k, s)] if col_n[(k, s)] else float("nan")
            pi = 100 * it_ok[(k, s)] / it_n[(k, s)] if it_n[(k, s)] else float("nan")
            d = f"{np.median(ds[k]):.3f}" if ds[k] else "—"
            print(f"{str(z)+'x':>6} {p:>5} | {s:>7} | {c:>8} {pc:5.1f}% | {i:>6} {pi:5.1f}% | {d:>13}")
        print("-" * 78)

    ok, n = stroke_baseline(samples)
    print(f"\nmốc so — `stroke_ratio` (bộ đo Cấu hình B đang dùng), theo cột: "
          f"{ok}/{n} = {100*ok/n:.1f}%")

    print("\nĐọc (chốt đã ghi ở đầu file):\n"
          "  mean/median/q90 Ở 1x ≈ Ở 4x, d′ cũng vậy  ->  thông tin KHÔNG mất khi\n"
          "      gộp patch; phóng to không thêm gì. Nút thắt nằm sau ViT.\n"
          "  d′ ở 4x LỚN HƠN HẲN 1x                   ->  PHÂN GIẢI là nút thắt.\n"
          "  d′ ~ 0 ở cả hai                          ->  gộp patch xoá tín hiệu,\n"
          "      phóng to vô ích => kết luận âm cho Cấu hình D.")


if __name__ == "__main__":
    _demo()
    main()
