"""
LINE通知モジュール
不快指数に応じた警告メッセージをLINEで送信する
"""
import os
from typing import Optional
from datetime import datetime
from linebot import LineBotApi
from linebot.models import TextSendMessage, FlexSendMessage
from linebot.exceptions import LineBotApiError


class LineNotifier:
    """LINE通知クラス"""

    def __init__(self, channel_access_token: Optional[str] = None, user_id: Optional[str] = None):
        """
        初期化

        Args:
            channel_access_token: LINEチャネルアクセストークン（省略時は環境変数から取得）
            user_id: 送信先のLINEユーザーID（省略時は環境変数から取得）
        """
        self.channel_access_token = channel_access_token or os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
        self.user_id = user_id or os.getenv('LINE_USER_ID')

        if not self.channel_access_token:
            raise ValueError("LINE_CHANNEL_ACCESS_TOKENが設定されていません")
        if not self.user_id:
            raise ValueError("LINE_USER_IDが設定されていません")

        self.line_bot_api = LineBotApi(self.channel_access_token)
        self.last_sent_level = None  # 連続送信防止用

    def send_discomfort_alert(self, temperature: float, humidity: float,
                             discomfort_index: float, wbgt: float,
                             risk_level: str, risk_info: dict) -> bool:
        """
        不快指数に応じた警告メッセージを送信

        Args:
            temperature: 気温（℃）
            humidity: 湿度（%）
            discomfort_index: 不快指数
            wbgt: WBGT（暑さ指数）
            risk_level: リスクレベル（'caution', 'warning', 'severe_warning', 'danger'）
            risk_info: リスク情報の辞書

        Returns:
            送信成功時はTrue、失敗時はFalse
        """
        # 警告レベル以下は送信しない
        if risk_level not in ['warning', 'severe_warning', 'danger']:
            return False

        # 同じレベルの連続送信を防止
        if self.last_sent_level == risk_level:
            return False

        try:
            # Flexメッセージを作成
            flex_message = self._create_flex_message(
                temperature, humidity, discomfort_index, wbgt,
                risk_level, risk_info
            )

            # メッセージを送信
            self.line_bot_api.push_message(
                self.user_id,
                flex_message
            )

            self.last_sent_level = risk_level
            return True

        except LineBotApiError as e:
            print(f"LINE送信エラー: {e}")
            return False
        except Exception as e:
            print(f"予期しないエラー: {e}")
            return False

    def _create_flex_message(self, temperature: float, humidity: float,
                            discomfort_index: float, wbgt: float,
                            risk_level: str, risk_info: dict) -> FlexSendMessage:
        """
        Flexメッセージを作成

        Args:
            temperature: 気温
            humidity: 湿度
            discomfort_index: 不快指数
            wbgt: WBGT
            risk_level: リスクレベル
            risk_info: リスク情報

        Returns:
            FlexSendMessage
        """
        # アイコンの選択
        icon_map = {
            'warning': '⚠️',
            'severe_warning': '🚨',
            'danger': '🆘'
        }
        icon = icon_map.get(risk_level, '⚠️')

        # 現在時刻
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Flexメッセージのコンテンツ
        flex_content = {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"{icon} 熱中症警告",
                        "weight": "bold",
                        "size": "xl",
                        "color": "#ffffff"
                    }
                ],
                "backgroundColor": risk_info['color']
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": risk_info['label'],
                        "weight": "bold",
                        "size": "xxl",
                        "color": risk_info['color'],
                        "align": "center",
                        "margin": "md"
                    },
                    {
                        "type": "separator",
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "🌡️ 気温",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 2
                                    },
                                    {
                                        "type": "text",
                                        "text": f"{temperature}°C",
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "md",
                                        "flex": 3,
                                        "weight": "bold"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "💧 湿度",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 2
                                    },
                                    {
                                        "type": "text",
                                        "text": f"{humidity}%",
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "md",
                                        "flex": 3,
                                        "weight": "bold"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "😓 不快指数",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 2
                                    },
                                    {
                                        "type": "text",
                                        "text": f"{discomfort_index}",
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "md",
                                        "flex": 3,
                                        "weight": "bold"
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "🥵 WBGT",
                                        "color": "#aaaaaa",
                                        "size": "sm",
                                        "flex": 2
                                    },
                                    {
                                        "type": "text",
                                        "text": f"{wbgt}°C",
                                        "wrap": True,
                                        "color": "#666666",
                                        "size": "md",
                                        "flex": 3,
                                        "weight": "bold"
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "separator",
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "contents": [
                            {
                                "type": "text",
                                "text": "💡 推奨対策",
                                "size": "sm",
                                "color": "#aaaaaa",
                                "weight": "bold"
                            },
                            {
                                "type": "text",
                                "text": risk_info['advice'],
                                "size": "md",
                                "wrap": True,
                                "color": "#666666",
                                "margin": "sm"
                            }
                        ]
                    },
                    {
                        "type": "separator",
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "contents": [
                            {
                                "type": "text",
                                "text": "⚠️ 注意事項",
                                "size": "sm",
                                "color": "#aaaaaa",
                                "weight": "bold"
                            },
                            {
                                "type": "text",
                                "text": self._get_precautions(risk_level),
                                "size": "sm",
                                "wrap": True,
                                "color": "#666666",
                                "margin": "sm"
                            }
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"測定時刻: {now}",
                        "size": "xs",
                        "color": "#aaaaaa",
                        "align": "center"
                    }
                ]
            }
        }

        return FlexSendMessage(
            alt_text=f"{icon} 熱中症警告: {risk_info['label']}",
            contents=flex_content
        )

    def _get_precautions(self, risk_level: str) -> str:
        """
        リスクレベルに応じた注意事項を取得

        Args:
            risk_level: リスクレベル

        Returns:
            注意事項のテキスト
        """
        precautions = {
            'warning': '・こまめな水分・塩分補給\n・適度な休憩をとる\n・体調の変化に注意',
            'severe_warning': '・激しい運動は中止\n・15-20分ごとに水分補給\n・涼しい場所で休憩\n・体調不良時は医療機関へ',
            'danger': '・外出を控える\n・冷房の効いた室内へ\n・緊急時は119番通報\n・高齢者や子供は特に注意'
        }
        return precautions.get(risk_level, '・こまめな水分補給を心がけましょう')

    def send_simple_message(self, message: str) -> bool:
        """
        シンプルなテキストメッセージを送信

        Args:
            message: 送信するメッセージ

        Returns:
            送信成功時はTrue、失敗時はFalse
        """
        try:
            self.line_bot_api.push_message(
                self.user_id,
                TextSendMessage(text=message)
            )
            return True
        except LineBotApiError as e:
            print(f"LINE送信エラー: {e}")
            return False
        except Exception as e:
            print(f"予期しないエラー: {e}")
            return False

    def reset_last_sent_level(self):
        """最後に送信したレベルをリセット（テスト用）"""
        self.last_sent_level = None
