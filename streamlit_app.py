import streamlit as st
import time
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import math
import os
from dotenv import load_dotenv
from line_notifier import LineNotifier

# 環境変数の読み込み
load_dotenv()

# ページ設定
st.set_page_config(
    page_title="熱中症対策温湿度監視システム",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# セッション状態の初期化
if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = {
        'timestamp': [],
        'temperature': [],
        'humidity': [],
        'discomfort_index': [],
        'wbgt': []  # 暑さ指数（WBGT）
    }

if 'is_connected' not in st.session_state:
    st.session_state.is_connected = False

if 'alert_history' not in st.session_state:
    st.session_state.alert_history = []

if 'line_notifier' not in st.session_state:
    # LINE Notifierの初期化（環境変数が設定されている場合のみ）
    try:
        if os.getenv('LINE_CHANNEL_ACCESS_TOKEN') and os.getenv('LINE_USER_ID'):
            st.session_state.line_notifier = LineNotifier()
            st.session_state.line_enabled = True
        else:
            st.session_state.line_notifier = None
            st.session_state.line_enabled = False
    except Exception as e:
        st.session_state.line_notifier = None
        st.session_state.line_enabled = False
        print(f"LINE通知の初期化エラー: {e}")

# 閾値設定（熱中症対策用）
HEATSTROKE_LEVELS = {
    'safe': {'di': 70, 'wbgt': 21, 'color': '#27ae60', 'label': '安全', 'advice': '通常の活動が可能です'},
    'caution': {'di': 75, 'wbgt': 25, 'color': '#f39c12', 'label': '注意', 'advice': 'こまめな水分補給を心がけましょう'},
    'warning': {'di': 80, 'wbgt': 28, 'color': '#e67e22', 'label': '警戒', 'advice': '積極的な休憩と水分・塩分補給が必要です'},
    'severe_warning': {'di': 85, 'wbgt': 31, 'color': '#e74c3c', 'label': '厳重警戒', 'advice': '激しい運動は避け、頻繁に休憩をとってください'},
    'danger': {'di': 90, 'wbgt': 35, 'color': '#c0392b', 'label': '危険', 'advice': '外出・運動を控え、涼しい場所で過ごしてください'}
}

# 関数定義
def calculate_discomfort_index(temp, humidity):
    """不快指数を計算"""
    di = 0.81 * temp + 0.01 * humidity * (0.99 * temp - 14.3) + 46.3
    return round(di, 1)

def calculate_wbgt(temp, humidity):
    """簡易WBGT（暑さ指数）を計算"""
    # 室内での簡易計算式
    wbgt = 0.567 * temp + 0.393 * (humidity / 100 * 6.105 * math.exp(17.27 * temp / (237.7 + temp))) + 3.94
    return round(wbgt, 1)

def get_heatstroke_risk(di, wbgt):
    """熱中症リスクレベルを判定"""
    if di >= HEATSTROKE_LEVELS['danger']['di'] or wbgt >= HEATSTROKE_LEVELS['danger']['wbgt']:
        return 'danger'
    elif di >= HEATSTROKE_LEVELS['severe_warning']['di'] or wbgt >= HEATSTROKE_LEVELS['severe_warning']['wbgt']:
        return 'severe_warning'
    elif di >= HEATSTROKE_LEVELS['warning']['di'] or wbgt >= HEATSTROKE_LEVELS['warning']['wbgt']:
        return 'warning'
    elif di >= HEATSTROKE_LEVELS['caution']['di'] or wbgt >= HEATSTROKE_LEVELS['caution']['wbgt']:
        return 'caution'
    else:
        return 'safe'

def get_hydration_recommendation(temp, humidity, activity_level='normal'):
    """推奨水分補給量を計算（ml/時間）"""
    base_amount = 200
    
    if temp > 30:
        base_amount += (temp - 30) * 20
    if humidity > 70:
        base_amount += (humidity - 70) * 5
    
    if activity_level == 'light':
        base_amount *= 1.2
    elif activity_level == 'moderate':
        base_amount *= 1.5
    elif activity_level == 'heavy':
        base_amount *= 2.0
    
    return int(base_amount)

def generate_mock_data():
    """模擬データを生成"""
    current_time = datetime.now()
    base_temp = 28 + math.sin(time.time() / 100) * 8
    base_humidity = 65 + math.cos(time.time() / 80) * 20
    
    temp = round(base_temp + random.uniform(-2, 2), 1)
    humidity = round(max(30, min(95, base_humidity + random.uniform(-5, 5))), 1)
    
    return current_time, temp, humidity

def add_data_point(timestamp, temp, humidity):
    """データポイントを追加"""
    di = calculate_discomfort_index(temp, humidity)
    wbgt = calculate_wbgt(temp, humidity)

    st.session_state.sensor_data['timestamp'].append(timestamp)
    st.session_state.sensor_data['temperature'].append(temp)
    st.session_state.sensor_data['humidity'].append(humidity)
    st.session_state.sensor_data['discomfort_index'].append(di)
    st.session_state.sensor_data['wbgt'].append(wbgt)

    # アラート履歴追加とLINE通知
    risk_level = get_heatstroke_risk(di, wbgt)
    if risk_level in ['warning', 'severe_warning', 'danger']:
        alert = {
            'timestamp': timestamp,
            'level': HEATSTROKE_LEVELS[risk_level]['label'],
            'di': di,
            'wbgt': wbgt,
            'temp': temp,
            'humidity': humidity
        }
        if not st.session_state.alert_history or st.session_state.alert_history[-1]['level'] != alert['level']:
            st.session_state.alert_history.append(alert)

            # LINE通知を送信
            if st.session_state.line_enabled and st.session_state.line_notifier:
                try:
                    success = st.session_state.line_notifier.send_discomfort_alert(
                        temperature=temp,
                        humidity=humidity,
                        discomfort_index=di,
                        wbgt=wbgt,
                        risk_level=risk_level,
                        risk_info=HEATSTROKE_LEVELS[risk_level]
                    )
                    if success:
                        print(f"LINE通知送信成功: {HEATSTROKE_LEVELS[risk_level]['label']}")
                except Exception as e:
                    print(f"LINE通知送信エラー: {e}")

    # 最新200件のデータのみ保持
    if len(st.session_state.sensor_data['timestamp']) > 200:
        for key in st.session_state.sensor_data:
            st.session_state.sensor_data[key] = st.session_state.sensor_data[key][-200:]

    # アラート履歴は最新50件
    if len(st.session_state.alert_history) > 50:
        st.session_state.alert_history = st.session_state.alert_history[-50:]

# カスタムCSS
st.markdown("""
<style>
    .sensor-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        text-align: center;
    }
    .big-number {
        font-size: 3rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    .risk-badge {
        padding: 0.5rem 1rem;
        border-radius: 25px;
        color: white;
        font-weight: bold;
        margin: 1rem 0;
        display: inline-block;
    }
    .alert-box {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid;
    }
</style>
""", unsafe_allow_html=True)

# ヘッダー表示
st.markdown("""
<div style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); padding: 1.5rem; border-radius: 10px; color: white; text-align: center; margin-bottom: 2rem;">
    <h1>🌡️ 熱中症対策温湿度監視システム</h1>
    <p>リアルタイム環境監視 × 不快指数・WBGT指標</p>
</div>
""", unsafe_allow_html=True)

# サイドバー設定
with st.sidebar:
    st.header("⚙️ システム設定")
    
    # 接続制御
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔌 監視開始", type="primary"):
            st.session_state.is_connected = True
            st.success("監視を開始しました！")
    
    with col2:
        if st.button("⏸️ 監視停止"):
            st.session_state.is_connected = False
            st.info("監視を停止しました")
    
    # 接続状態表示
    if st.session_state.is_connected:
        st.success("🟢 監視中")
    else:
        st.error("🔴 停止中")
    
    st.divider()
    
    # 活動レベル設定
    st.subheader("🏃 活動レベル")
    activity_level = st.select_slider(
        "現在の活動レベルを選択",
        options=['rest', 'light', 'normal', 'moderate', 'heavy'],
        value='normal',
        format_func=lambda x: {
            'rest': '🛋️ 安静',
            'light': '🚶 軽い活動',
            'normal': '🧑 通常',
            'moderate': '🏃 中程度の運動',
            'heavy': '💪 激しい運動'
        }[x]
    )
    
    st.divider()

    # LINE通知設定表示
    st.subheader("📱 LINE通知")
    if st.session_state.line_enabled:
        st.success("🟢 有効")
        st.caption("警告レベル以上で自動通知")
        if st.button("📨 テスト通知送信"):
            if st.session_state.line_notifier:
                success = st.session_state.line_notifier.send_simple_message(
                    "🔔 LINE通知のテストメッセージです。\n熱中症警告システムが正常に動作しています。"
                )
                if success:
                    st.success("テスト通知を送信しました！")
                else:
                    st.error("通知の送信に失敗しました")
    else:
        st.warning("🔴 無効")
        st.caption(".envファイルに設定を追加してください")
        with st.expander("📝 設定方法"):
            st.code("""
# .envファイルに以下を追加:
LINE_CHANNEL_ACCESS_TOKEN=your_token
LINE_USER_ID=your_user_id
            """)

    st.divider()

    # データクリア
    if st.button("🗑️ 全データクリア"):
        for key in st.session_state.sensor_data:
            st.session_state.sensor_data[key] = []
        st.session_state.alert_history = []
        # LINE通知のレベルもリセット
        if st.session_state.line_notifier:
            st.session_state.line_notifier.reset_last_sent_level()
        st.success("データをクリアしました")

# メインコンテンツ
if st.session_state.is_connected:
    timestamp, temp, humidity = generate_mock_data()
    add_data_point(timestamp, temp, humidity)

# 最新データ表示
if st.session_state.sensor_data['timestamp']:
    latest_temp = st.session_state.sensor_data['temperature'][-1]
    latest_humidity = st.session_state.sensor_data['humidity'][-1]
    latest_di = st.session_state.sensor_data['discomfort_index'][-1]
    latest_wbgt = st.session_state.sensor_data['wbgt'][-1]
    latest_time = st.session_state.sensor_data['timestamp'][-1]
    
    risk_level = get_heatstroke_risk(latest_di, latest_wbgt)
    risk_info = HEATSTROKE_LEVELS[risk_level]
    
    # 熱中症リスク表示（大きく目立つように）
    st.markdown(f"""
    <div style="background: {risk_info['color']}; padding: 2rem; border-radius: 15px; text-align: center; color: white; margin-bottom: 2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
        <h2 style="margin: 0; font-size: 2.5rem;">⚠️ 現在の熱中症リスク</h2>
        <h1 style="margin: 1rem 0; font-size: 4rem;">{risk_info['label']}</h1>
        <p style="font-size: 1.3rem; margin: 0;">{risk_info['advice']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # センサーデータ表示
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="sensor-card" style="border-left: 5px solid #e74c3c;">
            <h3>🌡️ 気温</h3>
            <div class="big-number" style="color: #e74c3c;">
                {latest_temp}°C
            </div>
            <p style="color: #666; font-size: 0.9rem;">
                {latest_time.strftime("%H:%M:%S")}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="sensor-card" style="border-left: 5px solid #3498db;">
            <h3>💧 湿度</h3>
            <div class="big-number" style="color: #3498db;">
                {latest_humidity}%
            </div>
            <p style="color: #666; font-size: 0.9rem;">
                {latest_time.strftime("%H:%M:%S")}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="sensor-card" style="border-left: 5px solid #9b59b6;">
            <h3>😓 不快指数</h3>
            <div class="big-number" style="color: #9b59b6;">
                {latest_di}
            </div>
            <p style="color: #666; font-size: 0.9rem;">
                (DI指標)
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="sensor-card" style="border-left: 5px solid #e67e22;">
            <h3>🥵 暑さ指数</h3>
            <div class="big-number" style="color: #e67e22;">
                {latest_wbgt}°C
            </div>
            <p style="color: #666; font-size: 0.9rem;">
                (WBGT)
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # 推奨事項表示
    st.subheader("💡 推奨対策")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        hydration = get_hydration_recommendation(latest_temp, latest_humidity, activity_level)
        st.info(f"""
        **💧 水分補給**  
        推奨量: **{hydration}ml/時間**  
        15-20分ごとにコップ1杯
        """)
    
    with col2:
        if risk_level in ['warning', 'severe_warning', 'danger']:
            st.warning(f"""
            **🏃 運動制限**  
            激しい運動は避けてください  
            こまめな休憩が必要です
            """)
        else:
            st.success(f"""
            **🏃 運動可能**  
            通常の活動が可能です  
            水分補給を忘れずに
            """)
    
    with col3:
        if risk_level in ['severe_warning', 'danger']:
            st.error(f"""
            **🌡️ 環境改善**  
            エアコン・扇風機使用推奨  
            涼しい場所へ移動してください
            """)
        elif risk_level == 'warning':
            st.warning(f"""
            **🌡️ 環境改善**  
            換気や冷房の使用を推奨  
            日陰で休憩しましょう
            """)
        else:
            st.info(f"""
            **🌡️ 快適な環境**  
            現在の環境は良好です  
            引き続き注意しましょう
            """)
    
    # グラフ表示
    if len(st.session_state.sensor_data['timestamp']) > 1:
        st.subheader("📊 環境データ推移")
        
        df = pd.DataFrame({
            '時刻': st.session_state.sensor_data['timestamp'],
            '気温(°C)': st.session_state.sensor_data['temperature'],
            '湿度(%)': st.session_state.sensor_data['humidity'],
            '不快指数': st.session_state.sensor_data['discomfort_index'],
            'WBGT(°C)': st.session_state.sensor_data['wbgt']
        })
        
        # タブで表示切り替え
        tab1, tab2, tab3 = st.tabs(["📈 総合グラフ", "🌡️ 温湿度グラフ", "⚠️ リスク指標グラフ"])
        
        with tab1:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df['時刻'], y=df['気温(°C)'],
                mode='lines+markers',
                name='気温(°C)',
                line=dict(color='#e74c3c', width=2),
                yaxis='y1'
            ))
            
            fig.add_trace(go.Scatter(
                x=df['時刻'], y=df['湿度(%)'],
                mode='lines+markers',
                name='湿度(%)',
                line=dict(color='#3498db', width=2),
                yaxis='y2'
            ))
            
            fig.update_layout(
                title="温度・湿度の推移",
                xaxis_title="時刻",
                yaxis=dict(title="気温(°C)", side="left"),
                yaxis2=dict(title="湿度(%)", side="right", overlaying="y"),
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            fig2 = px.scatter(df, x='気温(°C)', y='湿度(%)', 
                            color='WBGT(°C)',
                            size='不快指数',
                            color_continuous_scale='Reds',
                            title='気温と湿度の関係（色:WBGT、サイズ:不快指数）')
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)
        
        with tab3:
            fig3 = go.Figure()
            
            fig3.add_trace(go.Scatter(
                x=df['時刻'], y=df['不快指数'],
                mode='lines+markers',
                name='不快指数',
                line=dict(color='#9b59b6', width=3),
                fill='tozeroy'
            ))
            
            fig3.add_trace(go.Scatter(
                x=df['時刻'], y=df['WBGT(°C)'],
                mode='lines+markers',
                name='WBGT(°C)',
                line=dict(color='#e67e22', width=3),
                yaxis='y2'
            ))
            
            # 警戒ライン
            for level_name, level_data in HEATSTROKE_LEVELS.items():
                fig3.add_hline(
                    y=level_data['di'],
                    line_dash="dash",
                    line_color=level_data['color'],
                    annotation_text=f"DI:{level_data['label']}",
                    annotation_position="right"
                )
            
            fig3.update_layout(
                title="熱中症リスク指標の推移",
                xaxis_title="時刻",
                yaxis=dict(title="不快指数", side="left"),
                yaxis2=dict(title="WBGT(°C)", side="right", overlaying="y"),
                height=450,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig3, use_container_width=True)
        
        # 統計情報
        st.subheader("📊 統計情報（過去1時間）")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("平均気温", f"{df['気温(°C)'].mean():.1f}°C", 
                     f"{df['気温(°C)'].iloc[-1] - df['気温(°C)'].mean():.1f}°C")
        with col2:
            st.metric("平均湿度", f"{df['湿度(%)'].mean():.1f}%",
                     f"{df['湿度(%)'].iloc[-1] - df['湿度(%)'].mean():.1f}%")
        with col3:
            st.metric("平均不快指数", f"{df['不快指数'].mean():.1f}",
                     f"{df['不快指数'].iloc[-1] - df['不快指数'].mean():.1f}")
        with col4:
            st.metric("平均WBGT", f"{df['WBGT(°C)'].mean():.1f}°C",
                     f"{df['WBGT(°C)'].iloc[-1] - df['WBGT(°C)'].mean():.1f}°C")

    # アラート履歴
    if st.session_state.alert_history:
        with st.expander("🚨 アラート履歴", expanded=False):
            alert_df = pd.DataFrame(st.session_state.alert_history)
            alert_df['時刻'] = alert_df['timestamp'].apply(lambda x: x.strftime("%H:%M:%S"))
            st.dataframe(
                alert_df[['時刻', 'level', 'temp', 'humidity', 'di', 'wbgt']].rename(columns={
                    'level': 'レベル',
                    'temp': '気温',
                    'humidity': '湿度',
                    'di': '不快指数',
                    'wbgt': 'WBGT'
                }),
                use_container_width=True
            )

else:
    st.info("🔌 サイドバーの「監視開始」ボタンを押してデータ取得を開始してください")
    
    # 熱中症予防の基礎知識
    st.subheader("📚 熱中症予防の基礎知識")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🌡️ 不快指数（DI）とは
        気温と湿度から算出される体感的な暑さの指標
        
        - **70未満**: 快適
        - **70-75**: やや暑い
        - **75-80**: 暑くて汗が出る
        - **80-85**: 暑くてたまらない
        - **85以上**: 非常に危険
        """)
    
    with col2:
        st.markdown("""
        ### 🥵 WBGT（暑さ指数）とは
        熱中症予防の国際的な指標
        
        - **21未満**: 注意
        - **21-25**: 警戒
        - **25-28**: 厳重警戒
        - **28-31**: 危険
        - **31以上**: 極めて危険
        """)

# 計算式表示
with st.expander("📐 計算式の詳細"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 不快指数（DI）")
        st.latex(r"DI = 0.81 \times T + 0.01 \times H \times (0.99 \times T - 14.3) + 46.3")
        st.caption("T: 気温(°C), H: 湿度(%)")
    
    with col2:
        st.markdown("### WBGT（簡易版）")
        st.latex(r"WBGT = 0.567 \times T + 0.393 \times e + 3.94")
        st.caption("T: 気温(°C), e: 水蒸気圧")

# 自動更新
if st.session_state.is_connected:
    time.sleep(2)
    st.rerun()