import win32gui
import win32process
import psutil
import time
from ctypes import windll
import keyboard
import tkinter as tk
from tkinter import ttk, scrolledtext

class WindowInfoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ウィンドウ情報取得ツール")
        
        # メインフレーム
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 説明ラベル
        ttk.Label(main_frame, text="スペースキーを押すと、マウスカーソル位置のウィンドウ情報を取得します。").pack(pady=5)
        
        # プロセス監視設定
        monitor_frame = ttk.LabelFrame(main_frame, text="プロセス監視", padding=5)
        monitor_frame.pack(fill=tk.X, pady=5)
        
        self.target_pid = tk.StringVar()
        ttk.Label(monitor_frame, text="監視対象プロセスID:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(monitor_frame, textvariable=self.target_pid, width=10).pack(side=tk.LEFT, padx=5)
        self.monitor_button = ttk.Button(monitor_frame, text="監視開始", command=self.toggle_monitoring)
        self.monitor_button.pack(side=tk.LEFT, padx=5)
        
        # 情報表示エリア
        self.info_text = scrolledtext.ScrolledText(main_frame, height=15, width=60)
        self.info_text.pack(pady=5, fill=tk.BOTH, expand=True)
        
        # ボタン
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=5)
        
        ttk.Button(button_frame, text="情報取得", command=self.get_info).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="クリア", command=self.clear_info).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="終了", command=root.quit).pack(side=tk.LEFT, padx=5)
        
        # キーバインド
        self.root.bind('<space>', lambda e: self.get_info())
        self.root.bind('<Escape>', lambda e: root.quit())
        
        # 監視フラグ
        self.monitoring = False
        self.after_id = None

    def toggle_monitoring(self):
        if not self.monitoring:
            try:
                pid = int(self.target_pid.get())
                self.monitoring = True
                self.monitor_button.config(text="監視停止")
                self.monitor_process(pid)
            except ValueError:
                self.info_text.insert(tk.END, "有効なプロセスIDを入力してください。\n")
                self.info_text.see(tk.END)
        else:
            self.monitoring = False
            self.monitor_button.config(text="監視開始")
            if self.after_id:
                self.root.after_cancel(self.after_id)

    def monitor_process(self, pid):
        if not self.monitoring:
            return
            
        try:
            process = psutil.Process(pid)
            cpu_percent = process.cpu_percent()
            memory_info = process.memory_info()
            io_counters = process.io_counters()
            
            info_text = (
                "="*50 + "\n"
                f"時刻: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"CPU使用率: {cpu_percent}%\n"
                f"メモリ使用量: {memory_info.rss / 1024 / 1024:.2f} MB\n"
                f"読み込みバイト数: {io_counters.read_bytes}\n"
                f"書き込みバイト数: {io_counters.write_bytes}\n"
                + "="*50 + "\n\n"
            )
            
            self.info_text.insert(tk.END, info_text)
            self.info_text.see(tk.END)
            
        except psutil.NoSuchProcess:
            self.info_text.insert(tk.END, "プロセスが終了しました。\n")
            self.info_text.see(tk.END)
            self.monitoring = False
            self.monitor_button.config(text="監視開始")
            return
        except Exception as e:
            self.info_text.insert(tk.END, f"エラー: {str(e)}\n")
            self.info_text.see(tk.END)
        
        self.after_id = self.root.after(1000, lambda: self.monitor_process(pid))

    def get_info(self):
        info = get_window_info()
        if isinstance(info, dict):
            info_text = (
                "="*50 + "\n"
                f"ウィンドウタイトル: {info['window_title']}\n"
                f"プロセス名: {info['process_name']}\n"
                f"実行ファイルパス: {info['process_path']}\n"
                f"クラス名: {info['class_name']}\n"
                f"ウィンドウ位置: {info['window_rect']}\n"
                f"プロセスID: {info['process_id']}\n"
                + "="*50 + "\n\n"
            )
            self.info_text.insert(tk.END, info_text)
            self.info_text.see(tk.END)
            
            # プロセスIDを監視対象にセット
            self.target_pid.set(str(info['process_id']))
        else:
            self.info_text.insert(tk.END, f"エラー: {info}\n\n")
            self.info_text.see(tk.END)

    def clear_info(self):
        self.info_text.delete(1.0, tk.END)

def get_cursor_position():
    """マウスカーソルの位置を取得"""
    cursor = win32gui.GetCursorPos()
    return cursor

def get_window_info():
    """カーソル位置のウィンドウ情報を取得"""
    cursor_pos = get_cursor_position()
    window_handle = win32gui.WindowFromPoint(cursor_pos)
    
    try:
        # ウィンドウのタイトルを取得
        window_title = win32gui.GetWindowText(window_handle)
        
        # プロセスIDを取得
        _, process_id = win32process.GetWindowThreadProcessId(window_handle)
        
        # プロセス情報を取得
        process = psutil.Process(process_id)
        
        # ウィンドウのクラス名を取得
        class_name = win32gui.GetClassName(window_handle)
        
        # ウィンドウの位置とサイズを取得
        rect = win32gui.GetWindowRect(window_handle)
        
        return {
            'window_title': window_title,
            'process_name': process.name(),
            'process_path': process.exe(),
            'class_name': class_name,
            'window_rect': rect,
            'process_id': process_id
        }
    except Exception as e:
        return f"エラー: {str(e)}"

def main():
    # 必要なライブラリのインストール確認
    required_packages = ['pywin32', 'psutil', 'keyboard']
    
    try:
        import pip
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                print(f"{package}をインストールしています...")
                pip.main(['install', package])
        
        root = tk.Tk()
        app = WindowInfoApp(root)
        root.mainloop()
    except Exception as e:
        print(f"セットアップエラー: {str(e)}")

if __name__ == "__main__":
    main()