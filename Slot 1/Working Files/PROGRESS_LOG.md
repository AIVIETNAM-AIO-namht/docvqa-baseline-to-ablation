# PROGRESS LOG — Document VQA (OLP AI PTIT 2026)

> Cách dùng: chỉ ghi việc **mới so với lần nộp gần nhất**, không cần chi tiết ngày nào.
> Mỗi tuần: đọc mục **CHƯA NỘP** → viết báo cáo → cắt mục đó sang **ĐÃ NỘP** với tiêu đề `WEEKxx`.
> Ghi 1 dòng/việc: việc gì → để lại sản phẩm gì (đường dẫn). Đủ để dựng lại bảng "Công việc | Sản phẩm".
> Mọi báo cáo (.md nguồn + .docx nộp) nằm trong `Báo cáo/`; export bằng `python code/export_progress_report.py "<tên>.md"`.
>
> `WEEKxx` = **tuần**, khớp thẳng với bảng kế hoạch ở Outline mục V. Một tuần = một báo cáo, dù việc trải trên nhiều ngày.

---

## CHƯA NỘP

### WEEK02 — Báo cáo tiến độ (gộp trọn Tuần 2) — **chờ nộp cuối tuần**

- File: `Báo cáo/WEEK02 - Báo cáo tiến độ.docx` (nguồn md cùng tên; export bằng `code/export_progress_report.py "WEEK02 - Báo cáo tiến độ.md"`) — đã viết xong, **chưa nộp**: cuối tuần mới có kỳ nộp tổng kết Tuần 2.
- Tóm tắt: kiểm chứng 3 góp ý TA bằng số liệu gốc; truy gốc 4 con số lỗi; chốt giao thức đánh giá chống overfit; cập nhật Outline Project; Cấu hình B chạy end-to-end đạt 0,968, vượt baseline 95,45 trên cả ba split.

#### Phản hồi TA — 19/09/2026 (`feedback_TA/19 SEP 2026.docx.md`)

Nhận xét chung: báo cáo tốt. Khen 3 điểm: (1) phân rã lỗi theo dạng câu hỏi, chỉ ra 93,1% mất điểm ở argmax/argmin — kết luận "đúng bảng, sai hàng" dựa trên dữ liệu; (2) kiểm tra tính hợp lệ bằng cách đổi tên file nhãn rồi chạy lại; (3) thiết kế A→B→C→D tách được giá trị gia tăng từng tầng + có điểm dừng trao đổi TA.

Góp ý cần xử lý:

1. **Rủi ro lớn nhất — overfit tập train.** Toàn bộ đánh giá và thiết kế luật đang dựa trên `training_set`, cấu hình B cũng dự kiến đo trên chính tập đó ⇒ điểm sẽ lạc quan hơn thực tế. Yêu cầu:
   - Chia train theo **tài liệu** (không chia theo câu hỏi, vì nhiều câu dùng chung 1 tài liệu): một phần phát triển luật, một phần giữ riêng để đánh giá. Chỉ nhìn phần giữ riêng khi đã chốt luật.
   - Dùng public test làm kiểm tra cuối, không dùng để tinh chỉnh.
   - Sáu dạng đạt đúng 100,00 gợi ý dữ liệu sinh theo mẫu ⇒ luật khớp mẫu train có thể không khớp layout private test. Ghi rủi ro này vào phần hạn chế + kiểm tra luật có phụ thuộc đặc điểm riêng của mẫu không.
2. **Làm rõ các con số.** Ba con số đang gần nhau nhưng khác nhau: 415 ca lệch hàng / 403 câu trả lời sai / 315 ca thất bại ⇒ phải định nghĩa rõ từng con số đếm trên tập nào, tiêu chí gì. Cột "Đóng góp vào số câu sai" phải ghi rõ là theo **số câu** hay theo **điểm bị mất**. Con số "trần 100,00%" phải gọi rõ là **trần oracle** (điểm tối đa khi biết trước ô đúng) — không phải điểm hệ thống thực tế đạt được.
3. **Góc nhìn Topic Team.** Mục tiêu cuộc thi là điểm số, còn báo cáo Topic Team cần kết luận khái quát. Câu hỏi nghiên cứu đã có sẵn chất liệu: *với bài toán hỏi đáp trên bảng có lưới OCR tốt, luật không dùng mô hình đạt được đến đâu, và mô hình học sâu chỉ thực sự cần thiết ở loại lỗi nào?* Khi viết báo cáo cuối, gắn phát hiện với phần gap tổng hợp từ 10 paper — để kết quả không chỉ dừng ở "tăng bao nhiêu điểm".

#### Đã xác minh lại toàn bộ số liệu TA góp ý (21/09)

Cả 3 góp ý đều **đúng**. Đo lại từ CSV gốc:

**Overfit — nặng hơn dự kiến.** 1100 tài liệu × đúng 10 câu/tài liệu = 11.000 (không tài liệu nào lệch). Luật lõi của trần oracle ("nhãn = ô trái nhất không phải số trong hàng") đúng **3.772/3.772 = 100,00%** trên toàn bộ argmax/argmin ⇒ luật khớp **quy ước sinh dữ liệu**, không phải suy ra từ dữ liệu. Chia theo tài liệu khả thi ngay: 1100 → 880 dev / 220 eval. `public_test` (1000 câu) chỉ có `document_id`/`question`/`question_id` — không có nhãn, đúng là chỉ dùng làm kiểm tra cuối.

**Bốn con số — truy được gốc (phát hiện thêm mức 439):**
| Con số | File | Tiêu chí |
|---|---|---|
| 439 | `argextreme_oracle_ranked.csv` (3.772 câu) | `solver_logical_row_index ≠ expected_logical_row_index` |
| 415 | `argextreme_oracle.csv` (3.772 câu) | `solver_row ≠ expected_row` |
| 403 | cùng file | `is_correct ≠ True` — 403/403 cùng bảng, 0 ca khác bảng |
| 315 | `argextreme_rank2_failures.csv` | tập con của **cả** 415 và 403 |

Quan hệ lồng nhau: 315 ⊂ 403 ⊂ 415 ⊂ 439. Hiệu: 439−415 = 24 (lệch chỉ số hàng logic nhưng vẫn đúng hàng vật lý); 415−403 = 12 (lệch hàng nhưng vẫn trả lời đúng); 403−315 = 88. Kiểm lại mục 2.3 WEEK01: 220/315 = 69,8% ✓ · 120/315 = 38,1% theo `extreme_gap_ratio` ✓ · gap tuyệt đối < 0,10 = 3/315 ✓.

**Cột "Đóng góp vào số câu sai" đang tính theo ĐIỂM bị mất, không phải số câu** — hai cách cho kết quả khác nhau:
| | argmax | argmin | vbl |
|---|---|---|---|
| theo điểm (đang dùng) | 44,9% | 48,2% | 6,9% |
| theo số câu sai | 193/440 = 43,9% | 210/440 = 47,7% | ~37/440 = 8,4% |

**Phát hiện thêm — báo cáo WEEK01 có một chỗ sai:** viết "sáu dạng còn lại (6.693 câu) đạt 100,00". Thực tế **năm** dạng đạt 100,00 (lookup, count, sum, compare, cross_page_sum = 6.693); dạng thứ sáu còn lại `visual_bold_lookup` chỉ đạt 93,59. Cùng loại lỗi con số TA đang yêu cầu làm rõ.

**Phát hiện mới — harness đo trần oracle phụ thuộc file nhãn.** `code/audit_ceiling.py` tra text ô theo bbox bằng cách đọc `cell_annotations.jsonl` (file **nhãn**). Vi phạm ràng buộc hợp lệ của dự án, và file này không tồn tại trên `public_test`/`private_test` ⇒ con số "trần oracle 100,00%" hiện chưa đo được hợp lệ trên tập đích. Đường sửa: `ocr/*.json` có dữ liệu mức block (`bbox`, `block_id`, `text`) ⇒ tái dựng lưới từ OCR + ảnh trang, khớp bbox bằng chứng vàng với block OCR gần nhất.

**Đã sửa xong (21/09) — và trần oracle thật THẤP HƠN con số đã báo cáo.**

`code/oracle_ceiling.py` không đọc `cell_annotations.jsonl`. Lưới tái dựng thuần hình học: gom block theo `y0`, sắp theo `x0`. `code/verify_grid.py` đối chiếu với lưới vàng: **0 hàng trộn 2 bảng, 0 hàng sai thứ tự cột / 256.040 ô, 30.662 hàng** ⇒ `(table, row, column)` không cần file nhãn.

| Dạng | Trần oracle (bản cũ, đọc `is_bold` nhãn) | Trần oracle (đo từ ảnh) |
|---|---|---|
| 7 dạng còn lại | 100,00% | 100,00% — không đổi |
| `visual_bold_lookup` | 100,00% | **82,99%** |
| **Tổng** | **100,00%** | **99,17%** (10.909/11.000) |

Nguyên nhân: `is_bold` là trường **duy nhất** không có tương ứng trong OCR — câu hỏi tự nói "OCR không ghi nhận định dạng chữ". Đo độ dày nét từ ảnh (tỉ lệ pixel tối sống sót sau bào mòn 1 vòng, bỏ phiếu theo cột) chỉ đạt 82,99%. Đã thử 5 phép đo chuẩn hoá khác (`code/probe_bold2.py`), phép tốt nhất `core/ink` cũng đúng 82,99% ⇒ đây là **trần của tín hiệu ảnh**, không phải cài đặt tồi.

**Đính chính cùng ngày:** cả ba script đo (`probe_bold.py`, `probe_bold2.py`, `probe_bold_order.py`) đều cứng trang 1 khi cắt ô, nên 409/1.954 ô vàng nằm ở trang 2 bị cắt nhầm chỗ — mọi con số đo trước đó thấp hơn thực tế. Sau khi sửa: (a) 70,84% · (b) 81,12% · (c) 82,43% · (d) 83,55%. Kết luận không đổi, nhưng mức chênh giữa "tín hiệu ảnh" và "cài đặt tồi" nay rõ hơn.

Đã loại một tín hiệu giả: hàng in đậm luôn đứng đầu danh sách evidence (535/535 câu). Nhưng khi tín hiệu này lệch với tín hiệu ảnh (88/535 ca) thì **ảnh đúng 0/88, thứ tự đúng 88/88** ⇒ đó là quy ước sinh dữ liệu, dùng nó là học thuộc mẫu (`code/probe_bold_order.py`).

**Trần oracle theo split (giao thức đã sửa, không đọc `cell_annotations.jsonl`):**

| Split | Tài liệu | Câu | Khớp tuyệt đối | `visual_bold_lookup` |
|---|---|---|---|---|
| dev | 880 | 8.800 | 8.726 = **99,16%** | 370/444 = 83,33% |
| eval | 220 | 2.200 | 2.183 = **99,23%** | 74/91 = 81,32% |
| all | 1.100 | 11.000 | 10.909 = **99,17%** | 444/535 = 82,99% |

Khoảng cách dev−eval = 0,07 điểm % ⇒ lưới tái dựng và luật solver không phụ thuộc tài liệu nào.

**Chỗ so sánh sai đã sửa:** bảng trên đếm *khớp tuyệt đối*, còn mốc baseline TA Minh 95,45 là *điểm cuộc thi* `0,85·ANLS + 0,15·F1`. Hai đại lượng khác nhau, không trừ trực tiếp được. `oracle_ceiling.py` nay in thêm dòng điểm cuộc thi; trần oracle biết trước ô vàng nên F1 = 1,0 luôn.

#### Việc cần làm (rút ra từ phản hồi TA)

- [x] Tách `training_set` theo tài liệu thành 880 dev / 220 eval; chốt luật trên dev, chỉ đo eval sau khi chốt → `code/split_docs.py`, `splits/dev_docs.txt`, `splits/eval_docs.txt` (seed 20260921)
- [x] Viết lại harness trần oracle chỉ dùng `ocr/*.json` + ảnh trang → `code/oracle_ceiling.py`; lưới tái dựng từ hình học khớp vàng **0 lỗi / 256.040 ô** (`code/verify_grid.py`)
- [x] Phép kiểm hợp lệ tự động (đổi tên file nhãn rồi chạy lại) → `code/check_validity.py`
- [x] Thêm bảng định nghĩa các con số lỗi vào báo cáo → Outline §III.4 + WEEK02 §2.2
- [x] Đổi "trần 100,00%" → "trần oracle" ở mọi chỗ đã viết (còn `WEEK01 - Hieu bai toan...md` §2.5c) — bản lý thuyết đã có banner đính chính 21/09; WEEK01 §2.1/§5 đã sửa
- [x] Sửa "sáu dạng đạt 100,00" → "năm dạng" trong chính file WEEK01 → đã nộp lại bản đính chính 22/09
- [x] Ghi rõ cột "Đóng góp vào số câu sai" là theo điểm bị mất → Outline §III.4
- [x] Ghi vào phần hạn chế: luật lõi đúng 100% vì khớp quy ước generator, không phải suy luận → Outline §VII.1
- [x] Nối kết quả với phần gap 10 paper cho báo cáo Topic Team cuối → Outline §VIII

---

#### Số liệu Cấu hình B (tái lập: `python code/audit_rule_system.py --split all|dev|eval`)

| Split | Câu | ANLS | EvF1 | Điểm | vs 95,45 |
|---|---:|---:|---:|---:|---:|
| dev | 8.800 | 0,971 | 0,943 | 0,967 | +0,012 |
| eval | 2.200 | 0,976 | 0,949 | 0,972 | +0,017 |
| all | 11.000 | 0,972 | 0,945 | 0,968 | +0,013 |

Theo dạng (all): lookup 1,000 · sum 1,000 · count 1,000 · compare 1,000 · cross_page_sum 0,964 · argmax 0,936 · argmin 0,926 · visual_bold_lookup 0,831. Evidence dự đoán được 11.000/11.000 = 100%; không còn câu nào không trả lời được.

Chênh dev − eval = 0,005 điểm ⇒ chưa có dấu hiệu overfit theo tài liệu (trả lời góp ý 1 của TA 19/09). Trần oracle: dev 99,29 · eval 99,34 · all 99,30 (91 misses, toàn bộ ở `visual_bold_lookup`).

#### Cấu hình C (Tuần 3) — kết luận âm có bằng chứng, không dựng model

Tái lập: `python code/row_filter_ceiling.py --split dev|eval|all` · `python code/probe_gold_signal.py --split dev|eval`

**Trần của MỌI bộ lọc hàng tĩnh** cho `argmax`/`argmin` (harness `row_filter_ceiling.py`, **biết trước hàng vàng** — đây là phép đo trần, không phải solver):

| Split | Câu | B đúng | Trần | Dư địa nhánh C | Quy ra điểm thi |
|---|---:|---:|---:|---:|---:|
| dev | 3.024 | 2.827 = 93,49% | 2.998 = 99,14% | +171 = +5,65 đ% | +0,0194 |
| eval | 748 | 704 = 94,12% | 740 = 98,93% | +36 = +4,81 đ% | +0,0165 |
| all | 3.772 | 3.531 = 93,61% | 3.738 = 99,10% | +207 = +5,49 đ% | +0,0188 |

Khoảng cách dev − eval: B đúng −0,63 đ%; trần +0,21 đ% ⇒ eval nhỉnh hơn, không có dấu hiệu overfit.

**Công thức trần trong kế hoạch đã SAI và được sửa.** Kế hoạch tính `S ⊆ ⋂ pool_j` — điều kiện đó coi hàng nằm NGOÀI `pool_j` là hàng chặn, trong khi hàng ngoài `pool_j` không bao giờ ảnh hưởng tới câu `j`. Công thức đúng: `blocked[j] = {r ∈ pool_j : khoá(r) tốt hơn khoá(gold_j)}`, tập `T` khả thi ⇔ ∀i,j ∈ T: `gold_i ∉ blocked[j]`. Sửa xong trần **94,11% → 99,14%**. Harness `assert` bất biến "tập câu B đã đúng luôn khả thi ⇒ trần ≥ B đúng" trên từng bảng — không bảng nào vi phạm.

**Trần là cần, chưa đủ — phải có luật suy từ OCR mới triển khai được. Bốn họ luật đã đo, không họ nào chạm trần** (dev, 3.024 câu):

| Họ luật | Kết quả | Kết luận |
|---|---|---|
| Khử trùng văn bản (4 biến thể, `probe_dedup.py`) | 39,0% – 66,7% (baseline 93,5%) | Loại — phản tác dụng: 60,5% hàng vàng *cũng* mang nhãn trùng |
| Hàng in đậm đo từ ảnh (`probe_bold_rule.py`) | 10,4% | Loại |
| Từ khoá hàng tổng (`probe_row_filter.py`) | 27,2% vs 28,5% — không phân biệt | Loại |
| Hình học hàng (thụt lề, khe hở, đường kẻ) | đồng nhất tuyệt đối: cao độ 0,02121 mọi hàng, khe hở 0,00000 | Loại — **đây chính là tín hiệu LayoutLMv3 cần, và nó không tồn tại** |

**Phép đo chốt** (`probe_gold_signal.py` — trong đúng 197 câu B sai ở dev, tín hiệu nào trỏ đúng hàng vàng?): hàng đậm từ ảnh trúng **18/197 = 9,1%**; trong **156/197 = 79,2%** nó đo được nhưng chỉ vào một hàng **thứ ba** (không phải vàng, không phải hàng B chọn) ⇒ nhiều hàng cùng "nổi bật", và nổi bật **không tương quan** với hàng đúng. Tín hiệu văn bản "khối nhãn đầu" trúng 108/197 = 54,8% (eval 32/44 = 72,7%) — cùng họ với luật khử trùng đã bị loại.

**⇒ Không dựng LayoutLMv3/LayoutXLM.** Dư địa 99,14% là **oracle-only**; không luật không-cần-nhãn nào chạm tới. Không một dòng code nào của `audit_rule_system.py` bị sửa — mọi con số Cấu hình B giữ nguyên.

**Điểm dừng đã hứa với TA đã tới và giữ đúng cam kết** (WEEK02 §5): C không vượt B ⇒ **báo TA trước khi chuyển sang D**. Đối số định hướng D — phân rã 3,20 điểm mất của toàn hệ thống: `argmin` 39,4% · `argmax` 34,5% · `visual_bold_lookup` 25,7% · còn lại 0,5%. Vậy `argmax`/`argmin` giữ **73,9%** phần điểm mất nhưng là **oracle-only** (trần 99,10% chỉ đo được khi biết trước hàng vàng; 4 họ luật không-cần-nhãn đã kiểm đều không chạm tới). `visual_bold_lookup` chỉ giữ **25,7%** nhưng trần 82,99% của nó là trần của **một phép đo độ dày nét** — chưa chắc là trần của tín hiệu ảnh. Đó là chỗ duy nhất còn chạm tới được, và là căn cứ dồn Tuần 4 vào D.

#### Cấu hình D — probe khả thi đã chạy, zero-shot kết luận âm (**để dành cho KEEPTRACK WEEK04, không đưa vào báo cáo WEEK03**)

Tái lập: `python code/probe_vlm_bold.py extract` → `run` (Colab) → `score` · `probe_d/probe_d_colab.ipynb`

**Đây KHÔNG phải Cấu hình D — là phép đo khả thi chạy TRƯỚC khi dựng D**, để trả lời câu hỏi mở ở §Cấu hình C (82,99% là trần của tín hiệu, hay chỉ là trần của một phép đo độ dày nét?). Luật quyết định ghi trong script **trước khi chạy**: `D − B ≥ +0,03` → đáng dựng D + QLoRA; `≤ 0` → kết luận âm, dừng.

Thiết lập: 120 câu `visual_bold_lookup` trên dev (seed 20261007); mỗi câu ghép **2 dải hàng** ứng viên thành 1 ảnh, mỗi dải đóng khung + **chữ A/B vẽ thẳng lên ảnh**; Qwen2.5-VL-3B zero-shot trên Colab **T4 15 GB bf16**. Đối chứng là **đúng nhánh BOLD của Cấu hình B**, chỉ thay nguồn chọn hàng.

| Nhánh | ANLS | EvF1 | Điểm | Chọn đúng hàng |
|---|---:|---:|---:|---:|
| B (độ dày nét) | 0,827 | 0,769 | **0,818** | 96/120 |
| D (Qwen2.5-VL zero-shot) | 0,555 | 0,704 | **0,578** | **60/120** |

**Chênh lệch D − B = −0,241 điểm.** VLM không trả lời được A/B: **0/120** — luôn trả lời "A" cho **cả 120 ảnh**; 60/120 **đúng bằng mức đoán bừa**.

**Ba bản trước của phép đo đều vô hiệu và đã bị loại:** bản 1 nhồi mô tả hàng vào prompt → trả lời "A" 119/120; bản 2 khẳng định "dải TRÊN là (A)" bằng chữ trong prompt nhưng ảnh trống → "A" 120/120. Nhãn **vẽ lên ảnh** ở bản này gỡ đúng cái nhiễu đó.

**Thang sanity 4 bậc (10 ảnh/bậc) — chẩn đoán hỏng ở đâu:**

| Bậc | Phép thử | Kết quả | Loại bỏ được gì |
|---|---|---|---|
| `sanity` | 3 prompt, so 4-bit với bf16 | **4/10** cả hai; model **chép đúng chữ cả hai dải** | Không phải lỗi đọc ảnh / lượng tử hoá |
| `sanity2` | V0 gốc · V1 từng bước · V2 bỏ cột nhãn | Cả ba **4/10**; V1 luôn in `ĐÁP ÁN: A` | Không phải lỗi định dạng prompt |
| `sanity3` | **Đảo dải** (nhãn dính theo dải) · **Đổi nhãn** (giữ thứ tự) | ĐẢO DẢI → chữ lật **0/10** · ĐỔI NHÃN → chữ đứng **10/10** | **Model không đọc nhãn trong ảnh, không dùng nét chữ — chọn theo VỊ TRÍ** |
| `sanity4` | Zoom 4× so với 1× | **chưa chạy** | — |

Verdict in ra từ script: *"model không đọc nhãn, không dùng ảnh. Zero-shot vô dụng."* Model **chép chữ hai dải chính xác** (bậc 1) nhưng **không so sánh được độ đậm** (bậc 3) ⇒ lỗi ở **tầng so sánh**, không phải tầng thị giác.

**⇒ Không dựng Cấu hình D ở dạng zero-shot.** Theo luật đã ghi trước, −0,241 ≤ 0 ⇒ dừng. Không dòng code solver nào bị sửa.

**Hạn chế — không đọc quá kết quả:** (a) `sanity4` chưa chạy ⇒ câu hỏi mở của §Cấu hình C **vẫn còn nguyên**, chưa tách được "nút thắt phân giải ảnh" khỏi "ViT vứt mất độ dày nét"; (b) phép đo chỉ trả lời về **zero-shot** — D + QLoRA **chưa kiểm**, mà lỗi lại nằm đúng ở tầng fine-tuning sửa được, nên "dừng D" là dừng nhánh zero-shot; (c) 120 câu đủ để loại phương án thua 0,241 điểm, không đủ đo chênh lệch nhỏ.

#### Việc cần làm tuần sau (Tuần 3)

- [x] Cấu hình C — LayoutLMv3/LayoutXLM, chỉ trên `argmax`/`argmin` — **KẾT LUẬN ÂM CÓ BẰNG CHỨNG, không dựng model** (xem §Cấu hình C dưới)
- [ ] Ablation A/B/C/D đầy đủ + điền cột kết quả vào Outline mục IV

#### Câu hỏi đang chờ TA

- ~~Định nghĩa chính xác Evidence-F1 (ghép tham lam hay tối ưu, box thừa có bị phạt) — 15% điểm phụ thuộc; treo từ WEEK01.~~ ✅ **BTC đã trả lời** (2026-10-07): one-to-one, IoU ≥ 0,5, Hungarian hoặc greedy đều được nếu nhất quán, box thừa bị phạt qua precision. `evidence_f1.py` **đã đúng y hệt từ đầu**. Đo thêm: tham lam ≡ tối ưu trên 11.000 câu (0 khác biệt — không box nào chạm được 2 box vàng, nên câu hỏi con này vô nghĩa trên dataset); luật phạt box thừa đáng −0,0033 điểm cuộc thi.
- Quy ước `page` khi nộp file (`labels.jsonl` dùng 1-based) — treo từ WEEK01. **BTC không trả lời.**
- Thu hẹp C/D vào 3 dạng còn dư địa có còn đủ để gọi là ablation A/B/C/D đầy đủ không. **BTC không trả lời.**

---

## ĐÃ NỘP

### WEEK02 — Experiment Results (bản §II.5)

- File nộp: `Báo cáo/WEEK02 - Experiment Results.docx` (nguồn md cùng tên; export bằng `code/export_progress_report.py "WEEK02 - Experiment Results.md"`)
- Đây là `WEEK02 - Experiment Results` đã hứa ở Tuần 1, nay hoàn thành. Nộp ngay khi xong, **không chờ** báo cáo tiến độ — vì cuối tuần mới có kỳ nộp tổng kết Tuần 2.
- Nội dung: mốc Outline Tuần 2 (argmax 88,14 → 93,6 · argmin 87,12 → 92,6); ba split dev 0,967 / eval 0,972 / all 0,968 vs baseline 95,45; phân rã 8 dạng; đối chiếu trần oracle; kiểm tra hợp lệ.
- Bản này **có** mục "Câu hỏi cần TA hỗ trợ" (§5) — ba câu hỏi treo từ WEEK01. **Quy ước mới:** câu hỏi cho TA gửi qua **form đặt câu hỏi cho TA**, không ghi vào báo cáo tiến độ. `WEEK02 - Báo cáo tiến độ` chỉ nhắc một dòng trỏ sang §5 của bản này.

### WEEK01 — Báo cáo tiến độ
- File: `Báo cáo/WEEK01 - Báo cáo tiến độ (16-18.09).docx` (nguồn md cùng tên, dựng 22/09; export bằng `code/export_progress_report.py`). Bản nộp 18/09 lưu ở `Báo cáo/WEEK01 - Báo cáo tiến độ (16-18.09).BACKUP-18-09.docx`
- Bản tổng hợp tuần (§II.5, viết bổ sung 22/09): `Báo cáo/WEEK01 - Baseline and Error Analysis.docx` (nguồn md cùng tên) — mục 1 đối chiếu mốc Outline Tuần 1, mục 2 gom lại toàn bộ số liệu baseline/trần oracle/phân rã lỗi, mục 3 bốn phát hiện định hướng, mục 5 kế hoạch đã hứa cho Tuần 2 + trạng thái thực tế.
- Tóm tắt: 16 script Python audit/probe baseline TA Minh (chỉ đọc); 10 paper + Paper Tracker; harness `anls.py` + `evidence_f1.py`; chốt Outline Project nộp TA.
- Mốc đo được: baseline TA Minh 95,45 (ANLS 96,25 · Evidence-F1 90,89); trần oracle 99,17% (đo lại 21/09, không dùng nhãn); 93,1% câu sai ở argmax/argmin.
- **Đính chính 22/09** (mục 5 của báo cáo): hai con số trong bản nộp 18/09 đã sửa — "trần trích xuất 100,00%" → **trần oracle 99,17%**; "sáu dạng đạt 100,00" → **năm dạng** (6.693 câu). Bổ sung theo góp ý TA 19/09: định nghĩa 439/415/403/315, cột "Đóng góp" tính theo điểm bị mất.
- Kế hoạch đã hứa với TA cho tuần sau: `WEEK02 - Experiment Results` trong Working Files. **Đã hoàn thành** — xem WEEK02.
