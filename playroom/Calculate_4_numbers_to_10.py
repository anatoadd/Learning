#Calculate_4_numbers_to_10.py
import itertools

# 与えられた4つの1桁の数字を入力
digits = list(map(int, input("4つの数字を入力してください: ").split()))

# 使用可能な演算子
operators = ['+', '-', '*', '/']

# すべての数字の順列を試す
for nums in itertools.permutations(digits):
    # すべての演算子の組み合わせを試す
    for ops in itertools.product(operators, repeat=3):
        # 3つの演算子を使い、4つの数字を順番に計算
        expressions = [
            f"({nums[0]} {ops[0]} {nums[1]}) {ops[1]} {nums[2]} {ops[2]} {nums[3]}",
            f"{nums[0]} {ops[0]} ({nums[1]} {ops[1]} {nums[2]}) {ops[2]} {nums[3]}",
            f"{nums[0]} {ops[0]} {nums[1]} {ops[1]} ({nums[2]} {ops[2]} {nums[3]})",
            f"({nums[0]} {ops[0]} {nums[1]}) {ops[1]} ({nums[2]} {ops[2]} {nums[3]})",
            f"({nums[0]} {ops[0]} ({nums[1]} {ops[1]} {nums[2]})) {ops[2]} {nums[3]}"
        ]
        
        # 各式を評価して、10になるかチェック
        for expr in expressions:
            try:
                if abs(eval(expr) - 10) < 1e-9:  # 浮動小数点誤差の考慮
                    print(f"式: {expr} = 10")
                    exit()
            except ZeroDivisionError:
                continue

# どの組み合わせでも10にならない場合
print("10になりません")
