<<<<<<< HEAD
# Medical-Perceptions
=======
# ReViCARE - Hệ thống Quản lý Nhà thuốc Thông minh

ReViCARE là một hệ thống quản lý nhà thuốc toàn diện được xây dựng bằng Django, tích hợp các tính năng hiện đại như chẩn đoán bệnh thông minh, quản lý thuốc, bán hàng và trợ lý ảo.

## Tính năng chính

- **Chẩn đoán bệnh**: Sử dụng AI để chẩn đoán bệnh dựa trên triệu chứng
- **Quản lý thuốc**: Theo dõi kho thuốc, hạn sử dụng, và thông tin chi tiết
- **Bán hàng**: Hệ thống POS đơn giản và hiệu quả
- **Quản lý tài chính**: Theo dõi doanh thu, chi phí và báo cáo
- **Trợ lý ảo**: Chatbot hỗ trợ khách hàng 24/7

## Yêu cầu hệ thống

- Python 3.8+
- PostgreSQL (tùy chọn, mặc định sử dụng SQLite)
- Các thư viện Python được liệt kê trong `requirements.txt`

## Cài đặt

1. Clone repository:
```bash
git clone https://github.com/your-username/revicare.git
cd revicare
```

2. Tạo và kích hoạt môi trường ảo:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

4. Tạo file .env trong thư mục gốc và cấu hình các biến môi trường:
```
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

5. Thực hiện migrate database:
```bash
python manage.py migrate
```

6. Tạo tài khoản admin:
```bash
python manage.py createsuperuser
```

7. Chạy development server:
```bash
python manage.py runserver
```

## Cấu trúc project

```
revicare/
├── accounts/          # Quản lý người dùng
├── diagnosis/         # Chẩn đoán bệnh
├── pharmacy/          # Quản lý thuốc
├── finance/          # Quản lý tài chính
├── pos/              # Hệ thống bán hàng
├── chatbot/          # Trợ lý ảo
├── static/           # File tĩnh (CSS, JS, images)
├── templates/        # Template HTML
├── media/           # File người dùng tải lên
└── revicare/        # Cấu hình project
```

## Đóng góp

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit thay đổi (`git commit -m 'Add some AmazingFeature'`)
4. Push lên branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## Giấy phép

Dự án này được phân phối dưới giấy phép MIT. Xem `LICENSE` để biết thêm thông tin.

## Liên hệ

Your Name - email@example.com

Project Link: [https://github.com/your-username/revicare](https://github.com/your-username/revicare) 
>>>>>>> a1a1119 (Khởi tạo dự án và thêm .gitignore)
