"""Do the gold evidence regions overlap each other?

Outline §VI.1 cau 1 hoi grader ghep cap evidence bang Greedy hay Hungarian.
Cau hoi do CHI co y nghia neu hai vung vang co the cung dat IoU >= 0,5 voi
cung mot vung du doan -- ma dieu do doi hoi chinh cac vung vang phai de len
nhau. Do truc tiep thay vi gia dinh.

Doc:  data/training_set/labels.jsonl
      data/training_set/ocr/<document_id>.json
Khong ghi gi (chi in).
"""
import json
import statistics
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parents[3]
LABELS = BASE / "data" / "training_set" / "labels.jsonl"
OCR = BASE / "data" / "training_set" / "ocr"


def iou(a, b):
    ix1, iy1 = max(a[0], b[0]), max(a[1], b[1])
    ix2, iy2 = min(a[2], b[2]), min(a[3], b[3])
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua if ua > 0 else 0.0


def main():
    labels = [json.loads(l) for l in LABELS.open(encoding="utf-8") if l.strip()]
    print(f"questions                    : {len(labels)}")

    ocr_cache = {}

    def blocks_for(doc_id):
        if doc_id not in ocr_cache:
            data = json.loads((OCR / f"{doc_id}.json").read_text(encoding="utf-8"))
            m = {}
            for pg in data["pages"]:
                for b in pg["blocks"]:
                    m[b["block_id"]] = (b["page"], b["bbox"])
            ocr_cache[doc_id] = m
        return ocr_cache[doc_id]

    sizes = defaultdict(int)
    n_missing_block = 0
    n_mismatch_bbox = 0
    n_self_overlap = 0
    overlaps = []

    for lab in labels:
        ev = lab.get("evidence") or []
        sizes[len(ev)] += 1
        doc_id = lab["question_id"].rsplit("-q", 1)[0]
        blk = blocks_for(doc_id)

        boxes = []
        for e in ev:
            bid = e.get("block_id")
            if bid not in blk:
                n_missing_block += 1
                boxes.append((e["page"], e["bbox"]))
                continue
            page, bbox = blk[bid]
            if page != e["page"] or any(abs(x - y) > 1e-6 for x, y in zip(bbox, e["bbox"])):
                n_mismatch_bbox += 1
            boxes.append((page, bbox))

        worst = 0.0
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                if boxes[i][0] != boxes[j][0]:
                    continue
                worst = max(worst, iou(boxes[i][1], boxes[j][1]))
        if worst > 0:
            n_self_overlap += 1
            overlaps.append(worst)

    print(f"evidence-count distribution  : {dict(sorted(sizes.items()))}")
    print(f"block_id not found in OCR    : {n_missing_block}")
    print(f"labels bbox != OCR bbox      : {n_mismatch_bbox}")
    print(f"questions w/ overlapping gold: {n_self_overlap}")
    if overlaps:
        overlaps.sort()
        print(f"  IoU min / med / max        : {overlaps[0]:.3f} / "
              f"{statistics.median(overlaps):.3f} / {overlaps[-1]:.3f}")
        print(f"  IoU >= 0,5                 : {sum(1 for v in overlaps if v >= 0.5)}")


if __name__ == "__main__":
    main()
