import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import mmap

class LargeTextViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("大容量テキストビューア")
        self.root.geometry("800x600")

        # ファイル関連の変数
        self.current_file = None
        self.mm = None  # メモリマップトファイル
        self.line_positions = []  # 各行の開始位置
        self.total_lines = 0
        self.lines_per_page = 1000  # 1度に表示する行数
        self.current_start_line = 0

        self.setup_ui()

    def setup_ui(self):
        # ツールバー
        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(fill="x", pady=5)
        
        ttk.Button(self.toolbar, text="ファイルを開く", command=self.open_file).pack(side="left", padx=5)
        
        # スクロール可能なテキストエリア
        self.text_frame = ttk.Frame(self.root)
        self.text_frame.pack(fill="both", expand=True)

        self.text_area = tk.Text(self.text_frame, wrap=tk.NONE)
        self.y_scrollbar = ttk.Scrollbar(self.text_frame, orient="vertical")
        self.x_scrollbar = ttk.Scrollbar(self.root, orient="horizontal")

        self.text_area.config(yscrollcommand=self.y_scrollbar.set,
                            xscrollcommand=self.x_scrollbar.set)
        self.y_scrollbar.config(command=self.custom_yview)
        self.x_scrollbar.config(command=self.text_area.xview)

        self.y_scrollbar.pack(side="right", fill="y")
        self.text_area.pack(side="left", fill="both", expand=True)
        self.x_scrollbar.pack(fill="x")

        # ステータスバー
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var)
        self.status_bar.pack(fill="x", side="bottom")

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("テキストファイル", "*.txt"), ("すべてのファイル", "*.*")]
        )
        if file_path:
            try:
                # 既存のファイルをクローズ
                if self.current_file:
                    self.current_file.close()
                if self.mm:
                    self.mm.close()

                # 新しいファイルを開く
                self.current_file = open(file_path, 'rb')
                self.mm = mmap.mmap(self.current_file.fileno(), 0, access=mmap.ACCESS_READ)
                
                # ファイルサイズを表示
                file_size = os.path.getsize(file_path)
                self.status_var.set(f"ファイルサイズ: {file_size / (1024*1024):.2f} MB")

                # 行位置をインデックス化（最初の部分のみ）
                self.index_initial_lines()
                
                # 最初の部分を表示
                self.load_page(0)

            except Exception as e:
                messagebox.showerror("エラー", f"ファイルを開けませんでした: {str(e)}")

    def index_initial_lines(self):
        """最初の部分の行位置をインデックス化"""
        self.line_positions = [0]
        self.mm.seek(0)
        
        # 最初の10000行をインデックス化
        for _ in range(10000):
            line = self.mm.readline()
            if not line:
                break
            self.line_positions.append(self.mm.tell())
        
        self.total_lines = len(self.line_positions)

    def load_page(self, start_line):
        """指定された行から一定数の行を読み込んで表示"""
        if not self.mm:
            return

        self.text_area.delete(1.0, tk.END)
        
        try:
            # 指定された行位置にシーク
            if start_line < len(self.line_positions):
                self.mm.seek(self.line_positions[start_line])
            
            # 指定された行数分だけ読み込んで表示
            for _ in range(self.lines_per_page):
                line = self.mm.readline()
                if not line:
                    break
                try:
                    # バイナリデータをテキストにデコード
                    self.text_area.insert(tk.END, line.decode('utf-8'))
                except UnicodeDecodeError:
                    self.text_area.insert(tk.END, "[デコードエラー]\n")

            self.current_start_line = start_line
            
        except Exception as e:
            print(f"読み込みエラー: {str(e)}")

    def custom_yview(self, *args):
        """カスタムスクロール処理"""
        if not self.mm:
            return
        
        if args[0] == "moveto":
            # スクロール位置から表示すべき行を計算
            fraction = float(args[1])
            target_line = int(fraction * self.total_lines)
            self.load_page(target_line)
        
        elif args[0] == "scroll":
            units = int(args[1])
            if args[2] == "units":  # 1行単位のスクロール
                target_line = self.current_start_line + units
            else:  # ページ単位のスクロール
                target_line = self.current_start_line + (units * self.lines_per_page)
            
            target_line = max(0, min(target_line, self.total_lines - self.lines_per_page))
            self.load_page(target_line)

        # スクロールバーの位置を更新
        if self.total_lines > 0:
            fraction = self.current_start_line / self.total_lines
            self.y_scrollbar.set(fraction, fraction + (self.lines_per_page/self.total_lines))

if __name__ == "__main__":
    root = tk.Tk()
    app = LargeTextViewer(root)
    root.mainloop()