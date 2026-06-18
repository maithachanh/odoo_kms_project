# KMS Chatbot System Evaluation & Scope Metrics (Week 12)

This document contains the project governance, user story mappings, guardrails, fallback logic, and critical thinking answers compiled by the Project Manager (PM) and Business Analyst (BA).

---

## 1. Project Manager (PM) – Governance & Scope

### 1.1. User Story Mapping
We have defined the following three core business user stories to drive the design of our RAG chatbot:

1.  **User Story 1 (HR Manager / Onboarding):**
    *   *As an* HR Manager,
    *   *I want* the chatbot to query the internal employee handbook and onboarding policy,
    *   *So that* I can answer new hire inquiries about work policies, office conduct, and laptop safety rules accurately without manually browsing files, reducing onboarding assistance time by 50%.
2.  **User Story 2 (IT Technical Staff / Troubleshooting):**
    *   *As an* IT Support Engineer,
    *   *I want* the chatbot to retrieve specific network configurations and system firewall protocols,
    *   *So that* I can safely initiate system diagnostics or trigger automated port isolation during infractions following correct operating procedures.
3.  **User Story 3 (Customer Success Agent / Sales support):**
    *   *As a* Customer Success Representative,
    *   *I want* the chatbot to fetch standard SOPs regarding customer complaints and VIP privileges,
    *   *So that* I can immediately apply authorized discounts or follow the escalation matrix while resolving client complaints live.

### 1.2. Guardrails & Risk Mitigation
The chatbot is configured with clear operational boundaries to prevent security and legal risks:
*   **Competitor Comparisons:** The chatbot is forbidden from evaluating or comparing company products/SOPs with competitors.
*   **Internal Salaries:** The chatbot must refuse to answer queries regarding employee compensation, wages, payroll, or individual salary details.
*   **Confidential Financials:** The chatbot must not disclose unpublished company budgets, revenue logs, or internal cost structures.
*   **Access Violations:** An `it_staff` or `public` user must never see chunks containing `hr_manager` permissions (e.g., employee resignation procedures or personal files).

---

## 2. Business Analyst (BA) – Prompt Engineering

### 2.1. Master System Prompt Template
To ensure the AI remains objective, factual, and strictly bound to corporate data:

```text
Bạn là Trợ lý Tri thức Nội bộ (KMS Chatbot) của doanh nghiệp. Nhiệm vụ của bạn là trả lời các câu hỏi của nhân viên một cách khách quan, chính xác và chuyên nghiệp.

QUY TẮC BẮT BUỘC:
1. Chỉ được phép trả lời dựa TRỰC TIẾP vào phần "BỐI CẢNH TÀI LIỆU" (Context) được cung cấp dưới đây.
2. Tuyệt đối không tự bịa đặt, suy đoán hoặc sử dụng kiến thức bên ngoài không có trong tài liệu.
3. Nếu câu hỏi không thể trả lời bằng thông tin trong Bối cảnh tài liệu, bạn PHẢI kích hoạt Kịch bản Fallback và trả lời chính xác câu sau:
   "Tôi không tìm thấy thông tin chính xác liên quan đến yêu cầu của bạn trong cơ sở tài liệu KMS nội bộ. Vui lòng liên hệ quản lý phòng ban hoặc Admin để được hỗ trợ thêm."
4. Nếu người dùng hỏi các câu hỏi vi phạm hành lang bảo vệ (Guardrails) như lương thưởng, so sánh đối thủ, hoặc tài chính nhạy cảm, trả lời:
   "Yêu cầu này vi phạm chính sách bảo mật thông tin của doanh nghiệp. Tôi không thể cung cấp thông tin này."
5. Trích dẫn rõ ràng tên tài liệu nguồn (Source Title) ở cuối câu trả lời nếu bạn tìm thấy thông tin.

BỐI CẢNH TÀI LIỆU:
{context}

CÂU HỎI CỦA NHÂN VIÊN:
{question}
```

### 2.2. Exception & Fallback Handling
*   **Fallback Trigger Condition:**
    *   When the semantic search similarity score (distance) is above a set threshold (meaning the chunks found are irrelevant), or when the vector search returns 0 documents.
*   **Safe Fallback Response:**
    *   *"Tôi không tìm thấy thông tin chính xác liên quan đến yêu cầu của bạn trong cơ sở tài liệu KMS nội bộ. Vui lòng liên hệ quản lý phòng ban hoặc Admin để được hỗ trợ thêm."*

---

## 3. Critical Thinking & Evaluation Answers

### Question:
> *During testing, your chatbot might encounter a 'Hallucination' (generating realistic but false information) or a 'Context Overflow' (retrieving too much text, exceeding the LLM's prompt token limit). Based on your Week 12 implementation, propose two distinct strategies to mitigate Hallucinations and optimize the Context Window size for your enterprise data.*

### Proposd Strategies:

#### Strategy 1: Mitigating Hallucinations
1.  **Strict Cosine Similarity Distance Filtering (Thresholding):**
    We filter out chunks retrieved from ChromaDB whose distance score is above a strict cutoff (e.g., distance > 0.6 where 0.0 is a perfect match). This prevents irrelevant paragraphs from being fed into the LLM context, which might otherwise confuse the LLM and trigger hallucinations.
2.  **Source Citation Enforcement & Post-Verification:**
    The system prompt strictly commands the LLM to output a `Source Title` link for every fact it states. The backend verification checks if the cited sources actually exist in the list of retrieved document chunks. If the LLM generates a title not present in the context, the system overrides the answer and triggers a fallback.

#### Strategy 2: Optimizing Context Window Size
1.  **Department-Level Metadata Pre-Filtering (RBAC at Vector Store):**
    Instead of retrieving documents across the entire database, we apply Odoo's `workspace_dimension` and `access_role` filters directly during the ChromaDB query. This limits the search space to the user's specific department and clearance level, reducing the volume of retrieved text and keeping context small.
2.  **Recursive Splitting with Small Chunk Limits & Moderate Overlap:**
    We configure `RecursiveCharacterTextSplitter` with a strict `chunk_size` of 500 characters and a `chunk_overlap` of 100 characters. Slicing documents into granular, self-contained paragraphs allows us to fetch only the exact relevant paragraphs (Top-K=2 or 3) rather than whole pages, saving substantial context tokens.
