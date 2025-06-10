# ui/main_window.py
import tkinter as tk
from logic.core import example_logic

def run_app():
    def on_button_click():
        result = example_logic()
        label.config(text=f"結果: {result}")

    root = tk.Tk()
    root.title("Python学習用サンドボックス")
    root.geometry("400x200")

    label = tk.Label(root, text="ただの試運転", font=("Arial", 16))
    label.pack(pady=20)

    button = tk.Button(root, text="ロジック実行", command=on_button_click)
    button.pack(pady=10)

    root.mainloop()
