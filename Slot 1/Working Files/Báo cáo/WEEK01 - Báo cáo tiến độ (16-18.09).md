# BÁO CÁO TIẾN ĐỘ — 16/09 → 18/09/2026

Chủ đề: Hỏi đáp trên ảnh tài liệu (Document VQA) — OLP AI PTIT 2026, Vòng loại

Người thực hiện: Huỳnh Thuyên Nam

Kỳ báo cáo: 03 ngày (16/09 – 18/09/2026)

Bản đính chính: 22/09/2026 (xem mục 5 — hai con số đã sửa so với bản nộp đầu)

---

## 1. Tổng quan công việc đã thực hiện trong 03 ngày

| Ngày | Công việc | Sản phẩm để lại |
|---|---|---|
| 16/09 | Đọc đề bài và tài liệu hướng dẫn Topic Team; chốt subtopic; bắt đầu thu thập paper; tải repo bài giải của TA Minh về máy | reference/exam_question_docvqa.md, reference/Document hướng dẫn Topic Team.pdf, reference/hoi_dap_tren_anh_tai_lieu.md, papers/01-BoundingDocs/ |
| 16/09 (tối) | Đọc mã nguồn và tệp chẩn đoán của repo TA Minh; xác định được nơi baseline mất điểm | 5 tệp olp-ai-ptit-2026-preliminary-round/DocViVQA/artifacts/analysis/diagnostics/argextreme_*.csv |
| 17/09 | Thu thập đủ 10 paper, trích văn bản thô để đọc; lập Paper Tracker | papers/02-LMDX/ → papers/10-LiGT-ReceiptVQA/, papers/_txt/, papers/Paper_Tracker.md |
| 17/09 | Trích xuất quy chế và bài giải tham chiếu của TA Minh thành văn bản tra cứu được | reference/guide_extract.txt, reference/mentor_solution_extract.txt |
| 17/09 | Dựng harness đo điểm (ANLS + Evidence-F1) và bộ audit dữ liệu | anls.py, evidence_f1.py, audit_dataset.py, audit_solver.py, audit_sum.py |
| 17/09 | Chẩn đoán baseline TA Minh bằng 9 script probe độc lập | probe_mentor_arg.py, audit_headroom.py, probe_argmax_rule.py, audit_ceiling.py, probe_evidence_shape.py, probe_ev_extra.py, probe_gold_rows.py, probe_arg_ev.py, audit_rule_system.py |
| 18/09 | Tổng hợp lý thuyết bài toán (nguyên lý, công thức); gom gap chung và hạn chế của 10 paper | Slot 1/Working Files/WEEK01 - Hieu bai toan, nguyen ly, cong thuc.md, papers/GAP CHUNG - 10 paper va huong ap dung.md, papers/Tổng hợp hạn chế 10 paper.md |
| 18/09 | Chốt Project Outline chính thức để nộp TA | Outline Project - Hỏi đáp trên ảnh tài liệu (Document VQA).md |
| 18/09 | Kiểm chứng quy ước ghép cặp Evidence-F1 của grader bằng 2 script probe bổ sung | probe_evidence_matching.py, probe_greedy_vs_hungarian.py |

Tổng cộng: 16 script Python phân tích (tất cả chỉ đọc và in kết quả, không ghi đè dữ liệu), 10 paper được đọc và ghi chú, 6 tài liệu markdown tổng hợp. Toàn bộ mã nguồn nằm trong code/.

---

## 2. Kết quả hiện tại

### 2.1. Đã xác lập được mốc so sánh

| Hạng mục | Kết quả | Cách kiểm chứng |
|---|---|---|
| Baseline TA Minh trên training_set (11.000 câu) | ANLS 96,25 · Evidence-F1 90,89 · Score 95,45 | reference/mentor_solution_extract.txt |
| Trần oracle (trần trích xuất thật của bài toán) | **99,17% (10.909/11.000)** — đo lại 21/09 | code/oracle_ceiling.py + code/check_validity.py |
| Harness đo điểm | anls.py + evidence_f1.py, mỗi file có self-check chạy được | python anls.py, python evidence_f1.py |

Con số trần oracle là kết quả đo được, không phải suy đoán: nếu định vị bằng chứng là bài toán chọn ô rời rạc trên lưới OCR có sẵn, thì tồn tại một quy tắc chọn ô đạt gần như tuyệt đối. Nghĩa là gần như toàn bộ 4,55 điểm còn thiếu của baseline là mất ở khâu chọn ô, không phải ở khâu suy luận.

Trần oracle là điểm tối đa đạt được **khi biết trước ô đúng** — không phải điểm một hệ thống thực tế đạt được. Nó chứng minh bài toán giải được trên lưới OCR, không chứng minh hệ thống không-dùng-mô-hình đạt 99,17 điểm.

### 2.2. Đã định vị được chính xác chỗ baseline mất điểm

Phân rã 95,45 thành các phần theo dạng suy luận:

| Dạng suy luận | Số câu | ANLS | Evidence-F1 | Score | Đóng góp vào số câu sai |
|---|---|---|---|---|---|
| Lookup, Count, Sum, Compare, Cross-page Sum | 6.693 | — | — | 100,00 | 0,0% |
| Visual Bold Lookup | 535 | 96,90 | 74,82 | 93,59 | 6,9% |
| Argmax | 1.898 | 90,02 | 77,52 | 88,14 | 44,9% |
| Argmin | 1.874 | 89,00 | 76,49 | 87,12 | 48,2% |
| Tổng | 11.000 | — | — | — | 100,0% |

Kết luận: 93,1% số câu sai của baseline tập trung ở đúng hai dạng argmax/argmin. Năm dạng còn lại (6.693 câu) đã đạt 100,00 — không còn gì để cải thiện ở đó.

Cột "Đóng góp vào số câu sai" tính theo **điểm bị mất**, không phải theo số câu. Hai cách cho kết quả khác nhau: theo điểm là 44,9 / 48,2 / 6,9%; theo số câu là 43,9 / 47,7 / 8,4%.

### 2.3. Đã mổ được nguyên nhân gốc của phần mất điểm

Từ 3.772 dòng dữ liệu chẩn đoán argmax/argmin của chính repo TA Minh:

- 89,0% (3.357/3.772) chọn đúng hàng logic → tỷ lệ trả lời đúng đạt 100,0%.
- 415 ca (11,0%) chọn lệch hàng logic → tỷ lệ trả lời đúng chỉ còn 2,9% (12/415).
- 403 câu TA Minh trả lời sai — và 403/403 đều là "đúng bảng, sai hàng", không có ca nào sai vì đọc nhầm số.
- 69,8% (220/315) ca thất bại có hàng bị nhầm là hàng đã từng xuất hiện trước đó trong bảng.
- 120/315 ca thất bại có khoảng cách giá trị tương đối giữa hàng đúng và hàng sai nhỏ hơn 0,10 (khoảng cách tuyệt đối < 0,10 chỉ có 3/315).

Bốn con số 439 / 415 / 403 / 315 lồng nhau nhưng khác tiêu chí đếm (439 ⊂ 415 ⊂ 403 ⊂ 315 theo chiều ngược):

| Con số | Tiêu chí đếm | Đếm trên tập |
|---|---|---|
| 439 | solver_logical_row_index ≠ expected_logical_row_index | 3.772 |
| 415 | solver_row ≠ expected_row | 3.772 |
| 403 | is_correct ≠ True | 3.772 |
| 315 | Tập con của cả 415 và 403 — thất bại ngay cả khi đã xét lại hàng thứ hai | 403 |

Kết luận: đây là lỗi chọn ô rời rạc, không phải lỗi đọc chữ hay lỗi suy luận. Cải thiện OCR hay đổi sang mô hình lớn hơn không giải quyết được — phải sửa khâu tái dựng hàng logic.

### 2.4. Hai cái bẫy của dữ liệu đã đo được

- Bẫy dấu phân cách số: 25,3% ô dùng dấu . làm phân cách nghìn (ví dụ 1.850). Nếu hệ thống đọc thành 1.85 thì sai một ký tự nhưng ANLS cho 0 điểm cho cả câu đó.
- Đáp án không tồn tại trong OCR — nhưng chỉ ở đúng hai dạng số học: 14,3% (1.577/11.000) câu có đáp án không tồn tại dạng chuỗi trong văn bản OCR. Con số này không phân bố đều: sum 85,1% (1.540/1.810) và cross_page_sum 80,4% (37/46), còn sáu dạng trích xuất lại (9.144 câu: lookup, argmax, argmin, compare, count, visual_bold_lookup) đạt 0,0% — đáp án luôn tồn tại nguyên văn.

Đây là giới hạn của hệ thống chỉ biết chép, không phải giới hạn của hướng tiếp cận: hai dạng bị ảnh hưởng chính là hai dạng baseline đã đạt 100,00. Với sáu dạng trích xuất (9.144 câu), mọi đáp án đều có nguyên văn trong OCR.

### 2.5. Đã chốt được hướng đi và thiết kế thí nghiệm

Chọn hướng O-C: chẩn đoán baseline → sửa bằng giải pháp nhẹ nhất không dùng mô hình → chỉ khi đã đo xong mới thêm mô hình học sâu.

Thiết kế thí nghiệm triệt tiêu 4 cấu hình:

| Cấu hình | Phương pháp | Vai trò |
|---|---|---|
| A | Baseline TA Minh (95,45) | Mốc nền |
| B | Tái dựng hàng logic + căn chỉnh giá trị, không dùng mô hình | Đo hiệu quả thực tế của hướng heuristics |
| C | B + LayoutLMv3 / LayoutXLM | Đo giá trị gia tăng của spatial embedding |
| D | C + Qwen2.5-VL-3B | Đo giá trị gia tăng của VLM lớn |

Điểm quan trọng về mặt nghiên cứu: Cấu hình B là thứ đo trực tiếp future direction, nên không được gộp nó vào tầng model. Đây là lý do outline đặt câu hỏi theo thứ tự trần không-model là bao nhiêu → mất ở đâu → sửa được bao nhiêu → rồi mới đến mô hình, thay vì hỏi thẳng "kết hợp cơ chế SOTA thế nào".

---

## 3. Khó khăn kỹ thuật

- `visual_bold_lookup` chỉ có 535 câu — nhóm nhỏ nhất trong 8 dạng, nhưng lại chiếm 6,9% số câu sai (vì Evidence-F1 chỉ đạt 74,82). Đầu tư vào đây tốn công mà trần cải thiện thấp hơn argmax/argmin nhiều. Cần cân nhắc thứ tự ưu tiên.
- Ràng buộc về tính hợp lệ của suy luận. Pipeline suy luận chỉ được đọc manifest.jsonl, questions.jsonl, images/, ocr/ — tuyệt đối không được chạm labels.jsonl và cell_annotations.jsonl (hai file này chỉ dùng để đo). Cách tự kiểm đã đặt ra: đổi tên hai file nhãn rồi chạy lại, nếu pipeline vẫn chạy được thì mới hợp lệ.
- 14,3% câu có đáp án không tồn tại dạng chuỗi trong OCR — nhưng 100% số đó tập trung ở `sum` (85,1%) và `cross_page_sum` (80,4%), tức hai dạng mà đáp án phải tính ra chứ không thể chép ra. Sáu dạng trích xuất còn lại (9.144 câu) đạt 0,0% — đáp án luôn có nguyên văn. Đây là giới hạn của hệ thống chỉ biết chép, không phải giới hạn của hướng tiếp cận.
- Chỉ `training_set` có nhãn. public_test và private_test không có labels.jsonl và cell_annotations.jsonl; questions.jsonl trên test cũng không có trường reasoning_type. Nghĩa là intent router buộc phải phân loại dạng câu hỏi từ văn bản câu hỏi, không được dùng nhãn. (Đã kiểm tra bằng mắt: cả hai split test đều có thư mục ocr/, cấu trúc block y hệt train — nên vẫn trích xuất được.)

---

## Hỗ trợ từ TA

- Nhờ TA đánh giá và cho e góp ý cần cải thiện outline project ạ.

---

## 4. Kế hoạch 03 ngày tiếp theo (19/09 → 21/09)

| # | Việc | Kết quả mong đợi |
|---|---|---|
| 1 | Baseline luật thuần Python, không model cho cả 8 dạng — khớp theo ranh giới từ / cả khối, không dùng in trần | Điểm end-to-end thật của Cấu hình B, đo bằng chính anls.py + evidence_f1.py |
| 2 | Đo tỷ lệ IoU ≥ 0,5 thật giữa evidence dự đoán và evidence vàng | Đóng GAP CHUNG #1 (hiện mới đo một nửa, 75,2%) |
| 3 | Ưu tiên argmax/argmin — cần so sánh tinh, không phải OCR tốt hơn | Vượt mốc 88,14 (Argmax) và 87,12 (Argmin) |
| 4 | Ưu tiên `visual_bold_lookup` — lấy row/column từ ocr/*.json, suy is_bold bằng cv2.distanceTransform | Đẩy Evidence-F1 của nhóm này lên trên 74,82 |
| 5 | Intent router không nhãn — phân loại 8 dạng từ văn bản câu hỏi, bỏ hẳn labels.jsonl["reasoning_type"] | Ma trận nhầm lẫn đo trên train, chốt trước khi chạy test |
| 6 | Dựng lại lưới bảng từ ocr/*.json + ảnh trang | Bảng tái dựng đối chiếu được với cell_annotations.jsonl trên train |
| 7 | Đo end-to-end trên `training_set` + đo trần trích xuất | Bảng kết quả Cấu hình B so với Cấu hình A |
| 8 | Kiểm tra tính hợp lệ: đổi tên labels.jsonl + cell_annotations.jsonl rồi chạy lại | Pipeline vẫn chạy được (chứng minh không rò nhãn) |

Điểm dừng giữa tuần 2: nếu bộ chọn ô không chạy được, tôi sẽ hỏi TA trước khi đổi hướng — theo §II.3, mọi thay đổi output hoặc chiến lược đã thống nhất trong outline đều phải trao đổi với TA trước.

Output dự kiến cuối tuần 2: WEEK02 - Experiment Results trong Working Files.

---

## 5. ĐÍNH CHÍNH (22/09/2026)

Hai con số trong bản nộp ngày 18/09 đã được đo lại và sửa. Không có kết luận nào thay đổi; cả hai đều là lỗi ở khâu trích xuất số liệu, không phải ở khâu phân tích.

| Chỗ | Bản nộp 18/09 | Đã sửa | Vì sao sai |
|---|---|---|---|
| Mục 2.1 — trần của bài toán | "Trần trích xuất thật: 100,00% (11.000/11.000)" | **99,17% (10.909/11.000)**, gọi đúng tên là **trần oracle** | Harness cũ (`audit_ceiling.py`) lấy `is_bold` từ `cell_annotations.jsonl` — file NHÃN. Đo lại không dùng nhãn (`oracle_ceiling.py`, lưới tái dựng thuần hình học từ `ocr/*.json` + ảnh trang) thì phần thiếu 0,83% nằm trọn ở `visual_bold_lookup` (82,99%): `is_bold` là trường duy nhất không có tương ứng trong OCR, đúng như đề bài ghi "OCR không ghi nhận định dạng chữ" |
| Mục 2.2 — kết luận | "**Sáu** dạng còn lại (6.693 câu) đã đạt 100,00" | **Năm** dạng (6.693 câu) | Con số 6.693 câu là đúng, nhưng nhóm đó chỉ gồm 5 dạng: lookup, count, sum, compare, cross_page_sum. Dạng thứ sáu còn lại `visual_bold_lookup` chỉ đạt 93,59 — đã bị đếm nhầm vào nhóm 100,00 |

Bổ sung theo góp ý của TA (19/09): mục 2.1 nay nói rõ trần oracle là điểm tối đa **khi biết trước ô đúng**, không phải điểm hệ thống thực tế đạt được; mục 2.2 ghi rõ cột "Đóng góp vào số câu sai" tính theo **điểm bị mất**; mục 2.3 thêm bảng định nghĩa bốn con số 439 / 415 / 403 / 315.
