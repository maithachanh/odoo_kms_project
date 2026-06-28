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
            [[['name', '=', 'sale.order.tree.inherit.all']]],
            {'fields': ['id', 'name', 'active', 'arch_db']})
        if views:
            print("Found inheriting view:")
            print(views[0])
        else:
            print("Inheriting view not found in the DB!")
except Exception as e:
    print("Error:", e)
