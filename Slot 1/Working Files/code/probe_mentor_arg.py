"""Do solver cua minh tren dung 403 cau ma mentor lam sai (argmax/argmin).

Mentor: 403/3772 sai, 403/403 DUNG BANG nhung SAI HANG.
Cau hoi: do la loi chon hang, hay la de bai mo ho?
"""
import csv, sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from audit_ceiling import load, solve

P = HERE / "olp-ai-ptit-2026-preliminary-round/DocViVQA/artifacts/analysis/diagnostics/"
bad = {r["question_id"] for r in csv.DictReader(open(P / "argextreme_oracle.csv", encoding="utf-8"))
       if r["is_correct"] != "True"}
oracle = {r["question_id"]: r for r in csv.DictReader(open(P / "argextreme_oracle.csv", encoding="utf-8"))}

labels = {l["question_id"]: l for l in load("labels.jsonl")}
questions = {q["question_id"]: q["question"] for q in load("questions.jsonl")}
cells = load("cell_annotations.jsonl")
key = {(c["document_id"], c["page"], tuple(c["bbox"])): c for c in cells}

ok = n = 0
still_wrong = []
for qid in bad:
    lab, q = labels.get(qid), questions.get(qid)
    if not lab or q is None:
        continue
    doc = qid.rsplit("-q", 1)[0]
    ev = [key[(doc, e["page"], tuple(e["bbox"]))] for e in lab["evidence"]
          if (doc, e["page"], tuple(e["bbox"])) in key]
    got = solve(lab["reasoning_type"], q, ev)
    gold = lab["answers"][0]
    n += 1
    if got is not None and got.strip().lower() == gold.strip().lower():
        ok += 1
    else:
        still_wrong.append((qid, gold, got, oracle[qid]["solver_answer"]))

print(f"MY solver on mentor's {n} failures, gold evidence: {ok}/{n} = {100*ok/n:.2f}%")
print()
print("--- cau van sai (neu co) ---")
for qid, gold, got, mentor_got in still_wrong[:15]:
    print(f"  {qid}  gold={gold!r}  mine={got!r}  mentor={mentor_got!r}")

# Doi chieu: mentor sai bao nhieu tren TOAN BO, va bao nhieu trong so do la
# cung-bang-khac-hang
allrows = list(csv.DictReader(open(P / "argextreme_oracle.csv", encoding="utf-8")))
allbad = [r for r in allrows if r["is_correct"] != "True"]
same_tab = sum(r["solver_table"] == r["expected_table"] for r in allbad)
print()
print(f"mentor: {len(allbad)}/{len(allrows)} sai | cung bang: {same_tab} | khac bang: {len(allbad)-same_tab}")
print(f"mentor: sai hang: {sum(r['solver_row']!=r['expected_row'] for r in allbad)}")
