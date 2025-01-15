import random
import tkinter as tk
from tkinter import ttk
import time

class Roulette:
    def __init__(self, values=None):  # 盤面の値を直接受け取る
        self.values = values if values is not None else list(range(2, 13))
    
    def spin(self):
        """ルーレットを回して結果を返す"""
        return random.choice(self.values)
    
    def spin_multiple(self, times=1):
        """指定回数ルーレットを回して結果をリストで返す"""
        return [self.spin() for _ in range(times)]

class RouletteUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("ルーレットシミュレーター")
        
        # チャット入力欄
        ttk.Label(self.window, text="項目を入力（改行で区切り）:").grid(row=0, column=0, padx=5, pady=5)
        self.chat_text = tk.Text(self.window, height=10, width=40)
        self.chat_text.grid(row=0, column=1, padx=5, pady=5)
        self.chat_text.insert('1.0', '犬\n猫\n鳥\nうさぎ')  # デフォルト値
        
        # 回す回数設定
        ttk.Label(self.window, text="回す回数:").grid(row=1, column=0, padx=5, pady=5)
        self.times_var = tk.StringVar(value="1")
        self.times_entry = ttk.Entry(self.window, textvariable=self.times_var)
        self.times_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # 実行ボタン
        self.spin_button = ttk.Button(self.window, text="ルーレットを回す", command=self.spin_roulette)
        self.spin_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # 結果表示
        self.result_var = tk.StringVar()
        self.result_label = ttk.Label(self.window, textvariable=self.result_var)
        self.result_label.grid(row=3, column=0, columnspan=2, pady=5)

        # アニメーション用のキャンバス
        self.canvas = tk.Canvas(self.window, width=300, height=300)
        self.canvas.grid(row=4, column=0, columnspan=2, pady=10)
        self.draw_roulette()

    def draw_roulette(self):
        """ルーレットを描画"""
        self.canvas.delete("all")
        center_x, center_y = 150, 150
        radius = 100
        self.canvas.create_oval(center_x-radius, center_y-radius, 
                              center_x+radius, center_y+radius, 
                              fill="white", outline="black")
        # 矢印を描画
        self.canvas.create_line(150, 50, 150, 100, arrow=tk.LAST, width=2)

    def animate_spin(self, final_value, values):
        """ルーレットの回転アニメーション"""
        self.spin_button.config(state='disabled')  # ボタンを無効化
        frames = 30  # アニメーションのフレーム数
        for _ in range(frames):
            self.result_var.set(random.choice(values))
            self.window.update()
            time.sleep(0.05)
        self.result_var.set(f"結果: {final_value}")
        self.spin_button.config(state='normal')  # ボタンを有効化

    def spin_roulette(self):
        try:
            # テキストエリアから値を取得し、改行で分割
            text_content = self.chat_text.get('1.0', tk.END).strip()
            values = [line.strip() for line in text_content.split('\n') if line.strip()]
            
            if not values:
                self.result_var.set("項目を入力してください")
                return
                
            times = int(self.times_var.get())
            if times < 1:
                self.result_var.set("回数は1以上を入力してください")
                return
                
            roulette = Roulette(values=values)
            results = roulette.spin_multiple(times)
            
            if times == 1:
                self.animate_spin(results[0], values)
            else:
                self.animate_spin(str(results), values)
                
        except ValueError:
            self.result_var.set("正しい値を入力してください")

def main():
    app = RouletteUI()
    app.window.mainloop()

if __name__ == "__main__":
    main()
