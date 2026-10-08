"""Bộ định tuyến ý định KHÔNG NHÃN: câu hỏi -> 1 trong 8 dạng suy luận.

Cấu hình B cần biết câu hỏi thuộc dạng nào để chọn luật. Trên `public_test` /
`private_test` không có `labels.jsonl`, nên không được học tham số từ nhãn —
chỉ được đọc chữ của câu hỏi. File này là bộ định tuyến đó.

    python intent_router.py            # ma trận nhầm lẫn trên train

Luật xếp theo thứ tự LOẠI TRỪ DẦN, không phải theo tần suất: dấu hiệu nào hẹp
và không lẫn với dạng khác thì xét trước.

    cross_page_sum  'cộng với' + 'ở trang' (2 trang) — chỉ 46 câu, hẹp nhất
    count           'bao nhiêu dòng'
    sum             'tổng ... của hai|ba dòng'
    compare         'dòng nào có ... cao|thấp|nhỏ|ít hơn'  (có 'giữa ... với')
    visual_bold     'in đậm' / 'kiểu chữ' / 'hình thức trình bày' / 'quan sát'
    argmin          'nhỏ nhất|thấp nhất|ít nhất'
    argmax          'lớn nhất|cao nhất|nhiều nhất'
    lookup          còn lại (mặc định)

`argmax`/`argmin` xét SAU `compare` vì câu compare cũng chứa 'cao hơn' nhưng
kèm 'dòng nào'; câu argmax hỏi 'X nào có ... lớn nhất' (so trong cả cột).
`visual_bold` xét trước argmax vì câu đó cũng có 'dòng nào có'.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.stdout.reconfigure(encoding="utf-8")
from grid_ocr import DATA, load_jsonl

TYPES = ("cross_page_sum", "count", "sum", "compare", "visual_bold_lookup",
         "argmin", "argmax", "lookup")

RULES = [
    ("cross_page_sum", re.compile(r"cộng\s+với", re.I)),
    ("count",          re.compile(r"bao\s+nhiêu\s+dòng", re.I)),
    ("sum",            re.compile(r"tổng\s+.+?\s+của\s+(?:hai|ba)\s+dòng", re.I)),
    ("compare",        re.compile(r"dòng\s+nào\s+có\s+.+?\s+(?:cao|thấp|nhỏ|lớn|ít|nhiều)\s+hơn", re.I)),
    ("visual_bold_lookup", re.compile(r"in\s+đậm|kiểu\s+chữ|hình\s+thức\s+trình\s+bày|quan\s+sát\s+trực\s+tiếp", re.I)),
    ("argmin",         re.compile(r"(?:nhỏ|thấp|ít)\s+nhất", re.I)),
    ("argmax",         re.compile(r"(?:lớn|cao|nhiều)\s+nhất", re.I)),
]


def route(question):
    """-> một trong 8 dạng. Không đọc nhãn, chỉ đọc câu hỏi."""
    for rt, pat in RULES:
        if pat.search(question):
            return rt
    return "lookup"


def main():
    questions = load_jsonl(DATA / "questions.jsonl")
    gold = {l["question_id"]: l["reasoning_type"] for l in load_jsonl(DATA / "labels.jsonl")}

    m = defaultdict(int)
    per = defaultdict(lambda: [0, 0])
    for q in questions:
        g = gold[q["question_id"]]
        p = route(q["question"])
        m[(g, p)] += 1
        per[g][1] += 1
        per[g][0] += (g == p)

    print("===== MA TRAN NHAM LAN — bo dinh tuyen khong nhan (train, 11.000 cau) =====")
    print(f"{'gold -> doan':22}" + "".join(f"{t[:9]:>11}" for t in TYPES))
    for g in TYPES:
        row = "".join(f"{m[(g, p)] or '':>11}" for p in TYPES)
        print(f"{g:22}{row}")

    n = sum(per[g][1] for g in TYPES)
    ok = sum(per[g][0] for g in TYPES)
    print(f"\n{'dang':22}{'dung':>8}{'n':>8}{'chinh xac':>11}")
    for g in sorted(TYPES, key=lambda k: -per[k][1]):
        c, t = per[g]
        print(f"{g:22}{c:8d}{t:8d}{100*c/t:10.2f}%")
    print(f"{'TOAN BO':22}{ok:8d}{n:8d}{100*ok/n:10.2f}%")

    assert n == 11000, "so cau phai la 11.000"
    assert ok / n > 0.99, f"dinh tuyen yeu: {100*ok/n:.2f}%"


if __name__ == "__main__":
    main()
