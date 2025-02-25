import numpy as np
import tkinter as tk
import time

# 定数の定義
WHITE = 0
BLACK = 1
RIGHT = 0
UP = 1
LEFT = 2
DOWN = 3

# マップサイズ
MAP_SIZE = 50  # 大きなマップに変更

# 初期マップの作成
grid = np.zeros((MAP_SIZE, MAP_SIZE), dtype=int)

# エージェントの初期位置
x, y = MAP_SIZE // 2, MAP_SIZE // 2

# エージェントの初期方向
direction = RIGHT

# ウィンドウの設定
window = tk.Tk()
window.title("Langton's Ant")

# キャンバスの作成
canvas_size = 500
cell_size = canvas_size // MAP_SIZE
canvas = tk.Canvas(window, width=canvas_size, height=canvas_size, bg='white')
canvas.pack()

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

    # ウィンドウを更新
    window.update()

# メインループ
while True:
    update_grid()
    time.sleep(0.1)  # 動作の間隔を設定

window.mainloop()