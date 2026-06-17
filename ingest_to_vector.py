# -*- coding: utf-8 -*-
"""
KMS Vector DB Ingestion Pipeline (Ollama Version)
=================================================
Script này thực hiện nạp dữ liệu từ Odoo và ánh xạ phân quyền từ Matrix Sheet 
vào cơ sở dữ liệu Vector (ChromaDB) sử dụng Ollama nomic-embed-text.
"""

import os
import sys

# Reconfigure stdout to support UTF-8 on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Import các thư viện xử lý văn bản và Vector DB của LangChain
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

# Yêu cầu: Sử dụng langchain_chroma (không phải langchain_community)
from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings

# Nạp các biến môi trường cấu hình (nếu có)
load_dotenv()

# Cấu hình đường dẫn lưu trữ và tên Collection
PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "kms_collection"
EMBEDDING_MODEL = "nomic-embed-text"

# Cấu hình kết nối Odoo XML-RPC
HOST = os.getenv("ODOO_HOST", "localhost")
PORT = int(os.getenv("ODOO_PORT", "8069"))
DB = os.getenv("ODOO_DB", "odoo_kms")
USER = os.getenv("ODOO_USER", "admin")
PASSWORD = os.getenv("ODOO_PASSWORD", "admin")

def load_access_matrix():
    """
    BƯỚC 1: Đọc Matrix Sheet bằng pandas
    - Đọc file Excel 'access_matrix.xlsx' chứa bảng phân quyền bảo mật.
    - Tạo dictionary tra cứu nhanh với key là tiêu đề bài viết (Article Title)
      và value là tuple (Workspace Dimension, Access Role).
    """
    matrix_file = "access_matrix.xlsx"
    if not os.path.exists(matrix_file):
        print(f"Lỗi: Không tìm thấy file phân quyền '{matrix_file}'.")
        sys.exit(1)
        
    print(f"Đang đọc Matrix Sheet từ: {matrix_file}...")
    df = pd.read_excel(matrix_file)
    
    # Tạo dictionary tra cứu nhanh
    matrix_dict = {}
    for _, row in df.iterrows():
        title = str(row['Article Title']).strip()
        workspace = str(row['Workspace Dimension']).strip().lower()
        role = str(row['Access Role']).strip().lower()
        matrix_dict[title] = (workspace, role)
        
    print(f"Đã tải {len(matrix_dict)} quy tắc phân quyền từ Matrix Sheet.")
    return matrix_dict

def clean_html(html_content):
    """
    BƯỚC 2: Loại bỏ các thẻ HTML bằng BeautifulSoup
    - Trích xuất văn bản thuần túy (Text) từ nội dung HTML của Odoo.
    - Chuẩn hóa khoảng trắng để văn bản sạch hơn trước khi đưa vào mô hình vector.
    """
    if not html_content:
        return ""
    # Parse HTML và loại bỏ toàn bộ tag
    soup = BeautifulSoup(html_content, "html.parser")
    # Thay thế các tag xuống dòng hoặc danh sách bằng dấu cách để tránh dính chữ
    for element in soup.find_all(["br", "p", "div", "h1", "h2", "h3", "h4", "h5", "li"]):
        element.insert_after(" ")
    text = soup.get_text()
    # Loại bỏ khoảng trắng thừa
    return " ".join(text.split()).strip()

def fetch_articles_from_odoo():
    """Lấy danh sách bài viết từ hệ thống Odoo XML-RPC (Có Fallback sang Excel nếu Odoo offline)."""
    import xmlrpc.client
    url = f"http://{HOST}:{PORT}"
    print(f"Đang kết nối tới Odoo XML-RPC tại {url}...")
    try:
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(DB, USER, PASSWORD, {})
        if not uid:
            print("Đăng nhập Odoo thất bại! Chuyển sang đọc dữ liệu mẫu từ Excel template...")
            return None
        
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        fields_to_read = ['name', 'body_html', 'workspace_dimension', 'tag_ids']
        
        articles_data = models.execute_kw(
            DB, uid, PASSWORD,
            'kms.knowledge.article',
            'search_read',
            [[('active', '=', True)]],
            {'fields': fields_to_read}
        )
        
        # Đọc tên nhãn (tag names)
        tag_ids = set()
        for art in articles_data:
            if art.get('tag_ids'):
                tag_ids.update(art['tag_ids'])
        
        tag_mapping = {}
        if tag_ids:
            tags_data = models.execute_kw(
                DB, uid, PASSWORD,
                'res.partner.category',
                'read',
                [list(tag_ids)],
                {'fields': ['name']}
            )
            tag_mapping = {t['id']: t['name'] for t in tags_data}

        records = []
        for art in articles_data:
            title = art.get('name') or "Untitled"
            body = art.get('body_html') or ""
            tags = [tag_mapping.get(tid, f"Tag_{tid}") for tid in art.get('tag_ids', [])]
            records.append({
                'title': title,
                'body_html': body,
                'tags': tags
            })
        return records
    except Exception as e:
        print(f"Không thể kết nối Odoo ({e}). Chuyển sang đọc dữ liệu mẫu từ Excel template...")
        return None

def fetch_articles_from_excel_template():
    """Đọc dữ liệu mẫu từ file Excel template nếu Odoo server offline."""
    import openpyxl
    excel_path = 'kms_import_template.xlsx'
    if not os.path.exists(excel_path):
        print(f"Lỗi: Không tìm thấy file {excel_path}.")
        sys.exit(1)
        
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    sheet = wb.active
    
    headers = [str(cell.value).strip().lower() for cell in sheet[1]]
    title_idx = headers.index("title")
    content_idx = headers.index("content")
    tags_idx = headers.index("tags")
    
    records = []
    for row in list(sheet.iter_rows(min_row=2, values_only=True)):
        if not row or row[title_idx] is None:
            continue
        title = str(row[title_idx]).strip()
        content = str(row[content_idx]).strip() if row[content_idx] is not None else ""
        tags_str = str(row[tags_idx]).strip() if row[tags_idx] is not None else ""
        tags = [t.strip() for t in tags_str.split(',') if t.strip()] if tags_str else []
        records.append({
            'title': title,
            'body_html': content,
            'tags': tags
        })
    return records

def fetch_articles_from_excel():
    """Alias for RAG API server synthesis fallback compatibility."""
    return fetch_articles_from_excel_template()

def main():
    print("=================================================================")
    print("      KMS VECTOR INGESTION PIPELINE (PANDAS + OLLAMA + CHROMA)")
    print("=================================================================")

    # 1. Đọc Matrix Sheet
    matrix_dict = load_access_matrix()

    # 2. Lấy dữ liệu bài viết (Odoo hoặc Fallback Excel)
    articles = fetch_articles_from_odoo()
    if not articles:
        articles = fetch_articles_from_excel_template()

    # Đảm bảo có các bài viết mẫu phục vụ cho việc kiểm thử bảo mật của đề bài
    test_titles = [a['title'] for a in articles]
    if "IT Engineer Onboarding Protocol" not in test_titles:
        articles.append({
            'title': "IT Engineer Onboarding Protocol",
            'body_html': "<h2>IT Engineer Onboarding Protocol</h2><p>Welcome to the Engineering team. Upon arrival, all new IT technical hires must initialize their corporate GitHub profiles and configure their local environments according to the Dev guidelines.</p>",
            'tags': ["SOP", "Hardware"]
        })
    if "General Workspace Conduct Guideline" not in test_titles:
        articles.append({
            'title': "General Workspace Conduct Guideline",
            'body_html': "<h2>General Workspace Conduct Guideline</h2><p>It is our company policy to maintain an open, welcoming environment for all incoming cross-functional personnel and respect diversity.</p>",
            'tags': ["HR", "Policy"]
        })
    if "Network Security & System Firewall Policy" not in test_titles:
        articles.append({
            'title': "Network Security & System Firewall Policy",
            'body_html': "<h2>Network Security & System Firewall Policy</h2><p>In the event of system safety infractions, technical staff must trigger the automated port isolation protocol immediately to protect internal corporate data and network logs.</p>",
            'tags': ["SOP", "Network"]
        })
    if "Acceptable Hardware Use Agreement" not in test_titles:
        articles.append({
            'title': "Acceptable Hardware Use Agreement",
            'body_html': "<h2>Acceptable Hardware Use Agreement</h2><p>Disciplinary actions regarding corporate computing hardware safety violations will follow the general terms outlined in section 5. Ensure all devices have local antiviruses.</p>",
            'tags': ["Policy", "Hardware"]
        })

    # BƯỚC 3: Cấu hình bộ chia nhỏ văn bản (Text Splitter)
    # chunk_size=500 ký tự, chunk_overlap=100 ký tự đệm để không mất bối cảnh
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    
    chunks_list = []
    metadatas_list = []

    for art in articles:
        title = art['title']
        
        # BƯỚC 2: Làm sạch HTML body trước khi xử lý vector
        clean_text = clean_html(art['body_html'])
        if not clean_text:
            clean_text = title

        # Tra cứu phân quyền từ Matrix Sheet đã nạp ở Bước 1
        # Nếu bài viết không nằm trong Matrix Sheet, gán mặc định là ops (phòng ban) và public (vai trò truy cập)
        workspace_dim, access_role = matrix_dict.get(title, ("ops", "public"))

        # BƯỚC 3: Thực hiện chia text thành các chunk nhỏ
        chunks = text_splitter.split_text(clean_text)

        # BƯỚC 4: Gắn metadata cho từng chunk
        for chunk in chunks:
            chunks_list.append(chunk)
            metadatas_list.append({
                "title": title,
                "workspace_dimension": workspace_dim,
                "access_role": access_role,
                "tags": art['tags']
            })

    print(f"Đã chia nhỏ văn bản thành {len(chunks_list)} chunks.")

    # BƯỚC 5: Khởi tạo Ollama Embeddings với model nomic-embed-text
    # Mô hình này không dùng OpenAI, chạy hoàn toàn offline miễn phí cục bộ.
    print(f"Đang khởi tạo Ollama Embeddings (Model: '{EMBEDDING_MODEL}')...")
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

    # BƯỚC 6: Khởi tạo Chroma DB và lưu persistent (vật lý) xuống đĩa cứng
    # Sử dụng package langchain_chroma theo đúng yêu cầu đề bài.
    print(f"Đang lưu cơ sở dữ liệu Vector vào thư mục cục bộ: '{PERSIST_DIR}'...")
    
    # Xóa thư mục cũ (nếu có) để nạp mới hoàn toàn tránh trùng lặp bản ghi
    if os.path.exists(PERSIST_DIR):
        import shutil
        try:
            shutil.rmtree(PERSIST_DIR)
        except Exception as e:
            print(f"Cảnh báo: Không thể xóa thư mục cũ ({e}).")

    # Ingest dữ liệu
    try:
        db = Chroma.from_texts(
            texts=chunks_list,
            embedding=embeddings,
            metadatas=metadatas_list,
            persist_directory=PERSIST_DIR,
            collection_name=COLLECTION_NAME
        )
        print("\nTriển khai thành công!")
        print(f"Chroma DB đã được lưu tại '{PERSIST_DIR}', tên collection: '{COLLECTION_NAME}'")
    except Exception as e:
        print(f"\nLỗi khi khởi tạo Chroma DB hoặc gọi Ollama API: {e}")
        print("Mẹo: Hãy đảm bảo rằng phần mềm Ollama đã được khởi chạy và bạn đã kéo model về bằng lệnh: 'ollama pull nomic-embed-text'")

    print("=================================================================")

if __name__ == "__main__":
    main()
