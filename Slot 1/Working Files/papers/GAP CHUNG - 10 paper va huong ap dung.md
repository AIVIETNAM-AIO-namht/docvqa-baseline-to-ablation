# GAP CHUNG — 10 paper và phương án áp dụng được

**Subtopic:** Hỏi đáp trên ảnh tài liệu (Document VQA) · OLP AI PTIT 2026 — vòng loại
**Ngày:** 2026-09-17
**Đối tượng:** 10 PDF trong `Working Files/papers/`

> ## ⚠️ ĐÂY LÀ BẢN ĐỒ ĐỌC, KHÔNG PHẢI NỘI DUNG NỘP
>
> Quy chế Topic Team:
> - *"Các output được submit trong Topic Team phải do chính thành viên của nhóm trực tiếp thực hiện."*
> - *"Không sử dụng AI để viết nội dung sản phẩm nộp... AI không được sử dụng để thay thế quá trình tự đọc paper, tự phân tích hoặc tự xây dựng nội dung của nhóm."*
> - *"Khi tham khảo ý tưởng, kiến trúc, hình ảnh hoặc nội dung từ nguồn khác, nhóm cần ghi nguồn đầy đủ."*
>
> Mọi khẳng định dưới đây đều kèm **số section / số bảng + trích nguyên văn** để tự kiểm chứng. Phải tự mở PDF đọc lại trước khi dùng bất cứ dòng nào.
>
> **Quan hệ với 2 file đã có:**
> - `Tổng hợp hạn chế 10 paper.md` = hạn chế **của từng paper** (danh sách rời).
> - `WEEK01 - Output dự kiến (first-principle + reverse thinking).md` = chọn **loại output** (O-A…O-D).
> - **File này** = hạn chế **chung** — cái mà cả 10 paper cùng không giải quyết — và **phương án lấy từ paper nào để lấp**.

---

## 0. Cách đọc file này

Mỗi gap chung gồm 4 phần cố định:

| Phần | Nội dung |
|---|---|
| **Bằng chứng** | Số liệu + section từ ≥ 2 paper độc lập |
| **Vì sao là gap CHUNG** | Không phải lỗi riêng của một paper — cả nhóm phương pháp cùng vướng |
| **Chạm đề olp-ai-ptit không** | Có ảnh hưởng điểm số thật hay chỉ là vấn đề học thuật |
| **Phương án áp dụng được** | Lấy cơ chế cụ thể từ paper nào, làm gì |

---

## G1. Không paper nào đo chất lượng vùng evidence theo đúng protocol của đề

### Bằng chứng

Đề chấm: `Question_Score = 0.85×ANLS + 0.15×Evidence-F1`, evidence khớp khi **IoU ≥ 0.5**, mỗi câu có **2–6 vùng** evidence (`labels.jsonl`).

Quét cả 10 paper:

| Paper | Có metric localization? | Có ngưỡng IoU? | Multi-box? |
|---|---|---|---|
| BoundingDocs | Mean IoU (không ngưỡng) | ✗ | GT có nhiều box, nhưng báo cáo gộp |
| DocExplainerV0 | Mean IoU (không ngưỡng) | ✗ | ✗ — *"excluding cases that require reasoning over multiple elements or regions"* (§5) |
| LMDX | Micro-F1 field-level (khớp chuỗi) | ✗ | ✗ |
| LayoutLMv3 | **không có** | ✗ | ✗ |
| LiGT | **không có bbox** | ✗ | ✗ |
| TAPAS | **không có** | ✗ | ✗ |
| DocLLM | **không có** | ✗ | ✗ |
| DocVQA | **không có** (không có GT vùng đáp án) | ✗ | ✗ |
| Qwen2-VL / 2.5-VL | RefCOCO acc@0.5 | ✓ | ✗ — box đơn, ảnh tự nhiên |

**Qwen2-VL Table 6 là acc@0.5 trên RefCOCO** — đúng là IoU có ngưỡng, nhưng trên **ảnh tự nhiên, referring expression, một box**, không phải vùng đáp án trong tài liệu.

Và Qwen2-VL/Qwen2.5-VL **không có lấy một con số IoU nào khác**: grep `iou` trong cả hai paper chỉ ra các hit vô nghĩa (`various`, `previous`, `obvious`), cộng mIoU **thời gian** của Charades-STA (video, không phải box). Không phân bố IoU, không MeanIoU, không breakdown ở ngưỡng cao hơn, không đo vùng tài liệu.

**Một quan sát về chính các paper:** **LayoutLMv3, DocExplainerV0, Qwen2-VL, Qwen2.5-VL đều KHÔNG có mục Limitations.** DocLLM và TAPAS có nhưng rất ngắn. Nghĩa là phần lớn hạn chế trong file này phải **suy ra từ bảng số**, không đọc được từ lời tác giả — và đó là lý do mục "ĐIỂM CẦN XÁC MINH LẠI" ở cuối file quan trọng.

### Vì sao là gap CHUNG

Ba nhóm phương pháp độc lập cùng né:

1. **Nhóm KIE** (LMDX, LayoutLMv3, BoundingDocs) — có toạ độ nhưng chấm bằng **khớp chuỗi field-level**, không chấm bằng hình học. LMDX có `bounding_box` trong output (Algorithm 2) nhưng **không đưa vào metric nào**.
2. **Nhóm VQA** (DocVQA, DocLLM) — dataset **không có GT vùng đáp án**, nên về mặt dữ liệu không thể đo.
3. **Nhóm VLM** (Qwen2-VL, Qwen2.5-VL) — có đo IoU nhưng ở **benchmark detection ảnh tự nhiên**, không chuyển sang tài liệu.

→ **Không tồn tại tiền lệ để so sánh.** Nghĩa là: không có baseline số nào để nhóm đối chiếu, và cũng không có paper nào chỉ ra cách làm đúng.

### Chạm đề không

**Có, trực tiếp.** 0.15 điểm/câu × 2,000 câu private test. Và đây là **15% điểm mà toàn bộ reading list không phủ**.

Thêm một điểm nữa: `evaluate_predictions.py` trong repo TA Minh **không implement ANLS** — nó dùng exact match:

```python
answered = answer not in (None, "không xác định")
correct = answered and answer in label["answers"]
```

Và **không có phần Evidence-F1 nào cả**. Nghĩa là **metric chính thức vắng mặt trong reference implementation** — nhóm phải tự viết, và không thể tin số của script TA Minh.

### Phương án áp dụng được

| Lấy từ | Cơ chế | Áp dụng |
|---|---|---|
| **LMDX §3.5** | Grounding Verification — kiểm tra prediction có thật nằm trong segment không, loại nếu không | Dùng để **lọc evidence sai** trước khi nộp: box nào không chứa text của đáp án → loại |
| **LMDX Algorithm 2** | `G.bounding_box = {min(b.x), min(b.y), max(b.x), max(b.y)}` | Công thức gộp nhiều block thành 1 box — dùng để sinh evidence nhiều vùng |
| **DocExplainerV0 §4.3** | Naive OCR baseline — string-search đáp án trong OCR text, fallback từ đầu tiên | Baseline đối chứng bắt buộc phải có, để chứng minh phương pháp phức tạp hơn là có ích. ⚠️ **Nhưng đọc P4 trước** — DocVQA Table 1 đo được bẫy false-positive **10 điểm** của đúng cơ chế này (substring UB 87.00 vs subsequence UB 77.00). MeanIoU .494 có thể đã bị thổi lên |
| **BoundingDocs §3.2.2** | *"If the answer is found in multiple locations on the page through this procedure, all occurrences are considered valid answers."* | Cách sinh **nhiều box ứng viên** cho 1 câu — dùng để tăng recall evidence |

**Việc phải làm ngay:** tự viết `evidence_f1.py` theo đúng protocol (IoU ≥ 0.5, so khớp tập hợp nhiều box, có matching 1-1) **trước** khi tối ưu bất cứ thứ gì. Không có metric thì không biết mình đang cải thiện hay làm tệ đi.

---

## G2. Sinh toạ độ bằng VLM hỏng ở mức một bậc độ lớn — nhưng cả 4 paper vẫn đi theo hướng đó

### Bằng chứng

Hai paper độc lập, hai benchmark độc lập, cùng một con số:

**DocExplainerV0 Table 1** (ANLS / MeanIoU):

| Model | Prompt | ANLS | MeanIoU |
|---|---|---|---|
| SmolVLM-2.2B | Zero-shot | .527 | .011 |
| SmolVLM-2.2B | **Anchors** | .543 | **.026** |
| SmolVLM-2.2B | CoT | .561 | .011 |
| Qwen2-VL-7B | Zero-shot | .691 | .048 |
| Qwen2-VL-7B | **Anchors** | .694 | **.051** ← IoU cao nhất trong 3 prompt |
| Qwen2-VL-7B | **CoT** | **.720** ← ANLS cao nhất | **.038** ← tụt so với Anchors |
| Claude Sonnet 4 | Zero-shot | .737 | .031 |
| SmolVLM + DocExplainer (regressor) | Zero-shot | .572 | .175 |
| Qwen2-VL + DocExplainer | Zero-shot | .689 | .188 |
| **Qwen2-VL + Naive OCR** | Zero-shot | .690 | **.494** |

**Nghịch lý prompt — đọc kỹ bảng này:** cấu hình cho **ANLS cao nhất không phải cấu hình định vị tốt nhất**. Qwen2-VL CoT đạt ANLS .720 (cao nhất) nhưng MeanIoU **.038**, thấp hơn hẳn Anchors **.051**; SmolVLM lặp lại đúng pattern đó (.561/.011 so với .543/.026). Tác giả §4.4 tự viết: *"Among the various prompting settings, 'Anchors' is the one that most helps VLMs on this task, but without bringing significant advantages, while still compromising ANLS values, whose highest scores are achieved in the 'CoT' setting."*

→ Nghĩa là **tối ưu cho 85% và tối ưu cho 15% kéo ngược chiều nhau**. Chọn một prompt duy nhất cho cả hai là tự bỏ điểm. Phải tách: một cấu hình sinh đáp án, một cơ chế chọn evidence.

**BoundingDocs §4.6:**
> *"Claude 4 Sonnet achieves an average IoU of 0.031 on the BoundingDocs test set, while Qwen2.5-VL-7B reaches 0.048... their capacity to indicate the precise location of the answer is effectively nonexistent, which significantly undermines the interpretability of their responses."*

### Vì sao là gap CHUNG

Cả 4 paper sinh toạ độ (DocExplainerV0, BoundingDocs, Qwen2-VL, Qwen2.5-VL) đều dừng ở **IoU .011–.051** — dưới ngưỡng 0.5 của đề **một bậc độ lớn**.

Và cả 4 đều **không sửa được**:
- **DocExplainerV0** huấn luyện hẳn một regressor SigLIP2 để sửa → lên .188, vẫn **thua baseline OCR chuỗi đơn giản (.494) gần 3 lần**. Tác giả tự nhận §4.4: *"DocExplainer's results are still very far from the OCR-based baseline (approximately three times less effective)"*.
- **Qwen2.5-VL** đổi từ toạ độ chuẩn hoá sang toạ độ tuyệt đối để *"effectively represent the original size and position of objects"* — **nhưng RefCOCO lại thấp hơn Qwen2-VL cả 3 split** (92.7/94.6/89.7 vs 93.2/95.3/90.7). Đổi hệ toạ độ **không chứng minh được cải thiện localization**.

### Chạm đề không

**Có — và đây là kết luận kiến trúc quan trọng nhất của cả 10 paper.**

Evidence là bài toán **SELECTION, không phải GENERATION**. Không bao giờ hỏi VLM toạ độ. Luôn chọn trong candidate có sẵn.

Và một chi tiết có tính đòn bẩy cao: **MeanIoU .494 nằm sát ngay ngưỡng 0.5**. Nghĩa là chỉ cần **siết box chặt hơn một chút**, một phần lớn câu sẽ nhảy từ 0 điểm evidence lên điểm đầy đủ — vì metric là **ngưỡng nhị phân**, không phải trung bình. Đây là chỗ rẻ nhất để ăn điểm trong toàn bộ bài.

⚠️ **Phải tự đo.** MeanIoU .494 **không** suy ra trực tiếp tỉ lệ pass. Con số đó của DocExplainerV0 đo trên dataset khác. Việc cần làm là chạy baseline string-search trên `training_set` của olp-ai-ptit rồi đo **tỉ lệ IoU ≥ 0.5** thật.

### Phương án áp dụng được

| Lấy từ | Cơ chế | Áp dụng |
|---|---|---|
| **DocExplainerV0 §4.3** | Naive OCR: string-search đáp án trong OCR text, **fallback về từ đầu tiên** nếu không khớp đủ | Baseline số 1, chạy đầu tiên, đo tỉ lệ IoU≥0.5 thật |
| **LMDX §3.5 + Algorithm 2** | Grounding Verification + union hull nhiều block | Siết box: từ nhiều block khớp → gộp bằng min/max, loại block không chứa text |
| **BoundingDocs §3.2.2** | Mọi lần xuất hiện đều là đáp án hợp lệ | Sinh nhiều candidate box → tăng recall, rồi lọc bằng grounding |
| **`cell_annotations.jsonl`** (đề cho sẵn) | 256,040 dòng `{document_id, page, table, row, column, block_id, bbox, clean_text, is_bold, is_header}` | **Nguồn candidate box chính xác hơn OCR block thô** — box mức **cell**, khớp đúng ngưỡng IoU ≥ 0.5 mà đề yêu cầu |

**Lưu ý quan trọng:** LMDX §Limitations tự nhận *"LMDX's localization and bounding boxes are not reliable beyond line-level granularity"*. Đề cần mức **cell**. `cell_annotations.jsonl` cho sẵn mức cell → **đây là lợi thế dữ liệu mà cả 10 paper không có**. Nên khai thác trước tiên.

---

## G3. `argmax` / `argmin` / `compare` và `cross_page_sum` vắng mặt **về mặt cấu trúc** trong mọi paper

### Bằng chứng

Đề có 8 loại reasoning với số câu training:

| Loại | Số câu | Paper nào làm được? |
|---|---|---|
| `lookup` | 2,200 | ✅ tất cả |
| `argmax` | 1,898 | ❌ |
| `argmin` | 1,874 | ❌ |
| `sum` | 1,810 | ⚠️ chỉ TAPAS |
| `compare` | 1,722 | ❌ |
| `count` | 915 | ⚠️ chỉ TAPAS |
| `visual_bold_lookup` | 535 | ❌ |
| `cross_page_sum` | 46 | ❌ |

**TAPAS** — toán tử đóng và nhỏ: chỉ **{SUM, COUNT, AVERAGE, NONE}**. **Không có MAX/MIN** → không làm được `argmax`/`argmin`. Không có phép so sánh → không làm được `compare`. Tự nhận trong Limitations: *"structures with multiple aggregations such as 'number of actors with an average rating higher than 4' could not be handled correctly"*.

Và ngay cả `sum`/`count` cũng gần như không dùng: *"for more than 98% of the examples the aggregation is only applied to one or no cells"*.

**LayoutLMv3 §3.3** — head extractive thuần:
> *"We formalize this task as an extractive QA problem, where the model predicts start and end positions by classifying the last hidden state of each text token with a binary classifier."*

→ Chỉ trả về **span liên tục của input token**. Không thể sinh `sum`, `count`, `argmax`/`argmin`, hay bất kỳ đáp án nào không nằm nguyên văn trong text.

**LMDX** — copy text từ segment, không có toán tử nào.

**`cross_page_sum` hỏng theo thiết kế ở cả 3 kiến trúc:**
- LMDX chia chunk **theo trang**: *"The decision to first divide the document by page stems from the observation that entities rarely cross page boundaries"* → cross-page nằm ngoài thiết kế.
- TAPAS: *"our model would fail to capture very large tables, or databases that contain multiple tables"*.
- LayoutLMv3: **L = 512 token**, một trang.
- DocLLM: context **1,024 token** — trần cứng nhất, cấm luôn multi-page. Hệ quả lộ ra ở Table 5: WTQ (table-only) **DocLLM-7B 27.1 vs GPT-4 zero-shot 65.4** → **thua 38.3 điểm** dù GPT-4 không có layout. WTQ **không hề được nêu là failure** trong paper.

### Vì sao là gap CHUNG

Không phải "paper X yếu ở argmax". Mà là: **toàn bộ họ kiến trúc extractive/span-head không có khái niệm toán tử.** Chúng được thiết kế cho `lookup` — và `lookup` chỉ chiếm 2,200/11,000 = **20%** câu training.

`argmax + argmin + sum + compare + count` = **8,219/11,000 = 74.7%** câu hỏi nằm ngoài khả năng của mọi paper trong reading list.

### Chạm đề không

**Có — đây là gap lớn nhất về mặt điểm số.** Gần 3/4 câu hỏi thuộc loại mà không paper nào giải được.

### Phương án áp dụng được

| Lấy từ | Cơ chế | Áp dụng |
|---|---|---|
| **TAPAS Table 1 (soft operators)** | `COUNT = Σ ps(c)` · `SUM = Σ ps(c)·T[c]` · `AVERAGE = compute(SUM)/compute(COUNT)` | Công thức **khả vi** cho count/sum trên tập cell có xác suất — dùng khi cần học mềm |
| **TAPAS Appendix D** | `AVERAGE0(T,p) = Σ_c Tc · pc/(1 + Σ_{j≠c} pj)` — dạng Taylor | Xấp xỉ average không cần chia |
| **TAPAS (inference)** | *"we select all table cells for which their probability is larger than 0.5. These predictions are then executed against the table"* | **Tách chọn cell (học) khỏi thi hành toán tử (thủ tục)** — đây là pattern chính |
| **TAPAS Table 6** | Bỏ `{cols,rows}` → SQA SEQ tụt **19.6 (−19.4)** | **Structural prior (cột/dòng) chi phối hơn cả ngữ nghĩa** — phải giữ thông tin cột/dòng, không flatten bảng |
| **`cell_annotations.jsonl`** | Có sẵn `row`, `column`, `is_bold`, `is_header` | Đủ để viết solver thủ tục cho argmax/argmin/compare/count/sum **không cần model** |

**Hướng đúng:** model chỉ **chọn cell**; toán tử do **solver thủ tục** thi hành theo `reasoning_type`. Không bắt model sinh số. Đây là điều cả 10 paper không làm, và cũng là lý do chúng không làm được.

**`visual_bold_lookup` (535 câu):** `cell_annotations.jsonl` có cột **`is_bold`** — đề cho sẵn tín hiệu bold ở mức cell. Không paper nào trong reading list khai thác bold (LiGT có LayoutHEI nhưng cho layout, không cho bold).

---

## G4. Tiếng Việt: hoặc không được test, hoặc là ngôn ngữ yếu nhất

### Bằng chứng

| Paper | Tiếng Việt |
|---|---|
| BoundingDocs | **Không có.** Table 1/Table 8 liệt kê 10 ngôn ngữ — không có tiếng Việt. Tiếng Anh 93.31% |
| DocExplainerV0 | Không test |
| DocLLM | Pretrain + instruction-tuning **chỉ tiếng Anh** (Table 2, Table 3) |
| DocVQA | Chỉ tiếng Anh |
| TAPAS | Chỉ tiếng Anh |
| LayoutLMv3 | Chỉ tiếng Anh. `"XFUND"` → **0 hit** trong toàn paper |
| Qwen2.5-VL | **Tiếng Việt xuất hiện đúng 1 lần trong cả paper** — ở §2.2.1 mô tả dữ liệu train. **Không có đánh giá nào** |
| Qwen2-VL | **Có đo, và yếu.** Table 3 OCR đa ngữ nội bộ: **Vietnamese 73.0** vs 88–97 cho châu Âu / Nhật / Hàn. Chỉ hơn GPT-4o (72.0) **1.0 điểm**. Yếu thứ nhì |
| LiGT / ReceiptVQA | **Tiếng Việt** — nhưng **không sinh bbox**, và Location type chỉ ~40% accuracy |

**Thêm bằng chứng độc lập về multilingual:** Qwen2-VL Table 2 MTVQA: Previous SoTA 23.2 · GPT-4o 27.8 · Qwen2-VL-72B 30.9 · **7B 25.6 (thua GPT-4o)** · **2B 18.1 (thua cả SoTA cũ)**.

Và **Qwen2.5-VL Table 3 MTVQA: Qwen2.5-VL-72B 31.7 — THUA cả Previous Open-source SoTA (31.9) lẫn InternVL2.5-78B (31.9)**. Nhưng §3.1 vẫn viết *"showcasing its powerful multilingual text recognition abilities"*.

**LiGT Table 5 — toàn bộ bảng, vì đây là thí nghiệm tiếng Việt duy nhất trong 10 paper:**

| Nhóm | Model | ANLS (F1 · Accuracy) |
|---|---|---|
| **Upper bound** | MATCHED_OCR (UB) | **76.77** (76.72 · 76.77) |
| **Upper bound** | MATCHED_OCR_AVG (UB) | 74.63 (74.59 · 74.63) |
| **Random** | RAND_TOP10 | 4.62 (1.54 · 1.48) |
| **Random** | RAND_TOP100 | 2.71 (0.41 · 0.31) |
| **Extractive** | CafeBERT large | 56.59 (52.67 · 50.40) |
| **Extractive** | **PhoBERT base** | **61.39** (57.55 · 54.91) | ← extractive tốt nhất |
| **Extractive** | PhoBERT large | 57.87 (53.93 · 51.34) |
| **Extractive** | XLM-Roberta base | 58.00 (54.49 · 52.28) |
| **Extractive** | XLM-Roberta large | 57.81 (53.76 · 50.97) |
| **Extractive** | InfoXLM base | 58.33 (54.49 · 51.89) |
| **Extractive** | InfoXLM large | 57.56 (52.92 · 49.08) |
| **Extractive** | LiLT[PhoBERT] base | 59.87 (56.29 · 54.05) |
| **Extractive** | LiLT[XLM-Roberta] | 58.34 (54.49 · 51.92) |
| **Extractive** | LiLT[InfoXLM] | 58.77 (54.69 · 51.34) |
| **Extractive** | LayoutXLM base | 59.11 (55.45 · 53.05) |
| **Generative** | ViT5 base | 78.08 (67.04 · 61.82) |
| **Generative** | ViT5 large | 77.22 (66.69 · 61.60) |
| **Generative** | ViT5+2D base | 75.03 (63.56 · 58.20) |
| **Generative** | ViT5+2D large | 74.08 (63.17 · 58.08) |
| **Generative** | **ViT5+U base** | **78.98** (67.89 · 62.46) | ← ANLS cao nhất |
| **Generative** | ViT5+U large | 78.78 (**68.10** · 62.80) | ← F1 cao nhất |
| **Generative** | ViT5+2D+U base | 75.91 (65.08 · 59.92) |
| **Generative** | ViT5+2D+U large | 73.56 (62.41 · 57.43) |
| **Generative** | LaTr base | 73.98 (61.53 · 56.37) |
| **Generative** | LaTr large | 73.47 (61.79 · 56.95) |
| **Generative** | **LiGT (Ours) base** | 78.78 (67.90 · 62.63) |
| **Generative** | **LiGT (Ours) large** | 78.64 (68.09 · **63.02**) | ← Accuracy cao nhất |

Ba điều đọc ra từ bảng này:

1. **Khoảng cách extractive → generative là ~17–20 ANLS**, không phải vài điểm. Và nó **nhất quán qua mọi cặp model** — PhoBERT base 61.39 vs ViT5 base 78.08; LayoutXLM 59.11 vs LaTr 73.98. Đây không phải nhiễu, là hiệu ứng kiến trúc.
2. **Các biến thể "thêm layout" (2D, U) không thắng rõ.** ViT5+U base 78.98 là cao nhất, nhưng ViT5+2D lại **thấp hơn cả ViT5 trơn** (75.03 vs 78.08). Nghĩa là cơ chế nhúng layout **không miễn phí** — nhúng sai cách còn tệ hơn không nhúng.
3. **Trần thật nằm ở 76.77 (MATCHED_OCR UB)** — tức cả họ generative đã **vượt trần extractive**, và đang tiến sát trần của chính bài toán. Dư địa còn lại trên tiếng Việt rất hẹp.
4. **Chính paper này tự mâu thuẫn ở §5.4.** §5.4 viết: *"LiGT attained the highest F1, and Accuracy score compared to other baselines"*. Đối chiếu Table 5: LiGT large **F1 68.09 — thấp hơn ViT5+U large (68.10)**, và **ANLS 78.64 — thấp hơn ViT5+U base (78.98)**. LiGT chỉ thắng đúng **Accuracy (63.02 vs 62.80)**. Tức kiến trúc "nhúng layout vào embedding" của LiGT **không thắng trên chính bảng của nó** — nó chỉ **rẻ hơn** (không cần train U-Net như ViT5+U). Đây là bài học trực tiếp: **đừng tin câu "Our model achieves SOTA" ở abstract/kết luận — luôn mở bảng ra đối chiếu.**

### Vì sao là gap CHUNG

Hai tầng:

1. **Tầng dữ liệu:** không tồn tại benchmark document VQA tiếng Việt có annotation vùng đáp án. Đã kiểm 8 dataset tiếng Việt — **không cái nào có bbox/evidence**. (SDL có bbox nhưng ảnh **tổng hợp**, và **không có câu hỏi**; ViHERMES có evidence dạng **cấu trúc**, không phải toạ độ.)
2. **Tầng model:** mọi model mạnh trong reading list đều lấy tiếng Anh làm trung tâm, và khi đo tiếng Việt thì rơi vào nhóm yếu nhất.

### Chạm đề không

**Có.** Đề thi hoàn toàn tiếng Việt, và **dấu tiếng Việt là biến số quyết định** (xem G5).

### Phương án áp dụng được

| Lấy từ | Cơ chế | Áp dụng |
|---|---|---|
| **LiGT Table 5** | Trên **tiếng Việt**: extractive (LayoutXLM base 59.11 · PhoBERT base 61.39) thua generative (ViT5+U base **78.98**) **~20 điểm ANLS** | **Bằng chứng mạnh nhất cho lựa chọn kiến trúc.** Không dùng extractive span head |
| **LiGT §5** | Giải thích: *"the linearized OCR context could hinder the models' inherent capabilities of understanding semantic properties, since the OCR context lacks natural language structure"* | Cảnh báo: **flatten OCR thành chuỗi làm mất cấu trúc** — phải giữ cấu trúc block/bảng |
| **LiGT §5.5.3** | *"Accuracy scores in Location questions were only around 40%"* | Kỳ vọng thực tế cho câu hỏi vị trí tiếng Việt |
| **LiGT Table 4** | Fully-matched **75.86–76.77** vs Our approach **80.93–81.66** → **~19% đáp án không trích được nguyên văn** | **Trần extractability ~76–81%.** Bất kỳ phương pháp extractive thuần nào cũng bị chặn ở đây |
| **LiGT Table 8** | LayoutHEI: 2 mức 78.36 · **3 mức 79.07 (tốt nhất)** · 4 mức 78.78 · 5 mức 78.32 | ⚠️ Thí nghiệm chính dùng **4 mức — không tối ưu**. Nếu tái lập, thử **3 mức** |
| **LiGT LayoutHEI** | Băm tâm bbox vào phần tư đệ quy qua L mức; token câu hỏi nhận `"0"`; `ω = σ(ρ)`; `E^hash_t = ω ⊙ (1/L) Σ E^{αi}_t`; `E^input_t = E^semantic_t + E^hash_t` | Cơ chế **nhẹ**, cộng vào embedding có sẵn thay vì thêm embedding mới |
| **LiGT §5.5.2** | *"inducing fully new embedding layers to pretrained models might result in incompatibility"* | Bài học thiết kế: **không thêm embedding layer mới** vào model pretrain |

**Cảnh báo về LiGT:** paper này có 2 lỗi số liệu tự mâu thuẫn — Table 3 ghi **68,412** câu còn prose + Table 2 ghi **64,812** (lệch 3,600); và §5.4 claim LiGT "F1 cao nhất" nhưng Table 5 cho thấy **ViT5+U large F1 68.10 > LiGT large 68.09**. Trích phải đối chiếu bảng gốc.

---

## G5. Trần extractability + hallucination chỉ bị chặn một chiều

### Bằng chứng

**LiGT Table 4** — trần khi model hoàn hảo:

| | ANLS | F1 | Acc | EM |
|---|---|---|---|---|
| Fully-matched | 75.86 | 76.17 | 76.77 | 75.98 |
| Our approach | 80.93 | 81.26 | 81.66 | 81.04 |

→ **~19% đáp án không trích được nguyên văn** dù model hoàn hảo. Matching nới chỉ nâng lên ~81%.

**LMDX §3.5** — Grounding Verification:
> *"we look up the corresponding segment in the original document using the segment identifier and verify that the extracted text is exactly included on that segment. The entity is discarded if that verification fails, ensuring LMDX discards all LLM hallucinations."*

Algorithm 2, hai cổng:
1. `if P[j*2] ∉ M then Go to next i` — *"Segment ID is hallucinated. Grounding failure."*
2. `if T not substring of S then Go to next i`
3. Rồi mới `W = W ∪ (S ∩ T)`

**Nhưng:** grounding **chỉ loại được false positive**. Nó **không thể cứu false negative** — nếu model không tìm ra đáp án, không có gì để verify. Và LMDX tự nhận lỗi phổ biến nhất là **OCR gộp dòng**:
> *"A very common error type we observe is caused by OCR lines grouping multiple semantically different segments."*

Ví dụ thật (Appendix A.11): GT `line_item/program_desc` = "Local News 6a-630a" nhưng dự đoán "WJZ Local News 6a-630a" — **cột Channel bị OCR gộp vào cột Description**. Và: *"As LMDX_PaLM 2-S uses only coarse line layout information ([xcenter, ycenter] with 100 quantization buckets), the model fails in these cases."*

**BoundingDocs §5, Table 6** — mặt trái của việc nhồi layout:
> *"Incorporating layout and positional information into the prompt led to improved accuracy across most datasets, but at the cost of a higher percentage of non-parsable responses."*

→ 5.64% lỗi parse chung, **FUNSD 17.79%**. Salvage bằng regex: 5.64% → 1.53%, **nhưng** FUNSD 78.8 → 74.7 và XFUND 71.2 → 70.3.

**BoundingDocs §3.2.1** — lọc bỏ toàn bộ câu abstractive:
> *"we filtered out all questions that can be defined as abstractive... Since our objective is to provide the exact location of each answer within the document, it is essential to retain only extractive questions."*

### Vì sao là gap CHUNG

Cả họ phương pháp extractive bị chặn ở **cùng một trần ~76–81%**. Và cả hai hướng sửa đều có giá:
- Nhồi layout vào prompt → tăng accuracy nhưng **tăng lỗi parse** (BoundingDocs).
- Grounding verification → diệt hallucination nhưng **không cứu được miss** (LMDX).

Không paper nào giải được **false negative** — tức là trường hợp đáp án có thật trong tài liệu nhưng không trích được vì lý do hình thức (OCR gộp dòng, dấu tiếng Việt, đáp án không nằm nguyên văn).

### Chạm đề không

**Có.** Đề cho **OCR sẵn** → trần này **đã được nâng** so với LiGT (không phải tự OCR). Nhưng lỗi **OCR gộp dòng** vẫn còn nguyên trong `ocr/*.json` — đó là lỗi của dữ liệu, không phải của pipeline.

### Phương án áp dụng được

| Lấy từ | Cơ chế | Áp dụng |
|---|---|---|
| **LMDX §3.5** | Grounding Verification 2 cổng | Lọc evidence hallucinated trước khi nộp — **rẻ, chắc chắn có lợi** |
| **LMDX §Limitations** | Cảnh báo line-level không đủ tin | Dùng `cell_annotations.jsonl` (mức cell) thay vì line-level |
| **BoundingDocs §5 + Table 6** | Layout trong prompt → +accuracy, +parse error | **Không nhồi layout vào prompt dạng text.** Dùng bbox có cấu trúc. Đây là lợi thế kiến trúc thật, nên ghi nhận. Số đầy đủ ở **P1** |
| **BoundingDocs §3.2.1** | Lọc abstractive | ⚠️ **Không lặp lại việc này.** Đề có `sum`/`count`/`compare` — lọc abstractive là tự bỏ 3/4 câu hỏi |
| **LiGT Table 4** | Đo trần extractability | Chạy phép đo này trên olp-ai-ptit trước khi chọn kiến trúc |

---

## G6. Nhiễu annotation ở số/tiền/ngày — và metric không phân biệt được lỗi

### Bằng chứng

**BoundingDocs Table 3** — độ chính xác annotation theo loại:

| Loại | Đúng / Tổng | % |
|---|---|---|
| Acronyms | 8/8 | 100% |
| Currency | 20/14 | 70.00% |
| Named entities | 69/47 | 68.12% |
| Dates | 18/12 | 66.67% |
| **Numbers** | **32/15** | **46.88%** |
| Other | 25/10 | 40.00% |
| **Tổng** | 172/106 | **61.63%** |

Nguyên nhân gốc (§3.4):
> *"Numbers exhibit the lowest accuracy rate (46.88%), as numerical values frequently appear in unrelated sections of documents such as page numbers, reference codes, or unrelated quantities."*

Và §3.3: **~20%** trường hợp giá trị được annotate xuất hiện **nhiều hơn một lần** trên cùng trang:
> *"We found that in approximately 20% of cases, the annotated value appeared more than once on the same page."*

**Con số quan trọng nhất của cả mục này** — §3.4, ước lượng lan rộng của lỗi:
> *"The results, reported in Table 3, reveal that approximately 38% of questions with multiple answers per page contain at least one answer that is not logically related to the question. Extrapolating from this finding, we estimate that approximately 7% of all annotations (38% of the 20% with multiple matches) may exhibit this issue."*

→ Tức là **~7% nhãn trong một dataset đã qua kiểm định vẫn sai một cách có hệ thống**, và lỗi đó **không phải ngẫu nhiên** — nó tập trung đúng vào nhóm **số/tiền/ngày**, chính là nhóm chiếm phần lớn câu hỏi `lookup`/`sum`/`argmax` của đề.

Và một lời thú nhận về nhiễm bẩn train/test (§3.3):
> *"out of the 38,515 documents in the training split, 313 originate from the FUNSD/XFUND test sets, accounting for approximately 0.8%."*

→ Dataset dùng làm chuẩn để **đo** localization **cũng có test set rò vào train**. Nghĩa là con số MeanIoU .031/.048 ở §4.6 — và cả bảng DocExplainerV0 dùng lại chính dataset này — **đã bị lạc quan hoá nhẹ**. Con số thật còn thấp hơn.

**Về ANLS:** τ=0.5 **không** được định nghĩa trong paper DocVQA. `grep threshold` trong DocVQA → **0 hit**. Nguồn thật là **ST-VQA (arXiv 1905.13648) §3.4**, và τ áp lên **khoảng cách Levenshtein chuẩn hoá** (distance), không phải similarity: `s = 1 - NL` nếu `NL < τ`, ngược lại `0`.

**Xác nhận chéo:** LiGT §5.2.3 in lại **đúng công thức đó**, độc lập với ST-VQA — nên đây không phải suy đoán từ một nguồn. Cùng một piecewise formula, cùng áp lên distance.

Test ANLS với tiếng Việt (đã chạy):

| Prediction | Gold | ANLS | Vượt τ=0.5? |
|---|---|---|---|
| `Hoa don` | `Hóa đơn` | 0.571 | ✅ |
| `Phong Ke toan` | `Phòng Kế toán` | 0.769 | ✅ |
| `Nguyen Van A` | `Nguyễn Văn A` | 0.833 | ✅ |
| `Tram 110kV Bac` | `Trạm 110kV Bắc` | 0.857 | ✅ |

→ **Mất toàn bộ dấu vẫn đạt 0.571–0.857 — đều vượt τ=0.5 → ăn điểm đầy đủ.**

### Vì sao là gap CHUNG

Ba tầng vấn đề chồng lên nhau, và **cả 10 paper đều không chạm**:

1. **Nhiễu annotation** — BoundingDocs đo được 46.88% trên số, nhưng **không paper nào khác kiểm tra điều này trên dataset của mình**.
2. **Metric không phân biệt lỗi** — ANLS τ=0.5 không tách được "sai chính tả tiếng Việt" khỏi "trả lời đúng". Hệ quả: **không đo được hệ thống nào thực sự hiểu tiếng Việt**.
3. **Không paper nào báo cáo metric table-structure** — Qwen2-VL/Qwen2.5-VL không có TEDS, không có OmniDocBench.

### Chạm đề không

**Có, và đây là gap có tính phương pháp luận nặng nhất.**

- ANLS chiếm **85% điểm** → metric yếu ở đúng chỗ chiếm phần lớn điểm.
- Nếu nhóm tự annotate theo cách "khớp text, lấy mọi lần xuất hiện" thì **lặp lại đúng lỗi BoundingDocs §3.2.2**. Bất kỳ Evidence-F1 nào trên ~0.93 đều nằm trong **vùng nhiễu**.
- **Ngưỡng thực nghiệm cần nhớ:** BoundingDocs đo được **61.63%** annotation đúng trên mẫu kiểm tra, và §3.4 ước lượng **~7% nhãn sai có hệ thống** ngay cả trong dataset đã kiểm định. Nghĩa là nếu Evidence-F1 của nhóm vượt ~0.62 một cách đáng ngờ, phải kiểm tra lại chứ không phải mừng.
- **Đối xứng hai chiều:** con số 7% đó cũng là **trần trên của việc tự chấm mình**. Nếu nhóm tự annotate evidence rồi tự đo, sai số nền ít nhất cùng bậc — nên mọi kết luận phải kèm audit, không chỉ kèm điểm.

### Phương án áp dụng được

| Lấy từ | Cơ chế | Áp dụng |
|---|---|---|
| **ST-VQA §3.4** | Định nghĩa ANLS gốc + τ=0.5 áp lên distance | Viết `anls.py` **đúng chuẩn** — vì `evaluate_predictions.py` của TA Minh không có |
| **BoundingDocs §3.4 + Table 3** | Quy trình đo độ chính xác annotation theo loại | Chạy **audit annotation** trên `labels.jsonl` trước khi tin số |
| **BoundingDocs §3.2.2** | ⚠️ *"all occurrences are considered valid answers"* | **Tránh** cách này khi tự annotate. Nó là nguyên nhân gốc của 46.88% |
| **Peer et al. arXiv 2402.03848** | ANLS\* — biến thể xử lý được nhiều đáp án | Cân nhắc vì đề có `answers[]` nhiều giá trị |
| **OmniDocBench arXiv 2412.07626** | *"VLMs tend to perform worse on tables with merged cells"*; *"table rotation significantly impacts the accuracy of all models"* | Metric table-structure còn trống — nếu đo được, đây là đóng góp riêng |

---

## BẢNG TỔNG HỢP: GAP → PHƯƠNG ÁN

| # | Gap chung | Mức | Paper nào KHÔNG giải được | Phương án lấy từ |
|---|---|---|---|---|
| G1 | Không đo evidence theo protocol multi-box IoU≥0.5 | 🔴 | **cả 10** | LMDX §3.5 + Alg.2 · DocExplainerV0 §4.3 · `cell_annotations.jsonl` |
| G2 | Sinh toạ độ hỏng (.011–.051 vs ngưỡng .5) | 🔴 | DocExplainerV0, BoundingDocs, Qwen2-VL, Qwen2.5-VL | Chọn trong candidate: `cell_annotations.jsonl` + grounding |
| G3 | argmax/argmin/compare/cross_page_sum vắng mặt | 🔴 | **cả 10** (TAPAS thiếu MAX/MIN; LayoutLMv3 extractive-only) | TAPAS soft operators + tách chọn-cell / thi-hành-toán-tử |
| G4 | Tiếng Việt không test hoặc yếu nhất | 🔴 | BoundingDocs, DocLLM, DocVQA, TAPAS, LayoutLMv3, Qwen2.5-VL; Qwen2-VL 73.0 | LiGT Table 5 (extractive thua generative ~20 ANLS) + LayoutHEI |
| G5 | Trần extractability ~76–81% + grounding một chiều | 🟡 | LiGT, LMDX, BoundingDocs | LMDX grounding · BoundingDocs Table 6 (đừng nhồi layout vào prompt) |
| G6 | Nhiễu annotation số/tiền/ngày + ANLS không phân biệt lỗi | 🟡 | **cả 10** | ST-VQA §3.4 · BoundingDocs §3.4 audit · ANLS\* |

**Ngoài 6 gap trên, còn 4 cơ chế lấy thẳng từ paper dùng được ngay** — không gắn với gap nào, xem mục **P1–P4** ngay dưới: P1 (train lệch kiểu câu hỏi) · P2 (thêm attention đa phương thức làm tệ đi) · P3 (bỏ MIM là hỏng training) · P4 (bẫy false-positive của string-search).

---

## PHƯƠNG ÁN RÚT RA TỪ PAPER — DÙNG ĐƯỢC NGAY

Bốn phát hiện **không thuộc gap nào** ở trên, nhưng là **cơ chế cụ thể lấy thẳng từ paper** và áp được vào đề. Đã đối chiếu nguyên văn trong PDF.

### P1. Đừng train một kiểu câu hỏi rồi hy vọng nó chuyển sang kiểu khác

**BoundingDocs Table 6** — ablation theo kiểu câu hỏi (train → test):

| Cấu hình | Weighted Avg ANLS\* | Parse error |
|---|---|---|
| Templ. → Templ. | 91.3 | 0.04% |
| **Templ. → Reph.** | **87.8** ← tệ nhất | 1.62% |
| Reph. → Templ. | 90.7 | 0.04% |
| Reph. → Reph. | 90.6 | 0.04% |
| **Reph. → Reph. + bbox** | **91.6** ← điểm cao nhất | **5.64%** ← parse tệ nhất |
| Reph. → Reph. + bbox **w/regex** | 91.3 | 1.53% |

§4.7 nguyên văn:
> *"the Template-Template configuration demonstrated superior performance by leveraging structured, consistent question patterns... Notably, the Template-Rephrased setup performed least effectively, highlighting the challenges in transitioning from template-trained models to complex question structures."*

**Áp dụng:** olp-ai-ptit có **8 reasoning type với phân bố rất lệch** (`lookup` 2,200 → `cross_page_sum` 46). Nếu nhóm train/few-shot trên vài type dễ rồi đem đi thi, **kết quả sẽ tụt đúng theo pattern Templ.→Reph.** Phải **stratify theo `reasoning_type`** khi chia dev set, không chia ngẫu nhiên.

**Và về regex salvage:** thêm regex hậu xử lý **giảm parse error 5.64% → 1.53% nhưng mất 0.3 ANLS\*** — đồng thời **FUNSD 78.8 → 74.7, XFUND 71.2 → 70.3**. Tức nó **không miễn phí**: đổi một ít accuracy lấy việc gần như không còn output hỏng. Với đề này (nộp JSONL, một dòng hỏng là mất trắng câu đó) → **nên làm**.

### P2. Thêm đường attention đa phương thức có thể làm KẾT QUẢ TỆ ĐI

**DocLLM Table 7** — ablation trên các đường tương tác attention:

| Cấu hình | NTP accuracy |
|---|---|
| T2T (chỉ text-text) | 35.43 |
| T2S + T2T | 38.08 |
| S2T + T2T | 38.05 |
| **S2S + T2T** | **39.12** ← cao nhất |
| T2S + S2S + T2T | 39.06 |
| S2T + S2S + T2T | 39.07 |
| cả bốn đường | 39.02 |

§4.2 nguyên văn:
> *"keeping only the spatial-to-spatial interaction (i.e. s,s = 1) yields the highest NTP accuracy... For all experiments in Section 4, we therefore set s,s = 1, s,t = 0, and t,s = 0."*

→ **Bật thêm đường tương tác chéo đều làm giảm điểm.** Tác giả phải tắt `s,t` và `t,s` mới đạt kết quả tốt nhất.

**Và Table 8** — mục tiêu pretrain quan trọng hơn kiến trúc attention:

| Pretrain objective | NTP accuracy |
|---|---|
| Causal | 32.6 |
| Causal + Spatial | 36.2 |
| **Block Infilling + Spatial** | **39.1** |

**Áp dụng:** nếu ai đó trong nhóm định "sửa attention cho đa phương thức hơn" — **đây là bằng chứng để không làm**, hoặc nếu làm thì **phải ablate từng đường**. Còn **Block Infilling** là mục tiêu pretrain đáng bắt chước nếu tự pretrain.

### P3. Bỏ image-masking là hỏng training, không phải chỉ giảm điểm

**LayoutLMv3 Table 3** — ablation pretrain objective:

| # | Text embed | Params | Objective | FUNSD | CORD | RVL-CDIP | PubLayNet |
|---|---|---|---|---|---|---|---|
| 1 | None | 125M | MLM | 88.64 | 96.27 | 95.33 | — |
| 2 | **Linear** | 126M | MLM | 89.39 | 96.11 | 95.00 | **Loss Divergence** |
| 3 | Linear | 132M | MLM + MIM | 89.19 | 96.30 | 95.42 | — |
| 4 | Linear | 133M | MLM + MIM + WPA | **89.78** | **96.49** | **95.53** | **94.38** |

§3.3 nguyên văn:
> *"We have tried to train the model #2 with learning rates of {1e-4, 2e-4, 4e-4} combined with batch sizes of {16, 32}, but the loss of model #2 did not converge and the mAP score on PubLayNet is near zero."*

**Áp dụng:** MIM (masked image modeling) **không phải trang trí** — thiếu nó thì **loss không hội tụ qua 6 tổ hợp hyperparameter**. Nếu nhóm fine-tune LayoutLMv3/LayoutXLM, **giữ nguyên bộ objective gốc**, đừng gỡ MIM cho nhẹ. Và model #4 (đủ 3 objective) là tốt nhất trên **cả 4 benchmark**.

### P4. ⚠️ String-search đáp án trong OCR có bẫy false-positive 10 điểm

**DocVQA Table 1** — upper bound hai kiểu khớp:

| Kiểu khớp | ANLS (val) | ANLS (test) |
|---|---|---|
| OCR **substring** UB | 85.64 | **87.00** |
| OCR **subsequence** UB | 76.37 | **77.00** |

§5.1 nguyên văn:
> *"OCR substring UB yields more than 85% accuracy... It has a downside that the substring match in all cases need not be an actual answer match. For example if the answer is '2'... it will match with a '2' in '2020' or a '2' in '2pac'."*

**Áp dụng — và đây là cảnh báo trực tiếp cho Ưu tiên 2:** baseline khuyến nghị ở Ưu tiên 2 là **string-search đáp án trong `cell_annotations.jsonl`** — đúng cơ chế mà DocVQA đo được **bẫy 10 điểm** (87.00 vs 77.00).

Nghĩa là **MeanIoU .494 của DocExplainerV0 §4.3 có thể đã bị thổi lên bởi chính chế độ false-positive này**, vì §4.3 mô tả: *"if no full match, fall back to the first word"* — tức khớp mờ rồi vẫn trả box.

**Phải làm:** khớp theo **ranh giới từ / khớp trọn block**, **không** dùng `in` thô. Và khi báo cáo MeanIoU phải **kèm precision** — nếu không, con số .494 không có nghĩa.

**Đây là chỗ nối với G6:** nếu Evidence-F1 đo ra vượt ~0.62 một cách đáng ngờ, **kiểm tra false-positive trước, đừng mừng** — xem G6.

---

## HƯỚNG THỰC HIỆN KHẢ THI

Xếp theo **điểm kỳ vọng / công sức**, cho 4 tuần và làm solo.

### 🥇 Ưu tiên 1 — Dựng metric trước khi dựng model

**Làm gì:** viết `anls.py` (theo ST-VQA §3.4, τ=0.5 trên distance) + `evidence_f1.py` (IoU ≥ 0.5, matching tập hợp nhiều box).

**Vì sao trước:** `evaluate_predictions.py` của TA Minh dùng **exact match** và **không có Evidence-F1**. Không có metric đúng thì mọi cải tiến đều không đo được.

**Công sức:** ~1 ngày. **Rủi ro:** thấp. **Đây là việc không thể bỏ.**

### 🥈 Ưu tiên 2 — Baseline chọn-cell (ăn cả G2 và G3)

**Làm gì:**
1. Với mỗi câu, string-search đáp án trong `cell_annotations.jsonl` → lấy `bbox` mức cell (DocExplainerV0 §4.3, nhưng dùng cell thay vì OCR line).
2. Lọc bằng Grounding Verification (LMDX §3.5): box phải chứa text của đáp án.
3. Với `sum`/`count`/`argmax`/`argmin`/`compare` → **solver thủ tục** trên `row`/`column`/`clean_text` (TAPAS pattern: chọn cell bằng model, thi hành toán tử bằng code).
4. `visual_bold_lookup` → dùng cột **`is_bold`** có sẵn.

**Vì sao:** đây là baseline mà DocExplainerV0 đo được **MeanIoU .494** — **sát ngưỡng 0.5**. Và vì metric là **ngưỡng nhị phân**, siết box một chút là nhiều câu nhảy từ 0 lên full điểm. Đòn bẩy cao nhất trên mỗi giờ công.

**Công sức:** ~3–5 ngày. **Rủi ro:** thấp — không cần train gì.

### 🥉 Ưu tiên 3 — Đo trần trước khi chọn kiến trúc

**Làm gì:** chạy phép đo LiGT Table 4 trên olp-ai-ptit — bao nhiêu % đáp án trích được nguyên văn từ OCR cho sẵn?

**Vì sao:** nếu trần là ~80%, mọi kiến trúc extractive đều bị chặn ở đó. Biết trần rồi mới quyết có cần generative hay không.

**Công sức:** ~0.5 ngày.

### Ưu tiên 4 — Audit annotation (rẻ, phòng ngừa)

**Làm gì:** lặp lại quy trình BoundingDocs §3.4 trên `labels.jsonl`: lấy mẫu, kiểm tra thủ công, phân theo loại đáp án.

**Vì sao:** biết trước vùng nhiễu để không đuổi theo điểm ảo. Ngưỡng tham chiếu: **61.63%** (BoundingDocs).

**Công sức:** ~1 ngày.

### Không nên làm

| Ý tưởng | Vì sao không |
|---|---|
| Hỏi VLM toạ độ trực tiếp | 4 paper đo được .011–.051 — dưới ngưỡng một bậc độ lớn |
| Fine-tune extractive span head (LayoutLMv3-style) | LiGT Table 5: extractive thua generative **~20 ANLS trên tiếng Việt** |
| Lọc bỏ câu abstractive cho dễ | Bỏ luôn 74.7% câu hỏi (sum/count/compare/argmax/argmin) |
| Nhồi layout vào prompt dạng text | BoundingDocs Table 6: tăng lỗi parse lên 5.64% chung, **17.79% FUNGS** |
| Dùng model context ngắn (512/1,024) | Chặn multi-page; DocLLM WTQ thua GPT-4 zero-shot **38.3 điểm** |
| Dùng `evaluate_predictions.py` làm metric chính | Nó là exact match, không phải ANLS; không có Evidence-F1 |

---

## VIỆC CẦN LÀM TIẾP

1. **Tự đọc lại 10 PDF** và đối chiếu từng số trong file này — theo §III.3, đây là bắt buộc trước khi dùng.
2. **Chốt hướng A / B / C** (A = tái lập + đánh giá · B = sửa một điểm yếu · C = hướng nghiên cứu).
3. **Viết `anls.py` + `evidence_f1.py`** — Ưu tiên 1.
4. **Chốt loại output** và ghi vào `Working Files/` — quy chế §II.3 yêu cầu lock trong Tuần 1, đổi hướng phải được TA duyệt trước.
5. Cập nhật Google Form tiến độ **mỗi 3 ngày** (quá 3 ngày → buộc rời chương trình).

---

## NGUỒN

| # | Paper | Nguồn | Section / Bảng đã dùng |
|---|---|---|---|
| 1 | BoundingDocs | IJDAR (2026) 29:447–462 · arXiv 2501.03403v3 | §3.2.1, §3.2.2, §3.3, §3.4, §4.2, §4.6, §4.7, §5 · Table 3, Table 6 |
| 2 | DocExplainerV0 | arXiv 2509.10129v2 | §4.3, §4.4, §5 · Table 1 |
| 3 | DocVQA | arXiv 2007.00398v3 · WACV 2021 | §5.1 · Table 1, Table 3 |
| 4 | TAPAS | arXiv 2004.02349v2 · ACL 2020 | Table 1, Table 6 · Appendix D · Limitations |
| 5 | Qwen2-VL | arXiv 2409.12191v2 | §2.2.1 · Table 2, Table 3, Table 6, Table 7, Table 8 |
| 6 | Qwen2.5-VL | arXiv 2502.13923v1 | §2.2.1, §3.1 · Table 3, Table 5, Table 6 |
| 7 | LiGT / ReceiptVQA | arXiv 2502.19202v2 · IJDAR 2025 | §5.4, §5.5.2, §5.5.3 · Table 2, Table 3, Table 4, Table 5, Table 7, Table 8 · Appendix C, D.2 |
| 8 | LMDX | arXiv 2309.10952v2 · ACL Findings 2024 | §3.2, §3.5 · Algorithm 2 · Table 3, Table 5, Table 8, Table 9 · Appendix A.2, A.11, A.12 |
| 9 | DocLLM | arXiv 2401.00908v1 · ACL 2024 | §4.2 · Table 2, Table 3, Table 4, Table 5, Table 6, Table 7, Table 8 |
| 10 | LayoutLMv3 | arXiv 2204.08387v3 · EMNLP 2022 | §3.3 · Table 1, Table 3 |
| — | ANLS (τ=0.5) | ST-VQA · arXiv 1905.13648 §3.4 | Định nghĩa gốc |
| — | ANLS\* | Peer et al. · arXiv 2402.03848 | Biến thể nhiều đáp án |
| — | OmniDocBench | arXiv 2412.07626 | Table 6 · merged cell, rotation |
| — | Đề bài | `Working Files/reference/exam_question_docvqa.md` | Scoring, IoU ≥ 0.5, 8 reasoning type |
| — | Quy chế | `Working Files/reference/Document hướng dẫn Topic Team.pdf` | §II.3, §II.5, §III.1, §III.3 |
| — | Repo TA Minh | `olp-ai-ptit-2026-preliminary-round/` | **Tài liệu tham khảo — không phải sản phẩm nộp** |

---

## ĐIỂM CẦN XÁC MINH LẠI

| # | Điểm | Trạng thái |
|---|---|---|
| 1 | Tỉ lệ IoU ≥ 0.5 thật của baseline string-search trên olp-ai-ptit | **Chưa đo** — MeanIoU .494 là số của DocExplainerV0 trên dataset khác |
| 2 | Trần extractability trên olp-ai-ptit | **Chưa đo** — ~76–81% là số của LiGT |
| 3 | Độ chính xác annotation `labels.jsonl` | **Chưa audit** |
| 4 | BoundingDocs Table 8 chỉ có ở **arXiv v3**, không có trong bản IJDAR | Nếu trích phải ghi rõ arXiv v3 |
| 5 | LiGT mâu thuẫn 64,812 vs 68,412 câu | Đối chiếu Table 2/3 trước khi trích |
| 6 | LiGT §5.4 claim F1 cao nhất, Table 5 nói ngược | Đối chiếu bảng gốc |
| 7 | LayoutLMv3 prose ghi "78.08 → 78.76" nhưng Table 1 ghi 78.76 → 78.76 | Đối chiếu bảng gốc |
| 8 | Link tải ReceiptVQA | **Chưa xác minh** |
| 9 | MeanIoU **.494** của baseline string-search (DocExplainerV0 §4.3) có bị thổi lên bởi false-positive substring không | **Suy luận của mình, chưa đo** — DocVQA Table 1 chứng minh bẫy này tồn tại (87.00 vs 77.00) nhưng **không** chứng minh .494 mắc bẫy. Muốn khẳng định phải tự đo precision trên olp-ai-ptit |
| 10 | Bảng P1–P4 lấy số từ **dataset khác** (BoundingDocs, DocLLM, LayoutLMv3, DocVQA) | Đúng nguyên văn trong paper, nhưng **chưa đo trên olp-ai-ptit** — coi là giả thuyết, không phải kết luận |
