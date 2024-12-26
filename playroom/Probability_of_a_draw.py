from math import comb, factorial

# ユーザーから人数を入力
while True:
    try:
        n = int(input("人数を入力: "))
        if n <= 2:
            print("人数は2人以上を入力してください。")
        else:
            break
    except ValueError:
        print("無効な入力です。")

def prob(n):
    # 1. 全員同じ手を出す確率
    same = 3 / (3 ** n)
    
    # 2. グー、チョキ、パーが1回ずつ出る確率 (n >= 3)
    if n >= 3:
        diff = comb(n, 3) * factorial(3) * (1 / 3) ** n
    else:
        diff = 0
    
    # 相子の確率
    return same + diff

# 相子の確率を計算
result = prob(n)

# 結果を表示
print(f"n={n} 人の相子確率: {result:.6f}")