import pandas as pd

file_path = r"C:\Users\nhan\Downloads\Purchase Order (purchase.order).xlsx"
try:
    df = pd.read_excel(file_path)
    print("Unique values in Vendor column:")
    print(df['Vendor'].unique().tolist())
    print("\nFirst 10 values in Vendor column:")
    print(df['Vendor'].head(10).tolist())
except Exception as e:
    print("Error:", e)
