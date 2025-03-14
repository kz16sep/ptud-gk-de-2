# PTUD-GK-DE-2

## Thông tin cá nhân  
- **Họ và Tên:**  Huỳnh Long Hồ
- **Mã số sinh viên:** 21008411

## Giới thiệu dự án  
Đây là một ứng dụng quản lý công việc được xây dựng bằng Flask, cho phép người dùng theo dõi và quản lý các task với tính năng upload avatar và thông báo task quá hạn.. 

### Tính năng chính  
- User có thể tạo tài khoản, đăng nhập
- User có thể tạo, chỉnh sửa và xóa công việc  
- User có thể upload ảnh đại diện  
- Admin có quyền quản lý công việc của tất cả user  
- Hiển thị số công việc trễ hạn 

## Yêu Cầu Hệ Thống

- Python 3.8 trở lên
- pip (Python package installer)
- Git

## Hướng Dẫn Cài Đặt Chi Tiết

### 1. Chuẩn Bị Môi Trường

1.1 Cài đặt Python:
   - Truy cập [python.org](https://www.python.org/downloads/)
   - Tải và cài đặt Python phiên bản mới nhất
   - Đảm bảo tích chọn "Add Python to PATH" khi cài đặt
1.2 Cài đặt Visual Studio Code:
   -Truy cập code.visualstudio.com
   -Tải và cài đặt VS Code phiên bản mới nhất
   -Cài đặt Python extension bằng cách:
      -Mở VS Code
      -Vào Extensions (Ctrl + Shift + X)
      -Tìm Python và nhấn Install

1.3 Kiểm tra cài đặt:
   ```bash
   python --version
   pip --version
   ```

### 2. Tải Mã Nguồn

1. Tạo thư mục cho project:
   ```bash
   mkdir task-manager
   cd task-manager
   ```

2. Clone repository:
   ```bash
   git clone https://github.com/kz16sep/ptud-gk-de-2.git
   cd ptud-gk-de-2
   ```

### 3. Tạo Môi Trường Ảo

1. Tạo môi trường ảo:
   ```bash
   # Windows
   python -m venv venv
   
   # Linux/Mac
   python3 -m venv venv
   ```

2. Kích hoạt môi trường ảo:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

### 4. Cài Đặt Các Thư Viện

1. Cài đặt các package cần thiết:
   ```bash
   pip install -r requirements.txt
   ```

### 5. Khởi Tạo Database

1. Mở Python shell trong môi trường ảo:
   ```bash
   python
   ```

2. Tạo database:
   ```python
   from app import db
   db.create_all()
   exit()
   ```

### 6. Chạy Ứng Dụng

1. Khởi động server:
   ```bash
   python app.py
   ```

2. Truy cập ứng dụng:
   - Mở trình duyệt web
   - Truy cập địa chỉ: http://localhost:5000

### 7. Sử Dụng Ứng Dụng

1. Đăng ký tài khoản mới:
   - Click vào "Register"
   - Điền thông tin tài khoản
   - Đăng ký

2. Đăng nhập:
   - Nhập username và password
   - Click "Login"

3. Quản lý task:
   - Thêm task mới
   - Upload avatar
   - Theo dõi task quá hạn
   - Cập nhật trạng thái task

### 8. Xử Lý Lỗi Thường Gặp

1. Lỗi "No module named 'flask'":
   ```bash
   pip install flask
   ```

2. Lỗi database:
   - Xóa file `tasks.db`
   - Chạy lại lệnh tạo database

3. Lỗi port 5000 đã được sử dụng:
   - Tắt các ứng dụng đang sử dụng port 5000
   - Hoặc thay đổi port trong `app.py`:
     ```python
     app.run(port=5001)
     ```

### 9. Backup Dữ Liệu

- Database được lưu trong file `tasks.db`
- Avatars được lưu trong thư mục `static/avatars`
- Sao lưu các file này để đảm bảo dữ liệu

### 10. Cập Nhật Ứng Dụng

1. Pull code mới:
   ```bash
   git pull origin main
   ```

2. Cài đặt các package mới (nếu có):
   ```bash
   pip install -r requirements.txt
   ```

