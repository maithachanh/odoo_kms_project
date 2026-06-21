# KNOWLEDGE MANAGEMENT SYSTEM (KMS) & AI CHATBOT INTEGRATION
**Dự án:** Odoo KMS Project (FoodHub Knowledge Assistant)

---

## 1. Tổng Quan Hệ Thống (System Overview)
Hệ thống KMS là một giải pháp quản lý tri thức nội bộ được xây dựng trên nền tảng **Odoo 19**, tích hợp trợ lý AI thông minh qua công nghệ **RAG (Retrieval-Augmented Generation)**. 
Hệ thống cho phép nhân viên FoodHub tra cứu các quy trình vận hành (SOP), chính sách nhân sự, và hướng dẫn kỹ thuật thông qua giao diện Chatbot ngay trong Odoo, với dữ liệu được xử lý hoàn toàn **offline (cục bộ)** bằng Ollama để đảm bảo tính bảo mật.

---

## 2. Luồng Kiến Trúc Hệ Thống (System Flow)

Kiến trúc hệ thống bao gồm 3 thành phần chính: **Odoo (UI/Data)**, **RAG API (Middleware)**, và **ChromaDB + Ollama (AI Engine)**.

```mermaid
graph TD
    A[Người dùng Odoo] -->|Hỏi: "Cách xử lý khách hàng VIP?"| B(Odoo AI Agent Module)
    B -->|HTTP POST JSON| C{RAG API Server - Host Port 8000}
    C -->|1. Trích xuất Vector| D[(ChromaDB - Vector DB)]
    D -->|Trả về Top 2 Docs liên quan| C
    C -->|2. Ráp Context + Prompt| E[Ollama - Llama 3 / Phi 3]
    E -->|Trả lời dựa trên Context| C
    C -->|HTTP 200 OK JSON| B
    B -->|Hiển thị câu trả lời| A
```

### Các Module Cốt Lõi:
1. **Odoo Docker Container (`odoo19-web`)**: Chứa module `kms_knowledge` quản lý bài viết và giao diện Chatbot.
2. **RAG API Server (`rag_api.py`)**: Đóng vai trò cầu nối. Nhận request từ Odoo, tìm kiếm ngữ cảnh từ Vector DB, và gửi ngữ cảnh đó cho LLM sinh câu trả lời.
3. **Vector Ingestion (`ingest_to_vector.py`)**: Script đọc dữ liệu từ Odoo hoặc file Excel, băm nhỏ (chunking), nhúng (embedding), và lưu vào ChromaDB.

---

## 3. Các Mô Hình AI Được Tích Hợp (Integrated AI Models)

Hệ thống được thiết kế linh hoạt, hỗ trợ chuyển đổi giữa nhiều Provider, nhưng hiện tại được cấu hình mặc định để chạy **hoàn toàn offline**:

| Vai Trò | Model Khuyên Dùng | Mô tả |
|---------|------------------|-------|
| **LLM (Chat/Sinh Text)** | `ollama/phi3` (hoặc `llama3`) | Đóng vai trò "bộ não" đọc hiểu ngữ cảnh và sinh câu trả lời. Chạy local qua cổng `11434`. |
| **Embedding (Nhúng vector)** | `sentence-transformers/all-MiniLM-L6-v2` | Biến đổi văn bản thành các vector số (384 chiều) để so sánh độ tương đồng. Chạy local qua Hugging Face (Chế độ Offline). |
| **LLM (Cloud Backup)** | `gemini-1.5-flash` / `gpt-4o-mini` | Dự phòng trong trường hợp máy local không đủ phần cứng. Yêu cầu API Key. |

---

## 4. Các Tính Năng Bảo Mật Cốt Lõi (Security, Guardrails & Isolation)

Được xử lý trong file [rag_engine.py](file:///c:/Users/nhan/workplace/hsu/kms/odoo_kms_project/rag_engine.py) và Odoo để đảm bảo AI không bị "ảo giác" (hallucination), không rò rỉ thông tin hoặc bị khai thác trái phép:

*   **Identity & Greeting:** Nhận diện câu chào hỏi ("Hello", "Bạn là ai") để tự giới thiệu mà không cần query Database.
*   **Guardrails (Hàng rào bảo vệ):**
    *   `Confidential`: Chặn các câu hỏi nhạy cảm như lương thưởng ("my salary", "payroll").
    *   `Out-of-Scope`: Chặn các câu hỏi ngoài lề (World Cup, thời tiết).
    *   `Prompt Leakage`: Chặn các lệnh cố tình hack AI ("ignore previous instructions").
*   **Fallback (Dự phòng):** Nếu khoảng cách vector (distance) > `1.25` (không tìm thấy tài liệu nào trong KMS tương đồng với câu hỏi), AI sẽ trả về thông báo lỗi thay vì tự bịa thông tin.
*   **Phân Quyền Vai Trò (Role-Based Access Control - RBAC):**
    *   **Admin (`hr_manager`)**: Được quyền hỏi tất cả mọi tài liệu (HR, IT, Public).
    *   **IT Staff (`it_staff`)**: Chỉ được hỏi tài liệu kỹ thuật IT và Public, bị chặn tài liệu HR.
    *   **User thường (`public`)**: Chỉ được hỏi tài liệu Public, bị chặn hoàn toàn tài liệu HR và IT.
*   **Cô Lập Lịch Sử Chat (Chat History Isolation):** 
    Sử dụng Record Rule trong Odoo để giới hạn lịch sử chat theo từng tài khoản. Người dùng thường sẽ không thể xem lại lịch sử chat hay các thông tin nhạy cảm do Admin hỏi, loại bỏ rủi ro rò rỉ thông tin chéo.

---

## 5. Các Cập Nhật Mới Nhất Trên Hệ Thống (Latest System Updates)

Hệ thống đã được nâng cấp và sửa đổi các điểm nghẽn kỹ thuật quan trọng sau:

1.  **Tương thích Schema Odoo 19:**
    *   **Sửa lỗi `access_role`**: Cột `access_role` trên bảng `kms_knowledge_article` đã được tự động tính toán (`store=True`) và đồng bộ xuống cơ sở dữ liệu Postgres sau khi upgrade module.
    *   **Tương thích res.groups**: Khắc phục lỗi tương thích phân quyền Odoo 19 do thuộc tính `category_id` bị khai tử trên `res.groups`. Hệ thống đã định nghĩa bản ghi `res.groups.privilege` và liên kết thông qua `privilege_id` tại [kms_security.xml](file:///c:/Users/nhan/workplace/hsu/kms/odoo_kms_project/custom_addons/kms_knowledge/security/kms_security.xml).
2.  **Bảo mật & Phân quyền trên Giao diện:**
    *   Thêm luật phân quyền dòng chat (`rule_kms_ai_agent_chat_line_personal`) trong Odoo để chỉ cho phép hiển thị các câu hỏi/trả lời do chính người dùng hiện tại tạo ra (`create_uid == user.id`).
    *   Giảm thiểu tranh chấp luồng dữ liệu (concurrency locking) khi nhiều người dùng cùng lúc ghi đè vào trường `user_query` trên một bản ghi Agent dùng chung.
3.  **Tối ưu hóa RAG Offline (Chống nghẽn mạng):**
    *   Thiết lập chế độ **Hugging Face Offline** bằng cách gán `os.environ["HF_HUB_OFFLINE"] = "1"` và `model_kwargs={'local_files_only': True}` khi khởi tạo `HuggingFaceEmbeddings` trong các file [rag_engine.py](file:///c:/Users/nhan/workplace/hsu/kms/odoo_kms_project/rag_engine.py) và [ingest_to_vector.py](file:///c:/Users/nhan/workplace/hsu/kms/odoo_kms_project/ingest_to_vector.py).
    *   Giúp tăng tốc độ khởi tạo vector embeddings và loại bỏ hoàn toàn tình trạng máy chủ RAG API bị treo/timeout 120s do cố kết nối trực tiếp đến Hugging Face Hub khi chạy offline.
4.  **Bổ sung tài liệu Onboarding của HR:**
    *   Bổ sung tài liệu `"HR Onboarding Handbook"` vào quy trình băm nhúng tại [ingest_to_vector.py](file:///c:/Users/nhan/workplace/hsu/kms/odoo_kms_project/ingest_to_vector.py) để Admin có thể hỏi câu hỏi welcome nhân sự mới thành công, trong khi User thường bị chặn và trả về đúng thông báo từ chối quyền truy cập.

---

## 6. Hướng Dẫn Cài Đặt & Vận Hành (Setup & Running Guide)

### Yêu Cầu Hệ Thống (Prerequisites)
- Docker & Docker Compose
- Python 3.10+
- Ollama (đã tải model `phi3` và `nomic-embed-text`)

### Bước 1: Chuẩn bị Môi Trường Python
```bash
pip install langchain langchain-community langchain-chroma langchain-ollama chromadb sentence-transformers pandas openpyxl odoorpc beautifulsoup4 requests
```

### Bước 2: Chuẩn bị Ollama
```bash
# Khởi động Ollama
ollama serve

# Tải model Phi 3 và Nomic Embed Text
ollama pull phi3
ollama pull nomic-embed-text
```

### Bước 3: Đồng bộ Database & Chạy Docker
```bash
# Khởi chạy các container Odoo & Postgres
docker-compose up -d

# Nâng cấp module kms_knowledge để áp dụng cấu trúc dữ liệu mới
docker exec -u 0 odoo19-web odoo -u kms_knowledge -d odoo_kms --stop-after-init
```

### Bước 4: Nhúng Tri Thức Mới & Chạy RAG API
```bash
# Nhúng tri thức vào Vector Database (ChromaDB)
python ingest_to_vector.py

# Khởi chạy API Server
python rag_api.py
```

---

## 7. Cấu Trúc Thư Mục Quan Trọng

```text
odoo_kms_project/
├── docker-compose.yml              # Cấu hình container Odoo & Postgres
├── .env                            # Chứa API Keys và cấu hình Odoo
├── rag_api.py                      # Server REST API kết nối Odoo & ChromaDB
├── rag_engine.py                   # Lõi RAG (Guardrails, Offline HF Embeddings, Prompt)
├── ingest_to_vector.py             # Script nạp dữ liệu offline vào ChromaDB
├── setup_foodhub_data.py           # Script mồi dữ liệu mẫu FoodHub
├── test_vector_db.py               # Kiểm tra tính toàn vẹn của Vector DB offline
├── chroma_db/                      # (Folder tự sinh) Cơ sở dữ liệu Vector lưu cục bộ
└── custom_addons/
    └── kms_knowledge/              # Source code module Odoo
        ├── models/                 # Article & AI Agent models (kms_knowledge_article.py)
        ├── views/                  # XML UI và cấu trúc form/kanban
        ├── security/               # Phân quyền Odoo 19 (kms_security.xml)
        └── data/                   # Seed data (Agent mặc định)
```
