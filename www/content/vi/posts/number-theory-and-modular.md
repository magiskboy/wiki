---
title: "Number Theory and Modular"
date: "2019-09-17T13:41:33+07:00"
tags:
- math
- computer science
categories:
- Math
description: "Lý thuyết số là một phần quan trọng giúp cho máy tính xử lí công việc nhanh hơn, tiết kiệm tài nguyên hơn. Lý thuyết số cũng là 1 phần của toán học thuần tuý. Đối tượng lý thuyết số nghiên cứu là các số nguyên đi kèm theo nó là các phép toán cũng như tính chất của chúng."
---


Các thành tựu cơ bản mà lý thuyết số mang lại có tính ứng dụng trong thực tế rất cao nhưng các kiến thức nâng cao thì chưa áp dụng được nhiều. Một trong những ứng dụng quan trọng của lý thuyết số là ngành mật mã học.

> …virtually every theorem in elementary number theory arises in a natural, motivated way in connection with the problem of making computers do high-speed numerical calculations
> — <cite>Donald Knuth</cite>

## Phép đồng dư và 4 thuộc tính cơ bản của nó

Hồi học tiểu học, cô giáo nói với chúng tôi rằng tổng các chữ số của 1 số nếu chia hết cho 3 thì số đó chia hết cho 3? Lớn lên tôi vẫn thắc mắc rằng tại sao? Để trả lời câu hỏi đó, ta cùng tìm hiểu về số dư và những bài toán thú vị xung quanh đối tượng này.

Ta biết rằng 2 số nguyên khi đem chia cho nhau có thể ra kết quả không phải là số nguyên, và trong phạm vi của lý thuyết số, ta không cho phép điều này xảy ra. Thay vào đó, ta nhận được số dư, vậy tất cả các thành phần trong 1 phép tính chia đều là số nguyên.

Nếu A = B × Q + R thì B = A / Q dư R và số dư này luôn nhỏ hơn B

Lấy ví dụ A = 7, Q = 3, ta dễ thấy rằng B = A / Q = 7 / 3 = 2 dư 1

Vậy đồng dư (modular) là gì?
Nếu 2 số A và B chia cho M cùng có số dư giống nhau thì ta gọi A B là đồng dư của nhau.

Ví dụ: A = 7, B = 12, M = 5 thì ta nói A ≡ B (mod 7) hay A và B cùng là mô đun của M

Vậy toán tử này có những tính chất gì?
Dưới đây là 4 tính chất của phép toán này

```
Addition of constant
If a ≡ b (mod m) then a + c ≡ b + c (mod m) for any c
```

```
Addition
If a ≡ b (mod m) and c ≡ d then a + c ≡ b + d (mod m)
```

```
Multiplication by a constant
If a ≡ b (mod m) then a × c ≡ b × c (mod m) for any c
```

```
Multiplication
If a ≡ b (mod m) and c ≡ d (mod m) then a × c ≡ b × d (mod m)
```

Các bạn có thể dễ dàng chứng minh 4 công thức này bằng cách sử dụng biểu thức sau A = B × Q + R :smile:

OK, giờ cùng áp dụng các công thức trên để giải một số câu đố thú vị nhé

### Ứng dụng của phép đồng dư

__Bài toán 1__
Không cần thực hiện phép toán 17 × (12 × 19 + 5) − 23, bạn có thể cho biết số dư của nó khi chia cho 3 không? :smile:

```
Ta hãy nhớ rằng A ≡ B (mod M)→ A + C ≡ B + C (mod M) và A ≡ B (mod M) → A × C ≡ B × C (mod M), nhớ rằng M ở đây là 3 nhé
17 ≡ 2
12 ≡ 0, 5 ≡ 2 → (12 × 19 + 5) ≡ (0 + 2) ≡ 2
23 ≡ 2
Vậy ta có thể suy ra (17 × (12 × 19 + 5) − 23) ≡ (2 + 2 −2) = 2
```


__Bài toán 2__
Tìm số dư của $$ 4632^{10} $$ khi chia cho 10?

```
Ta dễ thấy 4632 ≡ 2 (mod 10) → 4632¹⁰ ≡ 2¹⁰ ≡ 1024 (mod 10)
vậy số dư khi chia 4632¹⁰ cho 10 cũng là số dư khi chia 1024 cho 10 và là 4
```


__Bài toán 3__
3475 chia hết cho 3 không, nếu không thì số dư là bao nhiêu?

```
Để ngắn gọn, trong bài ta ngầm hiểu các phép đồng dư là cho 3 nhé
ta có
```
$$10 ≡ 1 → 10^𝑘 ≡ 1^𝑘 ≡ 1$$
```
ta phân tích 3475 = 3 × 10³ + 4 × 10² + 7 × 10¹ + 5
vậy 3475 ≡ (0 × 1 + 1 × 1 + 7 × 1 + 2) = (0 + 1 + 1+ 2) = 1
vậy 3475 chia 3 dư 1
Điểm mấu chốt ở đây là các nhân tử 10 đều bị triệt tiêu để lại các chữ số nên tính tổng các chữ số đó cũng là tính tổng các đồng dư.
```

Vậy mình đã giới thiệu sơ qua về lí thuyết số cũng như ứng dụng của phép đồng dư.

Hẹn gặp lại trong bài viết sau.