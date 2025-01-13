import os
import tkinter as tk
from tkinter import filedialog, ttk

class FileRenameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ファイル名一括変更")
        
        # メインフレーム
        self.main_frame = ttk.Frame(root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # フォルダツリー部分
        self.tree_frame = ttk.LabelFrame(self.main_frame, text="フォルダ", padding=10)
        self.tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,5))
        
        self.folder_tree = ttk.Treeview(self.tree_frame)
        self.folder_tree.pack(fill=tk.BOTH, expand=True)
        
        # フォルダツリーのスクロールバー
        tree_scroll = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.folder_tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.folder_tree.configure(yscrollcommand=tree_scroll.set)
        
        # ファイル一覧表示部分
        self.files_frame = ttk.LabelFrame(self.main_frame, text="ファイル一覧", padding=10)
        self.files_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.files_listbox = tk.Listbox(self.files_frame, width=50, height=20)
        self.files_listbox.pack(fill=tk.BOTH, expand=True)
        
        # ファイルリストのスクロールバー
        files_scroll = ttk.Scrollbar(self.files_frame, orient="vertical", command=self.files_listbox.yview)
        files_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.files_listbox.configure(yscrollcommand=files_scroll.set)

        # ファイル名入力部分
        self.name_frame = ttk.Frame(root, padding=10)
        self.name_frame.pack(fill=tk.X)
        
        ttk.Label(self.name_frame, text="新しいファイル名:").pack(side=tk.LEFT)
        self.new_name = tk.StringVar()
        ttk.Entry(self.name_frame, textvariable=self.new_name, width=30).pack(side=tk.LEFT, padx=5)
        
        # 実行ボタン
        ttk.Button(root, text="実行", command=self.rename_files).pack(pady=10)

        # フォルダツリーの初期化
        self.init_folder_tree()
        
        # フォルダ選択時のイベントバインド
        self.folder_tree.bind('<<TreeviewSelect>>', self.on_folder_select)
        # フォルダ展開時のイベントバインド
        self.folder_tree.bind('<<TreeviewOpen>>', self.on_folder_open)

    def init_folder_tree(self):
        # ルートフォルダを取得
        for drive in self.get_drives():
            self.folder_tree.insert('', 'end', drive, text=drive)
            self.load_subitems(drive)

    def get_drives(self):
        if os.name == 'nt':  # Windows
            from ctypes import windll
            drives = []
            bitmask = windll.kernel32.GetLogicalDrives()
            for letter in range(65, 91):  # A-Z
                if bitmask & 1:
                    drives.append(chr(letter) + ":")
                bitmask >>= 1
            return drives
        else:  # Unix/Linux/Mac
            return ['/']

    def load_subitems(self, parent):
        path = self.folder_tree.item(parent)['text']
        try:
            # 既存の子アイテムを削除
            for child in self.folder_tree.get_children(parent):
                self.folder_tree.delete(child)
                
            dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) and not d.startswith('.')]
            for d in sorted(dirs):
                full_path = os.path.join(path, d)
                item_id = self.folder_tree.insert(parent, 'end', text=full_path)
                
                # サブフォルダの存在確認
                try:
                    has_subdirs = any(os.path.isdir(os.path.join(full_path, sd)) for sd in os.listdir(full_path) if not sd.startswith('.'))
                    if has_subdirs:
                        # ダミーアイテムを挿入
                        self.folder_tree.insert(item_id, 'end', text='dummy')
                except:
                    pass
        except:
            pass

    def on_folder_open(self, event):
        item = self.folder_tree.focus()
        self.load_subitems(item)

    def on_folder_select(self, event):
        selected_item = self.folder_tree.selection()[0]
        folder_path = self.folder_tree.item(selected_item)['text']
        self.update_file_list(folder_path)

    def update_file_list(self, folder_path):
        self.files_listbox.delete(0, tk.END)  # リストをクリア
        
        try:
            # 隠しファイルと一時ファイルを除外
            files = [f for f in os.listdir(folder_path) 
                    if not f.startswith('.') and not f.startswith('~$')]
            for filename in sorted(files):
                self.files_listbox.insert(tk.END, filename)
        except Exception as e:
            print(f'ファイル一覧の取得に失敗しました: {str(e)}')

    def rename_files(self):
        selected_item = self.folder_tree.selection()[0]
        folder_path = self.folder_tree.item(selected_item)['text']
        new_name_base = self.new_name.get()
        
        try:
            # 隠しファイルと一時ファイルを除外
            files = [f for f in os.listdir(folder_path) 
                    if not f.startswith('.') and not f.startswith('~$')]
            for i, filename in enumerate(sorted(files), 1):
                # 拡張子を取得
                _, ext = os.path.splitext(filename)
                # 新しいファイル名を作成（001形式の連番）
                new_filename = f"{new_name_base}{i:03d}{ext}"
                
                old_filepath = os.path.join(folder_path, filename)
                new_filepath = os.path.join(folder_path, new_filename)
                
                # ファイル名を変更
                os.rename(old_filepath, new_filepath)
                print(f'変更完了: {filename} → {new_filename}')
            
            # ファイル名変更後にリストを更新
            self.update_file_list(folder_path)
        except Exception as e:
            print(f'エラーが発生しました: {str(e)}')

# 使用例
if __name__ == "__main__":
    root = tk.Tk()
    app = FileRenameApp(root)
    root.mainloop()