# WEEK01 — Hiểu bài toán, nguyên lý, công thức

**Subtopic:** Hỏi đáp trên ảnh tài liệu
**Ngày:** 2026-09-17
**Tình trạng:** Đã có data của olp-ai-ptit (train/public/private) · Solo · Chưa chốt output
**Mục đích:** Thực hiện §II.1 — *"hiểu bài toán chính, nguyên lý hoạt động, các công thức hoặc quy trình quan trọng và cách kiến thức đó được áp dụng trong thực tế"*

---

> ## ⚠️ ĐỌC TRƯỚC
>
> File này là **bản đồ học tập để tự kiểm chứng**, không phải nội dung nộp.
>
> Quy chế §III.3: *"Không sử dụng AI để viết nội dung sản phẩm nộp... AI không được sử dụng để thay thế quá trình tự đọc paper, tự phân tích hoặc tự xây dựng nội dung của nhóm."*
>
> Mọi công thức ở đây đều **ghi rõ số trang / số hiệu công thức** để tự mở paper đối chiếu. **Đừng tin số trong file này** — hãy tự đọc lại nguồn trước khi dùng.
>
> Phần §5 (tự hệ thống lại) là chỗ **nhóm phải tự viết lại bằng lời của mình**. Bản ở đây chỉ là gợi ý khung.

> ### 🔴 ĐÍNH CHÍNH 21/09 — đọc trước khi trích dẫn bất kỳ con số nào
>
> **Mọi chỗ trong file này viết "trần 100,00%" đều là con số CŨ và SAI.** Bản đo đầu dùng `audit_ceiling.py`, script đó tra text ô qua `cell_annotations.jsonl` — **file nhãn**. File này không tồn tại trên `public_test`/`private_test`, nên con số chưa từng đo được trên tập đích.
>
> Số đúng, đo bằng `code/oracle_ceiling.py` (text ô từ `ocr/*.json`, lưới dựng thuần hình học, `is_bold` đo từ ảnh):
>
> | | Cũ (sai) | Đúng |
> |---|---:|---:|
> | `visual_bold_lookup` | 100,00% | **82,99%** |
> | 7 dạng còn lại | 100,00% | 100,00% |
> | Khớp tuyệt đối toàn tập | 100,00% | **99,17%** |
> | **Điểm cuộc thi** (`0,85·ANLS + 0,15·F1`) | — | **99,30** |
>
> Và gọi tên cho đúng: đây là **trần oracle** — điểm tối đa *khi biết trước ô đúng* — **không phải** điểm hệ thống thực tế đạt được (TA góp ý 19/09, mục 2). Khoảng cách 95,45 → 99,30 là **dư địa của bộ chọn ô**, không phải điểm đã có.
>
> Chi tiết + bảng theo split: `PROGRESS_LOG.md`, mục "Đã sửa xong (21/09)".

---

## 1. BÀI TOÁN CHÍNH

### 1.1 Phát biểu

Cho **ảnh trang tài liệu** + **kết quả OCR kèm toạ độ từng khối** + **câu hỏi tiếng Việt**, phải trả về **hai thứ cùng lúc**:

1. **Câu trả lời** dạng chuỗi
2. **Danh sách vùng bằng chứng** — trang nào, toạ độ nào

Cả hai đều được chấm điểm. Trả lời đúng mà không chỉ được vùng thì mất 15% điểm; chỉ đúng vùng mà trả lời sai thì mất 85%.

### 1.2 Vì sao đây KHÔNG phải bài tra cứu từ khoá

Ví dụ trong đề: *"Tổng chỉ tiêu tuyển mới của hai phòng ban có định biên 30 là bao nhiêu?"*

Con số đó **không được in ở bất kỳ đâu trên trang**. Nó chỉ tồn tại sau khi: tìm đúng vài ô trong bảng → hiểu quan hệ hàng/cột → cộng lại. Không có chuỗi nào trong OCR khớp được với đáp án.

**Hệ quả trực tiếp:** mọi kiến trúc "trích xuất span" (extractive QA) về mặt nguyên lý **không thể** sinh ra đáp án này. Không phải yếu — mà là không có cơ chế.

### 1.3 Tám kiểu suy luận — đây là bản đồ của cả bài toán

| Kiểu | Số câu | Chiếm | Yêu cầu |
|---|---:|---:|---|
| `lookup` | 2.200 | 20,0% | Tra trực tiếp giá trị một ô |
| `argmax` | 1.898 | 17,3% | Tìm dòng có giá trị **lớn nhất** |
| `argmin` | 1.874 | 17,0% | Tìm dòng có giá trị **nhỏ nhất** |
| `sum` | 1.810 | 16,5% | Cộng giá trị nhiều ô |
| `compare` | 1.722 | 15,7% | So sánh hai giá trị |
| `count` | 915 | 8,3% | Đếm số dòng thoả điều kiện |
| `visual_bold_lookup` | 535 | 4,9% | Tra ô **in đậm** — chỉ nhận biết được từ ảnh |
| `cross_page_sum` | 46 | 0,4% | Cộng giá trị nằm trên **hai trang khác nhau** |

**Ba cách cắt khác nhau của cùng một tập — đừng lẫn:**

| Cách cắt | Số câu | % | Ý nghĩa |
|---|---:|---:|---|
| Nhóm **tính toán** (`argmax+argmin+sum+compare+count+cross_page_sum`) | 8.265 | **75,1%** | Phải có toán tử, không chỉ đọc |
| Nhóm tính toán, **bỏ `cross_page_sum`** | 8.219 | 74,7% | Cách cắt cũ — thiếu `cross_page_sum` |
| Bỏ `visual_bold_lookup` + `cross_page_sum` | 10.419 | **94,7%** | Phần quy về **thao tác có cấu trúc trên bảng** |

**Con số quyết định là 75,1%** (`argmax+argmin+sum+compare+count+cross_page_sum` = 8.265/11.000). Ba phần tư bài toán nằm ở nhóm mà **không paper nào trong reading list có cơ chế xử lý** (xem §2.3). Chỉ `lookup` (20%) là bài toán mà extractive QA truyền thống giải được.

**94,7% khớp với TA Minh:** bài hướng dẫn §II (tr. 8) viết *"khoảng 95% câu hỏi có thể quy về các thao tác có cấu trúc trên bảng"*. Đo lại: `11.000 − 535 (visual_bold_lookup) − 46 (cross_page_sum) = 10.419 = 94,7%`. **Hai bên khớp nhau** — 94,7% là cách cắt *rộng hơn* (tính cả `lookup`), 75,1% là cách cắt *hẹp hơn* (chỉ nhóm cần toán tử). Không mâu thuẫn.

**Đối chiếu với trần trích xuất (§2.5b) — hai con số này khớp nhau về mặt cấu trúc:**

| | Số câu | % | Trần trích xuất |
|---|---:|---:|---|
| Sáu kiểu **tra cứu** (`lookup`, `argmax`, `argmin`, `compare`, `count`, `visual_bold_lookup`) | 9.144 | **83,1%** | **100,0%** chuỗi con liền |
| Hai kiểu **tính toán** (`sum`, `cross_page_sum`) | 1.856 | **16,9%** | **~0%** — đáp án không tồn tại trong tài liệu |

Đọc cùng nhau: **83,1% câu hỏi có đáp án nằm nguyên văn trong OCR, nhưng 75,1% câu hỏi đòi một phép toán.** Hai tập này **chồng lấn phần lớn** — `argmax`/`argmin`/`compare`/`count` vừa cần tính toán vừa có đáp án nguyên văn (đáp án là *nhãn dòng*, không phải con số đã tính). Đó chính là lý do kiến trúc "**chọn ô + solver thủ tục**" hoạt động: solver chọn đúng ô, rồi **đọc** nội dung ô — không bao giờ *sinh* chữ.

### 1.4 Ràng buộc kỹ thuật bắt buộc nhớ

| Ràng buộc | Giá trị | Nguồn |
|---|---|---|
| Hệ toạ độ | Chuẩn hoá `[x1,y1,x2,y2]`, mọi giá trị ∈ `[0,1]` | §2 đề |
| Gốc toạ độ | **Góc trên bên trái** trang | §2 đề |
| Bất biến | Luôn `x1 < x2` và `y1 < y2` | §2 đề |
| Số vùng bằng chứng | **2 – 6 vùng** mỗi câu | §2 đề |
| Ảnh | JPEG khổ dọc, 1600×2263 → 2000×2828 px | §2 đề |
| Mỗi tài liệu | 1 hoặc 2 trang, **đúng 10 câu hỏi** | §2 đề |
| Đáp án | 2 loại: chuỗi văn bản · giá trị số tính từ bảng | §2 đề |

**⚠️ Đã đo lại trên `training_set` — ràng buộc "2–6 vùng" KHÔNG đúng tuyệt đối:**

| Số vùng | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Câu | 2.611 | 3.897 | 1.526 | 1.152 | 1.679 | 56 | 72 | 5 | 3 |
| % | 23,7 | 35,4 | 13,9 | 10,5 | 15,3 | 0,5 | 0,7 | — | — |

**~1,2% số câu vượt quá 6 vùng** (136/11.000). Nếu code cứng `assert len(evidence) <= 6` hoặc cắt bớt còn 6 → mất điểm oan. Phải chịu được 7–10.

**✅ Đã giải quyết dứt điểm quy ước `page` — không có lệch 1 đơn vị:**

| Nơi | Giá trị | Bằng chứng |
|---|---|---|
| `labels.jsonl` evidence | **1-based** | Đo toàn tập: `distinct page = {1, 2}` — không có `0` |
| `cell_annotations.jsonl` | **1-based** | `"page": 1`, khớp `labels` |
| OCR file | **1-based** | `"block_id": "p01_b00000"` — tiền tố `p01` |
| Code TA Minh (`submission_pipeline.ipynb`) | **1-based** | `result.append({"page": block["page"], "bbox": block["bbox"]})` — chuyển thẳng, không `±1` |
| File nộp theo đề §1.3 (tr. 5) | ghi `"page": 0` | ⚠️ **Lỗi in của tài liệu**, không phải quy ước |

**Kết luận: dùng 1-based ở mọi nơi, chuyển thẳng không cộng trừ.** Trang 1 → `"page": 1`. Chỉ cần nhớ **đừng** viết `page - 1` theo ví dụ trong PDF.

### 1.5 Data của olp-ai-ptit — có sẵn, đã kiểm, khớp đề

Vị trí: `d:/AI/Project/Module 4/data/` (~282 MB). **Không nằm trong repo TA Minh** (`data/` bị gitignore) — phải tự tải về.

| Split | Tài liệu | Câu hỏi | Ghi chú |
|---|---:|---:|---|
| `training_set/` | 1.100 | 11.000 | **Có `labels.jsonl` + `cell_annotations.jsonl`** |
| `public_test/` | 100 | 1.000 | Có `questions.jsonl`, **không có labels** |
| `private_test/` | 200 | 2.000 | Có `questions.jsonl`, **không có labels** |

**Cấu trúc file (đã đọc trực tiếp):**

```
manifest.jsonl          {"id":"B-train-00000","image_paths":["images/B-train-00000_p01.jpg"],
                         "ocr_path":"ocr/B-train-00000.json","page_count":1,
                         "question_count":10,"split":"training_set"}

questions.jsonl         {"document_id":"B-train-00000","question_id":"B-train-00000-q01",
                         "question":"Trong bảng 1 ở trang 1, tổng Tuyển mới của hai dòng
                          có Phòng ban “Chăm sóc khách hàng” và Phòng ban “Kế toán”
                          và Định biên “30” là bao nhiêu?"}

labels.jsonl            {"question_id":"B-train-00000-q01","reasoning_type":"sum",
                         "answer_type":"number","answers":["7"],
                         "evidence":[{"page":1,"bbox":[0.0525,0.34114,0.304375,0.362351],
                                      "block_id":"p01_b00030"}, ...5 more...]}

cell_annotations.jsonl  {"document_id":"B-train-00000","page":1,"table":1,"row":0,
                         "column":0,"bbox":[...],"block_id":"p01_b00000",
                         "clean_text":"Phòng ban","is_bold":true,"is_header":true}

ocr/B-train-00000.json  {"coordinate_system":"normalized_xyxy","document_id":"...",
                         "ocr_source":"btc_synthetic_clean_layout_v3",
                         "pages":[{"blocks":[{"page":1,"block_id":"p01_b00000",
                                              "bbox":[...],"text":"Phòng ban"}, ...]}]}
```

**Ba điều rút ra:**

1. **`cell_annotations.jsonl` là tài sản lớn nhất của đề.** 256.040 ô, mỗi ô có `table`/`row`/`column`/`is_bold`/`is_header`. Đây chính là thứ TAPAS phải tự học, còn đề **cho sẵn**. Không paper nào trong reading list có đặc quyền này.
2. **Câu hỏi tự mô tả cấu trúc.** Ví dụ trên ghi rõ *"Trong bảng 1 ở trang 1"* và **trích nguyên văn giá trị ô lọc trong ngoặc kép**. Đây là cơ sở cho quy tắc tách ô lọc ở §3.8 — và là lý do bài toán dễ hơn tưởng.
3. **`ocr_source = "btc_synthetic_clean_layout_v3"` — và đây là giá trị của CẢ BA split.** Đã kiểm 40 file ngẫu nhiên mỗi split: `training_set` 40/40, `public_test` 40/40, `private_test` 40/40 đều là `btc_synthetic_clean_layout_v3`. **Không split nào dùng OCR thật** → mọi kết luận đo trên train **chuyển thẳng được sang test**, và lập luận "tiếng Việt có dấu làm OCR thật sai" (LiGT, §2.6) **không áp dụng cho đề này**. Đây là rủi ro lớn nhất từng bị treo — nay đã đóng.

---

## 2. NGUYÊN LÝ HOẠT ĐỘNG

### 2.1 Nguyên lý trung tâm: bằng chứng là bài toán **CHỌN**, không phải **SINH**

Đây là kết luận hội tụ của nhiều paper độc lập, và là nguyên lý quan trọng nhất của cả subtopic.

**Bằng chứng đo được** — DocExplainerV0, bảng so sánh 3 VLM × 3 kiểu prompt:

| Mô hình | Prompt | ANLS | MeanIoU |
|---|---|---:|---:|
| SmolVLM | Zero-shot | .527 | **.011** |
| SmolVLM | Anchors (OCR) | .543 | **.026** |
| SmolVLM | CoT | .561 | **.011** |
| Qwen2-VL-7B | Zero-shot | .691 | **.048** |

VLM **trả lời đúng** (ANLS .53–.69) nhưng **khoanh vùng sai hoàn toàn** (IoU .011–.048).

Ngưỡng của đề là **IoU ≥ 0,5**. Sinh toạ độ thua ngưỡng **một bậc độ lớn** — không phải "cần tinh chỉnh thêm", mà là **sai phương pháp**.

**Nguyên lý đúng:** đừng bao giờ hỏi VLM/LLM toạ độ. Hãy để nó **suy luận ra câu trả lời bằng ngôn ngữ**, rồi **tra ngược** vào danh sách block OCR có sẵn để lấy bbox.

### 2.2 Vì sao đề này thuận lợi hơn bài toán gốc

DocExplainerV0 phải tự OCR. **Đề này cho sẵn OCR + toạ độ từng khối.** Nghĩa là bước "tra ngược" ở đây **rẻ và chính xác hơn hẳn** — chỉ là bài toán ánh xạ chuỗi → block_id, không cần model nào.

Đây là lý do kỹ thuật khiến hướng "chọn thay vì sinh" khả thi trong 4 tuần.

### 2.3 Mô hình tư duy: TÁCH **CHỌN** KHỎI **TÍNH**

Pattern quan trọng nhất lấy từ TAPAS, và là thứ cả 10 paper khác không làm:

> **Model chỉ CHỌN cell. Toán tử do SOLVER THỦ TỤC thi hành.**

TAPAS làm đúng điều này ở suy luận (inference):
> *"we select all table cells for which their probability is larger than 0.5. These predictions are then executed against the table to retrieve the answer, by applying the predicted aggregation over the selected cells."*

Cell được mô hình hoá như **biến Bernoulli độc lập**; xác suất chọn cell `ps(c)` = trung bình logit của các token trong cell đó.

**Vì sao pattern này quan trọng với đề:**

| Việc | Ai làm | Vì sao |
|---|---|---|
| Chọn đúng ô nào | **Model** (học) | Cần hiểu ngôn ngữ + layout |
| Cộng / đếm / so sánh / tìm max | **Solver** (thủ tục) | Deterministic → **không thể hallucinate** |

Nếu để model tự sinh số, nó có thể sinh sai. Nếu solver cộng số, kết quả **đúng theo định nghĩa** hoặc **sai vì chọn sai ô** — hai loại lỗi tách bạch, sửa được từng loại.

**Toán tử TAPAS có:** `{NONE, COUNT, SUM, AVERAGE}`.
**Toán tử TAPAS THIẾU:** `MAX`, `MIN`, phép so sánh → **không làm được `argmax`/`argmin`/`compare`**.

Nhưng `cell_annotations.jsonl` của đề có sẵn `row`, `column`, `is_bold`, `is_header` → **đủ để tự viết solver thủ tục** cho cả 6 loại, không cần model.

### 2.4 Nguyên lý xác thực: Grounding Verification (LMDX)

LMDX giải bài toán "LLM bịa toạ độ" bằng một bước hậu xử lý. Cơ chế gồm **hai phép kiểm tra**:

1. **Segment ID có tồn tại không?** → không tồn tại = bịa → **loại**
2. **Text trích ra có phải chuỗi con của segment đó không?** → không phải = bịa → **loại**

Sau khi qua cả hai, bbox của entity = **hộp nhỏ nhất bao trọn mọi từ** thuộc entity.

**Kết quả LMDX công bố:** SOTA trên CORD/SROIE/VRDU với **0% hallucination** về bounding box.

**⚠️ Giới hạn phải hiểu đúng — đây là chỗ rất dễ hiểu sai:**

Grounding Verification **chỉ giết được dương tính giả**. Nó **không cứu được âm tính giả** — nếu model không dự đoán ra entity thì không có gì để xác thực. Nó làm **precision = 100%**, không làm recall tăng.

Với đề: cơ chế này dùng để **đảm bảo mọi bbox nộp lên đều trỏ vào block OCR có thật**. Nó không giúp tìm ra vùng bằng chứng đúng.

### 2.5 Nguyên lý về trần năng lực: không phải đáp án nào cũng trích xuất được

**Đo được (DocVQA Table 1, test split):**

| Heuristic | Điểm |
|---|---:|
| Vocab UB (chọn từ vựng cho sẵn) | 33,78 |
| **OCR substring UB** (đáp án là **chuỗi con liền** của OCR) | **87,00** |
| **OCR subsequence UB** (đáp án là **dãy con** của OCR) | **77,00** |

**Đọc bảng này cho đúng — đây là cái bẫy:**

Chênh lệch 87,00 − 77,00 = **10 điểm** chính là phần đáp án **chỉ khớp được ở mức dãy con** (các từ rời rạc, không liền nhau). Nếu code dùng `answer in ocr_text` thô, sẽ **ăn điểm ảo 10 điểm** — khớp những chỗ mà người chấm không coi là khớp.

→ **Bắt buộc khớp theo ranh giới từ / theo cả khối**, không dùng `in` thô.

Và cả 87,00 cũng **không phải 100**: ~13% đáp án không nằm trong OCR dưới bất kỳ dạng nào. Trần trích xuất thực tế theo LiGT còn thấp hơn: **~76–81%**.

### 2.5b Đã đo trần trích xuất THẬT trên olp-ai-ptit — và con số 99,9% là **DƯƠNG TÍNH GIẢ**

Chạy trên **toàn bộ 11.000 câu** của `training_set` (`audit_dataset.py` Q1):

| Heuristic | Câu | % |
|---|---:|---:|
| Đáp án là **chuỗi con liền** của OCR | 9.423 | 85,7% |
| Đáp án là **dãy con** (subsequence) của OCR | 1.568 | 14,3% |
| Không khớp dạng nào | **9** | **0,1%** |

**⚠️ Bản trước của file này ghi "trần trích xuất 99,9%". SAI. Đã kiểm lại và phát hiện 1.568 ca subsequence là DƯƠNG TÍNH GIẢ.**

Bằng chứng — tách theo `reasoning_type`:

| Kiểu | substring | subsequence | không khớp | **substring %** |
|---|---:|---:|---:|---:|
| `lookup` | 2.200 | 0 | 0 | **100,0%** |
| `argmax` | 1.898 | 0 | 0 | **100,0%** |
| `argmin` | 1.874 | 0 | 0 | **100,0%** |
| `compare` | 1.722 | 0 | 0 | **100,0%** |
| `count` | 915 | 0 | 0 | **100,0%** |
| `visual_bold_lookup` | 535 | 0 | 0 | **100,0%** |
| `sum` | 270 | **1.531** | 9 | **14,9%** |
| `cross_page_sum` | 9 | **37** | 0 | **19,6%** |

**Đọc bảng này cho đúng — đây là kết quả quan trọng nhất về metric:**

`1.531 + 37 = 1.568` — **toàn bộ** ca subsequence đều thuộc **hai kiểu tính toán**. Không một ca nào thuộc 6 kiểu còn lại.

**Vì sao đây là dương tính giả, không phải khớp thật:**

```
B-train-00001-q01   type=sum   answer='7381'
  evidence cells: ['Đồng Nai', '5.985', 'Lâm Đồng', '1.396']
  5.985 + 1.396 = 7.381  ✅  nhưng '7381' KHÔNG xuất hiện ở đâu trong tài liệu
```

Test subsequence chỉ hỏi *"các chữ số 7,3,8,1 có xuất hiện theo thứ tự ở đâu đó không"* — trong một tài liệu đầy số, **gần như luôn trả lời "có"**. Nó khớp với chữ số vương vãi khắp trang, không phải với đáp án.

**Kết luận đúng:**

1. **Sáu trong tám kiểu có trần trích xuất = 100,0%.** Mọi đáp án `lookup`/`argmax`/`argmin`/`compare`/`count`/`visual_bold_lookup` đều nằm **nguyên văn** trong OCR. Không có ca nào "chỉ khớp dãy con".
2. **Hai kiểu tính toán có trần trích xuất ≈ 0% — và đó là điều đúng về mặt cấu trúc.** `5.985 + 1.396 = 7.381` là số **được tính ra**, không được in ở đâu. Không heuristic trích xuất nào tìm được nó. Đây chính là lập luận ở §1.2, nay **đo được**.
3. **Bẫy DocVQA đảo chiều.** Ở DocVQA, subsequence UB (77,00) **thấp hơn** substring UB (87,00) → dùng `in` thô sẽ ăn điểm ảo. Ở olp-ai-ptit, subsequence lại **cao hơn** — vì nó bắt được những đáp án tính toán mà substring bỏ sót. **Cùng một cái bẫy, hai chiều ngược nhau.**
4. **Bài học vận hành:** nếu ai đó báo cáo "trần trích xuất 99,9%" cho đề này, **con số đó vô nghĩa**. Phải tách theo `reasoning_type` mới thấy sự thật: 100% với tra cứu, ~0% với tính toán.

**9 câu "không khớp dạng nào" — tất cả đều là `sum`.** Đây là mức sàn bất khả thi về mặt trích xuất: ngay cả heuristic lỏng nhất cũng không chạm tới.

### 2.5c Trần **oracle** của bài toán: **99,30** — đo được, không phải suy đoán

> **Đính chính (21/09, ghi ở WEEK02 §2.4).** Bảng dưới đây là bản **đầu**, đo bằng `audit_ceiling.py` — script đó tra text ô qua `cell_annotations.jsonl`, tức **file nhãn**, nên con số 100,00% không đo được trên tập đích (file này không tồn tại ở `public_test`/`private_test`). Bản viết lại `code/oracle_ceiling.py` lấy text ô từ `ocr/*.json` và dựng lưới thuần hình học: **7 dạng giữ nguyên 100,00%, `visual_bold_lookup` 100,00% → 82,99% (bảng dưới ghi 535/535 = 100,0%, đúng), tổng 99,17% khớp tuyệt đối**. Quy ra điểm cuộc thi (`0,85·ANLS + 0,15·F1`, F1 = 1,0 vì biết trước ô vàng): **99,30**. Con số 100,00% bên dưới là **sai** và được giữ lại làm mốc đối chiếu.
>
> Cũng gọi tên cho đúng: đây là **trần oracle** — điểm tối đa *khi biết trước ô đúng* — **không phải** điểm hệ thống thực tế đạt được (TA góp ý 19/09, mục 2).

Đây là số quan trọng nhất trong cả file. Chạy `audit_ceiling.py`: **đưa đúng evidence vàng**, dùng **solver thủ tục thuần Python, không có model nào**, rồi so với đáp án vàng:

| Kiểu | Đúng | Tỉ lệ |
|---|---:|---:|
| `lookup` | 2.200/2.200 | **100,0%** |
| `argmax` | 1.898/1.898 | **100,0%** |
| `argmin` | 1.874/1.874 | **100,0%** |
| `sum` | 1.810/1.810 | **100,0%** |
| `compare` | 1.722/1.722 | **100,0%** |
| `count` | 915/915 | **100,0%** |
| `visual_bold_lookup` | 535/535 | **100,0%** ← *sai, xem đính chính: 82,99%* |
| `cross_page_sum` | 46/46 | **100,0%** |
| **TỔNG** | **11.000/11.000** | **100,00%** ← *sai, xem đính chính: 99,17%* |

**Quy tắc duy nhất làm nên con số này — "ô phải cùng của hàng":**

> Trong một hàng, **ô được hỏi luôn là ô ngoài cùng bên phải**. Ô điều kiện (filter) nằm bên trái nó.

Đo lại để chứng minh — vị trí ô đáp án, đếm từ phải sang trong hàng của nó:

| Kiểu | Vị trí 0 (phải nhất) | 1 | 2 | 3 |
|---|---:|---:|---:|---:|
| `lookup` | **2.200** | — | — | — |
| `sum` / `cross_page_sum` | **45** | — | — | — |
| `visual_bold_lookup` | **535** | — | — | — |
| `argmax` | — | 726 | 1.116 | 55 |
| `argmin` | — | 714 | 1.098 | 60 |
| `compare` | — | 723 | 1.091 | 55 |

Nhóm `argmax`/`argmin`/`compare` có ô đáp án **không** phải ô phải nhất — nhưng đó là vì **đáp án của chúng là *nhãn hàng*, không phải giá trị ô**: evidence chỉ chứa **đúng hàng thắng** (đo được: `rows-per-question = 1/1/1`, min/median/max), nên không có gì để xếp hạng — chỉ cần đọc ô chữ bên trái nhất. Ô số bên phải trong evidence của chúng là **ô điều kiện dùng để định vị hàng**, không phải đáp án.

**Đọc kết quả này cho đúng — nó định hình toàn bộ kiến trúc:**

1. **Sinh đáp án là MIỄN PHÍ.** Một khi biết đúng ô nào, đáp án suy ra được bằng phép cộng/đếm/so sánh — không cần model, không thể hallucinate.
2. **Toàn bộ 100% điểm nằm ở bước CHỌN Ô.** Đây là xác nhận định lượng cho nguyên lý §2.1 — không còn là suy luận từ paper nữa.
3. **⚠️ Bản trước của mục này ghi 99,8% và đổ 22 câu thiếu cho "bất thường dữ liệu ở 3 tài liệu" — SAI.** Đo lại: **không có tài liệu bất thường nào.** 22 câu đó là **lỗi của solver**, do một nguyên nhân duy nhất: **ô đáp án trùng giá trị với ô điều kiện**, nên quy tắc cũ "bỏ mọi ô khớp chuỗi trong ngoặc kép" xoá luôn ô đáp án. Ví dụ `B-train-00086-q06`: hàng có `Thí sinh = 47` và `Đạt = 47` — chuỗi `"47"` bị coi là filter ở cả hai ô. Sửa bằng quy tắc "ô phải cùng của hàng" → **hết sạch**.
   > **Bài học:** khi solver sai, **mặc định là lỗi mình**, không phải lỗi dữ liệu. Suy đoán "dữ liệu bất thường" đã che mất một bug thật trong 2 phiên làm việc.
4. **`sum` và `cross_page_sum` cần cùng một quy tắc, nhưng hàng phải khoá theo `(page, table, row)`.** Khoá thiếu `page` làm hai hàng cùng toạ độ ở hai trang khác nhau bị gộp thành một — đó là toàn bộ lỗi của `cross_page_sum`.

**Suy ra mục tiêu tối ưu:** `Question_Score = 0,85×ANLS + 0,15×Evidence-F1`. Vì sinh đáp án đã đúng **100%** khi có evidence đúng, **hai hạng tử này gần như đo CÙNG một thứ** — chất lượng chọn ô. Tối ưu bộ chọn là tối ưu cả hai.

> **Trần này là trần *có điều kiện*.** Nó nói: *nếu* chọn đúng ô thì ăn trọn điểm. Nó **không** nói bộ chọn sẽ đạt 100% — đó là việc khó, và là toàn bộ nội dung còn lại của đồ án. Đừng đọc con số này thành "bài toán đã xong".

### 2.5d Evidence chính là **ô bảng**, không phải hộp tự do

Đo trên 39.937 vùng evidence (`audit_dataset.py` Q2):

| Kiểm tra | Kết quả |
|---|---:|
| bbox khớp **chính xác** một bbox trong `cell_annotations.jsonl` | **39.937/39.937 = 100,0%** |
| `block_id` tồn tại trong file OCR | **100,0%** |

**Hệ quả:** bài toán chọn vùng **không phải bài toán hồi quy toạ độ**. Không gian tìm kiếm là **hữu hạn và rời rạc** — đúng bằng tập cell có sẵn. Nộp bbox không nằm trong `cell_annotations` gần như chắc chắn là sai.

Đây là lý do kỹ thuật mạnh nhất khiến "chọn thay vì sinh" (§2.1) thắng: **không cần dự đoán toạ độ, chỉ cần dự đoán chỉ số cell.**

### 2.6 Nguyên lý về tiếng Việt: extractive thua generative rất xa

**LiGT Table 5 — đo trên ReceiptVQA (tiếng Việt, hoá đơn):**

| Hướng | Mô hình | ANLS |
|---|---|---:|
| **Extractive** | LayoutXLM base | 59,11 |
| **Extractive** | PhoBERT base | 61,39 |
| **Generative** | ViT5 + U | **78,98** |

**Chênh ~20 ANLS.** Trên tiếng Việt, hướng sinh thắng hướng trích xuất một khoảng rất lớn.

**Giải thích:** lỗi OCR dấu thanh tiếng Việt phá vỡ giả định "đáp án nằm nguyên văn trong text" mà extractive QA dựa vào. Model generative "sửa lỗi" được khi sinh; model extractive bị khoá cứng vào chuỗi hỏng.

**Kết hợp với §2.5:** trần trích xuất ~76–81%, mà hướng trích xuất lại thua ~20 điểm → **không nên đi hướng span-head extractive**. Đây là kết luận kỹ thuật, không phải sở thích.

**⚠️ CẢNH BÁO — lập luận này KHÔNG áp nguyên xi cho olp-ai-ptit. Đã kiểm tra và phát hiện mâu thuẫn:**

File OCR của đề ghi rõ:
```json
"ocr_source": "btc_synthetic_clean_layout_v3"
```

**OCR của olp-ai-ptit là OCR tổng hợp, sạch, do BTC sinh ra** — không phải OCR thật trên ảnh chụp. Nghĩa là **giả định "lỗi dấu thanh phá vỡ đáp án nguyên văn" không còn đúng**, ít nhất trên `training_set`.

Đối chiếu với số đo §2.5b — **đọc kỹ, con số này dễ bị hiểu sai**: 85,7% đáp án khớp **chuỗi con liền** trong OCR. 14,3% còn lại khớp dãy con, **nhưng đó là dương tính giả** (đáp án `sum` được tính ra, không hề tồn tại trong tài liệu). Nếu OCR hỏng dấu như ReceiptVQA thì ngay cả 85,7% cũng không đạt được — vì `lookup`/`argmax`/`argmin`/`compare`/`count`/`visual_bold_lookup` đều đang ở **100,0%** chuỗi con liền.

**Vậy kết luận §2.6 phải viết lại cho chính xác:**

| | ReceiptVQA (LiGT) | olp-ai-ptit (đề này) |
|---|---|---|
| Nguồn OCR | OCR thật trên ảnh hoá đơn chụp | **Tổng hợp, sạch** (`btc_synthetic_clean_layout_v3`) |
| Lỗi dấu thanh | Nhiều | **Không đáng kể** (6/8 kiểu khớp chuỗi con liền **100,0%**) |
| Extractive vs generative | Generative thắng ~20 ANLS | **Chưa đo — không được suy diễn** |

**Điều này KHÔNG lật ngược kiến trúc.** Lý do chọn "chọn ô + solver" ở §2.1 và §2.5c **không phải** vì OCR hỏng — mà vì **75,1% câu hỏi không có đáp án nguyên văn trong tài liệu** (§1.3). Đó là lập luận độc lập, và §2.5c đã xác nhận nó bằng số đo 100,00%.

**Nhưng nó bác bỏ một lập luận phụ:** không thể viện "tiếng Việt khó vì lỗi dấu" để biện minh cho lựa chọn kiến trúc trên dataset này. **Chỗ này phải ghi trung thực — nếu không, phần bảo vệ trước TA sẽ bị hỏi ngược và không trả lời được.**

**Việc còn phải làm:** kiểm `ocr_source` của `public_test` và `private_test` xem có cùng giá trị không. Nếu **khác** (ví dụ test dùng OCR thật) thì toàn bộ lập luận này phải xét lại — và đó là rủi ro lớn nhất chưa được kiểm chứng của cả kế hoạch.

### 2.7 Nguyên lý về metric: ANLS không phân biệt được hai loại lỗi rất khác nhau

**Đã tự chạy test:**

| Dự đoán | Gold | ANLS | Qua τ=0,5? |
|---|---|---:|---|
| `Hoa don` | `Hóa đơn` | 0,571 | ✅ |
| `Phong Ke toan` | `Phòng Kế toán` | 0,769 | ✅ |
| `Nguyen Van A` | `Nguyễn Văn A` | 0,833 | ✅ |
| `Tram 110kV Bac` | `Trạm 110kV Bắc` | 0,857 | ✅ |

**Mất sạch dấu vẫn ăn gần đủ điểm.** ANLS gộp "lỗi dấu" và "lỗi nghĩa" vào **cùng một thang** → không đo được năng lực tiếng Việt.

**Phải nói chính xác cho đúng:** ca `hoá đơn` vs `hóa đơn` cho ANLS 0,714 và **đúng là phải cho điểm** — cả hai cách gõ đều hợp lệ. Vấn đề **không phải** "metric chấm sai", mà là **metric không phân biệt được hai loại lỗi có mức nghiêm trọng hoàn toàn khác nhau**.

---

## 3. CÔNG THỨC VÀ QUY TRÌNH QUAN TRỌNG

### 3.1 Công thức chấm điểm của đề — §4 đề bài

**Điểm một câu:**
```
Question_Score = 0,85 × ANLS + 0,15 × Evidence-F1
```

**Điểm bài nộp (thang 100):**
```
Score = 100 × (1/N) × Σ_{i=1}^{N} Question_Score_i
```

**Điểm hiển thị bảng xếp hạng:**
```
Final_Score = 100 × (Score − Min)/(Max − Min)   nếu Score > Min
            = 0                                  nếu Score ≤ Min
```

`Min` = ngưỡng tối thiểu do BTC quy định · `Max` = điểm cao nhất hiện có trên bảng.

**Hai điều rút ra từ công thức này:**

1. **85/15** → câu trả lời chi phối. Tối ưu ANLS trước, evidence sau. Nhưng 15% vẫn đủ để quyết định thứ hạng khi ANLS bão hoà.
2. **Chuẩn hoá theo `Max` động** → điểm của mình **tính lại mỗi khi có đội vượt `Max`**. Không phải điểm tuyệt đối. Điều này nghĩa là **điểm hiển thị không so sánh được giữa các thời điểm**.

### 3.2 ANLS — công thức đầy đủ

**Nguồn gốc thật:** τ = 0,5 **không** được định nghĩa trong paper DocVQA (`grep threshold` → 0 hit). Nguồn thật là **ST-VQA §3.4**. **Xác nhận chéo:** LiGT §5.2.3 in lại đúng công thức đó, độc lập.

**Công thức (LiGT eq. 7 và 8):**

```
ANLS = (1/N) × Σ_{i=0}^{N} s(a_i, o_i)

        ⎧ 1 − NL(a_i, o_i)   nếu NL(a_i, o_i) < τ
s(·) = ⎨
        ⎩ 0                  nếu NL(a_i, o_i) ≥ τ
```

Với `NL` = **khoảng cách Levenshtein chuẩn hoá** ∈ [0,1] · `τ = 0,5`.

**⚠️ Chi tiết dễ viết sai nhất — τ áp lên DISTANCE, không phải SIMILARITY.**

Viết sai thành `if similarity < τ: score = 0` → đảo ngược hoàn toàn ngữ nghĩa, hệ thống sẽ **thưởng cho câu trả lời sai**. Đây là bug im lặng: code chạy không lỗi, điểm chỉ tệ hơn.

**Công thức khoảng cách Levenshtein chuẩn hoá:**
```
NL(a, o) = Levenshtein(a, o) / max(|a|, |o|)
```
Chia cho `max` độ dài — không phải `min`, không phải trung bình.

**Trường hợp nhiều đáp án chuẩn:** `labels.jsonl` có `answers` là **danh sách**. Lấy `max` ANLS trên mọi đáp án được chấp nhận.

### 3.3 Evidence-F1 — quy trình

Đề chỉ nêu: *"một cặp vùng trên cùng trang được coi là khớp khi `IoU >= 0,5`"*.

**Các bước suy ra (đề không viết ra, phải tự cài):**

1. **Ghép cặp** predicted box ↔ gold box. **Điều kiện bắt buộc: cùng `page`.** Box khác trang **không bao giờ** khớp, dù toạ độ trùng khít.
2. **IoU** cho `[x1,y1,x2,y2]` chuẩn hoá:
```
IoU = diện tích giao / diện tích hợp
```
3. Cặp có `IoU ≥ 0,5` → tính là **khớp** (true positive).
4. **Precision / Recall / F1** trên **tập hợp** box (không phải trên từng box):
```
Precision = số cặp khớp / số box dự đoán
Recall    = số cặp khớp / số box gold
F1        = 2·P·R / (P + R)
```
5. **Ghép cặp phải là matching một-một** — một box dự đoán không được tính khớp hai lần với hai box gold.

**Chỗ dễ sai:** ghép cặp tham lam (greedy) theo thứ tự sẽ cho kết quả **khác** ghép cặp tối ưu. Đề không nói rõ dùng cách nào → phải tự kiểm chứng và ghi lại giả định.

**Nhớ lại ràng buộc:** mỗi câu có **2–6 vùng gold**. Nộp 1 box to trùm cả trang sẽ có Recall cao nhưng Precision thấp — F1 không cứu được.

### 3.4 Công thức TAPAS — toán tử mềm

**TAPAS Table 1** — ví dụ nguyên văn trong paper:

| op | P(op) | compute(op, Ps, T) | Kết quả |
|---|---:|---|---:|
| NONE | 0 | — | — |
| COUNT | 0,1 | .9 + .9 + .2 | 2 |
| SUM | 0,8 | .9×37 + .9×31 + .2×15 | 64,2 |
| AVG | 0,1 | 64,2 ÷ 2 | 32,1 |
| **Kỳ vọng** | | `spred = .1×2 + .8×64,2 + .1×32,1` | **54,8** |

**Dạng tổng quát (khả vi, dùng khi cần học mềm):**
```
COUNT(Ps)   = Σ_c ps(c)
SUM(Ps, T)  = Σ_c ps(c) · T[c]
AVERAGE     = compute(SUM) / compute(COUNT)
spred       = Σ_op P(op) · compute(op, Ps, T)
```

`ps(c)` = xác suất chọn cell `c` (trung bình logit token trong cell) · `T[c]` = giá trị số của cell `c`.

**Giá trị thực tế cho đề:** đây là công thức cho phép **huấn luyện** trên tập cell có xác suất. Nhưng nếu chỉ cần **suy luận**, dùng bản cứng đơn giản hơn: chọn cell có `ps > 0,5` rồi solver cộng.

### 3.5 Công thức LMDX — hộp bao nhỏ nhất

**LMDX Algorithm 2 (Appendix A.2), dòng 21:**
```
G.bounding_box = { min(b.x), min(b.y), max(b.x), max(b.y) }  trên mọi từ w ∈ W
```
Với `W` = tập từ thuộc entity.

**Quy trình đầy đủ của Algorithm 2:**
```
for mỗi cặp (text, segment_id) trong dự đoán:
    nếu segment_id ∉ M:        → bỏ qua (bịa ID)
    S = M[segment_id]           # tra segment gốc
    nếu text ⊄ S:              → bỏ qua (bịa text)
    W = W ∪ (S ∩ text)          # gom từ
G.value = nối text của mọi w ∈ W
G.bounding_box = hộp nhỏ nhất bao mọi w
```

**Áp dụng cho đề:** `M` chính là các block OCR của đề. Đây là cơ chế **đảm bảo 100% bbox nộp lên trỏ vào block có thật** — và nó khớp hoàn hảo với việc đề cho `block_id` sẵn trong `labels.jsonl`.

### 3.6 Quy trình nộp bài

```
submission.zip
|-- predictions.jsonl
```

- Trình chấm tìm `predictions.jsonl` ở **bất kỳ vị trí nào** trong ZIP, bỏ qua mọi tệp khác → nộp kèm notebook/mã nguồn không sao
- **Tên tệp phải đúng chính xác** `predictions.jsonl`
- Mỗi dòng **đúng ba trường**:
```json
{"question_id":"B-public-00000-q01","answer":"7","evidence":[{"page":1,"bbox":[0.10,0.20,0.30,0.40]}]}
```
- `answer`: chuỗi **không rỗng**
- Mỗi `question_id` xuất hiện **đúng một lần**
- Danh sách `question_id` phải **khớp hoàn toàn** với tập kiểm tra

**Các lỗi làm bài **không được chấm**: thiếu câu hỏi · thừa câu hỏi · trùng mã · trường không hợp lệ.

### 3.7 ⚠️ Công cụ của TA Minh KHÔNG dùng được làm metric chính

`scripts/evaluate_predictions.py` (91 dòng) trong repo TA Minh:

```python
answered = answer not in (None, "không xác định")
correct  = answered and answer in label["answers"]
```

**Hai vấn đề:**

1. **Dùng exact match, không dùng ANLS.** Trong khi ANLS chiếm **85% điểm thật**. Chấm bằng script này rồi tin theo → tối ưu sai mục tiêu.
2. **Không có Evidence-F1 gì cả.** 15% điểm hoàn toàn không được đo.

→ **Bắt buộc tự viết `anls.py` + `evidence_f1.py`** trước khi làm bất cứ điều gì khác. Không có thước đo đúng thì mọi thử nghiệm sau đó đều vô nghĩa.

### 3.8 Quy trình tách **ô lọc** khỏi **ô toán hạng** — và quy tắc cuối cùng đã thay thế nó

Đây là phát hiện vận hành quan trọng nhất khi viết solver. Ban đầu tôi giả định evidence của câu `sum` chứa **toàn bộ ô cần cộng** → solver cộng hết → chỉ đúng **34,1%**.

**Sai. Evidence trộn hai loại ô:**

| Loại | Là gì | Ví dụ |
|---|---|---|
| **Ô lọc** (filter) | Dùng để **định vị hàng** | `"Kế toán"`, `"30"`, `"Chăm sóc khách hàng"` |
| **Ô toán hạng** (operand) | Ô **cần cộng** | giá trị ở cột được hỏi |

#### Bước 1 (lịch sử) — quy tắc "chuỗi trong ngoặc kép": 34,1% → 99,4%

```python
QUOTED = re.compile(r"[“”\"]([^”\"]+)[“”\"]")

def split(question, ev):
    quoted = {q.strip().lower() for q in QUOTED.findall(question)}
    filt, ops = [], []
    for c in ev:
        (filt if c["clean_text"].strip().lower() in quoted else ops).append(c)
    return filt, ops
```

Quy tắc: ô nào có `clean_text` **trùng một chuỗi trong ngoặc kép** của câu hỏi → ô lọc, loại ra.

**Quy tắc này chạy được nhưng SAI về bản chất** — nó phụ thuộc vào câu hỏi và vỡ ở một ca rất cụ thể: **khi ô đáp án trùng giá trị với ô lọc**. Ví dụ `B-train-00086-q06`: hàng có `Thí sinh = 47` **và** `Đạt = 47`; chuỗi `"47"` bị coi là lọc ở **cả hai** ô → xoá luôn ô đáp án → không còn toán hạng nào. Đây chính là nguồn của 22 câu "thiếu" mà bản trước đổ lỗi cho *"dữ liệu bất thường"* (§2.5c điểm 3).

#### Bước 2 (chốt) — quy tắc **ô phải cùng của hàng**: → **100,00%**

```python
def rows(ev):
    g = defaultdict(list)
    for c in ev:
        g[(c["page"], c["table"], c["row"])].append(c)   # page BẮT BUỘC có trong khoá
    return {k: sorted(v, key=lambda c: c["column"]) for k, v in g.items()}
```

> Trong một hàng, **ô được hỏi luôn là ô ngoài cùng bên phải**. Ô điều kiện nằm bên trái nó.

Quy tắc này **không đọc câu hỏi**, nên không thể vỡ vì trùng chuỗi. Và nó khớp với bảng chọn evidence của TA Minh (§4.2): ô đáp án luôn được liệt kê **cuối cùng** trong mỗi hàng.

**Khoá hàng phải có `page`.** Thiếu `page` thì hai hàng cùng toạ độ `(table, row)` ở **hai trang khác nhau** bị gộp thành một → `cross_page_sum` mất một toán hạng (đo được: tụt còn 43/46). Đây là toàn bộ lỗi của `cross_page_sum`.

**Áp dụng cho từng kiểu (bản chốt):**

| Kiểu | Toán hạng | Toán tử |
|---|---|---|
| `sum` / `cross_page_sum` | **ô phải cùng** của mỗi hàng | cộng |
| `lookup` | ô phải cùng của hàng duy nhất | trả nguyên văn |
| `visual_bold_lookup` | ô phải cùng của hàng **có ô in đậm** | trả nguyên văn |
| `count` | đếm số hàng phân biệt `(page, table, row)` | đếm |
| `argmax` / `argmin` | **evidence CHỈ chứa hàng thắng** — không có gì để xếp hạng | trả **nhãn hàng** = ô trái nhất không phải số |
| `compare` | 2 hàng, mỗi hàng 1 giá trị ở ô phải cùng | so sánh, trả nhãn hàng thắng |

**⚠️ Bẫy `argmax`/`argmin` — dễ viết sai nhất:** evidence **không** chứa các hàng ứng viên để `max()` lên. Nó chỉ chứa **hàng đã thắng**. Viết `max(nums)` sẽ trả `None` (0% đúng). Đáp án đúng là **nhãn của hàng đó** — ô trái nhất không phải số.

**⚠️ Bài học phương pháp — quan trọng hơn cả quy tắc:** khi solver sai, **mặc định là lỗi mình, không phải lỗi dữ liệu**. Suy đoán *"3 tài liệu bất thường"* đã che mất một bug thật trong **hai phiên làm việc**. Xem §2.5c điểm 3.

### 3.9 ⚠️ Bẫy dấu phân cách số — 25,3% ô bị ảnh hưởng

Đo trên 256.040 ô (`audit_dataset.py` Q4):

| Định dạng | Số ô | % |
|---|---:|---:|
| Dùng `.` làm dấu nhóm nghìn (`15.838` = mười lăm nghìn tám trăm ba mươi tám) | **64.712** | **25,3%** |
| Dùng `,` làm dấu nhóm nghìn | **0** | 0% |

**Hai hệ quả ngược chiều nhau:**

1. **Khi ĐỌC ô → số:** `"15.838"` phải parse thành `15838`, **không phải** `15.838`. Quy tắc: `.` theo sau bởi **đúng 3 chữ số** và khớp `\d{1,3}(\.\d{3})+` → là nhóm nghìn → bỏ dấu chấm.
2. **Khi GHI số → chuỗi:** đáp án vàng viết `15838` hay `15.838`? **Phải kiểm trước khi nộp.** Nếu model sinh `15838` mà vàng là `15.838`, ANLS vẫn cao (lệch 1 ký tự / 6 → NL ≈ 0,167 < τ=0,5 → vẫn ăn 0,833) — **nhưng exact match thì trượt sạch**.

**Điểm an ủi:** vì τ = 0,5 khá rộng, lệch dấu phân cách **không giết điểm ANLS**. Đây là chỗ metric khoan dung và nó tha cho một lỗi lẽ ra rất tốn kém.

**Cũng phải xử lý số có dấu:** `'+1'`, `'-2'` xuất hiện thật trong dữ liệu. Regex chỉ cho `-?` sẽ **âm thầm nuốt mất toán hạng** → cộng thiếu. Phải dùng `[+-]?` và strip `+`.

---

## 4. CÁCH ÁP DỤNG TRONG THỰC TẾ

### 4.1 Thứ tự ưu tiên — **đã cập nhật sau khi đo**

| # | Việc | Trạng thái | Vì sao |
|---|---|---|---|
| **P0** | ~~Có dataset~~ | ✅ **Xong** | `data/training_set` 1100 doc · 11.000 câu · 256.040 ô |
| **P0b** | ~~Đo trần trích xuất~~ | ✅ **Xong — tách theo kiểu** (§2.5b) | 6/8 kiểu **100,0%** chuỗi con liền · `sum`/`cross_page_sum` **~0%** |
| **P0c** | ~~Kiểm evidence ↔ cell~~ | ✅ **Xong — 100%** (§2.5d) | Không gian chọn là **rời rạc, hữu hạn** |
| **P0d** | ~~Đo trần solver với evidence vàng~~ | ✅ **Xong — 100,00%** (§2.5c) | Bài toán **quy hết về chọn ô** |
| **P1** | Viết `anls.py` + `evidence_f1.py` | ⬜ **CHẶN TẤT CẢ** | Không có thước đúng thì không đo được gì |
| **P2** | Baseline **chọn cell** (không sinh toạ độ) | ⬜ | §2.1 — kiến trúc đúng; solver đã viết xong ở `audit_ceiling.py` |
| **P3** | Baseline **không cần model**: rule-based chọn ô bằng chuỗi trong ngoặc kép | ⬜ | §3.8 — quy tắc đã kiểm chứng; đo được ngay mức sàn |
| **P0e** | Viết `anls.py` + `evidence_f1.py` | ✅ **Xong** (§5.2 dòng 1) | Chấm lại trần dưới metric thật: **100,00** |
| **P4** | ~~Kiểm `ocr_source` của public/private test~~ | ✅ **Xong — rủi ro đóng** (§1.5) | Cả 3 split đều `btc_synthetic_clean_layout_v3` |
| ~~P5~~ | ~~Xử lý 3 tài liệu bất thường~~ | ❌ **Không tồn tại** (§2.5c) | Đó là **bug của solver**, không phải bất thường dữ liệu — đã sửa |

**Ba phép đo P0b/P0c/P0d trả lời ba câu khác nhau — đừng gộp chúng lại:**

| Phép đo | Câu hỏi | Kết quả |
|---|---|---|
| P0b (§2.5b) | Đáp án có **tồn tại** trong tài liệu không? | **Có, với 6/8 kiểu (100,0%).** Với `sum`/`cross_page_sum`: **không** — đáp án là số tính ra |
| P0c (§2.5d) | Evidence có phải **ô có thật** không? | **Có, 100%.** Chọn ô là bài toán **rời rạc** trên 256.040 ô, không phải hồi quy toạ độ |
| P0d (§2.5c) | Nếu chọn **đúng ô**, solver có ra **đáp án đúng** không? | **Có, 100,00%.** Bước tính toán **miễn phí hoàn toàn** |

**Thay đổi lớn so với bản trước:** lo ngại cũ là "trần trích xuất chỉ 76–81% theo LiGT, nên 20% điểm là bất khả thi". **Đo thật bác bỏ lo ngại đó** — trần solver-với-evidence-vàng là **100,00%**. Nghĩa là **không còn lý do trì hoãn P2**: solver thủ tục đã chạy đúng 100% trên evidence vàng, việc còn lại chỉ là **thay evidence vàng bằng evidence tự dự đoán**.

**Nhưng P0b cũng cảnh báo một điều:** 16,9% câu (`sum`, `cross_page_sum`) có đáp án **không tồn tại dưới dạng chuỗi nào**. Với nhóm này, **không được phép** dùng mẹo "trích chuỗi con từ OCR" — bắt buộc phải chạy solver số học. Nếu baseline P3 quên điều này, nó sẽ mất trắng 16,9% và không hiểu vì sao.

**Điều này đổi hẳn mức độ rủi ro của đề:** không phải "liệu có kịp không", mà là "bộ chọn ô đạt bao nhiêu %". Mọi nỗ lực nên dồn vào **một chỗ duy nhất: chất lượng chọn ô**.

### 4.2 Bài giải tham chiếu của TA Minh — **mốc phải vượt**

> Nguồn: `reference/Documents_2026-8_Giải đề OAI - Đề 1_[Reading]-OlympicAI2026-Problem1.pdf` (Trần Quang Minh · Đinh Quang Vinh, AI VIETNAM, 29 tr.)
> Code kèm theo: `Module 4/olp-ai-ptit-2026-preliminary-round/DocViVQA/`

**Pipeline của TA Minh (Hình 9, tr. 11) — trùng khớp với kiến trúc §4.3 ở dưới:**

```
Document Images ──► OCR inference ──► Bounding box (text + geometry)
                                            │
                                            ▼
                                     Table Reconstruction
                                            │
                                            ▼
                                  Candidate Rows and Cells
                                            │
Question ──► Intent and Constraint Extraction ──► Reasoning Router
                                            │
        ┌───────────┬────────────┬──────────┴─────────┬────────────┐
        ▼           ▼            ▼                    ▼            ▼
   Bold Row     Lookup      Aggregation          Ranking     Comparison
   Resolver     Solver        Solver              Solver        Solver
        └───────────┴────────────┴──────────┬─────────┴────────────┘
                                            ▼
                                      Answer, Evidence
```

**Đây là bằng chứng mạnh nhất rằng kiến trúc §4.3 đúng:** TA Minh độc lập đi tới **cùng một kết luận** — router phân loại ý định → solver chuyên biệt cho từng kiểu → trả `(answer, evidence)`. Không có VLM nào sinh toạ độ trong cả pipeline.

**Quy tắc dựng bảng của TA Minh (§3.3, tr. 12) — dùng để tái tạo `(table, row, column)` nếu cần:**

```python
header_x_range   = [0.23, 0.35]
header_center_x  = (x1 + x2) / 2        # ≈ 0.29
# cùng cột  ⇔  cell.x1 ≤ header_center_x ≤ cell.x2
# cùng hàng ⇔  cell.y1 ≤ row_y ≤ cell.y2
```

**Quy tắc chọn evidence của TA Minh (§3.5, tr. 13) — đối chiếu được với §2.5c:**

| Loại câu hỏi | Ô được đưa vào evidence |
|---|---|
| Lookup | Ô điều kiện xác định hàng + ô chứa đáp án |
| Count | Ô điều kiện của các hàng được đếm |
| Sum | Ô điều kiện của hai hàng + hai ô giá trị được cộng |
| Compare | Ô điều kiện và ô giá trị của **cả hai** hàng |
| Argmax / Argmin | Các ô tối thiểu để xác định hàng thắng + ô chứa giá trị cực trị |
| Cross-page Sum | Ô điều kiện + ô giá trị của **từng** toán hạng trên **mỗi** trang |
| Visual Bold Lookup | Ô điều kiện của **cả hai** hàng ứng viên + ô đáp án của hàng in đậm |

→ Khớp với số đo §2.5c: `rows-per-question` = 1 cho `lookup`/`argmax`/`argmin`, = 2 cho `sum`/`compare`/`visual_bold_lookup`/`cross_page_sum`. **Quy tắc "ô phải cùng của hàng" là hệ quả trực tiếp của bảng này** — ô đáp án luôn là ô cuối cùng bên phải được liệt kê.

**Kết quả đánh giá của TA Minh (§10, tr. 28) — mốc so sánh:**

| Loại suy luận | ANLS (%) | Evidence-F1 (%) | Tổng hợp (%) |
|---|---:|---:|---:|
| Lookup | 100,00 | 100,00 | 100,00 |
| Count | 100,00 | 100,00 | 100,00 |
| Sum | 100,00 | 100,00 | 100,00 |
| Argmax | 90,02 | 77,52 | **88,14** |
| Argmin | 89,00 | 76,49 | **87,12** |
| Compare | 100,00 | 100,00 | 100,00 |
| Cross-page Sum | 100,00 | 100,00 | 100,00 |
| Visual Bold Lookup | 96,90 | 74,82 | **93,59** |
| **Toàn bộ training set** | **96,25** | **90,89** | **95,45** |

**Đọc bảng này cho đúng — ba điều quan trọng:**

1. **Đây là mốc phải vượt, không phải mốc phải bằng.** 95,45% là kết quả **trên training set**, tức là có thể đã khớp tham số với tập đó. Cần tự đo lại trên cùng tập rồi mới so.
2. **Năm kiểu đã chạm trần 100%** (`lookup`, `count`, `sum`, `compare`, `cross_page_sum`) → **không còn dư địa ở nhóm này**. Toàn bộ khoảng cách nằm ở **`argmax`/`argmin`/`visual_bold_lookup`**.
   > *Đính chính (21/09):* bản đầu viết "sáu dạng còn lại (6.693 câu) đạt 100,00" — sai. Sáu dạng còn lại gồm cả `visual_bold_lookup`, mà dạng đó chỉ đạt 93,59 (bản TA Minh) / 82,99 (trần oracle đo lại). Đúng là **năm** dạng, tổng 6.693 câu.
3. **`Evidence-F1` luôn thấp hơn `ANLS` ở đúng ba kiểu đó** (77,52 < 90,02 · 74,82 < 96,90). Nghĩa là **chọn đúng ô khó hơn sinh đúng đáp án** — xác nhận định lượng cho §2.1. `visual_bold_lookup` lệch nặng nhất: đáp án đúng 96,90% nhưng evidence chỉ 74,82% → **đây là chỗ hở lớn nhất của bài giải TA Minh**, và là chỗ đáng tập trung nhất.

**Hai kỹ thuật của TA Minh đáng lấy, kèm cảnh báo:**

| Kỹ thuật | Nội dung | Dùng được không |
|---|---|---|
| **Đo độ đậm bằng stroke-width** (§8.1, tr. 26) | `cv2.distanceTransform` trên ảnh nhị phân hoá Otsu → `2 × mean(distance)`; lấy median theo hàng; ngưỡng `VISUAL_SCORE_MARGIN = 0.02` | ✅ **Lấy được** — thuần CV, không cần train, đúng cho `visual_bold_lookup` |
| **`BoldPairResNet18`** (§8.2, tr. 27) | ResNet18 hai nhánh, ghép đặc trưng 2×512 → `Linear(1024, 2)`; chỉ nhận khi `p ≥ 0.60` | ⚠️ **Chỉ khi stroke-width không đủ.** Thêm một model = thêm rủi ro, mà `visual_bold_lookup` chỉ chiếm 4,9% |

**Cảnh báo về chính bài giải TA Minh:** `submission_pipeline.ipynb` dùng `block_id: f"p{page}_h{index}"` — **định dạng `block_id` khác** với OCR của BTC (`p01_b00000`). Nếu copy nguyên code, evidence xuất ra sẽ **không khớp** `cell_annotations.jsonl`. Phải sửa lại theo `block_id` gốc.

### 4.2b Chẩn đoán chỗ TA Minh mất điểm — **đã mổ từ chính log của TA Minh**

> Nguồn: `olp-ai-ptit-2026-preliminary-round/DocViVQA/artifacts/analysis/diagnostics/`
> Gồm `argextreme_oracle.csv` (3.772 dòng) · `argextreme_rank2_failures.csv` (315) · `argextreme_table_summary.csv` (3.772).
> Đây là **log của TA Minh tự sinh**, không phải suy đoán của mình. Kiểm lại bằng `probe_mentor_arg.py`.

**Câu hỏi đặt ra:** `argmax`/`argmin` là hai trong ba chỗ TA Minh mất điểm (§4.2: 90,02 / 89,00 ANLS). Mất vì **đọc sai tài liệu**, hay vì **chọn sai hàng**?

**Trả lời — 403/403 đều là "đúng bảng, sai hàng":**

| Đo | Số | Nghĩa |
|---|---|---|
| Sai trên tổng 3.772 câu `argmax`/`argmin` | **403** (10,7%) — `argmax` 193 · `argmin` 210 | quy mô lỗi |
| `solver_table == expected_table` | **403/403 = 100%** | **chưa bao giờ sai bảng** |
| `solver_row == expected_row` | **0/403** | **luôn luôn sai hàng** |
| `expected_row_count == solver_row_count` | **3.772/3.772 = 100%** | phân đoạn bảng **không có lỗi** |

→ TA Minh **không hề đọc nhầm tài liệu**. Họ dựng bảng đúng, đếm hàng đúng, rồi **chọn nhầm hàng**. Toàn bộ 10,7% nằm ở **một quyết định duy nhất**.

**Vì sao chọn nhầm — hai nguyên nhân cơ học, đọc từ log:**

| Nguyên nhân | Số | Đọc ra |
|---|---|---|
| **Hai ứng viên gần bằng nhau** — `extreme_gap_ratio` median **0,165**; **120/315** ca gap < 0,10 · **185/315** ca gap < 0,25 | 315 dòng rank-2 | **Hơn nửa số lỗi là suýt soát**, không phải đọc sai số. Đây là bài toán **phân biệt tinh**, không phải bài toán OCR |
| **Khoá hàng bị hiểu sai khi ô định danh trải nhiều ô vật lý** — `solver_entity_physical_cell_count != expected_...` | **262/403** | Sai khác điển hình: `solver=1, expected=2` (78 ca) và `solver=2, expected=1` (36 ca) → **định nghĩa "một hàng"** khi ô khoá bị gộp/trải là nguyên nhân chính |
| **Khoá hàng lặp lại** — `solver_seen_before = True` | **220/403** (False: 95) | Ở 220 ca, hàng sai **đã từng xuất hiện** → cạm bẫy **khoá trùng** |
| Bảng càng nhiều hàng càng dễ sai — `num_logical_rows` đỉnh ở **12** (72 ca), trải 6–22 | 403 | bảng lớn là chỗ lỗi tập trung |

**Và đây là con số quyết định hướng Tuần 2:**

> **Solver của mình chạy trên đúng 403 câu đó, với evidence vàng: 403/403 = 100,00%.**

Nghĩa là **không có câu nào trong 403 câu đó là bất khả thi**. Quy tắc "ô phải cùng của hàng" (§3.8) giải được **toàn bộ** chỗ TA Minh mất 10,7% — với điều kiện **chọn đúng hàng**. Khoảng cách giữa 95,45% của TA Minh và trần 100% **nằm trọn ở bộ chọn**, đúng như §2.5c đã kết luận.

⚠️ **Đọc con số này cho đúng — đây KHÔNG phải "mình giỏi hơn TA Minh":**

1. **Cả hai bên đều dùng evidence vàng.** 403/403 nói *"nếu biết hàng rồi thì giải được"*, **không** nói *"mình tìm được hàng"*. Bộ chọn ô — thứ TA Minh có và mình **chưa có** — vẫn là bài toán chưa giải.
2. **`argextreme_oracle.csv` là log chẩn đoán**, không phải bảng điểm nộp. Nó chạy trên tập con `argmax`/`argmin` với cơ chế riêng, không phải pipeline nộp bài. Đừng trích 403/403 như thể là điểm thi.
3. **Bài học phương pháp đáng giữ nhất:** TA Minh để lại **log chẩn đoán đủ chi tiết** để người sau mổ được lỗi của họ. Đây là thứ nên **tự làm** cho pipeline của mình ngay từ Tuần 2 — ghi `expected_*` cạnh `solver_*` cho **mọi** câu, không chỉ câu sai.

### 4.3 Kiến trúc suy ra từ các nguyên lý trên

```
Ảnh + OCR + câu hỏi
        │
        ├─► [1] Router: phân loại reasoning_type
        │         (8 lớp, hoặc gộp: lookup | tính toán | so sánh)
        │
        ├─► [2] Chọn cell  ← MODEL làm việc này
        │         dùng cell_annotations.jsonl (row, column, is_bold, is_header)
        │
        ├─► [3] Thi hành toán tử  ← SOLVER THỦ TỤC, không phải model
        │         sum / count / argmax / argmin / compare / cross_page_sum
        │
        └─► [4] Grounding Verification (LMDX Alg. 2)
                  ánh xạ đáp án → block_id → bbox có thật
                  loại mọi bbox không trỏ vào block tồn tại
```

**Điểm mấu chốt:** bước [3] **không có model**. Đó là chỗ loại bỏ hallucination về mặt số học, không phải bằng cách "prompt cẩn thận hơn".

### 4.4 Ánh xạ từng loại câu hỏi sang cơ chế

| Kiểu | Cơ chế | Cần gì |
|---|---|---|
| `lookup` | Chọn 1 cell → trả `clean_text` | Selector |
| `sum` | Chọn n cell → **cộng** | Selector + solver |
| `count` | Chọn n cell → **đếm** | Selector + solver |
| `argmax` | Chọn **cột** → tìm **dòng** max → trả nhãn dòng | Selector + solver |
| `argmin` | Như trên, min | Selector + solver |
| `compare` | Chọn 2 cell → so sánh → trả kết quả | Selector + solver |
| `cross_page_sum` | Chọn cell **trên 2 trang** → cộng | Selector + solver (chú ý `page`) |
| `visual_bold_lookup` | Lọc `is_bold == True` → chọn | Selector + **cột `is_bold`** |

**`cross_page_sum` — đã xem dữ liệu thật, hết bí ẩn:** mọi câu mẫu đều có `pages = [1, 2]` và **đúng 6 vùng evidence** (3 ô lọc + 3 ô toán hạng, hoặc tương đương). Solver thủ tục giải được **46/46 = 100%**. Không cần cơ chế đặc biệt nào ngoài việc **đừng quên `page` khi tra cell** — hai trang có thể có bbox trùng nhau về giá trị.

**`visual_bold_lookup` là món quà:** đề cho sẵn `is_bold` ở mức cell trong `cell_annotations.jsonl`. Không paper nào trong reading list khai thác bold. 535 câu — solver hiện tại lấy **535/535 = 100,0%** (§2.5c).

### 4.5 Những điều KHÔNG nên làm

| ❌ Không làm | Vì sao |
|---|---|
| Hỏi VLM toạ độ trực tiếp | IoU .011–.048 vs ngưỡng .5 (§2.1) |
| Fine-tune span-head extractive | Thua generative ~20 ANLS trên tiếng Việt (§2.6) |
| Lọc bỏ câu hỏi abstractive | Chúng là 75,1% bài toán (§1.3) |
| Nhồi layout vào prompt dạng text | Mất thông tin 2D — TAPAS Table 6: bỏ `{cols,rows}` → SQA tụt **19,6 điểm** |
| Dùng model context ngắn | `cross_page_sum` cần 2 trang; LayoutLMv3 L=512, DocLLM 1.024 token |
| Dùng `evaluate_predictions.py` làm metric chính | Exact match, không có Evidence-F1 (§3.7) |
| Khớp đáp án bằng `in` thô | Bẫy 10 điểm ảo (§2.5) |
| Viết `if similarity < τ` | τ áp lên **distance** (§3.2) |

### 4.6 Kiến thức nào dùng ở đâu — bảng tra nhanh

| Công thức / quy trình | Lấy từ | Dùng để |
|---|---|---|
| `0,85×ANLS + 0,15×Evidence-F1` | §4 đề | Viết metric |
| ANLS τ=0,5 trên **distance** | ST-VQA §3.4 · LiGT §5.2.3 | Viết `anls.py` |
| IoU ≥ 0,5 + matching cùng trang | §4 đề | Viết `evidence_f1.py` |
| Chọn cell `ps > 0,5` rồi solver thi hành | TAPAS (inference) | Kiến trúc chính |
| `COUNT = Σ ps(c)` · `SUM = Σ ps(c)·T[c]` | TAPAS Table 1 | Nếu cần học mềm |
| Hộp nhỏ nhất bao mọi từ | LMDX Alg. 2 dòng 21 | Sinh bbox từ block |
| Kiểm tra segment ID + substring | LMDX Alg. 2 dòng 10–16 | Xác thực, chống bịa |
| Giữ thông tin cột/dòng | TAPAS Table 6 | Không flatten bảng |
| `is_bold` mức cell | `cell_annotations.jsonl` | `visual_bold_lookup` |
| 87,00 vs 77,00 substring/subsequence | DocVQA Table 1 | Cảnh báo bẫy khớp chuỗi |
| **Tách ô lọc (chuỗi trong ngoặc kép) khỏi ô toán hạng** | **Tự đo trên olp-ai-ptit (§3.8)** | **Solver `sum` 34,1% → 99,4%** |
| **`argmax`/`argmin` = trả nhãn hàng, không phải `max()`** | **Tự đo trên olp-ai-ptit (§3.8)** | **Tránh 0% đúng** |
| **`.` là dấu nhóm nghìn (25,3% số ô)** | **Tự đo trên olp-ai-ptit (§3.9)** | **Parse số đúng** |
| **Trần 100,00% khi có evidence vàng** | **Tự đo trên olp-ai-ptit (§2.5c)** | **Chứng minh: chỉ cần tối ưu bộ chọn** |

---

## 5. TỰ HỆ THỐNG LẠI KIẾN THỨC

> **Phần này nhóm phải tự viết lại bằng lời của mình.** Bản dưới là khung gợi ý — dùng để đối chiếu, không copy.

### 5.1 Phần đã hiểu

- **Bài toán là hai bài toán ghép lại**, không phải một. Trả lời (85%) và định vị (15%) có **cơ chế lỗi khác nhau hoàn toàn** → phải đo riêng, sửa riêng.
- **75,1% câu hỏi không phải bài tra cứu.** `lookup` chỉ 20%. Đây là điều quyết định kiến trúc: mọi thứ thiết kế cho `lookup` sẽ bỏ rơi 3/4 bài toán.
- **Bằng chứng là bài toán CHỌN.** Số đo .011–.048 vs ngưỡng .5 là khoảng cách một bậc độ lớn, không phải khoảng cách tinh chỉnh.
- **Tách chọn khỏi tính** (TAPAS) là pattern trung tâm: model chọn cell, solver thủ tục thi hành toán tử.
- **ANLS τ=0,5 áp lên distance**, không phải similarity. Viết ngược là bug im lặng.
- **Metric của TA Minh không dùng được** — exact match, thiếu Evidence-F1.
- **Tiếng Việt đổi luật chơi:** extractive thua generative ~20 ANLS, vì lỗi dấu thanh phá giả định "đáp án nằm nguyên văn".
  - **⚠️ Nhưng đã tự bác bỏ một phần:** OCR của olp-ai-ptit là **tổng hợp, sạch** (`btc_synthetic_clean_layout_v3`) → **không** có lỗi dấu để nói tới. Lập luận "chọn thay vì sinh" **vẫn đúng**, nhưng phải viện lý do khác: **75,1% câu hỏi không có đáp án nguyên văn** (§1.3). Ghi trung thực chỗ này (§2.6).

**Bổ sung sau khi đo trên dữ liệu thật (2026-09-17):**

- **Toàn bộ bài toán quy về MỘT bước: chọn ô.** Đưa evidence vàng + solver thủ tục thuần Python → **100,00% đúng**, không có model nào (§2.5c). Đây là con số quan trọng nhất của cả file — nó biến "nguyên lý" thành "sự kiện đo được".
- **Evidence là ô bảng, không phải hộp tự do.** 39.937/39.937 vùng khớp **chính xác** một bbox trong `cell_annotations.jsonl` (§2.5d) → không gian tìm kiếm **rời rạc và hữu hạn**, không phải hồi quy toạ độ.
- **Câu hỏi tự mô tả cấu trúc.** Chúng ghi rõ *"bảng 1 ở trang 1"*, và evidence **đã bị cắt sẵn** còn đúng các hàng liên quan → phần lớn thao tác chỉ còn là đọc hàng. Nhưng **đừng** dựa vào việc trích giá trị trong ngoặc kép để tách ô lọc khỏi ô toán hạng: quy tắc đó **đã bị bác bỏ** (§3.8 bước 1). Quy tắc đúng là **ô phải cùng của hàng là ô được hỏi** (§3.8 bước 2).
- **`argmax`/`argmin` không phải bài toán xếp hạng.** Evidence **chỉ chứa hàng đã thắng**. Đáp án là **nhãn hàng**, không phải `max()` (§3.8).
- **`cross_page_sum` không có gì bí ẩn.** `pages=[1,2]`, 6 vùng, solver 46/46 = 100% (§2.5c). ⚠️ Nhưng phải khoá hàng theo `(page, table, row)` — bỏ `page` thì tụt còn 43/46.
- **Ràng buộc "2–6 vùng" của đề không đúng tuyệt đối.** ~1,2% số câu có 7–10 vùng (§1.4) — code cứng `<= 6` sẽ mất điểm oan.

### 5.2 Phần còn thiếu

> **Cập nhật 2026-09-17 (sau khi có data):** phần lớn bảng cũ đã **giải quyết xong**, chuyển thành **phần đã hiểu** (§5.1). Bảng dưới giữ lại cả dòng đã xong (đánh dấu ✅) để thấy đường đi, xen với các gap **còn thật**.

| # | Thiếu gì | Ảnh hưởng | Ưu tiên |
|---|---|---|---|
| 1 | ~~**Chưa có `anls.py` / `evidence_f1.py`**~~ | ✅ **ĐÃ VIẾT** — `anls.py` + `evidence_f1.py`, mỗi file có self-check chạy được (`python anls.py`). Đã chấm lại trần: **100,00 dưới metric thật**, không phải artefact của exact-match | ✅ xong |
| 2 | **Chưa biết đề định nghĩa Evidence-F1 chính xác thế nào** | Đề chỉ nói "IoU ≥ 0,5". Ghép cặp greedy hay tối ưu? Box thừa có bị phạt? | 🔴 **hỏi TA** |
| 3 | ~~**Chưa kiểm `ocr_source` của public/private test**~~ | ✅ **ĐÃ KIỂM — rủi ro đóng.** Cả ba split đều `btc_synthetic_clean_layout_v3` (40/40 · 40/40 · 40/40) → kết luận đo trên train chuyển thẳng sang test được | ✅ xong |
| 4 | **Chưa chạy được end-to-end** | Solver đúng 100,00% trên evidence **vàng**. Chưa biết đúng bao nhiêu trên evidence **tự dự đoán** — đây mới là điểm thật | 🟠 P2 |
| 5 | **Chưa có bộ chọn ô** | §2.5c chỉ ra: **toàn bộ điểm nằm ở đây**. Hiện chưa có model nào. Đã lượng hoá được khoảng cách: **403/403 câu TA Minh sai đều giải được nếu chọn đúng hàng** (§4.2b) | 🟠 P2 |
| 6 | ~~**Chưa hiểu 3 tài liệu bất thường**~~ | ❌ **KHÔNG TỒN TẠI.** `B-train-00086/00113/00176` không bất thường — 22 câu "thiếu" là **bug của solver** (ô đáp án trùng giá trị ô lọc → bị regex xoá nhầm). Đã sửa, trần lên 100,00%. **Bài học: solver sai thì mặc định là lỗi mình** (§3.8) | ✅ xong |
| 7 | **Chưa kiểm chứng chất lượng annotation của đề** | BoundingDocs ước ~7% nhãn sai. Nhưng evidence khớp cell **100%** (§2.5d) → nghi vấn này **giảm mạnh** | 🟢 thấp |
| 8 | **Chưa xác minh quy ước `page` khi nộp** | `labels.jsonl` là 1-based. File nộp? Lệch 1 → mất trắng Evidence-F1 | 🟡 hỏi TA |
| 9 | **Chưa xác minh định dạng số của đáp án** | Vàng ghi `15838` hay `15.838`? Ảnh hưởng exact match (không ảnh hưởng ANLS — §3.9) | 🟢 thấp |
| 10 | **Chưa đọc BoundingDocs §4.6 / §3.4 và DocExplainerV0 Table 1 bản gốc** | Các số đang dùng qua trung gian file GAP CHUNG | 🟡 |

**Ba dòng đã XOÁ khỏi bảng trên vì đã giải quyết:**

| Dòng cũ | Kết quả thật |
|---|---|
| ~~Chưa có data của olp-ai-ptit~~ | ✅ **Có.** 1.100/11.000/256.040 train · 100/1.000 public · 200/2.000 private — **khớp đúng đề** (§1.5) |
| ~~Chưa đo trần trích xuất trên olp-ai-ptit~~ | ✅ **Đo rồi — và kết quả ban đầu là DƯƠNG TÍNH GIẢ.** 85,7% chuỗi con liền · 14,3% "dãy con" (toàn bộ là `sum`/`cross_page_sum`, đáp án tính ra nên không tồn tại) · 0,1% không khớp gì. **Sáu trong tám kiểu đạt 100,0% chuỗi con liền** (§2.5b) |
| ~~Chưa biết `cross_page_sum` xử lý sao~~ | ✅ **Rồi.** `pages=[1,2]`, đúng 6 vùng evidence, solver giải **46/46 = 100%** (§2.5c) |

### 5.3 Vấn đề có thể tiếp tục tìm hiểu

1. ~~**Đề định nghĩa Evidence-F1 chính xác thế nào?** — Ghép cặp tham lam hay tối ưu? Box thừa có bị phạt không?~~ ✅ **ĐÃ ĐÓNG — BTC trả lời.** Nguyên văn: *"Nên dùng one-to-one matching với IoU ≥ 0.5; Hungarian hoặc greedy đều được nếu nhất quán. Prediction thừa vẫn làm giảm precision nên không nên sinh quá nhiều box."* `code/evidence_f1.py` **đã đúng y hệt** từ đầu (ghép 1-1 cùng trang, `prec = matched / len(pred)` nên box thừa bị phạt) — không phải sửa một dòng. Ba phép đo kèm theo: (a) `probe_greedy_vs_hungarian.py` trên cả 11.000 câu cho **0 khác biệt** giữa tham lam và tối ưu, vì **không box dự đoán nào chạm được 2 box vàng** — câu hỏi con "tham lam hay tối ưu" **vô nghĩa trên dataset này**; (b) 13,0% câu (1.431/11.000) sinh box thừa trong Cấu hình B, EvF1 có phạt 0,9447 vs không phạt 0,9665 ⇒ **luật phạt đáng −0,0033 điểm cuộc thi**; (c) `evidence_f1.py` self-check có assert cho cả phạt box thừa lẫn không khớp khác trang.

2. **Trần trích xuất của olp-ai-ptit là bao nhiêu?** — ✅ **Đã đo (§2.5b): 100,0% với 6 kiểu tra cứu, ~0% với 2 kiểu tính toán.** Con số 76–81% của LiGT là trên hoá đơn tiếng Việt, **không** chuyển sang được — vì OCR ở đây là tổng hợp sạch. **Bài học phương pháp:** một con số trần gộp cho cả dataset là vô nghĩa; phải tách theo `reasoning_type` mới thấy sự thật.

3. **`visual_bold_lookup` có lấy được gần trọn bằng `is_bold` không?** — Đề cho sẵn tín hiệu bold, không paper nào khai thác. 535 câu. ✅ **Trần đã biết: 535/535 = 100% khi có evidence vàng** (§2.5c) — nên câu hỏi thật chỉ còn là **bộ chọn** có tìm đúng ô bold không. Và đây đúng là chỗ **hổng to nhất của TA Minh**: §10 cho 96,90 ANLS nhưng chỉ **74,82 Evidence-F1** (§4.2).

4. **`argmax`/`argmin` có thực sự chỉ là "chọn cột rồi tìm max"?** — ✅ **Trả lời rồi: không phải xếp hạng gì cả.** Evidence **chỉ chứa hàng đã thắng**, nên đáp án là **nhãn hàng** (§3.8). Còn lại: bộ chọn phải tìm ra hàng nào thắng — và đây là **hai trong ba chỗ TA Minh mất điểm** (90,02 / 89,00 ANLS — §4.2).

   ✅ **Và nay đã mổ được chính xác chỗ khó (§4.2b):** TA Minh sai **403/3.772** câu, **403/403 đúng bảng nhưng sai hàng**, trong khi số hàng khớp **3.772/3.772**. Hai nguyên nhân: **120/315 ca hai ứng viên gần bằng nhau** (gap < 0,10) và **262/403 ca định nghĩa "hàng" lệch khi ô khoá trải nhiều ô vật lý**. → **Câu hỏi Tuần 2 không còn là "argmax khó ở đâu" mà là "làm sao chọn đúng hàng khi hai ứng viên suýt soát"**. Đây là bài toán **so sánh tinh**, không phải OCR.

5. **Lỗi OCR dấu thanh ảnh hưởng bao nhiêu?** — ✅ **Đã đóng (P4).** Cả ba split đều `btc_synthetic_clean_layout_v3` → **không split nào dùng OCR thật**. Lập luận "tiếng Việt có dấu làm OCR sai" **không áp dụng cho đề này** (§1.5). Con số LiGT 76–81% là trên hoá đơn chụp, **không chuyển sang được**.

6. **ANLS có phải metric đúng cho tiếng Việt?** — Đây là nội dung **O-B** trong `WEEK01 - Output dự kiến (first-principle + reverse thinking).md` §3.3. Đã có bằng chứng sơ bộ (§2.7), cần mở rộng thành bộ test có hệ thống.

### 5.4 Việc cần làm ngay

- [ ] **Tự đọc lại** DocVQA Table 1 (bẫy 87 vs 77) và DocExplainerV0 Table 1 (bảng ANLS vs MeanIoU) — **bản gốc, không qua file trung gian**
- [ ] **Tự chạy lại** bảng test ANLS tiếng Việt ở §2.7 — đừng tin số trong file này
- [x] ~~**Viết `anls.py` + `evidence_f1.py`** (P1)~~ — **XONG.** `anls.py` (τ=0,5 áp lên **distance**, best-of-`answers`, số vi-VN coi là bằng nhau) và `evidence_f1.py` (khớp 1-1 cùng trang, IoU ≥ 0,5, ghép tham lam + bản `_optimal` để đối chứng). Mỗi file có `__main__` self-check. **Còn phải hỏi TA** cách ghép cặp chính thức (§3.3)
- [ ] **Hỏi TA** về: quy ước `page`, cách ghép cặp Evidence-F1, và xác nhận có OCR + `cell_annotations` cho public/private test không
- [ ] **Chốt output + viết outline Tuần 1** vào `Working Files/` (bắt buộc cuối Tuần 1, §II.5)
- [ ] Cập nhật Paper Tracker nếu thêm paper mới

---

## 6. NGUỒN

| Nội dung | Nguồn | Đã tự kiểm chứng? |
|---|---|---|
| Định dạng đề, 8 kiểu reasoning, cấu trúc nộp, công thức chấm | `reference/exam_question_docvqa.md` §1–§4 | ✅ đọc trực tiếp |
| Quy chế, mốc tuần, quy định AI | `reference/Document hướng dẫn Topic Team.pdf` §II.1, §II.3, §II.5, §III.3 | ✅ đọc trực tiếp |
| ANLS (τ=0,5 trên distance), công thức eq. 7–8 | ST-VQA · arXiv 1905.13648 §3.4 · **LiGT §5.2.3** | ⚠️ **chưa đọc ST-VQA gốc** — công thức lấy từ LiGT |
| LiGT Table 5 (extractive vs generative, tiếng Việt) | arXiv 2502.19202 | ⚠️ qua file trung gian |
| Toán tử mềm TAPAS, Table 1, Table 6, inference `ps > 0,5` | arXiv 2004.02349 §2 | ✅ grep trực tiếp |
| LMDX Algorithm 2 (hộp bao nhỏ nhất, grounding) | arXiv 2309.10952 Appendix A.2 | ✅ grep trực tiếp |
| DocExplainerV0 bảng ANLS vs MeanIoU | arXiv 2509.10129 | ⚠️ qua file trung gian |
| DocVQA Table 1 (substring 87 / subsequence 77) | arXiv 2007.00398 §5.1 | ✅ grep trực tiếp |
| BoundingDocs (~7% nhãn sai, §3.4; IoU §4.6) | IJDAR (2026) · arXiv 2501.03403v3 | ⚠️ qua file trung gian |
| Tổng hợp gap 10 paper | `papers/GAP CHUNG - 10 paper va huong ap dung.md` | — |
| Metric của TA Minh (exact match, thiếu Evidence-F1) | `DocViVQA/scripts/evaluate_predictions.py` | ✅ đọc trực tiếp |
| Chẩn đoán lỗi `argmax`/`argmin` (403 câu) | `DocViVQA/artifacts/analysis/diagnostics/argextreme_*.csv` — kiểm bằng `probe_mentor_arg.py` | ✅ tự chạy lại |

**⚠️ Cảnh báo về độ tin cậy:** các dòng đánh dấu *"qua file trung gian"* là số liệu **chép lại từ file tổng hợp của nhóm**, chưa đối chiếu bản gốc trong phiên này. Trước khi dùng làm trích dẫn chính thức, **phải tự mở PDF kiểm lại** — nhất là DocExplainerV0 Table 1 và LiGT Table 5, vì hai bảng này là chỗ chống lưng cho toàn bộ lập luận ở §2.1 và §2.6.
