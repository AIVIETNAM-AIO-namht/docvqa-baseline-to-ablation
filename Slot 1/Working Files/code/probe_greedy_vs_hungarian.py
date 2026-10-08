"""Greedy vs Hungarian (maximum matching) tren du lieu that -- do, khong suy doan.

Outline §VI.1 cau 1 hoi grader ghep cap evidence bang thuat toan nao. Cau hoi
do chi co y nghia neu ton tai MOT hop du doan P dat IoU >= 0,5 voi HAI hop vang
khac nhau. Khi do Greedy (theo IoU giam dan) va maximum matching moi co the lech.

Do truc tiep: voi tung cau hoi, lay tap hop vang lam gold, lay MOI block OCR
tren cac trang cua cau do lam ung vien du doan (bao ho moi bo du doan co the
lay tu luoi), roi chay ca hai thuat toan va so ket qua.

Neu Greedy == maximum matching tren ca 11.000 cau thi cau hoi §VI.1 vo nghia.

Doc:  data/training_set/labels.jsonl
      data/training_set/manifest.jsonl
      data/training_set/ocr/<document_id>.json
Khong ghi gi (chi in).
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.setrecursionlimit(10000)

BASE = Path(__file__).resolve().parents[3]
TRAIN = BASE / "data" / "training_set"
THR = 0.5


def iou(a, b):
    ix1, iy1 = max(a[0], b[0]), max(a[1], b[1])
    ix2, iy2 = min(a[2], b[2]), min(a[3], b[3])
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua if ua > 0 else 0.0


def greedy(pairs):
    """pairs: list of (pred_idx, gold_idx, iou). Take by descending IoU."""
    used_p, used_g, n = set(), set(), 0
    for pi, gi, _ in sorted(pairs, key=lambda t: -t[2]):
        if pi in used_p or gi in used_g:
            continue
        used_p.add(pi)
        used_g.add(gi)
        n += 1
    return n


def optimal(adj, n_gold):
    """Kuhn's augmenting-path maximum bipartite matching."""
    match_g = [-1] * n_gold

    def try_k(u, seen):
        for v in adj[u]:
            if seen[v]:
                continue
            seen[v] = True
            if match_g[v] == -1 or try_k(match_g[v], seen):
                match_g[v] = u
                return True
        return False

    return sum(1 for u in range(len(adj)) if try_k(u, [False] * n_gold))


def main():
    labels = [json.loads(l) for l in (TRAIN / "labels.jsonl").open(encoding="utf-8") if l.strip()]
    docs = [json.loads(l)["id"] for l in (TRAIN / "manifest.jsonl").open(encoding="utf-8") if l.strip()]

    by_doc = defaultdict(list)
    for lab in labels:
        by_doc[lab["question_id"].rsplit("-q", 1)[0]].append(lab)

    n_q = 0
    n_precondition = 0       # some P reaches >= 2 gold boxes
    n_divergent = 0          # greedy != maximum matching
    n_gold_overlap = 0
    witnesses = []

    for doc in docs:
        data = json.loads((TRAIN / "ocr" / f"{doc}.json").read_text(encoding="utf-8"))
        blocks_by_page = defaultdict(list)
        for pg in data["pages"]:
            for b in pg["blocks"]:
                blocks_by_page[pg["page"]].append(b["bbox"])

        for lab in by_doc.get(doc, []):
            n_q += 1
            golds = [(e["page"], e["bbox"]) for e in (lab.get("evidence") or [])]
            for i in range(len(golds)):
                for j in range(i + 1, len(golds)):
                    if golds[i][0] == golds[j][0] and iou(golds[i][1], golds[j][1]) > 0:
                        n_gold_overlap += 1

            pages = {p for p, _ in golds}
            cand = [(p, bb) for p in pages for bb in blocks_by_page.get(p, [])]

            adj = [[] for _ in cand]
            pairs = []
            for ci, (cp, cbb) in enumerate(cand):
                for gi, (gp, gbb) in enumerate(golds):
                    if cp != gp:
                        continue
                    v = iou(cbb, gbb)
                    if v >= THR:
                        adj[ci].append(gi)
                        pairs.append((ci, gi, v))
                if len(adj[ci]) >= 2:
                    n_precondition += 1
                    if len(witnesses) < 5:
                        witnesses.append((lab["question_id"], adj[ci]))

            g = greedy(pairs)
            o = optimal(adj, len(golds))
            if g != o:
                n_divergent += 1
                if len(witnesses) < 5:
                    witnesses.append((lab["question_id"], f"greedy={g} optimal={o}"))

    print(f"questions                         : {n_q}")
    print(f"gold boxes overlapping (same page): {n_gold_overlap}")
    print()
    print(f"blocks P reaching >= 2 gold boxes : {n_precondition}")
    print(f"questions where greedy != optimal : {n_divergent}")
    if witnesses:
        print()
        print("witnesses:")
        for w in witnesses:
            print(f"  {w}")


if __name__ == "__main__":
    main()
