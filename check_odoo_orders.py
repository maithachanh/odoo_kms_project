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
    if not uid:
        print("Auth failed!")
    else:
        models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
        
        # Test PO
        try:
            po_count = models.execute_kw(DB, uid, PASSWORD, 'purchase.order', 'search_count', [[]])
            print("Purchase Orders (PO) count:", po_count)
            if po_count > 0:
                pos = models.execute_kw(DB, uid, PASSWORD, 'purchase.order', 'search_read', [[]], {'fields': ['name', 'amount_total'], 'limit': 5})
                for po in pos:
                    print(f"  - PO: {po.get('name')} | Total: {po.get('amount_total')}")
        except Exception as e:
            print("Error querying purchase.order:", e)
            
        # Test SO
        try:
            so_count = models.execute_kw(DB, uid, PASSWORD, 'sale.order', 'search_count', [[]])
            print("Sales Orders (SO) count:", so_count)
            if so_count > 0:
                sos = models.execute_kw(DB, uid, PASSWORD, 'sale.order', 'search_read', [[]], {'fields': ['name', 'amount_total'], 'limit': 5})
                for so in sos:
                    print(f"  - SO: {so.get('name')} | Total: {so.get('amount_total')}")
        except Exception as e:
            print("Error querying sale.order:", e)
            
except Exception as e:
    print("General Error:", e)
