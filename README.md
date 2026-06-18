# Odoo v19 KMS & Secure RAG Chatbot Integration

## 🎯 Project Overview
This project integrates a **custom KMS Knowledge module** in Odoo 19 with a local, secure **Retrieval-Augmented Generation (RAG) AI Chatbot**. Instead of redirecting users externally, the chatbot is natively integrated into Odoo, allowing employees to search internal SOP documentation and compile aggregated knowledge handbooks directly within the ERP interface.

```
                  ┌──────────────────────────────────────────────┐
                  │            Host Machine (Local)              │
                  │                                              │
                  │  ┌───────────────┐        ┌───────────────┐  │
                  │  │  Chroma DB    │        │    Ollama     │  │
                  │  │ (./chroma_db) │        │ (nomic-embed) │  │
                  │  └───────┬───────┘        └───────┬───────┘  │
                  │          │                        │          │
                  │  ┌───────▼────────────────────────▼───────┐  │
                  │  │          Host RAG API Server           │  │
                  │  │          (rag_api.py:8000)             │  │
                  │  └───────────────────▲────────────────────┘  │
                  └──────────────────────┼───────────────────────┘
                                         │ Requests (JSON-RPC)
                  ┌──────────────────────┼───────────────────────┐
                  │           Docker Container                   │
                  │                                              │
                  │  ┌────────────────────────────────────────┐  │
                  │  │           Odoo Web Container           │  │
                  │  │              (odoo19-web)              │  │
                  │  │  - kms.knowledge.article               │  │
                  │  │  - kms.ai.agent                        │  │
                  │  │  - kms.ai.agent.chat.line              │  │
                  │  └────────────────────────────────────────┘  │
                  └──────────────────────────────────────────────┘
```

---

## 📁 Repository Layout
```
├─ custom_addons/
│  └─ kms_knowledge/            # 🧩 Odoo Custom KMS & Chatbot Module
│     ├─ models/
│     │  └─ kms_knowledge_article.py # Python models & RAG REST client calls
│     ├─ security/
│     │  └─ ir.model.access.csv      # Access Control List (ACL) permissions
│     ├─ data/
│     │  └─ kms_ai_agent_data.xml    # Default AI Agent bootstrap records
│     ├─ views/
│     │  └─ kms_knowledge_article_views.xml # Native Kanban, Form & List views
│     └─ __manifest__.py        # Odoo module metadata manifest
├─ chroma_db/                   # 🗄️ Local vector database directory
├─ ingest_to_vector.py          # 📥 Vector ingestion pipeline (Ollama nomic-embed-text)
├─ test_vector_db.py            # 🧪 Automated semantic search & security isolation audit
├─ rag_engine.py                # 🧠 Core RAG search, fallback & guardrail engine
├─ rag_api.py                   # 🌐 Host REST API server (port 8000)
├─ app.py                       # 🖥️ Streamlit standalone UI (optional backup)
├─ docker-compose.yml           # 🐳 Docker services (Odoo v19 Web + Postgres v15 DB)
├─ odoo.conf                    # Odoo configuration settings
├─ requirements.txt             # 📦 Python project dependencies
└─ README.md                    # ⬅️ This file
```

---

## 🛠️ 1. Installation & Setup Instructions

### Prerequisites
1. Install **Docker Desktop**.
2. Install **Ollama** and pull the embedding model:
   ```bash
   ollama pull nomic-embed-text
   ```
3. Set up Python environment & install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Step 1: Spin Up Docker Services
Bring up Odoo and PostgreSQL containers in the background:
```bash
docker-compose up -d
```
- **Odoo Web**: `http://localhost:8069` (login: `admin` / `admin`)
- **PostgreSQL**: Port `5433` on Host

### Step 2: Build the Vector Database
Ingest articles (extracted from Odoo or fallback Excel templates) into ChromaDB:
```bash
python ingest_to_vector.py
```
To verify the database integrity, semantic accuracy, and security role isolation:
```bash
python test_vector_db.py
```

### Step 3: Run the Host RAG API Server
Start the HTTP REST server to bridge Odoo with the host embedding/LLM models:
```bash
python rag_api.py
```

### Step 4: Upgrade the Odoo Custom Module
Trigger Odoo to load the new views, permissions, and bootstrap records:
```bash
docker exec -i odoo19-web odoo -d odoo_kms -u kms_knowledge --stop-after-init
docker restart odoo19-web
```

---

## 🔒 2. Data Security & RAG Governance

The RAG Engine (`rag_engine.py`) enforces strict enterprise constraints:
*   **Role-Based Access Control (RBAC)**: Documents are pre-filtered during vector queries based on the user's Odoo credentials:
    - `hr_manager` $\rightarrow$ Can query all articles.
    - `it_staff` $\rightarrow$ Filtered to `it_staff` and `public` articles.
    - `public` $\rightarrow$ Restricted strictly to `public` articles.
*   **Predefined Guardrails**: Any query matching restricted terms (salaries, competitors, unpublished financials) is immediately blocked, returning a security notification.
*   **Fallback Detection**: If the query similarity L2 distance exceeds `450.0` (for `nomic-embed-text`), a clean fallback response is triggered instead of sending the prompt to the LLM, preventing hallucination.
*   **Dry-Run Mode**: If no `GEMINI_API_KEY` or `OPENAI_API_KEY` is loaded in `.env`, the engine works offline by retrieving the exact document snippets and printing them in the Odoo chat, avoiding network dependencies.

---

## 🖥️ 3. Odoo User Interface & Interactions

### AI Agent Kanban Dashboard
Navigate to **KMS Knowledge $\rightarrow$ AI Chatbot**. You will see three cards bootstrapped natively:
*   **Odoo Agent** (Model: GPT 4o)
*   **Livechat AI Agent** (Model: GPT 4o)
*   **Ask AI** (Model: Gemini 1.5 Flash)

### Interactive Chat & Reload
1. Click on **Ask AI** to open its form.
2. Type your question in the query text box.
3. Click **Hỏi AI**. The backend queries the host API, logs the conversation inside Odoo (`kms.ai.agent.chat.line`), and automatically reloads the view to show the response and cited sources instantly.

### One-Click Sổ tay (Synthesis Document)
Click the **Tổng hợp tài liệu** button in the header. The system aggregates all SOP knowledge articles, prompts the LLM to format it into a structured Markdown manual with an automated table of contents, creates an Odoo attachment, and starts an automatic download.

---

## 📥 4. Odoo Enterprise Migration Workflow

When importing or exporting documents between Odoo Enterprise and Local environments, follow this guide:

### Exporting from Odoo Enterprise
1. Switch to **List View** in the Knowledge module.
2. Select target articles and select **Actions $\rightarrow$ Export**.
3. Check **"I want to update data (import-compatible export)"** to generate External IDs.
4. Select these exact fields:
   - `id` (External ID)
   - `name` (Title)
   - `body` (HTML Content)
   - `parent_id/id` (Parent Article / External ID) - *Click `>` next to Parent Article and select `External ID`*.

### Importing into Odoo Local
1. Click **Favorites $\rightarrow$ Import records** in KMS Articles list.
2. Upload the exported file.
3. Map the columns:
   - `id` $\rightarrow$ `External ID`
   - `name` $\rightarrow$ `Display Name`
   - `body` $\rightarrow$ `Content` *(Manually select from dropdown as our local field is body_html)*
   - `parent_id/id` $\rightarrow$ `Parent Article / External ID`
4. Click **Test** and then **Import**.
