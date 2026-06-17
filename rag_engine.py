# -*- coding: utf-8 -*-
"""
Core RAG Engine for Week 12
===========================
Takes user queries, runs guardrail checks, queries local ChromaDB with role-based filters,
detects fallback scenarios (insufficient data), formats system prompts, and calls LLM (Gemini or OpenAI).
"""

import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Imports for LangChain & Vector Store
from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings

# Load environment variables
load_dotenv()

# PERSISTENT SETTINGS
PERSIST_DIR = os.getenv("PERSIST_DIRECTORY", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "kms_collection")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

# Guardrail keywords
GUARDRAILS = {
    "salary": ["lương", "salary", "thu nhập", "pay", "wage", "compensation", "bảng lương", "lương bổng", "thuong", "thưởng"],
    "competitor": ["salesforce", "microsoft", "google workspace", "confluence", "notion", "competitor", "đối thủ", "so sánh"],
    "financial": ["doanh thu", "budget", "revenue", "ngân sách", "tài chính", "lợi nhuận", "profit", "chi phí"]
}

# Standard Fallback response
FALLBACK_RESPONSE = (
    "Tôi không tìm thấy thông tin chính xác liên quan đến yêu cầu của bạn trong cơ sở tài liệu KMS nội bộ. "
    "Vui lòng liên hệ quản lý phòng ban hoặc Admin để được hỗ trợ thêm."
)

# Standard Guardrail response
GUARDRAIL_RESPONSE = "Yêu cầu này vi phạm chính sách bảo mật thông tin của doanh nghiệp. Tôi không thể cung cấp thông tin này."

# BA Master System Prompt Template
SYSTEM_PROMPT_TEMPLATE = """Bạn là Trợ lý Tri thức Nội bộ (KMS Chatbot) của doanh nghiệp. Nhiệm vụ của bạn là trả lời các câu hỏi của nhân viên một cách khách quan, chính xác và chuyên nghiệp.

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
{question}"""

def check_guardrails(query):
    """Check if query triggers any of the predefined guardrail boundaries."""
    query_lower = query.lower()
    for category, keywords in GUARDRAILS.items():
        if any(kw in query_lower for kw in keywords):
            return True, category
    return False, None

def get_db_filter(user_role):
    """
    Construct access control filter:
    - hr_manager: can access everything (no filter or OR containing all)
    - it_staff: access it_staff OR public
    - public: access public only
    """
    role = str(user_role).strip().lower()
    if role == 'hr_manager':
        # hr_manager can see everything
        return None
    elif role == 'it_staff':
        return {"$or": [{"access_role": "it_staff"}, {"access_role": "public"}]}
    else:
        # Default to public
        return {"access_role": "public"}

def get_rag_response(query_string, user_role, top_k=2, temperature=0.2, provider="gemini", api_key=None):
    """
    Main RAG Logic:
    1. Guardrail checks
    2. Document retrieval with metadata RBAC filters
    3. Fallback scoring check
    4. LLM response generation
    """
    # 1. Guardrail boundary check
    triggered, category = check_guardrails(query_string)
    if triggered:
        print(f"[GUARDRAIL TRIGGERED] Category: {category} for query: '{query_string}'")
        return {
            "answer": GUARDRAIL_RESPONSE,
            "sources": [],
            "fallback_triggered": False,
            "guardrail_triggered": True
        }

    # Load persistent vector database
    if not os.path.exists(PERSIST_DIR):
        return {
            "answer": "Lỗi: Cơ sở dữ liệu Vector chưa được xây dựng. Vui lòng chạy python ingest_to_vector.py trước.",
            "sources": [],
            "fallback_triggered": True
        }

    # Load local Ollama embeddings
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    db = Chroma(
        persist_directory=PERSIST_DIR, 
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )

    # 2. Retrieve documents using security metadata filter
    db_filter = get_db_filter(user_role)
    
    # Retrieve docs with similarity scores (returns List[Tuple[Document, float]])
    # Chroma returns squared L2 distance (lower = better)
    docs_with_scores = db.similarity_search_with_score(
        query_string, 
        k=top_k, 
        filter=db_filter
    )

    # 3. Fallback thresholding checks
    # Trigger fallback if no docs returned or if the best score is too high (L2 distance > 450.0)
    distance_threshold = 450.0
    fallback_triggered = False
    
    if not docs_with_scores:
        fallback_triggered = True
    else:
        best_doc, best_score = docs_with_scores[0]
        # L2 distance check
        if best_score > distance_threshold:
            print(f"[FALLBACK TRIGGERED] Best distance score is {best_score:.4f} (Threshold: {distance_threshold})")
            fallback_triggered = True

    if fallback_triggered:
        return {
            "answer": FALLBACK_RESPONSE,
            "sources": [],
            "fallback_triggered": True,
            "guardrail_triggered": False
        }

    # Extract clean text and source titles from retrieved docs
    context_chunks = []
    sources = []
    for doc, score in docs_with_scores:
        title = doc.metadata.get("title", "Untitled Document")
        context_chunks.append(f"--- NGUỒN: {title} ---\n{doc.page_content}")
        if title not in sources:
            sources.append(title)
            
    context_str = "\n\n".join(context_chunks)

    # 4. Prompt construction
    prompt = SYSTEM_PROMPT_TEMPLATE.format(context=context_str, question=query_string)

    # 5. LLM API invocation
    # If no api_key is provided, try to load from env
    if not api_key:
        if provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
        else:
            api_key = os.getenv("OPENAI_API_KEY")

    # Dry-run mock response if no API Key is available
    if not api_key:
        print("[DRY-RUN] No API Key provided. Returning mock response.")
        mock_answer = (
            "⚠️ [CHẾ ĐỘ THỬ NGHIỆM - CHƯA CÓ API KEY]\n\n"
            "Hệ thống đã truy xuất tài liệu thành công. Dưới đây là nội dung tham khảo tìm được:\n\n"
            + "\n\n".join([f"**{doc.metadata.get('title')}** (Vai trò: {doc.metadata.get('access_role')}): {doc.page_content}" for doc, _ in docs_with_scores])
        )
        return {
            "answer": mock_answer,
            "sources": sources,
            "fallback_triggered": False,
            "guardrail_triggered": False
        }

    # Execute LLM Call
    try:
        if provider == "gemini":
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=api_key,
                temperature=temperature
            )
            response = llm.invoke(prompt)
            answer = response.content
        elif provider == "openai":
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                openai_api_key=api_key,
                temperature=temperature
            )
            response = llm.invoke(prompt)
            answer = response.content
        else:
            return {
                "answer": "Lỗi: Không hỗ trợ nhà cung cấp LLM này.",
                "sources": [],
                "fallback_triggered": True
            }
            
        return {
            "answer": answer,
            "sources": sources,
            "fallback_triggered": False,
            "guardrail_triggered": False
        }
        
    except Exception as e:
        print(f"[LLM ERROR] {e}")
        return {
            "answer": f"Đã xảy ra lỗi khi gọi LLM API: {e}\n\nVui lòng kiểm tra lại API Key hoặc mạng.",
            "sources": sources,
            "fallback_triggered": True
        }
