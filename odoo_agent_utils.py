# -*- coding: utf-8 -*-
"""
Odoo Agent Utilities for calculation and keyword search
======================================================
Provides helper functions to connect to local Odoo database via XML-RPC,
detect query intents, perform aggregate calculations (sum, avg, diff, count) on PO/SO,
and search for products/orders to return clickable Odoo form links.
Includes model presence checking to gracefully handle missing Odoo modules (e.g. sale, purchase).
"""

import os
import xmlrpc.client
import re
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Odoo connection settings
HOST = os.getenv("ODOO_HOST", "localhost")
PORT = os.getenv("ODOO_PORT", "8069")
DB = os.getenv("ODOO_DB", "odoo_kms")
USER = os.getenv("ODOO_USER", "admin")
PASSWORD = os.getenv("ODOO_PASSWORD", "admin")

import socket
# Set default socket timeout of 10 seconds for XML-RPC
socket.setdefaulttimeout(10)

# Dynamically construct Odoo URL (supporting cloud & local)
ODOO_URL = os.getenv("ODOO_URL")
if not ODOO_URL:
    scheme = "https" if PORT == "443" else "http"
    host_clean = HOST.replace("http://", "").replace("https://", "").strip("/")
    ODOO_URL = f"{scheme}://{host_clean}:{PORT}"

def get_odoo_client():
    """Returns ServerProxy objects for Odoo common and object services."""
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common', allow_none=True)
        uid = common.authenticate(DB, USER, PASSWORD, {})
        if not uid:
            print("[ODOO] Authentication failed.")
            return None, None, None
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object', allow_none=True)
        return common, uid, models
    except Exception as e:
        print(f"[ODOO ERROR] Connection failed: {e}")
        return None, None, None

def check_model_exists(models, uid, model_name):
    """Checks if an Odoo model exists in the database to prevent Fault 2."""
    if not models or not uid:
        return False
    try:
        models.execute_kw(DB, uid, PASSWORD, model_name, 'search', [[]], {'limit': 0})
        return True
    except Exception:
        return False

def detect_intents(query_string):
    """
    Detects if the query requires Odoo Calculations or Keyword Searching.
    Returns:
        is_calculation (bool), is_search (bool), keywords (list)
    """
    q_lower = query_string.lower().strip()
    
    # 1. Calculation intent detection
    calc_words = ["tổng", "trung bình", "hiệu", "bao nhiêu đơn", "doanh số", "giá trị", "đếm", "số lượng", "cộng", "trừ", "chia", "sum", "average", "avg", "count", "difference", "diff"]
    po_so_words = ["po", "so", "đơn mua", "đơn bán", "đơn hàng mua", "đơn hàng bán", "sale order", "purchase order", "sales order", "sales orders", "purchase orders"]
    
    has_calc_word = any(w in q_lower for w in calc_words)
    has_po_so_word = any(w in q_lower for w in po_so_words)
    
    is_calculation = has_calc_word and has_po_so_word
    
    # 2. Search/Link intent detection
    stopwords = {
        "tìm", "kiếm", "cho", "tôi", "thông", "tin", "về", "sản", "phẩm", "link", "liên", "kết", 
        "đường", "dẫn", "hỏi", "là", "gì", "như", "thế", "nào", "ở", "đâu", "bao", "nhiêu", 
        "tính", "tổng", "trung", "bình", "hiệu", "đơn", "hàng", "mua", "bán", "của", "và", 
        "trong", "hệ", "thống", "có", "sẵn", "mặt", "hàng", "liên quan", "đến", "hiển", "thị", 
        "show", "find", "get", "link", "url", "hãy", "giúp"
    }
    
    words = re.findall(r'\b\w+\b', q_lower)
    keywords = [w for w in words if w not in stopwords and len(w) > 1]
    
    order_pattern = re.findall(r'\b[sp]o\d+\b', q_lower)
    if order_pattern:
        keywords = order_pattern + keywords
        is_search = True
    else:
        search_triggers = ["sản phẩm", "mặt hàng", "link", "đường dẫn", "coca", "burger", "pizza", "nước ngọt", "cơm", "gà", "fries", "khoai tây", "kem", "bánh", "drink", "food"]
        is_search = any(t in q_lower for t in search_triggers) or (len(keywords) > 0 and not is_calculation)
        
    return is_calculation, is_search, list(set(keywords))

def fetch_live_po_so_summary():
    """Queries Odoo PO/SO records and computes aggregates. Safely handles missing models."""
    common, uid, models = get_odoo_client()
    if not models:
        return "Warning: Could not connect to local Odoo database to fetch live PO/SO data."
        
    has_so = check_model_exists(models, uid, 'sale.order')
    has_po = check_model_exists(models, uid, 'purchase.order')
    
    if not has_so and not has_po:
        return (
            "--- LIVE ODOO DATABASE NOTICE ---\n"
            "Cảnh báo: Cả hai mô-đun Bán hàng (Sale) và Mua hàng (Purchase) đều chưa được cài đặt trên hệ thống Odoo cục bộ.\n"
            "Vui lòng cài đặt các mô-đun này để có thể thực hiện tính toán PO/SO.\n"
            "---------------------------------"
        )
        
    summary_parts = ["--- LIVE ODOO TRANSACTIONAL DATA ---"]
    so_total, po_total = 0.0, 0.0
    
    # Process Sales Orders (SO)
    if has_so:
        try:
            so_records = models.execute_kw(DB, uid, PASSWORD, 'sale.order', 'search_read', [[]], {'fields': ['name', 'amount_total', 'state']})
            so_count = len(so_records)
            so_total = sum(r.get('amount_total', 0.0) for r in so_records)
            so_avg = so_total / so_count if so_count > 0 else 0.0
            summary_parts.append(
                f"Sales Orders (SO) Summary:\n"
                f"  - Total Count: {so_count}\n"
                f"  - Total Amount: {so_total:,.2f} VND\n"
                f"  - Average Amount: {so_avg:,.2f} VND"
            )
        except Exception as e:
            summary_parts.append(f"Sales Orders (SO) Error: Could not query data ({e})")
    else:
        summary_parts.append("Sales Orders (SO) Info: Mô-đun Bán hàng (Sale) chưa được cài đặt.")
        
    # Process Purchase Orders (PO)
    if has_po:
        try:
            po_records = models.execute_kw(DB, uid, PASSWORD, 'purchase.order', 'search_read', [[]], {'fields': ['name', 'amount_total', 'state']})
            po_count = len(po_records)
            po_total = sum(r.get('amount_total', 0.0) for r in po_records)
            po_avg = po_total / po_count if po_count > 0 else 0.0
            summary_parts.append(
                f"Purchase Orders (PO) Summary:\n"
                f"  - Total Count: {po_count}\n"
                f"  - Total Amount: {po_total:,.2f} VND\n"
                f"  - Average Amount: {po_avg:,.2f} VND"
            )
        except Exception as e:
            summary_parts.append(f"Purchase Orders (PO) Error: Could not query data ({e})")
    else:
        summary_parts.append("Purchase Orders (PO) Info: Mô-đun Mua hàng (Purchase) chưa được cài đặt.")
        
    # Comparison Calculations
    if has_so and has_po:
        difference_so_po = so_total - po_total
        difference_po_so = po_total - so_total
        summary_parts.append(
            f"Comparison Calculations:\n"
            f"  - Difference (Total SO - Total PO): {difference_so_po:,.2f} VND\n"
            f"  - Difference (Total PO - Total SO): {difference_po_so:,.2f} VND"
        )
        
    summary_parts.append("-------------------------------------")
    return "\n\n".join(summary_parts)

def search_odoo_records(keywords):
    """
    Searches products, sales orders, and purchase orders in Odoo by keywords.
    Generates markdown links. Safely handles missing models.
    """
    if not keywords:
        return ""
        
    common, uid, models = get_odoo_client()
    if not models:
        return "Warning: Could not connect to local Odoo database to search records."
        
    user_base_url = "http://localhost:8069"
    results = []
    
    has_prod = check_model_exists(models, uid, 'product.product')
    has_so = check_model_exists(models, uid, 'sale.order')
    has_po = check_model_exists(models, uid, 'purchase.order')
    
    try:
        # 1. Search Products
        if has_prod:
            product_domain = ['|', ('name', 'ilike', keywords[0]), ('default_code', 'ilike', keywords[0])]
            for kw in keywords[1:]:
                product_domain = ['|'] + product_domain + ['|', ('name', 'ilike', kw), ('default_code', 'ilike', kw)]
                
            products = models.execute_kw(DB, uid, PASSWORD, 'product.product', 'search_read', [product_domain], {'fields': ['name', 'default_code', 'lst_price'], 'limit': 5})
            if products:
                results.append("\n**Sản phẩm liên quan tìm thấy trên Odoo:**")
                for prod in products:
                    prod_name = prod.get('name')
                    code = prod.get('default_code')
                    code_str = f" [{code}]" if code else ""
                    price = prod.get('lst_price', 0.0)
                    prod_id = prod.get('id')
                    link = f"{user_base_url}/web#id={prod_id}&model=product.product&view_type=form"
                    results.append(f"- [{prod_name}{code_str}]({link}) - Giá bán: {price:,.2f} VND")
                    
        # 2. Search Sales Orders
        if has_so:
            so_domain = [('name', 'ilike', keywords[0])]
            for kw in keywords[1:]:
                so_domain = ['|'] + so_domain + [('name', 'ilike', kw)]
                
            sos = models.execute_kw(DB, uid, PASSWORD, 'sale.order', 'search_read', [so_domain], {'fields': ['name', 'amount_total', 'partner_id'], 'limit': 5})
            if sos:
                results.append("\n**Đơn bán hàng (SO) liên quan:**")
                for so in sos:
                    so_name = so.get('name')
                    total = so.get('amount_total', 0.0)
                    partner = so.get('partner_id')
                    partner_name = partner[1] if partner else "Không rõ"
                    so_id = so.get('id')
                    link = f"{user_base_url}/web#id={so_id}&model=sale.order&view_type=form"
                    results.append(f"- [Đơn hàng {so_name}]({link}) - Khách hàng: {partner_name} - Tổng tiền: {total:,.2f} VND")
                    
        # 3. Search Purchase Orders
        if has_po:
            po_domain = [('name', 'ilike', keywords[0])]
            for kw in keywords[1:]:
                po_domain = ['|'] + po_domain + [('name', 'ilike', kw)]
                
            pos = models.execute_kw(DB, uid, PASSWORD, 'purchase.order', 'search_read', [po_domain], {'fields': ['name', 'amount_total', 'partner_id'], 'limit': 5})
            if pos:
                results.append("\n**Đơn mua hàng (PO) liên quan:**")
                for po in pos:
                    po_name = po.get('name')
                    total = po.get('amount_total', 0.0)
                    partner = po.get('partner_id')
                    partner_name = partner[1] if partner else "Không rõ"
                    po_id = po.get('id')
                    link = f"{user_base_url}/web#id={po_id}&model=purchase.order&view_type=form"
                    results.append(f"- [Đơn mua {po_name}]({link}) - Nhà cung cấp: {partner_name} - Tổng tiền: {total:,.2f} VND")
                    
        # Display connection notice if models are missing
        missing_notices = []
        if not has_prod:
            missing_notices.append("Sản phẩm (mô-đun product)")
        if not has_so:
            missing_notices.append("Đơn bán hàng (mô-đun sale)")
        if not has_po:
            missing_notices.append("Đơn mua hàng (mô-đun purchase)")
            
        if missing_notices:
            results.append(f"\n*Lưu ý: Hệ thống Odoo local hiện tại đang thiếu các mô-đun: {', '.join(missing_notices)}.*")
            
        if results:
            summary = (
                f"\n--- LIVE ODOO SEARCH RESULTS ---\n"
                + "\n".join(results)
                + f"\n---------------------------------"
            )
            return summary
        else:
            return ""
    except Exception as e:
        return f"Warning: Error searching Odoo database: {e}"
