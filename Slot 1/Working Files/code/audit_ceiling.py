"""Oracle-evidence ceiling for TACVU2, v5.

v5 reaches 11.000/11.000 = 100,00%. The whole thing rests on ONE rule:

    In a row, the cell being asked about is the RIGHTMOST cell.
    Condition (filter) cells sit to its left.

Rules, all inferred from the question text + cell metadata:
  operand = rightmost cell of each row in the evidence
  label   = leftmost non-numeric cell of a row (the row's name)

Per reasoning_type:
  sum, cross_page_sum  -> sum the operands over all rows
  lookup               -> the operand of the single row
  visual_bold_lookup   -> the operand of the one row containing a bold cell
  count                -> number of distinct rows
  argmax, argmin       -> the LABEL of the winning row (evidence holds only
                          that row, so there is nothing to rank)
  compare              -> label of the row whose operand wins the comparison

Two bugs v5 fixes, both worth remembering:
  * v2-v4 split evidence by "cells whose text is a quoted string in the
    question" to separate filters from operands. That breaks when the ANSWER
    cell happens to equal a filter value (row has Thí sinh=47 AND Đạt=47),
    because both get treated as filters. The rightmost-cell rule does not
    care about the question text at all.
  * rows must be keyed by (page, table, row), not (table, row). Without
    page, cross_page_sum merges two rows at the same coordinates on
    different pages and undercounts.
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
    """'1.850' -> 1850.0 (vi-VN groups thousands with '.'), '3,5' -> 3.5.

    Trailing '%' is stripped: 27,2% of argmax/argmin questions ask about a
    percentage column ('Tỷ trọng (%)', 'Tiến độ'), and 1.026 questions were
    failing on that alone. Sorting by the bare number is equivalent because
    every value in such a column carries the same unit.
    """
    s = s.strip().replace(" ", "").rstrip("%")
    if re.fullmatch(r"[+-]?\d{1,3}(\.\d{3})+", s):
        return float(s.replace(".", "").replace("+", ""))
    s2 = s.replace(",", ".")
    return float(s2) if re.fullmatch(r"[+-]?\d+(\.\d+)?", s2) else None


def fmt(v):
    """Render a float the way the labels do (vi-VN: '.' groups thousands)."""
    if v is None:
        return None
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return f"{v:.2f}".rstrip("0").rstrip(".").replace(".", ",")


def rows(ev):
    """Group evidence cells into rows, left-to-right. Key includes page."""
    g = defaultdict(list)
    for c in ev:
        g[(c["page"], c["table"], c["row"])].append(c)
    return {k: sorted(v, key=lambda c: c["column"]) for k, v in g.items()}


def label_of(cells):
    """Row label = leftmost cell that is not a number."""
    for c in cells:
        if to_number(c["clean_text"]) is None:
            return c["clean_text"]
    return cells[0]["clean_text"] if cells else None


def solve(rt, question, ev):
    R = rows(ev)

    if rt in ("sum", "cross_page_sum"):
        vals = [to_number(cs[-1]["clean_text"]) for cs in R.values()]
        vals = [v for v in vals if v is not None]
        return fmt(sum(vals)) if vals else None

    if rt == "lookup":
        return R[list(R)[0]][-1]["clean_text"] if len(R) == 1 else None

    if rt == "visual_bold_lookup":
        bold = [cs for cs in R.values() if any(c["is_bold"] for c in cs)]
        return bold[0][-1]["clean_text"] if len(bold) == 1 else None

    if rt == "count":
        return fmt(len(R))

    if rt in ("argmax", "argmin"):
        # evidence holds only the winning row -> answer is its label
        return label_of(sorted(ev, key=lambda c: c["column"]))

    if rt == "compare":
        if len(R) != 2:
            return None
        (_, c1), (_, c2) = list(R.items())
        v1, v2 = to_number(c1[-1]["clean_text"]), to_number(c2[-1]["clean_text"])
        if v1 is None or v2 is None:
            return None
        smaller = bool(re.search(r"nhỏ hơn|thấp hơn|ít hơn", question, re.I))
        return label_of(c1 if ((v1 < v2) == smaller) else c2)

    return None


def main():
    labels = load("labels.jsonl")
    cells = load("cell_annotations.jsonl")
    questions = {q["question_id"]: q["question"] for q in load("questions.jsonl")}
    key = {(c["document_id"], c["page"], tuple(c["bbox"])): c for c in cells}

    stats = defaultdict(lambda: [0, 0])
    misses = []

    for lab in labels:
        rt = lab.get("reasoning_type")
        qid = lab["question_id"]
        doc = qid.rsplit("-q", 1)[0]
        ev = [key[(doc, e["page"], tuple(e["bbox"]))] for e in lab["evidence"]
              if (doc, e["page"], tuple(e["bbox"])) in key]
        got = solve(rt, questions[qid], ev)
        gold = lab["answers"][0]
        stats[rt][1] += 1
        if got is not None and got.strip().lower() == gold.strip().lower():
            stats[rt][0] += 1
        else:
            misses.append((rt, qid, gold, got))

    print("===== ORACLE-EVIDENCE CEILING v5 (gold evidence -> deterministic solver) =====")
    print(f"{'type':20s} {'exact':>11s}  rate   n")
    ok_t = n_t = 0
    for rt, (ok, n) in sorted(stats.items(), key=lambda kv: -kv[1][1]):
        ok_t += ok
        n_t += n
        print(f"{rt:20s} {ok:5d}/{n:5d}  {100*ok/n:5.1f}%  {n}")
    print(f"{'ALL':20s} {ok_t:5d}/{n_t:5d}  {100*ok_t/n_t:.2f}%")

    print(f"\n===== misses ({len(misses)}) =====")
    for rt, qid, gold, got in misses[:20]:
        print(f"  [{rt}] {qid} gold={gold!r} got={got!r}")


if __name__ == "__main__":
    main()
