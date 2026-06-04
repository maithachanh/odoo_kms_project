# -*- coding: utf-8 -*-
"""
Odoo 19 XML-RPC Gateway Client
===============================
This standalone script connects to your local Odoo instance via XML-RPC,
authenticates with the database, and retrieves Knowledge articles along with 
all metadata (Tags, Dimensions, Visibility, etc.).

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

# Define models to query (falls back to kms.knowledge.article if custom model exists)
ARTICLE_MODELS = ['handmade.knowledge.article', 'kms.knowledge.article']
TAG_MODELS = ['handmade.knowledge.tag', 'res.partner.category']

URL = f"http://{HOST}:{PORT}"

def main():
    print("=" * 60)
    print("        ODOO 19 XML-RPC DATA RETRIEVAL GATEWAY")
    print("=" * 60)
    print(f"Connecting to {URL}...")
    
    # 1. Establish connection to common service for authentication
    try:
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        version = common.version()
        print(f"Server Odoo version: {version.get('server_version')}")
    except Exception as e:
        print(f"Error: Cannot connect to Odoo server. Make sure it is running on port {PORT}.")
        print(f"Details: {e}")
        sys.exit(1)

    # 2. Authenticate and get UID
    try:
        uid = common.authenticate(DB, USER, PASSWORD, {})
        if not uid:
            print("Authentication failed! Please check your database name and credentials.")
            sys.exit(1)
        print(f"Authentication successful! User UID: {uid}")
    except Exception as e:
        print(f"Authentication error: {e}")
        sys.exit(1)

    # 3. Establish connection to object service for executing database operations
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

    # Detect which article model is active in the database
    active_article_model = None
    for model in ARTICLE_MODELS:
        try:
            # Check if model exists by trying to search with limit 1
            models.execute_kw(DB, uid, PASSWORD, model, 'search', [[]], {'limit': 1})
            active_article_model = model
            break
        except Exception:
            continue

    if not active_article_model:
        print(f"Error: None of the article models {ARTICLE_MODELS} were found in database '{DB}'.")
        print("Please ensure your custom module is installed and database upgraded.")
        sys.exit(1)
        
    print(f"Active Article Model detected: '{active_article_model}'")

    # Detect which tag model is active
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
    fields_to_read = [
        'name', 
        'content', 
        'visibility', 
        'source_type', 
        'dimension', 
        'functional_topic', 
        'property_4', 
        'tag_ids',
        'breadcrumb_path'
    ]
    
    # We query only active articles (excluding Trash)
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

    # 5. Fetch and map Tag names (Many2many fields return list of IDs like [1, 2])
    tag_mapping = {}
    if active_tag_model:
        # Collect all tag IDs
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

    # 6. Format and Print Data Stream (JSON)
    formatted_articles = []
    for art in articles:
        # Map tag IDs to actual names
        tag_ids = art.get('tag_ids', [])
        tag_names = [tag_mapping.get(tid, f"Tag_{tid}") for tid in tag_ids]
        
        # Clean HTML content snippet for terminal preview (or keep full HTML)
        html_content = art.get('content') or ""
        
        formatted_art = {
            "title": art.get('name'),
            "breadcrumb": art.get('breadcrumb_path') or "Root",
            "html_content": html_content,
            "metadata": {
                "visibility": art.get('visibility'),
                "source": art.get('source_type'),
                "dimension": art.get('dimension'),
                "functional_topic": art.get('functional_topic') or "N/A",
                "property_4": art.get('property_4') or "N/A",
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
