#3個のサイコロを振り、その出目の積がkとなる確率が1/36であるようなkを全て答えよ
from itertools import product

# サイコロの出目
dice = [1, 2, 3, 4, 5, 6]

# 出目の積を計算し、頻度を数える
product_counts = {}

for rolls in product(dice, repeat=3):  # 3個のサイコロを振るすべての組み合わせ
    p = rolls[0] * rolls[1] * rolls[2]
    if p in product_counts:
        product_counts[p] += 1
    else:
        product_counts[p] = 1

# 確率が1/36となるkを探す
result = [k for k, count in product_counts.items() if count == 6]

print(result)