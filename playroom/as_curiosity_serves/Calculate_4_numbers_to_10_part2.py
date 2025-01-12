from itertools import permutations, product

# 数列の全パターン生成 (0000～9999) を辞書順にソート済みリストで保持
digits = [sorted(f"{i:04}") for i in range(10000)]
unique_digits = set(tuple(digit) for digit in digits)  # 重複排除

operators = ['+', '-', '*', '/']  # 演算子リスト

successful_sequences = 0  # 10を作れる数列のカウント
successful_expressions = []  # 10を作れる式を保存するリスト
original_successful_count = 0  # 元の10000通りのうち成功した数のカウント

# 元の数列と重複排除後の数列の対応を記録する辞書
digit_to_unique = {}
for i, digit in enumerate(digits):
    digit_tuple = tuple(digit)
    if digit_tuple not in digit_to_unique:
        digit_to_unique[digit_tuple] = []
    digit_to_unique[digit_tuple].append(i)

for digit_tuple in unique_digits:
    success_for_this_sequence = False  # この数列で10を作れるかを記録
    for perm in permutations(digit_tuple):  # 並び替え
        for ops in product(operators, repeat=3):  # 演算子の全パターン
            # 数式を生成
            expression = f"{perm[0]}{ops[0]}{perm[1]}{ops[1]}{perm[2]}{ops[2]}{perm[3]}"
            try:
                if eval(expression) == 10:  # 10を作れるか判定
                    success_for_this_sequence = True
                    successful_expressions.append(expression)  # 成功した式を保存
                    break  # 作れる場合は探索を終了
            except ZeroDivisionError:
                continue  # ゼロ除算を回避できるよう設定
            except:  # その他の例外をキャッチ
                continue
        if success_for_this_sequence:
            break  # 数列単位で探索終了
    if success_for_this_sequence:
        successful_sequences += 1
        # この重複排除後の数列に対応する元の数列の数をカウント
        original_successful_count += len(digit_to_unique[digit_tuple])

total_sequences = len(unique_digits)
success_ratio_unique = successful_sequences / total_sequences
success_ratio_original = original_successful_count / 10000

# 結果を出力
print("考慮した重複排除後の数列の数:", total_sequences)
print("10を作れる重複排除後の数列の数:", successful_sequences)
print("重複排除後の成功率:", success_ratio_unique)
print("元の10000通りに対する成功率:", success_ratio_original)
print("\n成功した式の例(最大10個):")
for expr in successful_expressions[:10]:  # 最大10個まで表示
    print(f"{expr} = 10")
