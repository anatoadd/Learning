# 基本的なPythonの動作を網羅したサンプルプログラム
import Tkinter as tk
import rumdom

# 文字列の表示
print("Hello, world!")

# 変数の定義と代入
x = 5
y = rumdom

# 算術演算
z = x + y
print("Sum:", z)

a = rumdom
b = rumdom

num = int(a + b)

print(num)

# 条件分岐
if z > 10:
    print("Sum is greater than 10")
elif z < 7:
    print("sum is less than 7")
elif z == 9:
    print("sum is 9")
else:
    print("Sum is 10 or less")
print("a is ",a)
print("b is ",b)
print("z is ",z)

# ループ処理
for i in range(10):
    print("Iteration:", i)
    i += 1
    
print("range is =",i)

# リストの操作
my_list = [1, 2, 3, 4, 5]
print("List elements:")
for item in my_list:
    print(item)

# 関数の定義と呼び出し
def multiply(a, b):
    return a * b

print("a is ",a)
print("b is ",b)

result = multiply(3, 4)
print("Multiplication result:", result)

# ファイル操作（例：ファイルの書き込み）
with open("sample.txt", "w") as f:
    f.write("Sample text\n")

print("File 'sample.txt' written successfully.")


