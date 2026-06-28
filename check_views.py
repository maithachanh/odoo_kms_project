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
            [[['model', '=', 'sale.order']]],
            {'fields': ['id', 'name', 'xml_id', 'type', 'inherit_id']})
        print("Found views for sale.order:")
        for v in views:
            print(f"ID: {v['id']} | Name: {v['name']} | XML ID: {v['xml_id']} | Type: {v['type']} | Inherits: {v['inherit_id']}")
except Exception as e:
    print("Error:", e)
