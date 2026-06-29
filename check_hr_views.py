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
        views = models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'search_read',
            [[['model', '=', 'hr.employee']]],
            {'fields': ['id', 'name', 'xml_id', 'type']})
        print("Views for hr.employee:")
        for v in views:
            print(f"ID: {v['id']} | Name: {v['name']} | XML ID: {v['xml_id']} | Type: {v['type']}")
except Exception as e:
    print("Error:", e)
