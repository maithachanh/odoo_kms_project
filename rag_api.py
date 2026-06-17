# -*- coding: utf-8 -*-
"""
Host RAG REST API Server (rag_api.py)
=====================================
Exposes a lightweight REST API on port 8000 to bridge Odoo (inside Docker) 
with the host machine's ChromaDB and LLM integration.

Endpoints:
- POST /query: Queries ChromaDB and returns the LLM-generated RAG answer.
- POST /synthesize: Aggregates Odoo KMS articles and compiles a consolidated Markdown document.
"""

import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from rag_engine import get_rag_response
from ingest_to_vector import fetch_articles_from_excel

# API PORT
PORT = 8000

class RAGRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_POST(self):
        parsed_path = urlparse(self.path)
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            payload = json.loads(post_data.decode('utf-8'))
        except Exception as e:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": f"Invalid JSON payload: {e}"}).encode())
            return

        if parsed_path.path == "/query":
            self.handle_query(payload)
        elif parsed_path.path == "/synthesize":
            self.handle_synthesize(payload)
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())

    def handle_query(self, payload):
        """Query ChromaDB and call LLM for answer."""
        query_string = payload.get("query", "")
        user_role = payload.get("role", "public")
        provider = payload.get("provider", "gemini")
        api_key = payload.get("api_key", None)

        if not query_string:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Missing 'query' parameter"}).encode())
            return

        print(f"[API QUERY] Role: {user_role} | Provider: {provider} | Query: '{query_string}'")
        
        # Execute RAG search
        response = get_rag_response(
            query_string=query_string,
            user_role=user_role,
            provider=provider,
            api_key=api_key
        )
        
        self._set_headers(200)
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def handle_synthesize(self, payload):
        """Aggregate all knowledge base documents and compile a consolidated markdown report."""
        provider = payload.get("provider", "gemini")
        api_key = payload.get("api_key", None)
        
        print("[API SYNTHESIZE] Compiling consolidated KMS manual...")

        # 1. Fetch all available articles (use local excel backup since Odoo might be offline)
        articles = fetch_articles_from_excel()
        if not articles:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": "Failed to read knowledge base source articles."}).encode())
            return

        # 2. Construct synthesis prompt
        knowledge_summary = []
        for idx, art in enumerate(articles, start=1):
            # Clean HTML tags using bs4
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(art['body_html'], "html.parser")
            clean_text = " ".join(soup.get_text().split())
            knowledge_summary.append(f"Tài liệu {idx}: {art['title']}\nNội dung: {clean_text}")

        context_str = "\n\n".join(knowledge_summary)
        
        synthesis_prompt = (
            "Bạn là chuyên gia Tổng hợp Tri thức Doanh nghiệp. Dưới đây là danh sách toàn bộ các quy trình, "
            "hướng dẫn vận hành SOP nội bộ của công ty:\n\n"
            f"{context_str}\n\n"
            "YÊU CẦU:\n"
            "Hãy tổng hợp và biên soạn lại toàn bộ các tài liệu trên thành một cuốn sổ tay hướng dẫn vận hành "
            "doanh nghiệp (KMS Handbook) chuyên nghiệp bằng định dạng Markdown.\n"
            "Sổ tay phải có tiêu đề chính, mục lục tự động, phân chia thành các phần rõ ràng (Nhân sự, Kỹ thuật IT, "
            "Bán hàng, Vận hành), và viết lại nội dung một cách mạch lạc, dễ hiểu, trình bày đẹp mắt."
        )

        # 3. Call LLM
        # Load API keys if not supplied
        if not api_key:
            if provider == "gemini":
                api_key = os.getenv("GEMINI_API_KEY")
            else:
                api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            # Fallback mock document if API Key is missing
            print("[DRY-RUN] No API Key provided for synthesis. Returning mock document.")
            mock_document = (
                "# SỔ TAY VẬN HÀNH DOANH NGHIỆP (KMS HANDBOOK)\n\n"
                "*(Bản phác thảo thử nghiệm - Chưa cấu hình API Key)*\n\n"
                "## Mục lục\n"
                "1. Quy trình Nhân sự (HR)\n"
                "2. Quy trình Kỹ thuật & IT\n"
                "3. Quy trình Bán hàng & Vận hành\n\n"
                "## 1. Quy trình Nhân sự (HR)\n"
                "- Hướng dẫn chào đón nhân viên mới và bàn giao công việc nghỉ việc.\n\n"
                "## 2. Quy trình Kỹ thuật & IT\n"
                "- Hướng dẫn thiết lập môi trường máy tính Dev và các chính sách bảo mật mạng.\n\n"
                "## 3. Quy trình Bán hàng & Vận hành\n"
                "- Chính sách hỗ trợ khách hàng VIP và quy trình vận hành máy chủ lưu trữ.\n"
            )
            self._set_headers(200)
            self.wfile.write(json.dumps({
                "document": mock_document,
                "filename": "KMS_Operation_Handbook_Mock.md"
            }).encode('utf-8'))
            return

        try:
            if provider == "gemini":
                from langchain_google_genai import ChatGoogleGenerativeAI
                llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    google_api_key=api_key,
                    temperature=0.3
                )
                response = llm.invoke(synthesis_prompt)
                document_content = response.content
            elif provider == "openai":
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    openai_api_key=api_key,
                    temperature=0.3
                )
                response = llm.invoke(synthesis_prompt)
                document_content = response.content
            else:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Unsupported LLM provider"}).encode())
                return

            self._set_headers(200)
            self.wfile.write(json.dumps({
                "document": document_content,
                "filename": "KMS_Company_Operation_Handbook.md"
            }).encode('utf-8'))

        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": f"LLM synthesis failed: {e}"}).encode())

def run(server_class=HTTPServer, handler_class=RAGRequestHandler, port=PORT):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"RAG REST API Server running on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("API Server stopped.")

if __name__ == '__main__':
    run()
