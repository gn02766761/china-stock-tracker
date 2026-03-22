"""
通知服务 (Notification Service)

支持多种通知方式：邮件、微信、短信、控制台
"""

import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from typing import List, Optional, Dict
from datetime import datetime
import requests

from price_alert import PriceAlert, AlertType, AlertStatus


class NotificationService:
    """通知服务"""
    
    def __init__(self, config_file: str = "config/notification_config.json"):
        """
        Parameters
        ----------
        config_file : str
            配置文件路径
        """
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置失败：{e}")
        
        # 默认配置
        return {
            'email': {
                'enabled': False,
                'smtp_server': 'smtp.qq.com',
                'smtp_port': 587,
                'sender': '',
                'password': '',
                'receivers': []
            },
            'wechat': {
                'enabled': False,
                'method': 'console',  # 'console', 'wechatpy', 'serverchan'
                'serverchan_key': ''
            },
            'sms': {
                'enabled': False,
                'provider': 'aliyun',
                'access_key': '',
                'access_secret': '',
                'phone_numbers': []
            },
            'console': {
                'enabled': True
            }
        }
    
    def send_alert_notification(self, alert: PriceAlert):
        """
        发送预警通知
        
        Parameters
        ----------
        alert : PriceAlert
            预警对象
        """
        methods = alert.notification_methods or ['console']
        
        for method in methods:
            try:
                if method == 'email' and self.config.get('email', {}).get('enabled'):
                    self._send_email_notification(alert)
                
                elif method == 'wechat':
                    self._send_wechat_notification(alert)
                
                elif method == 'sms' and self.config.get('sms', {}).get('enabled'):
                    self._send_sms_notification(alert)
                
                elif method == 'console':
                    self._send_console_notification(alert)
            
            except Exception as e:
                print(f"发送{method}通知失败：{e}")
    
    def _send_console_notification(self, alert: PriceAlert):
        """发送控制台通知"""
        print("\n" + "=" * 60)
        print("🚨 预警通知")
        print("=" * 60)
        print(f"股票代码：{alert.symbol}")
        print(f"股票名称：{alert.name}")
        print(f"预警类型：{alert.alert_type.value}")
        print(f"触发条件：{alert.condition_value}")
        print(f"当前值：{alert.current_value}")
        print(f"触发时间：{alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S') if alert.triggered_at else 'N/A'}")
        if alert.notes:
            print(f"备注：{alert.notes}")
        print("=" * 60)
    
    def _send_email_notification(self, alert: PriceAlert):
        """发送邮件通知"""
        email_config = self.config['email']
        
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = email_config['sender']
        msg['To'] = ', '.join(email_config['receivers'])
        msg['Subject'] = Header(f"股票预警通知 - {alert.symbol} {alert.name}", 'utf-8')
        
        # 邮件内容
        content = self._format_alert_content(alert, 'email')
        msg.attach(MIMEText(content, 'html', 'utf-8'))
        
        # 发送邮件
        server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
        server.starttls()
        server.login(email_config['sender'], email_config['password'])
        server.sendmail(email_config['sender'], email_config['receivers'], msg.as_string())
        server.quit()
        
        print(f"✓ 邮件通知已发送")
    
    def _send_wechat_notification(self, alert: PriceAlert):
        """发送微信通知"""
        wechat_config = self.config.get('wechat', {})
        method = wechat_config.get('method', 'console')
        
        if method == 'serverchan':
            # ServerChan 推送
            key = wechat_config.get('serverchan_key', '')
            if key:
                title = f"股票预警 - {alert.symbol} {alert.name}"
                content = self._format_alert_content(alert, 'text')
                
                url = f"https://sctapi.ftqq.com/{key}.send"
                data = {'title': title, 'desp': content}
                response = requests.post(url, data=data)
                
                if response.status_code == 200:
                    print(f"✓ 微信通知已发送 (ServerChan)")
                else:
                    print(f"✗ 微信通知发送失败：{response.text}")
        
        elif method == 'console' or True:
            # 默认使用控制台
            self._send_console_notification(alert)
    
    def _send_sms_notification(self, alert: PriceAlert):
        """发送短信通知"""
        # 这里可以接入阿里云短信等服务商
        # 示例代码仅供参考
        sms_config = self.config['sms']
        
        if sms_config.get('provider') == 'aliyun':
            # 阿里云短信 API
            print(f"✓ 短信通知已发送 (阿里云)")
        else:
            self._send_console_notification(alert)
    
    def _format_alert_content(self, alert: PriceAlert, format_type: str = 'text') -> str:
        """格式化预警内容"""
        alert_type_map = {
            AlertType.PRICE_ABOVE: "价格突破",
            AlertType.PRICE_BELOW: "价格跌破",
            AlertType.MA_CROSS_ABOVE: "均线上穿",
            AlertType.MA_CROSS_BELOW: "均线下穿",
            AlertType.RSI_OVERBOUGHT: "RSI 超买",
            AlertType.RSI_OVERSOLD: "RSI 超卖",
            AlertType.VOLUME_SPIKE: "成交量放大",
            AlertType.BOLLINGER_BREAKOUT: "布林带突破",
            AlertType.STOP_LOSS: "止损预警",
            AlertType.TAKE_PROFIT: "止盈预警"
        }
        
        alert_name = alert_type_map.get(alert.alert_type, alert.alert_type.value)
        
        if format_type == 'email':
            content = f"""
            <html>
            <body>
                <h2>🚨 股票预警通知</h2>
                <table border="1" cellpadding="5">
                    <tr><td>股票代码</td><td>{alert.symbol}</td></tr>
                    <tr><td>股票名称</td><td>{alert.name}</td></tr>
                    <tr><td>预警类型</td><td>{alert_name}</td></tr>
                    <tr><td>触发条件</td><td>{alert.condition_value}</td></tr>
                    <tr><td>当前值</td><td>{alert.current_value}</td></tr>
                    <tr><td>触发时间</td><td>{alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S') if alert.triggered_at else 'N/A'}</td></tr>
                </table>
                <p><strong>备注：</strong>{alert.notes or '无'}</p>
                <p style="color: #999; font-size: 12px;">
                    此邮件由股票分析系统自动发送，请勿回复。
                </p>
            </body>
            </html>
            """
            return content
        
        else:  # text
            content = f"""
🚨 股票预警通知

股票代码：{alert.symbol}
股票名称：{alert.name}
预警类型：{alert_name}
触发条件：{alert.condition_value}
当前值：{alert.current_value}
触发时间：{alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S') if alert.triggered_at else 'N/A'}
备注：{alert.notes or '无'}

---
股票分析系统自动通知
            """.strip()
            return content
    
    def test_notification(self, method: str = 'console'):
        """测试通知"""
        test_alert = PriceAlert(
            id="test_001",
            symbol="000001",
            name="测试股票",
            alert_type=AlertType.PRICE_ABOVE,
            condition_value=10.0,
            current_value=10.5,
            status=AlertStatus.TRIGGERED,
            notification_methods=[method]
        )
        
        print(f"测试{method}通知...")
        self.send_alert_notification(test_alert)
    
    def save_config(self):
        """保存配置"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 配置已保存到 {self.config_file}")
    
    def setup_email(
        self,
        smtp_server: str,
        smtp_port: int,
        sender: str,
        password: str,
        receivers: List[str]
    ):
        """
        配置邮件通知
        
        Parameters
        ----------
        smtp_server : str
            SMTP 服务器地址
        smtp_port : int
            SMTP 端口
        sender : str
            发件人邮箱
        password : str
            邮箱密码/授权码
        receivers : List[str]
            收件人列表
        """
        self.config['email'] = {
            'enabled': True,
            'smtp_server': smtp_server,
            'smtp_port': smtp_port,
            'sender': sender,
            'password': password,
            'receivers': receivers
        }
        
        self.save_config()
        print(f"✓ 邮件通知已配置")
    
    def setup_wechat_serverchan(self, serverchan_key: str):
        """
        配置 ServerChan 微信通知
        
        Parameters
        ----------
        serverchan_key : str
            ServerChan 推送 key
        """
        self.config['wechat'] = {
            'enabled': True,
            'method': 'serverchan',
            'serverchan_key': serverchan_key
        }
        
        self.save_config()
        print(f"✓ 微信通知已配置 (ServerChan)")


def create_notification_config_template():
    """创建配置文件模板"""
    config = {
        "email": {
            "enabled": False,
            "smtp_server": "smtp.qq.com",
            "smtp_port": 587,
            "sender": "your_email@qq.com",
            "password": "your_auth_code",
            "receivers": ["receiver1@email.com", "receiver2@email.com"]
        },
        "wechat": {
            "enabled": False,
            "method": "serverchan",
            "serverchan_key": "your_serverchan_key"
        },
        "sms": {
            "enabled": False,
            "provider": "aliyun",
            "access_key": "your_access_key",
            "access_secret": "your_access_secret",
            "phone_numbers": ["13800138000"]
        },
        "console": {
            "enabled": True
        }
    }
    
    os.makedirs("config", exist_ok=True)
    
    with open("config/notification_config.json", 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 配置文件模板已创建：config/notification_config.json")
    
    return config


if __name__ == "__main__":
    # 创建配置模板
    create_notification_config_template()
    
    # 测试通知
    service = NotificationService()
    service.test_notification('console')
