import xmlrpc.client
import json
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils import embedding_functions
import os

# Odoo connection settings (admin credentials as provided)
ODOO_URL = "http://localhost:8069"
DB = "postgres"  # default DB name in docker-compose
USERNAME = "admin"
PASSWORD = "admin"

# Mapping dimension -> access_role
DIMENSION_ROLE_MAP = {
    "hr": "hr_manager",
    "it": "it_staff",
    "sales": "sales_rep",
    "ops": "ops_staff",
    "legal": "legal_staff",
    "general": "public",
}

# Connect to Odoo via XML-RPC
common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

# Fetch all articles
fields = ["name", "body_html", "workspace_dimension", "tag_ids"]
records = models.execute_kw(DB, uid, PASSWORD, "kms.knowledge.article", "search_read", [[], []], {"fields": fields})

# Initialize Chroma (persistent) client
chroma_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "chroma_db")
client = chromadb.PersistentClient(path=chroma_path)
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = client.get_or_create_collection(name="kms_articles", embedding_function=embedding_fn)

# Text splitter
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

for rec in records:
    html = rec.get("body_html", "")
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    chunks = splitter.split_text(text)
    for idx, chunk in enumerate(chunks):
        metadata = {
            "title": rec.get("name"),
            "workspace_dimension": rec.get("workspace_dimension"),
            "access_role": DIMENSION_ROLE_MAP.get(rec.get("workspace_dimension"), "public"),
            "tags": rec.get("tag_ids"),
            "chunk_index": idx,
        }
        collection.add(
            documents=[chunk],
            metadatas=[metadata],
            ids=[f"{rec.get('id')}_{idx}"],
        )
print(f"Ingested {len(records)} articles with total chunks stored in {chroma_path}")
