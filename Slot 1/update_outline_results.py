"""Điền kết quả Cấu hình C vào Outline §IV + sửa 3 dòng số liệu cũ.

Chạy 1 lần. Backup tự động sang `.BACKUP-28-09.docx` trước khi sửa.

    python update_outline_results.py
"""
import shutil
import sys
from pathlib import Path

import docx
from docx.shared import Pt

BASE = Path(__file__).parent
SRC = BASE / "Outline Project - Hỏi đáp trên ảnh tài liệu (Document VQA).docx"
BAK = BASE / "Outline Project - Hỏi đáp trên ảnh tài liệu (Document VQA).BACKUP-28-09.docx"
sys.stdout.reconfigure(encoding="utf-8")

# Cột kết quả mới — mỗi dòng một cấu hình, khớp thứ tự bảng.
RESULTS = [
    "95,45 (mốc so sánh của TA)",
    "0,968 all · 0,967 dev · 0,972 eval\n"
    "argmax 0,936 · argmin 0,926 · visual_bold_lookup 0,831",
    "KHÔNG DỰNG — dư địa là oracle-only.\n"
    "Trần mọi bộ lọc hàng tĩnh: 99,14% dev · 98,93% eval (+0,019 điểm thi).\n"
    "4 họ luật không-cần-nhãn đều thất bại; tín hiệu thị giác tốt nhất chỉ trỏ\n"
    "đúng hàng vàng 9,1% trong 197 câu B sai. Hình học hàng đồng nhất tuyệt đối.\n"
    "⇒ Cấu hình B giữ nguyên, không đổi một dòng code nào.",
    "chưa chạy",
]

# 3 dòng số liệu cũ ở §III, nay là số của Cấu hình B (all) — ghi kèm số cũ.
FIXES = {
    "Argmax (1.898 câu): Đạt 88.14 điểm → Đóng góp 44.9% tổng số câu sai.":
        "Argmax (1.898 câu): 88,14 điểm (baseline TA) → 93,6 điểm (Cấu hình B). "
        "Dư địa còn lại là oracle-only — xem §IV, Cấu hình C.",
    "Argmin (1.874 câu): Đạt 87.12 điểm → Đóng góp 48.2% tổng số câu sai.":
        "Argmin (1.874 câu): 87,12 điểm (baseline TA) → 92,6 điểm (Cấu hình B). "
        "Dư địa còn lại là oracle-only — xem §IV, Cấu hình C.",
    "Visual Bold Lookup (535 câu): Đạt 93.59 điểm → Đóng góp 6.9% tổng số câu sai.":
        "Visual Bold Lookup (535 câu): 93,59 điểm (baseline TA) → 83,1 điểm (Cấu hình B). "
        "Trần tín hiệu ảnh 82,99% — đây là dư địa thật còn lại của hệ thống, "
        "hướng cho Cấu hình D.",
}


def add_cell(row):
    """Thêm một ô vào cuối hàng. python-docx không có API này."""
    import copy
    from docx.oxml.ns import qn
    from docx.table import _Cell
    tc = copy.deepcopy(row.cells[-1]._tc)
    for child in list(tc):
        if child.tag != qn("w:tcPr"):
            tc.remove(child)
    tcPr = tc.find(qn("w:tcPr"))
    if tcPr is not None:                      # bỏ nền sao chép, tô lại theo ý mình
        shd = tcPr.find(qn("w:shd"))
        if shd is not None:
            tcPr.remove(shd)
    row._tr.append(tc)
    return _Cell(tc, row.table)


def widen_grid(tbl):
    """Thêm cột vào `w:tblGrid`, co 4 cột cũ lại để TỔNG bề rộng không đổi.
    Bảng này có `tblW` cố định (14000 dxa); thêm cột mà không co lại thì bảng
    tràn ra ngoài trang."""
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    grid = tbl._tbl.find(qn("w:tblGrid"))
    cols = grid.findall(qn("w:gridCol"))
    total = sum(int(c.get(qn("w:w"))) for c in cols)
    share = total // (len(cols) + 1)
    scaled = [w * (total - share) // total for w in (int(c.get(qn("w:w"))) for c in cols)]
    new = scaled + [total - sum(scaled)]
    for c, w in zip(cols, new[:-1]):
        c.set(qn("w:w"), str(w))
    el = OxmlElement("w:gridCol")
    el.set(qn("w:w"), str(new[-1]))
    grid.append(el)
    assert sum(new) == total
    return new


def set_widths(tbl, widths):
    """Ghi `tcW` cho mọi ô — Word ưu tiên tcW hơn tblGrid khi cả hai có mặt."""
    from docx.oxml.ns import qn
    for row in tbl.rows:
        for cell, w in zip(row.cells, widths):
            tcPr = cell._tc.get_or_add_tcPr()
            tcW = tcPr.find(qn("w:tcW"))
            if tcW is None:
                from docx.oxml import OxmlElement
                tcW = OxmlElement("w:tcW")
                tcPr.append(tcW)
            tcW.set(qn("w:w"), str(w))
            tcW.set(qn("w:type"), "dxa")


def shade(cell, fill):
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    el = OxmlElement("w:shd")
    el.set(qn("w:val"), "clear")
    el.set(qn("w:fill"), fill)
    cell._tc.get_or_add_tcPr().append(el)


def fill(cell, text):
    cell.text = ""
    for i, line in enumerate(text.split("\n")):
        par = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        par.add_run(line).font.size = Pt(8)


def main():
    if not BAK.exists():
        shutil.copy2(SRC, BAK)
        print(f"backup -> {BAK.name}")

    d = docx.Document(SRC)
    from docx.table import Table

    tbl = None
    for i, el in enumerate(d.element.body.iterchildren()):
        if i == 51:
            tbl = Table(el, d)
    assert tbl is not None and len(tbl.rows) == 5, "bảng ablation đổi cấu trúc"

    # ô tiêu đề: lấy màu nền từ ô tiêu đề cũ để cột mới đồng bộ
    from docx.oxml.ns import qn
    hdr_fill = tbl.rows[0].cells[0]._tc.find(qn("w:tcPr")).find(qn("w:shd"))
    hdr_fill = hdr_fill.get(qn("w:fill")) if hdr_fill is not None else "D9E2F3"
    widths = widen_grid(tbl)

    for row, text in zip(tbl.rows, ["Kết quả đo được"] + RESULTS):
        cell = add_cell(row)
        if row is tbl.rows[0]:
            shade(cell, hdr_fill)
        fill(cell, text)
    set_widths(tbl, widths)
    assert len(tbl._tbl.find(qn("w:tblGrid")).findall(qn("w:gridCol"))) == 5

    n = 0
    for par in d.paragraphs:
        if par.text.strip() in FIXES:
            new = FIXES[par.text.strip()]
            for r in par.runs[1:]:
                r.text = ""
            par.runs[0].text = new
            n += 1
    assert n == 3, f"chỉ sửa được {n}/3 dòng số liệu cũ"

    d.save(SRC)
    print(f"OK  thêm cột 'Kết quả đo được' (5 dòng) + sửa {n} dòng số liệu cũ")


if __name__ == "__main__":
    main()
