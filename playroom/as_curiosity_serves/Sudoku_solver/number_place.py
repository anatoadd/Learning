# AIにて作成中

import pygame
import sys
import random
import json

# Pygame 初期化
pygame.init()

# 画面設定
WIDTH, HEIGHT = 540, 600
GRID_SIZE = 60
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("数独")

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# フォント設定
FONT = pygame.font.Font(None, 40)

def draw_grid():
    """ 数独の盤面を描画 """
    SCREEN.fill(WHITE)
    for i in range(10):
        line_width = 3 if i % 3 == 0 else 1
        pygame.draw.line(SCREEN, BLACK, (i * GRID_SIZE, 0), (i * GRID_SIZE, 540), line_width)
        pygame.draw.line(SCREEN, BLACK, (0, i * GRID_SIZE), (540, i * GRID_SIZE), line_width)

def draw_numbers(board):
    """ 数独の数字を描画 """
    for row in range(9):
        for col in range(9):
            num = board[row][col]
            if num != 0:
                text = FONT.render(str(num), True, BLACK)
                SCREEN.blit(text, (col * GRID_SIZE + 20, row * GRID_SIZE + 15))

def main():
    board = [[0] * 9 for _ in range(9)]  # 仮の空の数独盤面
    running = True
    while running:
        SCREEN.fill(WHITE)
        draw_grid()
        draw_numbers(board)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

def is_valid(board, row, col, num):
    """ 指定した (row, col) に num を入れてよいかチェック """
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
    
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def solve(board, count_solutions=False):
    """ バックトラッキングで数独を解く (解の数をカウントするオプション付き) """
    solutions = 0
    def backtrack():
        nonlocal solutions
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    for num in range(1, 10):
                        if is_valid(board, row, col, num):
                            board[row][col] = num
                            backtrack()
                            board[row][col] = 0
                    return
        solutions += 1
    
    backtrack()
    return solutions if count_solutions else solutions == 1

def generate_sudoku():
    """ 完成済みの数独をランダムに生成 """
    board = [[0] * 9 for _ in range(9)]
    for i in range(9):
        num = random.randint(1, 9)
        while not is_valid(board, i, i, num):
            num = random.randint(1, 9)
        board[i][i] = num
    solve(board)
    return board

def remove_numbers(board, difficulty):
    """ 盤面から数字を消して問題を作成する (解が一意か確認) """
    puzzle = [row[:] for row in board]
    difficulty_levels = {"beginner": 30, "intermediate": 40, "advanced": 50}
    count = difficulty_levels.get(difficulty, 40)
    while count > 0:
        row, col = random.randint(0, 8), random.randint(0, 8)
        while puzzle[row][col] == 0:
            row, col = random.randint(0, 8), random.randint(0, 8)
        temp = puzzle[row][col]
        puzzle[row][col] = 0
        if solve([row[:] for row in puzzle], count_solutions=True) > 1:
            puzzle[row][col] = temp  # 複数解があった場合、戻す
        else:
            count -= 1
    return puzzle

def save_problems(valid_puzzles, invalid_puzzles):
    """ 作成した問題を保存する """
    with open("valid_puzzles.json", "w") as f:
        json.dump(valid_puzzles, f)
    with open("invalid_puzzles.json", "w") as f:
        json.dump(invalid_puzzles, f)

def print_board(board):
    """ 盤面を表示する """
    for row in board:
        print(" ".join(str(num) if num != 0 else '.' for num in row))

valid_puzzles = []
invalid_puzzles = []
while True:
    sudoku_board = generate_sudoku()
    difficulty = input("難易度を選択 (beginner/intermediate/advanced/exit): ").strip().lower()
    if difficulty == "exit":
        break
    
    puzzle = remove_numbers(sudoku_board, difficulty)
    if solve([row[:] for row in puzzle], count_solutions=True) == 1:
        valid_puzzles.append(puzzle)
        print("\n問題 (一意な解あり):")
        print_board(puzzle)
    else:
        invalid_puzzles.append(puzzle)
        print("\n問題 (複数解あり - 破棄):")
        continue
    
    save_problems(valid_puzzles, invalid_puzzles)