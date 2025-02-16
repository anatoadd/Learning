#What day of the week is your birth?
from datetime import datetime

# ユーザーから入力を受け取る
birth_date_str = input("出生年月日を入力してください (例: YYYY-MM-DD): ")

# 入力を日付に変換
try:
    birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
    # 曜日を取得
    weekdays = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]
    weekday = weekdays[birth_date.weekday()]
    print(f"{birth_date_str} は {weekday} です。")
except ValueError:
    print("正しい形式で日付を入力してください (例: YYYY-MM-DD)。")