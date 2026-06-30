# 🧠 TÀI LIỆU KỸ SƯ AI (AI ENGINEER DOCS)

Tài liệu này trình bày chi tiết về luồng hoạt động (Data Flow) của hệ thống AI khi xử lý Prompt (Câu hỏi) của người dùng từ lúc nhập liệu cho đến lúc trả về kết quả.

---

## 1. 🌊 Luồng Xử Lý AI (AI Prompt Flow)

Hệ thống được thiết kế theo kiến trúc **RAG (Retrieval-Augmented Generation)** kết hợp với **Odoo Agent Intents**. Một vòng đời xử lý câu hỏi diễn ra qua 10 giai đoạn sau:

### Giai đoạn 1: Tiếp nhận và Phân quyền (Frontend & Controller)
- **Bước 1 (User Input)**: Người dùng nhập câu hỏi vào giao diện Chatbot (Odoo Widget hoặc Streamlit).
- **Bước 2 (Role Assignment)**: Odoo Controller (`main.py`) nhận câu hỏi, tự động kiểm tra chức vụ (Group) của người dùng trên Odoo để gán cờ `user_role` (`hr_manager`, `it_staff`, hoặc `public`).
- **Bước 3 (API Gateway)**: Odoo Controller đẩy gói tin JSON (chứa câu hỏi + quyền) sang máy chủ RAG API (`rag_api.py`).

### Giai đoạn 2: Phân tích Ý định & Kết nối ERP (Agentic Intents)
- **Bước 4 (Intent Detection & Live Data)**: RAG API ném câu hỏi vào hàm `detect_intents()`. 
  - Nếu phát hiện người dùng đang hỏi về Đơn mua hàng (PO) hay Đơn bán hàng (SO), AI Agent sẽ chạy luồng rẽ nhánh: Kết nối thẳng vào Database Odoo qua XML-RPC, dùng lệnh `search_read` để lấy số liệu các đơn hàng "sống", và tính toán tổng cộng/trung bình ngay lập tức.
  - Số liệu này được lưu trữ thành `odoo_context`.

### Giai đoạn 3: Rào chắn và Tìm kiếm (Retrieval & Guardrails)
- **Bước 5 (Pre-Guardrail Check)**: Bộ lọc AI kiểm tra xem câu hỏi có chứa từ khóa thao túng (Prompt Injection) hay nhạy cảm không. Nếu có, báo lỗi Fallback ngay lập tức.
- **Bước 6 (Vector Search)**: 
  - Biến câu hỏi thành Vector bằng mô hình Embedding (`all-MiniLM-L6-v2`).
  - Quét trong Vector Database (ChromaDB) để tìm các mẩu tài liệu (chunks) gần nghĩa nhất.
  - **Khóa bảo mật (RBAC)**: Câu lệnh tìm kiếm bị ép cứng bộ lọc Role (Ví dụ: `{"access_role": "public"}`), khiến Database giấu tiệt mọi tài liệu mật khỏi tầm mắt của nhân viên thường.
- **Bước 7 (Post-Guardrail Check)**: Đánh giá Điểm khoảng cách (L2 Distance) của tài liệu vừa tìm thấy. Nếu nó quá lạc đề (tức là không có trong hệ thống), AI cũng sẽ bị chặn lại để chống hiện tượng "Ảo giác" (Hallucination).

### Giai đoạn 4: Sinh văn bản (Generation)
- **Bước 8 (Prompt Construction)**: Hệ thống lắp ráp một Prompt khổng lồ theo công thức: `Prompt = [System Prompt] + [Context từ ChromaDB] + [Context Live Data Odoo] + [Câu hỏi của người dùng]`.
- **Bước 9 (LLM Inference)**: Prompt này được đẩy vào miệng mô hình siêu tốc độ chạy offline **Qwen:0.5b** (thông qua Ollama). Mô hình sẽ đọc ngữ cảnh và tự đúc kết thành câu trả lời văn bản.

### Giai đoạn 5: Trả Kết Quả
- **Bước 10 (Delivery)**: Trả về đoạn hội thoại cho Frontend, bao gồm cả nội dung Answer và danh sách Sources (tên tài liệu nguồn).

---

## 2. 📸 Giao diện Chức năng & Kết quả Demo (Project Screenshots & Demo)

Dưới đây là các hình ảnh minh chứng (Screenshots) cho thấy hệ thống đang hoạt động trơn tru trong thực tế:

### 2.1. Giao diện Streamlit Độc Lập
Giao diện ứng dụng chat toàn màn hình chạy bên ngoài Odoo, cho phép cấu hình tham số RAG, mô hình LLM và giả lập chức vụ (User Role Simulation).
![Giao diện Streamlit Cấu hình RAG & LLM](C:/Users/nhan/.gemini/antigravity/brain/4f7d3c0d-90d5-4d5d-9443-ce136c4360e5/media__1782804946141.jpg)

### 2.2. Giao diện Chatbot Nổi trên Odoo (Kiểm thử Phân Quyền)
Khung chat nhỏ gọn (Ask AI) nằm ở góc dưới cùng màn hình Odoo.
- **Trường hợp bị chặn (Guardrail - Access Denied)**: Khi tài khoản không có quyền xem thông tin mật, AI sẽ báo từ chối truy cập.
  ![Chatbot Odoo Báo Lỗi Phân Quyền](C:/Users/nhan/.gemini/antigravity/brain/4f7d3c0d-90d5-4d5d-9443-ce136c4360e5/media__1782804946298.jpg)
- **Trường hợp thành công (Authorized Access)**: Khi truy vấn đúng chức năng cho phép, AI sẽ trích xuất tài liệu nội bộ và tổng hợp thành các bước cụ thể.
  ![Chatbot Odoo Trả Lời Thành Công](C:/Users/nhan/.gemini/antigravity/brain/4f7d3c0d-90d5-4d5d-9443-ce136c4360e5/media__1782804946303.jpg)

### 2.3. Khả năng Tính toán Dữ liệu ERP "Sống" (Live Data Intents)
Chatbot không chỉ đọc tài liệu mà còn có khả năng kết nối sâu vào phân hệ Kế toán/Bán hàng (Sales) để tự động tính toán tổng số lượng và doanh số các đơn hàng (SO) trực tiếp từ Database Odoo.
![Chatbot Tính toán SO](C:/Users/nhan/.gemini/antigravity/brain/4f7d3c0d-90d5-4d5d-9443-ce136c4360e5/media__1782804946114.jpg)

### 2.4. Kiến trúc Container (Docker)
Hệ thống được đóng gói bài bản và chạy trên các container độc lập: Odoo Web, PostgreSQL DB, Ollama Server, và RAG API Engine.
![Kiến trúc Docker](C:/Users/nhan/.gemini/antigravity/brain/4f7d3c0d-90d5-4d5d-9443-ce136c4360e5/media__1782804946139.jpg)
