import os

cache_path = os.path.expanduser("~/.cache/huggingface/hub")
print("Cache path exists:", os.path.exists(cache_path))
if os.path.exists(cache_path):
    print("Contents of cache path:")
    for root, dirs, files in os.walk(cache_path):
        depth = root.replace(cache_path, "").count(os.sep)
        if depth <= 2:
            print("  " * depth + os.path.basename(root))
