# -*- coding: utf-8 -*-
"""
Verification Script for KMS Week 11 - Vector DB & Data Security (Ollama Version)
================================================================================
Loads the persisted vector database and executes:
- TEST A: Semantic similarity search with synonyms (welcome new developer)
- TEST B: Security isolation filter simulating 'it_staff' user role + assert check
"""

import os
import sys

# Đảm bảo terminal của Windows mã hóa UTF-8 để hiển thị đúng biểu tượng emoji
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Yêu cầu: Sử dụng langchain_chroma (không phải langchain_community)
from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings

# Đường dẫn đến ChromaDB vật lý lưu trên đĩa và tên Collection
persist_directory = "./chroma_db"
collection_name = "kms_collection"

# Khởi tạo mô hình sinh vector tương thích nomic-embed-text chạy offline qua Ollama
embedding_model = OllamaEmbeddings(model="nomic-embed-text")

# Kiểm tra sự tồn tại của thư mục database trước khi kết nối
if not os.path.exists(persist_directory):
    print(f"Lỗi: Thư mục chứa Vector DB '{persist_directory}' không tồn tại.")
    print("Vui lòng chạy python ingest_to_vector.py trước để tạo cơ sở dữ liệu.")
    sys.exit(1)

# Kết nối lại vào cơ sở dữ liệu ChromaDB
db = Chroma(
    persist_directory=persist_directory, 
    embedding_function=embedding_model,
    collection_name=collection_name
)

print("\n=================== RUNNING KMS WEEK 11 AUDIT ===================")

# --- TEST SCENARIO A: SEMANTIC ACCURACY TEST WITH SYNONYMS ---
# Sử dụng từ đồng nghĩa trong Matrix Sheet: "How do we welcome a new developer into the team?"
query_synonym = "How do we welcome a new developer into the team?"
results_semantic = db.similarity_search(query_synonym, k=2)

print(f"\n🔍 [TEST A] Semantic Search Results for Query: '{query_synonym}'")
print("-" * 65)
for i, doc in enumerate(results_semantic):
    print(f"[{i+1}] MATCH FOUND:")
    print(f"    -> Source Title : {doc.metadata.get('title')}")
    print(f"    -> Access Role  : {doc.metadata.get('access_role')}")
    print(f"    -> Snippet      : {doc.page_content[:130]}...\n")

# --- TEST SCENARIO B: SECURITY ISOLATION CHECK (METADATA FILTERS) ---
# Truy vấn chủ đề chung: "System safety and disciplinary actions protocol"
query_shared = "System safety and disciplinary actions protocol"

# Mô phỏng người dùng có quyền it_staff bằng cách sử dụng toán tử $or: chỉ được xem "it_staff" hoặc "public"
it_user_filter = {"$or": [{"access_role": "it_staff"}, {"access_role": "public"}]}
results_filtered = db.similarity_search(query_shared, k=2, filter=it_user_filter)

print(f"\n🔒 [TEST B] Simulating User with 'it_staff' Role (FILTER: access_role == it_staff OR public)")
print("-" * 65)
for i, doc in enumerate(results_filtered):
    print(f"[{i+1}] SECURE MATCH FOUND:")
    print(f"    -> Source Title : {doc.metadata.get('title')}")
    print(f"    -> Access Role  : {doc.metadata.get('access_role')}")
    print(f"    -> Snippet      : {doc.page_content[:130]}...\n")

# --- KIỂM TRA BẢO MẬT (ASSERT CHECK) ---
# Thực hiện kiểm tra xem có bất kỳ tài liệu nào có quyền hr_manager bị lọt vào kết quả không
for doc in results_filtered:
    role = doc.metadata.get("access_role")
    
    # Cảnh báo nghiêm trọng nếu phát hiện rò rỉ dữ liệu
    if role == "hr_manager":
        print("\n🚨 CRITICAL SECURITY WARNING: DATA LEAK DETECTED!")
        print(f"   -> Rò rỉ tài liệu: '{doc.metadata.get('title')}' có quyền 'hr_manager'!")
        
    # Lệnh assert đảm bảo chương trình sẽ crash ngay lập tức nếu điều kiện bảo mật bị vi phạm
    assert role != "hr_manager", "Security Violation: hr_manager document leaked to it_staff!"

print("✓ Bảo mật thành công: Không phát hiện rò rỉ dữ liệu 'hr_manager'.")
print("=================================================================")
