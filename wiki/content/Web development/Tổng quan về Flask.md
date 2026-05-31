---
tags:
  - web
date: 2026-05-29
---
# Tổng quan về Flask

Flask là một micro web framework cho Python, tập trung vào sự nhỏ gọn, linh hoạt và khả năng mở rộng. Khác với các framework lớn như Django hay Tornado, Flask không áp đặt cấu trúc hay thư viện tiêu chuẩn khắt khe, đổi lại lập trình viên phải tự quyết định nhiều giải pháp hơn.

## Nhỏ gọn và khả năng mở rộng

Các tính năng cốt lõi của Flask gồm URL routing, template engine, các high level class, testing module và command-line tool. Để deploy một model machine learning thì nhiêu đó là đủ. Khi ứng dụng phức tạp hơn, Flask mở rộng qua các extension tách biệt do cộng đồng phát triển: tương tác cơ sở dữ liệu với `Flask-SQLAlchemy`, quản trị dữ liệu với `Flask-Admin`, xác thực và phân quyền với `Flask-Login`, phát triển RESTful API với `Flask-Connexion`.

## Định tuyến bằng decorator

Nhờ tận dụng decorator của Python, việc định tuyến trong Flask rất trực quan: định nghĩa một hàm và đặt `@app.route()` lên trước để kết nối URL với hàm xử lý.

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def homepage():
    return 'Hello world'
```

Cơ chế này cũng tạo tiền đề cho các extension bổ sung decorator tùy chỉnh (như Flask-Login, Flask-Cache) để can thiệp vào tiến trình xử lý của bất kỳ router nào.

## Tương thích WSGI

Flask được cài đặt dựa trên tiêu chuẩn WSGI nên chạy được dễ dàng trên nhiều web server như Gunicorn, uWSGI, Hypercorn, hay Apache qua module `mod_wsgi`. Bản thân Flask được xây dựng trên thư viện Werkzeug (cung cấp lớp WSGI và các tiện ích HTTP) và Jinja (template engine).

## Cơ chế context

Flask dùng cơ chế context để giải quyết vấn đề truyền tải thông tin request xuyên suốt luồng xử lý mà không phải truyền biến `request` qua nhiều tầng gọi hàm. Flask cung cấp proxy như `flask.request` tự động trỏ đến đúng đối tượng request của worker đang xử lý. Ngoài request context còn có application context truy cập qua `flask.g` và `flask.current_app`. Chi tiết cài đặt của cơ chế này nằm trong tri thức riêng về context của Flask.

## Testing tích hợp

Flask cung cấp `TestClient` (lấy qua `app.test_client()`) hoạt động như một client thực sự, cho phép mô phỏng request gửi tới ứng dụng và kiểm thử trực tiếp các hàm router ngay trong mã nguồn, kể cả khi chúng đang được bọc bởi nhiều decorator.

```python
client = app.test_client()
response = client.get('/say/Thanh')
assert response.data == b'Hello, Thanh'
```

## Nguồn tham khảo

- [Flask có gì hay!](https://www.nkthanh.dev/posts/flask-co-gi-hay)
- [Flask Documentation](https://flask.palletsprojects.com)

## Liên kết tri thức

- [Decorator trong Python - đặc điểm ngôn ngữ được Flask dùng làm cơ chế định tuyến](../System%20level/Decorator%20trong%20Python.md)
- [Context trong Flask - cài đặt chi tiết của cơ chế context và proxy](./Context%20trong%20Flask.md)
- [WSGI và ASGI - Flask là framework đồng bộ tuân thủ chuẩn WSGI](./WSGI%20v%C3%A0%20ASGI.md)
- [Vì sao FastAPI nhanh - FastAPI được xem là người kế nhiệm Flask trên chuẩn ASGI](./V%C3%AC%20sao%20FastAPI%20nhanh.md)
