"""Bổ sung các mục còn thiếu cho Outline Project (Document VQA).

Chạy 1 lần trên bản gốc; backup đã có ở .BACKUP.docx.
Thêm: prose Mục II, Mục III.4 (định nghĩa các con số), nguyên tắc đánh giá ở Mục V,
Mục VII (hạn chế & rủi ro), Mục VIII (đóng góp Topic Team). Đổi VI -> IX cho tài liệu tham khảo.
"""
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parents[2]
SRC = BASE / "Outline Project - Hỏi đáp trên ảnh tài liệu (Document VQA).docx"
INDENT = 457200  # khớp mức thụt của các bullet hiện có


def shade(cell, fill):
    el = OxmlElement("w:shd")
    el.set(qn("w:val"), "clear")
    el.set(qn("w:fill"), fill)
    cell._tc.get_or_add_tcPr().append(el)


def find(doc, prefix):
    """Paragraph đầu tiên có text bắt đầu bằng `prefix`."""
    for p in doc.paragraphs:
        if p.text.strip().startswith(prefix):
            return p
    raise LookupError(prefix)


def para(doc, text, style=None, indent=None, bold=False):
    p = doc.add_paragraph(style=style) if style else doc.add_paragraph()
    if indent is not None:
        p.paragraph_format.left_indent = indent
    run = p.add_run(text)
    run.bold = bold
    return p


def anchor_after(node, ref):
    """Chèn node XML ngay sau ref; trả về node để làm mốc cho lần chèn kế."""
    ref.addnext(node)
    return node


def add_after(doc, ref_el, blocks):
    """blocks: list (kind, payload). Trả về element cuối."""
    cur = ref_el
    for kind, payload in blocks:
        if kind == "h":
            p = para(doc, payload, style="Heading 2")
        elif kind == "h1":
            p = para(doc, payload, style="Heading 1")
        elif kind == "b":
            p = para(doc, payload, indent=INDENT)
        elif kind == "p":
            p = para(doc, payload)
        elif kind == "note":
            p = para(doc, payload, indent=INDENT)
            for r in p.runs:
                r.font.size = Pt(10)
                r.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
        elif kind == "table":
            head, rows = payload
            t = doc.add_table(rows=1, cols=len(head))
            t.style = doc.tables[0].style  # khớp style bảng có sẵn của file
            t.alignment = WD_TABLE_ALIGNMENT.CENTER
            for k, txt in enumerate(head):
                c = t.rows[0].cells[k]
                c.text = ""
                c.paragraphs[0].add_run(txt).bold = True
                shade(c, "D9E2F3")
            for row in rows:
                cells = t.add_row().cells
                for k, txt in enumerate(row):
                    cells[k].text = txt
            cur = anchor_after(t._tbl, cur)
            continue
        else:
            raise ValueError(kind)
        cur = anchor_after(p._p, cur)
    return cur


doc = Document(SRC)

# ---------------------------------------------------------------- II. prose
anchor = find(doc, "II. TỔNG QUAN NGHIÊN CỨU")
anchor = anchor._p.getnext()  # Heading II -> Table ánh xạ paper
assert anchor.tag.endswith("}tbl"), anchor.tag
add_after(doc, anchor, [
    ("p", "Đọc bảng trên theo cột: mỗi paper đóng góp một tư duy phương pháp (cột giữa) cho đúng một bài toán con (cột phải). Ba quan sát rút ra:"),
    ("b", "Không paper nào giải trực tiếp bài toán \"chọn hàng logic trên lưới OCR\". Cả 10 paper đều giả định bảng đã ở dạng cấu trúc (HTML / markdown / chuỗi tuyến tính hóa), trong khi dữ liệu cuộc thi chỉ có ảnh tài liệu + block OCR phẳng. Đây là gap G3 của phần tổng hợp 10 paper: TAPAS thiếu toán tử MAX/MIN, LayoutLMv3 chỉ làm trích xuất."),
    ("b", "TAPAS đóng góp tư duy tách \"chọn ô\" khỏi \"thi hành toán tử\" — đúng khuôn Router + Solver ở Mục IV: phần cần học chỉ là chọn đúng ô, phần tính toán giao hết cho Python tất định."),
    ("b", "LayoutLMv3 và Qwen2.5-VL không phải hai lựa chọn thay thế nhau mà là hai mức trong cùng một thang: model nông (hiểu layout, không sinh văn bản) và VLM (sinh văn bản, hiểu ngữ nghĩa). Thang A → B → C → D ở Mục IV đi đúng theo hai mức này."),
])

# ---------------------------------------------------------------- III.4
anchor = find(doc, "Nhầm lẫn hàng trùng giá trị")
add_after(doc, anchor._p, [
    ("h", "4. Định nghĩa các con số thống kê lỗi"),
    ("p", "Bốn con số dưới đây đo trên cùng 3.772 câu argmax/argmin của training_set và lồng nhau, nhưng khác tiêu chí — người đọc dễ nhầm nếu không định nghĩa:"),
    ("table", (
        ["Con số", "Tiêu chí đếm", "Đếm trên tập"],
        [
            ["439", "solver_logical_row_index ≠ expected_logical_row_index", "3.772"],
            ["415", "solver_row ≠ expected_row", "3.772"],
            ["403", "is_correct ≠ True", "3.772"],
            ["315", "Tập con của cả 415 và 403 — thất bại ngay cả khi đã xét lại hàng thứ hai", "403"],
        ],
    )),
    ("p", "Quan hệ lồng nhau: 315 ⊂ 403 ⊂ 415 ⊂ 439. Hiệu giữa các mức: 439 − 415 = 24 ca lệch chỉ số hàng logic nhưng vẫn trỏ đúng hàng vật lý; 415 − 403 = 12 ca lệch hàng nhưng vẫn trả lời đúng; 403 − 315 = 88 ca trả lời sai nhưng không phải do nhầm hàng trùng giá trị."),
    ("p", "Cột \"Đóng góp vào số câu sai\" ở Mục III.2 tính theo ĐIỂM BỊ MẤT, không phải theo số câu. Hai cách cho kết quả khác nhau: theo điểm là 44,9 / 48,2 / 6,9%; theo số câu là 43,9 / 47,7 / 8,4%. Báo cáo chọn cách theo điểm vì thước đo của cuộc thi là điểm số, nhưng con số số câu được ghi kèm ở đây để đối chiếu."),
    ("p", "Con số \"trần oracle 100,00%\" là điểm tối đa đạt được KHI BIẾT TRƯỚC ô đúng (gold evidence) — không phải điểm một hệ thống thực tế đạt được. Nó chứng minh bài toán giải được hoàn toàn trên lưới OCR, không chứng minh hệ thống không-dùng-mô-hình đạt 100,00 điểm."),
])

# ---------------------------------------------------------------- V. nguyên tắc đánh giá
anchor = find(doc, "VI. TÀI LIỆU THAM KHẢO")
blocks = [
    ("h", "Nguyên tắc đánh giá (chống overfit)"),
    ("b", "Chia training_set theo TÀI LIỆU, không chia theo câu hỏi — vì 10 câu hỏi dùng chung một tài liệu, chia theo câu sẽ rò rỉ thông tin giữa hai phần: 880 tài liệu để phát triển luật, 220 tài liệu giữ riêng để đánh giá. Chỉ nhìn phần giữ riêng sau khi đã chốt luật."),
    ("b", "public_test (1.000 câu) chỉ có document_id / question / question_id, không có nhãn ⇒ chỉ dùng làm kiểm tra cuối, không dùng để tinh chỉnh."),
    ("b", "Mỗi cấu hình B / C / D báo cáo kèm hai số: điểm trên dev và điểm trên eval. Chênh lệch dev − eval là thước đo trực tiếp mức overfit, thay cho việc chỉ báo cáo một con số trên train."),

    ("h1", "VII. HẠN CHẾ VÀ RỦI RO ĐÃ NHẬN DIỆN"),
    ("h", "1. Rủi ro overfit vào tập train"),
    ("p", "Toàn bộ luật và toàn bộ đánh giá hiện dựa trên training_set. Mức độ nghiêm trọng đã đo được: luật lõi của trần oracle (\"nhãn của hàng là ô trái nhất không phải số\") đúng 3.772/3.772 = 100,00% trên toàn bộ argmax/argmin. Một luật đúng tuyệt đối như vậy khớp QUY ƯỚC SINH DỮ LIỆU chứ không phải suy ra từ dữ liệu, nên không có gì bảo đảm nó đúng trên layout của private test. Biện pháp: chia theo tài liệu như ở Mục V và kiểm tra luật có phụ thuộc đặc điểm riêng của mẫu không."),
    ("h", "2. Dấu vân tay dữ liệu sinh theo mẫu"),
    ("p", "1.100 tài liệu × đúng 10 câu/tài liệu = 11.000 câu, không tài liệu nào lệch. Năm dạng câu hỏi (lookup, count, sum, compare, cross_page_sum — 6.693 câu) đạt đúng 100,00 điểm. Đây là dấu hiệu dữ liệu được sinh theo template, và cũng là lý do không nên diễn giải các mức 100,00% như bằng chứng năng lực hệ thống."),
    ("h", "3. Trần oracle hiện chưa đo được độc lập với nhãn"),
    ("p", "Harness đo trần oracle hiện tại (audit_ceiling.py) tra text ô theo bbox bằng cách đọc cell_annotations.jsonl — đây là file NHÃN. Điều này vi phạm ràng buộc hợp lệ của chính dự án (pipeline không được chạm file nhãn), và file này không tồn tại trên public_test / private_test. Cần viết lại harness chỉ dùng ocr/*.json (có bbox và text ở mức block) để tái dựng lưới rồi khớp bbox bằng chứng vàng với block OCR gần nhất. Trần oracle chỉ có ý nghĩa khi đo được mà không chạm nhãn."),
    ("h", "4. Giới hạn của tập kiểm tra"),
    ("p", "public_test và private_test không có trường reasoning_type ⇒ không thể phân rã lỗi theo dạng câu hỏi trên tập đích. Router phải tự phân loại câu hỏi, và sai số của Router trở thành một nguồn lỗi mới chưa đo được trên train — cần đo riêng độ chính xác phân loại của Router trước khi quy mọi mất mát điểm cho khâu chọn hàng."),

    ("h1", "VIII. ĐÓNG GÓP DỰ KIẾN CHO BÁO CÁO TOPIC TEAM"),
    ("p", "Câu hỏi nghiên cứu khái quát: với bài toán hỏi đáp trên bảng có lưới OCR tốt, luật không dùng mô hình đạt được đến đâu, và mô hình học sâu chỉ thực sự cần thiết ở loại lỗi nào? Chất liệu trả lời, gắn với phần gap tổng hợp từ 10 paper:"),
    ("table", (
        ["Phát hiện", "Số liệu", "Gap tương ứng"],
        [
            ["Tầng không-dùng-mô-hình chạm trần oracle ở nhóm dạng tra cứu và tính toán", "5/8 dạng đạt 100,00 (6.693 câu)", "G3 — cả 10 paper thiếu toán tử MAX/MIN"],
            ["Toàn bộ phần mất điểm còn lại nằm ở khâu chọn hàng logic, không phải ở khâu đọc ô", "93,1% điểm mất ở argmax/argmin", "G3 — không paper nào làm chọn hàng trên lưới OCR"],
            ["Lỗi còn lại là nhầm hàng có giá trị trùng nhau — cần ngữ nghĩa, không cần hình học", "69,8% số ca thất bại", "G2 — biểu diễn vị trí và ngữ cảnh"],
            ["Sau khi luật đã đủ tốt, phần sai số còn lại mới là chỗ mô hình học sâu có giá trị biên", "So sánh C/D với B trên cùng tập eval", "G1, G4 — kiến trúc và dữ liệu huấn luyện"],
        ],
    )),
    ("p", "Kết luận dự kiến: trên bảng có lưới OCR tốt, phần lớn điểm số đến từ tái dựng cấu trúc chứ không từ hiểu ngữ nghĩa; mô hình học sâu chỉ thực sự cần thiết ở tầng phân biệt các hàng có giá trị trùng nhau — đúng loại lỗi mà luật hình học không thể giải."),
]

# mọi mục mới chèn TRƯỚC phần tài liệu tham khảo, rồi đánh số lại VI -> IX
ref_el = anchor._p
add_after(doc, ref_el.getprevious(), blocks)
for run in anchor.runs:
    if "VI." in run.text:
        run.text = run.text.replace("VI.", "IX.", 1)
        break

doc.save(SRC)
print(f"OK  {SRC.name}")
print(f"    paragraphs: {len(doc.paragraphs)}   tables: {len(doc.tables)}")
