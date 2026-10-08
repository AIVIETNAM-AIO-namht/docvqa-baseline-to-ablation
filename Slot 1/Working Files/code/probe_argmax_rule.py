"""Cau hoi argmax/argmin co giai duoc bang LUAT THUAN PYTHON khong?  (v2)

v1 dat 67,6% nhung phan lon loi la got=None -> loi KHOP TEN COT, khong phai
loi chon hang. Va v1 doan bang thay vi doc: cau hoi noi ro "bang 1 o trang 1".

v2 sua hai cho do, roi TACH loi theo nguyen nhan:
  A. khong tim thay cot      -> loi khop chuoi
  B. khong co so trong cot   -> loi kieu du lieu
  C. chon sai hang, xa       -> loi that
  D. chon sai hang, suyt soat (gap < 10% bien do) -> dung nhu mentor: 120/315

Muc dich: biet khoang cach con lai la loi KY THUAT hay loi SUY LUAN.
"""
import json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from audit_ceiling import load, to_number

PAT = re.compile(r"([^,;:?]{2,60}?)\s+nào\s+có\s+(.+?)\s+(lớn nhất|nhỏ nhất|cao nhất|thấp nhất|nhiều nhất|ít nhất)\s*\?", re.I)
LOC = re.compile(r"bảng\s+(\d+)\s+ở\s+trang\s+(\d+)", re.I)
DIR = {"lớn nhất": "max", "cao nhất": "max", "nhiều nhất": "max",
       "nhỏ nhất": "min", "thấp nhất": "min", "ít nhất": "min"}


def norm(s):
    """Chuan hoa de khop ten cot: bo dau cau, ha chu, gop khoang trang."""
    return re.sub(r"\s+", " ", re.sub(r"[()\[\]:.,]", " ", s)).strip().lower()


def parse(q):
    m, loc = PAT.search(q), LOC.search(q)
    if not m or not loc:
        return None
    return m.group(1).strip(), m.group(2).strip(), DIR[m.group(3).lower()], int(loc.group(1)), int(loc.group(2))


def find_col(table, name):
    """Tra cot theo ten, khop chinh xac truoc roi khop chua nhau."""
    h = {norm(c["clean_text"]): c["column"] for c in table if c["is_header"]}
    n = norm(name)
    if n in h:
        return h[n]
    hit = [col for t, col in h.items() if n and (n in t or t in n)]
    return hit[0] if len(hit) == 1 else None      # nhieu ket qua = mo ho -> tu choi


def rank(table, lab_col, val_col, direction):
    """Tra (nhan hang thang, gap tuong doi so voi hang nhi) tren MOT bang."""
    by_row = defaultdict(dict)
    for c in table:
        if not c["is_header"]:
            by_row[c["row"]][c["column"]] = c["clean_text"]
    scored = []
    for r, cols in by_row.items():
        v = to_number(cols.get(val_col, ""))
        if v is not None:
            scored.append((v, r, cols.get(lab_col)))
    if not scored:
        return None, None
    scored.sort(reverse=(direction == "max"))
    top = scored[0]
    gap = None
    if len(scored) > 1:
        lo, hi = sorted([abs(scored[0][0]), abs(scored[1][0])])
        gap = (hi - lo) / hi if hi else 0.0
    return top[2], gap


def main():
    labels = load("labels.jsonl")
    cells = load("cell_annotations.jsonl")
    questions = {q["question_id"]: q["question"] for q in load("questions.jsonl")}

    tabs = defaultdict(list)
    for c in cells:
        tabs[(c["document_id"], c["page"], c["table"])].append(c)

    cause = Counter()
    ok = n = 0
    near_miss = []
    for lab in labels:
        rt = lab.get("reasoning_type")
        if rt not in ("argmax", "argmin"):
            continue
        q = questions[lab["question_id"]]
        gold = lab["answers"][0].strip().lower()
        n += 1
        p = parse(q)
        if not p:
            cause["E. khong parse duoc cau hoi"] += 1
            continue
        lab_name, val_name, direction, tbl, page = p
        doc = lab["question_id"].rsplit("-q", 1)[0]
        table = tabs.get((doc, page, tbl))
        if not table:
            cause["F. khong thay bang trong du lieu"] += 1
            continue
        vc, lc = find_col(table, val_name), find_col(table, lab_name)
        if vc is None:
            cause[f"A. khong khop ten COT DO ({val_name[:22]})"] += 1
            continue
        if lc is None:
            cause[f"A. khong khop ten COT NHAN ({lab_name[:22]})"] += 1
            continue
        got, gap = rank(table, lc, vc, direction)
        if got is None:
            cause["B. cot do khong co so"] += 1
            continue
        if got.strip().lower() == gold:
            ok += 1
        elif gap is not None and gap < 0.10:
            cause["D. sai hang, SUYT SOAT (gap<10%)"] += 1
            near_miss.append((q, gold, got, gap))
        else:
            cause["C. sai hang, xa"] += 1
            near_miss.append((q, gold, got, gap))

    print("===== ARGMAX/ARGMIN bang LUAT THUAN PYTHON, doc bang+trang tu cau hoi =====")
    print(f"DUNG {ok}/{n} = {100*ok/n:.2f}%   (mentor: ANLS 89-90 / EvF1 77)")
    print("\n--- tach loi theo nguyen nhan ---")
    for k, v in cause.most_common():
        print(f"  {v:5d}  {100*v/n:5.1f}%  {k}")
    print("\n--- 10 ca suyt soat / sai xa (gap = k/cach tuong doi so voi hang nhi) ---")
    for q, g, got, gap in near_miss[:10]:
        gs = f"{gap:.3f}" if gap is not None else "  -  "
        print(f"  gap={gs} gold={g!r:20} got={got!r:20} | {q[:70]}")


if __name__ == "__main__":
    main()
