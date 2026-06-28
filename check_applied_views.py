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
        # Read the combined arch of the view, which shows the final output after inheritance
        view = models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'get_combined_arch', [1952])
        print(view)
except Exception as e:
    print("Error:", e)
