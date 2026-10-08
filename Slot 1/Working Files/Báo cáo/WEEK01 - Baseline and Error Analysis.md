# WEEK01 — BASELINE AND ERROR ANALYSIS

Chủ đề: Hỏi đáp trên ảnh tài liệu (Document VQA) — OLP AI PTIT 2026, Vòng loại
Người thực hiện: Huỳnh Thuyên Nam
Kỳ báo cáo: Tuần 1

Đây là bản tổng hợp kết quả cuối tuần theo §II.5 của hướng dẫn Topic Team, viết bổ sung 22/09/2026. Báo cáo tiến độ cùng kỳ là `WEEK01 - Báo cáo tiến độ (16-18.09)`.

---

## 1. Mức độ hoàn thành so với mục tiêu trong Outline

Mục tiêu nhóm đã đặt trong Outline (bảng kế hoạch, dòng **Tuần 1**):

> **Nội dung trọng tâm:** Tổng hợp kỹ thuật từ 10 Paper SOTA · Xây dựng Harness đo ANLS/Ev-F1 · Chuẩn hóa Phân định Bài toán vs Phương pháp.
> **Mốc đánh giá:** Xác lập Baseline TA Minh 95.45 và trần oracle 10.909/11.000 (99,17%), đo không dùng nhãn.

| Mục tiêu trong Outline | Chỉ tiêu | Kết quả đo được | Trạng thái |
|---|---:|---:|---|
| Xác lập baseline TA Minh trên training_set | 95,45 | **95,45** (ANLS 96,25 · EvF1 90,89) | ĐẠT |
| Xác lập trần oracle, **đo không dùng nhãn** | 10.909/11.000 = 99,17% | **99,17%** | ĐẠT |
| Sản phẩm: 10 paper SOTA + Paper Tracker | — | `papers/01-BoundingDocs/` → `papers/10-LiGT-ReceiptVQA/`, `papers/Paper_Tracker.md` | ĐẠT |
| Sản phẩm: harness đo ANLS / Evidence-F1 | — | `code/anls.py`, `code/evidence_f1.py` — mỗi file có self-check chạy được | ĐẠT |
| Sản phẩm: Outline Project chính thức | — | `Outline Project - Hỏi đáp trên ảnh tài liệu (Document VQA).docx` | ĐẠT |

Mục tiêu **không** đặt trong Outline nhưng đo được trong tuần và quyết định toàn bộ hướng đi các tuần sau:

| Hạng mục | Kết quả | Ý nghĩa |
|---|---:|---|
| Điểm mất của baseline tập trung ở đâu | **93,1%** ở argmax/argmin | Cải thiện tập trung, không rải đều 8 dạng |
| Nguyên nhân gốc của phần mất điểm | **403/403** ca sai là "đúng bảng, sai hàng" | Lỗi chọn ô rời rạc, không phải lỗi đọc chữ |
| Số dạng baseline đã chạm trần | **5 / 8** (6.693 câu) | Nửa bài toán không còn gì để cải thiện |
| Đáp án tồn tại nguyên văn trong OCR | 6 dạng trích xuất: **9.144 câu, 0,0%** thiếu | Hệ thống chỉ chép là đủ cho 83% số câu |

Kết luận của tuần: **bài toán đã được định vị xong trước khi viết một dòng code giải nào.** Biết được trần oracle, biết được chỗ mất điểm, và biết được nguyên nhân gốc là lỗi chọn ô rời rạc — cả ba đều là số đo, không phải suy đoán. Đây là cơ sở để Tuần 2 chỉ tập trung vào đúng khâu tái dựng hàng logic thay vì cải thiện OCR hay đổi mô hình lớn hơn.

---

## 2. Kết quả Tuần 1

### 2.1. Hai mốc so sánh đã xác lập

| Hạng mục | Kết quả | Cách kiểm chứng |
|---|---|---|
| Baseline TA Minh trên 11.000 câu | ANLS 96,25 · Evidence-F1 90,89 · **Score 95,45** | `reference/mentor_solution_extract.txt` |
| Trần oracle (điểm tối đa khi biết trước ô đúng) | **99,17% (10.909/11.000)** | `code/oracle_ceiling.py` + `code/check_validity.py` |
| Harness đo điểm | `anls.py` + `evidence_f1.py`, self-check chạy được | `python code/anls.py`, `python code/evidence_f1.py` |

Trần oracle là kết quả đo, không phải suy đoán: nếu định vị bằng chứng là bài toán **chọn ô rời rạc trên lưới OCR có sẵn**, thì tồn tại một quy tắc chọn ô đạt gần tuyệt đối. Nghĩa là gần như toàn bộ 4,55 điểm còn thiếu của baseline nằm ở khâu chọn ô, không phải ở khâu suy luận.

Trần oracle là điểm tối đa **khi biết trước ô đúng** — không phải điểm một hệ thống thực tế đạt được. Nó chứng minh bài toán giải được trên lưới OCR, không chứng minh hệ thống không-dùng-mô-hình đạt 99,17 điểm.

### 2.2. Định vị chỗ baseline mất điểm

Phân rã 95,45 theo dạng suy luận:

| Dạng suy luận | Số câu | ANLS | Evidence-F1 | Score | Đóng góp vào số câu sai |
|---|---:|---:|---:|---:|---:|
| lookup, count, sum, compare, cross_page_sum | 6.693 | — | — | **100,00** | 0,0% |
| visual_bold_lookup | 535 | 96,90 | 74,82 | 93,59 | 6,9% |
| argmax | 1.898 | 90,02 | 77,52 | 88,14 | 44,9% |
| argmin | 1.874 | 89,00 | 76,49 | 87,12 | 48,2% |
| **Toàn bộ** | **11.000** | — | — | — | **100,0%** |

**93,1% số câu sai tập trung ở đúng hai dạng argmax/argmin.** Năm dạng còn lại (6.693 câu) đã đạt 100,00 — không còn gì để cải thiện ở đó.

Cột "Đóng góp vào số câu sai" tính theo **điểm bị mất**, không phải theo số câu. Hai cách cho kết quả khác nhau: theo điểm là 44,9 / 48,2 / 6,9%; theo số câu là 43,9 / 47,7 / 8,4%.

### 2.3. Nguyên nhân gốc

Từ 3.772 dòng dữ liệu chẩn đoán argmax/argmin của chính repo TA Minh:

- 89,0% (3.357/3.772) chọn đúng hàng logic → tỷ lệ trả lời đúng 100,0%.
- 415 ca (11,0%) chọn lệch hàng logic → tỷ lệ trả lời đúng chỉ còn 2,9% (12/415).
- **403 câu trả lời sai — và 403/403 đều là "đúng bảng, sai hàng"**, không có ca nào sai vì đọc nhầm số.
- 69,8% (220/315) ca thất bại có hàng bị nhầm là hàng đã từng xuất hiện trước đó trong bảng.
- 120/315 ca thất bại có khoảng cách giá trị tương đối giữa hàng đúng và hàng sai < 0,10 (khoảng cách tuyệt đối < 0,10 chỉ có 3/315).

Bốn con số 439 / 415 / 403 / 315 lồng nhau nhưng khác tiêu chí đếm:

| Con số | Tiêu chí đếm | Đếm trên tập |
|---|---|---|
| 439 | `solver_logical_row_index ≠ expected_logical_row_index` | 3.772 |
| 415 | `solver_row ≠ expected_row` | 3.772 |
| 403 | `is_correct ≠ True` | 3.772 |
| 315 | Tập con của cả 415 và 403 — thất bại ngay cả khi đã xét lại hàng thứ hai | 403 |

Kết luận: **lỗi chọn ô rời rạc, không phải lỗi đọc chữ hay lỗi suy luận.** Cải thiện OCR hay đổi sang mô hình lớn hơn không giải quyết được — phải sửa khâu tái dựng hàng logic.

### 2.4. Hai cái bẫy của dữ liệu đã đo được

- **Bẫy dấu phân cách số:** 25,3% ô dùng dấu `.` làm phân cách nghìn (ví dụ `1.850`). Đọc thành `1.85` thì sai một ký tự nhưng ANLS cho 0 điểm cho cả câu.
- **Đáp án không tồn tại trong OCR:** 14,3% (1.577/11.000) câu có đáp án không tồn tại dạng chuỗi trong văn bản OCR. Con số này **không phân bố đều**: `sum` 85,1% (1.540/1.810) và `cross_page_sum` 80,4% (37/46), còn **sáu dạng trích xuất (9.144 câu) đạt 0,0%** — đáp án luôn tồn tại nguyên văn.

Đây là giới hạn của hệ thống chỉ biết chép, **không phải** giới hạn của hướng tiếp cận: hai dạng bị ảnh hưởng chính là hai dạng baseline đã đạt 100,00.

### 2.5. Thiết kế thí nghiệm đã chốt

| Cấu hình | Phương pháp | Vai trò |
|---|---|---|
| A | Baseline TA Minh (95,45) | Mốc nền |
| B | Tái dựng hàng logic + căn chỉnh giá trị, **không dùng mô hình** | Đo hiệu quả thực tế của hướng heuristics |
| C | B + LayoutLMv3 / LayoutXLM | Đo giá trị gia tăng của spatial embedding |
| D | C + Qwen2.5-VL-3B | Đo giá trị gia tăng của VLM lớn |

Điểm quan trọng về mặt nghiên cứu: **Cấu hình B đo trực tiếp future direction, nên không được gộp nó vào tầng model.** Đây là lý do Outline đặt câu hỏi theo thứ tự trần không-model là bao nhiêu → mất ở đâu → sửa được bao nhiêu → rồi mới đến mô hình, thay vì hỏi thẳng "kết hợp cơ chế SOTA thế nào".

---

## 3. Phát hiện chính của tuần

**1. Trần oracle biến "cải thiện mô hình" thành câu hỏi sai.** 99,17% đạt được chỉ bằng cách chọn ô trên lưới OCR có sẵn ⇒ 4,55 điểm thiếu của baseline không nằm ở năng lực mô hình. Đây là phát hiện định hướng cho cả bốn tuần còn lại: mọi nỗ lực đổ vào khâu chọn ô trước, mô hình sau.

**2. Phần mất điểm tập trung, không rải đều.** 93,1% ở argmax/argmin, và 5/8 dạng đã chạm trần. Nghĩa là bài toán không cần một giải pháp tổng quát cho 8 dạng — cần đúng một sửa chữa ở một khâu.

**3. 403/403 lỗi là "đúng bảng, sai hàng".** Con số này loại trừ toàn bộ giả thuyết về OCR kém hoặc suy luận số học sai. Nó thu hẹp không gian giải pháp xuống đúng một khâu: tái dựng hàng logic.

**4. 83% số câu chỉ cần chép nguyên văn.** Sáu dạng trích xuất (9.144 câu) có đáp án luôn tồn tại trong OCR với tỷ lệ thiếu 0,0%. Phần đáp án phải *tính ra* chỉ nằm ở `sum` và `cross_page_sum` — và cả hai dạng đó baseline đã đạt 100,00.

---

## 4. Khó khăn và điểm dừng

- **Một con số trong bản nộp 18/09 sai và đã được sửa.** Bản đầu ghi trần "100,00% (11.000/11.000)"; đo lại ngày 21/09 bằng harness không đọc nhãn cho **99,17%**. Nguyên nhân: harness cũ (`audit_ceiling.py`) lấy `is_bold` từ `cell_annotations.jsonl` — file **nhãn**. Phần thiếu 0,83% nằm trọn ở `visual_bold_lookup`. Chi tiết và bảng đối chiếu ở `WEEK02 - Báo cáo tiến độ`.
- **Cùng bản nộp đó đếm nhầm nhóm dạng:** viết "sáu dạng đạt 100,00", thực tế là **năm** dạng (6.693 câu). Dạng thứ sáu `visual_bold_lookup` chỉ đạt 93,59 và đã bị đếm nhầm vào nhóm 100,00.
- **Ràng buộc về tính hợp lệ của suy luận.** Pipeline suy luận chỉ được đọc `manifest.jsonl`, `questions.jsonl`, `images/`, `ocr/` — tuyệt đối không chạm `labels.jsonl` và `cell_annotations.jsonl` (hai file này chỉ dùng để đo). Cách tự kiểm: đổi tên hai file nhãn rồi chạy lại, pipeline vẫn chạy được thì mới hợp lệ. Chính lỗi ở mục trên là ví dụ cho thấy ràng buộc này có thật và dễ vi phạm.
- **Cảnh báo overfit đã lộ ra ngay trong tuần 1:** năm dạng đạt đúng 100,00 là dấu hiệu dữ liệu sinh theo mẫu. Cần giao thức đánh giá chống overfit trước khi tin bất kỳ con số nào — việc này chuyển sang Tuần 2.
- **Chỉ training_set có nhãn.** `public_test` và `private_test` không có `labels.jsonl` / `cell_annotations.jsonl`; `questions.jsonl` trên test cũng không có trường `reasoning_type` ⇒ intent router buộc phải phân loại dạng câu hỏi từ văn bản câu hỏi. Đã kiểm tra bằng mắt: cả hai split test đều có thư mục `ocr/`, cấu trúc block y hệt train.
- **Điểm dừng đã thống nhất với TA:** mọi thay đổi output hoặc chiến lược đã thống nhất trong Outline phải trao đổi với TA trước (§II.3).

---

## 5. Kế hoạch đã hứa cho Tuần 2

| # | Việc | Kết quả mong đợi |
|---|---|---|
| 1 | Baseline luật thuần Python cho cả 8 dạng, khớp theo ranh giới từ / cả khối | Điểm end-to-end thật của Cấu hình B, đo bằng chính `anls.py` + `evidence_f1.py` |
| 2 | Ưu tiên argmax/argmin — cần so sánh tinh, không phải OCR tốt hơn | Vượt mốc 88,14 (Argmax) và 87,12 (Argmin) |
| 3 | Ưu tiên `visual_bold_lookup` — suy `is_bold` từ ảnh bằng `cv2.distanceTransform` | Đẩy Evidence-F1 lên trên 74,82 |
| 4 | Dựng lại lưới bảng từ `ocr/*.json` + ảnh trang | Lưới tái dựng đối chiếu được với lưới vàng trên train |
| 5 | Intent router không nhãn | Phân loại 8 dạng chỉ từ văn bản câu hỏi |
| 6 | Kiểm tra tính hợp lệ: đổi tên hai file nhãn rồi chạy lại | Pipeline vẫn chạy được (chứng minh không rò nhãn) |

Output dự kiến cuối tuần 2: `WEEK02 - Experiment Results` trong Working Files.

Trạng thái thực tế: kế hoạch này đã được thực hiện trọn trong Tuần 2, nhưng **không có điểm số mới trong nửa đầu tuần** — Cấu hình B chưa chạy end-to-end. Sản phẩm `WEEK02 - Experiment Results` đã hoàn thành ở nửa sau Tuần 2 (Cấu hình B đạt **0,968**, vượt baseline 95,45 trên cả ba split).
