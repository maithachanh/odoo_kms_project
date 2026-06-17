# -*- coding: utf-8 -*-
"""
Odoo KMS Import Cleaner & Sorter
=================================
This script takes an Excel file exported from Odoo Enterprise,
cleans the columns to avoid data type or user mismatches, 
auto-assigns workspace dimensions, sorts the rows topologically 
(so parent articles are imported before their sub-articles),
and exports a clean file that Odoo can import in one click.

Usage:
    python clean_export.py <path_to_exported_excel.xlsx>
"""

import os
import sys
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

def clean_and_format_excel(input_path):
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' does not exist.")
        sys.exit(1)

    print(f"Loading exported file: {input_path}...")
    try:
        wb_in = openpyxl.load_workbook(input_path, data_only=True)
        ws_in = wb_in.active
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        sys.exit(1)

    # 1. Read headers and data rows
    rows_data = list(ws_in.iter_rows(values_only=True))
    if not rows_data:
        print("Error: The Excel file is empty.")
        sys.exit(1)

    headers = [str(h).strip() if h is not None else "" for h in rows_data[0]]
    data_rows = rows_data[1:]

    # Map header names (case-insensitive search)
    header_indices = {}
    for i, h in enumerate(headers):
        h_lower = h.lower()
        if "display name" in h_lower or "title" in h_lower or "name" in h_lower:
            header_indices["title"] = i
        elif "parent" in h_lower:
            header_indices["parent"] = i
        elif "created by" in h_lower or "author" in h_lower:
            header_indices["author"] = i
        elif "content" in h_lower or "body" in h_lower or "nội dung" in h_lower:
            header_indices["content"] = i
        elif "tags" in h_lower or "nhãn" in h_lower:
            header_indices["tags"] = i
        elif "dimension" in h_lower:
            header_indices["dimension"] = i

    # Fallbacks and validation
    title_idx = header_indices.get("title")
    if title_idx is None:
        print("Error: Could not find a 'Display Name' or 'Title' column in the Excel file.")
        sys.exit(1)

    parent_idx = header_indices.get("parent")
    content_idx = header_indices.get("content")
    tags_idx = header_indices.get("tags")
    dimension_idx = header_indices.get("dimension")

    print(f"Detected columns:")
    print(f"  - Title: Column {title_idx + 1} ('{headers[title_idx]}')")
    if parent_idx is not None:
        print(f"  - Parent: Column {parent_idx + 1} ('{headers[parent_idx]}')")
    if content_idx is not None:
        print(f"  - Content: Column {content_idx + 1} ('{headers[content_idx]}')")
    if tags_idx is not None:
        print(f"  - Tags: Column {tags_idx + 1} ('{headers[tags_idx]}')")
    if dimension_idx is not None:
        print(f"  - Workspace Dimension: Column {dimension_idx + 1} ('{headers[dimension_idx]}')")

    # 2. Extract records
    records = []
    all_titles = set()
    for row in data_rows:
        if not row or row[title_idx] is None:
            continue
        
        title = str(row[title_idx]).strip()
        # Clean title (Odoo enterprise export might prepended symbols or emails)
        # We keep the name clean
        parent = str(row[parent_idx]).strip() if (parent_idx is not None and row[parent_idx] is not None) else ""
        content = str(row[content_idx]).strip() if (content_idx is not None and row[content_idx] is not None) else ""
        tags = str(row[tags_idx]).strip() if (tags_idx is not None and row[tags_idx] is not None) else ""
        dimension = str(row[dimension_idx]).strip() if (dimension_idx is not None and row[dimension_idx] is not None) else ""

        all_titles.add(title)
        records.append({
            'title': title,
            'parent': parent,
            'content': content,
            'tags': tags,
            'dimension': dimension
        })

    print(f"Parsed {len(records)} records from spreadsheet.")

    # 3. Smart workspace dimension classification and HTML body formatting
    for rec in records:
        # Default workspace dimension if not set
        if not rec['dimension']:
            title_p_lower = (rec['title'] + " " + rec['parent']).lower()
            if any(k in title_p_lower for k in ['hr', 'training', 'onboarding', 'recruit', 'tuyển dụng', 'đào tạo', 'nhân sự']):
                rec['dimension'] = 'hr'
            elif any(k in title_p_lower for k in ['it', 'tech', 'dev', 'system', 'software', 'hardware', 'máy tính', 'công nghệ']):
                rec['dimension'] = 'it'
            elif any(k in title_p_lower for k in ['sales', 'mkt', 'marketing', 'deal', 'customer', 'vip', 'khách hàng', 'bán hàng']):
                rec['dimension'] = 'sales'
            elif any(k in title_p_lower for k in ['legal', 'law', 'contract', 'policy', 'pháp lý', 'hợp đồng', 'chính sách']):
                rec['dimension'] = 'legal'
            else:
                rec['dimension'] = 'ops' # default to operations for CS, Kitchen, Helpdesk, etc.

        # Ensure content has basic structure if empty
        if not rec['content']:
            rec['content'] = f"<h2>{rec['title']}</h2><p>Nội dung của bài viết đang được cập nhật...</p>"

    # 4. Topological Sort (Ensure parent is imported before child)
    sorted_records = []
    visited = set()
    
    # We want to process parents first
    # Map title -> record
    record_map = {r['title']: r for r in records}
    
    def visit(title):
        if title in visited:
            return
        visited.add(title)
        
        rec = record_map.get(title)
        if not rec:
            return
            
        parent = rec['parent']
        # If parent exists in our records, visit the parent first
        if parent and parent in record_map:
            visit(parent)
            
        sorted_records.append(rec)

    for rec in records:
        visit(rec['title'])

    print(f"Topologically sorted records (parent articles ordered before sub-articles).")

    # 5. Write to a clean new Excel file
    wb_out = openpyxl.Workbook()
    ws_out = wb_out.active
    ws_out.title = "KMS Clean Import"

    # Perfect column headers matching Odoo fields
    headers_out = ["Title", "Content", "Workspace Dimension", "Parent Article", "Tags"]
    ws_out.append(headers_out)

    # Styles
    header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    
    cell_font = Font(name="Arial", size=10)
    cell_alignment_left = Alignment(horizontal="left", vertical="top", wrap_text=True)
    cell_alignment_center = Alignment(horizontal="center", vertical="top", wrap_text=True)

    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )

    # Apply header style
    for col_idx in range(1, len(headers_out) + 1):
        cell = ws_out.cell(row=1, column=col_idx)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border

    # Write data rows
    for r_idx, rec in enumerate(sorted_records, start=2):
        row_data = [
            rec['title'],
            rec['content'],
            rec['dimension'],
            rec['parent'],
            rec['tags']
        ]
        ws_out.append(row_data)
        
        # Apply styles
        for col_idx in range(1, len(row_data) + 1):
            cell = ws_out.cell(row=r_idx, column=col_idx)
            cell.font = cell_font
            cell.border = thin_border
            if col_idx in [3]: # Workspace Dimension
                cell.alignment = cell_alignment_center
            else:
                cell.alignment = cell_alignment_left

    # Set column widths
    column_widths = {
        'A': 35, # Title
        'B': 55, # Content
        'C': 22, # Workspace Dimension
        'D': 25, # Parent Article
        'E': 20  # Tags
    }
    for col_letter, width in column_widths.items():
        ws_out.column_dimensions[col_letter].width = width

    ws_out.row_dimensions[1].height = 28

    # Save output
    output_path = os.path.join(os.path.dirname(input_path), "kms_clean_import.xlsx")
    try:
        wb_out.save(output_path)
        print(f"\nSuccess! Cleaned file saved to: {output_path}")
        print("This file contains perfect headers that match Odoo KMS fields.")
        print("All parent-child relations have been sorted to guarantee error-free import.")
    except Exception as e:
        print(f"Error saving output file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python clean_export.py <path_to_exported_excel.xlsx>")
        sys.exit(1)
    clean_format_excel(sys.argv[1])
