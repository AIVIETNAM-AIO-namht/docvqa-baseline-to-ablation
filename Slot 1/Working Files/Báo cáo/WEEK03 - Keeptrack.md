# KEEPTRACK — TUẦN 3 (WEEK03)

Chủ đề: Hỏi đáp trên ảnh tài liệu (Document VQA) — OLP AI PTIT 2026, Vòng loại
Người thực hiện: Huỳnh Thuyên Nam


---

## 1. Đã làm được gì

- Đo **trần của mọi bộ lọc hàng tĩnh** cho `argmax`/`argmin` trên cả ba split: **99,14%** (dev) / 98,93% (eval) / 99,10% (all).
- Phát hiện và sửa **một công thức sai trong kế hoạch**: trần tính lại từ 94,11% → **99,14%**; harness có `assert` bất biến (trần ≥ số câu B đúng).
- Kiểm chứng trần bằng **4 họ luật không-cần-nhãn** (khử trùng văn bản, hàng in đậm đo từ ảnh, từ khoá hàng tổng, hình học hàng): **0 họ chạm trần**.
- Đo **tín hiệu cứu hàng vàng trong đúng 197 câu B sai**: tín hiệu thị giác tốt nhất chỉ trỏ đúng **9,1%**; 79,2% nó đo được nhưng chỉ vào một hàng thứ ba ⇒ nhiễu.
- **Đóng câu hỏi Evidence-F1 treo từ WEEK01**: BTC trả lời one-to-one + IoU ≥ 0,5; `evidence_f1.py` **đã đúng y hệt từ đầu** (không sửa dòng nào); tham lam ≡ tối ưu trên 11.000 câu.
- Thêm **phép kiểm hợp lệ tự động** cho harness trần (đổi tên file nhãn rồi chạy lại).
- Viết báo cáo kết luận nhánh C.

## 2. Kết quả hiện tại

- Cấu hình B **giữ nguyên**: **0,968** (all) · 0,967 (dev) · 0,972 (eval) — **không dòng code solver nào bị sửa**.
- **Cấu hình C kết luận âm có bằng chứng — không dựng LayoutLMv3/LayoutXLM.** Dư địa 99,14% là **oracle-only** (phải biết trước đáp án), không luật không-cần-nhãn nào chạm tới; tín hiệu không gian/thị giác mà model cần đã đo là **không tồn tại** (hình học đồng nhất tuyệt đối) hoặc **không tương quan** (hàng đậm).
- Đã cập nhật vào Working Files: `Báo cáo/WEEK03 - Báo cáo tiến độ.docx` · `PROGRESS_LOG.md` · `code/row_filter_ceiling.py`, `code/probe_gold_signal.py`.

## 3. Đang cải thiện gì

- **Chuyển trọng tâm sang Cấu hình D (Qwen2.5-VL)**, dồn vào `visual_bold_lookup` — dư địa **duy nhất còn chạm tới được**: trần 82,99% của dạng này là trần của một phép đo độ dày nét, chưa chắc là trần của tín hiệu ảnh. Đây là căn cứ dồn Tuần 4 vào D thay vì C.
- Siết **phân tích rủi ro còn treo**: bộ định tuyến intent (`intent_router.py`) dùng luật regex viết sau khi khảo sát template train — nếu `private_test` dùng template khác thì luật sẽ vỡ.
- Hoàn thiện **bảng ablation A/B/C/D** và điền cột kết quả vào Outline mục IV.
