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