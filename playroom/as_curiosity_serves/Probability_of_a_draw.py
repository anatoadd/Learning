import tkinter as tk
from tkinter import ttk
from math import comb, factorial
from itertools import product

def prob(n):
    """n人でじゃんけんをした時の相子確率を計算"""
    print(f"{n}人の計算を開始...")  # 進行状況を表示
    
    # 全ての可能な手の組み合わせを生成
    total_patterns = 3 ** n  # 全パターン数を事前計算
    print(f"計算が必要なパターン数: {total_patterns}")
    
    all_patterns = list(product([0, 1, 2], repeat=n))  # 0:グー, 1:チョキ, 2:パー
    draw_count = 0
    
    # 各パターンについて相子かどうかを判定
    for i, pattern in enumerate(all_patterns):
        if i % (total_patterns // 100) == 0:  # 1%ごとに進捗を表示
            print(f"進捗: {i/total_patterns*100:.1f}% ({i}/{total_patterns} パターン処理済み)")
            
        # 全員同じ手の場合
        if len(set(pattern)) == 1:
            draw_count += 1
            continue
            
        # 手の出現回数を数える
        counts = [pattern.count(hand) for hand in range(3)]
        
        # グー、チョキ、パーが全て出ている場合
        if all(count > 0 for count in counts):
            draw_count += 1
            continue
            
        # 2種類の手が出ている場合
        hands = set(pattern)
        if len(hands) == 2:
            # それぞれの手の出現回数を数える
            counts = [pattern.count(hand) for hand in range(3)]
            # 勝敗判定
            is_draw = True
            for i in range(3):
                if counts[i] > 0 and counts[(i + 1) % 3] > 0:
                    is_draw = False
                    break
            if is_draw:
                draw_count += 1

    print(f"{n}人の計算完了")  # 計算完了を表示
    return draw_count / total_patterns, []

class JankenUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("じゃんけん相子確率計算")
        
        # 進行状況表示用のラベル
        self.status_label = ttk.Label(self.window, text="計算中...")
        self.status_label.grid(row=0, column=0, padx=10, pady=5)
        
        # 結果表示用のテキストウィジェット
        self.text = tk.Text(self.window, width=50, height=20)
        self.text.grid(row=1, column=0, padx=10, pady=5)
        
        # 計算開始
        self.window.after(100, self.calculate_probabilities)

    def calculate_probabilities(self):
        """確率を計算して表示"""
        for n in range(2, 11):  # 10人までに制限
            total_patterns = 3 ** n
            self.status_label.config(text=f"{n}人の確率を計算中... (計算必要パターン数: {total_patterns})")
            self.window.update()  # UIを更新
            
            probability, _ = prob(n)
            self.text.insert(tk.END, f"{n}人の場合の相子確率: {probability:.6f} ({probability*100:.4f}%)\n")
            self.text.see(tk.END)  # 最新の結果を表示
            self.window.update()
        
        self.status_label.config(text="計算完了")

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = JankenUI()
    app.run()