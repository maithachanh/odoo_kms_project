import xmlrpc.client
import pandas as pd

HOST = 'localhost'
PORT = 8069
DB = 'odoo_kms'
URL = f"http://{HOST}:{PORT}"
USER = 'admin'
PASSWORD = 'admin'

def safe_print(msg):
    try:
        print(msg)
    except Exception:
        try:
            print(msg.encode('utf-8', errors='ignore').decode('ascii', errors='ignore'))
        except Exception:
            pass

def clean_val(val):
    if pd.isna(val) or val == 'NaN' or val == '':
        return False
    return str(val).strip()

try:
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    uid = common.authenticate(DB, USER, PASSWORD, {})
    if uid:
        models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
        
        # Read the Excel file
        file_path = r"C:\Users\nhan\Downloads\new_Employee (hr.employee) (3).xlsx"
        df = pd.read_excel(file_path)
        safe_print(f"Reading {len(df)} rows from Excel...")
        
        # 1. Resolve or Create Departments
        safe_print("Resolving departments...")
        dept_cache = {}
        for index, row in df.iterrows():
            dept_name = clean_val(row.get('Department'))
            if dept_name and dept_name not in dept_cache:
                dept_ids = models.execute_kw(DB, uid, PASSWORD, 'hr.department', 'search', [[['name', '=', dept_name]]])
                if dept_ids:
                    dept_cache[dept_name] = dept_ids[0]
                else:
                    dept_id = models.execute_kw(DB, uid, PASSWORD, 'hr.department', 'create', [{'name': dept_name}])
                    dept_cache[dept_name] = dept_id
                    safe_print(f"Created Department: {dept_name}")
                    
        # 2. Resolve or Create Job Positions
        safe_print("Resolving job positions...")
        job_cache = {}
        for index, row in df.iterrows():
            job_name = clean_val(row.get('Job'))
            if job_name and job_name not in job_cache:
                job_ids = models.execute_kw(DB, uid, PASSWORD, 'hr.job', 'search', [[['name', '=', job_name]]])
                if job_ids:
                    job_cache[job_name] = job_ids[0]
                else:
                    job_id = models.execute_kw(DB, uid, PASSWORD, 'hr.job', 'create', [{'name': job_name}])
                    job_cache[job_name] = job_id
                    safe_print(f"Created Job Position: {job_name}")

        # 3. Create or Update Employees
        safe_print("Creating/updating employee records...")
        emp_ids_by_name = {}
        created_count = 0
        updated_count = 0
        for index, row in df.iterrows():
            emp_name = clean_val(row.get('Employee Name'))
            if not emp_name:
                continue
                
            email = clean_val(row.get('Work Email'))
            phone = clean_val(row.get('Work Phone'))
            dept_name = clean_val(row.get('Department'))
            job_name = clean_val(row.get('Job'))
            wage_val = row.get('Wage')
            wage = int(wage_val) if not pd.isna(wage_val) else 0
            
            vals = {
                'name': emp_name,
                'work_email': email or False,
                'work_phone': phone or False,
                'department_id': dept_cache.get(dept_name, False),
                'job_id': job_cache.get(job_name, False),
                'wage': wage
            }
            
            emp_ids = models.execute_kw(DB, uid, PASSWORD, 'hr.employee', 'search', [[['name', '=', emp_name]]])
            if emp_ids:
                models.execute_kw(DB, uid, PASSWORD, 'hr.employee', 'write', [[emp_ids[0]], vals])
                emp_ids_by_name[emp_name] = emp_ids[0]
                updated_count += 1
            else:
                emp_id = models.execute_kw(DB, uid, PASSWORD, 'hr.employee', 'create', [vals])
                emp_ids_by_name[emp_name] = emp_id
                created_count += 1
        
        safe_print(f"Employees created: {created_count}, updated: {updated_count}")
                
        # 4. Link Managers (parent_id)
        safe_print("Linking managers to employees...")
        linked_count = 0
        for index, row in df.iterrows():
            emp_name = clean_val(row.get('Employee Name'))
            manager_name = clean_val(row.get('Manager'))
            if emp_name and manager_name:
                emp_id = emp_ids_by_name.get(emp_name)
                manager_id = emp_ids_by_name.get(manager_name)
                if not manager_id:
                    m_ids = models.execute_kw(DB, uid, PASSWORD, 'hr.employee', 'search', [[['name', '=', manager_name]]])
                    if m_ids:
                        manager_id = m_ids[0]
                        emp_ids_by_name[manager_name] = manager_id
                
                if emp_id and manager_id:
                    models.execute_kw(DB, uid, PASSWORD, 'hr.employee', 'write', [[emp_id], {'parent_id': manager_id}])
                    linked_count += 1
                    
        safe_print(f"Successfully linked {linked_count} managers.")
        safe_print("Import completed successfully!")
except Exception as e:
    safe_print(f"Error during import: {e}")
