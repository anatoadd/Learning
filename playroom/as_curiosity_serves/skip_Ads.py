#　調整中

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

    # ... 残りのコードは同じ ...