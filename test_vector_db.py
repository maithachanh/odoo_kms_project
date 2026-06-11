import chromadb
import os

# Load persistent Chroma collection
chroma_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "chroma_db")
client = chromadb.PersistentClient(path=chroma_path)
collection = client.get_collection(name="kms_articles")

# Simple interactive search (modify query below as needed)
queries = [
    "How to welcome a new developer?",
    "What are the firewall policies?",
    "Hardware usage guidelines",
    "HR onboarding steps",
]

for q in queries:
    results = collection.query(
        query_texts=[q],
        n_results=3,
    )
    print(f"\nQuery: {q}")
    for idx, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
        print(f"  [{idx+1}] Title: {meta.get('title')} | Role: {meta.get('access_role')} | Dimension: {meta.get('workspace_dimension')}")
        print(f"       Snippet: {doc[:150]}...\n")
