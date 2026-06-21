# KMS Permission Configuration Result

## Scope

Configured the KMS system around the two internal roles requested:

- `hr_manager`
- `it_staff`

The default employee role remains `public` for normal users.

## Access Logic Applied

| Workspace Dimension | Access Role | Effective Access |
| --- | --- | --- |
| `hr` | `hr_manager` | HR Manager can access it. |
| `it` | `it_staff` | IT Staff and HR Manager can access it. |
| `sales`, `purchase`, `helpdesk`, `foh`, `technical`, `ops`, `legal` | `public` | Public, IT Staff, and HR Manager can access it. |

This matches the FoodHub public rows in the provided matrix, including `technical` articles such as `POS System Troubleshooting Guide` being treated as `public`.

## Files Changed

### `custom_addons/kms_knowledge/security/kms_security.xml`

Created new Odoo security configuration:

- Added `KMS IT Staff` group.
- Added `KMS HR Manager` group.
- Made `KMS HR Manager` imply `KMS IT Staff`.
- Made Odoo system administrators imply `KMS HR Manager`.
- Added record rules:
  - Public users see only `access_role = public`.
  - IT Staff sees `public` and `it_staff`.
  - HR Manager sees all articles.

### `custom_addons/kms_knowledge/security/ir.model.access.csv`

Updated ACLs for `kms.knowledge.article`:

- `base.group_user`: read-only access.
- `kms_knowledge.group_kms_it_staff`: read/write/create access, no unlink.
- `kms_knowledge.group_kms_hr_manager`: full access.

AI Agent and chat line ACLs were left unchanged.

### `custom_addons/kms_knowledge/models/kms_knowledge_article.py`

Added computed stored field:

- `access_role`

Mapping:

- `workspace_dimension == 'hr'` -> `hr_manager`
- `workspace_dimension == 'it'` -> `it_staff`
- all other workspaces -> `public`

Also updated AI Chatbot request role mapping:

- HR Manager group or system admin sends `role = hr_manager` to RAG API.
- IT Staff group sends `role = it_staff`.
- Other users send `role = public`.

### `custom_addons/kms_knowledge/views/kms_knowledge_article_views.xml`

Updated the Article UI:

- Added `Access Role` column in list view.
- Added readonly `Access Role` field in form properties.
- Added search filters for:
  - Public Access
  - IT Staff Access
  - HR Manager Access
- Added missing `IT` workspace filter.

### `custom_addons/kms_knowledge/__manifest__.py`

Registered the new security XML before `ir.model.access.csv` so Odoo can resolve the new groups during module upgrade.

### `ingest_to_vector.py`

Updated vector ingestion permission handling:

- Added workspace-to-role mapping shared with Odoo logic.
- Added fallback parser for `markdown/access_matrix.md` when `access_matrix.xlsx` is missing.
- Fetches `workspace_dimension` and `access_role` from Odoo XML-RPC.
- Preserves article metadata in ChromaDB:
  - `workspace_dimension`
  - `access_role`
  - `tags`

### `markdown/access_matrix.md`

Added the FoodHub public article rows from the provided matrix:

- `Poor Payment History Customer`
- `POS Pricing Fixes`
- `Recommended Time for Purchasing`
- `Avoid Purchasing at Unusually Low Prices`
- `Preventing Missing or Incorrect Item Deliveries`
- `POS System Troubleshooting Guide`

## Verification Performed

Ran Python syntax check:

```powershell
python -m py_compile custom_addons\kms_knowledge\models\kms_knowledge_article.py ingest_to_vector.py rag_engine.py rag_api.py
```

Result: passed.

Ran XML parse check:

```powershell
python -c "import xml.etree.ElementTree as ET; [ET.parse(p) for p in ['custom_addons/kms_knowledge/security/kms_security.xml','custom_addons/kms_knowledge/views/kms_knowledge_article_views.xml','custom_addons/kms_knowledge/data/kms_ai_agent_data.xml']]; print('xml ok')"
```

Result: `xml ok`.

## Permission-Denied Behavior Update

Updated `rag_engine.py` so restricted questions no longer fall through to a public document answer.

New behavior:

- The RAG engine first checks the best matching document across the full vector database.
- If that best matching document is restricted and the current user role cannot access it, the API returns:

```text
You do not have permission to access this information. Please contact an authorized manager or administrator if you need access.
```

- Only users with a valid role can receive the answer:
  - `hr_manager` can access `hr_manager`, `it_staff`, and `public` documents.
  - `it_staff` can access `it_staff` and `public` documents.
  - `public` can access only `public` documents.

Updated `custom_addons/kms_knowledge/models/kms_knowledge_article.py` so Odoo chat history shows:

```text
NO PERMISSION
```

in the `Sources` column when the RAG API returns `permission_denied = true`.

### Immediate Test Case

Question:

```text
How should employee resignation and offboarding be handled?
```

Expected result:

| Role | Expected Behavior |
| --- | --- |
| `hr_manager` | Gets an answer from `Employee Resignation and Offboarding SOP`. |
| `it_staff` | Gets no-permission response. |
| `public` | Gets no-permission response. |

Important: restart `rag_api.py` after this code change so the new permission gate is active.

## Not Run

I did not upgrade the live Odoo module or rebuild ChromaDB in this run.

Recommended next commands:

```powershell
docker exec -i odoo19-web odoo -d odoo_kms -u kms_knowledge --stop-after-init
docker restart odoo19-web
python ingest_to_vector.py
```
