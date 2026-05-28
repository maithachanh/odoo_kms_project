from pathlib import Path
p = Path('/usr/lib/python3/dist-packages/odoo/tools/translate.py')
s = p.read_text()
old = "if hasattr(local_self, 'env') and (uid := local_self.env.uid):\n            return uid"
new = (
    "local_env = getattr(local_self, 'env', None)\n"
    "        if local_env is not None:\n"
    "            uid = getattr(local_env, 'uid', None)\n"
    "            if uid:\n"
    "                return uid"
)
if old in s:
    s = s.replace(old, new)
    p.write_text(s)
    print('patched')
else:
    print('pattern not found')
