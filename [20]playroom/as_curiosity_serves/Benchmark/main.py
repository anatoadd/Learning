import psutil
import GPUtil
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import threading
import time
import numpy as np
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class BenchmarkMonitor:
    def __init__(self):
        try:
            self.monitoring = False
            self.data = {
                'timestamp': [],
                'cpu_usage': [],
                'cpu_freq': [],
                'cpu_temp': [],  # CPU温度を追加
                'memory_usage': [],
                'memory_available': [],
                'memory_speed': [],
                'gpu_usage': [], 
                'gpu_memory': [],
                'gpu_temp': [],
                'gpu_clock': [],
                'frame_size': [], # フレームサイズを追加
                'frame_rate': []  # フレームレートを追加
            }
            
            # システム情報の取得
            self.system_info = {
                'cpu_name': self._get_cpu_name(),
                'memory_info': self._get_memory_info(),
                'gpu_name': self._get_gpu_name()
            }
            
            # UIの初期化
            self.root = tk.Tk()
            self.root.title("ベンチマークモニター")
            
            # メインフレーム
            self.main_frame = ttk.Frame(self.root, padding="10")
            self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # コントロールボタン
            self.start_button = ttk.Button(self.main_frame, text="開始", command=self.start_monitoring)
            self.start_button.grid(row=0, column=0, padx=5)
            
            self.stop_button = ttk.Button(self.main_frame, text="停止", command=self.stop_monitoring)
            self.stop_button.grid(row=0, column=1, padx=5)
            
            # グラフ表示用のキャンバス
            plt.style.use('dark_background')  # グラフのスタイルを設定
            self.fig, (self.ax1, self.ax2, self.ax3, self.ax4) = plt.subplots(4, 1, figsize=(10, 10))
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
            self.canvas.get_tk_widget().grid(row=1, column=0, columnspan=2, pady=10)
            
            # 数値表示用のラベル
            self.info_frame = ttk.LabelFrame(self.main_frame, text="システム情報", padding="5")
            self.info_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
            
            self.cpu_label = ttk.Label(self.info_frame, text="CPU使用率: ---%")
            self.cpu_label.grid(row=0, column=0, padx=5)
            
            self.cpu_temp_label = ttk.Label(self.info_frame, text="CPU温度: ---°C")
            self.cpu_temp_label.grid(row=0, column=1, padx=5)
            
            self.memory_label = ttk.Label(self.info_frame, text="メモリ使用率: ---%")
            self.memory_label.grid(row=0, column=2, padx=5)
            
            self.gpu_label = ttk.Label(self.info_frame, text="GPU使用率: ---%")
            self.gpu_label.grid(row=0, column=3, padx=5)
            
            self.frame_label = ttk.Label(self.info_frame, text="フレームサイズ: --- MB")
            self.frame_label.grid(row=1, column=0, padx=5)
            
            self.fps_label = ttk.Label(self.info_frame, text="フレームレート: --- FPS")
            self.fps_label.grid(row=1, column=1, padx=5)

            # ウィンドウサイズの調整を許可
            self.root.resizable(True, True)
            
            # ウィンドウの最小サイズを設定
            self.root.minsize(800, 600)

        except Exception as e:
            print(f"初期化エラー: {str(e)}")
            raise

    def _get_cpu_name(self):
        try:
            import cpuinfo
            return cpuinfo.get_cpu_info()['brand_raw']
        except:
            return "Unknown CPU"

    def _get_memory_info(self):
        memory = psutil.virtual_memory()
        return f"{memory.total / (1024**3):.1f}GB"

    def _get_gpu_name(self):
        try:
            gpu = GPUtil.getGPUs()[0]
            return gpu.name
        except:
            return "Unknown GPU"

    def start_monitoring(self):
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True  # メインスレッド終了時に監視スレッドも終了
        self.monitor_thread.start()

    def stop_monitoring(self):
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join()
        self.save_results()

    def _monitor_loop(self):
        while self.monitoring:
            try:
                # システム情報の取得
                timestamp = datetime.now()
                
                # CPU情報
                cpu_freq = psutil.cpu_freq()
                cpu_usage = psutil.cpu_percent(percpu=True)
                
                # CPU温度の取得
                try:
                    temps = psutil.sensors_temperatures()
                    if 'coretemp' in temps:
                        cpu_temp = temps['coretemp'][0].current
                    else:
                        cpu_temp = 0
                except:
                    cpu_temp = 0
                
                # メモリ情報
                memory = psutil.virtual_memory()
                swap = psutil.swap_memory()
                
                # GPU情報
                gpu = GPUtil.getGPUs()[0]

                # フレーム情報の取得（サンプル値）
                frame_size = np.random.normal(50, 5)  # 平均50MB、標準偏差5MBのサンプルデータ
                frame_rate = np.random.normal(60, 2)  # 平均60FPS、標準偏差2FPSのサンプルデータ

                # データの保存
                self.data['timestamp'].append(timestamp)
                
                # CPU詳細データ
                cpu_usage_avg = np.mean(cpu_usage)
                self.data['cpu_usage'].append(cpu_usage_avg)
                self.data['cpu_freq'].append(cpu_freq.current)
                self.data['cpu_temp'].append(cpu_temp)
                
                # メモリ詳細データ
                self.data['memory_usage'].append(memory.percent)
                self.data['memory_available'].append(memory.available / (1024 * 1024 * 1024))
                self.data['memory_speed'].append(swap.used / (1024 * 1024))
                
                # GPU詳細データ
                gpu_usage = gpu.load * 100
                self.data['gpu_usage'].append(gpu_usage)
                self.data['gpu_memory'].append(gpu.memoryUsed)
                self.data['gpu_temp'].append(gpu.temperature)
                # GPUクロック情報は利用できないため0を設定
                self.data['gpu_clock'].append(0)
                
                # フレーム詳細データ
                self.data['frame_size'].append(frame_size)
                self.data['frame_rate'].append(frame_rate)

                # UI更新
                self.root.after(0, self._update_ui, cpu_usage_avg, cpu_temp, memory.percent, gpu_usage, frame_size, frame_rate)
                
                time.sleep(1)
            except Exception as e:
                print(f"モニタリングエラー: {str(e)}")
                time.sleep(1)

    def _update_ui(self, cpu_usage, cpu_temp, memory_usage, gpu_usage, frame_size, frame_rate):
        try:
            # ラベル更新
            self.cpu_label.config(text=f"CPU使用率: {cpu_usage:.1f}%")
            self.cpu_temp_label.config(text=f"CPU温度: {cpu_temp:.1f}°C")
            self.memory_label.config(text=f"メモリ使用率: {memory_usage:.1f}%")
            self.gpu_label.config(text=f"GPU使用率: {gpu_usage:.1f}%")
            self.frame_label.config(text=f"フレームサイズ: {frame_size:.1f} MB")
            self.fps_label.config(text=f"フレームレート: {frame_rate:.1f} FPS")
            
            # グラフ更新
            self._update_graphs()
        except Exception as e:
            print(f"UI更新エラー: {str(e)}")
        
    def _update_graphs(self):
        try:
            if len(self.data['timestamp']) > 0:
                self.ax1.clear()
                self.ax2.clear()
                self.ax3.clear()
                self.ax4.clear()
                
                # 直近30点のデータを表示
                display_points = 30
                start_idx = max(0, len(self.data['timestamp']) - display_points)
                
                # CPU使用率と温度を同じグラフに表示
                self.ax1.plot(self.data['timestamp'][start_idx:], self.data['cpu_usage'][start_idx:], label='使用率')
                self.ax1.plot(self.data['timestamp'][start_idx:], self.data['cpu_temp'][start_idx:], label='温度')
                self.ax1.set_title('CPU状態')
                self.ax1.legend()
                
                self.ax2.plot(self.data['timestamp'][start_idx:], self.data['memory_usage'][start_idx:])
                self.ax2.set_title('メモリ使用率 (%)')
                
                self.ax3.plot(self.data['timestamp'][start_idx:], self.data['gpu_usage'][start_idx:])
                self.ax3.set_title('GPU使用率 (%)')
                
                # フレーム情報のグラフを追加
                self.ax4.plot(self.data['timestamp'][start_idx:], self.data['frame_size'][start_idx:], label='フレームサイズ(MB)')
                self.ax4.plot(self.data['timestamp'][start_idx:], self.data['frame_rate'][start_idx:], label='FPS')
                self.ax4.set_title('フレーム情報')
                self.ax4.legend()
                
                self.fig.autofmt_xdate()
                self.canvas.draw()
        except Exception as e:
            print(f"グラフ更新エラー: {str(e)}")

    def save_results(self):
        """モニタリング結果を保存するメソッド"""
        try:
            df = pd.DataFrame(self.data)
            df.to_csv(f'benchmark_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv', index=False)
        except Exception as e:
            print(f"結果保存エラー: {str(e)}")

    def run(self):
        """UIを起動し、メインループを開始するメソッド"""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"実行エラー: {str(e)}")
            raise

# クラスのインスタンス化と実行
if __name__ == "__main__":
    try:
        monitor = BenchmarkMonitor()
        monitor.run()
    except Exception as e:
        print(f"アプリケーション起動エラー: {str(e)}")