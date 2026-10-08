"""Follow-up: why does the naive sum solver fail, and can row/col metadata fix it?

Prints full evidence dumps (with table/row/column/is_bold) for failing sum
questions so the cell semantics are visible instead of guessed.
"""
import json
import re
from collections import defaultdict
from pathlib import Path

DATA = Path(__file__).parent / "data" / "training_set"


def load(name):
    with open(DATA / name, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def to_number(s):
    s = s.strip()
    if re.fullmatch(r"-?\d{1,3}(\.\d{3})+", s):
        return float(s.replace(".", ""))
    s2 = s.replace(",", ".")
    return float(s2) if re.fullmatch(r"-?\d+(\.\d+)?", s2) else None


def main():
    labels = load("labels.jsonl")
    cells = load("cell_annotations.jsonl")
    questions = {q["question_id"]: q["question"] for q in load("questions.jsonl")}

    key = {}
    for c in cells:
        key[(c["document_id"], c["page"], tuple(c["bbox"]))] = c

    # ---------- detailed dump of failing sums ----------
    shown = 0
    for lab in labels:
        if lab.get("reasoning_type") != "sum" or shown >= 5:
            continue
        doc = lab["question_id"].rsplit("-q", 1)[0]
        ev = [key[(doc, e["page"], tuple(e["bbox"]))] for e in lab["evidence"]
              if (doc, e["page"], tuple(e["bbox"])) in key]
        nums = [to_number(c["clean_text"]) for c in ev]
        nums = [v for v in nums if v is not None]
        gold = float(lab["answers"][0].replace(".", ""))
        if nums and abs(sum(nums) - gold) < 1e-6:
            continue
        shown += 1
        print(f"\n--- {lab['question_id']}  gold={gold}  naive_sum={sum(nums)}")
        print(f"    Q: {questions[lab['question_id']]}")
        for c in ev:
            print(f"      tbl{c['table']} r{c['row']} c{c['column']} "
                  f"bold={int(c['is_bold'])} hdr={int(c['is_header'])} "
                  f"{c['clean_text']!r}")

    # ---------- hypothesis test: sum operand rows, keyed by row/col ----------
    def solve_sum(ev):
        """Operands = rows whose cells are all numeric (or the numeric cell in a
        row that also carries a text label). Filter cells are text-only rows."""
        rows = defaultdict(list)
        for c in ev:
            rows[(c["table"], c["row"])].append(c)
        total, found = 0.0, False
        for cs in rows.values():
            vals = [to_number(c["clean_text"]) for c in cs]
            vals = [v for v in vals if v is not None]
            if len(vals) == 1 and len(cs) >= 1:
                # a row with exactly one numeric cell = one operand
                if len(cs) == 1 or any(to_number(c["clean_text"]) is None for c in cs):
                    total += vals[0]
                    found = True
        return total if found else None

    ok = tot = 0
    for lab in labels:
        if lab.get("reasoning_type") != "sum":
            continue
        doc = lab["question_id"].rsplit("-q", 1)[0]
        ev = [key[(doc, e["page"], tuple(e["bbox"]))] for e in lab["evidence"]
              if (doc, e["page"], tuple(e["bbox"])) in key]
        try:
            gold = float(lab["answers"][0].replace(".", ""))
        except ValueError:
            continue
        tot += 1
        got = solve_sum(ev)
        if got is not None and abs(got - gold) < 1e-6:
            ok += 1
    print(f"\n===== sum solver v2 (row/col aware): {ok}/{tot} = {100*ok/tot:.1f}%")

    # ---------- the 9 answers nowhere in OCR ----------
    print("\n===== answers not found in OCR at all =====")
    ocr_cache = {}

    def ocr_text(doc):
        if doc not in ocr_cache:
            with open(DATA / "ocr" / f"{doc}.json", encoding="utf-8") as f:
                o = json.load(f)
            ocr_cache[doc] = re.sub(
                r"\s+", " ", " ".join(b["text"] for p in o["pages"] for b in p["blocks"])
            ).lower()
        return ocr_cache[doc]

    for lab in labels:
        doc = lab["question_id"].rsplit("-q", 1)[0]
        hay = ocr_text(doc)
        if not any(a.lower().strip() and a.lower().strip() in hay for a in lab["answers"]):
            print(f"  {lab['question_id']} type={lab.get('reasoning_type')} "
                  f"ans={lab['answers']} | {questions[lab['question_id']][:90]}")

    # ---------- visual_bold_lookup: recoverable by is_bold filter? ----------
    print("\n===== visual_bold_lookup: is the answer in a bold cell? =====")
    n_bold_ev = n_tot = 0
    for lab in labels:
        if lab.get("reasoning_type") != "visual_bold_lookup":
            continue
        doc = lab["question_id"].rsplit("-q", 1)[0]
        ev = [key[(doc, e["page"], tuple(e["bbox"]))] for e in lab["evidence"]
              if (doc, e["page"], tuple(e["bbox"])) in key]
        n_tot += 1
        if any(c["is_bold"] for c in ev):
            n_bold_ev += 1
    print(f"  >=1 bold evidence cell: {n_bold_ev}/{n_tot} = {100*n_bold_ev/n_tot:.1f}%")

    # ---------- how many cells are bold overall (prior for the classifier) ----------
    nb = sum(1 for c in cells if c["is_bold"])
    nh = sum(1 for c in cells if c["is_header"])
    print(f"\n  bold cells overall: {nb}/{len(cells)} = {100*nb/len(cells):.1f}%")
    print(f"  header cells overall: {nh}/{len(cells)} = {100*nh/len(cells):.1f}%")


if __name__ == "__main__":
    main()
