import os

# 画像ファイルが存在するディレクトリのパス
directory = ""# ファイルのアドレスを入力

# 対応するファイル拡張子
extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

# ディレクトリ内のファイルを取得し、指定の拡張子のもののみ対象にする
files = [f for f in os.listdir(directory) if os.path.splitext(f)[1].lower() in extensions]

# ファイルを順番にリネーム
for i, filename in enumerate(sorted(files), start=1):
    # 新しいファイル名を作成（例: 001.jpg）
    new_name = f"{i:03d}{os.path.splitext(filename)[1].lower()}"
    # 現在のファイルのフルパスと新しい名前のフルパスを取得
    old_file = os.path.join(directory, filename)
    new_file = os.path.join(directory, new_name)
    # ファイルをリネーム
    os.rename(old_file, new_file)

print("ファイルの名前が付け直されました。")
input("Press Enter to continue...")