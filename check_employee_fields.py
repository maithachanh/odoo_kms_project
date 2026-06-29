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
        fields = models.execute_kw(DB, uid, PASSWORD, 'hr.employee', 'fields_get',
            [[]], {'attributes': ['string', 'type', 'relation']})
        print("Employee fields containing 'wage' or 'contract':")
        for name, info in fields.items():
            if 'wage' in name or 'contract' in name or 'wage' in info.get('string', '').lower() or 'contract' in info.get('string', '').lower():
                print(f"Name: {name} | Label: {info['string']} | Type: {info['type']} | Relation: {info.get('relation', '')}")
except Exception as e:
    print("Error:", e)
