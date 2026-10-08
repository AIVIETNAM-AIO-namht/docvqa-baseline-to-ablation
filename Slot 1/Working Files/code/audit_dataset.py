"""Audit TACVU2 training_set: extractability ceiling + procedural-solver feasibility.

Answers the questions the WEEK01 knowledge file listed as "chua do duoc":
  Q1. What fraction of answers appear verbatim in the document OCR?
  Q2. Do evidence bboxes correspond 1:1 to cell_annotations blocks?
  Q3. For sum/count/argmax/argmin/compare: can a procedural solver recover the
      answer from the evidence cells alone?
  Q4. Do numeric cell texts use thousands separators (solver hazard)?
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

DATA = Path(__file__).parent / "data" / "training_set"


def load(name):
    with open(DATA / name, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def norm(s):
    """Lowercase, collapse whitespace. Keep diacritics — we are measuring
    Vietnamese, stripping them would hide exactly the errors we care about."""
    return re.sub(r"\s+", " ", s.lower()).strip()


def to_number(s):
    """Parse a cell value to float. Handles Vietnamese separators.

    Hazard: '1.234' is 1234 in vi-VN but 1.234 in en-US. We assume vi-VN
    grouping when the separator is '.' followed by exactly 3 digits.
    """
    s = s.strip().replace(" ", "")
    if not s:
        return None
    # vi-VN: '.' groups thousands, ',' is decimal
    if re.fullmatch(r"-?\d{1,3}(\.\d{3})+", s):
        return float(s.replace(".", ""))
    if re.fullmatch(r"-?\d{1,3}(,\d{3})+", s):
        return float(s.replace(",", ""))
    s2 = s.replace(".", "").replace(",", ".")
    m = re.fullmatch(r"-?\d+(\.\d+)?", s2)
    return float(s2) if m else None


def main():
    labels = load("labels.jsonl")
    cells = load("cell_annotations.jsonl")
    manifest = {m["id"]: m for m in load("manifest.jsonl")}

    print(f"labels={len(labels)}  cells={len(cells)}  docs={len(manifest)}")

    # ---- index cells by document ----
    cells_by_doc = defaultdict(list)
    for c in cells:
        cells_by_doc[c["document_id"]].append(c)

    # ---- index OCR text by document ----
    ocr_by_doc = {}
    for doc_id in manifest:
        with open(DATA / "ocr" / f"{doc_id}.json", encoding="utf-8") as f:
            ocr_by_doc[doc_id] = json.load(f)

    # ================= Q1: extractability ceiling =================
    n_sub = n_subseq = n_none = 0
    per_type_ceiling = defaultdict(lambda: [0, 0])  # type -> [substr_hit, total]
    for lab in labels:
        doc = lab["question_id"].rsplit("-q", 1)[0]
        blocks = [b["text"] for p in ocr_by_doc[doc]["pages"] for b in p["blocks"]]
        hay = norm(" \n ".join(blocks))
        hay_nows = re.sub(r"\s+", "", hay)
        rt = lab.get("reasoning_type", "?")
        per_type_ceiling[rt][1] += 1
        hit = False
        for a in lab["answers"]:
            a_n = norm(a)
            if a_n and a_n in hay:
                n_sub += 1
                hit = True
                break
            a_c = re.sub(r"\s+", "", a_n)
            # subsequence test
            it = iter(hay_nows)
            if a_c and all(ch in it for ch in a_c):
                n_subseq += 1
                hit = True
                break
        if hit:
            per_type_ceiling[rt][0] += 1
        else:
            n_none += 1

    total = len(labels)
    print("\n===== Q1: extractability ceiling (training_set) =====")
    print(f"substring   : {n_sub:5d} / {total} = {100*n_sub/total:5.1f}%")
    print(f"subsequence : {n_subseq:5d} / {total} = {100*n_subseq/total:5.1f}%")
    print(f"neither     : {n_none:5d} / {total} = {100*n_none/total:5.1f}%")
    print(f"-> substring UB = {100*(n_sub+n_subseq)/total:.1f}% (sum of both)")
    print("\nper reasoning_type substring-UB:")
    for rt, (h, t) in sorted(per_type_ceiling.items(), key=lambda kv: -kv[1][1]):
        print(f"  {rt:22s} {h:5d}/{t:5d} = {100*h/t:5.1f}%")

    # ================= Q2: evidence <-> cell_annotations =================
    cell_bbox_by_doc = defaultdict(set)
    for c in cells:
        cell_bbox_by_doc[c["document_id"]].add((c["page"], tuple(c["bbox"])))
    all_block_ids = defaultdict(set)
    for doc_id, o in ocr_by_doc.items():
        for p in o["pages"]:
            for b in p["blocks"]:
                all_block_ids[doc_id].add(b["block_id"])

    ev_in_cells = ev_in_blocks = ev_total = 0
    for lab in labels:
        doc = lab["question_id"].rsplit("-q", 1)[0]
        for e in lab["evidence"]:
            ev_total += 1
            if (e["page"], tuple(e["bbox"])) in cell_bbox_by_doc[doc]:
                ev_in_cells += 1
            if e.get("block_id") in all_block_ids[doc]:
                ev_in_blocks += 1
    print("\n===== Q2: do evidence boxes correspond to real blocks? =====")
    print(f"evidence regions total      : {ev_total}")
    print(f"bbox matches a cell exactly : {ev_in_cells} = {100*ev_in_cells/ev_total:.1f}%")
    print(f"block_id exists in OCR      : {ev_in_blocks} = {100*ev_in_blocks/ev_total:.1f}%")

    # ================= Q3: procedural solver on evidence cells =================
    # Build a lookup: (doc, page, bbox) -> cell record
    cell_by_key = {}
    for c in cells:
        cell_by_key[(c["document_id"], c["page"], tuple(c["bbox"]))] = c

    stats = defaultdict(Counter)
    sum_examples = []
    for lab in labels:
        rt = lab.get("reasoning_type", "?")
        doc = lab["question_id"].rsplit("-q", 1)[0]
        ev_cells = [
            cell_by_key[(doc, e["page"], tuple(e["bbox"]))]
            for e in lab["evidence"]
            if (doc, e["page"], tuple(e["bbox"])) in cell_by_key
        ]
        nums = [to_number(c["clean_text"]) for c in ev_cells]
        nums = [v for v in nums if v is not None]

        gold = None
        try:
            gold = float(lab["answers"][0].replace(".", "").replace(",", ""))
        except (ValueError, IndexError):
            pass

        if rt == "sum":
            got = sum(nums) if nums else None
            ok = got is not None and gold is not None and abs(got - gold) < 1e-6
            stats[rt]["ok" if ok else "fail"] += 1
            if not ok and len(sum_examples) < 6:
                sum_examples.append(
                    (lab["question_id"], gold, got, [c["clean_text"] for c in ev_cells])
                )
        elif rt == "count":
            stats[rt]["total"] += 1
            if gold is not None and abs(len(ev_cells) - gold) < 1e-6:
                stats[rt]["ok_ncells"] += 1
            if gold is not None and abs(len(nums) - gold) < 1e-6:
                stats[rt]["ok_nnumeric"] += 1

    print("\n===== Q3a: sum solvable by summing evidence cells? =====")
    s = stats["sum"]
    tot = s["ok"] + s["fail"]
    print(f"  exact match: {s['ok']}/{tot} = {100*s['ok']/tot:.1f}%")
    print("  failure samples (id, gold, got, cell_texts):")
    for qid, g, got, txt in sum_examples:
        print(f"    {qid} gold={g} got={got} cells={txt}")

    print("\n===== Q3b: count solvable by counting evidence cells? =====")
    c = stats["count"]
    print(f"  count == n_evidence_cells : {c['ok_ncells']}/{c['total']}"
          f" = {100*c['ok_ncells']/max(c['total'],1):.1f}%")
    print(f"  count == n_numeric_cells   : {c['ok_nnumeric']}/{c['total']}"
          f" = {100*c['ok_nnumeric']/max(c['total'],1):.1f}%")

    # ================= Q4: separator hazard =================
    sep_hits = Counter()
    for c in cells:
        t = c["clean_text"]
        if re.fullmatch(r"-?\d{1,3}(\.\d{3})+", t.strip()):
            sep_hits["dot_group"] += 1
        elif re.fullmatch(r"-?\d{1,3}(,\d{3})+", t.strip()):
            sep_hits["comma_group"] += 1
    print("\n===== Q4: numeric cell formatting =====")
    print(f"  cells with '.' thousands grouping: {sep_hits['dot_group']}")
    print(f"  cells with ',' thousands grouping: {sep_hits['comma_group']}")
    print(f"  total cells                      : {len(cells)}")

    # ================= Q5: evidence count distribution =================
    dist = Counter(len(l["evidence"]) for l in labels)
    print("\n===== Q5: evidence regions per question =====")
    for k in sorted(dist):
        print(f"  {k} regions: {dist[k]:5d}  ({100*dist[k]/total:.1f}%)")


if __name__ == "__main__":
    main()
