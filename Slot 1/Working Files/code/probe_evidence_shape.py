"""Evidence vang duoc cau tao the nao? — do de biet cho nao con thieu.

Bo dem o tren cho thay: count F1=1.000 (toi khop CHINH XAC), con
argmax/argmin recall chi 0,71 (toi THIEU o), lookup/sum precision chi 0,68
(toi THUA o). Vay luat cua nhan la gi?

Cau hoi: trong mot hang, tap o vang = nhung o nao?
  (a) chi o tra loi
  (b) o tra loi + o bo loc neu trong cau
  (c) MOI o cua hang do (ca cot khong lien quan)
  (d) o tra loi + o nhan hang
"""
import sys, re
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from audit_ceiling import load, to_number

QUOTED = re.compile(r"([^,;:?]{2,40}?)\s*[“\"]([^”\"]+)[”\"]")


def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[()\[\]:.,“”\"]", " ", s)).strip().lower()


def main():
    labels = load("labels.jsonl")
    cells = load("cell_annotations.jsonl")
    questions = {q["question_id"]: q["question"] for q in load("questions.jsonl")}
    key = {(c["document_id"], c["page"], tuple(c["bbox"])): c for c in cells}

    # index (doc, page, table) -> cells, va so o khong-header moi hang
    tabs = defaultdict(list)
    for c in cells:
        tabs[(c["document_id"], c["page"], c["table"])].append(c)

    shape = defaultdict(Counter)
    for rt in {l["reasoning_type"] for l in labels}:
        shape[rt] = Counter()

    for lab in labels:
        rt = lab["reasoning_type"]
        qid = lab["question_id"]
        q = questions[qid]
        doc = qid.rsplit("-q", 1)[0]
        g = [key[(doc, e["page"], tuple(e["bbox"]))] for e in lab["evidence"]
             if (doc, e["page"], tuple(e["bbox"])) in key]
        if not g:
            shape[rt]["khong_join_duoc"] += 1
            continue

        tbl = tabs[(doc, g[0]["page"], g[0]["table"])]
        gset = {(c["row"], c["column"]) for c in g}
        rows = {c["row"] for c in g}
        body = [c for c in tbl if not c["is_header"]]
        ncol = len({c["column"] for c in body})
        rowcells = defaultdict(set)
        for c in body:
            rowcells[c["row"]].add(c["column"])

        # trong moi hang vang: o vang chiem bao nhieu phan
        # ponytail: hang khong co o body nao (chi toan header) -> bo qua, khong tinh
        live = [r for r in rows if rowcells[r]]
        full = sum(1 for r in live if gset >= {(r, c) for c in rowcells[r]})
        only_right = sum(1 for r in live
                         if {c for (rr, c) in gset if rr == r} == {max(rowcells[r])})
        rightmost = all(all(c == max(rowcells[r]) for (rr, c) in gset if rr == r)
                        for r in live)
        rows = set(live)

        # o vang co phai o cuoi hang khong? (luat v5 cua audit_ceiling)
        # va o vang co phai la MOI o cua hang khong?
        shape[rt]["n"] += 1
        shape[rt]["hang_full" if full == len(rows) else "hang_mot_phan"] += 1
        shape[rt]["chi_o_phai" if only_right == len(rows) else "co_o_khac"] += 1
        shape[rt]["moi_o_vang_deu_la_o_phai_nhat" if rightmost else "co_o_khong_phai_phai_nhat"] += 1
        shape[rt]["so_o_vang"] += len(g)
        shape[rt]["so_hang"] += len(rows)
        shape[rt]["so_cot_bang"] += ncol
        shape[rt]["so_o_moi_hang"] += sum(len(rowcells[r]) for r in rows) / len(rows)

    print("===== CAU TAO EVIDENCE VANG =====")
    for rt in sorted(shape, key=lambda k: -shape[k]["n"]):
        s = shape[rt]
        n = s["n"]
        print(f"\n{rt}  (n={n})")
        print(f"  o vang/cau   = {s['so_o_vang']/n:.2f}   hang/cau = {s['so_hang']/n:.2f}"
              f"   o cua hang = {s['so_o_moi_hang']/n:.1f}   cot bang = {s['so_cot_bang']/n:.1f}")
        print(f"  moi o vang la o PHAI NHAT cua hang: {100*s['moi_o_vang_deu_la_o_phai_nhat']/n:5.1f}%")
        print(f"  o vang trum TOAN BO hang          : {100*s['hang_full']/n:5.1f}%")
        print(f"  trong hang chi lay o phai nhat    : {100*s['chi_o_phai']/n:5.1f}%")


if __name__ == "__main__":
    main()
