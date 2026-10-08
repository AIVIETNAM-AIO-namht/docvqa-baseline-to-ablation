# Tổng hợp hạn chế còn tồn tại — 10 paper trong Paper Tracker

**Subtopic:** Hỏi đáp trên ảnh tài liệu (Document Visual Question Answering)
**Ngày tổng hợp:** 2026-09-17
**Phạm vi:** 10 paper đã thu thập trong `Olympic AI - Paper Tracker.xlsx`

---

> ## ⚠️ LƯU Ý VỀ QUY CHẾ TOPIC TEAM
>
> Đây là **bản đồ chỉ chỗ** để thành viên **tự đọc lại paper gốc và tự phân tích** — **không phải** nội dung để dán vào sản phẩm nộp.
>
> Theo *Document hướng dẫn Topic Team*:
> - *"Các output được submit trong Topic Team phải do chính thành viên của nhóm trực tiếp thực hiện."*
> - *"Không sử dụng AI để viết nội dung sản phẩm nộp... AI không được sử dụng để thay thế quá trình tự đọc paper, tự phân tích hoặc tự xây dựng nội dung của nhóm."*
> - *"Khi tham khảo ý tưởng, kiến trúc, hình ảnh hoặc nội dung từ nguồn khác, nhóm cần ghi nguồn đầy đủ."*
>
> Mọi mục dưới đây đều kèm **số section + trích nguyên văn** để tự kiểm chứng lại. Bắt buộc phải tự đọc trước khi dùng.

---

## 0. Trạng thái xác minh

| Mức | Nghĩa | Paper |
|---|---|---|
| ✅ **Đã đọc PDF gốc** | Trích nguyên văn trực tiếp từ file PDF | BoundingDocs, LMDX, DocLLM, LayoutLMv3, LiGT |
| ✅ **Đã fetch HTML/PDF và khớp số** | Đối chiếu từng con số với nguồn | DocExplainerV0, Qwen2-VL, Qwen2.5-VL, DocVQA, TAPAS |
| ❌ **Chưa xác minh** | Không tìm được nguồn | Không có mục nào |

**Hai điểm cần lưu ý về nguồn:**

1. **BoundingDocs Table 8** (phân bố ngôn ngữ) **KHÔNG có trong bản IJDAR đã xuất bản** — chỉ có trong **arXiv v3 (2501.03403v3)**. Nếu trích, phải ghi rõ arXiv v3, không ghi IJDAR.
2. **DocLLM**: con số BizDocs CLS `84.9` và `31.1` nằm ở **hai bảng khác nhau** (Table 5 SDDS và Table 6 STDD). Trích sai bảng sẽ ra kết luận ngược.

---

## 1. BoundingDocs — IJDAR (2026) 29:447–462

**DOI:** 10.1007/s10032-025-00563-5 · **arXiv:** 2501.03403v3
**Tác giả:** Simone Giovannini, Fabio Coppini, Andrea Gemelli, Simone Marinai
**Nguồn đọc:** `Working Files/papers/BoundingDocs - IJDAR 2025.pdf`

### Quy mô
48,151 document / 237,437 page / 249,016 QA pair · ~190 GB · chia 80-10-10 (train 38,516 doc / 198,601 câu; val 4,804 / 24,956; test 4,832 / 25,463) · gộp từ 11 nguồn.

### Hạn chế

| # | Hạn chế | Vị trí | Trích nguyên văn |
|---|---|---|---|
| 1 | **Lọc bỏ toàn bộ câu hỏi abstractive** | §3.2.1 | *"we filtered out all questions that can be defined as abstractive... Since our objective is to provide the exact location of each answer within the document, it is essential to retain only extractive questions."* |
| 2 | **Nhồi layout vào prompt tăng accuracy nhưng tăng lỗi parse JSON** | §5, Table 6 | *"Incorporating layout and positional information into the prompt led to improved accuracy across most datasets, but at the cost of a higher percentage of non-parsable responses."* → 5.64% chung, **FUNSD 17.79%** |
| 3 | **Annotation số chỉ đúng 46.88%** — thấp nhất mọi loại | §3.4, Table 3 | *"Numbers exhibit the lowest accuracy rate (46.88%), as numerical values frequently appear in unrelated sections of documents such as page numbers, reference codes, or unrelated quantities."* |
| 4 | **Nguyên nhân gốc của #3:** khớp bằng Jaccard nên mọi lần xuất hiện đều được coi là đáp án đúng | §3.2.2 | *"If the answer is found in multiple locations on the page through this procedure, all occurrences are considered valid answers."* → **~7% annotation có thể sai** |
| 5 | **Oracle setup** — chỉ đưa trang chứa đáp án vào model | §4.2 | *"only the page containing the answer is provided as input to the model... serving as a theoretical upper bound on performance"* |
| 6 | **Localization gần như bằng không** | §4.6 | *"Claude 4 Sonnet achieves an average IoU of 0.031 on the BoundingDocs test set, while Qwen2.5-VL-7B reaches 0.048... their capacity to indicate the precise location of the answer is effectively nonexistent, which significantly undermines the interpretability of their responses."* |
| 7 | **Không so sánh được với benchmark khác** — dùng ANLS\* chứ không phải ANLS | §4.1 | *"these results are not directly comparable to established benchmarks (e.g., DocVQA or DUDE)"*; *"comparisons between different model types (e.g., LLMs vs. vision LLMs) should be avoided."* |
| 8 | **Tiếng Anh chiếm 93.31%**; phần phi tiếng Anh chỉ từ XFUND, câu hỏi **dịch tự động**; **không có tiếng Việt** | Table 8 (**arXiv v3**) | English 232,362 (93.31%) · Italian 3,857 (1.55%) · Spanish 2,753 (1.11%) · French 2,176 (0.87%) · German 2,564 (1.03%) · Portuguese 3,743 (1.50%) · Chinese 1,116 (0.45%) · Japanese 445 (0.18%) · **Total 249,016** |
| 9 | **85% câu hỏi là template rồi cho LLM viết lại** | §3.2.3–3.2.4 | Template: `What is the [key name]?`; *"We manually refined around 10 keys per dataset."*; *"This raised concerns that fine-tuning an LLM on these questions could introduce bias, potentially leading to poor performance on questions written by humans"* |
| 10 | **Lệch nguồn cực mạnh** | Table 2 | FATURA: 102,403 / 249,016 câu hỏi (**41%**) từ 10,000 trang · Deepform: 24,345 / 48,151 document (**51%**) |
| 11 | Fine-tune chỉ **10%** train split | §4.2 | — |
| 12 | Áp Amazon Textract OCR cho **mọi** dataset bất kể đã có OCR | §3.2.1 | *"regardless of whether they already contained OCR data"* |
| 13 | Thông tin trong document bị dùng phí | §3.5 | *"the potential amount of information present in the documents is underutilized, as the annotated fields are few compared to the entire body of the documents."* |
| 14 | Nhiễm bẩn tập train | — | 313 / 38,515 document train lấy từ test set FUNSD/XFUND (**~0.8%**, có công bố) |

### Câu hỏi mở chính paper tự nêu (§5)
*"whether images can fully replace textual content in prompts, whether bounding boxes remain essential even when using images, and how different modalities interact to enhance model performance."*

### Điểm yếu về annotation (§3.4)
- **~20%** trường hợp giá trị được annotate xuất hiện **nhiều hơn một lần** trên cùng trang
- **~38%** số câu hỏi có nhiều đáp án/trang chứa **ít nhất một đáp án không liên quan logic** tới câu hỏi
- **~7%** tổng số annotation có thể mắc lỗi này
- Độ chính xác theo loại: Acronyms **100%** · Named entities **68.12%** · Currency **70.00%** · Dates **66.67%** · Numbers **46.88%** · Other **40.00%**
- Mẫu kiểm tra: 106/172 = **61.63%**

---

## 2. DocExplainerV0 — arXiv 2509.10129

**Tên đầy đủ:** *Towards Reliable and Interpretable Document Question Answering via VLMs*
**Paper quan trọng nhất cho bài toán của nhóm.**

### Table 1 — đã khớp từng con số với nguồn

| Model | Prompt | ANLS | MeanIoU |
|---|---|---|---|
| SmolVLM-2.2B | Zero-shot | .527 | .011 |
| SmolVLM-2.2B | Anchors | .543 | .026 |
| SmolVLM-2.2B | CoT | .561 | .011 |
| Qwen2-VL-7B | Zero-shot | .691 | .048 |
| Qwen2-VL-7B | Anchors | .694 | .051 |
| Qwen2-VL-7B | **CoT** | **.720** ← ANLS tốt nhất | **.038** ← IoU tệ nhất |
| Claude Sonnet 4 | Zero-shot | .737 | .031 |
| SmolVLM + DocExplainer | Zero-shot | .572 | .175 |
| Qwen2-VL + DocExplainer | Zero-shot | .689 | .188 |
| SmolVLM + Naive OCR | Zero-shot | .556 | .405 |
| **Qwen2-VL + Naive OCR** | Zero-shot | .690 | **.494** |

### Hạn chế

- **VLM không sinh được toạ độ:** *"VLMs are unable to provide the position of the value extracted from the document"*
- **Regressor học được vẫn thua baseline OCR ~3 lần:** *"DocExplainer's results are still very far from the OCR-based baseline (approximately three times less effective)"* (MeanIoU .188 vs .494)
- **Trade-off ngược chiều ANLS ↔ localization:** CoT cho ANLS cao nhất (.720) nhưng IoU thấp nhất (.038). Chuyển sang DocExplainer mất ~3 điểm ANLS để đổi ~15 điểm IoU.
- **Phạm vi bị giới hạn:** chỉ xét *"questions where the answer can be clearly localized within a single bounding box"*, loại bỏ *"cases that require reasoning over multiple elements or regions"*
- **Tự nhận chưa phải giải pháp:** *"Rather than providing a complete solution, our goal was to establish a benchmark"*

---

## 3. DocVQA — WACV 2021

**arXiv:** 2007.00398

- **Thiên lệch nguồn dữ liệu:** toàn bộ ảnh từ **UCSF Industry Documents Library** — 6,071 tài liệu ngành thuốc lá / thực phẩm / dược / hóa dầu, giai đoạn 1900–2018. Đây là kho tài liệu litigation, **không phải phân bố tài liệu thực tế**.
- **Chọn trang có chủ đích:** *"We also prioritized pages with tables, forms, lists and figures over pages which only have running text"* → không phải mẫu ngẫu nhiên.
- **Loại bỏ ảnh chất lượng thấp:** *"Majority of documents in the library are binarized"* và *"we did not want poor image quality to be a bottleneck"* → **benchmark đánh giá cao hơn chất lượng scan thực tế** trên bản scan hành chính.
- **Ép extractive nhưng tự mâu thuẫn:** worker được yêu cầu hỏi câu *"can be answered using text present in the image"* và *"enter the answer verbatim"* — nhưng paper lại viết *"Answers... are inherently open ended"*.
- **Human upper bound không sạch:** đáp án test lấy từ *"a few volunteers from our institution"* — khác pool crowdworker viết câu hỏi.
- Cap **10 câu/trang**; **chỉ tiếng Anh**.
- **ANLS không được định nghĩa trong paper này** — paper không nêu giá trị τ nào. τ=0.5 đến từ **ST-VQA (arXiv 1905.13648)**.

---

## 4. TAPAS — ACL 2020

**arXiv:** 2004.02349 · **Có mục "Limitations" riêng**

- **Chỉ một bảng, phải fit memory:** *"our model would fail to capture very large tables, or databases that contain multiple tables"*
- **Chỉ chọn cell trong MỘT cột:** *"first selects a single column and then cells from within that column only"* → câu hỏi trải 2 cột không biểu diễn được
- **Toán tử đóng và nhỏ:** {SUM, COUNT, AVERAGE, NONE}. **Không tính được hiệu/hiệu số.**
- **Không số học trên giá trị cell** — error analysis WikiTQ (n=200):
  - 2% *"the answer is the difference between scalars, so it is outside of the model capabilities"*
  - 16% *"the gold denotation has a textual value that does not appear in the table"*
  - 10% *"the table is too big to fit in 512 tokens"*
  - 13% *"TaPas selected no cells"*
- **Cap 512 token**; số bị tokenize mất mát (xử lý qua rank id, **không phải số học**)
- **Trần weak supervision:** với gold operator + gold cell, SQA lên **86.4** so với **67.2** công bố

---

## 5. Qwen2-VL — arXiv 2409.12191

- **Không có Limitations section.**
- Toạ độ **chuẩn hoá [0,1000)** → sai prior cho box chặt.
- **MTVQA chỉ 30.9** (bản 72B) trong khi OCRBench 877 trên cùng model — tín hiệu rõ nhất về yếu phi tiếng Anh.
- **Không báo cáo benchmark table-structure nào** (không TEDS, không OmniDocBench).
- Blog kỹ thuật tự nhận: *"relatively weak in tasks involving counting, character recognition, and 3D spatial awareness"*.
- Grounding chỉ đo trên **RefCOCO** — benchmark kiểu detection, tolerance rộng, **không đo độ chính xác box chặt**.

---

## 6. Qwen2.5-VL — arXiv 2502.13923

- **Không có Limitations section**; Conclusion không có future work.
- **Đổi sang toạ độ tuyệt đối** vì *"relative coordinates fail to effectively represent the original size and position of objects"* — **nhưng RefCOCO lại THẤP HƠN Qwen2-VL cả 3 split**: 92.7 / 94.6 / 89.7 vs 93.2 / 95.3 / 90.7 → **không chứng minh được cải thiện localization**.
- Pretrain *"primarily composed of Chinese and English"*; **không báo cáo metric tiếng Việt nào**.
- OCRBench_v2 chỉ **61.5 (en)**; OCRBench v1 gần như đứng yên (877→885); DocVQA **giảm nhẹ** 96.5→96.4.
- **OmniDocBench edit distance 0.226 (en)** — lỗi parse tài liệu thật còn đáng kể.
- Tự nhận về CoT: *"Intermediate reasoning steps may fail to adequately integrate visual information, either by ignoring relevant visual cues or misinterpreting them"*.
- **Box drift là failure mode có thật**: cộng đồng báo tham số `max_pixel` mặc định gây *"bbox shiftting"*.

---

## 7. LiGT / ReceiptVQA — arXiv 2502.19202 (IJDAR 2025)

**Tự phê bình rõ nhất trong 10 paper.**

- **KHÔNG sinh bounding box, KHÔNG đánh giá localization** → đóng góp **0** cho thành phần Evidence-F1.
- **Trần OCR-extractability: chỉ 75.98% đáp án khớp hoàn toàn trong OCR** (81.04% nếu dùng matching nới) → **~19–24% đáp án không trích được dù model hoàn hảo**.
- Input cap **180 token** (câu hỏi + OCR linearized) — quá chặt cho văn bản hành chính nhiều bảng.
- **Location type chỉ ~40% accuracy**, Quantity ~60%.
- **Không có xử lý lỗi OCR tiếng Việt** — không dấu, không chuẩn hoá tone mark, không segmentation.
- Tự nhận: *"our dataset may not be sufficient to reflect real-world scenarios"*; *"our model has not provided exclusive solutions for current problems that the baseline models have faced"*; *"there exists imbalances in question types and answer types"*.
- **Mâu thuẫn số liệu:** phần prose + Table 2 ghi **64,812** QA, Table 3 ghi **68,412** → lệch 3,600.
- **Kết quả Table 5 mâu thuẫn claim:** ViT5+U large F1 **68.10** > LiGT large **68.09**.

### ⭐ Bằng chứng mạnh nhất cho lựa chọn kiến trúc (Table 5, đã đọc lại trực tiếp)

So sánh **extractive vs generative trên tiếng Việt**:

| Nhóm | Model | ANLS | F1 | Acc |
|---|---|---|---|---|
| Extractive | LayoutXLM base | **59.11** | 55.45 | 53.05 |
| Extractive | PhoBERT base | **61.39** | 57.55 | 54.91 |
| Extractive | LiLT[PhoBERT] base | 59.87 | 56.29 | 54.05 |
| Generative | ViT5 base | 78.08 | 67.04 | 61.82 |
| Generative | **ViT5+U base** | **78.98** | 67.89 | 62.46 |
| Generative | LiGT (Ours) base | 78.78 | 67.9 | 62.63 |
| Generative | LiGT large | 78.64 | 68.09 | 63.02 |

**Chênh ~20 điểm ANLS giữa extractive và generative trên tài liệu tiếng Việt.**

Nhận định nguyên văn của tác giả:
> *"all large extractive models performed considerably worse than their base versions, which is not a regular phenomenon in NLP tasks. For this reason, we speculate that the linearized OCR context could hinder the models' inherent capabilities of understanding semantic properties, since the OCR context lacks na[tural language structure]."*

---

## 8. LMDX — arXiv 2309.10952 (ACL Findings 2024)

**Có mục "Limitations" riêng + Appendix A.11 "Error analysis"**

- **Chỉ text, không có ảnh:** *"LMDX's input is text lines and their bounding boxes, usually coming from OCR. This means that LMDX can not extract non-textual entities (e.g. checkboxes, signatures, logos, etc). This also limits performance in high-data scenarios, as all page image information is discarded. Furthermore, such input means that LMDX is sensitive to errors from the OCR process (wrong reading order, incorrect line grouping, undetected text and erroneously recognized characters)."*
- **Localization chỉ tới mức dòng:** *"LMDX's localization mechanism is applied at the line level... If the entity text appears multiple times on the line, we don't have a definitive way to choose the correct text. Thus, LMDX's localization and bounding boxes are not reliable beyond line-level granularity."*
- **Toạ độ thô:** 2 coordinate `[xcenter, ycenter]` với **B = 100 quantization buckets** (Appendix A.12) → thô hơn nhiều so với ngưỡng IoU ≥ 0.5.
- **Token budget:** input **6144** / output **2048**.
- **Chia chunk theo trang → cross-page nằm ngoài thiết kế:** *"The decision to first divide the document by page stems from the observation that entities rarely cross page boundaries"*
- **Lỗi phổ biến nhất là OCR gộp dòng:** *"A very common error type we observe is caused by OCR lines grouping multiple semantically different segments."*
  - Ví dụ thật (A.11): GT `line_item/program_desc` = "Local News 6a-630a" nhưng dự đoán "WJZ Local News 6a-630a" — **cột Channel bị OCR gộp vào cột Description**.
  - Ví dụ 2: nhầm giữa hai key liền kề "Invoice Period" và "Flight Dates".
  - *"As LMDX_PaLM 2-S uses only coarse line layout information ([xcenter, ycenter] with 100 quantization buckets), the model fails in these cases, which is a current limitation of LMDX."*
- **Hallucination chỉ bị chặn bằng hậu kiểm, không phải model tự tránh:** *"we discard any prediction whose text does not appear on the specified segment, ensuring we discard all hallucination"*
- **Latency** (Table 8, median ms): LayoutLMv3 GPU-T4 **30 ms** / CPU 648 ms · Donut GPU-T4 620 ms / CPU 14,392 ms · **LMDX_Gemini Pro trên TPU 3,653 ms** (95th pct 7,102 · 99th 8,345)
- **Sụp ở chế độ ít dữ liệu** (Table 3, CORD Micro-F1 theo số doc train |D|): LMDX 66.95 / 90.02 / 91.40 / 91.48 / 93.40 / 94.51 · LayoutLMv3 **0.00** / 74.04 / 85.78 / 90.39 / 93.59 / 95.66 · Donut **0.00** / 26.15 / 65.68 / 71.81 / 75.85 / 81.55
- **Template shift:** *"LMDX_PaLM 2-S has a drop less than 5% Micro-F1 on Unseen Template compared to Single Template across data regimes, while LayoutLMv2 see a drop between 19% and 27%."*

---

## 9. DocLLM — arXiv 2401.00908 (ACL 2024)

- **Không có Limitations section.** Tự nhận duy nhất, ở §7 Conclusions: *"In future work, we plan to infuse vision into DocLLM in a lightweight manner."*
- **Không có image encoder:** *"Unlike existing multimodal LLMs, DocLLM strategically omits costly image encoders, instead prioritizing bounding box information"* → modality chỉ **T+L**, **không thấy được con dấu đỏ, chữ ký, checkbox, chữ viết tay**. Văn bản hành chính Việt Nam thì đầy con dấu và chữ ký.
- **Context length 1,024 token** — trần cứng nhất: *"The maximum sequence length, or context length, is consistently set to 1,024 for both versions during the entire training process."* (Table 4: Max context length 1,024 cho cả 1B và 7B) → **cấm luôn multi-page**.
- **Điểm yếu bảng biểu lộ rõ** — Table 5 (SDDS), đã xác minh:

  | Dataset | GPT-4+OCR (ZS) | DocLLM-7B (T+L) | Chênh |
  |---|---|---|---|
  | **WTQ** (Accuracy) | **65.4** | **27.1** | **−38.3** |
  | TabFact | 77.1 | 66.4 | −10.7 |
  | DocVQA | 82.8 | 69.5 | −13.3 |
  | DUDE | 54.6 | 47.2 | −7.4 |
  | KLC | 45.9 | **60.3** | +14.4 |
  | CORD | 58.3 | **67.4** | +9.1 |
  | FUNSD | 37.0 | **51.8** | +14.8 |
  | SROIE | 90.6 | **91.9** | +1.3 |
  | VRDU a.-b. | 43.7 | **88.8** | +45.1 |

  → Trên benchmark **table-only** (WTQ), DocLLM **thua GPT-4 zero-shot 38 điểm** dù GPT-4 không có layout. Nhất quán với trần 1,024 token — câu hỏi bảng cần nhiều dòng trong context.
- **Sụp ở held-out classification** — Table 6 (STDD), đã xác minh:

  | Task | GPT-4+OCR (ZS) | DocLLM-7B | DocLLM-1B |
  |---|---|---|---|
  | DocVQA | 82.8 | 63.4 | 53.5 |
  | KLC | 45.9 | **49.9** | 40.1 |
  | BizDocs VQA | 76.4 | 73.3 | 65.5 |
  | BizDocs KIE | 66.1 | **72.6** | 63.0 |
  | **BizDocs CLS** | 84.9 | **31.1** | **20.8** |

  ⚠️ **Lưu ý trích dẫn:** BizDocs CLS `84.9` (GPT-4) và `31.1` (DocLLM-7B) nằm ở **Table 6**, không phải Table 5. Ở **Table 5 (SDDS)**, DocLLM-7B đạt BizDocs CLS **99.4** — tức là *thắng*. Trích sai bảng sẽ ra kết luận ngược hoàn toàn.
- **OCR engine chưa chốt:** *"the choice of OCR engines to obtain such cohesive blocks remains an open area for exploration. Practical comparisons with various OCR engines and/or layout parsers are left as future work, as LayoutLMs underscore the importance of accurate OCR for improved VQA results."*
- **Held-out quá mỏng:** *"Due to the high cost of instruction-tuning, we were not able to run additional experiments with different held-out datasets."*
- **Phụ thuộc hyperparameter λ:** *"keeping only the spatial-to-spatial interaction (i.e. λs,s = 1) yields the highest NTP accuracy... the vanilla text-only self-attention mechanism yields the lowest NTP accuracy."*
- **Dữ liệu pretrain chỉ tiếng Anh** (Table 2): CDIP 5,092,636 doc / 16,293,353 page / 3,637,551,478 token + DocBank 499,609 / 499,609 / 228,362,274 → **tổng 5,592,245 doc / 16,792,962 page / 3,865,913,752 token**.
- **Instruction-tuning không có tiếng Việt** (Table 3): VQA 145,090/24,347 · NLI 104,360/12,720 · KIE 236,806/38,039 · CLS 149,627/21,813 → **tổng 635,883 train / 96,919 test**.
- **Cấu hình:** DocLLM-1B = Falcon-1B, 24 layer, hidden 1,536 · DocLLM-7B = Llama2-7B, 36 layer, hidden 4,096. Train trên 8×24GB A10g (7B) / 1×24GB A10g (1B); 1 epoch pretrain + 3 epoch instruction-tuning.
- **BizDocs chưa public** → kết quả STDD **không tái lập được đầy đủ**: *"is a collection of business entity filings that is due to be released publicly"*.

---

## 10. LayoutLMv3 — arXiv 2204.08387 (EMNLP 2022)

- **Không có Limitations section.** §5 "CONCLUSION AND FUTURE WORK" chỉ nói: *"In future research, we will investigate scaling up pre-trained models so that the models can leverage more training data to drive SOTA results further. In addition, we will explore few-shot and zero-shot learning capabilities to facilitate more real-world business scenarios in the Document AI industry."* → ngầm thừa nhận **cần nhiều dữ liệu supervised cho mỗi task**, chưa chạy được few/zero-shot.
- **Sequence length L = 512:** *"we tokenize the text sequence with Byte-Pair Encoding (BPE) with a maximum sequence length L = 512"* → 512 là trần cứng cho text + layout, và **image patch dùng chung budget này**.
- **⭐ Extractive-only head — mismatch quyết định:** *"We formalize this task as an extractive QA problem, where the model predicts start and end positions by classifying the last hidden state of each text token with a binary classifier."* → **chỉ trả về span liên tục của input token**, không thể sinh `sum`, `count`, `argmin`/`argmax` hay bất kỳ đáp án nào không nằm nguyên văn trong text.
- **Chỉ tiếng Anh:** pretrain trên **IIT-CDIP Test Collection 1.0** (11M ảnh, khởi tạo từ **RoBERTa** — tiếng Anh); image tokenizer từ DiT với vocab 8,192.
  - **"XFUND" → 0 hit trong toàn paper** → **không có đánh giá đa ngữ**.
  - Chỉ có một kết quả phi tiếng Anh ở appendix: LayoutLMv3-Chinese_BASE train trên 50M trang tiếng Trung, EPHOIE mean F1 99.21.
  - **Tiếng Việt: không được đề cập.**
- **Phụ thuộc OCR:** *"We use Microsoft Read API to extract text and bounding boxes from images and use heuristics to find given answers in the extracted text as in LayoutLMv2."* — lỗi OCR truyền thẳng vào model, **không có đường dự phòng từ ảnh gốc**.
- **Layout detection yếu** — OmniDocBench (arXiv 2412.07626) Table 6, mAP trung bình: **LayoutLMv3 (RoBERTa-B, 138.4M params) = 28.84** vs **DocLayout-YOLO v10m (19.6M) = 47.38** → **thua một model nhỏ hơn 7 lần**.
  - Theo loại trang: Book 42.12 · Slides 13.63 · Research Report 43.22 · Textbook 21.00 · **Exam Paper 5.48** · Magazine 31.81 · Academic Literature 64.66 · **Notes 0.80** · Newspaper 30.84
- **Kết quả công bố:** DocVQA ANLS **83.37** (LARGE) · FUNSD F1 92.08 · CORD 97.46 · RVL-CDIP 95.93 · PubLayNet 95.1 mAP. Phân vùng DocVQA dùng: 10,194 / 1,286 / 1,287 ảnh và 39,463 / 5,349 / 5,188 câu.

### Bổ sung từ OmniDocBench (arXiv 2412.07626)
- *"Several Vision Language Models (VLMs) tend to perform worse on tables with merged cells, but colored backgrounds do not significantly impact table recognition accuracy"*
- *"table rotation significantly impacts the accuracy of all models"*
- *"Almost all models have lower recognition accuracy in Chinese compared to English"*
- *"VLMs, however, struggle with high-density documents like newspapers due to limitations in input resolution and token length"*
- **Loại trừ khỏi metric:** header, footer, số trang, footnote, caption của figure/table/footnote → tức là bỏ đúng những vùng mà văn bản hành chính Việt Nam dùng để **tham chiếu chéo**.

---

# TỔNG HỢP XUYÊN PAPER

## A. Hạn chế đề olp-ai-ptit đã tự động giải quyết

| Hạn chế | Paper | Vì sao đã được giải |
|---|---|---|
| OCR là nguồn lỗi / phải tự OCR | LMDX, DocLLM, LayoutLMv3, LiGT, BoundingDocs | **OCR + bbox được cho sẵn** trong `ocr/*.json` |
| Trần OCR-extractability 75.98% | LiGT | Không phụ thuộc OCR tự sinh |
| Lỗi parse JSON khi nhồi bbox vào prompt (5.64% chung, 17.79% FUNSD) | BoundingDocs | Pipeline dùng bbox có cấu trúc, không nhồi vào prompt. **Đây là lợi thế kiến trúc thật, nên ghi nhận trong báo cáo** |
| VLM sinh toạ độ sai (IoU .011–.051) | DocExplainerV0, BoundingDocs, Qwen2-VL, Qwen2.5-VL | Chọn trong OCR block có sẵn → .494, sát ngưỡng 0.5 |
| Toạ độ thô: 100 buckets / [0,1000) | LMDX, Qwen2-VL | bbox normalized liên tục trong `[0,1]` |
| Context cap 512 / 1,024 | LayoutLMv3, TAPAS, DocLLM | Không dùng các model đó |
| Extractive-only head không làm được sum/count/argmin | LayoutLMv3 | Solver thủ tục theo `reasoning_type` |
| Oracle setup (chỉ đưa trang chứa đáp án) | BoundingDocs | Đề cho toàn bộ document (1–2 trang) — **khó hơn**, không phải dễ hơn |
| Chỉ một bảng / một cột | TAPAS | Pipeline có `table_blocks()` tách theo bảng |

## B. Hạn chế CÒN SỐNG với olp-ai-ptit

| Hạn chế | Mức độ | Ghi chú |
|---|---|---|
| **Chỉ tiếng Anh** (BoundingDocs 93.31%, DocVQA, TAPAS, DocLLM, LayoutLMv3) | 🔴 Cao | Tiếng Việt + dấu là vùng **chưa có benchmark nào**. Cơ hội tạo đóng góp riêng. |
| **ANLS không phân biệt được chính tả tiếng Việt** (đã test) | 🔴 Cao | Mất **toàn bộ** dấu vẫn đạt ANLS **0.71–0.86** — đều vượt τ=0.5 → **ăn điểm đầy đủ**. Hệ quả: không đo được hệ thống nào hiểu tiếng Việt thật. Ảnh hưởng 85% điểm. |
| **Nhiễu annotation trên số/tiền/ngày** (46.88% / 70.00% / 66.67%) | 🔴 Cao | Nếu tự annotate theo cách "khớp text, lấy mọi lần xuất hiện" thì lặp lại đúng lỗi BoundingDocs. **Bất kỳ Evidence-F1 nào trên ~0.93 đều nằm trong vùng nhiễu.** |
| **Multi-table / multi-page ngoài input contract** | 🟡 TB | TAPAS 1 bảng · LMDX no-cross-page · DocLLM 1024 token. Văn bản hành chính VN nhiều bảng nhiều trang. Đề có `cross_page_sum` (46 câu). |
| **Câu hỏi cần tính toán ngoài SUM/COUNT/AVG** | 🟡 TB | TAPAS không làm được. `compare` (1,722 câu) nằm đúng vùng này. |
| **Localization chỉ tới mức dòng** | 🟡 TB | LMDX line-level; ngưỡng IoU ≥ 0.5 của đề cần mức **cell**. |
| **Không paper nào báo cáo metric table-structure** | 🟡 TB | Không TEDS, không OmniDocBench ở Qwen2-VL/Qwen2.5-VL. Vùng đo lường còn trống. |
| **Bảng có merged cell** | 🟡 TB | OmniDocBench: *"VLMs tend to perform worse on tables with merged cells"*. Trùng khớp với gap đã tìm thấy trong repo TA Minh. |

## C. Kết luận quan trọng nhất

**1. Evidence là bài toán SELECTION, không phải GENERATION.**
Cả 4 paper sinh toạ độ đều hội tụ: VLM sinh toạ độ đạt IoU **.011–.051** — **dưới ngưỡng 0.5 của đề một bậc độ lớn**. Chọn trong OCR block có sẵn đạt **.494**, sát ngưỡng. → **Không bao giờ hỏi VLM toạ độ; luôn chọn trong candidate có sẵn.**

**2. Kiến trúc extractive là bẫy đã được đo.**
LiGT Table 5 trên **tiếng Việt**: extractive (LayoutXLM 59.11) thua generative (ViT5+U 78.98) **~20 điểm ANLS**. Pipeline solver thủ tục không nằm ở either extreme nhưng **không dùng extractive span head** → đã né đúng cái bẫy này.

**3. Bảng có merged cell là điểm yếu được dự báo độc lập bởi cả literature lẫn thực nghiệm.**
OmniDocBench nói VLM yếu với merged cell. Gap trong repo TA Minh cho thấy entity trải nhiều physical row là tín hiệu mạnh nhất của lỗi chọn dòng. **Hai nguồn độc lập chỉ cùng một chỗ.**

---

# VIỆC CẦN LÀM TIẾP

## Hai câu còn treo

1. **Chốt hướng A / B / C**
   - **A** — Tái lập + đánh giá
   - **B** — Sửa một điểm yếu *(đang nghiêng về hướng này)*
   - **C** — Hướng nghiên cứu

   Cơ sở cho **B**: trong repo TA Minh, localization đúng **100%** nhưng **chọn dòng sai 403/403**. Oracle cho thấy khi số physical cell của entity khớp → accuracy **95.98%**; khi lệch → **đúng 0.00%**. Sửa hết 403 case → **+3.66% accuracy tổng**, cộng tối đa **+0.55%** từ Evidence-F1.

2. **Đã có data của olp-ai-ptit local chưa?**
   Đã kiểm: **không có thư mục `data/` nào**. `.gitignore` dòng 207–209 chặn `DocViVQA/data/`, `DocViVQA/outputs/`, `DocViVQA/artifacts/models/*.pt` → **một bản clone sạch không chạy được gì cả**.

## Việc hành chính
- Cập nhật tiến độ Google Form **mỗi 3 ngày** (quy chế: quá 3 ngày không cập nhật → buộc rời chương trình)
- Cuối mỗi tuần: đẩy một bản kết quả vào `Working Files/`
- Ghi chú nguồn gốc: repo của TA Minh là **tài liệu tham khảo**, **không phải** sản phẩm nộp của nhóm

---

# NGUỒN

| # | Paper | Nguồn |
|---|---|---|
| 1 | BoundingDocs | IJDAR (2026) 29:447–462 · DOI 10.1007/s10032-025-00563-5 · arXiv 2501.03403v3 |
| 2 | DocExplainerV0 | arXiv 2509.10129 |
| 3 | DocVQA | arXiv 2007.00398 · WACV 2021 |
| 4 | TAPAS | arXiv 2004.02349 · ACL 2020 |
| 5 | Qwen2-VL | arXiv 2409.12191 |
| 6 | Qwen2.5-VL | arXiv 2502.13923 |
| 7 | LiGT / ReceiptVQA | arXiv 2502.19202 · IJDAR 2025 |
| 8 | LMDX | arXiv 2309.10952 · ACL Findings 2024 |
| 9 | DocLLM | arXiv 2401.00908 · ACL 2024 |
| 10 | LayoutLMv3 | arXiv 2204.08387 · EMNLP 2022 |
| — | ANLS (τ=0.5) | ST-VQA · arXiv 1905.13648 |
| — | ANLS\* | Peer et al. · arXiv 2402.03848 |
| — | OmniDocBench | arXiv 2412.07626 |
| — | M3DocRAG | arXiv 2411.04952 |
| — | Đề bài | `Working Files/reference/exam_question_docvqa.md` |
| — | Quy chế | `Working Files/reference/Document hướng dẫn Topic Team.pdf` |
