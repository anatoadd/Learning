#　広告スキッパー調整中

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.edge.options import Options
import time

class YoutubeAdSkipper:
    def __init__(self):
        # Edgeオプションの設定
        edge_options = Options()
        edge_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        try:
            # 既存のEdgeセッションに接続
            self.driver = webdriver.Edge(options=edge_options)
            self.wait = WebDriverWait(self.driver, 10)
            print("既存のEdgeブラウザに接続しました")
        except Exception as e:
            print("接続エラー:", e)
            print("Edgeを以下のコマンドで起動してください：")
            print('msedge.exe --remote-debugging-port=9222')
            exit(1)

    def skip_ads(self):
        while True:
            try:
                # 広告スキップボタンを探す
                skip_button = self.wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ytp-ad-skip-button"))
                )
                # スキップボタンが見つかったらクリック
                skip_button.click()
                print("広告をスキップしました")
            except TimeoutException:
                # スキップボタンが見つからない場合は継続
                pass
            time.sleep(1)  # CPU負荷軽減のため1秒待機

    def run(self):
        try:
            print("広告スキッパーを起動しました。終了するにはCtrl+Cを押してください。")
            self.skip_ads()
        except KeyboardInterrupt:
            print("\n広告スキッパーを終了します")