# Hướng dẫn tự học và sử dụng API Odoo XML-RPC

Tài liệu này hướng dẫn bạn cách hiểu và sử dụng cổng kết nối **XML-RPC** của Odoo để phục vụ cho việc tích hợp mô hình AI RAG (Retrieval-Augmented Generation) Agent.

---

## 💡 1. XML-RPC là gì và tại sao Odoo sử dụng nó?

- **XML-RPC** (eXtensible Markup Language Remote Procedure Call) là một giao thức gọi hàm từ xa sử dụng mã hóa XML để truyền tải thông tin và giao thức HTTP để thực hiện yêu cầu.
- Odoo mở sẵn cổng XML-RPC trên cổng chạy web mặc định (`8069`). Điều này có nghĩa là bất kỳ ứng dụng bên ngoài nào (viết bằng Python, Node.js, Java,...) đều có thể kết nối, đăng nhập và thao tác với cơ sở dữ liệu Odoo (đọc, ghi, xóa, cập nhật) mà không cần lập trình viên Odoo phải viết thêm Restful API.

---

## 🛠️ 2. Cách thức Odoo XML-RPC hoạt động

Hệ thống cung cấp hai điểm cuối (endpoints) chính:

1. **`http://localhost:8069/xmlrpc/2/common`**:
   - Dùng cho các tác vụ chung như xác thực người dùng, kiểm tra phiên bản Odoo.
   - Hàm quan trọng nhất: `authenticate(db, username, password, user_agent_env)`. Nếu thông tin đúng, nó sẽ trả về mã số định danh duy nhất của người dùng (`UID`).
   
2. **`http://localhost:8069/xmlrpc/2/object`**:
   - Dùng để thực thi các hành động trên cơ sở dữ liệu (ORM).
   - Hàm quan trọng nhất: `execute_kw(db, uid, password, model_name, method_name, arguments, keyword_arguments)`.
   - Các phương thức phổ biến để truy vấn dữ liệu:
     - `'search'`: Tìm kiếm bản ghi khớp với bộ lọc (domain), trả về danh sách IDs.
     - `'read'`: Đọc chi tiết các trường thông tin dựa trên danh sách IDs.
     - `'search_read'`: Kết hợp cả tìm kiếm và đọc chi tiết trong một câu lệnh đơn lẻ (tối ưu hóa hiệu năng).

---

## 💻 3. Phân tích chi tiết mã nguồn Script `xmlrpc_client.py`

Kịch bản [xmlrpc_client.py](file:///c:/Users/nhan/workplace/hsu/kms/odoo_kms_project/xmlrpc_client.py) được thiết kế theo các bước tiêu chuẩn:

### Bước 1: Khởi tạo kết nối & Xác thực
```python
common = xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/2/common')
uid = common.authenticate('odoo_kms', 'admin', 'admin', {})
```
*Đoạn mã này kết nối tới dịch vụ chung, gửi thông tin đăng nhập và lưu lại `uid` để sử dụng ở các bước sau.*

### Bước 2: Khởi tạo dịch vụ đối tượng và truy vấn bài viết
```python
models = xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/2/object')
fields_to_read = ['name', 'content', 'visibility', 'source_type', 'dimension', 'functional_topic', 'property_4', 'tag_ids', 'breadcrumb_path']
articles = models.execute_kw(
    'odoo_kms', uid, 'admin', 
    'handmade.knowledge.article',  # Tên model bài viết
    'search_read', 
    [[('active', '=', True)]],     # Chỉ lấy bài viết đang hoạt động (không nằm trong thùng rác)
    {'fields': fields_to_read}
)
```
*Hàm `search_read` sẽ tìm kiếm các bài viết có `active = True`, sau đó trả về danh sách các cột/trường được chỉ định trong `fields_to_read`.*

### Bước 3: Giải quyết liên kết nhãn Many2many (`tag_ids`)
Mặc định, trường Many2many như `tag_ids` sẽ trả về danh sách mã số (ví dụ: `[1, 2]`). Để chuyển đổi thành chữ viết đọc được (ví dụ: `[HR, SOP]`), script sẽ thu thập tất cả các ID nhãn đó và gọi lệnh `read` trên bảng thẻ để lấy tên tương ứng:
```python
tags_data = models.execute_kw('odoo_kms', uid, 'admin', 'handmade.knowledge.tag', 'read', [list(all_tag_ids)], {'fields': ['name']})
```

---

## 🚀 4. Hướng dẫn chạy thử nghiệm & Học tập

### Chạy script trên Terminal:
Mở cửa sổ dòng lệnh tại thư mục dự án và chạy:
```bash
python xmlrpc_client.py
```

### Kết quả in ra mong muốn:
Màn hình sẽ hiển thị cấu trúc dữ liệu JSON sạch của các bài viết mà bạn đã nhập bằng tệp Excel ở bước trước:
```json
[
    {
        "title": "HR-001: Quy trình Bàn giao Công việc khi Nghỉ việc",
        "breadcrumb": "Root",
        "html_content": "<h2>Quy trình Bàn giao Công việc</h2>...",
        "metadata": {
            "visibility": "workspace",
            "source": "company",
            "dimension": "methodological",
            "functional_topic": "Human Resources",
            "property_4": "HR-SOP",
            "tags": ["HR", "SOP", "Onboarding"]
        }
    }
]
```

### 🎯 Bài tập tự thực hành để hiểu sâu hơn:
1. **Thay đổi bộ lọc (Domain)**:
   Mở file [xmlrpc_client.py](file:///c:/Users/nhan/workplace/hsu/kms/odoo_kms_project/xmlrpc_client.py), tìm dòng định nghĩa `domain = [('active', '=', True)]` và sửa thành `domain = [('visibility', '=', 'private')]` (chỉ hiển thị các tài liệu cá nhân). Lưu lại và chạy lại script để quan sát sự thay đổi.
2. **Sử dụng để liên kết AI RAG**:
   Đầu ra JSON của script này chính là cấu trúc lý tưởng để nạp vào cơ sở dữ liệu Vector (Vector DB) của mô hình AI RAG. AI sẽ phân tích nội dung bài viết (`html_content`) và dựa vào các thuộc tính metadata (`dimension`, `tags`) để trả lời câu hỏi của người dùng một cách chính xác nhất.
