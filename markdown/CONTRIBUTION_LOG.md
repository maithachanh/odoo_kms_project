# CONTRIBUTION_LOG.md - Nhật ký đóng góp Dự án KMS Tuần 10

Tài liệu này ghi nhận sự đóng góp chi tiết của từng thành viên trong nhóm đối với việc triển khai Module KMS tùy chỉnh và tích hợp API XML-RPC trong Tuần 10.

---

## 👥 Bảng Phân chia Đóng góp (Contribution Matrix)

| Student ID | Name | Role | Specific Task Handled | % Contribution | Peer Sign-off |
|---|---|---|---|---|---|
| [ID 1] | [Họ tên thành viên 1] | Dev | Thiết kế mô hình dữ liệu (`kms.knowledge.article`), thiết lập odoo.conf, viết views.xml, và sửa lỗi API XML-RPC. | 25% | Verified |
| [ID 2] | [Họ tên thành viên 2] | Dev | Phát triển kịch bản kết nối API ngoài (`xmlrpc_client.py`), cấu hình test Postman, và kiểm thử API CRUD. | 25% | Verified |
| [ID 3] | [Họ tên thành viên 3] | BA / Data | Làm sạch dữ liệu SOP từ Phase 1, ánh xạ và chuẩn bị file dữ liệu Excel mẫu (`kms_import_template.xlsx`). | 25% | Verified |
| [ID 4] | [Họ tên thành viên 4] | BA / Data | Thực hiện import dữ liệu Excel vào hệ thống Odoo, kiểm tra tính toàn vẹn của cấu trúc thư mục cha-con và định dạng HTML. | 25% | Verified |

---

## 📝 Chi tiết Nhiệm vụ của từng Vai trò

### 1. Vai trò Phát triển (Dev Roles)
- **Nhiệm vụ chính**:
  - Dựng cấu trúc thư mục của module tùy chỉnh `kms_knowledge`.
  - Thiết kế lược đồ bảng dữ liệu `kms.knowledge.article` với các trường bắt buộc (`name`, `body_html`, `parent_id`, `workspace_dimension`, `tag_ids`).
  - Viết giao diện Form/List/Kanban tùy chỉnh chia cột Properties và phân nhóm theo phòng ban.
  - Cấu hình file `odoo.conf` và kiểm tra logs khởi động của Odoo container.
  - Xây dựng file Python độc lập (`xmlrpc_client.py`) kết nối API XML-RPC bảo mật và phân giải dữ liệu tags.

### 2. Vai trò Nghiệp vụ và Dữ liệu (BA/Data Roles)
- **Nhiệm vụ chính**:
  - Rà soát các tài liệu hướng dẫn vận hành chuẩn (SOP) từ Phase 1.
  - Làm sạch, chuyển đổi định dạng nội dung tài liệu sang cấu trúc HTML (sử dụng các thẻ `<h2>`, `<ul>`, `<li>`, `<strong>` để giữ nguyên định dạng hiển thị).
  - Ánh xạ dữ liệu vào tệp Excel mẫu khớp với các trường dữ liệu của hệ thống mới.
  - Tiến hành Import hàng loạt (Bulk Import) qua giao diện Odoo, xử lý ánh xạ trường Many2many (`tag_ids`) bằng cơ chế tự động tạo nhãn (`Create new values`).
  - Nghiệm thu giao diện Odoo xem các thư mục cha-con và văn bản rich-text hiển thị đúng chưa.

---

*(Lưu ý: Nhóm vui lòng chỉnh sửa lại Họ tên, Mã số sinh viên thực tế của các thành viên trước khi nén tệp tin ZIP nộp bài).*
