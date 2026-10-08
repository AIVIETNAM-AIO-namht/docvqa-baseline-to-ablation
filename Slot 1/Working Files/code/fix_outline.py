"""Sửa 4 chỗ lệch giữa Outline và số liệu đã đo (22/09).

1. Mục VII.3  — trần oracle nay đã đo được không nhãn (99,17%), không còn là vấn đề mở.
2. Mục VII.4  — sai số Router nay đã đo (11.000/11.000), nguồn lỗi này bằng 0.
3. Tuần 1     — "trần bằng chứng 11.000/11.000" -> trần oracle 10.909/11.000 (99,17%).
4. Đếm paper  — 6 -> 10 ở Mục I và Tuần 1; bổ sung Qwen2-VL vào danh mục tham khảo (đủ 10).

Chạy 1 lần. Backup: *.BACKUP2.docx
"""
import sys
from pathlib import Path

from docx import Document

sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parents[2]
SRC = BASE / "Outline Project - Hỏi đáp trên ảnh tài liệu (Document VQA).docx"


def find(doc, prefix):
    for p in doc.paragraphs:
        if p.text.strip().startswith(prefix):
            return p
    raise LookupError(prefix)


def set_text(p, text):
    """Ghi đè text, giữ định dạng của run đầu."""
    p.runs[0].text = text
    for r in p.runs[1:]:
        r.text = ""


def set_cell(cell, text):
    p = cell.paragraphs[0]
    if p.runs:
        set_text(p, text)
    else:
        p.add_run(text)


def cell_at(t, text, col):
    """Ô (hàng chứa `text`, cột `col`)."""
    for row in t.rows:
        if text in row.cells[0].text:
            return row.cells[col]
    raise LookupError(text)


doc = Document(SRC)

# ------------------------------------------------ 0. Mục III.4 — trần oracle 100,00% -> 99,17%
set_text(find(doc, 'Con số "trần oracle 100,00%"'), (
    'Con số "trần oracle 99,17%" (10.909/11.000, đo không dùng nhãn) là điểm tối đa đạt được KHI '
    'BIẾT TRƯỚC ô đúng (gold evidence) — không phải điểm một hệ thống thực tế đạt được. Nó chứng '
    'minh bài toán giải được gần hoàn toàn trên lưới OCR, không chứng minh hệ thống không-dùng-mô-hình '
    'đạt 99,17 điểm. Phần thiếu 0,83% nằm trọn ở visual_bold_lookup, đúng loại thông tin mà OCR '
    'không ghi nhận.'
))

# ------------------------------------------------ 1. Mục VII.3
set_text(find(doc, "3. Trần oracle hiện chưa"), "3. Trần oracle đã đo được độc lập với nhãn")
set_text(find(doc, "Harness đo trần oracle hiện tại"), (
    "Đã sửa xong 21/09. Harness cũ (audit_ceiling.py) tra text ô theo bbox bằng cách đọc "
    "cell_annotations.jsonl — file NHÃN — nên vi phạm ràng buộc hợp lệ của chính dự án và không "
    "chạy được trên public_test / private_test. Harness mới (oracle_ceiling.py) chỉ dùng ocr/*.json "
    "và ảnh trang: gom block theo y0, sắp theo x0 để tái dựng lưới, rồi khớp bbox bằng chứng vàng "
    "với block OCR gần nhất. Tính hợp lệ được kiểm tự động bằng check_validity.py (đổi tên file "
    "nhãn rồi chạy lại, kết quả không đổi). Trần oracle: 10.909/11.000 = 99,17% — dev 99,16% · "
    "eval 99,23%, chênh 0,07 điểm % ⇒ lưới không phụ thuộc tài liệu nào. Phần thiếu 0,83% nằm "
    "trọn ở visual_bold_lookup (82,99%): is_bold là trường duy nhất không có tương ứng trong OCR "
    "(đề bài ghi rõ \"OCR không ghi nhận định dạng chữ\"), và 5 phép đo độ dày nét khác nhau đều "
    "dừng ở 82,99% ⇒ đây là trần của tín hiệu ảnh, không phải lỗi cài đặt."
))

# ------------------------------------------------ 2. Mục VII.4
set_text(find(doc, "public_test và private_test không có trường reasoning_type"), (
    "public_test và private_test không có trường reasoning_type ⇒ không thể phân rã lỗi theo dạng "
    "câu hỏi trên tập đích. Đã xử lý bằng bộ định tuyến không nhãn (intent_router.py): luật regex "
    "loại trừ dần chỉ đọc chữ của câu hỏi, không đọc labels.jsonl. Kết quả 11.000/11.000 = 100,00% "
    "trên train, nhưng con số này không tự nó là bằng chứng — luật được viết sau khi đã khảo sát "
    "template của train, nên đúng tuyệt đối là hệ quả của quy ước sinh dữ liệu. Bằng chứng thật là "
    "phân bố dự đoán trên hai tập KHÔNG có nhãn: cả 8 dạng đều khớp phân bố train trong ±1 điểm % "
    "(public_test và private_test). Vậy nguồn lỗi do Router ≈ 0, mọi mất mát điểm còn lại quy được "
    "cho khâu chọn hàng. Giới hạn còn lại: nếu private_test dùng template câu hỏi khác, luật regex "
    "sẽ vỡ — đây là rủi ro chưa đo được."
))

# ------------------------------------------------ 3. Tuần 1 milestone
set_cell(cell_at(doc.tables[3], "Tuần 1", 3), (
    "- Xác lập Baseline TA Minh 95.45 và trần oracle 10.909/11.000 (99,17%), đo không dùng nhãn."
))

# ------------------------------------------------ 4. Đếm paper: 6 -> 10
p = find(doc, "Phương pháp thực hiện (Proposed Methods)")
p.runs[2].text = "10 bài báo khoa học cốt lõi"
p.runs[3].text = (
    " (BoundingDocs, LMDX, DocLLM, LayoutLMv3, TAPAS, DocVQA, Qwen2-VL, Qwen2.5-VL, "
    "DocExplainerV0, LiGT) kết hợp với thuật toán Heuristics không gian 2D bằng Python thuần "
    "để giải quyết 2 bài toán con trên theo lộ trình từ nhẹ đến nặng (Không model → Model nông → VLM)."
)
set_cell(cell_at(doc.tables[3], "Tuần 1", 1), (
    "- Tổng hợp kỹ thuật từ 10 Paper SOTA.- Xây dựng Harness đo ANLS/Ev-F1.- Chuẩn hóa Phân định "
    "Bài toán vs Phương pháp."
))

# ------------------------------------------------ 4b. Tham khảo: 9 -> 10 (thêm Qwen2-VL)
ref = find(doc, "Bai, S., et al. (2025). Qwen2.5-VL Technical Report")
new = ref.insert_paragraph_before(
    "Wang, P., Bai, S., Tan, S., Wang, S., Fan, Z., Bai, J., Chen, K., Liu, X., Wang, J., Ge, W., "
    "Fan, Y., Dang, K., Du, M., Ren, X., Men, R., Liu, D., Zhou, C., Zhou, J., & Lin, J. (2024). "
    "Qwen2-VL: Enhancing Vision-Language Model's Perception of the World at Any Resolution. "
    "[arXiv:2409.12191]"
)
new.style = ref.style

doc.save(SRC)

n_ref = sum(1 for q in doc.paragraphs if "(20" in q.text and ")" in q.text
            and q.paragraph_format.left_indent is None and q.style.name == "Normal")
print(f"OK  {SRC.name}")
print(f"    paragraphs: {len(doc.paragraphs)}   tables: {len(doc.tables)}")
