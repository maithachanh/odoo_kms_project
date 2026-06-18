# -*- coding: utf-8 -*-
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

e = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
db = Chroma(persist_directory='./chroma_db', embedding_function=e, collection_name='kms_collection')

# List all documents in the collection
collection = db._collection
all_data = collection.get(include=["metadatas"])
print(f"Total documents in DB: {collection.count()}")
print("\n--- ALL ARTICLE TITLES IN DB ---")
titles = set()
for meta in all_data["metadatas"]:
    t = meta.get("title", "?")
    titles.add(t)
for t in sorted(titles):
    print(f"  - {t}")

# Debug TC-01
print("\n--- TC-01: Poor payment history query ---")
results = db.similarity_search_with_score(
    "How should employees handle customers with poor payment history?", k=5
)
for doc, score in results:
    print(f"  Title: {doc.metadata.get('title','?')} | Score: {score:.4f} | Role: {doc.metadata.get('access_role','?')}")

# Debug TC-10
print("\n--- TC-10: Employee reimbursement policy query ---")
results2 = db.similarity_search_with_score(
    "What is FoodHub's employee reimbursement policy?", k=5
)
for doc, score in results2:
    print(f"  Title: {doc.metadata.get('title','?')} | Score: {score:.4f} | Role: {doc.metadata.get('access_role','?')}")
