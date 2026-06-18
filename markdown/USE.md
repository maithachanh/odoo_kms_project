# Hướng dẫn Vận hành và Sử dụng Hệ thống Odoo KMS (Tuần 10)

Tài liệu này hướng dẫn bạn cách khởi động dự án, nhập dữ liệu (import Excel), truy vấn trực tiếp cơ sở dữ liệu PostgreSQL và kiểm thử cổng API XML-RPC.

---

## 🚀 1. Khởi động môi trường Docker

Để khởi động các container Odoo Web và PostgreSQL Database, mở terminal tại thư mục gốc của dự án và chạy:
```bash
docker compose up -d
```
- **Odoo Web Server**: Lắng nghe tại [http://localhost:8069](http://localhost:8069)
- **PostgreSQL Database**: Lắng nghe tại cổng **5433** trên máy host (để tránh xung đột cổng `5432` mặc định).

---

## 🔑 2. Đăng nhập và Sử dụng giao diện Odoo

1. Mở trình duyệt và truy cập: [http://localhost:8069](http://localhost:8069)
2. Nhập thông tin đăng nhập:
   - **Tài khoản**: `admin`
   - **Mật khẩu**: `admin`
   - **Cơ sở dữ liệu**: `odoo_kms` (Được tự động kết nối).

---

## 📥 3. Hướng dẫn Import Dữ liệu Excel (Task 10.1)

### Cách 1: Sử dụng File mẫu chuẩn sẵn có
Để nạp dữ liệu SOP mẫu vào ứng dụng **KMS Knowledge**:
1. Trên thanh menu chính Odoo, chọn ứng dụng **KMS Knowledge** -> **Articles**.
2. Nhấp chọn biểu tượng **List View** (dạng danh sách) ở góc trên bên phải màn hình.
3. Nhấp vào **biểu tượng Bánh răng (Settings)** bên phải tiêu đề danh sách, chọn **Import records** (Nhập bản ghi).
4. Nhấn **Upload File** và chọn tệp **[kms_import_template.xlsx](file:///c:/Users/nhan/workplace/hsu/kms/odoo_kms_project/kms_import_template.xlsx)** nằm trong thư mục dự án của bạn.
5. **QUAN TRỌNG (Để không bị lỗi Tag)**: Tại dòng trường **Tags**, ở bên phải sẽ xuất hiện thông báo màu đỏ *"When a value cannot be matched"*. Hãy chọn tùy chọn **`Create new values`** (Tạo giá trị mới) để Odoo tự tạo nhãn.
6. Nhấn nút **Test** để kiểm tra tính hợp lệ. Khi hệ thống báo màu xanh lá cây *"Everything seems valid"*, nhấn **Import** để hoàn tất.

### Cách 2: Tự động dọn dẹp và chuẩn hóa file Export từ Odoo Enterprise (Đạt tỷ lệ thành công 100%)
Nếu bạn có một file Excel chứa dữ liệu thô xuất từ Odoo Enterprise (có các cột như `Display Name`, `Parent Article`, `Created by`, `Created on`), bạn có thể dùng công cụ tự động dọn dẹp và sắp xếp phân cấp của chúng tôi:

1. Chạy lệnh dọn dẹp (thay `"đường_dẫn_tới_file_excel_của_bạn.xlsx"` bằng đường dẫn thực tế của file bạn vừa tải về):
   ```bash
   python clean_export.py "đường_dẫn_tới_file_excel_của_bạn.xlsx"
   ```
2. Công cụ này sẽ thực hiện tự động:
   - Đổi tên các cột khớp 100% với tên trường của Odoo KMS (`Title`, `Content`, `Workspace Dimension`, `Parent Article`, `Tags`) để Odoo **tự động nhận diện ánh xạ** mà không cần cấu hình bằng tay.
   - Loại bỏ các cột thừa gây lỗi kiểu dữ liệu (như cột `Created on` chứa ngày giờ gây lỗi crash split, và cột `Created by` chứa tên người dùng không khớp ID).
   - **Sắp xếp thứ tự phân cấp (Topological Sort):** Đảm bảo bài viết Cha được tạo trước bài viết Con trong file Excel, triệt tiêu hoàn toàn lỗi liên kết quan hệ khi import.
   - Tự động phân loại `Workspace Dimension` (`hr`, `it`, `sales`, `ops`, `legal`) dựa trên phân tích từ ngữ tiêu đề và nhóm cha.
3. File kết quả **`kms_clean_import.xlsx`** sẽ được lưu cùng thư mục với file gốc của bạn.
4. Bạn chỉ cần tải file `kms_clean_import.xlsx` này lên Odoo, nhấn **Test** và **Import** là hoàn tất thành công ngay lần đầu tiên!

---

## 🗄️ 4. Kiểm tra Dữ liệu đi sâu vào Database (PostgreSQL)

Để xác nhận xem dữ liệu sau khi import đã đi sâu vào bảng cơ sở dữ liệu PostgreSQL vật lý hay chưa, bạn có thể thực hiện một trong hai cách:

### Cách 1: Chạy truy vấn trực tiếp qua dòng lệnh Docker cURL/psql
Mở terminal và chạy lệnh sau để truy vấn trực tiếp bảng dữ liệu `kms_knowledge_article`:
```bash
docker exec -it odoo19-db psql -U odoo -d odoo_kms -c "SELECT id, name, workspace_dimension FROM kms_knowledge_article;"
```

### Cách 2: Kết nối qua DBeaver hoặc pgAdmin
Cấu hình kết nối cơ sở dữ liệu với thông tin:
- **Host**: `localhost`
- **Port**: `5433`
- **Database**: `odoo_kms`
- **User/Password**: `odoo` / `odoo`
Sau đó, mở bảng `kms_knowledge_article` để xem các dòng dữ liệu vật lý.

---

## 📡 5. Sử dụng API Gateway ngoài (XML-RPC - Task 10.2)

Sau khi dữ liệu đã được import vào Odoo, bạn có thể chạy kịch bản Python bên ngoài để kéo dữ liệu và in ra màn hình:
```bash
python xmlrpc_client.py
```
- Script sẽ tự động xác thực và in ra luồng dữ liệu định dạng JSON chứa tiêu đề (`title`), nội dung HTML (`body_html`), và các nhãn (`tags`) tương ứng lấy trực tiếp từ database.

---

## 🛠️ 6. Kiểm thử API bằng cURL / Postman
Xem chi tiết hướng dẫn và các mẫu XML payload cấu hình Postman tại tệp tin **[api_testing.md](file:///c:/Users/nhan/workplace/hsu/kms/odoo_kms_project/api_testing.md)**.
