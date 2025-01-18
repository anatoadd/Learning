import random
import tkinter as tk
from tkinter import ttk
import time
import math

class Roulette:
    def __init__(self, values=None):  # 盤面の値を直接受け取る
        self.values = values if values is not None else list(range(2, 13))
    
    def spin(self):
        """ルーレットを回して結果を返す"""
        # 完全なランダムな角度を生成(0-360度)
        random_angle = random.uniform(0, 360)
        # 角度から対応する項目のインデックスを計算
        item_count = len(self.values)
        angle_per_item = 360 / item_count
        selected_index = int((random_angle % 360) / angle_per_item)
        return self.values[selected_index], random_angle
    
    def spin_multiple(self, times=1):
        """指定回数ルーレットを回して結果をリストで返す"""
        return [self.spin()[0] for _ in range(times)]

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
        self.current_angle = 0
        
        # 色のリストを定義（異なる色相の色を使用）
        self.colors = [
            "#FF6B6B",  # 赤
            "#4ECDC4",  # ターコイズ
            "#FFD93D",  # 黄色
            "#95A5A6",  # グレー
            "#8E44AD",  # 紫
            "#2ECC71",  # 緑
            "#E67E22",  # オレンジ
            "#3498DB",  # 青
            "#E74C3C",  # 深い赤
            "#1ABC9C",  # エメラルド
            "#F1C40F",  # 金色
            "#34495E"   # 紺
        ]
        
        self.draw_roulette()

    def draw_roulette(self, rotation_angle=0):
        """ルーレットを描画"""
        self.canvas.delete("all")
        center_x, center_y = 150, 150
        radius = 100
        
        # テキストエリアから値を取得
        text_content = self.chat_text.get('1.0', tk.END).strip()
        values = [line.strip() for line in text_content.split('\n') if line.strip()]
        
        if not values:
            # 値が無い場合は空のルーレットを描画
            self.canvas.create_oval(center_x-radius, center_y-radius, 
                                  center_x+radius, center_y+radius, 
                                  fill="white", outline="black")
            return
            
        # ルーレットの分割数
        n = len(values)
        angle = 360 / n
        
        # 各項目を描画
        for i in range(n):
            start_angle = i * angle + rotation_angle
            # 扇形を描画（定義済みの色を使用）
            color_index = i % len(self.colors)
            self.canvas.create_arc(center_x-radius, center_y-radius,
                                 center_x+radius, center_y+radius,
                                 start=start_angle, extent=angle,
                                 fill=self.colors[color_index])
            
            # テキストの位置を計算
            text_angle = math.radians(start_angle + angle/2)
            text_radius = radius * 0.7  # テキストの配置位置を調整
            text_x = center_x + text_radius * math.cos(text_angle)
            text_y = center_y - text_radius * math.sin(text_angle)
            
            # テキストを描画（角度を反転）
            rotated_text_angle = (start_angle + angle/2) % 360
            if 90 <= rotated_text_angle <= 270:
                rotated_text_angle += 180
            self.canvas.create_text(text_x, text_y, text=values[i], angle=rotated_text_angle, fill="black")
        
        # 矢印を描画（外側から内側へ）
        self.canvas.create_line(300, 150, 250, 150, arrow=tk.LAST, width=2)

    def animate_spin(self, final_value, final_angle, values):
        """ルーレットの回転アニメーション"""
        self.spin_button.config(state='disabled')  # ボタンを無効化
        
        # アニメーションの設定
        total_rotation = 1440 + final_angle  # 4回転 + 最終位置
        frames = 120  # フレーム数を増やして、よりなめらかに
        
        for i in range(frames):
            progress = i / frames
            # より滑らかな減速のためのイージング関数
            eased_progress = 1 - math.pow(1 - progress, 4)  # 4次のイージング
            current_angle = total_rotation * eased_progress
            
            # ルーレットを描画
            self.draw_roulette(-current_angle)  # マイナスを付けて時計回りに
            
            # 結果表示を更新
            if i == frames - 1:  # 最後のフレームでのみ結果を表示
                self.result_var.set(f"結果: {final_value}")
                
            self.window.update()
            
            # 進行に応じて待機時間を調整
            wait_time = 0.01 + (progress * 0.03)  # 進むにつれて待機時間を長く
            time.sleep(wait_time)
            
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
            if times == 1:
                result, angle = roulette.spin()
                self.animate_spin(result, angle, values)
            else:
                results = roulette.spin_multiple(times)
                self.result_var.set(f"結果: {results}")
                
        except ValueError:
            self.result_var.set("正しい値を入力してください")

def main():
    app = RouletteUI()
    app.window.mainloop()

if __name__ == "__main__":
    main()
