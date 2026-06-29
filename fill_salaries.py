import os
import glob
import pandas as pd
import random

downloads_path = r"C:\Users\nhan\Downloads"
search_pattern = os.path.join(downloads_path, "*employee*.xlsx")
files = glob.glob(search_pattern)

# Filter out temp/lock files starting with ~$
files = [f for f in files if not os.path.basename(f).startswith("~$")]

if files:
    # Get the most recently modified file
    files.sort(key=os.path.getmtime, reverse=True)
    file_path = files[0]
    print(f"Found Excel file at: {file_path}")
    
    try:
        df = pd.read_excel(file_path)
        
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
        
        # Check if 'Job' column exists
        job_col = None
        for col in df.columns:
            if 'job' in col.lower():
                job_col = col
                break
                
        # Generate Wage
        if job_col:
            df['Wage'] = df[job_col].apply(get_wage)
        else:
            df['Wage'] = [12000000 + random.randint(-2000000, 3000000) for _ in range(len(df))]
            
        # Format wage as integers
        df['Wage'] = df['Wage'].astype(int)
        
        # Save file back
        df.to_excel(file_path, index=False)
        print("Successfully generated wages and saved the Excel file!")
        
    except Exception as e:
        print("Error processing Excel:", e)
else:
    print("Employee Excel file not found in Downloads folder!")
