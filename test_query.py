import requests
import json

url = "http://127.0.0.1:8000/query"
query = "How should we welcome a new employee according to HR guidelines?"

print("=== Testing Query with 'hr_manager' role ===")
payload_admin = {
    "query": query,
    "role": "hr_manager",
    "provider": "ollama"
}
try:
    res = requests.post(url, json=payload_admin, timeout=120)
    print("Status Code:", res.status_code)
    print("Response JSON:")
    print(json.dumps(res.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print("Error:", e)

print("\n=== Testing Query with 'public' role ===")
payload_user = {
    "query": query,
    "role": "public",
    "provider": "ollama"
}
try:
    res = requests.post(url, json=payload_user, timeout=120)
    print("Status Code:", res.status_code)
    print("Response JSON:")
    print(json.dumps(res.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print("Error:", e)
