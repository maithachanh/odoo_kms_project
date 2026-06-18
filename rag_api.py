# -*- coding: utf-8 -*-
"""
Host RAG REST API Server (rag_api.py)
=====================================
Exposes a lightweight REST API on port 8000 to bridge Odoo (inside Docker) 
with the host machine's ChromaDB and LLM integration (Ollama / Gemini / OpenAI).

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

    def do_GET(self):
        """Health check endpoint."""
        if self.path == "/health":
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "ok", "message": "RAG API Server is running"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Use POST /query or POST /synthesize"}).encode())

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
        provider = payload.get("provider", "ollama")  # Default to Ollama
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
        provider = payload.get("provider", "ollama")  # Default to Ollama
        api_key = payload.get("api_key", None)
        
        print(f"[API SYNTHESIZE] Compiling consolidated KMS manual via {provider}...")

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
            knowledge_summary.append(f"Document {idx}: {art['title']}\nContent: {clean_text}")

        context_str = "\n\n".join(knowledge_summary)
        
        synthesis_prompt = (
            "You are a Knowledge Synthesis Expert for FoodHub, a fast-food restaurant chain. "
            "Below is the complete list of operational procedures, SOPs, and internal guidelines:\n\n"
            f"{context_str}\n\n"
            "INSTRUCTIONS:\n"
            "Please synthesize and compile all the above documents into a professional FoodHub Operations Handbook "
            "in Markdown format.\n"
            "The handbook must have a main title, table of contents, and be divided into clear sections "
            "(Sales, Purchasing, Helpdesk, Front-of-House, Technical & IT), "
            "with the content rewritten in a clear, concise, and well-formatted manner."
        )

        # 3. Call LLM
        # Load API keys if not supplied
        if not api_key and provider != "ollama":
            if provider == "gemini":
                api_key = os.getenv("GEMINI_API_KEY")
            else:
                api_key = os.getenv("OPENAI_API_KEY")

        # For cloud APIs without key, return mock
        if not api_key and provider not in ("ollama",):
            print("[DRY-RUN] No API Key provided for synthesis. Returning mock document.")
            mock_document = (
                "# FOODHUB OPERATIONS HANDBOOK\n\n"
                "*(Draft - No API Key configured)*\n\n"
                "## Table of Contents\n"
                "1. Sales Procedures\n"
                "2. Purchasing Procedures\n"
                "3. Helpdesk & Delivery\n"
                "4. Front-of-House Operations\n"
                "5. Technical & IT Support\n\n"
                "## 1. Sales Procedures\n"
                "- Customer handling guidelines, VIP privileges, and POS pricing fixes.\n\n"
                "## 2. Purchasing Procedures\n"
                "- Recommended purchasing times and supplier price verification.\n\n"
                "## 3. Helpdesk & Delivery\n"
                "- Preventing missing or incorrect deliveries.\n\n"
                "## 4. Front-of-House Operations\n"
                "- Customer complaint handling procedures.\n\n"
                "## 5. Technical & IT Support\n"
                "- POS system troubleshooting guide.\n"
            )
            self._set_headers(200)
            self.wfile.write(json.dumps({
                "document": mock_document,
                "filename": "FoodHub_Operations_Handbook_Mock.md"
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
            elif provider == "ollama":
                from langchain_ollama import ChatOllama
                llm = ChatOllama(
                    model="phi3",
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
                "filename": "FoodHub_Operations_Handbook.md"
            }).encode('utf-8'))

        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": f"LLM synthesis failed: {e}"}).encode())

def run(server_class=HTTPServer, handler_class=RAGRequestHandler, port=PORT):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print("=" * 60)
    print(f"  FoodHub RAG REST API Server running on port {port}")
    print(f"  Endpoints:")
    print(f"    POST /query      - Query knowledge base with RAG")
    print(f"    POST /synthesize - Compile operations handbook")
    print(f"    GET  /health     - Health check")
    print("=" * 60)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("API Server stopped.")

if __name__ == '__main__':
    run()
