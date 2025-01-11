from itertools import permutations, product

# 数列の全パターン生成 (0000～9999) を辞書順にソート済みリストで保持
digits = [sorted(f"{i:04}") for i in range(10000)]
unique_digits = set(tuple(digit) for digit in digits)  # 重複排除

operators = ['+', '-', '*', '/']  # 演算子リスト

successful_sequences = 0  # 10を作れる数列のカウント

for digit_tuple in unique_digits:
    success_for_this_sequence = False  # この数列で10を作れるかを記録
    for perm in permutations(digit_tuple):  # 並び替え
        for ops in product(operators, repeat=3):  # 演算子の全パターン
            # 数式を生成
            expression = f"{perm[0]}{ops[0]}{perm[1]}{ops[1]}{perm[2]}{ops[2]}{perm[3]}"
            try:
                if eval(expression) == 10:  # 10を作れるか判定
                    success_for_this_sequence = True
                    break  # 作れる場合は探索を終了
            except ZeroDivisionError:
                continue  # ゼロ除算を回避できるよう設定
        if success_for_this_sequence:
            break  # 数列単位で探索終了
    if success_for_this_sequence:
        successful_sequences += 1

total_sequences = len(unique_digits)
success_ratio = successful_sequences / 10000

# 結果を出力
print("考慮した数列の数", total_sequences)
print("10を作れる数列の数:", successful_sequences)
print("成功率:", success_ratio)
