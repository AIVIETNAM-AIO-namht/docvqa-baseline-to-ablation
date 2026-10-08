# docvqa-baseline-to-ablation

Hỏi đáp trên ảnh tài liệu (**Document VQA**) — lời giải cho vòng loại *OLP AI PTIT 2026*.

Bắt đầu từ baseline của mentor (**0,9545**), dựng một hệ luật thuần Python đạt **0,968**,
rồi đo trần của từng tầng mô hình học sâu trước khi quyết định có dựng hay không.

Điểm đáng chú ý không nằm ở con số cuối, mà ở chỗ **hai tầng mô hình đều cho kết luận âm
có bằng chứng đo được** — và phần lớn công sức của dự án là chứng minh điều đó bằng số liệu
thay vì bằng phỏng đoán.

---

## Kết quả

| Cấu hình | Mô tả | Điểm (all) | Trạng thái |
|---|---|---:|---|
| **A** | Baseline mentor | 0,9545 | đối chứng |
| **B** | Hệ luật thuần Python | **0,968** | đã dựng |
| **C** | + LayoutLMv3 / LayoutXLM | — | **kết luận âm** (không dựng) |
| **D** | + Qwen2.5-VL | — | **kết luận âm** ở zero-shot |

Cấu hình B theo split: **0,967** (dev) · **0,972** (eval) · **0,968** (all).
Chênh dev − eval = 0,005 ⇒ không có dấu hiệu overfit theo tài liệu.

Phân rã theo dạng câu hỏi (11.000 câu, thang điểm cuộc thi):

| Dạng | Số câu | ANLS | Evidence-F1 | Điểm |
|---|---:|---:|---:|---:|
| `lookup` | 2.200 | 1,000 | 1,000 | 1,000 |
| `sum` | 1.810 | 1,000 | 1,000 | 1,000 |
| `compare` | 1.722 | 1,000 | 1,000 | 1,000 |
| `count` | 915 | 1,000 | 1,000 | 1,000 |
| `cross_page_sum` | 46 | 1,000 | 0,757 | 0,964 |
| `argmax` | 1.898 | 0,946 | 0,878 | 0,936 |
| `argmin` | 1.874 | 0,936 | 0,867 | 0,926 |
| `visual_bold_lookup` | 535 | 0,839 | 0,783 | 0,831 |

Trần oracle toàn hệ thống: **99,17%** (10.909/11.000). Phần điểm mất tập trung ở
`argmin` (39,4%) · `argmax` (34,5%) · `visual_bold_lookup` (25,7%).

---

## Bài toán

Mỗi câu hỏi kèm một ảnh tài liệu chứa **nhiều bảng**. Phải trả về:

```json
{"question_id": "...", "answer": "...", "evidence": [{"page": 1, "bbox": [x0, y0, x1, y1]}]}
```

Điểm mỗi câu = `0,85 × ANLS + 0,15 × Evidence-F1`. Tám dạng câu hỏi, từ tra cứu ô
(`lookup`) tới cực trị theo hàng (`argmax`/`argmin`) và tra cứu theo định dạng chữ
(`visual_bold_lookup` — "ô in đậm ở cột X").

**Ràng buộc hợp lệ:** lời giải **không được đọc file nhãn** (`labels.jsonl`,
`cell_annotations.jsonl`). Nhãn chỉ dùng để chấm điểm. Phép kiểm hợp lệ tự động:
đổi tên file nhãn rồi chạy lại — kết quả phải không đổi.

---

## Cách tiếp cận

### Lưới bảng tái dựng từ OCR, không từ nhãn

`code/grid_ocr.py` dựng lưới `(table, row, column)` thuần hình học: gom block OCR theo
`y0`, sắp theo `x0`. Đối chiếu với lưới vàng: **0 hàng trộn 2 bảng, 0 hàng sai thứ tự
cột / 256.040 ô, 30.662 hàng** (`code/verify_grid.py`).

### `is_bold` đo từ ảnh

`is_bold` là trường **duy nhất không có tương ứng trong OCR** — đề bài ghi rõ
*"OCR không ghi nhận định dạng chữ"*. Đo độ dày nét từ ảnh trang (tỉ lệ pixel tối sống
sót sau bào mòn 1 vòng, bỏ phiếu theo cột). Năm phép đo chuẩn hoá khác nhau đều cho
cùng kết quả ⇒ đây là **trần của tín hiệu ảnh**, không phải lỗi cài đặt.

### Giao thức chống overfit

`training_set` chia theo **tài liệu** (không chia theo câu hỏi — nhiều câu dùng chung một
tài liệu): **880 dev / 220 eval** tài liệu, seed 20260921. Luật chốt trên dev, chỉ đo
eval sau khi chốt. Mỗi cấu hình báo cáo **hai** con số; chênh dev − eval là thước đo
overfit trực tiếp. `public_test` chỉ dùng làm kiểm tra cuối.

---

## Hai kết luận âm

Đây là phần đóng góp chính. Cả hai đều là **đo trần trước khi dựng model**, và cả hai
đều tiết kiệm nhiều ngày GPU cho một hướng đã biết là âm.

### Cấu hình C — tín hiệu không gian không tồn tại

Kế hoạch ban đầu: dựng LayoutLMv3/LayoutXLM để khai thác **tín hiệu không gian** của hàng.
Trước khi dựng, đo trần của mọi bộ lọc hàng tĩnh cho `argmax`/`argmin`:

| Split | Câu | B đúng | Trần (biết trước hàng vàng) | Dư địa |
|---|---:|---:|---:|---:|
| dev | 3.024 | 93,49% | 99,14% | +5,65 đ% |
| eval | 748 | 94,12% | 98,93% | +4,81 đ% |

Dư địa +5,65 điểm % nghe hấp dẫn — nhưng là **oracle-only**. Kiểm bằng 4 họ luật
không-cần-nhãn: **0 họ chạm trần**.

| Họ luật | Kết quả (dev) |
|---|---|
| Khử trùng văn bản | 39,0 – 66,7% (baseline 93,5%) — phản tác dụng |
| Hàng in đậm đo từ ảnh | 10,4% |
| Từ khoá hàng tổng | không phân biệt được (27,2% vs 28,5%) |
| Hình học hàng | cao độ **đồng nhất tuyệt đối** (0,02121), khe hở **bằng 0** |

Phép đo chốt — trong đúng **197 câu B làm sai**, tín hiệu thị giác tốt nhất trỏ đúng hàng
vàng chỉ **9,1%**; trong **79,2%** nó đo được nhưng chỉ vào một hàng **thứ ba** ⇒ nhiều
hàng cùng "nổi bật", và nổi bật **không tương quan** với hàng đúng.

⇒ **Không dựng LayoutLMv3.** Loại tín hiệu mà nó được kỳ vọng khai thác đã đo là
*không tồn tại* trong dữ liệu này. Kết luận này trả lời trực tiếp câu hỏi nghiên cứu:
*mô hình học sâu chỉ thực sự cần thiết ở loại lỗi nào?*

### Cấu hình D — zero-shot không đọc được độ đậm

`visual_bold_lookup` là dạng **duy nhất** có trần dưới 100% (82,99%), vì nó phụ thuộc
`is_bold` — trường không có trong OCR. Câu hỏi mở: 82,99% là trần của **tín hiệu ảnh**,
hay chỉ là trần của **một phép đo độ dày nét**? VLM đọc ảnh trực tiếp là phép thử duy nhất
còn lại.

Chạy Qwen2.5-VL-3B zero-shot trên 120 câu (Colab T4), đối chứng là đúng nhánh BOLD của
Cấu hình B:

| Nhánh | ANLS | EvF1 | Điểm | Chọn đúng hàng |
|---|---:|---:|---:|---:|
| B (đo độ dày nét) | 0,827 | 0,769 | **0,818** | 96/120 |
| D (Qwen2.5-VL zero-shot) | 0,555 | 0,704 | **0,578** | **60/120** |

Chênh **−0,241**. 60/120 chọn đúng = **đúng mức đoán bừa**. Thang sanity 4 bậc chỉ ra
nguyên nhân: model **chép đúng chữ cả hai dải** nhưng **không so sánh được độ đậm** —
đảo dải thì chữ không lật (0/10), đổi nhãn thì chữ đứng yên (10/10) ⇒ **chọn theo vị trí**.
Lỗi nằm ở **tầng so sánh**, không phải tầng thị giác.

Luật quyết định đã ghi trong script **trước khi chạy** (`D − B ≥ +0,03` → dựng D + QLoRA;
`≤ 0` → dừng). Kết quả −0,241 ⇒ dừng nhánh zero-shot.

---

## Cấu trúc repo

```
Slot 1/
  Working Files/
    code/                  # toàn bộ harness và probe
      grid_ocr.py            # tái dựng lưới bảng từ OCR + ảnh (không đọc nhãn)
      audit_rule_system.py   # Cấu hình B — solver chính
      anls.py                # độ đo ANLS
      evidence_f1.py         # độ đo Evidence-F1
      oracle_ceiling.py      # đo trần oracle, không đọc cell_annotations.jsonl
      row_filter_ceiling.py  # trần của mọi bộ lọc hàng tĩnh (nhánh C)
      probe_*.py             # các phép đo độc lập, mỗi file một giả thuyết
      check_validity.py      # phép kiểm hợp lệ tự động
      split_docs.py          # chia train theo tài liệu (880 dev / 220 eval)
    splits/                # dev_docs.txt, eval_docs.txt
    Báo cáo/               # báo cáo tiến độ theo tuần (.md nguồn + .docx nộp)
    papers/                # 10 paper + Paper Tracker + tổng hợp gap
    reference/             # đề bài, hướng dẫn Topic Team
    probe_d/               # probe khả thi Cấu hình D (notebook Colab + kết quả)
  Outline Project ... .docx  # Outline nộp TA (mục IV = bảng ablation)
  PROGRESS_LOG.md            # nhật ký công việc theo tuần
```

---

## Chạy lại

Dữ liệu cuộc thi **không nằm trong repo** (889 MB, và không phải để phát tán). Đặt vào:

```
data/training_set/{labels,questions,cell_annotations}.jsonl
data/training_set/ocr/*.json
data/training_set/images/*.png
```

Chia split rồi chạy solver:

```bash
python "Slot 1/Working Files/code/split_docs.py"                    # 880 dev / 220 eval
python "Slot 1/Working Files/code/audit_rule_system.py" --split dev
python "Slot 1/Working Files/code/audit_rule_system.py" --split eval
python "Slot 1/Working Files/code/audit_rule_system.py" --split all
```

Phép kiểm hợp lệ (đổi tên file nhãn rồi chạy lại — kết quả phải không đổi):

```bash
python "Slot 1/Working Files/code/check_validity.py"
```

Đo trần và các probe nhánh C:

```bash
python "Slot 1/Working Files/code/oracle_ceiling.py"
python "Slot 1/Working Files/code/row_filter_ceiling.py" --split dev
python "Slot 1/Working Files/code/probe_gold_signal.py"  --split dev
```

Yêu cầu: Python 3.10+ · `python-docx` (chỉ để export báo cáo) · `numpy`, `Pillow`.
Solver Cấu hình B **không cần GPU và không cần PyTorch**.

---

## Tác giả

**Huỳnh Thuyên Nam** — OLP AI PTIT 2026, Vòng loại, chủ đề Document VQA.

Nhật ký công việc đầy đủ theo tuần: [`PROGRESS_LOG.md`](Slot%201/Working%20Files/PROGRESS_LOG.md)
