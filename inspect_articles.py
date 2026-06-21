import sqlite3

db_path = "./chroma_db/chroma.sqlite3"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Query key-value metadata to rebuild document records
# Each document has an id, and keys like 'title', 'access_role', 'workspace_dimension'
cursor.execute("SELECT id, key, string_value FROM embedding_metadata WHERE key IN ('title', 'access_role', 'workspace_dimension');")
rows = cursor.fetchall()

docs = {}
for doc_id, key, val in rows:
    if doc_id not in docs:
        docs[doc_id] = {}
    docs[doc_id][key] = val

print("=== Unique Documents in ChromaDB ===")
unique_docs = {}
for doc_id, meta in docs.items():
    title = meta.get('title', 'Unknown')
    role = meta.get('access_role', 'Unknown')
    workspace = meta.get('workspace_dimension', 'Unknown')
    unique_docs[title] = (role, workspace)

for title, (role, workspace) in sorted(unique_docs.items()):
    print(f"- Title: {title:<50} | Role: {role:<12} | Workspace: {workspace}")

conn.close()
