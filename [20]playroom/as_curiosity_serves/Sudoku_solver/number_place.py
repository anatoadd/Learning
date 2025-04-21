# AIにて作成中

import pygame
import sys
import random
import json

# Pygame 初期化
pygame.init()

# 画面設定
WIDTH, HEIGHT = 540, 700  # ボタン用に高さを増やす
GRID_SIZE = 60
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("数独")

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# フォント設定
FONT = pygame.font.Font(None, 40)

# ボタンの設定
NEW_GAME_BUTTON = pygame.Rect(20, 600, 200, 40)
NUMBER_BUTTONS = [pygame.Rect(240 + i*30, 600, 25, 40) for i in range(9)]

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

def draw_buttons():
    """ ボタンを描画 """
    # 新規ゲーム開始ボタン
    pygame.draw.rect(SCREEN, GREEN, NEW_GAME_BUTTON)
    text = FONT.render("新規ゲーム", True, BLACK)
    SCREEN.blit(text, (30, 610))
    
    # 数字ボタン
    for i in range(9):
        pygame.draw.rect(SCREEN, BLUE, NUMBER_BUTTONS[i])
        text = FONT.render(str(i+1), True, WHITE)
        SCREEN.blit(text, (245 + i*30, 610))

def draw_grid():
    """ 数独の盤面を描画 """
    SCREEN.fill(WHITE)
    for i in range(10):
        line_width = 3 if i % 3 == 0 else 1
        pygame.draw.line(SCREEN, BLACK, (i * GRID_SIZE, 0), (i * GRID_SIZE, 540), line_width)
        pygame.draw.line(SCREEN, BLACK, (0, i * GRID_SIZE), (540, i * GRID_SIZE), line_width)
    draw_buttons()

def draw_numbers(board, original_board, selected_cell, invalid_cells):
    """ 数独の数字を描画 """
    for row in range(9):
        for col in range(9):
            # 選択されたセルの背景を灰色で描画
            if (row, col) == selected_cell:
                pygame.draw.rect(SCREEN, GRAY, (col * GRID_SIZE, row * GRID_SIZE, GRID_SIZE, GRID_SIZE))
            
            # 無効な数字を赤で表示
            if (row, col) in invalid_cells:
                color = RED
            # 元々あった数字を青で表示
            elif original_board[row][col] != 0:
                color = BLUE
            else:
                color = BLACK

            num = board[row][col]
            if num != 0:
                text = FONT.render(str(num), True, color)
                SCREEN.blit(text, (col * GRID_SIZE + 20, row * GRID_SIZE + 15))

def check_board_validity(board):
    """ 盤面全体の妥当性をチェック """
    invalid_cells = set()
    
    # 各行をチェック
    for row in range(9):
        nums = {}
        for col in range(9):
            if board[row][col] != 0:
                if board[row][col] in nums:
                    invalid_cells.add((row, col))
                    invalid_cells.add((row, nums[board[row][col]]))
                nums[board[row][col]] = col

    # 各列をチェック
    for col in range(9):
        nums = {}
        for row in range(9):
            if board[row][col] != 0:
                if board[row][col] in nums:
                    invalid_cells.add((row, col))
                    invalid_cells.add((nums[board[row][col]], col))
                nums[board[row][col]] = row

    # 各3x3ブロックをチェック
    for block_row in range(3):
        for block_col in range(3):
            nums = {}
            for i in range(3):
                for j in range(3):
                    row = block_row * 3 + i
                    col = block_col * 3 + j
                    if board[row][col] != 0:
                        if board[row][col] in nums:
                            invalid_cells.add((row, col))
                            prev_row, prev_col = nums[board[row][col]]
                            invalid_cells.add((prev_row, prev_col))
                        nums[board[row][col]] = (row, col)

    return invalid_cells

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

def main():
    # 初期盤面の生成
    board = [[0] * 9 for _ in range(9)]  # 空の盤面で開始
    original_board = [row[:] for row in board]
    
    selected_cell = None
    invalid_cells = set()
    running = True
    
    while running:
        SCREEN.fill(WHITE)
        draw_grid()
        draw_numbers(board, original_board, selected_cell, invalid_cells)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                
                # 新規ゲームボタンのクリック処理
                if NEW_GAME_BUTTON.collidepoint(x, y):
                    complete_board = generate_sudoku()
                    board = remove_numbers(complete_board, "intermediate")
                    original_board = [row[:] for row in board]
                    selected_cell = None
                    invalid_cells = set()
                
                # 数字ボタンのクリック処理
                for i, button in enumerate(NUMBER_BUTTONS):
                    if button.collidepoint(x, y) and selected_cell:
                        row, col = selected_cell
                        if original_board[row][col] == 0:
                            board[row][col] = i + 1
                            invalid_cells = check_board_validity(board)
                
                # 盤面のセル選択
                col = x // GRID_SIZE
                row = y // GRID_SIZE
                if 0 <= row < 9 and 0 <= col < 9:
                    if original_board[row][col] == 0:  # 元々の数字は変更不可
                        selected_cell = (row, col)
            
            elif event.type == pygame.KEYDOWN and selected_cell:
                row, col = selected_cell
                if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                    board[row][col] = 0
                elif event.unicode.isdigit() and event.unicode != '0':
                    board[row][col] = int(event.unicode)
                
                invalid_cells = check_board_validity(board)
                
                # 盤面が完成したかチェック
                if not invalid_cells and all(all(cell != 0 for cell in row) for row in board):
                    print("おめでとうございます！パズルが完成しました！")
                    running = False
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()