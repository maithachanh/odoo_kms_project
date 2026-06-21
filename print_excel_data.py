import pandas as pd
import os

excel_file = "kms_import_template.xlsx"
if os.path.exists(excel_file):
    df = pd.read_excel(excel_file)
    print("Columns:", df.columns)
    print("\nArticles in Excel:")
    for idx, row in df.iterrows():
        print(f"- {row.get('Title')} (Tags: {row.get('Tags')})")
else:
    print("Excel file not found:", excel_file)
