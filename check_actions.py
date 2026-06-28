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
        
        # Search ir.model.data for the actions
        data_records = models.execute_kw(DB, uid, PASSWORD, 'ir.model.data', 'search_read',
            [[
                ['model', '=', 'ir.actions.act_window'],
                ['module', 'in', ['purchase', 'sale', 'product']],
                ['name', 'in', ['purchase_form_action', 'product_template_action']]
            ]],
            {'fields': ['module', 'name', 'res_id']})
        print("Found XML IDs in ir.model.data:")
        for r in data_records:
            print(f"XML ID: {r['module']}.{r['name']} | ID: {r['res_id']}")
except Exception as e:
    print("Error:", e)
