"""Test the quoted-filter rule for sum/cross_page_sum.

Hypothesis from inspecting failures: the evidence list of a sum question
contains BOTH
  (a) filter cells  - cells whose text appears as a quoted string in the
      question ("Kế toán", "30", "15.838"), used to locate the row, and
  (b) operand cells - the single remaining cell per selected row, i.e. the
      value in the column the question asks to total.

If true, sum is fully deterministic: drop cells matching a quoted filter
value, add up what is left. No model needed for the arithmetic.

Also tests the same rule for argmax/argmin/compare, where the operand is the
cell to be ranked, not summed.
"""
import json
import re
from collections import defaultdict
from pathlib import Path

DATA = Path(__file__).parent / "data" / "training_set"
QUOTED = re.compile(r"[“”\"]([^“”\"]+)[“”\"]")


def load(name):
    with open(DATA / name, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def to_number(s):
    s = s.strip()
    if re.fullmatch(r"-?\d{1,3}(\.\d{3})+", s):
        return float(s.replace(".", ""))
    s2 = s.replace(",", ".")
    return float(s2) if re.fullmatch(r"-?\d+(\.\d+)?", s2) else None


def operands(question, ev):
    """Split evidence into (filters, operands) using quoted strings in the question."""
    quoted = {q.strip().lower() for q in QUOTED.findall(question)}
    filt, ops = [], []
    for c in ev:
        t = c["clean_text"].strip().lower()
        (filt if t in quoted else ops).append(c)
    return filt, ops


def fmt(v):
    """Render a float the way the labels do (vi-VN: '.' groups thousands)."""
    if v is None:
        return None
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return f"{v:.2f}".rstrip("0").rstrip(".").replace(".", ",")


def main():
    labels = load("labels.jsonl")
    cells = load("cell_annotations.jsonl")
    questions = {q["question_id"]: q["question"] for q in load("questions.jsonl")}
    key = {(c["document_id"], c["page"], tuple(c["bbox"])): c for c in cells}

    results = defaultdict(lambda: [0, 0])

    for lab in labels:
        rt = lab.get("reasoning_type")
        if rt not in ("sum", "cross_page_sum", "argmax", "argmin", "compare"):
            continue
        qid = lab["question_id"]
        doc = qid.rsplit("-q", 1)[0]
        ev = [key[(doc, e["page"], tuple(e["bbox"]))] for e in lab["evidence"]
              if (doc, e["page"], tuple(e["bbox"])) in key]
        filt, ops = operands(questions[qid], ev)
        nums = [to_number(c["clean_text"]) for c in ops]
        nums = [v for v in nums if v is not None]
        gold_raw = lab["answers"][0]

        got = None
        if rt in ("sum", "cross_page_sum") and nums:
            got = fmt(sum(nums))
        elif rt == "argmax" and nums:
            got = fmt(max(nums))
        elif rt == "argmin" and nums:
            got = fmt(min(nums))

        results[rt][1] += 1
        # ANLS-style: exact after normalisation is what we score here
        if got is not None and got.strip().lower() == gold_raw.strip().lower():
            results[rt][0] += 1

    print("===== quoted-filter rule: deterministic solver on evidence cells =====")
    print(f"{'type':18s} {'exact':>10s}  rate")
    tot_ok = tot_n = 0
    for rt, (ok, n) in sorted(results.items(), key=lambda kv: -kv[1][1]):
        tot_ok += ok
        tot_n += n
        print(f"{rt:18s} {ok:5d}/{n:5d}  {100*ok/n:5.1f}%")
    print(f"{'TOTAL':18s} {tot_ok:5d}/{tot_n:5d}  {100*tot_ok/tot_n:5.1f}%")

    # --- how often is the split clean (exactly one operand per selected row)? ---
    print("\n===== operand-count sanity (sum only) =====")
    bad = 0
    for lab in labels:
        if lab.get("reasoning_type") != "sum":
            continue
        qid = lab["question_id"]
        doc = qid.rsplit("-q", 1)[0]
        ev = [key[(doc, e["page"], tuple(e["bbox"]))] for e in lab["evidence"]
              if (doc, e["page"], tuple(e["bbox"])) in key]
        _, ops = operands(questions[qid], ev)
        if len(ops) != 2:
            bad += 1
    print(f"  sum questions with != 2 operands: {bad}")


if __name__ == "__main__":
    main()
