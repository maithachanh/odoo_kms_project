import os
import time

print("Setting HF_HUB_OFFLINE = 1...")
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

try:
    print("Importing HuggingFaceEmbeddings...")
    from langchain_community.embeddings import HuggingFaceEmbeddings
    
    print("Initializing HuggingFaceEmbeddings...")
    t0 = time.time()
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'local_files_only': True}
    )
    t1 = time.time()
    print("Successfully initialized in offline mode!")
    print("Time taken:", round(t1 - t0, 2), "seconds")
    
    print("Testing embedding a query...")
    vec = embeddings.embed_query("test query")
    print("Embedded query successfully, vector size:", len(vec))
except Exception as e:
    print("Error:", e)
