# LINE通知機能セットアップガイド

Arduino温湿度センサーから取得した不快指数に応じて、LINE公式アカウントから自動で警告通知を送る機能の設定方法を説明します。

## 📋 目次
1. [機能概要](#機能概要)
2. [LINE Messaging APIの設定](#line-messaging-apiの設定)
3. [環境変数の設定](#環境変数の設定)
4. [動作確認](#動作確認)
5. [トラブルシューティング](#トラブルシューティング)

---

## 🎯 機能概要

### 不快指数計算
気温と湿度から不快指数を自動計算し、以下の基準で警告レベルを判定します：

- **安全（DI < 70）**: 通常の活動が可能
- **注意（DI 70-75）**: こまめな水分補給を推奨
- **警戒（DI 75-80）**: 積極的な休憩と水分補給が必要 ⚠️ **LINE通知開始**
- **厳重警戒（DI 80-85）**: 激しい運動は避ける 🚨 **LINE通知**
- **危険（DI 85+）**: 外出・運動を控える 🆘 **LINE通知**

### LINE通知のタイミング
- 警戒レベル以上（DI ≥ 75 または WBGT ≥ 28）になった時
- 警告レベルが変化した時（例：警戒→厳重警戒）
- 同じレベルでの連続送信は防止

---

## 🔧 LINE Messaging APIの設定

### 1. LINE Developersコンソールでチャネル作成

1. [LINE Developers](https://developers.line.biz/ja/)にアクセス
2. 「ログイン」してプロバイダーを作成または選択
3. 「新規チャネル作成」をクリック
4. 「Messaging API」を選択
5. 必要事項を入力：
   - チャネル名: 例「熱中症警告システム」
   - チャネル説明: 任意
   - カテゴリ: 適切なものを選択
   - サブカテゴリ: 適切なものを選択

### 2. チャネルアクセストークン取得

1. 作成したチャネルの「Messaging API設定」タブを開く
2. 「チャネルアクセストークン（長期）」セクションで「発行」をクリック
3. 表示されたトークンをコピーして保存（後で使用）

### 3. Webhook設定（オプション）

- 「Webhook設定」で「Webhookの利用」をオフのままでOK（プッシュ通知のみ使用）

### 4. 応答メッセージ設定

1. 「Messaging API設定」タブで：
   - 「応答メッセージ」を「オフ」にする
   - 「あいさつメッセージ」は任意

### 5. 友だち追加とユーザーID取得

#### 方法1: QRコードで友だち追加
1. 「Messaging API設定」タブの「QRコード」をスマホで読み取り
2. LINE公式アカウントを友だち追加

#### 方法2: LINE IDで検索
1. 「Messaging API設定」タブの「LINE ID」をメモ
2. LINEアプリで検索して友だち追加

#### ユーザーIDの取得方法

**推奨方法: テストメッセージで確認**

以下のPythonスクリプトを使用：

```python
from linebot import LineBotApi
from linebot.models import TextSendMessage

# チャネルアクセストークンを設定
channel_access_token = 'YOUR_CHANNEL_ACCESS_TOKEN'
line_bot_api = LineBotApi(channel_access_token)

# ブロードキャストメッセージを送信（全友だちに送信）
line_bot_api.broadcast(TextSendMessage(text='テストメッセージ'))

# または、特定のイベントで取得する方法もあります
```

**別の方法: Webhook経由で取得**
1. チャネルの「Webhook設定」を有効化
2. WebhookのURLを設定（ngrokなどを使用）
3. LINEボットにメッセージを送信
4. Webhookイベントから `userId` を取得

---

## ⚙️ 環境変数の設定

### 1. `.env`ファイルの作成

プロジェクトルートに`.env`ファイルを作成します：

```bash
cp .env.example .env
```

### 2. `.env`ファイルを編集

```bash
# LINE Messaging API設定
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token_here
LINE_USER_ID=your_user_id_here

# 不快指数の警告閾値（オプション、デフォルト値があります）
# WARNING_THRESHOLD=80
# SEVERE_WARNING_THRESHOLD=85
# DANGER_THRESHOLD=90
```

**設定例**：
```bash
LINE_CHANNEL_ACCESS_TOKEN=abcdefghijklmnopqrstuvwxyz1234567890ABCD...
LINE_USER_ID=U1234567890abcdef1234567890abcdef
```

### 3. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

主要パッケージ：
- `line-bot-sdk`: LINE Messaging API SDK
- `python-dotenv`: 環境変数の読み込み
- `streamlit`: Webアプリフレームワーク

---

## ✅ 動作確認

### 1. Streamlitアプリの起動

```bash
streamlit run streamlit_app.py
```

### 2. LINE通知設定の確認

1. アプリのサイドバーで「📱 LINE通知」セクションを確認
2. **🟢 有効** と表示されていればOK
3. **🔴 無効** の場合は`.env`ファイルの設定を見直す

### 3. テスト通知の送信

1. サイドバーの「📨 テスト通知送信」ボタンをクリック
2. LINEに通知が届くことを確認

### 4. 実際の警告通知のテスト

1. 「🔌 監視開始」ボタンをクリック
2. 温湿度データがシミュレートされます
3. 不快指数が警戒レベル（DI ≥ 75）に達すると自動でLINE通知が送信されます

---

## 🔍 トラブルシューティング

### LINE通知が「🔴 無効」と表示される

**原因と対処法**：
1. `.env`ファイルが存在しない
   → プロジェクトルートに`.env`ファイルを作成
2. 環境変数が正しく設定されていない
   → `.env`ファイルの記述を確認（スペースや改行に注意）
3. アプリを再起動していない
   → Streamlitアプリを再起動（Ctrl+Cで停止後、再度`streamlit run`）

### テスト通知が送信されない

**確認項目**：
1. チャネルアクセストークンが正しいか
   → LINE Developersコンソールで再確認
2. ユーザーIDが正しいか
   → LINEボットを友だち追加しているか確認
3. エラーメッセージを確認
   → ターミナルに表示されるエラーログを確認

### 通知が届かない

**確認項目**：
1. LINEアプリで通知設定がオンになっているか
2. LINEボットをブロックしていないか
3. インターネット接続は正常か
4. チャネルが有効化されているか（LINE Developersコンソールで確認）

### 同じ通知が何度も届く

**原因**：
- セッション状態がリセットされている可能性があります

**対処法**：
- ブラウザをリフレッシュせずに使用する
- 「🗑️ 全データクリア」を実行してリセット

---

## 📱 Arduino実機との連携

現在はシミュレーションデータを使用していますが、実機のArduinoと連携する場合：

### 必要な変更点

1. **`generate_mock_data()`関数を実際のセンサー読み取り関数に置き換え**

```python
# 例: シリアル通信でArduinoからデータ取得
import serial

def read_arduino_data():
    """Arduinoから温湿度データを取得"""
    ser = serial.Serial('/dev/ttyUSB0', 9600)  # ポートは環境に応じて変更
    line = ser.readline().decode('utf-8').strip()
    temp, humidity = map(float, line.split(','))
    return datetime.now(), temp, humidity
```

2. **`streamlit_app.py`の該当箇所を修正**

```python
# 変更前
if st.session_state.is_connected:
    timestamp, temp, humidity = generate_mock_data()
    add_data_point(timestamp, temp, humidity)

# 変更後
if st.session_state.is_connected:
    timestamp, temp, humidity = read_arduino_data()
    add_data_point(timestamp, temp, humidity)
```

### Arduinoスケッチ例（DHT22センサー使用）

```cpp
#include <DHT.h>

#define DHTPIN 2
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
}

void loop() {
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  if (!isnan(humidity) && !isnan(temperature)) {
    Serial.print(temperature);
    Serial.print(",");
    Serial.println(humidity);
  }

  delay(2000);  // 2秒ごとに測定
}
```

---

## 📚 参考リンク

- [LINE Messaging API ドキュメント](https://developers.line.biz/ja/docs/messaging-api/)
- [line-bot-sdk-python GitHub](https://github.com/line/line-bot-sdk-python)
- [Streamlit ドキュメント](https://docs.streamlit.io/)

---

## 📝 ライセンスと注意事項

- LINE Messaging APIの利用規約に従ってください
- 無料プランでは月間メッセージ数に制限があります（プッシュメッセージ: 200通/月）
- 個人情報の取り扱いには十分注意してください
