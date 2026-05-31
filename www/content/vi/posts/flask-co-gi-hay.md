---
title: "Flask có gì hay!"
date: "2021-03-17T08:34:48+07:00"
tags:
  - python
  - web
  - flask
categories:
  - Python
  - Web development
description: "Python là một ngôn ngữ rất đẹp, một đứa trẻ cũng có thể làm quen với lập trình bằng Python. Và chẳng có gì lạ khi có những lớp học lập trình cho trẻ con được mở ra và ngôn ngữ mà họ chọn lại là Python."
---


Cú pháp của Python rất sáng sủa và dễ học, chính vì thế có rất nhiều thư viện ở nhiều lĩnh vực được cài đặt bằng Python, hoặc ít nhất cũng có interface là Python như:

- Tensorflow, PyTorch, Theano cho machine learning
- Numpy, SciPy cho tính toán khoa học
- Spark, Pandas cho việc xử lí dữ liệu
- Docker cho containerize
- Django, Flask, FastAPI, Tornado cho phát triển web

Trong bài viết này, mình muốn tập trung vào những thứ hay ho của một web framework - Flask, một framework được cài đặt thuần bằng Python và có được sự hưởng ứng của nhiều người.

### 1. Đơn giản và khả năng mở rộng

Thật sự, Flask là một framework web cực kì nhỏ gọn (như tác giả nói rằng Flask là một micro web framework) so với những đàn anh của nó như Django hay Tornado. Vậy Flask có những gì

- URL routing
- Template engine
- Các high level class
- Testing module
- Commandline tool

Flask không bắt bạn phải làm theo những gì được coi là tiêu chuẩn của nó (tất nhiên vẫn cần có những pattern riêng cho việc này nhưng nó không quá phức tạp) như các framework khác, đặc biệt là Django trong Python.

Nếu bạn cần deploy một model machine learning, nhiêu đó là quá đủ.

Ứng dụng của bạn phức tạp hơn? Flask có 1 giải pháp - extension

Flask có thể được cộng đồng mở rộng bằng cách phát triển các module tách biệt cho nó, cực kì linh hoạt.

Bạn cần tương tác với database, Flask-SQLAlchemy giúp bạn điều này.

Bạn muốn có một hệ thống quản lí dữ liệu như Django, Flask-Admin có thể là lựa chọn hay đấy.

Bạn cần các chức năng authenticate và authorization cho các request, Flask-Login giúp bạn điều đó.

Bạn cần phát triển các RestfulAPI nhanh chóng và thuận tiện, Flask-Connexion sẽ giúp bạn.

Bạn có thể build bất kì một hệ thống web backend nào dựa trên Flask, tất nhiên sự đơn giản của framework cũng đồng nghĩa với việc bạn phải động não nhiều hơn.

### 2. Cấu trúc đơn giả và hiệu quả

Bạn muốn có một backend, đây là những thứ bạn cần với Flask

```python
# main.py

from flask import Flask

app = Flask(__name__)

@app.route('/')
def homepage():
	return 'Hello world'
```

và bạn có thể chạy nó

```sh
$ FLASK_APP=main:app flask run
* Serving Flask app "main:app"
* Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
* Debug mode: off
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

Sự đơn giản mà Flask có được cũng nhờ cú pháp đơn giản của Python. Để định nghĩa một router, bạn đơn giản viết một hàm và wrap nó bằng decorator trong Python.

Decorator là một design pattern hiệu quả, bạn có thể xem thêm nó [ở đây](https://en.wikipedia.org/wiki/Decorator_pattern)

Bằng cách này, các lập trình viên có thể thoả sức viết thêm các modifier cho các router như Flask-Login, Flask-Cache.

Đơn giản là các library đó sẽ viết thêm các decorator để người dùng có thể sử dụng cho bất kì router nào họ muốn, thật quá đơn giản.

### 3. Flask tương thích với đa số các Python web server

Flask được implement dựa trên [WSGI](https://wsgi.readthedocs.io/en/latest/what.html) nên nó có thể chạy dễ dàng trên các web server như gunicorn, uvicorn hay hypercorn. Thậm chí, từ xa xưa, Apache cũng có một module cho wsgi là `mod_wsgi`.

### 4. Context

Một điều thú vị nữa mà Flask đem lại có lẽ là khái niệm về `context`.

Nếu bạn nào từng làm Django hẳn sẽ gặp những trường hợp như bạn phải pass cái biến `request` qua 3, 4 hàm lồng nhau, trên thực tế nó không chỉ đem lại một cấu trúc code rối rắm mà còn làm mất tính đồng nhất khó kiểm soát.

Flask đi sau và tất nhiên nó có giải pháp khắc phục chuyện này - `context`.

Như bạn biết, khi có 2 request (2 `context` khác nhau) gửi đến app của bạn, app của bạn cơ bản là fork ra 2 thread khác nhau để xử lí 2 request đó.

Flask có một proxy có thể phân biệt request của từng thread là `flask.request`.

Khi bạn gọi `flask.request`, Flask app sẽ tìm đúng request mà bạn sở hữu và trả về một `Request` object, object này mang toàn bộ thông tin request của client gửi đến server.

```python
@app.route('/books')
def create_book():
	print(id(flask.request))
	...
```

Khi có 2 request đến đồng thời, `flask.request` sẽ có trỏ đến 2 `Request` object khác nhau tuỳ vào việc nó được gọi trong thread nào. Vâng, nó thật là kì diệu.

Chi tiết cụ thể tại sao Flask có thể làm được việc này mình sẽ nói trong bài viết sau, khi nói về thread local.

Bạn cũng có thể thấy khái niệm `context` này được sử dụng trong [ReactJS](https://reactjs.org/docs/context.html) để giải quyết vấn đề tương tự.

Ngoài [request context](https://flask.palletsprojects.com/en/1.1.x/reqcontext/), flask còn có [application context](https://flask.palletsprojects.com/en/1.1.x/appcontext/), các bạn có thể tham khảo tài liệu của Flask để biết thêm cách dùng của nó.

### 5. Testing

Testing luôn là một vấn đề khó khăn đối với đa số các bạn, trong đó có cả mình 😆. Điều đó càng trở nên kinh dị nếu như framework mà bạn chọn không hỗ trợ tốt unit testing. Thật may mắn, Flask làm việc này cực kì tốt (so với đa số các web framework trong Python 😀).

Khi bạn viết một app trong Flask, về cơ bản là bạn tạo ra một `Flask` object với hàng tá các router trong đó.

Vậy việc test app chính là việc test các hàm router trong cái app này. Vậy làm sao để test các hàm đó khi nó đang nằm trong app, thậm chí, có thế hàm đó đang được decorate bởi một đống các hàm khác?

Flask giúp chúng ta điều này bằng cách cung cấp cho bạn một `TestClient` object, cái đó đóng vai trò như là một client thực sự.

Để tạo được object này, bạn chỉ cần gọi phương thức `test_client` trong `Flask` object

Giả sử, backend của bạn có một api truyền lên tên một người và trả về lời chào người đó, bạn có thể làm như sau:

```python
app = Flask(__name__)

@app.route('/say/<name>', methods=['GET'])
def say_hello(name):
	return f'Hello, {name}'

client = app.test_client()

response = client.get('/say/Thanh')

assert response.data == b'Hello, Thanh'
```

OK, đó là những điều mình cảm thấy Flask thật tuyệt vời để mình có thể phát triển một webservice trong Python. Bạn thì sao, cho mình ý kiến của các bạn trong phần comment bên dưới nhé, bye bye.
