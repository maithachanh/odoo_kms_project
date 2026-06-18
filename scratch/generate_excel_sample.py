import pandas as pd

# Define structured KMS articles with parent-child relationships, dimensions, and tags
data = [
    {
        "id": "kms_knowledge.art_root_hr",
        "name": "Sổ tay nhân sự KMS (HR Handbook)",
        "body_html": "<h2>Sổ tay Nhân sự KMS</h2><p>Chào mừng bạn đến với KMS. Đây là tài liệu hướng dẫn các quy chế và chính sách làm việc chung dành cho mọi nhân viên công ty.</p>",
        "parent_id/id": "",
        "workspace_dimension": "hr",
        "tag_ids/name": "HR, Policy, Handbook"
    },
    {
        "id": "kms_knowledge.art_child_onboarding",
        "name": "Quy trình Thử việc & Onboard cho nhân viên mới",
        "body_html": "<h2>Quy trình Thử việc & Onboard</h2><p>Tất cả nhân viên mới sẽ trải qua thời gian thử việc 2 tháng. Trong tuần đầu tiên, nhân sự sẽ hướng dẫn cài đặt tài khoản và giới thiệu các phòng ban.</p>",
        "parent_id/id": "kms_knowledge.art_root_hr",
        "workspace_dimension": "hr",
        "tag_ids/name": "HR, SOP, Onboarding"
    },
    {
        "id": "kms_knowledge.art_child_resignation",
        "name": "Quy trình bàn giao công việc khi nghỉ việc",
        "body_html": "<h2>Quy trình Bàn giao công việc</h2><p>Nhân viên xin thôi việc cần thông báo trước 30 ngày (với hợp đồng xác định thời hạn) hoặc 45 ngày (hợp đồng không xác định thời hạn) và thực hiện bàn giao đầy đủ thiết bị.</p>",
        "parent_id/id": "kms_knowledge.art_root_hr",
        "workspace_dimension": "hr",
        "tag_ids/name": "HR, SOP, Offboarding"
    },
    {
        "id": "kms_knowledge.art_root_it",
        "name": "Tài liệu kỹ thuật IT & Bảo mật mạng",
        "body_html": "<h2>Tài liệu Kỹ thuật IT</h2><p>Tài liệu này chứa các hướng dẫn thiết lập hạ tầng, bảo mật hệ thống và quy định sử dụng tài nguyên công nghệ thông tin.</p>",
        "parent_id/id": "",
        "workspace_dimension": "it",
        "tag_ids/name": "IT, Guide, Security"
    },
    {
        "id": "kms_knowledge.art_child_dev_env",
        "name": "Hướng dẫn Cài đặt Môi trường làm việc cho Dev",
        "body_html": "<h2>Hướng dẫn cài đặt môi trường</h2><p>Tài liệu hướng dẫn cấu hình máy tính cá nhân cho lập trình viên mới. Cần cài đặt Git, Docker Desktop và IDE (VS Code/PyCharm) tương ứng.</p>",
        "parent_id/id": "kms_knowledge.art_root_it",
        "workspace_dimension": "it",
        "tag_ids/name": "IT, SOP, Technical"
    },
    {
        "id": "kms_knowledge.art_child_network_sec",
        "name": "Quy trình Cách ly Cổng mạng khi có Sự cố",
        "body_html": "<h2>Quy trình cách ly cổng mạng</h2><p>Khi phát hiện dấu hiệu tấn công mạng hoặc mã độc xâm nhập, kỹ thuật viên IT phải lập tức cô lập phân vùng bị ảnh hưởng và ngắt kết nối switch tương ứng.</p>",
        "parent_id/id": "kms_knowledge.art_root_it",
        "workspace_dimension": "it",
        "tag_ids/name": "IT, SOP, Security"
    }
]

df = pd.DataFrame(data)
df.to_excel("kms_import_sample.xlsx", index=False)
print("SUCCESS: kms_import_sample.xlsx created.")
