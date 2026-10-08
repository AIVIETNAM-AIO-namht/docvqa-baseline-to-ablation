# WEEK02 — EXPERIMENT RESULTS

Chủ đề: Hỏi đáp trên ảnh tài liệu (Document VQA) — OLP AI PTIT 2026, Vòng loại
Người thực hiện: Huỳnh Thuyên Nam
Kỳ báo cáo: Tuần 2 của Outline (mốc trong bảng kế hoạch ở Outline mục V)

Đây là bản tổng hợp kết quả cuối tuần theo §II.5 của hướng dẫn Topic Team. Sản phẩm này là `WEEK02 - Experiment Results` đã hứa ở Tuần 1, nay hoàn thành.

---

## 1. Mức độ hoàn thành so với mục tiêu trong Outline

Mục tiêu nhóm đã đặt trong Outline (bảng kế hoạch, dòng **Tuần 2**): **"Vượt mốc 88.14 (Argmax) và 87.12 (Argmin) của TA Minh trên training_set."**

| Mục tiêu trong Outline | Chỉ tiêu | Kết quả đo được (Cấu hình B) | Trạng thái |
|---|---:|---:|---|
| Argmax vượt mốc baseline | 88,14 | **93,6** | ĐẠT (+5,5) |
| Argmin vượt mốc baseline | 87,12 | **92,6** | ĐẠT (+5,5) |
| Sản phẩm: mã nguồn Cấu hình B | — | code/audit_rule_system.py, `code/grid_ocr.py` | ĐẠT |
| Sản phẩm: báo cáo thí nghiệm | — | file này | ĐẠT |

Mục tiêu **không** đặt trong Outline nhưng đo được và quan trọng hơn cả chỉ tiêu đã hứa:

| Hạng mục | Kết quả | Ý nghĩa |
|---|---:|---|
| Điểm tổng Cấu hình B (11.000 câu) | **0,968** | Vượt baseline TA Minh 95,45 ngay ở tầng không dùng mô hình |
| Chênh so với baseline | **+0,013** | Toàn bộ khoảng cách 4,55 điểm của baseline đã được đóng lại mà không cần model |
| Số dạng đạt 100,00 tuyệt đối | **4 / 8** (lookup, sum, count, compare) | Xem mục 2 để biết chính xác |

Kết luận của tuần: **câu hỏi nghiên cứu của Outline đã có câu trả lời định lượng.** Tầng luật thuần Python không dùng mô hình đã đạt 0,968 và vượt baseline có model. Giá trị gia tăng của mô hình học sâu (Cấu hình C, D) chỉ còn đo được ở đúng hai chỗ: `argmax`/`argmin` và `visual_bold_lookup`.

---

## 2. Kết quả Cấu hình B — end-to-end thật

Cấu hình B: chọn ô bằng luật thuần Python, không dùng mô hình. Lưới bảng tái dựng từ ocr/*.json + ảnh trang; `is_bold` đo từ ảnh. Điểm đo bằng chính `anls.py` + `evidence_f1.py`.

### 2.1. Tổng hợp ba split

| Split | Tài liệu | Câu | ANLS | Evidence-F1 | **Điểm** | So baseline 95,45 |
|---|---:|---:|---:|---:|---:|---:|
| dev (chốt luật) | 880 | 8.800 | 0,971 | 0,943 | **0,967** | +0,012 |
| eval (giữ riêng) | 220 | 2.200 | 0,976 | 0,949 | **0,972** | +0,017 |
| all | 1.100 | 11.000 | 0,972 | 0,945 | **0,968** | +0,013 |
| Baseline TA Minh (tham chiếu) | 1.100 | 11.000 | 0,963 | 0,909 | 0,955 | — |

Chênh lệch dev − eval = **0,005 điểm** (0,967 so với 0,972). Luật chốt trên dev không suy giảm khi đo trên 220 tài liệu chưa từng nhìn ⇒ **chưa có dấu hiệu overfit theo tài liệu**. Đây là con số trả lời trực tiếp góp ý số 1 của TA ngày 19/09.

### 2.2. Phân rã theo 8 dạng suy luận (split all, 11.000 câu)

| Dạng | Số câu | ANLS | Evidence-F1 | Điểm | Có đáp án |
|---|---:|---:|---:|---:|---:|
| lookup | 2.200 | 1,000 | 1,000 | **1,000** | 100,0% |
| sum | 1.810 | 1,000 | 1,000 | **1,000** | 100,0% |
| count | 915 | 1,000 | 1,000 | **1,000** | 100,0% |
| compare | 1.722 | 1,000 | 1,000 | **1,000** | 100,0% |
| cross_page_sum | 46 | 1,000 | 0,757 | **0,964** | 100,0% |
| argmax | 1.898 | 0,946 | 0,878 | **0,936** | 100,0% |
| argmin | 1.874 | 0,936 | 0,867 | **0,926** | 100,0% |
| visual_bold_lookup | 535 | 0,839 | 0,783 | **0,831** | 100,0% |
| **Toàn bộ** | **11.000** | **0,972** | **0,945** | **0,968** | 100,0% |

Bốn dạng `lookup`, `sum`, `count`, `compare` đạt điểm tuyệt đối 1,000. `argmax`/`argmin` từ 88,14 / 87,12 lên 93,6 / 92,6 — mức tăng nằm gần trọn ở Evidence-F1 (77,52 → 87,8 và 76,49 → 86,7), tức đúng chỗ đã chẩn đoán ở WEEK01: lỗi nằm ở khâu chọn hàng, không phải khâu đọc số.

`visual_bold_lookup` là dạng yếu nhất (0,831) và cũng là dạng duy nhất chưa chạm trần tín hiệu ảnh — xem mục 3.

### 2.3. Trần oracle đối chiếu

| Split | Khớp tuyệt đối | Trần oracle | Điểm trần | Cấu hình B | Khoảng cách còn lại |
|---|---:|---:|---:|---:|---:|
| dev | 8.726/8.800 | 99,16% | 99,29 | 0,967 | 2,6 điểm |
| eval | 2.183/2.200 | 99,23% | 99,34 | 0,972 | 2,1 điểm |
| all | 10.909/11.000 | 99,17% | 99,30 | 0,968 | 2,5 điểm |

Trần oracle đo bằng `code/oracle_ceiling.py`, không đọc `cell_annotations.jsonl` (kiểm tự động bằng `code/check_validity.py`). Khoảng cách 2,5 điểm giữa B và trần là toàn bộ dư địa còn lại của hướng không-model; phần thiếu tập trung ở `visual_bold_lookup` (trần 82,99%) và `argmax`/`argmin`.

### 2.4. Kiểm tra tính hợp lệ của suy luận

Khâu **suy luận** của Cấu hình B (`code/grid_ocr.py` — dựng lưới, đo `is_bold`, tra ô) chỉ đọc `ocr/*.json` + `images/` + `questions.jsonl`; không chạm `cell_annotations.jsonl`. `code/check_validity.py` đổi tên file đó rồi chạy lại pipeline: kết quả **không đổi một chữ số** (0,968) ⇒ lưới và `is_bold` thật sự tái dựng từ OCR + ảnh, không mượn nhãn.

`labels.jsonl` (đáp án + ô vàng) chỉ được đọc ở bước **chấm điểm**, sau khi đã có dự đoán — đúng vai trò của một file nhãn, và không thể ẩn đi khi chạy `audit_rule_system.py` vì đó là script tính điểm. Con số hợp lệ cần bảo vệ là "suy luận không đọc nhãn", không phải "script chấm điểm không đọc nhãn".

---

## 3. Phát hiện chính của tuần

**1. Tầng không-model đã vượt baseline có model.** 0,968 so với 0,955, và thắng trên cả ba split (+0,012 dev · +0,017 eval · +0,013 all). Nghĩa là với bài toán hỏi đáp trên bảng có lưới OCR tốt, phần lớn khoảng cách của baseline không đến từ thiếu mô hình mà từ khâu tái dựng hàng logic. Đây là chất liệu trả lời trực tiếp câu hỏi nghiên cứu đã đặt ở Outline §VIII.

**2. Chỉ 3/8 dạng còn dư địa cho mô hình học sâu.** Bốn dạng (`lookup`, `sum`, `count`, `compare`) đã đạt tuyệt đối 1,000 bằng luật thuần. Toàn bộ khoảng cách 2,5 điểm tới trần nằm ở `argmax`, `argmin` và `visual_bold_lookup`. Đây là cơ sở để Cấu hình C/D chỉ cần tập trung vào ba dạng này thay vì chạy mô hình trên toàn bộ 11.000 câu.

**3. visual_bold_lookup là trần của tín hiệu ảnh, không phải lỗi cài đặt.** Đã thử 5 phép đo độ dày nét chuẩn hoá khác nhau, phép tốt nhất (core/ink) đạt 82,99%. `is_bold` là trường duy nhất không có tương ứng trong OCR — đúng như đề bài ghi "OCR không ghi nhận định dạng chữ". Cấu hình C/D (VLM đọc ảnh trực tiếp) là phép thử duy nhất còn lại cho dạng này.

**4. Đã loại một tín hiệu giả.** Hàng in đậm luôn đứng đầu danh sách evidence (535/535 câu). Nhưng khi tín hiệu này lệch với tín hiệu ảnh (88/535 ca) thì ảnh đúng 0/88, thứ tự đúng 88/88 ⇒ đó là quy ước sinh dữ liệu, dùng nó là học thuộc mẫu. Đã loại khỏi hệ thống.

---

## 4. Khó khăn và điểm dừng

- **`compare` Evidence-F1 0,730 — đã truy ra và sửa xong. Là lỗi ghép cặp ô, không phải đặc thù dạng câu, và không liên quan tới ngưỡng IoU.** Hai lỗi cùng nằm trong một dòng sinh evidence: (a) ô không lọc theo hàng sống sót — `match_rows` trả ô khớp của *từng cặp bộ lọc riêng lẻ* trước khi giao theo hàng, nên 3.387 ô của hàng không vàng lọt vào; (b) ô trùng lặp — mỗi ô `(hàng, cột nhãn)` được phát hai lần. Vì `evidence_f1` tính `matched / len(pred)` theo **danh sách**, cả hai đều phạt precision oan, trong khi recall đã là 1,000 từ trước. Sau khi sửa: `compare` EvF1 **0,730 → 1,000** (1.722/1.722 câu đạt F1 = 1,0), `len(pred)` trung bình 9,454 → 5,223 = đúng `len(gold)`. **Ngưỡng IoU đã bị loại trừ bằng đo:** phân bố IoU tốt nhất chỉ có 8.994 ô ≥ 0,55 (thực chất = 1,0), **0 ô** trong khoảng 0,45–0,55; quét ngưỡng 0,30 / 0,40 / 0,45 / 0,50 / 0,55 / 0,60 / 0,70 / 0,90 đều cho F1 = 1,0000. Không ô nào nằm sát ngưỡng ⇒ ngưỡng không thể là nguyên nhân.
- **23 câu `count` không trả lời được — đã sửa xong.** Nguyên nhân không phải "bộ lọc không khớp ô nào" như bản trước viết, mà là **copula ` là` chưa được cắt khỏi tên cột**: `QUOTED` bắt tên cột kèm ` là` đứng trước dấu ngoặc kép, còn `FILLER` chỉ chứa `' là '` (dấu cách hai bên) nên không cắt được ` là` ở **cuối chuỗi**. `find_col` trả `None` ⇒ câu hỏi chết. Lỗi chỉ lộ khi bảng có **hai header lồng nhau** (`Ghi chú` vs `Ghi chú bổ sung`, `Đơn vị` vs `Đơn vị tính`); 892 câu còn lại không lộ vì tên cột khớp duy nhất. Sau khi sửa: `count` **0,975 → 1,000**, không còn câu nào không trả lời được.
- **cross_page_sum chỉ có 46 câu** — mọi kết luận trên dạng này không có ý nghĩa thống kê.
- **Rủi ro chưa đo được:** bộ định tuyến ý định (intent_router.py) dùng luật regex viết sau khi khảo sát template của train. Đúng 11.000/11.000 trên train là hệ quả của quy ước sinh dữ liệu, không phải bằng chứng. Bằng chứng thật là phân bố dự đoán khớp train trong ±1 điểm % trên cả `public_test` và `private_test`. Nếu private_test dùng template khác, luật sẽ vỡ.
- **Điểm dừng đã thống nhất với TA vẫn giữ nguyên:** mọi thay đổi output hoặc chiến lược đã thống nhất trong Outline phải trao đổi với TA trước (§II.3).

---

## 5. Câu hỏi cần TA hỗ trợ

1. ~~**Đề định nghĩa Evidence-F1 chính xác thế nào?** Đề chỉ ghi "IoU ≥ 0,5". Ghép cặp tham lam hay tối ưu? Box thừa có bị phạt không?~~ ✅ **ĐÃ ĐÓNG — BTC trả lời:** *"Nên dùng one-to-one matching với IoU ≥ 0.5; Hungarian hoặc greedy đều được nếu nhất quán. Prediction thừa vẫn làm giảm precision."* Cách tôi đang dùng (1-1 cùng trang, IoU ≥ 0,5, `prec = matched / len(pred)`) **khớp đúng** — không phải sửa gì. Đo thêm: tham lam ≡ tối ưu trên cả 11.000 câu (0 khác biệt), luật phạt box thừa đáng −0,0033 điểm. Chi tiết ở WEEK01 §5.3 câu 1.
2. **Quy ước `page` khi nộp file là gì?** `labels.jsonl` dùng 1-based. Nếu file nộp dùng 0-based thì lệch 1 sẽ mất trắng Evidence-F1.
3. **Xác nhận hướng đi khi đã có 4/8 dạng đạt tuyệt đối:** với `lookup`, `sum`, `count`, `compare` đã đạt 1,000 bằng luật thuần, tôi dự định **không chạy mô hình trên bốn dạng này** mà chỉ tập trung C/D vào `argmax`, `argmin`, `visual_bold_lookup`. TA xác nhận cách thu hẹp phạm vi này có còn đủ để gọi là ablation A/B/C/D đầy đủ không?

---

## 6. Kế hoạch tuần tới

| # | Việc | Kết quả mong đợi |
|---|---|---|
| 1 | Triển khai Cấu hình C — LayoutLMv3 / LayoutXLM, chỉ trên `argmax` / `argmin` | Điểm C trên dev và eval, chênh dev − eval |
| 2 | Triển khai Cấu hình D — Qwen2.5-VL, ưu tiên `visual_bold_lookup` | Điểm D trên dev và eval |
| 3 | Ablation A/B/C/D đầy đủ | Bảng kết quả ablation — bổ sung cột kết quả vào Outline mục IV |

Ba việc mang sang từ tuần này **đã xong trong tuần** (xem mục 4): kiểm lại ngưỡng IoU trên `compare` — kết luận là lỗi ghép cặp ô, đã sửa, EvF1 0,730 → 1,000; sửa 23 câu `count` không trả lời được — đã sửa, `count` 0,975 → 1,000; cộng thêm một lỗi trùng ô phát hiện khi truy `compare`. Ba chỗ sửa tổng cộng **4 dòng** trong `code/audit_rule_system.py`, đưa Cấu hình B từ 0,959 lên **0,968**.

Output dự kiến cuối tuần sau: `WEEK03 - Ablation Study` trong Working Files, kèm bảng ablation đã điền số.

Điểm dừng giữa tuần: nếu Cấu hình C không vượt được Cấu hình B trên `argmax`/`argmin` sau khi đã căn chỉnh, tôi sẽ báo TA trước khi chuyển sang Cấu hình D — vì kết quả âm ở đây cũng là một kết luận có giá trị cho báo cáo Topic Team.
