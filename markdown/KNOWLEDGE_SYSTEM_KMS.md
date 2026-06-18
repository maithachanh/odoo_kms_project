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
    C -->|2. Ráp Context + Prompt| E[Ollama - Llama 3]
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
| **LLM (Chat/Sinh Text)** | `ollama/llama3` (8B) | Đóng vai trò "bộ não" đọc hiểu ngữ cảnh và sinh câu trả lời. Chạy local qua cổng `11434`. (Có thể dùng `qwen2:1.5b` hoặc `phi3` nếu máy yếu). |
| **Embedding (Nhúng vector)** | `sentence-transformers/all-MiniLM-L6-v2` | Biến đổi văn bản thành các vector số (384 chiều) để so sánh độ tương đồng. Chạy local siêu nhẹ. |
| **LLM (Cloud Backup)** | `gemini-1.5-flash` / `gpt-4o-mini` | Dự phòng trong trường hợp máy local không đủ phần cứng. Yêu cầu API Key. |

---

## 4. Các Tính Năng Bảo Mật Cốt Lõi (Guardrails & Fallback)

Được xử lý trong file `rag_engine.py` để đảm bảo AI không bị "ảo giác" (hallucination) hoặc rò rỉ thông tin:

*   **Identity & Greeting:** Nhận diện câu chào hỏi ("Hello", "Bạn là ai") để tự giới thiệu mà không cần query Database.
*   **Guardrails (Hàng rào bảo vệ):**
    *   `Confidential`: Chặn các câu hỏi nhạy cảm như lương thưởng ("my salary", "payroll").
    *   `Out-of-Scope`: Chặn các câu hỏi ngoài lề (World Cup, dự đoán chứng khoán).
    *   `Prompt Leakage`: Chặn các lệnh cố tình hack AI ("ignore previous instructions").
*   **Fallback (Dự phòng):** Nếu khoảng cách vector (distance) > `1.25` (nghĩa là không tìm thấy tài liệu nào trong KMS trùng khớp với câu hỏi), AI sẽ tự động từ chối trả lời thay vì bịa đặt thông tin.

---

## 5. Hướng Dẫn Cài Đặt (Setup Instructions)

### Yêu Cầu Hệ Thống (Prerequisites)
- Docker & Docker Compose
- Python 3.10+
- Ollama (đã tải model `llama3`)

### Bước 1: Chuẩn bị Môi Trường Python
```bash
# Cài đặt các thư viện cần thiết
pip install langchain langchain-community langchain-ollama chromadb sentence-transformers pandas openpyxl odoorpc beautifulsoup4 requests
```

### Bước 2: Chuẩn bị Ollama
```bash
# Khởi động Ollama
ollama serve

# Tải model Llama 3
ollama pull llama3
```

### Bước 3: Chuẩn bị Odoo & Database
```bash
# Khởi chạy Odoo bằng Docker
docker-compose up -d

# Truy cập http://localhost:8069 (admin/admin)
# Vào Apps -> Cài đặt/Upgrade module "KMS Knowledge Base"
```

---

## 6. Các Bước Chạy Dự Án (Steps to Run)

Mỗi khi hệ thống có dữ liệu tri thức mới, hoặc khi khởi động lại máy, bạn cần thực hiện theo luồng sau:

### 1. Sinh Dữ Liệu & Nhúng Vector (Ingestion)
Mục đích: Đưa tri thức từ dạng text sang Vector Database.
```bash
# Tạo file Excel chứa dữ liệu FoodHub mẫu
python setup_foodhub_data.py

# Đọc Excel, nhúng (embed) và lưu vào thư mục ./chroma_db
python ingest_to_vector.py
```
*Kết quả:* Thư mục `chroma_db` xuất hiện chứa cơ sở dữ liệu.

### 2. Khởi Chạy RAG API Server
Mục đích: Lắng nghe request từ Odoo.
```bash
# Chạy server ở port 8000
python rag_api.py
```
*(Lưu ý: Terminal này phải luôn được giữ mở trong suốt quá trình sử dụng Odoo)*

### 3. Tương tác trên Odoo
1. Mở trình duyệt: `http://localhost:8069`
2. Truy cập Menu **KMS Knowledge** -> **AI Chatbot**
3. Mở Agent **FoodHub Knowledge Assistant**
4. Nhập câu hỏi (Ví dụ: *"How should customer complaints be handled?"*) và nhấn **Ask AI**.

---

## 7. Cấu Trúc Thư Mục Quan Trọng

```text
odoo_kms_project/
├── docker-compose.yml              # Cấu hình container Odoo & Postgres
├── .env                            # Chứa API Keys và cấu hình Odoo
├── rag_api.py                      # Server FastAPI/HTTP kết nối Odoo & ChromaDB
├── rag_engine.py                   # Lõi RAG (Guardrails, Fallback, Prompt LLM)
├── ingest_to_vector.py             # Script nạp dữ liệu vào ChromaDB
├── setup_foodhub_data.py           # Script mồi dữ liệu mẫu FoodHub
├── evaluate_rag.py                 # Tool tự động test 10 Test cases
├── chroma_db/                      # (Folder tự sinh) Lưu trữ Vector DB
└── custom_addons/
    └── kms_knowledge/              # Source code module Odoo
        ├── models/                 # Chứa Article & AI Agent models
        ├── views/                  # UI (English) & Kanban/Form
        └── data/                   # Seed data (Agent FoodHub mặc định)
```
