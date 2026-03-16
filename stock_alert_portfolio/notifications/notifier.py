"""
通知模块 - 支持邮件和钉钉
"""
import smtplib
import requests
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime
from typing import List, Dict
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import config


class NotificationService:
    """通知服务类"""
    
    def __init__(self):
        self.email_enabled = config.EMAIL_ENABLED
        self.dingtalk_enabled = config.DINGTALK_ENABLED
    
    def send_email(self, subject: str, content: str, to_address: str = None) -> bool:
        """
        发送邮件通知
        
        Args:
            subject: 邮件主题
            content: 邮件内容
            to_address: 收件人地址 (默认使用配置中的 EMAIL_TO)
            
        Returns:
            是否发送成功
        """
        if not self.email_enabled:
            print("邮件通知未启用")
            return False
        
        to_address = to_address or config.EMAIL_TO
        
        if not to_address:
            print("未配置收件人地址")
            return False
        
        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = config.EMAIL_USER
            msg['To'] = to_address
            msg['Subject'] = Header(subject, 'utf-8')
            
            # 添加内容
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
            
            # 发送邮件
            server = smtplib.SMTP(config.EMAIL_HOST, config.EMAIL_PORT)
            server.starttls()
            server.login(config.EMAIL_USER, config.EMAIL_PASSWORD)
            server.sendmail(config.EMAIL_USER, to_address, msg.as_string())
            server.quit()
            
            print(f"邮件已发送：{subject}")
            return True
            
        except Exception as e:
            print(f"邮件发送失败：{e}")
            return False
    
    def send_dingtalk(self, content: str, webhook: str = None) -> bool:
        """
        发送钉钉通知
        
        Args:
            content: 通知内容
            webhook: 钉钉机器人 webhook URL (默认使用配置中的 DINGTALK_WEBHOOK)
            
        Returns:
            是否发送成功
        """
        if not self.dingtalk_enabled:
            print("钉钉通知未启用")
            return False
        
        webhook = webhook or config.DINGTALK_WEBHOOK
        
        if not webhook:
            print("未配置钉钉 Webhook")
            return False
        
        try:
            headers = {'Content-Type': 'application/json'}
            data = {
                "msgtype": "text",
                "text": {
                    "content": content
                }
            }
            
            response = requests.post(webhook, headers=headers, data=json.dumps(data))
            
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    print("钉钉通知已发送")
                    return True
            
            print(f"钉钉通知发送失败：{response.text}")
            return False
            
        except Exception as e:
            print(f"钉钉通知发送失败：{e}")
            return False
    
    def send_alert_notifications(self, alerts: List[Dict]) -> int:
        """
        发送预警通知
        
        Args:
            alerts: 预警列表
            
        Returns:
            成功发送的通知数量
        """
        if not alerts:
            return 0
        
        success_count = 0
        
        # 构建通知内容
        alert_messages = []
        for alert in alerts:
            alert_messages.append(
                f"{alert['message']}\n时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        
        content = "\n\n".join(alert_messages)
        subject = f"股票预警通知 - {len(alerts)}条"
        
        # 发送邮件
        if self.email_enabled:
            if self.send_email(subject, content):
                success_count += 1
        
        # 发送钉钉
        if self.dingtalk_enabled:
            if self.send_dingtalk(content):
                success_count += 1
        
        return success_count
    
    def send_daily_report(self, portfolio_summary: Dict) -> bool:
        """
        发送每日投资组合报告
        
        Args:
            portfolio_summary: 投资组合摘要
            
        Returns:
            是否发送成功
        """
        if not self.email_enabled and not self.dingtalk_enabled:
            return False
        
        # 构建报告内容
        report = f"""
📊 投资组合日报
时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💰 总资产：{portfolio_summary.get('total_market_value', 0):.2f} 元
💵 总投入：{portfolio_summary.get('total_invested', 0):.2f} 元
📈 总盈亏：{portfolio_summary.get('total_profit_loss', 0):.2f} 元
📊 收益率：{portfolio_summary.get('profit_loss_rate', 0):.2f}%
📦 持仓数量：{portfolio_summary.get('total_holdings', 0)}

持仓明细:
"""
        
        for pos in portfolio_summary.get('positions', []):
            report += f"""
{pos['stock_name']}({pos['stock_code']})
  当前价：{pos['current_price']:.2f} | 成本：{pos['avg_cost']:.2f}
  盈亏：{pos['profit_loss']:.2f} ({pos['profit_loss_rate']:+.2f}%)
"""
        
        subject = f"投资组合日报 - {datetime.now().strftime('%Y-%m-%d')}"
        
        success = False
        
        if self.email_enabled:
            success = self.send_email(subject, report)
        
        if self.dingtalk_enabled:
            success = self.send_dingtalk(report)
        
        return success
