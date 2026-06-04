# Tài liệu Kiểm thử nhanh API Odoo KMS (cURL & Postman)

Tài liệu này cung cấp các lệnh cURL chạy nhanh từ Terminal và hướng dẫn cấu hình kiểm thử trên Postman cho các API của Odoo 19.

---

## ⚡ PHẦN 1: Kiểm thử bằng cURL (Chạy ngay từ Terminal)

Bạn có thể nhấn nút **Run** (Chạy) ở góc trên bên phải mỗi khối mã dưới đây để chạy trực tiếp:

### 🔑 1. API Xác thực XML-RPC (Authentication)
* **Mục đích**: Nhận về mã số ID người dùng (`UID`) để làm việc với DB.
```bash
curl -X POST -H "Content-Type: text/xml" \
     -d "<?xml version='1.0'?><methodCall><methodName>authenticate</methodName><params><param><value><string>odoo_kms</string></value></param><param><value><string>admin</string></value></param><param><value><string>admin</string></value></param><param><value><struct/></value></param></params></methodCall>" \
     http://localhost:8069/xmlrpc/2/common
```

### 📂 2. API Lấy danh sách bài viết XML-RPC (Search & Read)
* **Mục đích**: Lấy danh sách bài viết kèm quyền riêng tư (`visibility`) đang hoạt động.
* **Lưu ý**: Hãy thay đổi số `2` ở trường `<int>2</int>` thành `UID` bạn nhận được ở Bước 1.
```bash
curl -X POST -H "Content-Type: text/xml" \
     -d "<?xml version='1.0'?><methodCall><methodName>execute_kw</methodName><params><param><value><string>odoo_kms</string></value></param><param><value><int>2</int></value></param><param><value><string>admin</string></value></param><param><value><string>handmade.knowledge.article</string></value></param><param><value><string>search_read</string></value></param><param><value><array><data><value><array><data><value><array><data><value><string>active</string></value><value><string>=</string></value><value><boolean>1</boolean></value></data></array></value></data></array></value></data></array></value></param><param><value><struct><member><name>fields</name><value><array><data><value><string>name</string></value><value><string>visibility</string></value></data></array></value></member></struct></value></param></params></methodCall>" \
     http://localhost:8069/xmlrpc/2/object
```

---

## 📬 PHẦN 2: Hướng dẫn cấu hình kiểm thử bằng Postman (GUI)

Để kiểm thử các API này trên công cụ Postman, hãy tạo các Request mới theo các thông số cấu hình dưới đây:

### 🔑 1. API Xác thực (Common API - Authentication)
* **Method**: `POST`
* **URL**: `http://localhost:8069/xmlrpc/2/common`
* **Headers**: Thêm dòng `Content-Type` là `text/xml`
* **Body**: Chọn tab **Body** -> **raw** -> Chọn định dạng **XML** (hoặc Text) ở cuối dòng, sau đó dán nội dung sau vào:
```xml
<?xml version="1.0"?>
<methodCall>
    <methodName>authenticate</methodName>
    <params>
        <param><value><string>odoo_kms</string></value></param>
        <param><value><string>admin</string></value></param>
        <param><value><string>admin</string></value></param>
        <param><value><struct/></value></param>
    </params>
</methodCall>
```
* **Cách kiểm tra kết quả**: Nhấn **Send**. Bạn sẽ nhận được mã phản hồi dạng XML chứa số ID của user ở phần `<int>...</int>` (Ví dụ: `<value><int>2</int></value>` tức UID = 2).

---

### 📂 2. API Lấy dữ liệu bài viết (Object API - Search Read)
* **Method**: `POST`
* **URL**: `http://localhost:8069/xmlrpc/2/object`
* **Headers**: Thêm dòng `Content-Type` là `text/xml`
* **Body**: Chọn tab **Body** -> **raw** -> chọn định dạng **XML**, sau đó dán nội dung sau vào *(Thay số 2 ở dòng `<value><int>2</int></value>` bằng UID bạn vừa nhận được ở bước trên nếu cần)*:
```xml
<?xml version="1.0"?>
<methodCall>
    <methodName>execute_kw</methodName>
    <params>
        <param><value><string>odoo_kms</string></value></param>
        <param><value><int>2</int></value></param>
        <param><value><string>admin</string></value></param>
        <param><value><string>handmade.knowledge.article</string></value></param>
        <param><value><string>search_read</string></value></param>
        <param>
            <value>
                <array>
                    <data>
                        <value>
                            <array>
                                <data>
                                    <value>
                                        <array>
                                            <data>
                                                <value><string>active</string></value>
                                                <value><string>=</string></value>
                                                <value><boolean>1</boolean></value>
                                            </data>
                                        </array>
                                    </value>
                                </data>
                            </array>
                        </value>
                    </data>
                </array>
            </value>
        </param>
        <param>
            <value>
                <struct>
                    <member>
                        <name>fields</name>
                        <value>
                            <array>
                                <data>
                                    <value><string>name</string></value>
                                    <value><string>visibility</string></value>
                                    <value><string>dimension</string></value>
                                </data>
                            </array>
                        </value>
                    </member>
                </struct>
            </value>
        </param>
    </params>
</methodCall>
```
* **Cách kiểm tra kết quả**: Nhấn **Send**. Bạn sẽ nhận về một chuỗi XML chứa thông tin danh sách các bài viết (gồm tiêu đề, visibility và dimension) lấy trực tiếp từ database.
