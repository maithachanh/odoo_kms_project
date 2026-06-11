# BA Access Control Matrix – KMS Knowledge Articles

## Workspace Dimension & Access Role Mapping

| Article Title                            | Workspace Dimension | Access Role  | Target Synonym Keywords                                  |
|------------------------------------------|---------------------|--------------|----------------------------------------------------------|
| IT Engineer Onboarding Protocol          | it                  | it_staff     | onboarding, welcome, new hire, developer, engineer       |
| Network Security & System Firewall Policy| it                  | it_staff     | security, firewall, system safety, port, infractions     |
| Acceptable Hardware Use Agreement        | general             | public       | hardware, disciplinary, safety, computing, violations    |
| General Workspace Conduct Guideline      | general             | public       | welcome, workspace, conduct, incoming, cross-functional  |
| HR Onboarding Protocol                   | hr                  | hr_manager   | onboarding, new hire, employment, contract, handbook     |

## Access Control Rules
- `hr` dimension     → `hr_manager` role only
- `it` dimension     → `it_staff` role (+ `public` can also read general)
- `general` dimension→ `public` (all roles)

## Data Source
- Odoo model: `kms.knowledge.article`
- Fetched via XML-RPC on port 8069
- Fields extracted: `name`, `body`, `workspace_dimension`, `access_role`, `tags`
