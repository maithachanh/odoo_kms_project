# Access Control Matrix - KMS Knowledge Base

This document details the mapping between article workspaces, access roles, and synonyms as defined by the Business Analyst (BA) for Week 11 and Week 12.

## 1. Access Control Mapping Rules

According to corporate data security guidelines:
- **HR Workspace (`hr`)** articles are restricted to **`hr_manager`** only.
- **IT Workspace (`it`)** articles are restricted to **`it_staff`** and `hr_manager`.
- **General Workspaces (`sales`, `ops`, `legal`, etc.)** articles are accessible to **`public`** (all roles).

---

## 2. Article Access Matrix & Synonym Reference

| Article Title / Display Name | Workspace Dimension | Access Role | Target Synonym List (For Search Testing) | Description / Sample Content |
| :--- | :---: | :---: | :--- | :--- |
| **IT Engineer Onboarding Protocol** | `it` | `it_staff` | `["welcome new developer", "setup pc", "onboarding dev", "welcome dev"]` | Standard onboarding protocol for new engineering hires to setup local environment and tools. |
| **HR Onboarding Handbook** | `hr` | `hr_manager` | `["welcome new employee", "onboard staff", "hr handbook"]` | Policy for welcoming general cross-functional employees and setting up payroll/contracts. |
| **Network Security & System Firewall Policy** | `it` | `it_staff` | `["system safety", "firewall config", "network security"]` | Procedures for troubleshooting network ports and handling security infractions. |
| **Acceptable Hardware Use Agreement** | `ops` (General) | `public` | `["hardware safety", "laptop policy", "disciplinary action"]` | General policy detailing acceptable hardware use and basic safety rules for all company devices. |
| **Quy trình Bàn giao Công việc khi Nghỉ việc** | `hr` | `hr_manager` | `["resign", "leave job", "quit", "handover"]` | Detailed process for handing over roles and terminating accounts upon resignation. |
| **Quy trình Vận hành Máy chủ và Backup** | `ops` (General) | `public` | `["server backup", "ops procedure", "ops guidelines"]` | Daily check protocols and backup schedule for server logs and database files. |
| **Troubleshooting** | `ops` (General) | `public` | `["fix issues", "error support", "ops help"]` | Resolving common operational blockages for customer support agents. |
| **Customer Complaint Handling** | `sales` (General) | `public` | `["complaint support", "customer feedback", "sales ops"]` | Standard procedures for dealing with unhappy clients and processing returns. |
| **VIP Customer Privileges** | `sales` (General) | `public` | `["vip benefits", "discount policy", "loyalty program"]` | Guide on handling high-net-worth client accounts and applying custom discounts. |

---

## 3. Security Filtering Logic in Querying

When simulating a user query:
*   A **Public user** can only query chunks with `access_role = public`.
*   An **IT Staff user** can query chunks with `access_role = it_staff` OR `access_role = public`.
*   An **HR Manager user** can query all chunks (`hr_manager`, `it_staff`, or `public`).
