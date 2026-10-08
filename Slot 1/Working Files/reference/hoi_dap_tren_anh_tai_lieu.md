# HỎI ĐÁP TRÊN ẢNH TÀI LIỆU

## 1. Mô tả bài toán

Một câu hỏi về tài liệu hành chính hiếm khi được trả lời bằng cách tra một từ khóa. *“Tổng chỉ tiêu tuyển mới của hai phòng ban có định biên 30 là bao nhiêu?”* — con số ấy không được in ở bất kỳ đâu trên trang giấy. Nó chỉ xuất hiện sau khi tìm đúng vài ô trong một bảng, hiểu được quan hệ hàng và cột giữa chúng, rồi cộng lại.

Trả lời đúng vẫn chưa đủ nếu hệ thống không nói được nó lấy số từ đâu. Người kiểm tra cần nhìn thấy chính xác vùng nào trên trang nào đã dẫn tới đáp án; nếu không, không có cách nào phân biệt một suy luận đúng với một phỏng đoán may mắn.

Trong tác vụ **Hỏi đáp trên ảnh tài liệu**, mỗi mẫu dữ liệu gồm ảnh trang tài liệu, kết quả OCR kèm tọa độ của từng khối văn bản, và các câu hỏi tiếng Việt về nội dung tài liệu đó. Với mỗi câu hỏi, các đội thi cần đưa ra câu trả lời dạng văn bản và danh sách vùng bằng chứng trên trang. Cả hai phần đều được tính điểm.

## 2. Mô tả dữ liệu

Dữ liệu được chia thành ba tập:

| Tập dữ liệu | Số tài liệu | Số ảnh trang | Số câu hỏi | Nhãn | Mục đích |
|---|---:|---:|---:|---|---|
| `training_set` | 1.100 | 1.426 | 11.000 | Có | Huấn luyện và kiểm tra chương trình |
