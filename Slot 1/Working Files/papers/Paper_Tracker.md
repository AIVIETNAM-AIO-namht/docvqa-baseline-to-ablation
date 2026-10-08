# Olympic AI — Paper Tracker (Hỏi đáp trên ảnh tài liệu)

Tổng hợp 10 paper, xuất từ `Olympic_AI_-_Paper_Tracker.xlsx`. Mỗi paper có 1 folder con tương ứng trong thư mục `paper/`.

---

## 1. BoundingDocs: a Unified Dataset for Document Question Answering with Spatial Annotations

- **Link Paper:** https://doi.org/10.1007/s10032-025-00563-5
- **Năm:** 2026
- **Venue / Journal:** International Journal on Document Analysis and Recognition (IJDAR)
- **Rank:** Other
- **Mức độ liên quan:** Direct
- **Bài toán chính:** Document Question Answering cần vừa trả lời đúng vừa xác định chính xác vùng bằng chứng trên ảnh tài liệu.
- **Phương pháp chính:** Hợp nhất nhiều dataset Document AI thành QA; cung cấp OCR và bounding box chính xác của answer; đánh giá nhiều prompting strategies.
- **Cải tiến chính:** Bổ sung spatial annotations để biến QA tài liệu thành bài toán answer + evidence localization có thể kiểm chứng.
- **Kết quả chính:** Cho thấy thông tin bounding box/prompting phù hợp giúp open-weight models hiểu tài liệu tốt hơn.
- **Học được gì từ paper?:** Hiểu cách gắn câu trả lời với vùng chứng cứ thay vì chỉ sinh text.
- **Có thể áp dụng gì cho topic?:** Áp dụng trực tiếp cho Hỏi đáp trên ảnh tài liệu: output gồm answer và danh sách vùng bằng chứng.
- **Ghi chú / Câu hỏi:** Olympic AI — Hỏi đáp trên ảnh tài liệu

> Thư mục: `paper/01-BoundingDocs/`

---

## 2. LMDX: Language Model-based Document Information Extraction and Localization

- **Link Paper:** https://arxiv.org/pdf/2309.10952
- **Năm:** 2024
- **Venue / Journal:** ACL Findings
- **Rank:** Top Conference
- **Mức độ liên quan:** Direct
- **Bài toán chính:** Trích xuất thông tin & định vị câu trả lời/bằng chứng trên tài liệu bằng LLM mà không bị ảo giác tọa độ.
- **Phương pháp chính:** Quantize tọa độ OCR thành bucket XX|YY; ép LLM trích xuất segment; hậu xử lý Grounding Verification Decoding.
- **Cải tiến chính:** Cơ chế hậu xử lý xác thực (Grounding Verification) nhằm loại bỏ hoàn toàn ảo giác tọa độ.
- **Kết quả chính:** Đạt SOTA trên CORD, SROIE, VRDU với 0% hallucination về Bounding Box.
- **Học được gì từ paper?:** Không để LLM tự "đoán" số tọa độ. Trích xuất ID/Segment rồi tra ngược (Inverse Lookup) OCR gốc.
- **Có thể áp dụng gì cho topic?:** Áp dụng trực tiếp cho Module Post-processing Grounding Verification để ánh xạ câu trả lời về đúng Bounding Box OCR gốc với độ chính xác 100%.
- **Ghi chú / Câu hỏi:** Đảm bảo Bounding Box xuất ra khớp chính xác đến từng pixel của khối OCR.

> Thư mục: `paper/02-LMDX/`

---

## 3. DocLLM: A Layout-Aware Generative Language Model for Multimodal Document Understanding

- **Link Paper:** https://arxiv.org/pdf/2401.00908
- **Năm:** 2024
- **Venue / Journal:** ACL
- **Rank:** Top Conference
- **Mức độ liên quan:** Direct
- **Bài toán chính:** Đọc hiểu & QA trên tài liệu bố cục phức tạp (bảng biểu) mà không cần Vision Encoder (ViT).
- **Phương pháp chính:** Chỉnh sửa Attention thành Disentangled Spatial Attention (Text-Spatial, Spatial-Text...); Pre-train bằng Block Infilling.
- **Cải tiến chính:** Tích hợp ma trận vị trí 2D trực tiếp vào Attention layer của LLM giúp học cấu trúc hình học.
- **Kết quả chính:** Vượt GPT-4+OCR trên 14/16 DocVQA benchmark (DocVQA 69.5%, DUDE 47.2%).
- **Học được gì từ paper?:** Bố cục 2D (Spatial Layout) đóng vai trò sống còn trong việc hiểu tài liệu phức tạp (Table QA, Bảng điểm).
- **Có thể áp dụng gì cho topic?:** Áp dụng tư duy phân tích khoảng cách tương đối giữa câu hỏi, câu trả lời và vùng bằng chứng xung quanh.
- **Ghi chú / Câu hỏi:** Cực hữu ích nếu tiến hành Fine-tune mô hình nguồn mở (Llama-3 / Qwen2).

> Thư mục: `paper/03-DocLLM/`

---

## 4. LayoutLMv3: Pre-training for Document AI with Unified Text and Image Masking

- **Link Paper:** https://arxiv.org/pdf/2204.08387
- **Năm:** 2022
- **Venue / Journal:** EMNLP
- **Rank:** Top Conference
- **Mức độ liên quan:** Related
- **Bài toán chính:** Trích xuất & định vị thực thể trên tài liệu bằng kiến trúc đa phương thức đồng nhất.
- **Phương pháp chính:** Đưa Text, 2D Bbox và Image Patches vào Transformer đồng nhất; Pre-train MLM, MIM và Word-Patch Alignment.
- **Cải tiến chính:** Dán nhãn trực tiếp từng token thuộc câu trả lời/bằng chứng dưới dạng Token Classification / Span Extraction.
- **Kết quả chính:** Đạt SOTA trên FUNSD, CORD, DocVQA với tốc độ suy luận siêu nhanh.
- **Học được gì từ paper?:** OCR không thể biểu diễn đầy đủ chữ in đậm, đường kẻ, ô merge hoặc đặc điểm thị giác; cần bổ sung visual signal khi layout quyết định đáp án.
- **Có thể áp dụng gì cho topic?:** Dùng làm candidate selector/reranker cho visual_bold_lookup, header/cell classification và các trường hợp OCR không đủ; không dùng thay symbolic solver.
- **Ghi chú / Câu hỏi:** Hỗ trợ đa ngôn ngữ/Tiếng Việt rất tốt (dùng bản LayoutXLM).

> Thư mục: `paper/04-LayoutLMv3/`

---

## 5. TAPAS: Weakly Supervised Table Parsing via Pre-training

- **Link Paper:** https://arxiv.org/abs/2004.02349
- **Năm:** 2020
- **Venue / Journal:** ACL 2020
- **Rank:** Top Conference
- **Mức độ liên quan:** Direct
- **Bài toán chính:** Trả lời câu hỏi trên bảng khi đáp án có thể là cell trực tiếp hoặc kết quả tính toán như SUM, COUNT, so sánh, cực trị.
- **Phương pháp chính:** Mở rộng BERT để mã hóa bảng; dự đoán các cell được chọn và aggregation operator thay vì phải sinh logical form/SQL đầy đủ.
- **Cải tiến chính:** Kết hợp cell selection với aggregation trong một mô hình end-to-end và học từ weak supervision chỉ gồm câu hỏi và denotation.
- **Kết quả chính:** Cải thiện SQA từ 55.1 lên 67.2 accuracy; cạnh tranh tốt trên WikiSQL và WikiTableQuestions, với kiến trúc đơn giản hơn semantic parsing đầy đủ.
- **Học được gì từ paper?:** Với dữ liệu dạng bảng, nên học/chọn các cell và phép toán một cách tách bạch; phép tính cuối nên deterministic để giảm hallucination.
- **Có thể áp dụng gì cho topic?:** Áp dụng trực tiếp cho lookup, sum, count, compare, argmax và argmin; có thể triển khai bản nhẹ gồm intent router, cell selector và symbolic solver.
- **Ghi chú / Câu hỏi:** Paper có tính 20/80 cao nhất vì 6 dạng reasoning trên chiếm khoảng 94.7% câu hỏi training. Code: https://github.com/google-research/tapas

> Thư mục: `paper/05-TAPAS/`

---

## 6. DocVQA: A Dataset for VQA on Document Images

- **Link Paper:** https://arxiv.org/pdf/2007.00398
- **Năm:** 2021
- **Venue / Journal:** WACV 2021
- **Rank:** Other
- **Mức độ liên quan:** Direct
- **Bài toán chính:** Giới thiệu bài toán và bộ dữ liệu Visual Question Answering trên ảnh tài liệu thực tế (DocVQA) nhằm thu hẹp khoảng cách giữa Computer Vision, OCR và NLP Reading Comprehension.
- **Phương pháp chính:** Thu thập 50,000 cặp QA trên 12,767 ảnh tài liệu từ UCSF Industry Documents Library. Đề xuất độ đo ANLS (Average Normalized Levenshtein Similarity) để đánh giá câu trả lời dựa trên khoảng cách chỉnh sửa (Edit Distance) có tính đến lỗi OCR
- **Cải tiến chính:** 1. Xây dựng benchmark DocVQA đầu tiên có mật độ văn bản cao (~182 token/ảnh) kết hợp với các cấu trúc phức tạp (bảng, biểu mẫu, bố cục multi-column, chữ viết tay).

2. Thiết kế chỉ số đánh giá ANLS thay cho Exact Match nhằm chịu lỗi nhỏ do OCR gây ra.

3. Phân loại 9 dạng câu hỏi để đánh giá toàn diện khả năng hiểu bố cục không gian (Spatial/Layout reasoning).
- **Kết quả chính:** - Human Performance: ANLS 94.36%.- Best Baseline Model (BERT-Large trên OCR text): ANLS 47.05%.$\rightarrow$ Xuất hiện khoảng cách cực lớn (~47%) giữa mô hình và con người, chứng minh mô hình xử lý văn bản thuần túy (NLP) thất bại khi thiếu thông tin thị giác và cấu trúc không gian (Layout/Visual).
- **Học được gì từ paper?:** Mật độ token văn bản cao kết hợp thông tin vị trí bounding box/layout là yếu tố sinh tử đối với bài toán hiểu tài liệu. Các chỉ số cứng như Exact Match/BLEU không phản ánh đúng năng lực của mô hình OCR/VQA bằng ANLS.
- **Có thể áp dụng gì cho topic?:** Dùng làm Benchmark chuẩn để đánh giá các mô hình Multimodal LLM (Qwen2-VL, LLaVA-Doc, LayoutLMv3, ColPali) và thiết kế pipeline Multimodal RAG / Information Extraction từ hợp đồng, hóa đơn, tài liệu doanh nghiệp.
- **Ghi chú / Câu hỏi:** _(trống)_

> Thư mục: `paper/06-DocVQA/`

---

## 7. Qwen2-VL: To See the World More Clearly

- **Link Paper:** https://arxiv.org/abs/2409.12191
- **Năm:** 2024
- **Venue / Journal:** arXiv / Pre-print (Alibaba Cloud)
- **Rank:** Other
- **Mức độ liên quan:** Direct
- **Bài toán chính:** Xử lý ảnh tài liệu độ phân giải cao, nhận diện văn bản dài và dự đoán trực tiếp tọa độ Bounding Box dưới dạng text tokens.
- **Phương pháp chính:** Sử dụng Dynamic Resolution (giữ nguyên tỷ lệ tài liệu), mã hóa vị trí 2D bằng 2D-RoPE; đầu ra dự đoán trực tiếp <box>(y1,x1),(y2,x2)</box>.
- **Cải tiến chính:** Khả năng Visual Grounding trực tiếp trên ảnh không cần qua bước OCR độc lập.
- **Kết quả chính:** Đạt điểm SOTA trên DocVQA, ChartQA, InfoVQA và các benchmark Visual Grounding.
- **Học được gì từ paper?:** VLM thế hệ mới có khả năng "nhìn" và "định vị" trực tiếp tốt mà không bị giới hạn bởi lỗi OCR đọc sai.
- **Có thể áp dụng gì cho topic?:** Dùng Qwen2-VL / Qwen2.5-VL làm Mô hình End-to-End mạnh nhất để vừa suy luận câu trả lời vừa xuất Bounding Box bằng chứng.
- **Ghi chú / Câu hỏi:** Cần kết hợp OCR Bounding Box Refinement để đảm bảo tọa độ không bị chênh lệch vài pixel so với ground-truth.

> Thư mục: `paper/07-Qwen2-VL/`

---

## 8. Qwen2.5-VL Technical Report

- **Link Paper:** https://arxiv.org/abs/2502.13923
- **Năm:** _(trống)_
- **Venue / Journal:** arXiv (Technical Report, Qwen Team – Alibaba)
- **Rank:** Other
- **Mức độ liên quan:** Direct
- **Bài toán chính:** Xây backbone thị giác–ngôn ngữ mã nguồn mở, nhiều kích cỡ (3B/7B/72B), có khả năng định vị vật thể bằng bounding box/points trực tiếp.
- **Phương pháp chính:** Dynamic-resolution ViT huấn luyện từ đầu + window attention để giảm chi phí tính toán mà vẫn giữ độ phân giải gốc.
- **Cải tiến chính:** Trích xuất dữ liệu có cấu trúc từ hoá đơn/form/bảng; sinh trực tiếp toạ độ box/point trong output.
- **Kết quả chính:** Bản 72B sánh ngang GPT-4o/Claude 3.5 Sonnet về document understanding; bản 3B đủ nhẹ cho phần cứng hạn chế.
- **Học được gì từ paper?:** Có backbone mã nguồn mở thật sự khả thi để fine-tune trong giới hạn compute sinh viên, không cần huấn luyện lại từ đầu như DocLLM/LayoutLMv3.
- **Có thể áp dụng gì cho topic?:** Dùng Qwen2.5-VL-3B làm backbone chính để fine-tune (QLoRA) cho bài Hỏi đáp trên ảnh tài liệu, thay vì tự thiết kế kiến trúc mới. Bản 7B chỉ dùng để chạy zero-shot/few-shot làm mốc tham chiếu, không fine-tune.
- **Ghi chú / Câu hỏi:** Là technical report (chưa qua peer-review dạng hội nghị), nhưng được dùng làm baseline chuẩn trong chính paper #8 bên dưới — cho thấy độ tin cậy thực tế cao.

> Thư mục: `paper/08-Qwen2.5-VL/`

---

## 9. Towards Reliable and Interpretable Document Question Answering via VLMs (DocExplainerV0)

- **Link Paper:** https://arxiv.org/abs/2509.10129
- **Năm:** 2025
- **Venue / Journal:** arXiv preprint
- **Rank:** Other
- **Mức độ liên quan:** Direct
- **Bài toán chính:** Đánh giá định lượng khả năng định vị vùng bằng chứng của VLM khi trả lời câu hỏi tài liệu - đúng ngay khoảng trống "metric đánh giá evidence region" bạn đang thiếu, dùng chính bộ BoundingDocs (paper đã có trong tracker của bạn).
- **Phương pháp chính:** So sánh 3 VLM (SmolVLM-2.2B, Qwen2-VL-7B, Claude Sonnet 4) × 3 kiểu prompt (zero-shot, Chain-of-Thought, anchor OCR); đề xuất DocExplainerV0 — tách rời sinh câu trả lời (VLM) khỏi định vị bbox (một regressor riêng dựa trên SigLIP2), không cần fine-tune VLM gốc.
- **Cải tiến chính:** Báo cáo song song 2 chỉ số ANLS (văn bản) và MeanIoU (vùng bằng chứng) - chuẩn đánh giá đúng bài toán "answer + evidence" của đề.
- **Kết quả chính:** VLM tự sinh toạ độ qua prompt cho ANLS cao (0.5–0.7) nhưng MeanIoU cực thấp (0.01–0.05) — tức trả lời đúng nhưng chỉ sai vùng khoanh; ngược lại, baseline đơn giản "tìm answer text khớp trong OCR rồi lấy bbox tương ứng" đạt MeanIoU cao nhất (~0.4–0.5), vượt xa cả DocExplainerV0 (~0.18–0.19).
- **Học được gì từ paper?:** Đừng bắt LLM/VLM tự "đoán" số toạ độ — sai số rất lớn; cách hiệu quả nhất (và rẻ nhất) là suy luận answer bằng ngôn ngữ rồi tra ngược (inverse lookup / string-match) vào các block OCR có sẵn để lấy bbox chính xác.
- **Có thể áp dụng gì cho topic?:** Đây gần như là kiến trúc "20/80" cho đề của bạn — vì dữ liệu đã cho OCR + tọa độ từng khối sẵn (không phải tự OCR như BoundingDocs gốc): (1) module sinh câu trả lời (LLM/VLM), (2) module tra ngược khớp câu trả lời vào danh sách block OCR để lấy vùng bằng chứng, gần giống hướng LMDX (paper #2 cũ) nhưng đơn giản, rẻ, và đã được đo lường định lượng rõ ràng.
- **Ghi chú / Câu hỏi:** ✅ **ĐÃ ĐÓNG** — mở bằng mắt cả hai split test: **đều có `ocr/`**, cấu trúc block y hệt train (`block_id`/`page`/`text`/`bbox`), `ocr_source` vẫn `btc_synthetic_clean_layout_v3`. Số tệp: `public_test` 100 tệp / `private_test` 200 tệp. Nhưng **chỉ `training_set` có nhãn** — `labels.jsonl` và `cell_annotations.jsonl` **không tồn tại** trên test, và `questions.jsonl` trên test **không có `reasoning_type`**. Chi tiết: `WEEK01 - Outline và kế hoạch.md` §4.1.2 + §4.1.3.

> Thư mục: `paper/09-DocExplainerV0/`

---

## 10. LiGT: Layout-infused Generative Transformer for VQA on Vietnamese Receipts (ReceiptVQA)

- **Link Paper:** https://arxiv.org/abs/2502.19202
- **Năm:** 2025
- **Venue / Journal:** International Journal on Document Analysis and Recognition (IJDAR)
- **Rank:** Other
- **Mức độ liên quan:** Direct
- **Bài toán chính:** Document VQA tiếng Việt trên hoá đơn/biên lai — tài liệu bán cấu trúc gần giống ảnh tài liệu hành chính trong đề (khác với ViOCRVQA/ViTextVQA vốn là scene-text ảnh chụp ngoài đời).
- **Phương pháp chính:** Kiến trúc encoder-decoder generative, nhúng thông tin layout (toạ độ) trực tiếp vào embedding layer sẵn có của LM thay vì thêm module spatial attention riêng; giới thiệu bộ ReceiptVQA (9.500 ảnh, ~64.800 câu hỏi tiếng Việt).
- **Cải tiến chính:** Cách nhúng layout "nhẹ" (tận dụng embedding có sẵn) thay vì kiến trúc nặng như DocLLM; so sánh trực tiếp generative vs extractive trên dữ liệu tiếng Việt.
- **Kết quả chính:** Kiến trúc generative xử lý lỗi OCR tiếng Việt tốt hơn hẳn cách trích xuất token-classification kiểu LayoutLMv3; kết hợp đa phương thức (text+layout+visual) là bắt buộc.
- **Học được gì từ paper?:** Đặc thù tiếng Việt (dấu thanh, lỗi OCR dấu) ảnh hưởng khác hẳn benchmark tiếng Anh — không thể giả định các paper tiếng Anh áp dụng nguyên trạng.
- **Có thể áp dụng gì cho topic?:** Tham khảo cách xử lý lỗi OCR tiếng Việt và chọn hướng kiến trúc generative (không phải token-classification) cho phần sinh câu trả lời, đúng bối cảnh câu hỏi tiếng Việt trên ảnh tài liệu hành chính của đề thi.
- **Ghi chú / Câu hỏi:** Cùng venue (IJDAR) với paper BoundingDocs đã có — tiện tra thêm citation chéo; là paper Document VQA tiếng Việt gần nhất về bản chất (structured document, không phải scene-text) mà mình tìm được.

> Thư mục: `paper/10-LiGT-ReceiptVQA/`

---
