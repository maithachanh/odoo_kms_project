import requests

url = "http://127.0.0.1:8000/health"
try:
    res = requests.get(url, timeout=5)
    print("Health Status Code:", res.status_code)
    print("Health Response:", res.json())
except Exception as e:
    print("Health Check Failed:", e)
