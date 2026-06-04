# Hướng dẫn kiểm tra trạng thái hoạt động của dự án Odoo KMS

Tài liệu này hướng dẫn bạn cách kiểm tra xem hệ thống Odoo 19 đã chạy thành công hay chưa, và các bước xác minh hoạt động.

---

## 🛠️ Bước 1: Kiểm tra trạng thái của các Docker Container

Chạy lệnh dưới đây tại thư mục gốc của dự án:
```powershell
docker compose ps
```

### Kết quả mong muốn:
Cả 2 dịch vụ `odoo19-db` và `odoo19-web` đều phải hiển thị trạng thái `Up`.
```text
NAME         IMAGE         STATUS         PORTS
odoo19-db    postgres:15   Up             0.0.0.0:5433->5432/tcp, [::]:5433->5432/tcp
odoo19-web   odoo:19.0     Up             0.0.0.0:8069->8069/tcp, [::]:8069->8069/tcp
```
*(Lưu ý: Cổng cơ sở dữ liệu trên máy host đã được chuyển sang cổng **5433** để tránh xung đột trên máy của bạn).*

---

## 📄 Bước 2: Kiểm tra Logs của Odoo Web

Chạy lệnh sau để xem log hoạt động của Odoo:
```powershell
docker logs odoo19-web
```

### Dấu hiệu thành công:
Cuối log phải xuất hiện dòng thông báo dịch vụ HTTP của Odoo đang chạy mà không gặp lỗi kết nối cơ sở dữ liệu:
```text
INFO ? odoo: Using configuration file at /etc/odoo/odoo.conf
INFO ? odoo: database: odoo@db:5432
INFO ? odoo.service.server: HTTP service (werkzeug) running on <container_id>:8069
```

---

## 🌐 Bước 3: Đăng nhập vào giao diện Odoo Web

1. Mở trình duyệt web và truy cập địa chỉ: [http://localhost:8069](http://localhost:8069)
2. Nhập thông tin tài khoản quản trị:
   - **Tài khoản (Email):** `admin`
   - **Mật khẩu (Password):** `admin`
3. Nhấp **Log in**.

---

## 🧩 Bước 4: Kiểm tra các Module đã cài đặt

Sau khi đăng nhập thành công vào Odoo:
1. Truy cập menu ứng dụng bằng cách nhấp vào biểu tượng góc trên bên trái màn hình.
2. Chọn menu **Apps** (Ứng dụng).
3. Tại thanh tìm kiếm, xóa bộ lọc mặc định `Apps` và lọc theo **Installed** (Đã cài đặt).
4. Xác nhận xem các module sau đã được cài đặt và hiển thị:
   - **Website** (Trang web)
   - **Live Chat** (Trò chuyện trực tiếp)
   - **To-Do** (Danh sách công việc - dùng làm KMS gọn nhẹ)

---

## 🗄️ Bước 5: Kiểm tra kết nối Database qua DBeaver / pgAdmin

Để truy cập cơ sở dữ liệu PostgreSQL trực tiếp từ máy tính của bạn:
1. Mở công cụ quản trị Database (ví dụ: DBeaver).
2. Tạo kết nối PostgreSQL mới hoặc import tệp cấu hình `.dbeaver-data-sources.xml` sẵn có.
3. Cấu hình các thông số kết nối:
   - **Host:** `localhost`
   - **Port:** `5433` (đã cập nhật)
   - **Database:** `odoo_kms`
   - **Username:** `odoo`
   - **Password:** `odoo`
4. Thực hiện **Test Connection** để xác nhận kết nối thành công.
