import os
import glob
import time

print("All .xlsx files in Downloads folder:")
downloads_path = r"C:\Users\nhan\Downloads"
for file in os.listdir(downloads_path):
    if file.endswith('.xlsx') and not file.startswith('~$'):
        path = os.path.join(downloads_path, file)
        mtime = os.path.getmtime(path)
        print(f"File: {file} | Size: {os.path.getsize(path)} bytes | Modified: {time.ctime(mtime)}")
