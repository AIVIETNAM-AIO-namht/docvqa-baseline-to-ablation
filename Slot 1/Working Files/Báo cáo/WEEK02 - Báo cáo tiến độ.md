# BÁO CÁO TIẾN ĐỘ ĐỊNH KỲ — TUẦN 2

Chủ đề: Hỏi đáp trên ảnh tài liệu (Document VQA) — OLP AI PTIT 2026, Vòng loại
Người thực hiện: Huỳnh Thuyên Nam
Kỳ báo cáo: **Tuần 2 (WEEK02)** — mốc trong bảng kế hoạch ở Outline mục V

Báo cáo này gộp trọn Tuần 2 thành **một bản duy nhất**: đầu tuần kiểm chứng phản hồi TA và sửa giao thức đánh giá, cuối tuần chạy Cấu hình B end-to-end. Mốc đã hứa cho Tuần 2 trong Outline: *"Vượt mốc 88.14 (Argmax) và 87.12 (Argmin) của TA Minh trên training_set."* — **đã đạt, xem mục 3.1.**

Báo cáo thí nghiệm đầy đủ theo §II.5 của hướng dẫn Topic Team nằm ở `WEEK02 - Experiment Results` — đây chính là sản phẩm đã hứa từ Tuần 1, nay hoàn thành.

---

## Tóm tắt nhanh (bốn mục theo form cập nhật)

- **Công việc đã thực hiện:** kiểm chứng 3 góp ý TA 19/09 bằng số liệu gốc; truy gốc bốn con số lỗi; chốt giao thức chống overfit 880 dev / 220 eval theo tài liệu; viết lại harness trần oracle để không đọc file nhãn; chạy Cấu hình B end-to-end và truy/sửa 3 lỗi trong khâu sinh evidence.
- **Kết quả hiện tại:** Cấu hình B (luật thuần Python, **không dùng mô hình**) đạt **0,968** (all) · 0,967 (dev) · 0,972 (eval) — vượt baseline TA Minh 95,45 trên cả ba split. Mốc Outline Tuần 2 **ĐẠT cả hai**: argmax 88,14 → **93,6** · argmin 87,12 → **92,6**. Chênh dev − eval = 0,005 điểm ⇒ chưa có dấu hiệu overfit theo tài liệu.
- Chi tiết từng mục ở §1–§4 dưới đây. Câu hỏi cho TA không nằm trong báo cáo — xem ghi chú ở mục "Tóm tắt nhanh".

---

## 1. Tổng quan công việc trong tuần

| # | Công việc | Sản phẩm để lại |
|---|---|---|
| 1 | Nhận phản hồi TA, đọc kỹ 3 góp ý; rà lại toàn bộ số liệu đã báo cáo | `feedback_TA/19 SEP 2026.docx.md` |
| 2 | Đo lại từ CSV gốc để kiểm chứng từng góp ý; truy gốc bốn con số lỗi; kiểm tra `public_test` có nhãn hay không | `code/audit_ceiling.py`, `PROGRESS_LOG.md` |
| 3 | Sửa Outline Project theo phản hồi TA; lập file theo dõi tiến độ giữa các tuần | `Outline Project ...docx`, `PROGRESS_LOG.md` |
| 4 | Chốt giao thức đánh giá chống overfit (880 dev / 220 eval theo tài liệu); viết lại harness trần oracle để không đọc file nhãn; đính chính hai con số sai trong báo cáo WEEK01 | `code/split_docs.py`, `splits/dev_docs.txt`, `splits/eval_docs.txt`, `code/oracle_ceiling.py`, `code/check_validity.py` |
| 5 | Chạy Cấu hình B end-to-end trên cả ba split; truy và sửa 3 lỗi trong khâu sinh evidence; đo trần oracle đối chiếu | `code/audit_rule_system.py`, `code/grid_ocr.py` |
| 6 | Viết báo cáo kết quả thí nghiệm cuối tuần | `WEEK02 - Experiment Results.docx` |

---

## 2. Kiểm chứng phản hồi TA (đầu tuần)

### 2.1. Cả ba góp ý đều đúng, đã kiểm chứng bằng số

| Góp ý của TA | Kết quả kiểm chứng |
|---|---|
| Rủi ro overfit vào tập train | **Đúng, và nặng hơn dự kiến.** Luật lõi của trần oracle đúng **3.772/3.772 = 100,00%** trên toàn bộ argmax/argmin. Một luật đúng tuyệt đối như vậy khớp *quy ước sinh dữ liệu*, không phải suy ra từ dữ liệu |
| Ba con số 415/403/315 gần nhau, cần định nghĩa | **Đúng.** Truy được gốc và quan hệ lồng nhau: 315 ⊂ 403 ⊂ 415 ⊂ 439 (mục 2.2) |
| Cần góc nhìn khái quát cho báo cáo Topic Team | **Đúng.** Đã bổ sung Mục VIII của Outline, gắn từng phát hiện với phần gap tổng hợp từ 10 paper |

### 2.2. Truy gốc bốn con số lỗi

| Con số | Tiêu chí đếm | Đếm trên |
|---|---|---|
| 439 | `solver_logical_row_index ≠ expected_logical_row_index` | 3.772 |
| 415 | `solver_row ≠ expected_row` | 3.772 |
| 403 | `is_correct ≠ True` | 3.772 |
| 315 | Tập con của cả 415 và 403 | 403 |

Quan hệ: 315 ⊂ 403 ⊂ 415 ⊂ 439. Hiệu giữa các mức: 439 − 415 = 24 ca lệch chỉ số hàng logic nhưng vẫn trỏ đúng hàng vật lý; 415 − 403 = 12 ca lệch hàng nhưng vẫn trả lời đúng; 403 − 315 = 88 ca trả lời sai nhưng không do nhầm hàng trùng giá trị.

Đồng thời làm rõ: cột "Đóng góp vào số câu sai" trong báo cáo WEEK01 tính theo **điểm bị mất**, không phải theo số câu. Hai cách cho kết quả khác nhau — theo điểm là 44,9 / 48,2 / 6,9%; theo số câu là 43,9 / 47,7 / 8,4%. Báo cáo chọn cách theo điểm vì thước đo cuộc thi là điểm số, và đã ghi kèm con số theo số câu để đối chiếu.

### 2.3. Sửa một lỗi số liệu trong báo cáo WEEK01

Báo cáo WEEK01 viết "sáu dạng còn lại (6.693 câu) đạt 100,00". Kiểm lại: chỉ **năm** dạng đạt 100,00 (lookup, count, sum, compare, cross_page_sum = 6.693 câu); dạng thứ sáu còn lại là `visual_bold_lookup` chỉ đạt 93,59. Đây đúng là loại lỗi con số mà TA đang yêu cầu làm rõ, nên ghi lại ở đây thay vì sửa lặng lẽ vào bản đã nộp.

### 2.4. Chốt giao thức đánh giá chống overfit

Đã kiểm tra tính khả thi và chốt trước khi chạy thí nghiệm:

- Chia `training_set` theo **tài liệu**, không chia theo câu hỏi: **880 tài liệu để phát triển luật / 220 tài liệu giữ riêng để đánh giá**. Chia được ngay vì dữ liệu có 1.100 tài liệu × đúng 10 câu/tài liệu = 11.000 câu, không tài liệu nào lệch.
- Chỉ nhìn phần giữ riêng sau khi đã chốt luật. Mỗi cấu hình B/C/D báo cáo kèm **hai** số (dev và eval); chênh lệch dev − eval là thước đo trực tiếp mức overfit.
- `public_test` (1.000 câu) chỉ có `document_id` / `question` / `question_id`, **không có nhãn** — xác nhận đúng như TA nói: chỉ dùng làm kiểm tra cuối, không dùng để tinh chỉnh.

### 2.5. Outline Project đã cập nhật

| Mục | Nội dung bổ sung |
|---|---|
| II | Viết phần diễn giải bảng ánh xạ paper → bài toán con (trước đó chỉ có tiêu đề và bảng) |
| III.4 *(mới)* | Định nghĩa bốn con số thống kê lỗi + làm rõ cột "Đóng góp" tính theo điểm + gọi đúng tên **trần oracle** |
| V | Nguyên tắc đánh giá chống overfit (880/220, vai trò của public_test, báo cáo kèm dev − eval) |
| VII *(mới)* | Hạn chế và rủi ro: overfit, dấu vân tay dữ liệu sinh theo mẫu, trần oracle chưa đo độc lập với nhãn, giới hạn của tập kiểm tra |
| VIII *(mới)* | Đóng góp dự kiến cho báo cáo Topic Team — câu hỏi nghiên cứu khái quát gắn với gap G1–G6 |
| VI → IX | Đánh số lại mục tài liệu tham khảo |

### 2.6. Phát hiện mới: harness đo trần oracle phụ thuộc file nhãn

Đây là việc phát sinh khi rà lại tính hợp lệ của chính công cụ đo, và nó ảnh hưởng trực tiếp tới con số "trần oracle 100,00%" đã báo cáo:

- `code/audit_ceiling.py` tra text của ô theo bbox bằng cách đọc **`cell_annotations.jsonl`** — đây là file **nhãn**.
- Điều này vi phạm ràng buộc hợp lệ của chính dự án (pipeline suy luận không được chạm `labels.jsonl` và `cell_annotations.jsonl`), và file này **không tồn tại** trên `public_test` / `private_test`.
- Hệ quả: trần oracle hiện đo được là trần *có biết trước ô đúng*, đo trên train, có dùng nhãn — chưa phải một phép đo hợp lệ và chưa chạy được trên tập đích.

**Đã sửa xong — và trần oracle thật thấp hơn con số đã báo cáo.** `code/oracle_ceiling.py` không đọc `cell_annotations.jsonl`; lưới dựng thuần hình học: gom block theo `y0`, sắp theo `x0`. `code/verify_grid.py` đối chiếu với lưới vàng được **0 hàng trộn 2 bảng, 0 hàng sai thứ tự cột / 256.040 ô, 30.662 hàng** ⇒ `(table, row, column)` không cần file nhãn. Phép kiểm hợp lệ tự động (`code/check_validity.py`, đổi tên file nhãn rồi chạy lại) **đạt**.

| Dạng | Bản cũ (đọc `is_bold` từ nhãn) | Bản đo từ ảnh |
|---|---:|---:|
| 7 dạng còn lại | 100,00% | 100,00% — không đổi |
| `visual_bold_lookup` | 100,00% | **82,99%** |
| Khớp tuyệt đối toàn tập | 100,00% | **99,17%** (10.909/11.000) |
| **Điểm cuộc thi** (`0,85·ANLS + 0,15·F1`) | **100,00** | **99,30** |

Nguyên nhân: `is_bold` là trường **duy nhất** không có tương ứng trong OCR — chính đề bài nói "OCR không ghi nhận định dạng chữ". Đo độ dày nét từ ảnh chỉ đạt 82,99%; đã thử 5 phép đo chuẩn hoá khác (`code/probe_bold2.py`), phép tốt nhất `core/ink` cũng đúng **82,99%** ⇒ đây là **trần của tín hiệu ảnh**, không phải cài đặt tồi.

Đã loại một tín hiệu giả: hàng in đậm luôn đứng đầu danh sách evidence (535/535 câu). Nhưng khi tín hiệu này lệch với tín hiệu ảnh (88/535 ca) thì **ảnh đúng 0/88, thứ tự đúng 88/88** ⇒ đó là quy ước sinh dữ liệu; dùng nó là học thuộc mẫu, không phải suy luận.

Chênh dev − eval của trần oracle là 0,07 điểm % (99,16% so với 99,23%) ⇒ lưới và luật solver không phụ thuộc tài liệu nào.

---

## 3. Kết quả Cấu hình B — end-to-end thật (cuối tuần)

Cấu hình B: chọn ô bằng luật thuần Python, **không dùng mô hình**. Lưới bảng tái dựng từ `ocr/*.json` + ảnh trang; `is_bold` đo từ ảnh. Điểm đo bằng chính `anls.py` + `evidence_f1.py`.

### 3.1. Mốc Outline Tuần 2 — ĐẠT cả hai chỉ tiêu

| Chỉ tiêu Outline | Mốc | Kết quả Cấu hình B | Trạng thái |
|---|---:|---:|---|
| Argmax vượt baseline TA Minh | 88,14 | **93,6** | ĐẠT (+5,5) |
| Argmin vượt baseline TA Minh | 87,12 | **92,6** | ĐẠT (+5,5) |

### 3.2. Tổng hợp ba split

| Split | Tài liệu | Câu | ANLS | Evidence-F1 | **Điểm** | So baseline 95,45 |
|---|---:|---:|---:|---:|---:|---:|
| dev (nơi chốt luật) | 880 | 8.800 | 0,971 | 0,943 | **0,967** | +0,012 |
| eval (giữ riêng) | 220 | 2.200 | 0,976 | 0,949 | **0,972** | +0,017 |
| all | 1.100 | 11.000 | 0,972 | 0,945 | **0,968** | +0,013 |
| Baseline TA Minh (tham chiếu) | 1.100 | 11.000 | 0,963 | 0,909 | 0,955 | — |

Chênh lệch **dev − eval = 0,005 điểm**. Luật chốt trên dev không suy giảm khi đo trên 220 tài liệu chưa từng nhìn ⇒ chưa có dấu hiệu overfit theo tài liệu. Đây là con số trả lời trực tiếp góp ý số 1 của TA.

**Tầng không dùng mô hình đã vượt baseline có model**, và thắng trên cả ba split. Nghĩa là phần lớn khoảng cách 4,55 điểm của baseline không đến từ thiếu mô hình, mà từ khâu tái dựng hàng logic.

### 3.3. Phân rã theo 8 dạng suy luận (split all, 11.000 câu)

| Dạng | Số câu | ANLS | Evidence-F1 | Điểm |
|---|---:|---:|---:|---:|
| lookup | 2.200 | 1,000 | 1,000 | **1,000** |
| sum | 1.810 | 1,000 | 1,000 | **1,000** |
| count | 915 | 1,000 | 1,000 | **1,000** |
| compare | 1.722 | 1,000 | 1,000 | **1,000** |
| cross_page_sum | 46 | 1,000 | 0,757 | 0,964 |
| argmax | 1.898 | 0,946 | 0,878 | 0,936 |
| argmin | 1.874 | 0,936 | 0,867 | 0,926 |
| visual_bold_lookup | 535 | 0,839 | 0,783 | 0,831 |
| **Toàn bộ** | **11.000** | **0,972** | **0,945** | **0,968** |

Mức tăng ở `argmax`/`argmin` nằm gần trọn ở Evidence-F1 (77,52 → 87,8 và 76,49 → 86,7), tức đúng chỗ đã chẩn đoán ở WEEK01: lỗi ở khâu **chọn hàng**, không phải khâu đọc số.

### 3.4. Đối chiếu trần oracle

| Split | Khớp tuyệt đối | Trần oracle | Điểm trần | Cấu hình B | Khoảng cách còn lại |
|---|---:|---:|---:|---:|---:|
| dev | 8.726/8.800 | 99,16% | 99,29 | 0,967 | 2,6 điểm |
| eval | 2.183/2.200 | 99,23% | 99,34 | 0,972 | 2,1 điểm |
| all | 10.909/11.000 | 99,17% | 99,30 | 0,968 | 2,5 điểm |

Toàn bộ khoảng cách 2,5 điểm nằm ở `argmax`, `argmin` và `visual_bold_lookup` — đây là dư địa còn lại của hướng không-model, và cũng là cơ sở để Cấu hình C/D **chỉ cần chạy trên ba dạng này** thay vì toàn bộ 11.000 câu.

### 3.5. Ba lỗi đã truy ra và sửa

Ba lỗi này đưa Cấu hình B từ 0,959 lên 0,968:

| Lỗi | Nguyên nhân thật | Sau khi sửa |
|---|---|---|
| `compare` Evidence-F1 0,730 | Ô không lọc theo hàng sống sót (3.387 ô của hàng không vàng lọt vào) + mỗi ô `(hàng, cột)` bị phát hai lần. Ngưỡng IoU **đã bị loại trừ bằng đo**: 0 ô nằm trong khoảng 0,45–0,55, quét 8 ngưỡng đều cho F1 = 1,0000 | EvF1 **0,730 → 1,000** |
| 23 câu `count` không trả lời được | Copula ` là` chưa được cắt khỏi tên cột ở **cuối chuỗi**; lỗi chỉ lộ khi bảng có hai header lồng nhau (`Ghi chú` vs `Ghi chú bổ sung`) | `count` **0,975 → 1,000** |
| Ô trùng lặp trong danh sách evidence | Phát hiện thêm khi truy `compare`; `evidence_f1` tính `matched / len(pred)` theo danh sách nên phạt precision oan | `len(pred)` 9,454 → 5,223 = đúng `len(gold)` |

### 3.6. Kiểm tra tính hợp lệ của suy luận

Khâu **suy luận** (`code/grid_ocr.py` — dựng lưới, đo `is_bold`, tra ô) chỉ đọc `ocr/*.json` + `images/` + `questions.jsonl`, **không chạm** `cell_annotations.jsonl`.

Phép kiểm tự động đã chạy lại trong tuần này:

```
python code/check_validity.py code/audit_rule_system.py --hide cell_annotations.jsonl
→ HỢP LỆ: code/audit_rule_system.py chạy được mà không cần cell_annotations.jsonl
```

Kết quả giống hệt khi có file nhãn (0,968) ⇒ lưới và `is_bold` thật sự tái dựng từ OCR + ảnh, không mượn `cell_annotations.jsonl`.

`labels.jsonl` (đáp án + ô vàng) chỉ được đọc ở bước **chấm điểm**, sau khi đã có dự đoán — đúng vai trò file nhãn, và không thể ẩn đi khi chạy `audit_rule_system.py` vì đó chính là script tính điểm. **Con số cần bảo vệ là "suy luận không đọc nhãn", không phải "script chấm điểm không đọc nhãn".**

---

## 4. Kế hoạch tuần tới

| # | Việc | Kết quả mong đợi |
|---|---|---|
| 1 | Triển khai Cấu hình C — LayoutLMv3 / LayoutXLM, chỉ trên `argmax` / `argmin` | Điểm C trên dev và eval, chênh dev − eval |
| 2 | Triển khai Cấu hình D — Qwen2.5-VL, ưu tiên `visual_bold_lookup` | Điểm D trên dev và eval |
| 3 | Ablation A/B/C/D đầy đủ | Bảng kết quả ablation — bổ sung cột kết quả vào Outline mục IV |

Output dự kiến cuối tuần tới: `WEEK03 - Ablation Study` trong Working Files, kèm bảng ablation đã điền số.

Điểm dừng giữa tuần: nếu Cấu hình C không vượt được Cấu hình B trên `argmax`/`argmin` sau khi đã căn chỉnh, tôi sẽ báo TA trước khi chuyển sang Cấu hình D — vì kết quả âm ở đây cũng là một kết luận có giá trị cho báo cáo Topic Team.
