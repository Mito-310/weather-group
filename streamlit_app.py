import streamlit as st
import time
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import math

# ページ設定
st.set_page_config(
    page_title="Arduino温湿度監視システム",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# HTMLテンプレートをStreamlitで表示
html_content = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Arduino温湿度監視システム</title>
    <style>
        .sensor-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 5px solid #3498db;
            margin-bottom: 1rem;
            text-align: center;
        }
        
        .big-number {
            font-size: 3rem;
            font-weight: bold;
            color: #3498db;
            margin: 1rem 0;
        }
        
        .alert-warning {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        
        .alert-danger {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
    </style>
</head>
<body>
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; color: white; text-align: center; margin-bottom: 2rem;">
        <h1>🌡️ Arduino温湿度監視システム</h1>
        <p>リアルタイム不快指数アラート</p>
    </div>
</body>
</html>
"""

# セッション状態の初期化
if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = {
        'timestamp': [],
        'temperature': [],
        'humidity': [],
        'discomfort_index': []
    }

if 'is_connected' not in st.session_state:
    st.session_state.is_connected = False

if 'warning_threshold' not in st.session_state:
    st.session_state.warning_threshold = 75

if 'danger_threshold' not in st.session_state:
    st.session_state.danger_threshold = 80

# 関数定義
def calculate_discomfort_index(temp, humidity):
    """不快指数を計算する関数"""
    di = 0.81 * temp + 0.01 * humidity * (0.99 * temp - 14.3) + 46.3
    return round(di, 1)

def get_comfort_level(discomfort_index):
    """快適レベルを判定する関数"""
    if discomfort_index < 70:
        return "快適", "#27ae60"
    elif discomfort_index < 75:
        return "やや暑い", "#f39c12"
    elif discomfort_index < 80:
        return "暑くて汗が出る", "#e74c3c"
    else:
        return "暑くてたまらない", "#c0392b"

def generate_mock_data():
    """模擬データを生成する関数"""
    current_time = datetime.now()
    base_temp = 25 + math.sin(time.time() / 100) * 10
    base_humidity = 60 + math.cos(time.time() / 80) * 20
    
    temp = round(base_temp + random.uniform(-2, 2), 1)
    humidity = round(max(20, min(90, base_humidity + random.uniform(-5, 5))), 1)
    
    return current_time, temp, humidity

def add_data_point(timestamp, temp, humidity):
    """データポイントを追加する関数"""
    di = calculate_discomfort_index(temp, humidity)
    
    st.session_state.sensor_data['timestamp'].append(timestamp)
    st.session_state.sensor_data['temperature'].append(temp)
    st.session_state.sensor_data['humidity'].append(humidity)
    st.session_state.sensor_data['discomfort_index'].append(di)
    
    # 最新100件のデータのみ保持
    if len(st.session_state.sensor_data['timestamp']) > 100:
        for key in st.session_state.sensor_data:
            st.session_state.sensor_data[key] = st.session_state.sensor_data[key][-100:]

# ヘッダー表示
st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; color: white; text-align: center; margin-bottom: 2rem;">
    <h1>🌡️ Arduino温湿度監視システム</h1>
    <p>リアルタイム不快指数アラート</p>
</div>
""", unsafe_allow_html=True)

# サイドバー設定
with st.sidebar:
    st.header("⚙️ 設定")
    
    # 接続制御
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔌 接続開始", type="primary"):
            st.session_state.is_connected = True
            st.success("接続しました！")
    
    with col2:
        if st.button("🔌 接続停止"):
            st.session_state.is_connected = False
            st.info("接続を停止しました")
    
    # 接続状態表示
    if st.session_state.is_connected:
        st.success("🟢 接続中")
    else:
        st.error("🔴 未接続")
    
    st.divider()
    
    # アラート設定
    st.subheader("🚨 アラート設定")
    st.session_state.warning_threshold = st.slider(
        "警告閾値", 60, 90, st.session_state.warning_threshold, 0.1
    )
    st.session_state.danger_threshold = st.slider(
        "危険閾値", 70, 95, st.session_state.danger_threshold, 0.1
    )
    
    st.divider()
    
    # データクリア
    if st.button("🗑️ データクリア"):
        for key in st.session_state.sensor_data:
            st.session_state.sensor_data[key] = []
        st.success("データをクリアしました")

# メインコンテンツ
if st.session_state.is_connected:
    # 模擬データ生成
    timestamp, temp, humidity = generate_mock_data()
    add_data_point(timestamp, temp, humidity)

# 最新データ表示
if st.session_state.sensor_data['timestamp']:
    latest_temp = st.session_state.sensor_data['temperature'][-1]
    latest_humidity = st.session_state.sensor_data['humidity'][-1]
    latest_di = st.session_state.sensor_data['discomfort_index'][-1]
    latest_time = st.session_state.sensor_data['timestamp'][-1]
    
    comfort_level, comfort_color = get_comfort_level(latest_di)
    
    # センサーデータ表示
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="sensor-card">
            <h3>🌡️ 気温</h3>
            <div class="big-number" style="color: #e74c3c;">
                {latest_temp}°C
            </div>
            <p style="color: #666;">
                最終更新: {latest_time.strftime("%H:%M:%S")}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="sensor-card">
            <h3>💧 湿度</h3>
            <div class="big-number" style="color: #3498db;">
                {latest_humidity}%
            </div>
            <p style="color: #666;">
                最終更新: {latest_time.strftime("%H:%M:%S")}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="sensor-card">
            <h3>😊 不快指数</h3>
            <div class="big-number" style="color: {comfort_color};">
                {latest_di}
            </div>
            <div style="background: {comfort_color}; color: white; padding: 0.5rem; border-radius: 25px; margin: 1rem 0;">
                <strong>{comfort_level}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # アラート表示
    if latest_di >= st.session_state.danger_threshold:
        st.markdown(f"""
        <div class="alert-danger">
            🚨 <strong>危険:</strong> 非常に不快な環境です（{st.session_state.danger_threshold}以上）
        </div>
        """, unsafe_allow_html=True)
    elif latest_di >= st.session_state.warning_threshold:
        st.markdown(f"""
        <div class="alert-warning">
            ⚠️ <strong>警告:</strong> 不快指数が高めです（{st.session_state.warning_threshold}以上）
        </div>
        """, unsafe_allow_html=True)
    
    # グラフ表示
    if len(st.session_state.sensor_data['timestamp']) > 1:
        st.subheader("📊 データ履歴")
        
        # データフレーム作成
        df = pd.DataFrame({
            '時刻': st.session_state.sensor_data['timestamp'],
            '気温(°C)': st.session_state.sensor_data['temperature'],
            '湿度(%)': st.session_state.sensor_data['humidity'],
            '不快指数': st.session_state.sensor_data['discomfort_index']
        })
        
        # 時系列グラフ
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['時刻'], y=df['気温(°C)'],
            mode='lines+markers',
            name='気温(°C)',
            line=dict(color='#e74c3c', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['時刻'], y=df['湿度(%)'],
            mode='lines+markers',
            name='湿度(%)',
            line=dict(color='#3498db', width=2),
            yaxis='y2'
        ))
        
        fig.add_trace(go.Scatter(
            x=df['時刻'], y=df['不快指数'],
            mode='lines+markers',
            name='不快指数',
            line=dict(color='#9b59b6', width=3),
            yaxis='y3'
        ))
        
        # 警告・危険ライン
        fig.add_hline(
            y=st.session_state.warning_threshold,
            line_dash="dash",
            line_color="#f39c12",
            annotation_text="警告ライン"
        )
        
        fig.add_hline(
            y=st.session_state.danger_threshold,
            line_dash="dash",
            line_color="#e74c3c",
            annotation_text="危険ライン"
        )
        
        fig.update_layout(
            title="センサーデータ時系列グラフ",
            xaxis_title="時刻",
            yaxis=dict(title="気温(°C) / 不快指数"),
            yaxis2=dict(title="湿度(%)", side="right", overlaying="y"),
            height=500,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # データテーブル
        st.subheader("📋 最新データ")
        st.dataframe(df.tail(10).iloc[::-1], use_container_width=True)

else:
    st.info("🔌 「接続開始」ボタンを押してデータ取得を開始してください")

# 数式表示
st.subheader("📐 不快指数計算式")
st.latex(r"DI = 0.81 \times T + 0.01 \times H \times (0.99 \times T - 14.3) + 46.3")
st.caption("T: 気温(°C), H: 湿度(%), DI: 不快指数")

# 自動更新
if st.session_state.is_connected:
    time.sleep(2)
    st.rerun()