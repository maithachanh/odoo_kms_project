import os
import glob
import pandas as pd

downloads_path = r"C:\Users\nhan\Downloads"
search_pattern = os.path.join(downloads_path, "*purchase*.xlsx")
files = glob.glob(search_pattern)

with open("excel_details.txt", "w", encoding="utf-8") as out:
    for f in files:
        out.write(f"=== File: {f} ===\n")
        try:
            df = pd.read_excel(f)
            out.write(f"Columns: {df.columns.tolist()}\n")
            out.write("Data:\n")
            out.write(df.to_string())
            out.write("\n\n")
        except Exception as e:
            out.write(f"Error: {e}\n\n")
print("Details written to excel_details.txt")
