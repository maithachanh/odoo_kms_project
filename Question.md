# 📋 Danh Sách Câu Hỏi Phân Quyền Bảo Mật RAG (RAG Security Access Control Questions)

Tài liệu này tổng hợp và phân loại chi tiết các câu hỏi kiểm thử bảo mật trên hệ thống **KMS Knowledge AI Chatbot**. Hệ thống áp dụng cơ chế phân quyền dựa trên vai trò (Role-Based Access Control - RBAC) tại tầng Vector Database (ChromaDB) kết hợp Siêu dữ liệu (Metadata).

---

## 👥 1. Tóm tắt Cấu hình Phân quyền (Access Control Summary)

| Vai trò RAG | Tài khoản Kiểm thử | Quyền truy cập Tài liệu KMS |
| :--- | :--- | :--- |
| **`hr_manager`** (Admin) | `admin` | **Toàn bộ hệ thống** (Tài liệu HR mật, IT nội bộ & Public) |
| **`it_staff`** (IT Staff) | *Cấu hình thêm* | Tài liệu **IT nội bộ** và các tài liệu **Public** |
| **`public`** (Standard User) | `user1`, `user2`, `user3` | **Chỉ tài liệu Public** (Không được phép truy cập IT & HR mật) |

---

## 🔒 2. Nhóm 1: Câu hỏi CHỈ ADMIN (`hr_manager`) hỏi được
*Đây là các câu hỏi truy vấn thông tin từ tài liệu Nhân sự nội bộ mật. User thường (`public`) và IT Staff (`it_staff`) khi hỏi các câu này sẽ bị chặn và nhận thông báo **Fallback**.*

### Tài liệu nguồn 1: `Salary and Payroll Administration Policy` (HR/Payroll)
* **Câu hỏi kiểm thử:**
  1. *"Chính sách và cách tính thưởng doanh số cuối năm của các bộ phận kinh doanh như thế nào?"*
  2. *"Individual salary details and payroll logs are confidential or not?"* *(Chi tiết lương cá nhân và nhật ký lương có được bảo mật không?)*
  3. *"Inquiries regarding payroll calculations must be submitted to whom?"* *(Các thắc mắc về tính toán lương phải được gửi cho ai?)*
* **Kết quả mong đợi:**
  * **Admin (`hr_manager`):** Được chatbot trả lời chi tiết (yêu cầu gửi văn bản cho HR Manager, tính bảo mật của lương...).
  * **User thường (`public`):** Trả về thông báo chặn truy cập (Fallback).

### Tài liệu nguồn 2: `Employee Resignation and Offboarding SOP` (HR/Offboarding)
* **Câu hỏi kiểm thử:**
  1. *"Quy trình bàn giao công việc và ký biên bản thanh lý hợp đồng khi nhân viên xin nghỉ việc là gì?"*
  2. *"Nhân viên thôi việc cần nộp thông báo trước bao nhiêu ngày?"*
  3. *"Các tài sản doanh nghiệp nào cần hoàn trả trước khi nhân viên nghỉ việc?"*
* **Kết quả mong đợi:**
  * **Admin (`hr_manager`):** Được trả lời chi tiết (cần thông báo trước 30 ngày, trả lại laptop, security token, chìa khóa...).
  * **User thường (`public`):** Trả về thông báo chặn truy cập (Fallback).

---

## 🛡️ 3. Nhóm 2: Câu hỏi CHỈ ADMIN & IT STAFF hỏi được (User thường bị chặn)
*Đây là các câu hỏi truy vấn từ tài liệu Nghiệp vụ IT nội bộ. User thường (`public`) khi hỏi các câu này sẽ bị chặn hoàn toàn.*

### Tài liệu nguồn 1: `IT Engineer Onboarding Protocol` (IT/SOP)
* **Câu hỏi kiểm thử:**
  1. *"How do we welcome a new developer into the team?"*
  2. *"Lập trình viên IT mới gia nhập cần làm gì khi đến công ty?"*
  3. *"Làm thế nào để cấu hình môi trường phát triển cục bộ và profile GitHub doanh nghiệp cho nhân sự IT mới?"*
* **Kết quả mong đợi:**
  * **Admin / IT Staff:** Nhận được hướng dẫn kỹ thuật chi tiết.
  * **User thường (`public`):** Bị chặn và nhận thông báo Fallback.

### Tài liệu nguồn 2: `Network Security & System Firewall Policy` (IT/Security)
* **Câu hỏi kiểm thử:**
  1. *"Quy trình cách ly và cô lập cổng switch mạng switch IT khi phát hiện có mã độc tấn công là gì?"*
  2. *"Làm cách nào để bảo vệ dữ liệu nội bộ và log mạng khi phát hiện hành vi xâm phạm an toàn hệ thống?"*
  3. *"What triggers the automated port isolation protocol?"* *(Điều gì kích hoạt giao thức cô lập cổng tự động?)*
* **Kết quả mong đợi:**
  * **Admin / IT Staff:** Nhận hướng dẫn cô lập cổng switch bảo mật.
  * **User thường (`public`):** Bị chặn và nhận thông báo Fallback.

---

## 🔓 4. Nhóm đối chứng: Câu hỏi PUBLIC (TẤT CẢ mọi người đều hỏi được)
*Để đảm bảo hệ thống không chặn nhầm thông tin công cộng, tất cả các tài khoản bao gồm User thường đều phải nhận được câu trả lời chính xác cho các câu hỏi sau:*

1. *"Quy trình xử lý các khiếu nại của khách hàng khi xảy ra lỗi giao nhầm món ăn là gì?"* (Nguồn: `Customer Complaint Handling`)
2. *"VIP Customer Privileges"* (Nguồn: `VIP Customer Privileges`)
3. *"Chính sách quy định về việc cài đặt phần mềm diệt virus trên các máy tính xách tay của công ty là gì?"* (Nguồn: `POS System Troubleshooting Guide` hoặc tài liệu bảo mật thiết bị chung)
4. *"Avoid Purchasing at Unusually Low Prices"* (Nguồn: `Avoid Purchasing at Unusually Low Prices`)

---

## 🧪 5. Phản hồi Mong đợi khi bị Chặn truy cập (Fallback Response)

Khi tài khoản không có đủ quyền truy cập (vai trò `public` cố tình hỏi các câu ở Nhóm 1 và Nhóm 2), chatbot bắt buộc phải hiển thị câu trả lời fallback chuẩn hóa bảo mật:

> ⚠️ *"I could not find sufficient information in the FoodHub knowledge base to answer this question. Please consult your supervisor or the appropriate department for further assistance."*
> 
> *(Hoặc phiên bản tiếng Việt tương đương nếu được cấu hình)*

---

## 🖥️ 6. Cách thực hiện Kiểm thử Phân quyền (How to Verify)

Bạn có thể kiểm tra trực tiếp qua hai phương thức:

### Cách A: Giao diện Odoo AI Chatbot
1. Đăng nhập Odoo bằng tài khoản **Admin** (`admin` / `admin`).
2. Vào **KMS Knowledge** ➔ **AI Chatbot**, hỏi: *"Quy trình bàn giao công việc khi nghỉ việc là gì?"* ➔ **Mong đợi: Trả lời chi tiết**.
3. Đăng xuất và đăng nhập lại bằng **User 1** (`user1` / `password123`).
4. Hỏi lại đúng câu hỏi trên ➔ **Mong đợi: Trả về thông báo Fallback** (không tiết lộ thông tin nghỉ việc).

### Cách B: Chạy Script Kiểm thử Tự động qua XML-RPC
Chạy file kiểm thử phân quyền tích hợp để kiểm tra phản hồi tự động từ API RAG:
```bash
python xmlrpc_client.py
```
*(Script sẽ tự động đăng nhập luân phiên các tài khoản và kiểm tra xem chatbot có trả về tài liệu mật cho user thường hay không)*
