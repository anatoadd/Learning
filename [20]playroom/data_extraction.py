import pandas as pd
import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

class DataExtractionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("エクセルデータ抽出ツール")
        
        # 入力フォルダ選択部分
        self.input_frame = ttk.LabelFrame(root, text="入力設定", padding=10)
        self.input_frame.pack(fill="x", padx=10, pady=5)
        
        self.input_path = tk.StringVar()
        ttk.Label(self.input_frame, text="入力フォルダ:").pack(anchor="w")
        input_entry = ttk.Entry(self.input_frame, textvariable=self.input_path, width=50)
        input_entry.pack(side="left", padx=5)
        ttk.Button(self.input_frame, text="参照", command=self.select_input_folder).pack(side="left")

        # 出力フォルダ選択部分
        self.output_frame = ttk.LabelFrame(root, text="出力設定", padding=10)
        self.output_frame.pack(fill="x", padx=10, pady=5)
        
        self.output_path = tk.StringVar()
        ttk.Label(self.output_frame, text="出力フォルダ:").pack(anchor="w")
        output_entry = ttk.Entry(self.output_frame, textvariable=self.output_path, width=50)
        output_entry.pack(side="left", padx=5)
        ttk.Button(self.output_frame, text="参照", command=self.select_output_folder).pack(side="left")

        # 抽出条件入力部分
        self.criteria_frame = ttk.LabelFrame(root, text="抽出条件", padding=10)
        self.criteria_frame.pack(fill="x", padx=10, pady=5)
        
        # 行検索条件
        row_frame = ttk.Frame(self.criteria_frame)
        row_frame.pack(fill="x", pady=2)
        ttk.Label(row_frame, text="行の条件:").pack(side="left")
        self.row_type = tk.StringVar(value="number")
        ttk.Radiobutton(row_frame, text="番号指定", variable=self.row_type, value="number").pack(side="left")
        ttk.Radiobutton(row_frame, text="テキスト検索", variable=self.row_type, value="text").pack(side="left")
        self.row_criteria = tk.StringVar()
        ttk.Entry(row_frame, textvariable=self.row_criteria, width=30).pack(side="left", padx=5)
        
        # 列検索条件
        col_frame = ttk.Frame(self.criteria_frame)
        col_frame.pack(fill="x", pady=2)
        ttk.Label(col_frame, text="列の条件:").pack(side="left")
        self.col_type = tk.StringVar(value="number")
        ttk.Radiobutton(col_frame, text="番号指定", variable=self.col_type, value="number").pack(side="left")
        ttk.Radiobutton(col_frame, text="列名(A,B,C...)", variable=self.col_type, value="letter").pack(side="left")
        ttk.Radiobutton(col_frame, text="テキスト検索", variable=self.col_type, value="text").pack(side="left")
        self.col_criteria = tk.StringVar()
        ttk.Entry(col_frame, textvariable=self.col_criteria, width=30).pack(side="left", padx=5)
        
        # 実行ボタン
        ttk.Button(root, text="実行", command=self.execute_extraction).pack(pady=10)

    def select_input_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_path.set(folder)

    def select_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_path.set(folder)

    def parse_number_criteria(self, criteria_str):
        if not criteria_str:
            return None
        try:
            return [int(x.strip()) - 1 for x in criteria_str.split(',')]
        except ValueError:
            return None

    def parse_letter_criteria(self, criteria_str):
        if not criteria_str:
            return None
        try:
            def letter_to_number(letter):
                return sum((ord(c.upper()) - ord('A') + 1) * (26 ** i)
                         for i, c in enumerate(reversed(letter))) - 1
            return [letter_to_number(x.strip()) for x in criteria_str.split(',')]
        except ValueError:
            return None

    def execute_extraction(self):
        input_folder = self.input_path.get()
        output_folder = self.output_path.get()
        
        if not input_folder or not output_folder:
            messagebox.showerror("エラー", "入力フォルダと出力フォルダを指定してください")
            return
            
        row_type = self.row_type.get()
        col_type = self.col_type.get()
        row_criteria = self.row_criteria.get()
        col_criteria = self.col_criteria.get()

        try:
            self.extract_data_from_excel(
                input_folder, output_folder,
                row_type, row_criteria,
                col_type, col_criteria
            )
            messagebox.showinfo("完了", "データ抽出が完了しました")
        except Exception as e:
            messagebox.showerror("エラー", f"処理中にエラーが発生しました: {str(e)}")

    def extract_data_from_excel(self, input_folder, output_folder, 
                              row_type, row_criteria, col_type, col_criteria):
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        
        excel_files = [f for f in os.listdir(input_folder) 
                      if f.endswith(('.xlsx', '.xls')) and not f.startswith('~$')]
        
        for file in excel_files:
            try:
                input_path = os.path.join(input_folder, file)
                df = pd.read_excel(input_path)
                extracted_df = df.copy()
                
                # 行の抽出
                if row_type == "number" and row_criteria:
                    row_indices = self.parse_number_criteria(row_criteria)
                    if row_indices is not None:
                        extracted_df = extracted_df.iloc[row_indices]
                elif row_type == "text" and row_criteria:
                    row_mask = extracted_df.astype(str).apply(
                        lambda x: x.str.contains(row_criteria, na=False)).any(axis=1)
                    extracted_df = extracted_df[row_mask]
                
                # 列の抽出
                if col_type == "number" and col_criteria:
                    col_indices = self.parse_number_criteria(col_criteria)
                    if col_indices is not None:
                        extracted_df = extracted_df.iloc[:, col_indices]
                elif col_type == "letter" and col_criteria:
                    col_indices = self.parse_letter_criteria(col_criteria)
                    if col_indices is not None:
                        extracted_df = extracted_df.iloc[:, col_indices]
                elif col_type == "text" and col_criteria:
                    col_mask = extracted_df.astype(str).apply(
                        lambda x: x.str.contains(col_criteria, na=False)).any()
                    extracted_df = extracted_df.loc[:, col_mask]
                
                output_filename = f"extracted_{file}"
                output_path = os.path.join(output_folder, output_filename)
                extracted_df.to_excel(output_path, index=False)
                
            except Exception as e:
                print(f"エラー ({file}): {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DataExtractionApp(root)
    root.mainloop()