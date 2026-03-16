"""
预警检查引擎
"""
from datetime import datetime
from typing import List, Tuple, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database_manager import DatabaseManager, PriceAlert, TechnicalAlert
from app.data_service import StockDataService


class AlertEngine:
    """预警引擎类"""
    
    def __init__(self, db_manager: DatabaseManager, data_service: StockDataService):
        self.db = db_manager
        self.data_service = data_service
        self.check_results = []  # 存储检查结果
    
    def check_price_alerts(self) -> List[dict]:
        """
        检查所有价格预警
        
        Returns:
            触发的预警列表
        """
        triggered_alerts = []
        alerts = self.db.get_active_price_alerts()
        
        for alert in alerts:
            current_price = self.data_service.get_current_price(alert.stock_code)
            
            if current_price is None:
                continue
            
            triggered = False
            message = ""
            
            if alert.alert_type == 'price_above' and current_price >= alert.threshold_value:
                triggered = True
                message = f"⬆️ {alert.stock_name}({alert.stock_code}) 价格突破 {alert.threshold_value}元，当前价：{current_price:.2f}元"
            
            elif alert.alert_type == 'price_below' and current_price <= alert.threshold_value:
                triggered = True
                message = f"⬇️ {alert.stock_name}({alert.stock_code}) 价格跌破 {alert.threshold_value}元，当前价：{current_price:.2f}元"
            
            elif alert.alert_type == 'change_above':
                change_pct = self.data_service.get_price_change(alert.stock_code)
                if change_pct is not None and change_pct >= alert.threshold_value:
                    triggered = True
                    message = f"📈 {alert.stock_name}({alert.stock_code}) 涨幅超过 {alert.threshold_value}%，当前涨幅：{change_pct:.2f}%"
            
            elif alert.alert_type == 'change_below':
                change_pct = self.data_service.get_price_change(alert.stock_code)
                if change_pct is not None and change_pct <= alert.threshold_value:
                    triggered = True
                    message = f"📉 {alert.stock_name}({alert.stock_code}) 跌幅超过 {alert.threshold_value}%，当前跌幅：{change_pct:.2f}%"
            
            if triggered:
                # 避免重复触发 (1 小时内不重复)
                if alert.last_triggered:
                    time_since_last = (datetime.now() - alert.last_triggered).total_seconds()
                    if time_since_last < 3600:  # 1 小时
                        continue
                
                # 记录日志
                self.db.log_alert(
                    alert_id=alert.id,
                    alert_type='price',
                    stock_code=alert.stock_code,
                    stock_name=alert.stock_name,
                    trigger_value=current_price,
                    message=message
                )
                
                triggered_alerts.append({
                    'alert_id': alert.id,
                    'type': 'price',
                    'stock_code': alert.stock_code,
                    'stock_name': alert.stock_name,
                    'message': message,
                    'trigger_value': current_price
                })
        
        return triggered_alerts
    
    def check_technical_alerts(self) -> List[dict]:
        """
        检查所有技术指标预警
        
        Returns:
            触发的预警列表
        """
        triggered_alerts = []
        alerts = self.db.get_active_technical_alerts()
        
        for alert in alerts:
            # 获取股票数据并计算技术指标
            df = self.data_service.get_stock_data(alert.stock_code, days=60)
            
            if df is None or df.empty:
                continue
            
            df = self.data_service.calculate_technical_indicators(df)
            
            if df.empty:
                continue
            
            triggered = False
            message = ""
            trigger_value = None
            
            # 获取最新指标值
            latest = df.iloc[-1]
            
            if alert.indicator.upper() == 'RSI':
                rsi_value = latest.get('rsi')
                if rsi_value is not None:
                    trigger_value = rsi_value
                    if alert.condition == 'above' and rsi_value >= alert.threshold_value:
                        triggered = True
                        message = f"🔴 {alert.stock_name}({alert.stock_code}) RSI 上穿 {alert.threshold_value}，当前 RSI: {rsi_value:.2f}"
                    elif alert.condition == 'below' and rsi_value <= alert.threshold_value:
                        triggered = True
                        message = f"🟢 {alert.stock_name}({alert.stock_code}) RSI 下穿 {alert.threshold_value}，当前 RSI: {rsi_value:.2f}"
            
            elif alert.indicator.upper() == 'MACD':
                macd_value = latest.get('macd')
                signal_value = latest.get('macd_signal')
                if macd_value is not None and signal_value is not None:
                    trigger_value = macd_value
                    if alert.condition == 'cross_above' and macd_value > signal_value:
                        prev_macd = df.iloc[-2].get('macd', macd_value)
                        prev_signal = df.iloc[-2].get('macd_signal', signal_value)
                        if prev_macd <= prev_signal:  # 刚刚金叉
                            triggered = True
                            message = f"💛 {alert.stock_name}({alert.stock_code}) MACD 金叉，MACD: {macd_value:.2f}, Signal: {signal_value:.2f}"
                    elif alert.condition == 'cross_below' and macd_value < signal_value:
                        prev_macd = df.iloc[-2].get('macd', macd_value)
                        prev_signal = df.iloc[-2].get('macd_signal', signal_value)
                        if prev_macd >= prev_signal:  # 刚刚死叉
                            triggered = True
                            message = f"💙 {alert.stock_name}({alert.stock_code}) MACD 死叉，MACD: {macd_value:.2f}, Signal: {signal_value:.2f}"
            
            elif alert.indicator.upper() in ['MA5', 'MA10', 'MA20', 'MA60']:
                ma_column = alert.indicator.lower()
                ma_value = latest.get(ma_column)
                close_price = latest.get('close')
                if ma_value is not None and close_price is not None:
                    trigger_value = close_price
                    if alert.condition == 'cross_above' and close_price > ma_value:
                        prev_close = df.iloc[-2].get('close', close_price)
                        if prev_close <= ma_value:  # 刚刚上穿
                            triggered = True
                            message = f"📊 {alert.stock_name}({alert.stock_code}) 股价上穿{alert.indicator}，收盘价：{close_price:.2f}, {alert.indicator}: {ma_value:.2f}"
                    elif alert.condition == 'cross_below' and close_price < ma_value:
                        prev_close = df.iloc[-2].get('close', close_price)
                        if prev_close >= ma_value:  # 刚刚下穿
                            triggered = True
                            message = f"📉 {alert.stock_name}({alert.stock_code}) 股价下穿{alert.indicator}，收盘价：{close_price:.2f}, {alert.indicator}: {ma_value:.2f}"
            
            elif alert.indicator.upper() == 'BB':
                bb_upper = latest.get('bb_upper')
                bb_lower = latest.get('bb_lower')
                close_price = latest.get('close')
                if bb_upper is not None and bb_lower is not None and close_price is not None:
                    trigger_value = close_price
                    if alert.condition == 'touch_upper' and close_price >= bb_upper:
                        triggered = True
                        message = f"📈 {alert.stock_name}({alert.stock_code}) 股价触及布林带上轨，收盘价：{close_price:.2f}, 上轨：{bb_upper:.2f}"
                    elif alert.condition == 'touch_lower' and close_price <= bb_lower:
                        triggered = True
                        message = f"📉 {alert.stock_name}({alert.stock_code}) 股价触及布林带下轨，收盘价：{close_price:.2f}, 下轨：{bb_lower:.2f}"
            
            if triggered:
                # 避免重复触发
                if alert.last_triggered:
                    time_since_last = (datetime.now() - alert.last_triggered).total_seconds()
                    if time_since_last < 3600:  # 1 小时
                        continue
                
                # 记录日志
                self.db.log_alert(
                    alert_id=alert.id,
                    alert_type='technical',
                    stock_code=alert.stock_code,
                    stock_name=alert.stock_name,
                    trigger_value=trigger_value,
                    message=message
                )
                
                triggered_alerts.append({
                    'alert_id': alert.id,
                    'type': 'technical',
                    'stock_code': alert.stock_code,
                    'stock_name': alert.stock_name,
                    'message': message,
                    'trigger_value': trigger_value
                })
        
        return triggered_alerts
    
    def run_all_checks(self) -> List[dict]:
        """
        运行所有预警检查
        
        Returns:
            所有触发的预警列表
        """
        all_triggered = []
        
        # 检查价格预警
        price_alerts = self.check_price_alerts()
        all_triggered.extend(price_alerts)
        
        # 检查技术指标预警
        technical_alerts = self.check_technical_alerts()
        all_triggered.extend(technical_alerts)
        
        self.check_results = all_triggered
        return all_triggered
    
    def get_check_summary(self) -> dict:
        """获取检查摘要"""
        return {
            'check_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_triggered': len(self.check_results),
            'price_alerts': len([a for a in self.check_results if a['type'] == 'price']),
            'technical_alerts': len([a for a in self.check_results if a['type'] == 'technical'])
        }
