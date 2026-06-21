import time
print("Importing get_rag_response from rag_engine...")
from rag_engine import get_rag_response

query = "How to perform a proper handover before resigning from the company?"

print("\n=== Testing get_rag_response with 'hr_manager' ===")
t0 = time.time()
try:
    res = get_rag_response(query, user_role="hr_manager")
    t1 = time.time()
    print("Success! Time taken:", round(t1 - t0, 2), "seconds")
    print("Response:", res)
except Exception as e:
    print("Error:", e)

print("\n=== Testing get_rag_response with 'public' ===")
t0 = time.time()
try:
    res = get_rag_response(query, user_role="public")
    t1 = time.time()
    print("Success! Time taken:", round(t1 - t0, 2), "seconds")
    print("Response:", res)
except Exception as e:
    print("Error:", e)
