---
tags:
  - python
date: 2026-05-29
---
# Closure trong Python

Closure trong Python là một hàm được định nghĩa bên trong một hàm khác và được trả về như giá trị của hàm ngoài, trong đó hàm bên trong vẫn truy cập được các biến của hàm ngoài kể cả sau khi hàm ngoài đã kết thúc. Closure là cơ chế nền tảng cho decorator và là một công cụ thay thế hiệu quả cho hàm đệ quy trong nhiều trường hợp.

## Cấu trúc cơ bản

Hàm ngoài định nghĩa biến cục bộ và một nested function dùng biến đó, rồi trả về nested function.

```python
def outer():
    x = 1
    def inner():
        print(f'x in outer function: {x}')
    return inner
```

Giá trị trả về của `outer` là một hàm. Nói cách khác, closure là việc định nghĩa một hàm mà hàm đó định nghĩa các hàm khác, mang theo môi trường biến của nơi nó được tạo ra.

## Ghi biến của hàm ngoài bằng `nonlocal`

Mặc định, nested function chỉ đọc được biến của hàm ngoài; gán lại biến đó sẽ báo lỗi vì Python coi nó là biến cục bộ mới. Từ khóa `nonlocal` báo cho nested function rằng biến không phải biến cục bộ, cho phép cập nhật biến của hàm ngoài qua nhiều lần gọi.

```python
def outer():
    x = 1
    def inner():
        nonlocal x
        x += 1
        return x
    return inner
```

## Thay thế hàm đệ quy

Hàm đệ quy yêu cầu tư duy ngược từ trạng thái hiện tại về trạng thái trước đó và xác định điều kiện dừng. Closure cho phép tư duy tự nhiên hơn: giữ trạng thái trong biến của hàm ngoài và cập nhật nó qua mỗi lần gọi. Dãy Fibonacci viết bằng closure:

```python
def fib():
    x1, x2 = 0, 1
    def get_next_number():
        nonlocal x1, x2
        x1, x2 = x2, x1 + x2
        return x2
    return get_next_number
```

So sánh hiệu năng cho thấy closure nhanh hơn đệ quy nhiều bậc (bài tham khảo đo được khoảng 1000 lần cho cùng bài toán Fibonacci): mọi giá trị tạm của hàm đệ quy được lưu riêng biệt trên call stack, trong khi closure cập nhật cùng một bộ biến trong một vòng lặp. Ngoài ra, đệ quy bị giới hạn độ sâu - mặc định CPython chỉ cho phép khoảng 1000 stack frame và vượt quá sẽ phát sinh `RecursionError`; closure về bản chất là một vòng lặp nên không vướng giới hạn này. Khi cần hiệu năng tối đa và bài toán chia được thành bài toán con, dynamic programming vẫn tốt hơn, nhưng closure dễ hiểu hơn và đủ tốt cho phần lớn trường hợp.

## Thay thế class đơn giản

Closure có thể thay thế một class khi class đó không có quá nhiều thuộc tính và phương thức. Một closure nhận tham số cấu hình rồi sinh ra các hàm chuyên biệt - ví dụ một bộ phân loại học sinh theo cận điểm số:

```python
def make_student_classifier(lower_bound, upper_bound):
    def classify_student(exam_dict):
        return {k: v for k, v in exam_dict.items() if lower_bound <= v < upper_bound}
    return classify_student

grade_A = make_student_classifier(80, 100)
grade_B = make_student_classifier(70, 80)
```

## Nguồn tham khảo

- [Đừng sử dụng đệ qui trong Python](https://www.nkthanh.dev/posts/dung-su-dung-de-qui-trong-python)
- [Don't Use Recursion In Python Any More - Towards Data Science](https://towardsdatascience.com/dont-use-recursion-in-python-any-more-918aad95094c)
- [sys.setrecursionlimit - Python documentation](https://docs.python.org/3/library/sys.html#sys.setrecursionlimit)

## Liên kết tri thức

- [Decorator trong Python - decorator dựa trên closure để giữ hàm gốc và tham số cấu hình](./Decorator%20trong%20Python.md)
- [Coroutine trong Python - cùng cơ chế giữ trạng thái cục bộ qua nhiều lần gọi, nhưng coroutine suspend/resume thay vì trả về hàm](./Coroutine%20trong%20Python.md)
