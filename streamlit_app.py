<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Arduino温湿度監視システム</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #2c3e50, #34495e);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-left: 10px;
            animation: pulse 2s infinite;
        }
        
        .status-connected {
            background-color: #2ecc71;
        }
        
        .status-disconnected {
            background-color: #e74c3c;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            padding: 30px;
        }
        
        .sensor-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            border-left: 5px solid #3498db;
            transition: transform 0.3s ease;
        }
        
        .sensor-card:hover {
            transform: translateY(-2px);
        }
        
        .sensor-card h3 {
            font-size: 1.2rem;
            margin-bottom: 15px;
            color: #2c3e50;
        }
        
        .sensor-value {
            font-size: 3rem;
            font-weight: bold;
            color: #3498db;
            margin: 10px 0;
        }
        
        .sensor-unit {
            font-size: 1.2rem;
            color: #7f8c8d;
            margin-left: 5px;
        }
        
        .discomfort-card {
            grid-column: 1 / -1;
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            text-align: center;
        }
        
        .discomfort-index {
            font-size: 4rem;
            font-weight: bold;
            margin: 20px 0;
        }
        
        .comfort-level {
            font-size: 1.5rem;
            font-weight: bold;
            margin: 10px 0;
            padding: 10px 20px;
            border-radius: 25px;
            display: inline-block;
        }
        
        .level-comfortable {
            background: #d5f4e6;
            color: #27ae60;
            border-left-color: #27ae60;
        }
        
        .level-slightly-uncomfortable {
            background: #fef9e7;
            color: #f39c12;
            border-left-color: #f39c12;
        }
        
        .level-uncomfortable {
            background: #fadbd8;
            color: #e74c3c;
            border-left-color: #e74c3c;
        }
        
        .level-very-uncomfortable {
            background: #f4cccc;
            color: #c0392b;
            border-left-color: #c0392b;
        }
        
        .alert-section {
            grid-column: 1 / -1;
            margin-top: 20px;
        }
        
        .alert {
            padding: 15px 20px;
            border-radius: 8px;
            margin: 10px 0;
            font-weight: bold;
            text-align: center;
            display: none;
        }
        
        .alert-warning {
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }
        
        .alert-danger {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            animation: alertPulse 1s infinite;
        }
        
        @keyframes alertPulse {
            0% { background: #f8d7da; }
            50% { background: #ffcccb; }
            100% { background: #f8d7da; }
        }
        
        .controls {
            grid-column: 1 / -1;
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            margin-top: 20px;
        }
        
        .control-group {
            display: flex;
            align-items: center;
            margin: 15px 0;
            gap: 15px;
        }
        
        .control-group label {
            min-width: 120px;
            font-weight: bold;
        }
        
        .control-group input {
            padding: 8px 12px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }
        
        .btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s ease;
        }
        
        .btn:hover {
            background: #2980b9;
        }
        
        .chart-container {
            grid-column: 1 / -1;
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            margin-top: 20px;
        }
        
        .chart {
            width: 100%;
            height: 300px;
            border: 1px solid #ddd;
            border-radius: 6px;
            position: relative;
            background: #f8f9fa;
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
                gap: 20px;
                padding: 20px;
            }
            
            .sensor-value {
                font-size: 2rem;
            }
            
            .discomfort-index {
                font-size: 2.5rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Arduino温湿度監視システム</h1>
            <p>リアルタイム不快指数アラート
                <span id="connectionStatus" class="status-indicator status-disconnected"></span>
            </p>
        </div>
        
        <div class="main-content">
            <div class="sensor-card">
                <h3>🌡️ 気温</h3>
                <div class="sensor-value" id="temperature">--<span class="sensor-unit">°C</span></div>
                <p>最終更新: <span id="tempLastUpdate">--:--</span></p>
            </div>
            
            <div class="sensor-card">
                <h3>💧 湿度</h3>
                <div class="sensor-value" id="humidity">--<span class="sensor-unit">%</span></div>
                <p>最終更新: <span id="humidityLastUpdate">--:--</span></p>
            </div>
            
            <div class="discomfort-card">
                <h3>😊 不快指数</h3>
                <div class="discomfort-index" id="discomfortIndex">--</div>
                <div class="comfort-level" id="comfortLevel">測定中...</div>
                <p>不快指数 = 0.81 × 気温 + 0.01 × 湿度 × (0.99 × 気温 - 14.3) + 46.3</p>
            </div>
            
            <div class="alert-section">
                <div class="alert alert-warning" id="warningAlert">
                    ⚠️ 警告: 不快指数が高めです（75以上）
                </div>
                <div class="alert alert-danger" id="dangerAlert">
                    🚨 危険: 非常に不快な環境です（80以上）
                </div>
            </div>
            
            <div class="controls">
                <h3>🎛️ アラート設定</h3>
                <div class="control-group">
                    <label>警告閾値:</label>
                    <input type="number" id="warningThreshold" value="75" min="60" max="90" step="0.1">
                    <span>（不快指数）</span>
                </div>
                <div class="control-group">
                    <label>危険閾値:</label>
                    <input type="number" id="dangerThreshold" value="80" min="70" max="95" step="0.1">
                    <span>（不快指数）</span>
                </div>
                <div class="control-group">
                    <label>更新間隔:</label>
                    <input type="number" id="updateInterval" value="2" min="1" max="60" step="1">
                    <span>秒</span>
                </div>
                <button class="btn" onclick="updateSettings()">設定を適用</button>
                <button class="btn" onclick="connectToArduino()">Arduinoに接続</button>
            </div>
            
            <div class="chart-container">
                <h3>📊 データ履歴</h3>
                <canvas class="chart" id="dataChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        // システム設定
        let config = {
            warningThreshold: 75,
            dangerThreshold: 80,
            updateInterval: 2000,
            serialPort: null,
            isConnected: false
        };

        // データ保存用配列
        let sensorData = {
            timestamps: [],
            temperatures: [],
            humidities: [],
            discomfortIndices: []
        };

        // DOM要素
        const elements = {
            temperature: document.getElementById('temperature'),
            humidity: document.getElementById('humidity'),
            discomfortIndex: document.getElementById('discomfortIndex'),
            comfortLevel: document.getElementById('comfortLevel'),
            connectionStatus: document.getElementById('connectionStatus'),
            warningAlert: document.getElementById('warningAlert'),
            dangerAlert: document.getElementById('dangerAlert'),
            tempLastUpdate: document.getElementById('tempLastUpdate'),
            humidityLastUpdate: document.getElementById('humidityLastUpdate'),
            chart: document.getElementById('dataChart')
        };

        // 不快指数計算関数
        function calculateDiscomfortIndex(temp, humidity) {
            // 不快指数の計算式: DI = 0.81T + 0.01H(0.99T - 14.3) + 46.3
            const di = 0.81 * temp + 0.01 * humidity * (0.99 * temp - 14.3) + 46.3;
            return Math.round(di * 10) / 10;
        }

        // 快適レベル判定
        function getComfortLevel(discomfortIndex) {
            if (discomfortIndex < 70) {
                return { level: '快適', class: 'level-comfortable' };
            } else if (discomfortIndex < 75) {
                return { level: 'やや暑い', class: 'level-slightly-uncomfortable' };
            } else if (discomfortIndex < 80) {
                return { level: '暑くて汗が出る', class: 'level-uncomfortable' };
            } else {
                return { level: '暑くてたまらない', class: 'level-very-uncomfortable' };
            }
        }

        // データ更新関数
        function updateSensorData(temperature, humidity) {
            const now = new Date();
            const timeString = now.toLocaleTimeString();
            
            // 不快指数計算
            const discomfortIndex = calculateDiscomfortIndex(temperature, humidity);
            const comfort = getComfortLevel(discomfortIndex);

            // UI更新
            elements.temperature.innerHTML = `${temperature}<span class="sensor-unit">°C</span>`;
            elements.humidity.innerHTML = `${humidity}<span class="sensor-unit">%</span>`;
            elements.discomfortIndex.textContent = discomfortIndex;
            elements.tempLastUpdate.textContent = timeString;
            elements.humidityLastUpdate.textContent = timeString;

            // 快適レベル更新
            elements.comfortLevel.textContent = comfort.level;
            elements.comfortLevel.className = `comfort-level ${comfort.class}`;
            elements.discomfortIndex.className = `discomfort-index ${comfort.class.replace('level-', '')}`;

            // アラート処理
            checkAlerts(discomfortIndex);

            // データ履歴に追加
            addToHistory(now, temperature, humidity, discomfortIndex);

            // チャート更新
            updateChart();
        }

        // アラートチェック
        function checkAlerts(discomfortIndex) {
            elements.warningAlert.style.display = 'none';
            elements.dangerAlert.style.display = 'none';

            if (discomfortIndex >= config.dangerThreshold) {
                elements.dangerAlert.style.display = 'block';
                playAlertSound('danger');
            } else if (discomfortIndex >= config.warningThreshold) {
                elements.warningAlert.style.display = 'block';
                playAlertSound('warning');
            }
        }

        // アラート音再生
        function playAlertSound(type) {
            // Web Audio APIを使用したアラート音生成
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);

            oscillator.frequency.setValueAtTime(type === 'danger' ? 800 : 600, audioContext.currentTime);
            oscillator.type = 'sine';

            gainNode.gain.setValueAtTime(0, audioContext.currentTime);
            gainNode.gain.linearRampToValueAtTime(0.3, audioContext.currentTime + 0.1);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        }

        // データ履歴に追加
        function addToHistory(timestamp, temp, humidity, di) {
            sensorData.timestamps.push(timestamp);
            sensorData.temperatures.push(temp);
            sensorData.humidities.push(humidity);
            sensorData.discomfortIndices.push(di);

            // 最大100データポイントを保持
            if (sensorData.timestamps.length > 100) {
                sensorData.timestamps.shift();
                sensorData.temperatures.shift();
                sensorData.humidities.shift();
                sensorData.discomfortIndices.shift();
            }
        }

        // チャート更新（簡易実装）
        function updateChart() {
            const canvas = elements.chart;
            const ctx = canvas.getContext('2d');
            const width = canvas.offsetWidth;
            const height = canvas.offsetHeight;
            
            canvas.width = width;
            canvas.height = height;

            // チャートクリア
            ctx.clearRect(0, 0, width, height);
            ctx.fillStyle = '#f8f9fa';
            ctx.fillRect(0, 0, width, height);

            if (sensorData.timestamps.length < 2) return;

            // グリッド描画
            ctx.strokeStyle = '#dee2e6';
            ctx.lineWidth = 1;
            for (let i = 0; i <= 5; i++) {
                const y = (height / 5) * i;
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(width, y);
                ctx.stroke();
            }

            // 温度ライン
            ctx.strokeStyle = '#e74c3c';
            ctx.lineWidth = 2;
            ctx.beginPath();
            sensorData.temperatures.forEach((temp, i) => {
                const x = (width / (sensorData.temperatures.length - 1)) * i;
                const y = height - ((temp - 15) / 25) * height;
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            });
            ctx.stroke();

            // 不快指数ライン
            ctx.strokeStyle = '#3498db';
            ctx.lineWidth = 2;
            ctx.beginPath();
            sensorData.discomfortIndices.forEach((di, i) => {
                const x = (width / (sensorData.discomfortIndices.length - 1)) * i;
                const y = height - ((di - 50) / 40) * height;
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            });
            ctx.stroke();

            // 凡例
            ctx.fillStyle = '#e74c3c';
            ctx.fillRect(10, 10, 20, 10);
            ctx.fillStyle = '#333';
            ctx.font = '12px Arial';
            ctx.fillText('温度 (°C)', 35, 20);

            ctx.fillStyle = '#3498db';
            ctx.fillRect(10, 25, 20, 10);
            ctx.fillStyle = '#333';
            ctx.fillText('不快指数', 35, 35);
        }

        // Arduino接続（シミュレーション）
        async function connectToArduino() {
            try {
                // Web Serial APIが利用可能かチェック
                if ('serial' in navigator) {
                    config.serialPort = await navigator.serial.requestPort();
                    await config.serialPort.open({ baudRate: 9600 });
                    
                    config.isConnected = true;
                    elements.connectionStatus.className = 'status-indicator status-connected';
                    
                    // データ読み取り開始
                    readArduinoData();
                } else {
                    // Web Serial APIが利用できない場合は模擬データ
                    startSimulation();
                }
            } catch (error) {
                console.log('Arduino接続をシミュレーションで開始');
                startSimulation();
            }
        }

        // Arduinoからのデータ読み取り
        async function readArduinoData() {
            const textDecoder = new TextDecoderStream();
            const readableStreamClosed = config.serialPort.readable.pipeTo(textDecoder.writable);
            const reader = textDecoder.readable.getReader();

            try {
                while (true) {
                    const { value, done } = await reader.read();
                    if (done) break;
                    
                    // データパース（フォーマット: "TEMP:25.6,HUM:60.2"）
                    const match = value.match(/TEMP:([\d.]+),HUM:([\d.]+)/);
                    if (match) {
                        const temp = parseFloat(match[1]);
                        const humidity = parseFloat(match[2]);
                        updateSensorData(temp, humidity);
                    }
                }
            } catch (error) {
                console.error('データ読み取りエラー:', error);
            }
        }

        // シミュレーション開始
        function startSimulation() {
            config.isConnected = true;
            elements.connectionStatus.className = 'status-indicator status-connected';
            
            setInterval(() => {
                // 模擬データ生成
                const baseTemp = 25 + Math.sin(Date.now() / 10000) * 10;
                const baseHumidity = 60 + Math.cos(Date.now() / 8000) * 20;
                
                const temp = Math.round((baseTemp + (Math.random() - 0.5) * 2) * 10) / 10;
                const humidity = Math.round((baseHumidity + (Math.random() - 0.5) * 5) * 10) / 10;
                
                updateSensorData(temp, humidity);
            }, config.updateInterval);
        }

        // 設定更新
        function updateSettings() {
            config.warningThreshold = parseFloat(document.getElementById('warningThreshold').value);
            config.dangerThreshold = parseFloat(document.getElementById('dangerThreshold').value);
            config.updateInterval = parseInt(document.getElementById('updateInterval').value) * 1000;
            
            alert('設定を更新しました');
        }

        // 初期化
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Arduino温湿度監視システム初期化完了');
            
            // 自動接続開始
            setTimeout(() => {
                connectToArduino();
            }, 1000);
        });
    </script>
</body>
</html>