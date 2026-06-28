import xmlrpc.client
import sys

HOST = 'localhost'
PORT = 8069
DB = 'odoo_kms'
USER = 'admin'
PASSWORD = 'admin'
URL = f"http://{HOST}:{PORT}"

try:
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    uid = common.authenticate(DB, USER, PASSWORD, {})
    if not uid:
        print("Auth failed")
        sys.exit(1)
        
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
    modules = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read', [[('name', '=', 'website')]], {'fields': ['name', 'state']})
    print("Website module status:", modules)
except Exception as e:
    print("Error:", e)
