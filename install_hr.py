import xmlrpc.client

HOST = 'localhost'
PORT = 8069
DB = 'odoo_kms'
URL = f"http://{HOST}:{PORT}"
USER = 'admin'
PASSWORD = 'admin'

try:
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    uid = common.authenticate(DB, USER, PASSWORD, {})
    if uid:
        models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
        
        # Find 'hr' module
        modules = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read',
            [[['name', '=', 'hr']]], {'fields': ['id', 'state']})
        if modules:
            module_id = modules[0]['id']
            state = modules[0]['state']
            print(f"Found 'hr' module (ID: {module_id}, State: {state})")
            if state != 'installed':
                print("Installing 'hr' module...")
                models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'button_immediate_install', [[module_id]])
                print("Installation triggered successfully!")
            else:
                print("'hr' module is already installed!")
        else:
            print("Module 'hr' not found in Odoo module list!")
except Exception as e:
    print("Error:", e)
