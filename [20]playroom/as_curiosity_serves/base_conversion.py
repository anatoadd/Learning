import tkinter as tk
from tkinter import ttk

class BaseConverter:
    def __init__(self):
        # メインウィンドウの設定
        self.root = tk.Tk()
        self.root.title("基数変換プログラム")
        self.root.geometry("400x300")

        # 入力フレーム
        input_frame = ttk.LabelFrame(self.root, text="入力", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # 入力数値の基数選択
        ttk.Label(input_frame, text="入力の基数:").grid(row=0, column=0, padx=5)
        self.input_base = ttk.Combobox(input_frame, values=["2進数", "10進数", "16進数"], state="readonly")
        self.input_base.set("10進数")
        self.input_base.grid(row=0, column=1, padx=5)

        # 数値入力
        ttk.Label(input_frame, text="数値:").grid(row=1, column=0, padx=5, pady=5)
        self.input_number = ttk.Entry(input_frame)
        self.input_number.grid(row=1, column=1, padx=5, pady=5)

        # 変換先の基数選択
        ttk.Label(input_frame, text="変換先の基数:").grid(row=2, column=0, padx=5)
        self.output_base = ttk.Combobox(input_frame, values=["2進数", "10進数", "16進数"], state="readonly")
        self.output_base.set("2進数")
        self.output_base.grid(row=2, column=1, padx=5)

        # 変換ボタン
        convert_button = ttk.Button(self.root, text="変換", command=self.convert)
        convert_button.pack(pady=10)

        # 結果表示フレーム
        result_frame = ttk.LabelFrame(self.root, text="結果", padding=10)
        result_frame.pack(fill="x", padx=10, pady=5)

        self.result_label = ttk.Label(result_frame, text="")
        self.result_label.pack()

    def convert(self):
        try:
            # 入力値の取得
            input_str = self.input_number.get()
            input_base_str = self.input_base.get()
            output_base_str = self.output_base.get()

            # 入力基数の決定
            if input_base_str == "2進数":
                input_base = 2
            elif input_base_str == "10進数":
                input_base = 10
            else:  # 16進数
                input_base = 16

            # 10進数への変換
            if input_base == 10:
                decimal_num = int(input_str)
            else:
                decimal_num = int(input_str, input_base)

            # 出力基数への変換
            if output_base_str == "2進数":
                result = bin(decimal_num)[2:]  # "0b"を除去
            elif output_base_str == "10進数":
                result = str(decimal_num)
            else:  # 16進数
                result = hex(decimal_num)[2:].upper()  # "0x"を除去し大文字に

            self.result_label.config(text=f"変換結果: {result}")

        except ValueError:
            self.result_label.config(text="無効な入力です")

if __name__ == "__main__":
    app = BaseConverter()
    app.root.mainloop()
