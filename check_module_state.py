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
        print("Updating module list in Odoo...")
        models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'update_list', [])
        
        modules = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read',
            [[['name', 'like', 'contract']]],
            {'fields': ['id', 'name', 'state', 'summary']})
        print("Found modules matching 'contract' after update:")
        print(modules)
except Exception as e:
    print("Error:", e)
