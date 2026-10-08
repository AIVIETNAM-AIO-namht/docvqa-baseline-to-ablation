"""Evidence-F1 for TACVU2 — 15% of the score.

The đề says only: "một cặp vùng trên cùng trang được coi là khớp khi IoU >= 0,5".
It does NOT say how to pair them, or whether surplus boxes are penalised.
That gap is worth 15% of the score — ask the TA (WEEK01 §3.3, §5.3 câu 1).

This file implements the standard reading (DocVQA/ST-VQA lineage):

    match  = one-to-one, same page, IoU >= 0.5
    P      = matched / len(pred)          <- surplus boxes ARE penalised
    R      = matched / len(gold)
    F1     = 2PR / (P + R)

Pairing is GREEDY by descending IoU. With IoU >= 0.5 a box can overlap at most
one gold box heavily, so greedy and optimal agree on essentially every real
case — but `evidence_f1_optimal` is here if you need to prove that claim
rather than assume it (Hungarian would need scipy; brute force is fine because
gold is capped at 6 regions by construction).

bboxes are normalised [x1, y1, x2, y2] with page 1-based.
"""
from itertools import permutations


def iou(a, b):
    ix1, iy1 = max(a[0], b[0]), max(a[1], b[1])
    ix2, iy2 = min(a[2], b[2]), min(a[3], b[3])
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua if ua > 0 else 0.0


def _pairs(pred, gold, thr):
    """All (iou, i, j) with same page and IoU >= thr."""
    out = []
    for i, p in enumerate(pred):
        for j, g in enumerate(gold):
            if p["page"] != g["page"]:
                continue
            v = iou(p["bbox"], g["bbox"])
            if v >= thr:
                out.append((v, i, j))
    return sorted(out, reverse=True)


def evidence_f1(pred, gold, thr=0.5):
    if not pred or not gold:
        return 0.0
    used_p, used_g, matched = set(), set(), 0
    for _, i, j in _pairs(pred, gold, thr):
        if i in used_p or j in used_g:
            continue
        used_p.add(i)
        used_g.add(j)
        matched += 1
    if matched == 0:
        return 0.0
    prec = matched / len(pred)
    rec = matched / len(gold)
    return 2 * prec * rec / (prec + rec)


def evidence_f1_optimal(pred, gold, thr=0.5):
    """Same metric, maximum matching instead of greedy. Slow but exact."""
    cand = _pairs(pred, gold, thr)
    if not cand:
        return 0.0
    best = 0
    n = min(len(pred), len(gold))
    for size in range(n, 0, -1):
        for combo in permutations(cand, size):
            if len({c[1] for c in combo}) == size and len({c[2] for c in combo}) == size:
                best = size
                break
        if best:
            break
    if best == 0:
        return 0.0
    prec = best / len(pred)
    rec = best / len(gold)
    return 2 * prec * rec / (prec + rec)


def question_score(anls_value, ev_f1, w_anls=0.85, w_ev=0.15):
    return w_anls * anls_value + w_ev * ev_f1


if __name__ == "__main__":
    A = {"page": 1, "bbox": [0.0, 0.0, 0.1, 0.1]}
    B = {"page": 1, "bbox": [0.05, 0.0, 0.15, 0.1]}   # IoU 1/3 -> below thr
    C = {"page": 2, "bbox": [0.0, 0.0, 0.1, 0.1]}     # identical box, other page

    assert evidence_f1([A], [A]) == 1.0
    assert evidence_f1([A], [B]) == 0.0, "IoU 1/3 is below 0.5"
    assert evidence_f1([A], [C]) == 0.0, "same box on another page is NOT a match"
    assert evidence_f1([A, B], [A]) < 1.0, "surplus pred box costs precision"
    assert abs(evidence_f1([A, B], [A]) - 2 * (1 / 2) * 1 / (1 / 2 + 1)) < 1e-9
    assert evidence_f1([], [A]) == 0.0
    assert abs(evidence_f1([A], [A, A]) - 2 * 1 * 0.5 / 1.5) < 1e-9, "surplus gold box costs recall"
    # greedy vs optimal agree on a case where greedy could go wrong
    D = {"page": 1, "bbox": [0.02, 0.0, 0.12, 0.1]}
    assert evidence_f1([A, D], [A, D]) == 1.0
    assert abs(evidence_f1([A, D], [A, D]) - evidence_f1_optimal([A, D], [A, D])) < 1e-9
    print("evidence_f1.py self-check OK")
