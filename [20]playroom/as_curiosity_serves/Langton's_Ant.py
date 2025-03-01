import numpy as np
import tkinter as tk
from tkinter import ttk
import time

# 定数の定義
WHITE = 0
BLACK = 1
RIGHT = 0
UP = 1
LEFT = 2
DOWN = 3

# マップサイズ
MAP_SIZE = 500

# 初期マップの作成
grid = np.zeros((MAP_SIZE, MAP_SIZE), dtype=int)

# エージェントの初期位置
x, y = MAP_SIZE // 2, MAP_SIZE // 2

# エージェントの初期方向
direction = RIGHT

# 動作フラグ
running = False

# 速度設定
speed_levels = {
    1: 180,  # 最遅: 180フレームで1動作
    2: 165,
    3: 150, 
    4: 135,
    5: 120,
    6: 90,
    7: 60,
    8: 45,
    9: 35,
    10: 30  # 最速: 30フレームで1動作
}
current_speed = 5  # デフォルト値

# ウィンドウの設定
window = tk.Tk()
window.title("Langton's Ant")

# コントロールフレームの作成
control_frame = ttk.Frame(window)
control_frame.pack(pady=5)

# スピードコントロールの作成
speed_label = ttk.Label(control_frame, text="速度:")
speed_label.pack(side=tk.LEFT, padx=5)

speed_scale = ttk.Scale(control_frame, from_=1, to=10, orient=tk.HORIZONTAL,
                       length=200)
speed_scale.set(current_speed)
speed_scale.pack(side=tk.LEFT, padx=5)

# スタート/ストップボタンの作成
def toggle_simulation():
    global running
    running = not running
    start_stop_button.config(text="停止" if running else "開始")
    if running:
        simulation_loop()  # ループ再開

start_stop_button = ttk.Button(control_frame, text="開始", command=toggle_simulation)
start_stop_button.pack(side=tk.LEFT, padx=5)

# キャンバスの作成
canvas_size = 500
cell_size = canvas_size // MAP_SIZE
canvas = tk.Canvas(window, width=canvas_size, height=canvas_size, bg='white')
canvas.pack(pady=5)

def update_grid():
    global x, y, direction
    
    # 現在のマスの色に基づいて動作
    if grid[y][x] == WHITE:
        grid[y][x] = BLACK  # 白マスを黒マスに変更
        direction = (direction + 1) % 4  # 右に90度回転
    else:
        grid[y][x] = WHITE  # 黒マスを白マスに変更
        direction = (direction - 1) % 4  # 左に90度回転

    # エージェントの位置を更新
    if direction == RIGHT:
        x = (x + 1) % MAP_SIZE
    elif direction == UP:
        y = (y - 1) % MAP_SIZE
    elif direction == LEFT:
        x = (x - 1) % MAP_SIZE
    elif direction == DOWN:
        y = (y + 1) % MAP_SIZE

    # キャンバスをクリア
    canvas.delete("all")

    # グリッドの描画
    for i in range(MAP_SIZE):
        for j in range(MAP_SIZE):
            color = 'black' if grid[i][j] == BLACK else 'white'
            canvas.create_rectangle(j * cell_size, i * cell_size,
                                    (j + 1) * cell_size, (i + 1) * cell_size,
                                    fill=color, outline='gray')

def simulation_loop():
    global current_speed
    if running:
        current_speed = int(round(speed_scale.get()))  # スライダーの値を四捨五入して整数に変換
        current_speed = max(1, min(10, current_speed))  # 範囲外の値を防ぐ
        delay = speed_levels.get(current_speed, 100)  # 万が一キーがない場合のデフォルト値を100msに設定
        update_grid()
        window.after(delay, simulation_loop)  # 適切な整数値を渡す


# シミュレーションループの開始
simulation_loop()

window.mainloop()