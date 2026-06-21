# Danh sách Tài khoản & Vai trò toàn Hệ thống (All System Accounts & Credentials)

Tài liệu này tổng hợp toàn bộ các tài khoản, thông tin đăng nhập, cổng kết nối và vai trò của các thành phần trong hệ thống Odoo KMS & RAG Chatbot cục bộ (Local).

---

## 🧩 1. Tài khoản Đăng nhập Odoo ERP (Odoo Local Users)

| Tên người dùng | Tên đăng nhập (Login) | Mật khẩu (Password) | Vai trò hệ thống Odoo (Group) | Vai trò RAG Chatbot (Role) | Ghi chú |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin` | System Administrator (`base.group_system`) | **`hr_manager`** | Quản trị viên cao nhất, có quyền xem tất cả tài liệu mật. |
| **User 1** | `user1` | `password123` | Internal User (`base.group_user`) | **`public`** | Nhân viên thường, bị chặn tài liệu IT/HR mật. |
| **User 2** | `user2` | `password123` | Internal User (`base.group_user`) | **`public`** | Nhân viên thường, bị chặn tài liệu IT/HR mật. |
| **User 3** | `user3` | `password123` | Internal User (`base.group_user`) | **`public`** | Nhân viên thường, bị chặn tài liệu IT/HR mật. |

---

## 🗄️ 2. Tài khoản Cơ sở dữ liệu PostgreSQL (Local Database Credentials)

Sử dụng để kết nối thông qua các công cụ quản trị dữ liệu (ví dụ: DBeaver, pgAdmin):

| Tham số kết nối | Giá trị cấu hình | Ghi chú |
| :--- | :--- | :--- |
| **Host (Máy chủ)** | `localhost` | Chạy trên máy cục bộ của bạn. |
| **Port (Cổng kết nối)** | `5433` | Đã ánh xạ từ cổng `5432` bên trong Docker ra máy Host. |
| **Database (Cơ sở dữ liệu)** | `odoo_kms` | Cơ sở dữ liệu chứa toàn bộ bài viết KMS và chat logs. |
| **Username (Tài khoản)** | `odoo` | Tài khoản có quyền đọc ghi dữ liệu Odoo. |
| **Password (Mật khẩu)** | `odoo` | Mật khẩu kết nối. |

---

## 🌐 3. Cổng Dịch vụ Mạng cục bộ (Local Service Ports)

Các cổng dịch vụ đang chạy trong môi trường phát triển của bạn:

*   **Odoo Web ERP Interface**:
    *   **Địa chỉ**: `http://localhost:8069`
    *   **Nhiệm vụ**: Cung cấp giao diện làm việc chính cho nhân viên và quản lý bài viết KMS, giao diện AI Chatbot Kanban/Form.
*   **Host RAG REST API Server**:
    *   **Địa chỉ**: `http://localhost:8000`
    *   **Nhiệm vụ**: Cung cấp các API `/query` và `/synthesize` kết nối Odoo Docker với ChromaDB và Ollama trên máy Host.
*   **Ollama Local API**:
    *   **Địa chỉ**: `http://localhost:11434`
    *   **Nhiệm vụ**: Cung cấp dịch vụ mô hình nhúng `nomic-embed-text` chạy offline.
*   **Streamlit UI Standalone (Optional Backup)**:
    *   **Địa chỉ**: `http://localhost:8501`
    *   **Nhiệm vụ**: Giao diện chat RAG độc lập (sử dụng làm phương án backup kiểm thử).
