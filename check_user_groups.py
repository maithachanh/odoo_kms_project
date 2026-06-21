import xmlrpc.client

HOST = 'localhost'
PORT = 8069
DB = 'odoo_kms'
URL = f"http://{HOST}:{PORT}"

def check_user(username, password):
    try:
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        uid = common.authenticate(DB, username, password, {})
        if not uid:
            print(f"[{username}] Auth failed")
            return
        
        models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
        
        # Check groups
        is_admin = models.execute_kw(DB, uid, password, 'res.users', 'has_group', [uid, 'base.group_system'])
        is_hr = models.execute_kw(DB, uid, password, 'res.users', 'has_group', [uid, 'kms_knowledge.group_kms_hr_manager'])
        is_it = models.execute_kw(DB, uid, password, 'res.users', 'has_group', [uid, 'kms_knowledge.group_kms_it_staff'])
        
        role = 'public'
        if is_hr or is_admin:
            role = 'hr_manager'
        elif is_it:
            role = 'it_staff'
            
        print(f"User: {username:<8} | UID: {uid:<3} | Admin: {str(is_admin):<5} | HR Manager: {str(is_hr):<5} | IT Staff: {str(is_it):<5} | Mapped Role: {role}")
    except Exception as e:
        print(f"[{username}] Error: {e}")

print("=== User Group & Role Mapping Check ===")
check_user("admin", "admin")
check_user("user1", "password123")
check_user("user2", "password123")
check_user("user3", "password123")
