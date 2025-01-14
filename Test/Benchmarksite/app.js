class BenchmarkViewer {
    constructor() {
        this.initializeApp();
        this.loadSystemInfo();
        this.setupEventListeners();
    }

    initializeApp() {
        // アプリケーションの初期化
        this.currentPage = 'system';
        this.charts = {};
        this.systemInfo = {};
    }

    async loadSystemInfo() {
        try {
            // Performance APIを使用してメモリ情報を取得
            const memory = performance.memory;
            // NavigatorのhardwareConcurrencyでCPUコア数を取得
            const cpuCores = navigator.hardwareConcurrency;

            const systemData = {
                cpu: {
                    model: "取得不可", // ブラウザからCPUモデル名は取得不可
                    cores: cpuCores,
                    threads: cpuCores,
                    speed: "取得不可", // クロック速度も取得不可
                    temperature: "取得不可" // 温度も取得不可
                },
                memory: {
                    total: `${Math.round(memory.jsHeapSizeLimit / (1024 * 1024))} MB`,
                    used: `${Math.round((memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100)}%`,
                    speed: "取得不可" // メモリ速度は取得不可
                },
                gpu: {
                    model: "取得不可", // GPUの詳細情報は取得不可
                    memory: "取得不可",
                    driver: "取得不可",
                    temperature: "取得不可"
                }
            };

            // WebGLを使用してGPU情報の一部を取得
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            if (gl) {
                const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                if (debugInfo) {
                    systemData.gpu.model = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
                }
            }

            this.updateSystemInfo(systemData);
        } catch (error) {
            console.error('システム情報の読み込みに失敗:', error);
        }
    }

    updateSystemInfo(data) {
        // システム情報の表示を更新
        const cpuInfo = document.querySelector('#cpu-info .info-content');
        const memoryInfo = document.querySelector('#memory-info .info-content');
        const gpuInfo = document.querySelector('#gpu-info .info-content');

        cpuInfo.innerHTML = `
            <p>モデル: ${data.cpu.model}</p>
            <p>コア数: ${data.cpu.cores}</p>
            <p>スレッド数: ${data.cpu.threads}</p>
            <p>クロック: ${data.cpu.speed}</p>
            <p>温度: ${data.cpu.temperature}</p>
        `;

        memoryInfo.innerHTML = `
            <p>総容量: ${data.memory.total}</p>
            <p>速度: ${data.memory.speed}</p>
            <p>使用率: ${data.memory.used}</p>
        `;

        gpuInfo.innerHTML = `
            <p>モデル: ${data.gpu.model}</p>
            <p>メモリ: ${data.gpu.memory}</p>
            <p>ドライバ: ${data.gpu.driver}</p>
            <p>温度: ${data.gpu.temperature}°C</p>
        `;
    }

    setupEventListeners() {
        // ナビゲーションのイベントリスナー設定
        document.querySelectorAll('nav a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = e.target.dataset.page;
                this.changePage(page);
            });
        });
    }

    changePage(page) {
        // ページ切り替え処理
        document.querySelectorAll('.page').forEach(p => p.style.display = 'none');
        document.getElementById(`${page}-page`).style.display = 'block';
        this.currentPage = page;

        if (page === 'benchmark') {
            this.initializeBenchmarkCharts();
        }
    }

    initializeBenchmarkCharts() {
        // ベンチマークチャートの初期化
        if (!this.charts.score) {
            const scoreCtx = document.getElementById('score-chart').getContext('2d');
            this.charts.score = new Chart(scoreCtx, {
                type: 'bar',
                data: {
                    labels: ['総合', 'CPU', 'GPU', 'メモリ', 'ストレージ'],
                    datasets: [{
                        label: 'ベンチマークスコア',
                        data: [85, 90, 82, 88, 78],
                        backgroundColor: '#3498db'
                    }]
                }
            });
        }
    }
}

// アプリケーションの起動
document.addEventListener('DOMContentLoaded', () => {
    const app = new BenchmarkViewer();
});