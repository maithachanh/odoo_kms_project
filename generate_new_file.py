import os
import pandas as pd
import random

src_file = r"C:\Users\nhan\Downloads\Employee (hr.employee) (3).xlsx"
dest_file = r"C:\Users\nhan\Downloads\new_Employee (hr.employee) (3).xlsx"
workspace_dest = r"C:\Users\nhan\workplace\hsu\kms\odoo_kms_project\new_Employee (hr.employee) (3).xlsx"

try:
    df = pd.read_excel(src_file)
    print("Original Columns:", df.columns.tolist())
    
    # Mapping Job to logical Salaries
    def get_wage(job):
        job_str = str(job).lower()
        if 'ceo' in job_str or 'founder' in job_str:
            return 50000000 + random.randint(-5000000, 5000000)
        elif 'manager' in job_str:
            return 25000000 + random.randint(-2000000, 3000000)
        elif 'chef' in job_str:
            return 18000000 + random.randint(-1500000, 2000000)
        elif 'cashier' in job_str:
            return 8000000 + random.randint(-500000, 1000000)
        elif 'staff' in job_str or 'cook' in job_str or 'dishwasher' in job_str or 'bartender' in job_str or 'stocker' in job_str:
            return 7000000 + random.randint(-500000, 1000000)
        else:
            return 10000000 + random.randint(-1000000, 1500000)
            
    # Find Job column
    job_col = None
    for col in df.columns:
        if 'job' in col.lower():
            job_col = col
            break
            
    if job_col:
        df['Wage'] = df[job_col].apply(get_wage)
    else:
        df['Wage'] = [12000000 + random.randint(-2000000, 3000000) for _ in range(len(df))]
        
    df['Wage'] = df['Wage'].astype(int)
    
    # Save to Downloads
    df.to_excel(dest_file, index=False)
    # Save to Workspace
    df.to_excel(workspace_dest, index=False)
    
    print(f"Successfully generated wages and saved to:\n- {dest_file}\n- {workspace_dest}")
except Exception as e:
    print("Error:", e)
