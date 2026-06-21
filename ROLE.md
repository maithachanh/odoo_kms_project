# Hướng dẫn Phân quyền & Bộ Câu hỏi Kiểm thử RAG (Role-Based Testing Guide)

Tài liệu này hướng dẫn cách kiểm thử cơ chế phân quyền bảo mật (Security Isolation) trên hệ thống RAG Chatbot bằng bộ câu hỏi mẫu được phân loại chi tiết theo từng Vai trò (Role).

---

## 👥 1. Danh sách Vai trò & Quyền Hạn (Roles Matrix)

| Vai trò trong RAG | Nhóm quyền trong Odoo | Phạm vi tài liệu được truy xuất |
| :--- | :--- | :--- |
| **`hr_manager`** (Admin) | Quản trị viên (`admin`) | **Tất cả tài liệu** (HR mật, IT nghiệp vụ, Public) |
| **`it_staff`** (IT Staff) | Nhóm Kỹ thuật IT (nếu cấu hình) | Tài liệu **IT nghiệp vụ** + Tài liệu **Public** |
| **`public`** (Standard User) | Nhân viên thường (`user1`, `user2`, `user3`) | **Chỉ tài liệu Public** (Tuyệt đối không lộ IT/HR mật) |

---

## ❓ 2. Bộ Câu hỏi Kiểm thử theo Vai trò (Test Questions)

### 🔴 Nhóm A: Câu hỏi Bảo mật Nhân sự (Quyền Admin - `hr_manager`)
*Đây là các câu hỏi liên quan đến tài liệu nội bộ mật của ban giám đốc hoặc phòng nhân sự.*

*   **Câu hỏi mẫu:**
    1.  *"Quy trình bàn giao công việc và ký biên bản thanh lý hợp đồng khi nhân viên xin nghỉ việc là gì?"*
    2.  *"Chính sách và cách tính thưởng doanh số cuối năm của các bộ phận kinh doanh như thế nào?"*
    3.  *"Báo cáo tự kiểm điểm và hình thức kỷ luật nhân viên làm hư hỏng tài sản công ty được lưu trữ ở đâu?"*
*   **Hành vi mong đợi (Expected Behavior):**
    *   **Tài khoản Admin đăng nhập:** Chatbot hiển thị câu trả lời chi tiết kèm nguồn tài liệu (HR Handbook / Policy).
    *   **Tài khoản User thường đăng nhập:** Chatbot tự động trả về thông báo **Fallback** chặn truy cập:
        > *"Tôi không tìm thấy thông tin chính xác liên quan đến yêu cầu của bạn trong cơ sở tài liệu KMS nội bộ. Vui lòng liên hệ quản lý phòng ban hoặc Admin để được hỗ trợ thêm."*

---

### 🟡 Nhóm B: Câu hỏi Nghiệp vụ Kỹ thuật (Quyền IT Staff - `it_staff` / Admin)
*Đây là các câu hỏi liên quan đến hạ tầng kỹ thuật, cấu hình phần mềm nội bộ dành cho đội ngũ IT.*

*   **Câu hỏi mẫu:**
    1.  *"How do we welcome a new developer into the team?"* (Hướng dẫn cài đặt Git, SSH key, môi trường Dev)
    2.  *"Quy trình cách ly và cô lập cổng switch mạng switch IT khi phát hiện có mã độc tấn công là gì?"*
    3.  *"Hướng dẫn cấu hình địa chỉ IP tĩnh và DNS dự phòng trên hệ thống server nội bộ?"*
*   **Hành vi mong đợi (Expected Behavior):**
    *   **Tài khoản Admin / IT Staff đăng nhập:** Chatbot hiển thị câu trả lời trích xuất từ tài liệu kỹ thuật (IT Onboarding / Network Security Policy).
    *   **Tài khoản User thường đăng nhập:** Chatbot tự động chặn và trả về thông báo **Fallback**.

---

### 🟢 Nhóm C: Câu hỏi Quy chế Chung (Quyền Công cộng - `public` / Tất cả các vai trò)
*Đây là các tài liệu thông tin chung, quy định cơ bản mà bất kỳ nhân viên nào cũng có quyền tiếp cận.*

*   **Câu hỏi mẫu:**
    1.  *"Chính sách quy định về việc cài đặt phần mềm diệt virus trên các máy tính xách tay của công ty là gì?"*
    2.  *"Quy trình xử lý các khiếu nại của khách hàng khi xảy ra lỗi giao nhầm món ăn là gì?"*
    3.  *"Quy định chung về việc bảo đảm môi trường làm việc cởi mở và tôn trọng sự đa dạng đối với nhân viên mới?"*
*   **Hành vi mong đợi (Expected Behavior):**
    *   **Tất cả các tài khoản (Admin, User 1, User 2, User 3) đăng nhập:** Chatbot đều trả về câu trả lời chính xác, trích dẫn nguồn (ví dụ: *Acceptable Hardware Use Agreement*, *Customer Complaint Handling*...).

---

## 🧪 3. Hướng dẫn các bước chạy thử nghiệm (Verification Steps)

1.  **Bước 1**: Đăng nhập Odoo local bằng tài khoản admin (`admin` / `admin`). Truy cập **KMS Knowledge $\rightarrow$ AI Chatbot**, mở Agent và hỏi các câu hỏi ở **Nhóm A**. Xác nhận AI trả lời thành công.
2.  **Bước 2**: Đăng xuất tài khoản admin.
3.  **Bước 3**: Đăng nhập bằng tài khoản `user1` (Mật khẩu: `password123`).
4.  **Bước 4**: Vào mục chat và gõ lại đúng câu hỏi ở **Nhóm A** hoặc **Nhóm B**. Xác nhận AI **chặn hoàn toàn** và hiển thị thông báo Fallback an toàn.
5.  **Bước 5**: Gõ câu hỏi ở **Nhóm C**. Xác nhận AI trả lời bình thường.
