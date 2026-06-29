import os
import glob
import time

app_data = r"C:\Users\nhan\.gemini\antigravity"
current_time = time.time()

print("Searching App Data recursively for .xlsx files:")
for root, dirs, files in os.walk(app_data):
    for file in files:
        if file.endswith('.xlsx'):
            path = os.path.join(root, file)
            mtime = os.path.getmtime(path)
            print(f"FOUND: {path} | Size: {os.path.getsize(path)} bytes | Age: {int(current_time - mtime)}s")
