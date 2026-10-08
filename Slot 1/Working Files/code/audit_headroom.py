"""Phan ra diem cua mentor theo kieu suy luan -> 4,55 diem con thieu nam o dau?

First-principles: Score = 100 * 1/N * SUM(0,85*ANLS + 0,15*EvF1).
Voi evidence vang, solver thuan Python da dat 100% (audit_ceiling.py).
=> diem la ham cua MOT bien: chon dung o hay khong.
Vay phan ra 4,55 diem con thieu de biet nen dat cong suc vao dau.

Nguon so: PDF mentor §10 tr.28. So cau: labels.jsonl training_set.
"""
W = 0.85  # trong so ANLS (exam_question_docvqa.md §3)
T = [  # (kieu, so cau, ANLS, Evidence-F1)
    ("lookup",             2200, 100.00, 100.00),
    ("count",               915, 100.00, 100.00),
    ("sum",                1810, 100.00, 100.00),
    ("compare",            1722, 100.00, 100.00),
    ("cross_page_sum",       46, 100.00, 100.00),
    ("argmax",             1898,  90.02,  77.52),
    ("argmin",             1874,  89.00,  76.49),
    ("visual_bold_lookup",  535,  96.90,  74.82),
]
N = sum(n for _, n, _, _ in T)
assert N == 11000, f"tong so cau phai la 11.000, dang la {N}"

rows = [(k, n, W * a + (1 - W) * e, 100 - (W * a + (1 - W) * e)) for k, n, a, e in T]
overall = sum(n * s for _, n, s, _ in rows) / N
print(f"overall = {overall:.2f}  (PDF mentor §10 ghi 95,45)")
assert abs(overall - 95.45) < 0.01, "phan ra khong khop so da cong bo -> cong thuc sai"

total_loss = sum(n * h / 100 for _, n, _, h in rows)
print(f"\n{'kieu':22}{'so cau':>8}{'diem/cau':>10}{'ho':>8}{'diem thieu':>12}{'% tong thieu':>14}")
for k, n, s, h in sorted(rows, key=lambda r: -r[1] * r[3]):
    loss = n * h / 100
    print(f"{k:22}{n:8d}{s:10.2f}{h:8.2f}{loss:12.2f}{100 * loss / total_loss:13.1f}%")
print(f"{'TONG':22}{N:8d}{'':10}{'':8}{total_loss:12.2f}{100:13.1f}%")

ae = sum(n * h / 100 for k, n, _, h in rows if k in ("argmax", "argmin"))
print(f"\nargmax+argmin chiem {ae:.2f}/{total_loss:.2f} = {100 * ae / total_loss:.1f}% toan bo diem con thieu")
