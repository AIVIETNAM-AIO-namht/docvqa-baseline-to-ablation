# BÁO CÁO TIẾN ĐỘ ĐỊNH KỲ — TUẦN 3

Chủ đề: Hỏi đáp trên ảnh tài liệu (Document VQA) — OLP AI PTIT 2026, Vòng loại
Người thực hiện: Huỳnh Thuyên Nam
Kỳ báo cáo: **Tuần 3 (WEEK03)** — mốc trong bảng kế hoạch ở Outline mục V

Mốc đã hứa cho Tuần 3: *"Triển khai Cấu hình C — LayoutLMv3 / LayoutXLM, chỉ trên `argmax`/`argmin`."*

**Kết quả: Cấu hình C không được dựng — nhưng đây là một kết luận âm *có bằng chứng*, không phải việc chưa làm.** Tuần này đo trần của nhánh C trước khi bỏ công dựng model, và phát hiện trần đó **không triển khai được**. Chi tiết ở §2.

---

## Tóm tắt nhanh (bốn mục theo form cập nhật)

- **Công việc đã thực hiện:** đo trần chính xác của **mọi** bộ lọc hàng tĩnh cho `argmax`/`argmin` trên cả ba split; kiểm chứng bằng 4 họ luật không-cần-nhãn xem có luật nào chạm được trần không; sửa một công thức sai trong kế hoạch (trần 94,11% → **99,14%**); thêm phép kiểm hợp lệ tự động cho harness trần.
- **Kết quả hiện tại:** Cấu hình B đứng nguyên (0,968 all · 0,967 dev · 0,972 eval) — **không có dòng code nào của solver bị sửa trong tuần này**. Trần nhánh C đo được 99,14% (dev) / 98,93% (eval), nhưng **0 trong 4 họ luật không-cần-nhãn** chạm tới nó. Trên đúng 197 câu B sai, tín hiệu thị giác tốt nhất chỉ trỏ đúng hàng vàng **9,1%** số ca ⇒ **Cấu hình C cho kết luận âm có bằng chứng.**
- **Khó khăn đang gặp:** điểm dừng đã hứa với TA đã tới — xem §5. Cấu hình C cho kết quả âm có bằng chứng, nên theo đúng cam kết tôi **báo TA trước khi chuyển sang Cấu hình D.**
- **Câu hỏi cần TA hỗ trợ:** câu hỏi gửi riêng qua **form đặt câu hỏi cho TA**, không ghi trong báo cáo này (quy ước từ WEEK02).

Chi tiết từng mục ở §1–§5 dưới đây.

---

## 1. Tổng quan công việc trong tuần

| # | Công việc | Sản phẩm để lại |
|---|---|---|
| 1 | Viết harness đo trần chính xác của mọi bộ lọc hàng tĩnh cho `argmax`/`argmin`, chạy trên dev **và** eval | `code/row_filter_ceiling.py` |
| 2 | Kiểm chứng trần bằng 4 họ luật không-cần-nhãn (khử trùng văn bản, hàng đậm từ ảnh, từ khoá hàng tổng, hình học hàng) | `code/probe_dedup.py`, `code/probe_bold_rule.py`, `code/probe_row_filter.py` |
| 3 | Đo tín hiệu cứu hàng vàng **trong đúng 197 câu B sai** — phép đo chốt kết luận | `code/probe_gold_signal.py` |
| 4 | Thêm phép kiểm hợp lệ tự động cho harness trần (đổi tên file nhãn rồi chạy lại) | `code/check_validity.py` (đã có, nay áp cho harness mới) |
| 5 | Viết báo cáo kết luận nhánh C | `WEEK03 - Báo cáo tiến độ.docx` |

---

## 2. Cấu hình C — đo trần trước khi dựng model

### 2.1. Vì sao đo trần trước

Cấu hình C theo Outline là **Cấu hình B + LayoutLMv3/LayoutXLM**, thu hẹp vào `argmax`/`argmin`, với kỳ vọng *"giải quyết Tái dựng hàng logic bằng mô hình học nông có tham số spatial"*.

Dựng LayoutLMv3 là việc lớn: chưa cài `torch`/`transformers`, GPU chỉ có **4.096 MiB VRAM**, và đây là lần đầu dự án dùng mô hình học sâu. Trước khi bỏ công đó, tuần này đo **giới hạn trên** của cả nhánh: nếu biết trước đáp án thì việc chọn hàng giỏi nhất có thể đạt bao nhiêu? Con số đó chặn trần của mọi model không gian, kể cả model hoàn hảo.

### 2.2. Trần đo được — và một công thức sai trong kế hoạch đã được sửa

Kế hoạch ban đầu tính trần bằng điều kiện `S ⊆ ⋂ pool_j`. Điều kiện đó **sai**: nó coi hàng nằm ngoài `pool_j` là hàng chặn, trong khi hàng ngoài `pool_j` không bao giờ ảnh hưởng tới câu `j`. Sửa lại thành:

```
blocked[j] = {r ∈ pool_j : khoá(r) TỐT HƠN khoá(hàng vàng j)}
Tập câu T khả thi  ⇔  với mọi i,j ∈ T:  gold_i ∉ blocked[j]
trần[bảng] = max |T|
```

Sửa công thức **nâng** trần từ 94,11% lên 99,14%. Harness có một bất biến kiểm được: tập câu Cấu hình B **đã đúng** luôn khả thi (chọn bộ lọc bằng chính `pool_j`), nên trần **bắt buộc ≥** số câu B đúng — harness `assert` điều này trên từng bảng và không bảng nào vi phạm.

| Split | Câu `argmax`/`argmin` | Cấu hình B đúng | Trần (biết trước hàng vàng) | Dư địa nhánh C |
|---|---:|---:|---:|---:|
| dev | 3.024 | 2.827 = **93,49%** | 2.998 = **99,14%** | +171 câu = +5,65 điểm % |
| eval | 748 | 704 = **94,12%** | 740 = **98,93%** | +36 câu = +4,81 điểm % |
| all | 3.772 | 3.531 = **93,61%** | 3.738 = **99,10%** | +207 câu = +5,49 điểm % |

Quy ra điểm cuộc thi (dư địa × tỉ trọng 3.772/11.000): **+0,0194 điểm** (dev) · **+0,0165** (eval) · **+0,0188** (all) — tức 0,968 → ~0,987 trong kịch bản tốt nhất.

**Khoảng cách dev − eval — sản phẩm Tuần 3 yêu cầu:**

| Đại lượng | dev | eval | Chênh (dev − eval) |
|---|---:|---:|---:|
| Tỉ lệ B đúng | 93,49% | 94,12% | −0,63 điểm % |
| Trần | 99,14% | 98,93% | +0,21 điểm % |

Eval **nhỉnh hơn** dev ở tỉ lệ B đúng và gần bằng ở trần ⇒ không có dấu hiệu overfit theo tài liệu, khớp kết luận đã báo ở WEEK02. 26 câu (dev) và 8 câu (eval) nằm ở bảng tự mâu thuẫn — hai câu trên cùng bảng đòi hai tập hàng khác nhau, không bộ lọc tĩnh nào cứu được cả hai.

### 2.3. Trần là **cần**, chưa **đủ** — và đây là chỗ kế hoạch rẽ nhánh

Trần 99,14% đo bằng cách **nhìn trước hàng vàng** (`labels.jsonl`), nên nó không phải một solver. Muốn biến nó thành điểm thật phải có một **luật suy từ OCR** chọn đúng tập hàng đó. Kế hoạch đã ghi rõ nhánh quyết định:

> **Trần phủ định (> 94,2%, tức tìm được luật không cần nhãn)** ⇒ cài luật đó vào `argmax`/`argmin` và chạy lại cả ba split.

Hai vế của câu này **mâu thuẫn nhau sau khi sửa công thức**: trần 99,14% > 94,2% (vế đầu đúng), nhưng không luật không-cần-nhãn nào tồn tại (vế trong ngoặc sai). Vế trong ngoặc mới là vế có nghĩa — nó mới là điều kiện triển khai được. Nên tuần này dành trọn §2.4 để trả lời đúng câu đó.

### 2.4. Bốn họ luật không-cần-nhãn — không họ nào chạm trần

| Họ luật | Kết quả đo (dev, 3.024 câu) | Kết luận |
|---|---|---|
| Khử trùng văn bản (4 biến thể) | 39,0% – 66,7% (baseline 93,5%) | **Loại** — kéo tụt mạnh |
| Hàng in đậm đo từ ảnh (`bold_row`) | 10,4% | **Loại** — vô dụng |
| Từ khoá hàng tổng / hàng phụ | không phân biệt được (27,2% vs 28,5%) | **Loại** |
| Hình học hàng (thụt lề, khe hở, đường kẻ) | đồng nhất tuyệt đối: cao độ 0,02121 ở mọi hàng, khe hở 0,00000 | **Loại** |

Chi tiết đáng chú ý:

- **Khử trùng văn bản** là họ có tín hiệu thật (81,7% hàng bị loại có nhãn trùng, so với 64,3% hàng được giữ) nhưng **phản tác dụng**: 60,5% hàng vàng *cũng* mang nhãn trùng, nên áp thô kéo 93,49% xuống 39,0%.
- **Hàng in đậm** là tín hiệu thị giác thật, đo được sạch từ ảnh trang — nhưng bỏ phiếu trên toàn bộ ứng viên chỉ đúng 10,4%.
- **Hình học** đã đo trên 9 tài liệu khác nhau: cao độ hàng đều tăm tắp, khe hở giữa các hàng bằng đúng 0, không thụt lề, không đường phân khối. **Đây chính là loại tín hiệu mà LayoutLMv3 được kỳ vọng khai thác — và nó không tồn tại trong dữ liệu này.**

### 2.5. Phép đo chốt: tín hiệu cứu hàng vàng **trong đúng 197 câu B sai**

Bốn họ luật trên đo trên toàn bộ 3.024 câu. Nhưng câu hỏi hẹp hơn mới quyết định: **trong 197 câu B làm sai, có tín hiệu nào trỏ đúng hàng vàng không?** Nếu có một tín hiệu trúng phần lớn 197 câu thì vẫn còn đường.

| Tín hiệu (đo trên 197 câu B sai, dev) | Số câu | Tỉ lệ |
|---|---:|---:|
| Hàng vàng **chính là** hàng in đậm đo từ ảnh | 18 | **9,1%** |
| Hàng vàng **không phải** hàng in đậm | 179 | 90,9% |
| Hàng in đậm lại đúng là hàng B **đã chọn** (tín hiệu vô dụng) | 23 | 11,7% |
| Đo được hàng đậm nhưng nó sai chỗ (không phải vàng, không phải hàng B chọn) | 156 | 79,2% |
| Không đo được hàng đậm | 0 | 0,0% |
| Hàng vàng nằm trong khối nhãn chưa lặp (tín hiệu văn bản) | 108 | **54,8%** |

Trên eval (44 câu B sai): hàng đậm trúng **6,8%**, khối đầu trúng **72,7%**. Cùng kết luận.

Đọc bảng này: tín hiệu thị giác tốt nhất trỏ đúng hàng vàng **9,1%** số ca, và trong **79,2%** số ca nó đo được nhưng chỉ vào một hàng **thứ ba** — không phải hàng vàng, cũng không phải hàng B đã chọn. Nghĩa là trong bảng có **nhiều hơn một** hàng mang tín hiệu "nổi bật", và tín hiệu nổi bật **không tương quan** với hàng đúng. Một model học trên tín hiệu này sẽ học đúng cái nhiễu đó.

### 2.6. Kết luận Cấu hình C

**Không dựng LayoutLMv3/LayoutXLM.** Bốn lý do, xếp theo sức nặng:

1. **Không có tín hiệu để học.** Mọi tín hiệu không-cần-nhãn đã đo đều thất bại, và tín hiệu thị giác tốt nhất chỉ trúng 9,1% số ca sai. LayoutLMv3 khai thác tín hiệu không gian + thị giác; cả hai đã đo là không tồn tại (hình học đồng nhất tuyệt đối) hoặc không tương quan (hàng đậm).
2. **Dư địa là oracle-only.** Trần 99,14% chỉ đạt được khi biết trước đáp án. Không có luật nào chạm tới ⇒ con số đó không chuyển thành điểm thi được.
3. **Chi phí lớn, kết quả âm đã biết trước.** 4.096 MiB VRAM, chưa cài `torch`, vài ngày công — cho một kết quả mà §2.4–2.5 đã đo là âm.
4. **Cấu hình B không bị xê dịch.** Không một dòng code nào của `audit_rule_system.py` thay đổi trong tuần này; mọi con số đã nộp cho TA giữ nguyên giá trị.

**Đây là kết luận âm *có bằng chứng*, không phải việc chưa làm:** nó trả lời câu hỏi nghiên cứu của Topic Team — *"mô hình học sâu chỉ thực sự cần thiết ở loại lỗi nào?"* — bằng số đo: ở `argmax`/`argmin` của bộ dữ liệu này, **không loại lỗi nào cần mô hình không gian**, vì tín hiệu không gian không tồn tại.

---

## 3. Định hướng cho Cấu hình D — dư địa thật nằm ở chỗ khác

Đặt cạnh trần oracle toàn hệ thống 99,17%:

| Dạng | Trần oracle | Cấu hình B | Dư địa còn lại |
|---|---:|---:|---:|
| 7 dạng còn lại | 100,00% | ~100% | ~0 |
| `argmax` | 100,00% | 93,6 | 6,4 điểm % nhưng **oracle-only** (§2) |
| `argmin` | 100,00% | 92,6 | 7,4 điểm % nhưng **oracle-only** (§2) |
| `visual_bold_lookup` | **82,99%** | 83,1 | **0 — đã chạm trần tín hiệu** |

Phân rã 3,20 điểm mất của toàn hệ thống (11.000 câu): **`argmin` 39,4% · `argmax` 34,5% · `visual_bold_lookup` 25,7%** · `cross_page_sum` 0,5% · bốn dạng còn lại 0,0%. Nghĩa là **`argmax`/`argmin` giữ 73,9% phần điểm mất, `visual_bold_lookup` chỉ giữ 25,7%** — nhưng 73,9% kia là **oracle-only** (§2.6): trần 99,10% đo được chỉ với điều kiện biết trước hàng vàng, và bốn họ luật không-cần-nhãn đã kiểm đều **không chạm tới**. Nên câu hỏi không phải "dư địa nằm ở đâu" mà là **"dư địa nào chạm tới được"** — và chỉ còn một chỗ.

Chỗ đó là `visual_bold_lookup`: dạng duy nhất có trần **dưới 100%**, vì `is_bold` là trường **duy nhất không có tương ứng trong OCR** (đúng như đề bài ghi *"OCR không ghi nhận định dạng chữ"*). Trần 82,99% đã đo là **trần của tín hiệu ảnh** — 5 phép đo độ dày nét chuẩn hoá khác nhau đều cho cùng kết quả, nên không phải lỗi cài đặt. Cấu hình B đang ở 83,1%, tức **đã chạm trần đó**.

**Đối số định hướng:** dư địa của `argmax`/`argmin` là 73,9% phần điểm mất nhưng không triển khai được (§2.6 — oracle-only, mọi luật không-cần-nhãn đã đo đều trượt). `visual_bold_lookup` bị chặn bởi tín hiệu ảnh mà pipeline hiện tại **chỉ đọc qua một phép đo độ dày nét**. **VLM đọc ảnh trực tiếp (Cấu hình D — Qwen2.5-VL) là phép thử duy nhất còn lại để trả lời câu hỏi thật: 82,99% là trần của tín hiệu, hay chỉ là trần của phép đo độ dày nét?** Đây là căn cứ để Tuần 4 dồn vào D thay vì C.

---

## 4. Khó khăn và điểm dừng

- **Điểm dừng đã hứa với TA đã tới, và đã giữ đúng cam kết.** WEEK02 §5 ghi: *"nếu Cấu hình C không vượt được Cấu hình B trên `argmax`/`argmin` sau khi đã căn chỉnh, tôi sẽ báo TA trước khi chuyển sang Cấu hình D."* Cấu hình C **không vượt** B — nó không dựng được vì dư địa là oracle-only (§2.6). Vậy nên: **báo cáo này là thông báo cho TA, và tôi chưa chuyển sang D.**
- **Rủi ro tiến độ:** Tuần 3 theo Outline là tuần dựng C. Kết quả âm nghĩa là tuần này không sinh ra model nào. Đổi lại, kết luận âm này tiết kiệm nhiều ngày GPU cho một hướng đã biết là âm, và trả lời trực tiếp câu hỏi nghiên cứu của Topic Team.
- **`visual_bold_lookup` đã chạm trần tín hiệu ảnh 82,99%** — không phải lỗi cài đặt. Dạng này là dư địa **duy nhất còn chạm tới được** (§3): trần 82,99% là trần của một phép đo độ dày nét, chưa chắc là trần của tín hiệu ảnh.
- **`cross_page_sum` chỉ có 46 câu** — mọi kết luận trên dạng này không có ý nghĩa thống kê.
- **Rủi ro chưa đo được ở bộ định tuyến intent** (`intent_router.py`): luật regex viết sau khi khảo sát template của train. Đúng 11.000/11.000 trên train là hệ quả của quy ước sinh dữ liệu, không phải bằng chứng. Bằng chứng thật là phân bố dự đoán khớp train trong ±1 điểm % trên cả `public_test` và `private_test`. **Nếu private_test dùng template câu hỏi khác, luật sẽ vỡ.**
- **Một tín hiệu giả tiếp tục bị loại:** hàng in đậm luôn đứng đầu danh sách evidence (535/535 câu) — nhưng khi lệch với ảnh thì ảnh đúng 0/88, thứ tự đúng 88/88 ⇒ quy ước sinh dữ liệu. Tuần này xác nhận thêm: dùng chính hàng đậm làm luật chỉ được 10,4%.

---

## 5. Kế hoạch tuần tới

| # | Việc | Kết quả mong đợi |
|---|---|---|
| 1 | Ablation A/B/C/D đầy đủ, điền cột kết quả vào Outline mục IV | Bảng kết quả ablation |
| 2 | Chuyển trọng tâm sang Cấu hình D — dư địa duy nhất còn chạm tới được (§3) | Điểm Cấu hình D trên dev và eval |

Output dự kiến cuối tuần tới: `WEEK03 - Ablation Study` trong Working Files.
