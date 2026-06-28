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
        module = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read',
            [[['name', '=', 'kms_knowledge']]],
            {'fields': ['id', 'name', 'state', 'latest_version']})
        print(module)
except Exception as e:
    print("Error:", e)
