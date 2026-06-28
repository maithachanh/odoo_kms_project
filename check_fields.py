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
        fields = models.execute_kw(DB, uid, PASSWORD, 'purchase.order.line', 'fields_get',
            [['price_unit', 'product_qty', 'product_id']], {'attributes': ['string', 'type']})
        print("Fields in purchase.order.line:")
        print(fields)
except Exception as e:
    print("Error:", e)
