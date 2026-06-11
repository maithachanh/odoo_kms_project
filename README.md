# Odoo v19 Community Local Deployment & Knowledge Migration

## 🎯 Project Goal
Deploy a **local Odoo 19 Community** environment using Docker, expose the PostgreSQL database, activate the **Website** and **Live Chat** modules, install the **To‑Do** module (as a lightweight KMS), and provide a clear workflow for importing Phase 1 SOP/Documentation data (Excel) and for connecting external DB clients (pgAdmin/DBeaver).

---

## 📁 Repository Layout (`d:\odoo19-local`)
```
├─ docker-compose.yml          # Docker services (Postgres + Odoo) – port 5433 exposed
├─ odoo.conf                  # Odoo configuration (admin password = admin)
├─ odoo-data/                 # Persistent Odoo data (mounted in container)
├─ postgres-data/             # Persistent PostgreSQL data (mounted in container)
├─ odoo-patches/              # Custom patch for translate.py (optional)
├─ .dbeaver-data-sources.xml  # DBeaver data source configuration (generated)
└─ README.md                  # ⬅️ This file
```

---

## 🛠️ 1. Starting the Environment (Docker)
```bash
# From the project root (d:\odoo19-local) run:
 docker-compose up -d   # pulls postgres:15 and odoo:19.0 images, creates containers
```
- **Odoo container**: `odoo19-web` (exposes port **8069** → http://localhost:8069)
- **PostgreSQL container**: `odoo19-db` (exposes port **5433** on host → host can connect directly)
- The `docker‑compose.yml` already maps `5433:5432` so GUI tools can reach the DB.

### Restart / Re‑create a service (e.g., after config change)
```bash
# Re‑create only the DB container (useful when exposing new ports)
 docker-compose up -d --force-recreate db

# Restart Odoo to load new config
 docker-compose restart odoo
```

---

## 🔐 2. Odoo Login Details
- **URL:** `http://localhost:8069`
- **Database name:** `odoo_kms` (created automatically during the first CLI install)
- **Admin user:**
  - **Login:** `admin`
  - **Password:** `admin`
- The master password used by the CLI (`odoo.conf`) is also `admin` (plain‑text for simplicity).

> **Tip:** If you need to change the admin password, edit `odoo.conf` → `admin_passwd = <new>` and restart the Odoo container.

---

## 📂 3. Database Access (PostgreSQL)
You can connect from any client that supports PostgreSQL (pgAdmin, DBeaver, psql, etc.).

| Parameter | Value |
|---|---|
| **Host** | `localhost` |
| **Port** | `5433` |
| **Username** | `odoo` |
| **Password** | `odoo` |
| **Database** | `odoo_kms` |

### Example with `psql`
```bash
docker exec -it odoo19-db psql -U odoo -d odoo_kms
```
You will land in the PostgreSQL prompt (`odoo_kms=>`).

---

## ⚙️ 4. DBeaver Configuration
A ready‑to‑use DBeaver data source file has been generated:

- File: **`.dbeaver-data-sources.xml`** (placed in the project root).
- It defines a PostgreSQL connection named **`odoo_local_pg`** with the credentials shown above.

### Importing into DBeaver
1. Open DBeaver.
2. Choose **File → Import…**.
3. Select **DBeaver → Data Sources** and click **Next**.
4. Click **Browse** and locate the `.dbeaver-data-sources.xml` file in the project folder.
5. Finish the wizard. The new connection will appear in the **Database Navigator**.
6. Double‑click the connection to test it; you should be connected to the `odoo_kms` database.

If you prefer to create the connection manually, use the same parameters listed in section **3**.

---

## 🧩 5. Modules Installed (via CLI)
The following core modules are **pre‑installed**:
- `base`
- `website`
- `website_livechat`
- `project_todo` (the **To‑Do** app used as a lightweight Knowledge‑Management module)
- All their dependencies (e.g., `mail`, `web`, `project`, `website_mail`, `website_project`, …)

You can verify in the UI under **Apps → Installed**.

---

## 📦 6. Live Chat Widget (Task 4.3)
1. Open **Live Chat** app → create/select a channel (e.g., *Support*).
2. Go to **Website → Configuration → Settings** → enable **Live Chat** and select the channel.
3. Visit the public site `http://localhost:8069` as a guest; you should see the chat bubble in the lower‑right corner.

---

## 📊 7. Importing Phase 1 SOP Data (Excel → To‑Do)
1. **Create a sample To‑Do record** in Odoo (Title, Description, Tags).
2. Switch to **List View**, select the record, choose **Action → Export**.
   - Export the fields `name`, `description`, `tag_ids` (or whatever tag field you use).
   - Save as **Excel** (`template.xlsx`).
3. **Map your Phase 1 Excel** columns to the template columns:
   - `Article Title` → `Name`
   - `Procedural Content` → `Description` (HTML allowed)
   - `Metadata Labels` → `Tags`
4. Paste your data into the template, then **Import** back via **Action → Import**.
5. Verify the imported records appear correctly in the **To‑Do** list.

---

## 🛠️ 8. Common Commands Cheat‑Sheet
| Command | Description |
|---|---|
| `docker ps` | List running containers |
| `docker logs odoo19-web` | View Odoo logs |
| `docker exec odoo19-web odoo -c /etc/odoo/odoo.conf -d odoo_kms -i base,website_livechat,project_todo --without-demo=True --stop-after-init` | Re‑initialize DB and install modules |
| `docker-compose down` | Stop & remove containers (data stays in volumes) |
| `docker-compose up -d` | Bring everything back up |
| `docker exec -it odoo19-db psql -U odoo -d odoo_kms` | Open a psql shell inside the DB container |

---

## 📚 9. Where to Find More Info
- **Official Odoo Docker Guide:** https://github.com/odoo/docker
- **Odoo 19 Export/Import Docs:** https://www.odoo.com/documentation/19.0/applications/general/export_import.html
- **Live Chat Documentation:** https://www.odoo.com/documentation/19.0/applications/websites/website/livechat.html

---

## 👥 10. Team On‑boarding Checklist
1. Clone the repository and run `docker-compose up -d`.
2. Open http://localhost:8069, log in with `admin`/`admin`.
3. Verify the **Live Chat** widget appears on the homepage.
4. Connect your DB client using the credentials above (or import the DBeaver data source).
5. Import the Phase 1 Excel using the template workflow.
6. Start using the **To‑Do** module as your KMS – add, edit, tag SOPs.

---

**Enjoy your local Odoo 19 environment!** 🎉
