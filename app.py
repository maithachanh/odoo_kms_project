# -*- coding: utf-8 -*-
"""
Conversational Chat UI (app.py) - FoodHub Knowledge Assistant
==============================================================
Builds a user-friendly conversational interface using Streamlit.
Provides a sidebar to select simulated User Roles, choose LLM Provider (including Ollama),
adjust RAG parameters, with clear notifications for fallback and guardrail events.
"""

import streamlit as st
import os
from rag_engine import get_rag_response

# Page layout and styling
st.set_page_config(
    page_title="FoodHub Knowledge Assistant",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for vibrant FoodHub theme (Warm Orange/Red accents)
st.markdown("""
<style>
    .main {
        background-color: #fcfbfa;
    }
    .stChatInputContainer {
        border-radius: 12px;
    }
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #D35400;
        border-bottom: 2px solid #D35400;
        padding-bottom: 6px;
        margin-bottom: 12px;
    }
    .user-pill {
        background-color: #FDEBD0;
        color: #B9770E;
        padding: 4px 8px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 0.85em;
    }
</style>
""", unsafe_allow_html=True)

st.title("🍔 FoodHub Knowledge Assistant")
st.markdown("Retrieval-Augmented Generation (RAG) system for FoodHub sales, purchasing, helpdesk, front-of-house, and technical operations.")

# Sidebar Settings
st.sidebar.markdown('<p class="sidebar-header">⚙️ CONFIGURATION</p>', unsafe_allow_html=True)

# 1. Simulate Login Role
st.sidebar.subheader("🔒 User Role Simulation")
selected_role = st.sidebar.selectbox(
    "Select a role to test clearance & filters:",
    options=["public", "sales", "purchase", "helpdesk", "foh", "technical"],
    index=0,
    format_func=lambda x: {
        "public": "General Employee (Public)",
        "sales": "Sales Staff",
        "purchase": "Purchasing Officer",
        "helpdesk": "Helpdesk Agent",
        "foh": "Front-of-House Staff",
        "technical": "IT & Technical Support"
    }[x]
)

# 2. LLM Provider Selector
st.sidebar.subheader("🧠 LLM Engine Config")
llm_provider = st.sidebar.radio(
    "Select LLM Provider:",
    options=["ollama", "gemini", "openai"],
    index=0,
    format_func=lambda x: {
        "ollama": "Ollama Offline (Llama3)",
        "gemini": "Google Gemini (Online)",
        "openai": "OpenAI GPT-4o-mini"
    }[x]
)

# API Key input (only for cloud APIs)
api_key_input = ""
if llm_provider != "ollama":
    default_key = ""
    if llm_provider == "gemini":
        default_key = os.getenv("GEMINI_API_KEY", "")
    else:
        default_key = os.getenv("OPENAI_API_KEY", "")
        
    api_key_input = st.sidebar.text_input(
        f"Enter {llm_provider.upper()} API Key:",
        value=default_key,
        type="password"
    )

# 3. Parameters Selection
st.sidebar.subheader("🎚️ RAG & LLM Parameters")
top_k = st.sidebar.slider("Retrieve Top-K Chunks:", min_value=1, max_value=5, value=2)
temperature = st.sidebar.slider("Creativity (Temperature):", min_value=0.0, max_value=1.0, value=0.2, step=0.1)

# Reset Chat button
st.sidebar.markdown("---")
if st.sidebar.button("🧹 Clear Chat History"):
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
            st.markdown(f"**📚 Sources:** `{', '.join(message['sources'])}`")
        if "status_alert" in message:
            alert_type, alert_msg = message["status_alert"]
            if alert_type == "warning":
                st.warning(alert_msg)
            elif alert_type == "error":
                st.error(alert_msg)

# Handle new user inputs
if user_query := st.chat_input("Ask a question about FoodHub procedures..."):
    # Display user question
    with st.chat_message("user"):
        st.markdown(user_query)
        st.markdown(f"<span class=\"user-pill\">Simulated Role: {selected_role}</span>", unsafe_allow_html=True)
    
    st.session_state.messages.append({
        "role": "user",
        "content": user_query
    })
    
    # Process RAG response
    with st.spinner("🤖 Retrieving knowledge & generating answer..."):
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
            st.markdown(f"**📚 Sources:** `{', '.join(response['sources'])}`")
            
        # Display status warnings
        status_alert = None
        if response.get("guardrail_triggered"):
            status_alert = ("error", "🚨 Guardrail Event: The query was intercepted by the guardrail filter (Scenario 6/7/8).")
            st.error(status_alert[1])
        elif response.get("fallback_triggered"):
            status_alert = ("warning", "⚠️ Fallback Event: A fallback scenario was triggered (Scenario 1/2).")
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
