# DANH SÁCH NHIỆM VỤ - TÍNH TOÁN DỮ LIỆU & LIÊN KẾT ODOO (TASK_1)

Dưới đây là các nhiệm vụ cần thực hiện để hoàn thành 2 bài toán tích hợp live data Odoo vào Chatbot AI.

---

## 1. Thiết kế & Xây dựng các Module cốt lõi
- [x] Tạo tiện ích `odoo_agent_utils.py` để xử lý kết nối XML-RPC, nhận diện ý định và truy vấn Odoo.
- [x] Tích hợp cơ chế lấy dữ liệu Odoo thời gian thực và chèn vào bối cảnh (context) trong `rag_engine.py`.
- [x] Cập nhật System Prompt hướng dẫn LLM cách đọc dữ liệu tính toán và hiển thị link Markdown liên kết Odoo.

---

## 2. Khắc phục lỗi trong quá trình Kiểm thử & Phát triển
- [x] **Khắc phục lỗi Unicode Windows:** Sửa lỗi `UnicodeEncodeError` khi in các ký tự tiếng Việt ra console bằng cách cấu hình stdout UTF-8.
- [ ] **Xử lý Graceful Degradation khi thiếu Module Odoo:**
  - Odoo local hiện tại chưa được cài đặt mô-đun **Purchase (Mua hàng)** hoặc **Sale (Bán hàng)** dẫn đến lỗi `<Fault 2: "Object purchase.order doesn't exist">`.
  - Cần nâng cấp `odoo_agent_utils.py` để tự động kiểm tra xem model Odoo (`purchase.order`, `sale.order`, `product.product`) có tồn tại hay không trước khi query.
  - Nếu thiếu mô-đun, chatbot phải trả về phản hồi lịch sự hướng dẫn người dùng cài đặt mô-đun tương ứng thay vì báo lỗi hệ thống.

---

## 3. Xác minh & Đóng gói
- [ ] Chạy kiểm thử tự động với `scratch/test_odoo_integration.py` sau khi sửa lỗi thiếu mô-đun Odoo.
- [ ] Khởi động lại REST RAG API Server trên host (Port 8000).
- [ ] Kiểm tra thực tế trong giao diện Chatbot của Odoo (hỏi tính toán PO/SO, hỏi từ khóa sản phẩm để nhận link liên kết).
- [ ] Cập nhật tài liệu Walkthrough.
