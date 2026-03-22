"""
实时行情监控器 (Realtime Monitor)

实时监控股票价格，触发预警时发送通知
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import time
import threading
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from price_alert import PriceAlertManager, PriceAlert, AlertType, AlertStatus
from utils.data_collector import StockDataCollector
from notification_service import NotificationService


class RealtimeMonitor:
    """实时行情监控器"""
    
    def __init__(
        self,
        tushare_token: str = None,
        alert_manager: PriceAlertManager = None,
        notification_service: NotificationService = None
    ):
        """
        Parameters
        ----------
        tushare_token : str
            Tushare API token
        alert_manager : PriceAlertManager
            预警管理器
        notification_service : NotificationService
            通知服务
        """
        self.token = tushare_token or os.getenv('TUSHARE_TOKEN')
        self.collector = StockDataCollector(token=self.token) if self.token else None
        
        self.alert_manager = alert_manager or PriceAlertManager()
        self.notification_service = notification_service or NotificationService()
        
        # 监控配置
        self.watchlist: List[str] = []  # 监控股票列表
        self.monitoring = False  # 是否正在监控
        self.monitor_thread: Optional[threading.Thread] = None
        self.check_interval = 60  # 检查间隔（秒）
        
        # 回调函数
        self.on_alert_triggered: Optional[Callable] = None
        
        # 注册预警回调
        self.alert_manager.register_callback(self._on_alert_triggered)
    
    def add_to_watchlist(self, symbols: List[str]):
        """添加股票到监控股票列表"""
        for symbol in symbols:
            if symbol not in self.watchlist:
                self.watchlist.append(symbol)
    
    def remove_from_watchlist(self, symbol: str):
        """从监控股票列表移除"""
        if symbol in self.watchlist:
            self.watchlist.remove(symbol)
    
    def start_monitoring(self, interval: int = 60, blocking: bool = False):
        """
        开始监控
        
        Parameters
        ----------
        interval : int
            检查间隔（秒）
        blocking : bool
            是否阻塞当前线程
        """
        if self.monitoring:
            print("⚠️ 监控已在运行中")
            return
        
        self.monitoring = True
        self.check_interval = interval
        
        print(f"🚀 开始实时监控，检查间隔：{interval}秒")
        print(f"📊 监控股票：{len(self.watchlist)}只")
        
        if blocking:
            self._monitor_loop()
        else:
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
            self.monitor_thread = None
        
        print("⏹️ 监控已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring:
            try:
                self._check_all_alerts()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"❌ 监控循环错误：{e}")
                time.sleep(self.check_interval)
    
    def _check_all_alerts(self):
        """检查所有预警"""
        active_alerts = self.alert_manager.get_active_alerts()
        
        if not active_alerts:
            return
        
        # 按股票代码分组
        symbols_to_check = list(set([a.symbol for a in active_alerts]))
        
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 检查 {len(symbols_to_check)} 只股票...")
        
        for symbol in symbols_to_check:
            try:
                # 获取实时数据
                data = self._get_realtime_data(symbol)
                
                if data is not None and not data.empty:
                    # 检查该股票的预警
                    alerts_for_symbol = [a for a in active_alerts if a.symbol == symbol]
                    self._check_symbol_alerts(symbol, data, alerts_for_symbol)
                
            except Exception as e:
                print(f"❌ 检查 {symbol} 失败：{e}")
    
    def _get_realtime_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        获取实时数据
        
        Parameters
        ----------
        symbol : str
            股票代码
        
        Returns
        -------
        pd.DataFrame
            股票数据
        """
        if not self.collector:
            return None
        
        try:
            # 获取最近 30 天数据（用于计算技术指标）
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
            
            data = self.collector.get_stock_data(symbol, start_date, end_date)
            
            if data is not None and not data.empty:
                data = self.collector.calculate_technical_indicators(data)
            
            return data
        
        except Exception as e:
            print(f"获取数据失败：{e}")
            return None
    
    def _check_symbol_alerts(
        self,
        symbol: str,
        data: pd.DataFrame,
        alerts: List[PriceAlert]
    ):
        """检查单只股票的预警"""
        triggered = self.alert_manager.check_alerts(data)
        
        for alert in triggered:
            print(f"🚨 预警触发：{alert.symbol} - {alert.name} - {alert.alert_type.value}")
    
    def _on_alert_triggered(self, alert: PriceAlert):
        """预警触发回调"""
        # 发送通知
        self.notification_service.send_alert_notification(alert)
        
        # 调用用户回调
        if self.on_alert_triggered:
            self.on_alert_triggered(alert)
    
    def get_monitor_status(self) -> dict:
        """获取监控状态"""
        return {
            'monitoring': self.monitoring,
            'watchlist_count': len(self.watchlist),
            'active_alerts': len(self.alert_manager.get_active_alerts()),
            'triggered_alerts_24h': len(self.alert_manager.get_triggered_alerts(hours=24)),
            'check_interval': self.check_interval
        }
    
    def quick_setup_alert(
        self,
        symbol: str,
        name: str,
        current_price: float,
        stop_loss_pct: float = 5.0,
        take_profit_pct: float = 10.0,
        notification_methods: List[str] = None
    ) -> List[PriceAlert]:
        """
        快速设置预警（止损 + 止盈）
        
        Parameters
        ----------
        symbol : str
            股票代码
        name : str
            股票名称
        current_price : float
            当前价格
        stop_loss_pct : float
            止损百分比
        take_profit_pct : float
            止盈百分比
        notification_methods : List[str]
            通知方式
        
        Returns
        -------
        List[PriceAlert]
            创建的预警列表
        """
        alerts = []
        
        # 止损预警
        stop_price = current_price * (1 - stop_loss_pct / 100)
        alerts.append(self.alert_manager.create_stop_loss_alert(
            symbol, name, stop_price,
            notification_methods=notification_methods,
            notes=f"止损 {stop_loss_pct}%"
        ))
        
        # 止盈预警
        target_price = current_price * (1 + take_profit_pct / 100)
        alerts.append(self.alert_manager.create_take_profit_alert(
            symbol, name, target_price,
            notification_methods=notification_methods,
            notes=f"止盈 {take_profit_pct}%"
        ))
        
        print(f"✅ 已设置预警：{symbol} - 止损{stop_price:.2f}, 止盈{target_price:.2f}")
        
        return alerts


class SimpleMonitor:
    """简易监控器（无需 Tushare token）"""
    
    def __init__(self, alert_manager: PriceAlertManager = None):
        """
        Parameters
        ----------
        alert_manager : PriceAlertManager
            预警管理器
        """
        self.alert_manager = alert_manager or PriceAlertManager()
        self.notification_service = NotificationService()
        self.watchlist: List[str] = []
        self.monitoring = False
    
    def add_stock(self, symbol: str, name: str = ""):
        """添加监控股票"""
        if symbol not in self.watchlist:
            self.watchlist.append(symbol)
            print(f"✓ 添加监控股票：{symbol} {name}")
    
    def set_price_alert(
        self,
        symbol: str,
        name: str,
        target_price: float,
        above: bool = True
    ):
        """设置价格预警"""
        alert_type = AlertType.PRICE_ABOVE if above else AlertType.PRICE_BELOW
        direction = "突破" if above else "跌破"
        
        self.alert_manager.create_alert(
            symbol=symbol,
            name=name,
            alert_type=alert_type,
            condition_value=target_price,
            notification_methods=['console'],
            notes=f"价格{direction}{target_price:.2f}"
        )
        
        print(f"✓ 设置预警：{symbol} - {direction}{target_price:.2f}")
    
    def set_stop_loss_take_profit(
        self,
        symbol: str,
        name: str,
        current_price: float,
        stop_loss_pct: float = 5.0,
        take_profit_pct: float = 10.0
    ):
        """设置止损止盈预警"""
        stop_price = current_price * (1 - stop_loss_pct / 100)
        target_price = current_price * (1 + take_profit_pct / 100)
        
        # 止损
        self.alert_manager.create_alert(
            symbol=symbol,
            name=name,
            alert_type=AlertType.STOP_LOSS,
            condition_value=stop_price,
            notification_methods=['console'],
            notes=f"止损{stop_loss_pct}%"
        )
        
        # 止盈
        self.alert_manager.create_alert(
            symbol=symbol,
            name=name,
            alert_type=AlertType.TAKE_PROFIT,
            condition_value=target_price,
            notification_methods=['console'],
            notes=f"止盈{take_profit_pct}%"
        )
        
        print(f"✓ 设置止损止盈：{symbol} - 止损{stop_price:.2f}, 止盈{target_price:.2f}")
    
    def check_manual(self, symbol: str, current_price: float):
        """
        手动检查预警
        
        Parameters
        ----------
        symbol : str
            股票代码
        current_price : float
            当前价格
        """
        # 创建临时数据
        data = pd.DataFrame({
            'close': [current_price],
            'rsi': [50],
            'vol': [1000000]
        })
        
        triggered = self.alert_manager.check_alerts(data)
        
        for alert in triggered:
            print(f"🚨 预警触发：{alert.symbol} - {alert.name}")
            print(f"   条件：{alert.alert_type.value} = {alert.condition_value}")
            print(f"   当前：{alert.current_value}")
            
            # 发送通知
            self.notification_service.send_alert_notification(alert)
        
        return triggered
    
    def list_alerts(self):
        """列出所有预警"""
        alerts = self.alert_manager.get_active_alerts()
        
        if not alerts:
            print("暂无活跃预警")
            return
        
        print("\n" + "=" * 60)
        print("活跃预警列表")
        print("=" * 60)
        
        for alert in alerts:
            status_icon = "🔴" if alert.alert_type in [AlertType.STOP_LOSS, AlertType.RSI_OVERSOLD] else "🟢"
            print(f"{status_icon} {alert.symbol} - {alert.name}")
            print(f"   类型：{alert.alert_type.value}")
            print(f"   条件：{alert.condition_value}")
            if alert.expires_at:
                print(f"   过期：{alert.expires_at.strftime('%Y-%m-%d %H:%M')}")
            print()
