import xmlrpc.client

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
        print("Auth failed!")
    else:
        models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
        articles = models.execute_kw(
            DB, uid, PASSWORD, 
            'kms.knowledge.article', 
            'search_read', 
            [[('active', '=', True)]], 
            {'fields': ['name', 'workspace_dimension', 'access_role']}
        )
        print("=== Articles in Odoo ===")
        for art in sorted(articles, key=lambda x: x.get('name') or ''):
            print(f"- Title: {art.get('name'):<50} | Role: {art.get('access_role'):<12} | Workspace: {art.get('workspace_dimension')}")
except Exception as e:
    print("Error:", e)
