# -*- coding: utf-8 -*-
"""
Conversational Chat UI (app.py)
===============================
Builds a user-friendly conversational interface using Streamlit.
Provides a sidebar to select simulated User Roles, adjust RAG parameters,
and enter API keys, with clear warnings for security blocks and fallback scenarios.
"""

import streamlit as st
import os
from rag_engine import get_rag_response

# Page layout and styling
st.set_page_config(
    page_title="KMS Knowledge Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for vibrant look and premium feel
st.markdown("""
<style>
    .main {
        background-color: #f9fbfd;
    }
    .stChatInputContainer {
        border-radius: 12px;
    }
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1F4E78;
        border-bottom: 2px solid #1F4E78;
        padding-bottom: 6px;
        margin-bottom: 12px;
    }
    .user-pill {
        background-color: #E2F0D9;
        color: #385723;
        padding: 4px 8px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 0.85em;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 KMS Knowledge Base RAG Chatbot")
st.markdown("Hệ thống truy xuất tài liệu SOP và trả lời tự động hỗ trợ vận hành nội bộ.")

# Sidebar Settings
st.sidebar.markdown('<p class="sidebar-header">⚙️ CẤU HÌNH HỆ THỐNG</p>', unsafe_allow_html=True)

# 1. Simulate Login Role (Security Access)
st.sidebar.subheader("🔒 Vai trò người dùng (Access Role)")
selected_role = st.sidebar.selectbox(
    "Chọn vai trò để mô phỏng kiểm thử phân quyền:",
    options=["public", "it_staff", "hr_manager"],
    index=0,
    format_func=lambda x: {
        "public": "Public (Nhân viên chung)",
        "it_staff": "IT Staff (Kỹ thuật viên IT)",
        "hr_manager": "HR Manager (Quản lý Nhân sự)"
    }[x]
)

# Display role details
if selected_role == "public":
    st.sidebar.info("🔓 Quyền hạn: Chỉ được truy cập các tài liệu chung (Public).")
elif selected_role == "it_staff":
    st.sidebar.info("💻 Quyền hạn: Xem tài liệu IT và tài liệu chung. Bị chặn tài liệu HR.")
elif selected_role == "hr_manager":
    st.sidebar.success("👑 Quyền hạn tối cao: Xem toàn bộ tài liệu (HR, IT, Public).")

# 2. LLM Provider Selector
st.sidebar.subheader("🧠 Cấu hình Mô hình LLM")
llm_provider = st.sidebar.radio(
    "Chọn nhà cung cấp LLM API:",
    options=["gemini", "openai"],
    index=0,
    format_func=lambda x: "Google Gemini (Miễn phí)" if x == "gemini" else "OpenAI GPT-4o-mini"
)

# Load default keys from environment
default_key = ""
if llm_provider == "gemini":
    default_key = os.getenv("GEMINI_API_KEY", "")
else:
    default_key = os.getenv("OPENAI_API_KEY", "")

api_key_input = st.sidebar.text_input(
    f"Nhập {llm_provider.upper()} API Key:",
    value=default_key,
    type="password",
    help="Lấy API Key Gemini miễn phí từ Google AI Studio."
)

# 3. Parameters Selection
st.sidebar.subheader("🎚️ Tham số RAG & LLM")
top_k = st.sidebar.slider("Số lượng tài liệu truy xuất (Top-K Chunks):", min_value=1, max_value=5, value=2)
temperature = st.sidebar.slider("Độ sáng tạo (Temperature):", min_value=0.0, max_value=1.0, value=0.2, step=0.1)

# Reset Chat button
st.sidebar.markdown("---")
if st.sidebar.button("🧹 Xóa lịch sử chat"):
    st.session_state.messages = []
    st.rerun()

# ----------------- CHAT WINDOW INTERFACE -----------------

# Initialize message history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display message history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            st.markdown(f"**📚 Tài liệu nguồn:** `{', '.join(message['sources'])}`")
        if "status_alert" in message:
            alert_type, alert_msg = message["status_alert"]
            if alert_type == "warning":
                st.warning(alert_msg)
            elif alert_type == "error":
                st.error(alert_msg)

# Handle new user inputs
if user_query := st.chat_input("Nhập câu hỏi tại đây..."):
    # Display user question
    with st.chat_message("user"):
        st.markdown(user_query)
        st.markdown(f"<span class=\"user-pill\">Mô phỏng vai trò: {selected_role}</span>", unsafe_allow_html=True)
    
    st.session_state.messages.append({
        "role": "user",
        "content": user_query
    })
    
    # Process RAG response
    with st.spinner("🤖 Đang tìm kiếm tài liệu và suy luận..."):
        response = get_rag_response(
            query_string=user_query,
            user_role=selected_role,
            top_k=top_k,
            temperature=temperature,
            provider=llm_provider,
            api_key=api_key_input
        )
        
    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(response["answer"])
        
        # Display sources if any
        if response.get("sources"):
            st.markdown(f"**📚 Tài liệu nguồn:** `{', '.join(response['sources'])}`")
            
        # Display status warnings
        status_alert = None
        if response.get("guardrail_triggered"):
            status_alert = ("error", "🚨 Cảnh báo: Câu hỏi bị hệ thống Guardrails từ chối trả lời do vi phạm chính sách bảo mật nội bộ.")
            st.error(status_alert[1])
        elif response.get("fallback_triggered"):
            status_alert = ("warning", "⚠️ Kịch bản Fallback: Không tìm thấy tài liệu phù hợp trong KMS hoặc LLM bị lỗi kết nối.")
            st.warning(status_alert[1])

    # Save to history
    history_entry = {
        "role": "assistant",
        "content": response["answer"],
        "sources": response.get("sources", [])
    }
    if status_alert:
        history_entry["status_alert"] = status_alert
        
    st.session_state.messages.append(history_entry)
