"""PROBE KHẢ THI — Qwen2.5-VL có đọc chữ đậm tốt hơn trần tín hiệu ảnh 82,99%?

Đây KHÔNG phải solver, không phải Cấu hình D. Nó là một phép đo để trả lời đúng
một câu: VLM zero-shot chọn đúng hàng in đậm hơn `grid_ocr.bold_row()` (đo độ dày
nét, trần 82,99%) không? Kết quả quyết định có đáng bỏ công dựng D + QLoRA không.

  Có  -> QLoRA trên 535 mẫu là bước tiếp theo hợp lý.
  Không -> kết luận âm có bằng chứng, giống nhánh C, tiết kiệm cả tuần.

Ba pha, chạy ở hai máy (model nặng chạy Colab, 4 GB VRAM local không đủ).
Dữ liệu đi qua Drive, không đóng gói zip:
  --extract  (local) : cắt rời từng hàng ứng viên, xếp chồng thành 2 dải
  --run      (Colab) : Qwen2.5-VL-3B zero-shot       -> probe_d/preds.jsonl
  --score    (local) : ráp lựa chọn của VLM vào ĐÚNG nhánh BOLD của Cấu hình B,
                       chấm bằng anls + evidence_f1 -> so trực tiếp với 0,831

Ảnh đưa cho VLM ghép 2 dải của 2 hàng, ngăn bởi khoảng trắng. Mỗi dải được đóng
khung và mang một CHỮ CÁI vẽ thẳng lên ảnh (A/B). Bản đầu nhồi mô tả hàng vào
prompt — nhưng `groups()` trả về cả văn xuôi câu hỏi ("hai dòng Điểm bán ..."),
nên VLM nhận một mệnh đề vô nghĩa và trả lời "A" cho có (119/120).

Bản thứ hai bỏ mô tả nhưng cũng KHÔNG vẽ gì lên ảnh: prompt khẳng định "dải
TRÊN là (A)" bằng chữ, còn ảnh thì trống. Model trả lời "A" cho 120/120 ảnh —
đó là phản ứng hợp lý trước thông tin thiếu, không phải bằng chứng nó không so
được độ đậm. Nhãn vẽ lên ảnh gỡ đúng cái nhiễu đó.

`cell_annotations.jsonl` chỉ được đọc ở pha score, để biết VLM chọn đúng hàng
vàng hay không (chẩn đoán). Không có đường nào để nó chảy vào dự đoán.
"""

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

# ponytail: console Windows mặc định cp1258, in tiếng Việt là vỡ. Colab bọc
# stdout bằng OutStream không có reconfigure -> phải guard.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# ponytail: import nặng để trong hàm. Pha `run` chạy trên Colab chỉ có zip
# (items.jsonl + crops/), không có grid_ocr/audit_rule_system — import ở đây là
# vỡ ngay trên Colab.
SPLITS = HERE.parent / "splits"
OUT = HERE.parent / "probe_d"
BOLD_TYPE = "visual_bold_lookup"
# ponytail: tăng số này mỗi khi đổi schema items.jsonl. Drive giữ bản cũ rất dễ
# (đã xảy ra 1 lần: Colab chạy items.jsonl cũ + code cũ -> KeyError 'desc' khó
# hiểu). Chốt này biến lỗi mờ thành một câu chỉ đúng việc phải làm.
# schema 3: thêm "band_box" (bbox từng dải trong canvas) — sanity4 cần nó để vẽ
# lại nhãn A/B lên bản đảo mà không phải suy từ band_h + GAP.
SCHEMA = 3
# ponytail: SCHEMA ở trên canh items.jsonl, số này canh CODE. Tách riêng vì hai
# thứ lệch nhau độc lập. Tăng khi sửa thứ mà bản cũ trên Drive vẫn "trông hợp lệ"
# — vd `cmd_sanity2` thiếu `empty_cache()` làm Cell 3 OOM, mà Cell 2 vẫn qua vì
# hàm vẫn tồn tại. Notebook assert đúng số này để bắt bản cũ ngay tại Cell 2.
CODE_VERSION = 8
N_SAMPLE = 120
SEED = 20261007
# Bề dày khung vẽ quanh mỗi dải. Đủ để mắt người thấy đó là một dải tách rời,
# đủ mảnh để không làm dày nét chữ bên trong (bài toán đang đo chính là độ dày
# nét). 3 px trên ảnh ~1500 px rộng là mức vô hại.
FRAME = 3
# Bề rộng cột nhãn bên trái. 64 px đủ cho một chữ cái cao bằng cả dải (~40 px),
# tức lớn hơn hẳn một patch 28 px của Qwen — nhãn phải chắc chắn nhìn thấy được,
# nếu không lại đo phải "model không thấy nhãn" thay vì "model không so được nét".
GUTTER = 64
# ponytail: crop lấy TRỌN ô (không nới). Nới MARGIN làm bbox hai hàng kề nhau
# chồng lên nhau 2*MARGIN (đo được: 30/120 ảnh, phần chồng = đúng 2*MARGIN) —
# dải dưới lòi cả hàng bên cạnh vào, câu hỏi "dải nào đậm hơn" thành mơ hồ.
# Bản cũ đã đưa ảnh hỏng đó cho model. Muốn thấy chữ trọn vẹn thì nới DỌC lên
# rồi CẮT phần chồng ở giữa, nhưng ô OCR đã vừa khít chữ nên chưa cần.
MARGIN = 0.0
# Hệ số phóng to cho probe #4. Ảnh đã đo: dòng chữ cao 48 px, nét ngang dày
# 2 px; ViT Qwen gộp patch 14 px nên một dòng chỉ trải 3,4 patch và chênh
# đậm-nhạt chỉ ~10% một patch. 4x đưa nét lên 8 px = 57% một patch.
ZOOM = 4
# Trần pixel của Qwen2.5-VL-3B, lấy từ `preprocessor_config.json` của chính
# checkpoint đó (`max_pixels: 12845056`). KHÔNG phải 1.003.520 — đó là mặc định
# của class trong transformers, và checkpoint này ghi đè nó cao hơn hẳn. Bản đầu
# của hằng số này chép nhầm con số mặc định, thành ra đi HẠ trần của model.
#
# Hệ quả: canvas 4x ở đây là 6,8M px, VỪA KHÍT dưới trần thật => probe #4 không
# cần nâng trần chút nào. Giữ hằng số lại làm mốc assert trước khi nạp model
# (nạp mất ~2 phút, sai số học ở đây thì phí).
ZOOM_MAX_PX = 12_845_056


# --------------------------------------------------------------- chọn bảng

def resolve(doc, q, tabs, docs):
    """(table, page, tbl, ac, G) — đúng bước chọn bảng của nhánh BOLD.

    ponytail: chép ~12 dòng từ `audit_rule_system.main` thay vì refactor hàm đó.
    Cấu hình B đang đóng băng (WEEK03 §2 "không đổi một dòng code nào"), và probe
    này là đồ bỏ. Chép rẻ hơn sửa file đang đóng băng.
    """
    from audit_rule_system import ASKED, PAGE, TBL, find_col, groups, match_rows
    pages = [int(x) for x in PAGE.findall(q)]
    mt = TBL.search(q)
    asked = next((a.group(1) for a in (r.search(q) for r in ASKED) if a), None)
    cands = [(p, int(mt.group(1))) for p in pages[:1]] if mt else \
            [(p, t) for p in pages[:1] for (pp, t) in docs[doc] if pp == p]
    for page, tbl in cands:
        table = tabs[doc].get((page, tbl))
        if not table:
            continue
        ac = find_col(table, asked)
        G = groups(q, table)
        if not G:
            continue
        rr, _ = match_rows(table, G[0])
        if rr is None:
            continue
        return table, page, tbl, ac, G
    return None


def candidates(table, G):
    """[{row, cells}] theo đúng thứ tự nhóm trong câu — 2 ứng viên."""
    from audit_rule_system import match_rows
    out = []
    for grp in G:
        rr, cells = match_rows(table, grp)
        if not rr:
            continue
        out.append({"row": min(rr), "cells": cells})
    return out


def crop_bbox(table, rows):
    """Bao lồi các ô của `rows`, nới MARGIN, kẹp vào trang."""
    xs0, ys0, xs1, ys1 = [], [], [], []
    for c in table:
        if c["row"] in rows:
            x0, y0, x1, y1 = c["bbox"]
            xs0.append(x0); ys0.append(y0); xs1.append(x1); ys1.append(y1)
    if not xs0:
        return None
    return (max(0.0, min(xs0) - MARGIN), max(0.0, min(ys0) - MARGIN),
            min(1.0, max(xs1) + MARGIN), min(1.0, max(ys1) + MARGIN))


def gold_bold(table, cands, ann):
    """Chỉ số ứng viên có TOÀN BỘ ô in đậm theo nhãn vàng, hoặc None.

    Lọc theo CẢ (page, table, row) — một trang có thể có 2 bảng cùng đánh số
    hàng, thiếu `table` là hàng của bảng kia lẫn vào và `all()` luôn sai.
    """
    page, tbl = table[0]["page"], table[0]["table"]
    for i, c in enumerate(cands):
        cells = [a for a in ann if a["page"] == page and a["table"] == tbl
                 and a["row"] == c["row"] and not a["is_header"]]
        if cells and all(a["is_bold"] for a in cells):
            return i
    return None


# --------------------------------------------------------------- pha extract

def _compose(bands, labels):
    """Dán các dải vào canvas, mỗi dải một khung + một nhãn ở cột trái.

    ponytail: nhãn nằm ở CỘT RIÊNG bên trái, không vẽ đè lên chữ. Vẽ đè thì
    `_variant` không có cách nào đổi nhãn mà không đụng vào pixel chữ — đúng
    thứ đang được đo. Cột nhãn rộng bằng chiều cao dải nên chữ cái to bằng cả
    dải: cỡ đó mới chắc vượt một patch 28 px của Qwen.
    """
    from PIL import Image, ImageDraw, ImageFont

    gap = 24                      # đủ rộng để mắt người tách hai dải
    w = GUTTER + max(b.width for b in bands)
    h = sum(b.height for b in bands) + gap * (len(bands) - 1)
    canvas = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(canvas)
    boxes, y = [], 0
    for b, lab in zip(bands, labels):
        canvas.paste(b, (GUTTER, y))
        d.rectangle([GUTTER, y, GUTTER + b.width - 1, y + b.height - 1],
                    outline=(0, 0, 0), width=FRAME)
        # `load_default(size=)` có từ Pillow 10.1; máy này 12.1.
        f = ImageFont.load_default(size=max(22, min(GUTTER - 8, b.height)))
        d.text((GUTTER // 2, y + b.height // 2), lab, fill=(0, 0, 0),
               font=f, anchor="mm")
        boxes.append([GUTTER, y, GUTTER + b.width, y + b.height])
        y += b.height + gap
    return canvas, boxes


def _variant(it, order, labels):
    """Dựng lại canvas từ PNG đã lưu. `order` = thứ tự dải, `labels` = nhãn.

    Cắt lại từ ảnh đã lưu chứ không cắt lại từ trang: Colab chỉ có items.jsonl
    + crops/, không có grid_ocr. `band_box` bắt đầu tại x=GUTTER nên phần cắt
    KHÔNG dính nhãn cũ — dựng lại được bao nhiêu lần cũng sạch.
    """
    from PIL import Image

    im = Image.open(OUT / it["crop"]).convert("RGB")
    bands = [im.crop(tuple(b)) for b in it["band_box"]]
    return _compose([bands[k] for k in order], labels)[0]


def stack_rows(doc, page, table, rows):
    """Cắt RIÊNG từng hàng, xếp chồng thành các dải, MỖI DẢI MANG MỘT CHỮ CÁI
    vẽ lên ảnh.

    ponytail: bản đầu cắt bao lồi 2 hàng — nhưng bbox là hình chữ nhật nên kéo
    theo mọi hàng nằm giữa (đo được: 6 hàng), và model phải tự định vị đúng 2
    hàng trong ảnh. Đó là bài toán grounding, không phải đọc chữ đậm. Cắt rời
    từng hàng rồi xếp chồng khử luôn grounding: model chỉ còn phải SO SÁNH.
    Cùng một trang, cùng tỉ lệ px nên so độ dày nét là hợp lệ.

    ponytail: nhãn A/B VẼ LÊN ẢNH, không chỉ nằm trong prompt. Bản trước để
    prompt tự khẳng định "dải TRÊN là (A)" còn ảnh trống — model trả "A" cho
    120/120, không tách được "không so được độ đậm" khỏi "chọn phương án được
    nhắc trước". Nhãn nằm trong ảnh thì nó DÍNH theo dải, nên phép đảo dải mới
    đo được cái cần đo (xem `cmd_sanity3`).
    """
    from PIL import Image

    from grid_ocr import DATA

    bands = []
    with Image.open(DATA / "images" / f"{doc}_p{page:02d}.jpg") as im:
        W, H = im.size
        for r in rows:
            bb = crop_bbox(table, {r})
            if not bb:
                return None, None, None
            px = (int(bb[0] * W), int(bb[1] * H),
                  int(round(bb[2] * W)), int(round(bb[3] * H)))
            bands.append(im.crop(px))

    canvas, boxes = _compose(bands, ["AB"[i] for i in range(len(bands))])
    return canvas, [b.height for b in bands], boxes


def cmd_extract(args):
    from grid_ocr import DATA, build_tables, load_jsonl

    keep = set((SPLITS / "dev_docs.txt").read_text(encoding="utf-8").split())
    labels = load_jsonl(DATA / "labels.jsonl")
    questions = {q["question_id"]: q["question"] for q in load_jsonl(DATA / "questions.jsonl")}
    ann = defaultdict(list)
    for a in load_jsonl(DATA / "cell_annotations.jsonl"):
        ann[a["document_id"]].append(a)

    pool = [l for l in labels
            if l["reasoning_type"] == BOLD_TYPE and l["question_id"].rsplit("-q", 1)[0] in keep]
    random.Random(SEED).shuffle(pool)
    pool = pool[:N_SAMPLE]

    tabs, docs = {}, defaultdict(set)
    for lab in pool:
        doc = lab["question_id"].rsplit("-q", 1)[0]
        if doc not in tabs:
            mine = build_tables(doc)
            tabs[doc] = mine
            docs[doc] = set(mine)

    OUT.mkdir(exist_ok=True)
    (OUT / "crops").mkdir(exist_ok=True)
    items, skip = [], defaultdict(int)
    for lab in pool:
        qid = lab["question_id"]
        doc = qid.rsplit("-q", 1)[0]
        got = resolve(doc, questions[qid], tabs, docs)
        if not got:
            skip["khong chon duoc bang"] += 1
            continue
        table, page, tbl, ac, G = got
        cands = candidates(table, G)
        if len(cands) < 2:
            skip[f"chi {len(cands)} ung vien"] += 1
            continue
        # Thứ tự dải = thứ tự nhóm trong câu, nên dải đầu mang nhãn (A).
        canvas, heights, boxes = stack_rows(doc, page, table, [c["row"] for c in cands])
        if canvas is None:
            skip["khong co bbox"] += 1
            continue
        name = f"crops/{qid}.png"
        canvas.save(OUT / name)

        items.append({
            "schema": SCHEMA,
            "qid": qid, "doc": doc, "page": page, "table": tbl, "crop": name,
            "band_h": heights, "band_box": boxes,
            "cand": [{"row": c["row"]} for c in cands],
            "gold_bold": gold_bold(table, cands, ann[doc]),
        })

    with (OUT / "items.jsonl").open("w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")

    print(f"vbl trong dev: {len(pool)} cau lấy mẫu / {sum(1 for l in labels if l['reasoning_type']==BOLD_TYPE and l['question_id'].rsplit('-q',1)[0] in keep)} cau dev")
    print(f"ghi {len(items)} item -> {OUT/'items.jsonl'}")
    for k, v in skip.items():
        print(f"  bỏ {v:4d}  {k}")
    if items:
        h = [sum(it["band_h"]) for it in items]
        print(f"ảnh xếp chồng: cao {min(h)}–{max(h)} px, "
              f"số dải {sorted({len(it['band_h']) for it in items})}")
        print(f"nhãn vàng chọn được hàng đậm: "
              f"{sum(1 for it in items if it['gold_bold'] is not None)}/{len(items)}")
    print(f"crop -> {OUT/'crops'}   (đồng bộ lên Drive rồi chạy Colab)")

    # Chốt kiểm chạy được ở máy, KHÔNG cần model: `cmd_sanity3` tin vào hai
    # điều — dựng lại canvas từ band_box ra đúng ảnh đã lưu, và đổi nhãn thì
    # ảnh phải khác. Cả hai vỡ im lặng (ảnh vẫn "trông hợp lệ") nên phải đo.
    if items:
        import numpy as np
        from PIL import Image
        same = sum(np.array_equal(np.asarray(Image.open(OUT / it["crop"]).convert("RGB")),
                                  np.asarray(_variant(it, [0, 1], ["A", "B"]).convert("RGB")))
                   for it in items)
        diff = sum(not np.array_equal(np.asarray(Image.open(OUT / it["crop"]).convert("RGB")),
                                      np.asarray(_variant(it, [0, 1], ["B", "A"]).convert("RGB")))
                   for it in items)
        assert same == len(items), f"dựng lại canvas lệch ảnh gốc: {len(items)-same} ảnh"
        assert diff == len(items), f"đổi nhãn mà ảnh không đổi: {len(items)-diff} ảnh"
        print(f"chốt: dựng lại khớp ảnh gốc {same}/{len(items)} · "
              f"đổi nhãn khác ảnh gốc {diff}/{len(items)}")


# --------------------------------------------------------------- pha run (Colab)

def load_items():
    """Đọc items.jsonl, chặn ngay nếu là bản schema cũ.

    Không có chốt này thì bản cũ vỡ bằng `KeyError: 'desc'` ở giữa vòng lặp —
    đúng cái đã xảy ra trên Colab, và thông báo lỗi chẳng nói gì về nguyên nhân
    thật (Drive còn file cũ).
    """
    items = [json.loads(l) for l in (OUT / "items.jsonl").open(encoding="utf-8")]
    if items and items[0].get("schema") != SCHEMA:
        raise SystemExit(
            f"items.jsonl là bản CŨ (schema={items[0].get('schema')}, cần {SCHEMA}).\n"
            f"Chạy lại ở máy:  python code/probe_vlm_bold.py extract\n"
            f"rồi đồng bộ {OUT/'items.jsonl'} + {OUT/'crops'} lên Drive.")
    return items


PROMPT = """Ảnh ghép hai dải cắt ra từ hai dòng của cùng một bảng.
Mỗi dải được đóng khung và có sẵn một chữ cái in bên trái: dải có chữ (A) và
dải có chữ (B). Hai dải cách nhau một khoảng trắng.

Dải nào được in ĐẬM (nét chữ đậm hơn rõ rệt)? Chỉ trả lời một chữ cái: A hoặc B."""


def parse_ab(raw):
    """'A'/'B' trong câu trả lời -> 0/1, hoặc None nếu không có.

    ponytail: chỉ nhận chữ cái ĐẦU TIÊN đứng riêng (`\\b`). Văn xuôi tiếng Việt
    đầy chữ "a"/"A" ("Ảnh ...", "Dòng A ...") nên dò chuỗi con là bắt bừa. Đây
    là dòng dễ vỡ nhất của dụng cụ đo — để một chỗ, không chép hai bản.
    """
    import re
    m = re.search(r"\b([AB])\b", raw.upper())
    return "AB".index(m.group(1)) if m else None


def cmd_run(args):
    model, proc, _ = _load_model(args.quant4)

    items = load_items()
    preds = []
    for i, it in enumerate(items, 1):
        raw = _ask(model, proc, OUT / it["crop"], PROMPT, 8)
        pick = parse_ab(raw)
        preds.append({"qid": it["qid"], "pick": pick, "raw": raw})
        print(f"[{i}/{len(items)}] {it['qid']} -> {raw!r} pick={pick}", flush=True)

    with (OUT / "preds.jsonl").open("w", encoding="utf-8") as f:
        for p in preds:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"ghi {len(preds)} dự đoán -> {OUT/'preds.jsonl'}")


# --------------------------------------------------------------- pha score

def cmd_score(args):
    from grid_ocr import DATA, bold_row, build_tables, fill_bold, load_jsonl
    from audit_rule_system import grid
    from anls import anls
    from evidence_f1 import evidence_f1

    labels = {l["question_id"]: l for l in load_jsonl(DATA / "labels.jsonl")}
    questions = {q["question_id"]: q["question"] for q in load_jsonl(DATA / "questions.jsonl")}

    items = load_items()
    preds = {json.loads(l)["qid"]: json.loads(l)
             for l in (OUT / "preds.jsonl").open(encoding="utf-8")}

    tabs, docs = {}, defaultdict(set)
    for it in items:
        if it["doc"] not in tabs:
            mine = build_tables(it["doc"])
            tabs[it["doc"]] = mine
            docs[it["doc"]] = set(mine)

    arms = {"B (độ dày nét)": {}, "D (Qwen2.5-VL)": {}}
    hit_row = {"B (độ dày nét)": 0, "D (Qwen2.5-VL)": 0}
    no_pick = 0

    for it in items:
        lab = labels[it["qid"]]
        table, page, tbl, ac, G = resolve(it["doc"], questions[it["qid"]], tabs, docs)
        cands = candidates(table, G)
        assert [c["row"] for c in cands] == [c["row"] for c in it["cand"]], it["qid"]
        gg = grid(table)

        # Nhánh B: đúng hàm đang chạy trong Cấu hình B, không sửa gì.
        cand_rows = {c["row"] for c in cands}
        fill_bold(it["doc"], table, cand_rows)
        b_row = bold_row(it["doc"], table, cand_rows)
        picks = {"B (độ dày nét)": next((i for i, c in enumerate(cands) if c["row"] == b_row), None)}

        p = preds[it["qid"]]["pick"]
        if p is None:
            no_pick += 1
        picks["D (Qwen2.5-VL)"] = p

        for arm, pick in picks.items():
            if pick is None:
                arms[arm][it["qid"]] = (0.0, 0.0)
                continue
            if pick == it["gold_bold"]:
                hit_row[arm] += 1
            # Ráp vào ĐÚNG nhánh BOLD của audit_rule_system, chỉ thay nguồn chọn
            # hàng. Cùng một luật dựng evidence cho cả hai nhánh ⇒ so sánh sạch.
            win = cands[pick]
            r = win["row"]
            pred_ans = gg[(r, ac)]["clean_text"] if ac is not None and (r, ac) in gg else None
            lose = [min([c for (r3, _), c in gg.items() if r3 == c2["row"]],
                        key=lambda c: c["column"])
                    for c2 in cands if c2["row"] != r
                    if any(r3 == c2["row"] for r3, _ in gg)]
            pred_ev = win["cells"] + ([gg[(r, ac)]] if ac is not None and (r, ac) in gg else []) + lose
            a = anls(pred_ans or "", lab["answers"])
            ef = evidence_f1(pred_ev, lab["evidence"]) if pred_ev else 0.0
            arms[arm][it["qid"]] = (a, ef)

    n = len(items)
    print(f"===== PROBE KHẢ THI — {n} câu visual_bold_lookup, split dev =====")
    print("ảnh ghép 2 dải, nhãn A/B VẼ TRÊN ẢNH (cột trái). VLM zero-shot.\n")
    print(f"{'nhánh':22s}{'ANLS':>8s}{'EvF1':>8s}{'điểm':>8s}{'chọn đúng hàng':>16s}")
    for arm in arms:
        a = sum(v[0] for v in arms[arm].values()) / n
        e = sum(v[1] for v in arms[arm].values()) / n
        print(f"{arm:22s}{a:8.3f}{e:8.3f}{0.85*a+0.15*e:8.3f}"
              f"{f'{hit_row[arm]}/{n}':>16s}")
    print(f"\nVLM không trả lời được A/B: {no_pick}/{n}")
    d = sum(v[0] for v in arms["D (Qwen2.5-VL)"].values()) / n
    de = sum(v[1] for v in arms["D (Qwen2.5-VL)"].values()) / n
    b = sum(v[0] for v in arms["B (độ dày nét)"].values()) / n
    be = sum(v[1] for v in arms["B (độ dày nét)"].values()) / n
    print(f"chênh lệch D − B: {(0.85*d+0.15*de) - (0.85*b+0.15*be):+.3f} điểm")
    print(f"\nQuyết định: ≥ +0,03 → đáng dựng D + QLoRA.  ≤ 0 → kết luận âm, dừng.")


# ------------------------------------------------- pha sanity (Colab, chẩn đoán)

# Ba câu hỏi trên CÙNG một ảnh. Câu 1–2 là câu buộc phải đúng được nếu model
# thật sự nhìn ảnh (đọc chữ). Câu 3 là câu đang nghi ngờ. Đọc được chữ mà câu 3
# vẫn hằng số => lỗi ở tầng SO SÁNH. Không đọc nổi chữ => lỗi ở tầng NHÌN.
# Cả hai đều là kết luận về DỤNG CỤ ĐO, không phải về Qwen2.5-VL.
SANITY_PROMPTS = [
    ("doc_A", "Chép lại nguyên văn dòng chữ trong dải (A) của ảnh. Bỏ qua chữ cái "
              "(A) in ở đầu dải. Không giải thích, không thêm gì."),
    ("doc_B", "Chép lại nguyên văn dòng chữ trong dải (B) của ảnh. Bỏ qua chữ cái "
              "(B) in ở đầu dải. Không giải thích, không thêm gì."),
    ("so_dam", PROMPT),
]


def _budget_slot(ip):
    """-> (vật chứa trần, tên) hoặc (None, ""). Dò bằng subscript, KHÔNG isinstance.

    Hai dạng API thật, đã gặp cả hai:
      transformers cũ : thuộc tính phẳng `max_pixels`
      transformers 5.x: `size["longest_edge"]`. `max_pixels` chỉ còn là kwarg của
                        `__init__`, không lưu thành thuộc tính (đã nổ ở Colab 5.18).

    ponytail: bản trước lọc bằng `isinstance(size, dict)` và TRƯỢT, vì `size` ở
    5.x là `SizeDict` — dataclass thường trong `image_utils`, không phải dict con.
    Nó có `__getitem__`/`__setitem__`, và chính nguồn 5.x đọc trần bằng
    `self.size["longest_edge"]`, nên subscript là API thật chứ không phải mẹo.
    Dò theo khả năng subscript để bắt cả hai đời.
    """
    if hasattr(ip, "max_pixels"):
        return ip, "max_pixels"
    size = getattr(ip, "size", None)
    if size is not None and hasattr(size, "__getitem__"):
        try:
            size["longest_edge"]
        except (KeyError, TypeError):
            return None, ""
        return size, 'size["longest_edge"]'
    return None, ""


def _pixel_budget(ip):
    """Đọc trần pixel của image processor. -> (giá trị, tên chỗ chứa)."""
    slot, where = _budget_slot(ip)
    if slot is None:
        return None, ""
    return (slot.max_pixels if where == "max_pixels" else slot["longest_edge"]), where


def _set_pixel_budget(ip, n):
    """Nâng trần pixel, trả tên chỗ đã ghi. Không nhận dạng được thì nổ rõ ràng.

    ponytail: KHÔNG đoán bừa thuộc tính. Trần này không ăn thì `smart_resize`
    thu ảnh về trong IM LẶNG và probe #4 in ra một con số trông như đáp án —
    đúng kiểu hỏng mà cả probe này sinh ra để bắt. Thà nổ ở đây.
    """
    slot, where = _budget_slot(ip)
    if slot is None:
        raise SystemExit(
            f"{type(ip).__name__}: không tìm được chỗ chứa trần pixel. "
            f"Thuộc tính đang có: {sorted(vars(ip))}. "
            f"Cập nhật `_budget_slot` theo API mới rồi chạy lại.")
    if where == "max_pixels":
        slot.max_pixels = n
    else:
        slot["longest_edge"] = n
    # Đọc LẠI chứ không tin là ghi đã ăn. Ghi vào chỗ mà lúc gọi processor không
    # đọc tới thì trần không có tác dụng, và triệu chứng duy nhất là ảnh bị thu
    # nhỏ trong im lặng. Đây là chốt phụ; chốt chính là assert lưới token ở
    # `cmd_sanity4` (so lưới 1x với 4x), vì đó mới là thứ `smart_resize` thật sự dùng.
    got, _ = _pixel_budget(ip)
    if got != n:
        raise SystemExit(
            f"Ghi trần {n:,} vào {where} nhưng đọc lại được {got} -> trần KHÔNG ăn. "
            f"Processor không dùng chỗ này lúc resize.")
    return where


def _load_model(quant4, zoom=1):
    """Nạp model, trả (model, proc, nhãn cấu hình). Tách ra vì sanity chạy 2 lần."""
    import torch
    import transformers
    from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

    model_id = "Qwen/Qwen2.5-VL-3B-Instruct"
    # Trả cache về driver TRƯỚC khi nạp. Model cũ đã chết về mặt Python nhưng bộ
    # nhớ của nó vẫn nằm trong cache allocator; nạp model mới lên trên là tràn T4.
    # Đặt ở đây chứ không ở từng caller: sanity/sanity2/run đều đi qua hàm này.
    torch.cuda.empty_cache()
    # bf16 nếu máy báo có, không thì fp16.
    # ponytail: nhánh fp16 gần như không bao giờ chạy — Colab T4 báo bf16=True
    # (torch 2.11), nên `dtype thật=torch.bfloat16` trên mọi lần chạy. Giữ lại
    # làm đường lui cho GPU đời cũ. Cả hai đều 2 byte/param nên tính VRAM như nhau.
    dt = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    # ponytail: 4.56 đổi tên `torch_dtype` -> `dtype`. Tên cũ ở 5.x rơi vào
    # **kwargs và bị bỏ qua IM LẶNG => nạp fp32 (15 GB) => tràn VRAM T4 16 GB.
    key = ("dtype" if tuple(int(x) for x in transformers.__version__.split(".")[:2]) >= (4, 56)
           else "torch_dtype")
    kw = {key: dt, "device_map": "auto"}
    if quant4:
        from transformers import BitsAndBytesConfig
        kw["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_compute_dtype=dt)
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(model_id, **kw)
    proc = AutoProcessor.from_pretrained(model_id)
    # ponytail: trần pixel phải đủ cho ảnh đã phóng, nếu không `smart_resize` thu
    # ảnh về trong im lặng và probe #4 tự vô hiệu mà vẫn in ra số. Đặt cạnh
    # `from_pretrained` để không ai nạp processor mà quên nó.
    # 1x giữ nguyên mặc định => mọi probe cũ không đổi hành vi.
    #
    # CHỈ NÂNG, KHÔNG HẠ. Config của checkpoint đã đặt 12.845.056; ghi đè xuống
    # một số nhỏ hơn là tự bóp trần của model. In ra cả giá trị TRƯỚC khi ghi để
    # lần sau biết có phải động vào hay không.
    if zoom > 1:
        before, where = _pixel_budget(proc.image_processor)
        if before is None or before < ZOOM_MAX_PX:
            where = _set_pixel_budget(proc.image_processor, ZOOM_MAX_PX)
        after, _ = _pixel_budget(proc.image_processor)
        print(f"[zoom{zoom}x] trần pixel "
              f"{'?' if before is None else f'{before:,}'} -> {after:,} (ở {where})",
              flush=True)
    tag = "4-bit" if quant4 else ("bf16" if dt is torch.bfloat16 else "fp16")
    if zoom > 1:
        tag += f" zoom{zoom}x"
    # Kiểm chứng dtype đã ăn thật, không tin tham số truyền vào.
    print(f"[{tag}] transformers {transformers.__version__} | dtype thật="
          f"{next(model.parameters()).dtype}", flush=True)
    return model, proc, tag


def _load_pic(img, zoom=1):
    """Đường dẫn HOẶC PIL.Image -> PIL.Image RGB, phóng `zoom` lần nếu cần.

    LANCZOS chứ không NEAREST: phép đo là độ dày nét, nội suy tuyến tính giữ
    được gradient mực/giấy (đúng thứ đang đo), NEAREST thì nhân bản pixel thành
    khối vuông cứng.
    """
    from PIL import Image

    pic = img.convert("RGB") if hasattr(img, "convert") else Image.open(img).convert("RGB")
    if zoom > 1:
        pic = pic.resize((pic.width * zoom, pic.height * zoom), Image.LANCZOS)
    return pic


def _prep(proc, pic, prompt):
    """Ảnh + prompt -> batch chưa lên device. Tách khỏi `_ask` để sanity4 in
    được `image_grid_thw` — con số chứng minh `smart_resize` KHÔNG thu nhỏ ảnh."""
    msgs = [{"role": "user", "content": [
        {"type": "image", "image": pic},
        {"type": "text", "text": prompt}]}]
    text = proc.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    return proc(text=[text], images=[pic], return_tensors="pt")


def _ask(model, proc, img, prompt, max_new, zoom=1):
    """`img` là đường dẫn HOẶC PIL.Image sẵn — sanity3 dựng canvas đảo tại chỗ."""
    import torch

    inp = _prep(proc, _load_pic(img, zoom), prompt).to(model.device)
    with torch.no_grad():
        out = model.generate(**inp, max_new_tokens=max_new, do_sample=False)
    return proc.batch_decode(out[:, inp.input_ids.shape[1]:], skip_special_tokens=True)[0].strip()


def cmd_sanity(args):
    """Chẩn đoán: model có NHÌN ảnh không, và có SO SÁNH được không.

    Chạy cả bf16 lẫn 4-bit trên cùng mẫu để tách "quantize bào nét chữ" khỏi
    "model không attend vào ảnh".
    """
    import torch

    items = load_items()[:args.n]
    print(f"sanity: {len(items)} ảnh x {len(SANITY_PROMPTS)} câu hỏi\n", flush=True)

    for quant4 in ([False, True] if args.both else [args.quant4]):
        model, proc, tag = _load_model(quant4)
        hit = 0
        for it in items:
            img = OUT / it["crop"]
            got = {}
            for name, prompt in SANITY_PROMPTS:
                mx = 40 if name.startswith("doc_") else 8
                got[name] = _ask(model, proc, img, prompt, mx)
            pick = parse_ab(got["so_dam"])
            ok = pick == it["gold_bold"]
            hit += ok
            print(f"[{tag}] {it['qid']} gold={it['gold_bold']} pick={pick} {'OK' if ok else 'SAI'}\n"
                  f"    doc_A: {got['doc_A'][:90]!r}\n"
                  f"    doc_B: {got['doc_B'][:90]!r}\n"
                  f"    so_dam: {got['so_dam'][:40]!r}", flush=True)
        print(f"[{tag}] so_dam đúng {hit}/{len(items)}\n", flush=True)
        del model
        torch.cuda.empty_cache()


# ------------------------------------------- pha sanity2 (Colab, chẩn đoán #2)

# Lần 1: model trả 'A' cho CẢ 10 ảnh (đúng 4/10 = đúng mức đoán hằng số) dù
# `doc_tren`/`doc_duoi` chép được chữ thật ở cả hai dải. Nghĩa là tầng NHÌN ổn,
# còn tầng CHỌN thì không. Ba biến thể trên CÙNG 10 ảnh cũ tách hai nghi phạm:
#   V0 = mốc so sánh
#   V1 = buộc chép-rồi-so  -> nếu đổi kết quả: lỗi ở tầng SO SÁNH
#   V2 = bỏ cột tên đơn vị -> nếu đổi kết quả: lỗi ở CỘT NHÃN (dải còn lẫn
#        hàng khác đậm hơn, model trả lời đúng theo thứ nó nhìn thấy)
MARK = "ĐÁP ÁN"

SANITY2_PROMPTS = [
    ("V0_goc", PROMPT),
    ("V1_tung_buoc",
     "Ảnh này ghép hai dải cắt ra từ hai dòng của cùng một bảng: dải TRÊN (A) "
     "và dải DƯỚI (B).\nLàm đúng ba bước:\n"
     "Bước 1: chép nguyên văn chữ ở dải TRÊN.\n"
     "Bước 2: chép nguyên văn chữ ở dải DƯỚI.\n"
     "Bước 3: so sánh độ đậm nét chữ của hai dải vừa chép.\n"
     "Kết thúc bằng đúng một dòng: ĐÁP ÁN: A hoặc ĐÁP ÁN: B"),
    ("V2_bo_cot_dau",
     PROMPT + "\n\nBỏ qua cột đầu tiên (tên đơn vị) ở cả hai dải, chỉ so phần số."),
]


def parse_marked(raw):
    """Đáp án đứng sau dấu `ĐÁP ÁN:`; không có dấu thì lùi về `parse_ab`.

    ponytail: V1 bắt model chép từng bước, nên chữ 'A'/'B' của phần chép lẫn
    vào trước đáp án (ô "Xếp loại" trong bảng toàn giá trị 'A'/'B' đứng riêng).
    Lấy chữ cái ĐẦU là bắt bừa; `rfind` dấu rồi parse phần đuôi mới đúng.
    """
    i = raw.upper().rfind(MARK)
    return parse_ab(raw[i:] if i >= 0 else raw)


def cmd_sanity2(args):
    """Probe #2: lỗi ở tầng SO SÁNH hay ở CỘT NHÃN? Không cắt lại ảnh.

    Chỉ chạy bf16: lần 1 đã đo 4-bit giống bf16 10/10 item, thêm cấu hình chỉ
    tốn VRAM mà không thêm thông tin.
    """
    items = load_items()[:args.n]
    model, proc, tag = _load_model(False)
    print(f"sanity2 [{tag}]: {len(items)} ảnh x {len(SANITY2_PROMPTS)} biến thể\n", flush=True)

    hit = {n: 0 for n, _ in SANITY2_PROMPTS}
    for it in items:
        img = OUT / it["crop"]
        row = []
        for name, prompt in SANITY2_PROMPTS:
            mx = 160 if name.startswith("V1") else 8
            raw = _ask(model, proc, img, prompt, mx)
            pick = parse_marked(raw)
            ok = pick == it["gold_bold"]
            hit[name] += ok
            row.append(f"{name}={pick}{' OK' if ok else ' X'}")
            if name.startswith("V1"):
                print(f"    {it['qid']} V1 chép: {raw[:160]!r}", flush=True)
        print(f"[{tag}] {it['qid']} gold={it['gold_bold']}  " + "  ".join(row), flush=True)

    print(flush=True)
    for name, _ in SANITY2_PROMPTS:
        print(f"[{tag}] {name:14s} đúng {hit[name]}/{len(items)}", flush=True)

    import torch
    del model
    torch.cuda.empty_cache()


def cmd_sanity3(args):
    """Probe #3: model SO SÁNH được, hay chỉ BÁM VỊ TRÍ dải trên?

    Hai phép đảo trên CÙNG ảnh, tách hai giả thuyết:

      V3_dao   : đảo THỨ TỰ dải, nhãn A/B dính theo dải (dải đậm vẫn là "A").
                 -> Đo "model bám vị trí hay bám nhãn". Đây là phép cũ.
      V4_doi_nhan: giữ nguyên thứ tự, ĐỔI chữ cái (dải đậm thành "B").
                 -> Đo "model có nhìn nhãn trong ảnh không". Phép cũ THIẾU nó.

    Chỉ V3 là không đủ: bản đầu tiên vẽ nhãn lên ảnh nên "LẬT" có thể là model
    nhìn thấy chữ cái, mà cũng có thể là model đọc được độ đậm rồi đối chiếu
    với prompt. V4 phân biệt: nếu V4 KHÔNG lật, model chưa bao giờ đọc nhãn.
    """
    import numpy as np
    from PIL import Image

    items = load_items()[:args.n]
    model, proc, tag = _load_model(False)
    print(f"sanity3 [{tag}]: {len(items)} ảnh, đảo dải (nhãn dính theo dải) + đổi nhãn\n",
          flush=True)

    hit = {"V0_goc": 0, "V3_dao": 0, "V4_doi_nhan": 0}
    lat = {"dao": 0, "doi_nhan": 0}
    for it in items:
        # Dải đậm theo nhãn vàng: 0 = dải đầu (nhãn A), 1 = dải sau (nhãn B).
        bold_i = it["gold_bold"]

        # Đảo thứ tự: dải đậm xuống dưới NHƯNG vẫn mang nhãn "A".
        flip = _variant(it, order=[1, 0], labels=["A", "B"])
        # Giữ thứ tự: dải đậm ở trên nhưng mang nhãn "B".
        swap = _variant(it, order=[0, 1], labels=["B", "A"])

        # Ảnh hỏng thì mọi kết luận về nó đều vô nghĩa — kiểm tra trước khi tin.
        assert np.array_equal(np.asarray(Image.open(OUT / it["crop"]).convert("RGB")),
                              np.asarray(_variant(it, [0, 1], ["A", "B"]).convert("RGB"))), \
            f"{it['qid']}: dựng lại canvas không khớp ảnh gốc"
        assert not np.array_equal(np.asarray(flip), np.asarray(swap)), it["qid"]

        picks = {}
        for name, img in (("V0_goc", OUT / it["crop"]), ("V3_dao", flip),
                          ("V4_doi_nhan", swap)):
            raw = _ask(model, proc, img, PROMPT, 8)
            picks[name] = parse_ab(raw)
            hit[name] += picks[name] == bold_i

        # Đảo dải mà nhãn dính theo dải => đáp án ĐÚNG KHÔNG ĐỔI (vẫn "A").
        # Chữ cái lật nghĩa là model chọn theo VỊ TRÍ, không theo nét.
        if picks["V0_goc"] is not None and picks["V3_dao"] is not None:
            lat["dao"] += picks["V0_goc"] != picks["V3_dao"]
        # Đổi nhãn mà giữ thứ tự => đáp án đúng PHẢI ĐỔI (A -> B). Chữ cái đứng
        # nghĩa là model không đọc chữ cái trong ảnh, chỉ đoán theo vị trí.
        if picks["V0_goc"] is not None and picks["V4_doi_nhan"] is not None:
            lat["doi_nhan"] += picks["V0_goc"] == picks["V4_doi_nhan"]

        print(f"[{tag}] {it['qid']} gold={bold_i} "
              f"gốc={picks['V0_goc']} đảo={picks['V3_dao']} "
              f"đổi_nhãn={picks['V4_doi_nhan']}", flush=True)

    n = len(items)
    print(flush=True)
    for name in hit:
        print(f"[{tag}] {name:12s} đúng {hit[name]}/{n}", flush=True)
    print(flush=True)
    print(f"[{tag}] ĐẢO DẢI   (nhãn dính theo dải) -> chữ cái lật: {lat['dao']}/{n}", flush=True)
    print(f"[{tag}] ĐỔI NHÃN  (giữ thứ tự)         -> chữ cái đứng: {lat['doi_nhan']}/{n}",
          flush=True)
    print("\nĐọc (cả hai phép tính trên V0_goc, ảnh đúng nét chữ như nhau):\n"
          "  ĐẢO DẢI lật  + ĐỔI NHÃN đứng -> model đọc nhãn trong ảnh, so được nét,\n"
          "                                  nhưng nghiêng về vị trí. Lỗi ở harness.\n"
          "  ĐẢO DẢI đứng + ĐỔI NHÃN đứng -> model không đọc nhãn, không dùng ảnh.\n"
          "                                  Zero-shot vô dụng; QLoRA là đường duy nhất.\n"
          "  ĐỔI NHÃN lật                 -> model đọc nhãn và so được nét. Tốt nhất.",
          flush=True)

    import torch
    del model
    torch.cuda.empty_cache()


def cmd_sanity4(args):
    """Probe #4: nút thắt là PHÂN GIẢI hay ViT VỨT nét chữ?

    sanity3 kết luận âm: model không đọc nhãn trong ảnh, không so được nét. Hai
    nguyên nhân khác nhau, và chúng dẫn tới hai việc TRÁI NGƯỢC nhau:

      (a) thiếu phân giải — dòng chữ 48 px chỉ trải 3,4 patch 14 px, chênh
          đậm-nhạt 1-2 px chìm trong một patch. Sửa bằng BIỂU DIỄN ĐẦU VÀO
          (cắt sát dòng + phóng to). QLoRA không cần.
      (b) ViT vứt nét thật — QLoRA đóng băng ViT (mặc định) cũng vô ích, và cả
          Cấu hình D đổ. Phải dừng, ghi kết luận âm.

    Phép thử: phóng canvas 4x. (a) đoán model LẬT được; (b) đoán vẫn đứng yên.

    Chạy LẠI đúng ba biến thể của sanity3 trên CÙNG 10 ảnh để so trực tiếp, và
    chạy CẢ 1x lẫn 4x trong cùng lượt trên cùng model — sanity3 đo 1x ở bf16,
    đem so với 4x-4bit là lệch hai biến.
    """
    from PIL import Image
    import torch

    items = load_items()[:args.n]

    # Kiểm tra ngân sách pixel TRƯỚC khi nạp model: sai số học ở đây mà để tới
    # sau `_load_model` là mất hai phút chờ mới biết mình gõ nhầm một chữ số.
    for it in items:
        w, h = Image.open(OUT / it["crop"]).size
        need = w * ZOOM * h * ZOOM
        assert need <= ZOOM_MAX_PX, (
            f"{it['qid']}: {w}x{h} ở {ZOOM}x = {need} px > ZOOM_MAX_PX "
            f"{ZOOM_MAX_PX} -> `smart_resize` sẽ thu nhỏ lại, phép đo vô hiệu. "
            f"Nâng ZOOM_MAX_PX.")

    # 4-bit chứ không bf16. Không phải thoả hiệp cho vừa VRAM: đây ĐÚNG LÀ cấu
    # hình Cấu hình D sẽ chạy (QLoRA 4-bit), nên đo ở đây là đo bản thật.
    #
    # Ở 4x, mỗi ảnh thành ~29k patch; riêng activation của ViT đã ~1,1 GB, cộng
    # trọng số 2 byte/param của 3B (~6 GB) là tràn T4 14,56 GB — đúng cái OOM đã
    # gặp, thiếu có 0,19 MiB. 4-bit hạ trọng số xuống ~1,7 GB, dư sức.
    #
    # Và 4-bit KHÔNG đổi phép đo: Cell 2b của sanity3 đã chạy 4-bit song song bf16
    # trên cùng 10 ảnh, ra y hệt 10/10. Nên ở đây chỉ có bộ nhớ đổi, kết quả thì
    # không — không cần bận tâm chuyện lượng tử hoá ăn vào tín hiệu nét.
    model, proc, tag = _load_model(True, zoom=ZOOM)
    print(f"sanity4 [{tag}]: {len(items)} ảnh, ba biến thể của sanity3, đo ở cả 1x lẫn {ZOOM}x\n",
          flush=True)

    # Chốt chống tự lừa: nếu `smart_resize` vẫn thu ảnh về thì probe đo nhầm
    # thứ khác mà vẫn in ra số đẹp. So kích thước ảnh và lưới token thật.
    small = items[0]
    w1 = Image.open(OUT / small["crop"]).width
    p1 = _prep(proc, _load_pic(OUT / small["crop"], 1), PROMPT)
    p4 = _prep(proc, _load_pic(OUT / small["crop"], ZOOM), PROMPT)
    n1 = int(p1["image_grid_thw"][0].prod())
    n4 = int(p4["image_grid_thw"][0].prod())
    budget, where = _pixel_budget(proc.image_processor)
    print(f"  ảnh gốc {w1} px -> lưới token {tuple(p1['image_grid_thw'][0].tolist())}"
          f"  ({n1} token thị giác)", flush=True)
    print(f"  ảnh {ZOOM}x  {w1 * ZOOM} px -> lưới token {tuple(p4['image_grid_thw'][0].tolist())}"
          f"  ({n4} token thị giác)", flush=True)
    print(f"  trần pixel của processor: {budget:,} (ở {where})", flush=True)
    # So với trần THẬT của processor, không so với hằng số của mình: hằng số chỉ
    # là thứ ta ĐỊNH ghi, còn đây là thứ nó ĐANG giữ.
    assert n4 > 2 * n1, (
        f"phóng {ZOOM}x mà lưới token chỉ nở {n1} -> {n4} -> `smart_resize` đã thu "
        f"ảnh về, probe đang đo ảnh nhỏ hơn tưởng. Trần hiện tại {budget:,} ở {where}.")

    # Đo CẢ HAI mức phóng trong cùng một lượt, cùng một model. sanity3 đã đo 1x
    # rồi nhưng ở bf16; so 4x-4bit với 1x-bf16 là so lệch hai biến, không đọc
    # được. Chạy lại 1x ở đây gần như miễn phí và làm phép so thành CẶP.
    hit = {z: {"V0_goc": 0, "V3_dao": 0, "V4_doi_nhan": 0} for z in (1, ZOOM)}
    lat = {z: {"dao": 0, "doi_nhan": 0} for z in (1, ZOOM)}
    for it in items:
        bold_i = it["gold_bold"]
        flip = _variant(it, order=[1, 0], labels=["A", "B"])
        swap = _variant(it, order=[0, 1], labels=["B", "A"])

        picks = {}
        for z in (1, ZOOM):
            picks[z] = {}
            for name, img in (("V0_goc", OUT / it["crop"]), ("V3_dao", flip),
                              ("V4_doi_nhan", swap)):
                raw = _ask(model, proc, img, PROMPT, 8, zoom=z)
                picks[z][name] = parse_ab(raw)
                hit[z][name] += picks[z][name] == bold_i

            if picks[z]["V0_goc"] is not None and picks[z]["V3_dao"] is not None:
                lat[z]["dao"] += picks[z]["V0_goc"] != picks[z]["V3_dao"]
            if picks[z]["V0_goc"] is not None and picks[z]["V4_doi_nhan"] is not None:
                lat[z]["doi_nhan"] += picks[z]["V0_goc"] == picks[z]["V4_doi_nhan"]

            # Trả cache giữa các mức phóng. Đã tràn một lần ở 4x; rẻ hơn nhiều so
            # với chạy lại cả cell.
            torch.cuda.empty_cache()

        print(f"[{tag}] {it['qid']} gold={bold_i} | "
              f"1x gốc={picks[1]['V0_goc']} đảo={picks[1]['V3_dao']} "
              f"đổi_nhãn={picks[1]['V4_doi_nhan']} | "
              f"{ZOOM}x gốc={picks[ZOOM]['V0_goc']} đảo={picks[ZOOM]['V3_dao']} "
              f"đổi_nhãn={picks[ZOOM]['V4_doi_nhan']}", flush=True)

    n = len(items)
    for z in (1, ZOOM):
        print(flush=True)
        for name in hit[z]:
            print(f"[{tag}] {z}x {name:12s} đúng {hit[z][name]}/{n}", flush=True)
        print(f"[{tag}] {z}x ĐẢO DẢI   (nhãn dính theo dải) -> chữ cái lật: "
              f"{lat[z]['dao']}/{n}", flush=True)
        print(f"[{tag}] {z}x ĐỔI NHÃN  (giữ thứ tự)         -> chữ cái đứng: "
              f"{lat[z]['doi_nhan']}/{n}", flush=True)

    print("\nĐọc (1x và 4x chạy CÙNG model, CÙNG 10 ảnh — so trực tiếp được):\n"
          f"  ĐẢO DẢI ở {ZOOM}x CAO HƠN HẲN 1x -> nút thắt là PHÂN GIẢI. Đường đi\n"
          "                            là biểu diễn đầu vào (cắt sát dòng rồi\n"
          "                            phóng), QLoRA chỉ là tuỳ chọn.\n"
          f"  ĐẢO DẢI ở {ZOOM}x Y NHƯ 1x      -> ViT vứt nét thật. Zero-shot lẫn\n"
          "                            QLoRA-đóng-băng-ViT đều vô ích => dừng, ghi\n"
          "                            kết luận âm.",
          flush=True)

    del model
    torch.cuda.empty_cache()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["extract", "run", "score", "sanity", "sanity2",
                                     "sanity3", "sanity4"])
    ap.add_argument("--quant4", action="store_true", help="lượng tử hoá 4-bit (nếu thiếu VRAM)")
    ap.add_argument("--n", type=int, default=10, help="sanity: số ảnh lấy mẫu")
    ap.add_argument("--both", action="store_true", help="sanity: chạy cả bf16 lẫn 4-bit")
    args = ap.parse_args()
    {"extract": cmd_extract, "run": cmd_run, "score": cmd_score,
     "sanity": cmd_sanity, "sanity2": cmd_sanity2, "sanity3": cmd_sanity3,
     "sanity4": cmd_sanity4}[args.mode](args)


if __name__ == "__main__":
    main()
