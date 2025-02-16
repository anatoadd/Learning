import tkinter as tk
from tkinter import ttk
from math import comb, factorial
from itertools import product
import time

def prob(n, ui_instance=None):
    """n人でじゃんけんをした時の相子確率を計算"""
    print(f"{n}人の計算を開始...")  # 進行状況を表示
    
    # 全ての可能な手の組み合わせを生成
    total_patterns = 3 ** n  # 全パターン数を事前計算
    print(f"計算が必要なパターン数: {total_patterns}")
    
    all_patterns = list(product([0, 1, 2], repeat=n))  # 0:グー, 1:チョキ, 2:パー
    draw_count = 0
    
    # 各パターンについて相子かどうかを判定
    for i, pattern in enumerate(all_patterns):
        # 一時停止状態のチェック
        if ui_instance and ui_instance.paused:
            while ui_instance.paused:
                ui_instance.window.update()
                time.sleep(0.1)  # CPUの負荷を下げるために少し待機
        
        # 進捗表示の条件を修正
        if total_patterns >= 100 and i % (total_patterns // 100) == 0:
            print(f"進捗: {i/total_patterns*100:.1f}% ({i}/{total_patterns} パターン処理済み)")
            if ui_instance:
                ui_instance.window.update()  # UIの更新
            
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
        
        # 進行状況表示用のフレーム
        self.status_frame = ttk.LabelFrame(self.window, text="進行状況", padding=5)
        self.status_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        # 現在の計算状況
        self.status_label = ttk.Label(self.status_frame, text="計算中...")
        self.status_label.grid(row=0, column=0, padx=5, pady=2)
        
        # 進捗バー
        self.progress = ttk.Progressbar(self.status_frame, length=300, mode='determinate')
        self.progress.grid(row=1, column=0, padx=5, pady=2)
        
        # コントロールボタンフレーム
        self.control_frame = ttk.Frame(self.window)
        self.control_frame.grid(row=1, column=0, padx=10, pady=5)
        
        # 一時停止/再開ボタン
        self.pause_button = ttk.Button(self.control_frame, text="一時停止", command=self.toggle_pause)
        self.pause_button.grid(row=0, column=0, padx=5)
        
        # 結果表示用のテキストウィジェット
        self.text = tk.Text(self.window, width=50, height=20)
        self.text.grid(row=2, column=0, padx=10, pady=5)
        
        # 計算制御用の変数
        self.paused = False
        self.current_n = 2
        
        # 計算開始
        self.calculate_next(2)  # 2人から開始

    def toggle_pause(self):
        """計算の一時停止/再開を切り替え"""
        self.paused = not self.paused
        if self.paused:
            self.pause_button.config(text="再開")
            self.status_label.config(text="一時停止中...")
        else:
            self.pause_button.config(text="一時停止")
            self.calculate_next(self.current_n)

    def calculate_next(self, n):
        """n人の確率を計算し、次の計算をスケジュール"""
        if self.paused:
            return
            
        if n > 20:  # 20人を超えたら終了
            self.status_label.config(text="計算完了")
            self.progress['value'] = 100
            return
            
        self.current_n = n
        total_patterns = 3 ** n
        self.status_label.config(text=f"{n}人の確率を計算中... (計算必要パターン数: {total_patterns})")
        self.progress['value'] = (n - 2) * 100 / 18  # 2人から20人までの進捗を表示
        self.window.update()  # UIを更新
        
        probability, _ = prob(n, self)  # UIインスタンスを渡す
        self.text.insert(tk.END, f"{n}人の場合の相子確率: {probability:.6f} ({probability*100:.4f}%)\n")
        self.text.see(tk.END)  # 最新の結果を表示
        
        # 次の人数の計算をスケジュール
        self.window.after(100, lambda: self.calculate_next(n + 1))

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = JankenUI()
    app.run()