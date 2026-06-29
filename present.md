# 🚀 BÁO CÁO TỔNG QUAN HỆ THỐNG ODOO KMS & AI CHATBOT

Tài liệu này trình bày chi tiết về luồng hoạt động, kiến trúc Docker và các chức năng cốt lõi của dự án Quản trị Tri thức (KMS) tích hợp AI.

---

## 1. Luồng Hệ Thống (System Flow)

Kiến trúc của hệ thống được thiết kế theo mô hình **RAG (Retrieval-Augmented Generation)** nhằm giúp AI trả lời chính xác dựa trên tài liệu nội bộ (ví dụ: cẩm nang HR) mà không bị "ảo giác" (hallucination).

### Sơ đồ Luồng xử lý (Workflow):
1. **User Input**: Người dùng nhập câu hỏi thông qua giao diện Chatbot nhúng trong Odoo (hoặc qua Streamlit).
2. **API Gateway**: Yêu cầu được gửi từ frontend (JS/OWL) qua JSON-RPC đến Backend Controller của Odoo (`/kms/ask_ai`). Odoo đóng vai trò định tuyến và tiếp tục đẩy yêu cầu sang **RAG API Server**.
3. **Retrieval (Truy xuất tài liệu)**:
   - Hệ thống nhúng (Embedding Model: `all-MiniLM-L6-v2`) sẽ chuyển câu hỏi của người dùng thành vector (dãy số).
   - Truy vấn vector này vào cơ sở dữ liệu **ChromaDB** để tìm kiếm Top-K các đoạn tài liệu có nội dung liên quan nhất đến câu hỏi.
4. **Augmentation (Tổng hợp ngữ cảnh)**: 
   - RAG Engine lấy các đoạn tài liệu vừa tìm được, ghép nối vào một *Prompt Template* cùng với câu hỏi của người dùng.
5. **Generation (Sinh văn bản)**:
   - Gửi Prompt hoàn chỉnh tới **Ollama (mô hình nội bộ Qwen:0.5b)** để suy luận và sinh ra câu trả lời cuối cùng.
6. **Response**: Trả kết quả (Answer) và Nguồn tài liệu tham khảo (Sources) về lại giao diện cho người dùng chỉ trong vài giây.

---

## 2. Kiến trúc Docker & Vận hành

Hệ thống được đóng gói 100% bằng Docker (thông qua `docker-compose.yml`), giúp dễ dàng triển khai (Plug-and-play) trên mọi môi trường mà không lo xung đột phần mềm.

**Hệ sinh thái bao gồm 4 container (microservices) chính chạy song song:**

- 🐋 **`odoo19-db` (PostgreSQL 15)**: 
  - Lưu trữ dữ liệu cấu trúc của Odoo (thông tin nhân viên, bài viết tri thức, cấu hình phân quyền).
- 🐋 **`odoo19-web` (Odoo 19 core)**: 
  - Chạy backend Python và giao diện Web. Chứa module `kms_knowledge` (custom addons) mà chúng ta tự viết.
  - Cổng (Port) giao tiếp: `8069`.
- 🐋 **`odoo19-rag-api` (FastAPI Server)**: 
  - Bộ não RAG trung tâm. Chứa thư viện LangChain, ChromaDB và các logic nhúng (embeddings).
  - Được ánh xạ thư mục `./chroma_db` ra bên ngoài để bảo toàn dữ liệu vector khi khởi động lại.
  - Cổng giao tiếp nội bộ: `8000`.
- 🐋 **`odoo19-ollama` (Local LLM Server)**: 
  - Động cơ chạy AI Offline. Hiện đang lưu trữ siêu mô hình tốc độ cao `Qwen:0.5b`.
  - Giúp hệ thống hoạt động hoàn toàn bảo mật (không gửi dữ liệu công ty ra ngoài Internet).
  - Cổng giao tiếp nội bộ: `11434`.

*(Ngoài ra còn có giao diện **Streamlit** độc lập chạy trên cổng `8501` để phục vụ các bài test nhanh ngoài Odoo).*

---

## 3. Các Chức Năng Chính (Core Features)

### 3.1. Quản Trị Tri Thức (Knowledge Management)
- Tự động nạp và quản lý bài viết tri thức (Knowledge Articles) ngay trên giao diện gốc của Odoo.
- Vector hóa tài liệu (Tự động băm nhỏ - chunking và chuyển đổi văn bản thành vector để lưu vào ChromaDB).

### 3.2. Trợ Lý AI Nội Bộ (AI Chatbot Widget)
- Tích hợp một hộp thoại Chatbot nổi (Floating Chat Widget) vào mọi màn hình của Odoo thông qua công nghệ Odoo Web Library (OWL - Javascript).
- Trả lời các câu hỏi về quy định nhân sự, lương thưởng, quy trình công ty một cách siêu tốc (dưới 5 giây) ngay trên máy tính cá nhân.

### 3.3. Phân Quyền Bảo Mật (Role-based Access Control - RBAC)
- Khả năng lọc kết quả tìm kiếm theo quyền của người dùng:
  - **Nhân viên thường**: Chỉ AI được phép trả lời dựa trên tài liệu *Public*.
  - **Quản lý Nhân sự (HR Manager)**: AI được phép truy xuất thêm các tài liệu *Mật (Confidential)* như chính sách lương thưởng, kỷ luật.

### 3.4. Tự Động Tổng Hợp Sổ Tay (Synthesis)
- Nút bấm **"Synthesize Handbook"** cho phép AI tự động đọc hàng loạt bài viết riêng lẻ và tóm tắt lại thành một cuốn Cẩm nang nhân sự (hoặc Sổ tay quy trình) hoàn chỉnh, có bố cục rõ ràng.

### 3.5. Nhập Dữ Liệu Tự Động (Auto Import)
- Hỗ trợ công cụ import nhân viên & sơ đồ tổ chức đệ quy thông minh qua API XML-RPC, giúp giải quyết triệt để bài toán nghẽn mạng (Timeout) của tính năng import mặc định.

---

## 4. Hướng Dẫn Chạy Dự Án (How to Run)

Để khởi chạy toàn bộ hệ thống từ con số 0, bạn chỉ cần thực hiện 3 bước chuẩn hóa sau:

### Bước 1: Khởi động hệ sinh thái Docker
Mở Terminal (hoặc Command Prompt) tại thư mục gốc của dự án và chạy lệnh:
```bash
docker-compose up -d --build
```
Lệnh này sẽ tự động tải các image cần thiết và dựng lên cả 4 container (PostgreSQL, Odoo, RAG API, Ollama).

### Bước 2: Kéo mô hình AI (Chỉ làm 1 lần đầu)
Vì dự án sử dụng mô hình AI siêu nhẹ chạy nội bộ để tránh nghẽn mạng, bạn cần lệnh cho Ollama kéo mô hình `qwen:0.5b` về máy:
```bash
docker exec -it odoo19-ollama ollama pull qwen:0.5b
```

### Bước 3: Cài đặt Module Odoo và Nạp Dữ Liệu
1. Truy cập vào `http://localhost:8069`, đăng nhập bằng tài khoản `admin` / mật khẩu `admin`.
2. Bật **Developer Mode** (Chế độ nhà phát triển) trong phần Settings.
3. Vào menu **Apps**, bấm **Update Apps List**.
4. Tìm module có tên **KMS Knowledge Base** và bấm **Activate (Cài đặt)**.
5. (Tuỳ chọn) Nếu muốn tự động tạo hàng loạt nhân viên và sơ đồ phòng ban, hãy mở terminal chạy kịch bản import:
```bash
python import_employees_xmlrpc.py
```
