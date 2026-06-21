import os
import glob

conv_id = "c420a0e9-8330-49f8-b5bc-bebbf77d585e"
base_path = f"C:/Users/nhan/.gemini/antigravity/brain/{conv_id}/.system_generated/tasks"

print("Searching in directory:", base_path)
if os.path.exists(base_path):
    files = glob.glob(os.path.join(base_path, "*.log"))
    for fpath in files:
        basename = os.path.basename(fpath)
        if "1723" in basename:
            print(f"\n=== {basename} ===")
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                # Print last 50 lines of logs
                lines = f.readlines()
                for line in lines[-50:]:
                    print(line, end="")
            print("-" * 50)
else:
    print("Directory not found")
