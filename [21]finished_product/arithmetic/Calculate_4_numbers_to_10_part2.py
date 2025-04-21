from itertools import permutations, product

# 必要なモジュールをインポート
# permutations: 順列を生成するための関数
# product: 直積(全ての組み合わせ)を生成するための関数

# 数列の生成と重複排除のための準備
digits = []  # 0000から9999までの4桁の数字を格納するリスト
success_map = {}  # 各数列パターンが10を作れるかどうかを記録する辞書

# 0000から9999までの全ての4桁の数字を生成
for i in range(10000):
    try:
        # 各数字を1桁ずつのリストに変換 (例: 123 → [0,1,2,3])
        digit_list = [int(d) for d in f"{i:04}"]
        digits.append(tuple(sorted(digit_list)))  # タプルとして昇順にソートして追加
    except ValueError:
        continue

# 重複を排除した数列のセットを作成
unique_digits = set(digits)

# 使用する演算子と計算パターンの定義
operators = ['+', '-', '*', '/']  # 基本的な四則演算
patterns = [
    "{}{}{}{}{}{}{}",      # 例: a+b+c+d
    "({}{}{}){}{}{}{}", # 例: (a+b+c)+d
    "{}{}({}{}{}{}{})",   # 例: a+(b+c+d)
    "({}{}{}{}{}{}{})",   # 例: (a+b+c+d)
    "({}{}{}){}({}{}{})", # 例: (a+b)+(c+d)
    "({}{}{})({}{}{}{})", # 例: (a+b)+(c+d)
    "{}({}{}{}{}{}{})",   # 例: a+(b+c+d)
]

# 各数列パターンに対して計算を実行
for digit_tuple in unique_digits:
    found_ten = False  # 10を作れたかどうかのフラグ
    # 数字の順列を生成して試行
    for perm in permutations(digit_tuple):
        if found_ten:
            break
        # 演算子の全ての組み合わせを試行
        for ops in product(operators, repeat=3):
            if found_ten:
                break
            # 各計算パターンを試行
            for pattern in patterns:
                try:
                    # 数式を組み立てて計算
                    expression = pattern.format(perm[0], ops[0], perm[1], ops[1], perm[2], ops[2], perm[3])
                    # eval()の代わりに、演算子を関数として実装
                    nums = [float(perm[0])]
                    for i in range(3):
                        if ops[i] == '+':
                            nums.append(float(perm[i+1]))
                        elif ops[i] == '-':
                            nums.append(-float(perm[i+1]))
                        elif ops[i] == '*':
                            nums[-1] *= float(perm[i+1])
                        elif ops[i] == '/':
                            nums[-1] /= float(perm[i+1])
                    result = sum(nums)
                    # 結果が10に近い場合（浮動小数点の誤差を考慮）
                    if abs(result - 10) < 1e-10:
                        success_map[digit_tuple] = True
                        found_ten = True
                        break
                except (ZeroDivisionError, ValueError):
                    # 0での除算や不正な計算をスキップ
                    continue
    # 10を作れなかった場合
    if not found_ten:
        success_map[digit_tuple] = False

# 結果の集計
total_sequences = 10000  # 全体の数列数
# 元の10000通りの中で10を作れる数列の数を計算
successful_sequences = sum(1 for digit_tuple in digits 
                         if success_map.get(digit_tuple, False))

# 重複排除後の成功数を計算
unique_successful = sum(1 for result in success_map.values() if result)

# 結果の出力
print(f"重複排除後の数列数: {len(unique_digits)}")
print(f"重複排除後の10を作れる数列の数: {unique_successful}")
print(f"元の10000通りの中で10を作れる数列の数: {successful_sequences}")
print(f"成功率: {successful_sequences / 100}%")