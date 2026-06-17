# -*- coding: utf-8 -*-
"""
Odoo 19 XML-RPC Gateway Client
===============================
This standalone script connects to your local Odoo instance via XML-RPC,
authenticates with the database, and retrieves KMS articles along with 
all metadata (Tags, Dimensions, etc.) as required by Task 10.2.

Requirements:
- Odoo running on http://localhost:8069
- Database: odoo_kms
- Credentials: admin / admin
"""

import xmlrpc.client
import json
import sys

# ---- CONFIGURATION ----
HOST = 'localhost'
PORT = 8069
DB = 'odoo_kms'
USER = 'admin'
PASSWORD = 'admin'

# Define models to query (primary: assignment kms, secondary: handmade)
ARTICLE_MODELS = ['kms.knowledge.article', 'handmade.knowledge.article']
TAG_MODELS = ['res.partner.category', 'handmade.knowledge.tag']

URL = f"http://{HOST}:{PORT}"

def main():
    print("=" * 60)
    print("        KMS METADATA-AWARE XML-RPC GATEWAY CLIENT")
    print("=" * 60)
    print(f"Connecting to {URL}...")
    
    # 1. Establish connection to common service for authentication
    try:
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        version = common.version()
        print(f"Server Odoo version: {version.get('server_version')}")
    except Exception as e:
        print(f"Error: Cannot connect to Odoo server. Make sure Odoo is running.")
        print(f"Details: {e}")
        sys.exit(1)

    # 2. Authenticate and get UID
    try:
        uid = common.authenticate(DB, USER, PASSWORD, {})
        if not uid:
            print("Authentication failed! Please check credentials.")
            sys.exit(1)
        print(f"Authentication successful! User UID: {uid}")
    except Exception as e:
        print(f"Authentication error: {e}")
        sys.exit(1)

    # 3. Establish connection to object service
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

    # Detect active article model in the database
    active_article_model = None
    for model in ARTICLE_MODELS:
        try:
            models.execute_kw(DB, uid, PASSWORD, model, 'search', [[]], {'limit': 1})
            active_article_model = model
            break
        except Exception:
            continue

    if not active_article_model:
        print(f"Error: None of the models {ARTICLE_MODELS} were found.")
        sys.exit(1)
        
    print(f"Active Article Model detected: '{active_article_model}'")

    # Detect active tag model
    active_tag_model = None
    for model in TAG_MODELS:
        try:
            models.execute_kw(DB, uid, PASSWORD, model, 'search', [[]], {'limit': 1})
            active_tag_model = model
            break
        except Exception:
            continue
    print(f"Active Tag Model detected: '{active_tag_model}'")

    # 4. Fetch Articles
    print(f"\nQuerying articles from '{active_article_model}'...")
    
    # Use fields corresponding to the active model schema
    if active_article_model == 'kms.knowledge.article':
        fields_to_read = [
            'name', 
            'body_html', 
            'workspace_dimension', 
            'tag_ids',
            'breadcrumb_path'
        ]
    else:
        # Fallback to old handmade model fields
        fields_to_read = [
            'name', 
            'content', 
            'visibility', 
            'tag_ids',
            'breadcrumb_path'
        ]
        
    domain = [('active', '=', True)]
    
    try:
        articles = models.execute_kw(
            DB, uid, PASSWORD, 
            active_article_model, 
            'search_read', 
            [domain], 
            {'fields': fields_to_read}
        )
        print(f"Retrieved {len(articles)} active articles.")
    except Exception as e:
        print(f"Error reading articles: {e}")
        sys.exit(1)

    # 5. Fetch and map Tag names
    tag_mapping = {}
    if active_tag_model:
        all_tag_ids = set()
        for art in articles:
            if art.get('tag_ids'):
                all_tag_ids.update(art['tag_ids'])
        
        if all_tag_ids:
            try:
                tags_data = models.execute_kw(
                    DB, uid, PASSWORD, 
                    active_tag_model, 
                    'read', 
                    [list(all_tag_ids)], 
                    {'fields': ['name']}
                )
                tag_mapping = {tag['id']: tag['name'] for tag in tags_data}
            except Exception as e:
                print(f"Warning: Failed to fetch tag details: {e}")

    # 6. Format and Print Data Stream
    formatted_articles = []
    for art in articles:
        tag_ids = art.get('tag_ids', [])
        tag_names = [tag_mapping.get(tid, f"Tag_{tid}") for tid in tag_ids]
        
        # Select correct content and dimension based on active schema
        content_val = art.get('body_html') if 'body_html' in art else art.get('content', '')
        dimension_val = art.get('workspace_dimension') if 'workspace_dimension' in art else art.get('visibility', 'N/A')
        
        formatted_art = {
            "title": art.get('name'),
            "breadcrumb": art.get('breadcrumb_path') or "Root",
            "html_content": content_val or "",
            "metadata": {
                "dimension": dimension_val,
                "tags": tag_names
            }
        }
        formatted_articles.append(formatted_art)

    # Print final JSON output stream
    print("\n" + "=" * 60)
    print("                    DATA STREAM OUTPUT (JSON)")
    print("=" * 60)
    json_str = json.dumps(formatted_articles, indent=4, ensure_ascii=False)
    try:
        print(json_str)
    except UnicodeEncodeError:
        sys.stdout.flush()
        sys.stdout.buffer.write((json_str + "\n").encode('utf-8'))
    print("=" * 60)
    print("Data stream successfully retrieved and printed.")

if __name__ == '__main__':
    main()
