"""
价格预警模块 (Price Alert)

监控股票价格，当达到预设条件时触发预警
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import os


class AlertType(Enum):
    """预警类型"""
    PRICE_ABOVE = "price_above"          # 价格突破上方
    PRICE_BELOW = "price_below"          # 价格跌破下方
    MA_CROSS_ABOVE = "ma_cross_above"    # 均线上穿
    MA_CROSS_BELOW = "ma_cross_below"    # 均线下穿
    RSI_OVERBOUGHT = "rsi_overbought"    # RSI 超买
    RSI_OVERSOLD = "rsi_oversold"        # RSI 超卖
    VOLUME_SPIKE = "volume_spike"        # 成交量放大
    BOLLINGER_BREAKOUT = "bollinger_breakout"  # 布林带突破
    STOP_LOSS = "stop_loss"              # 止损预警
    TAKE_PROFIT = "take_profit"          # 止盈预警


class AlertStatus(Enum):
    """预警状态"""
    ACTIVE = "active"       # 激活
    TRIGGERED = "triggered" # 已触发
    EXPIRED = "expired"     # 已过期
    CANCELLED = "cancelled" # 已取消


@dataclass
class PriceAlert:
    """价格预警配置"""
    id: str
    symbol: str
    name: str
    alert_type: AlertType
    condition_value: float
    current_value: float = 0.0
    status: AlertStatus = AlertStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    triggered_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    notification_methods: List[str] = field(default_factory=list)  # ['email', 'wechat', 'sms']
    notes: str = ""
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'name': self.name,
            'alert_type': self.alert_type.value,
            'condition_value': self.condition_value,
            'current_value': self.current_value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'triggered_at': self.triggered_at.isoformat() if self.triggered_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'notification_methods': self.notification_methods,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PriceAlert':
        """从字典创建"""
        alert = cls(
            id=data['id'],
            symbol=data['symbol'],
            name=data['name'],
            alert_type=AlertType(data['alert_type']),
            condition_value=data['condition_value'],
            current_value=data.get('current_value', 0.0),
            status=AlertStatus(data.get('status', 'active')),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            triggered_at=datetime.fromisoformat(data['triggered_at']) if data.get('triggered_at') else None,
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None,
            notification_methods=data.get('notification_methods', []),
            notes=data.get('notes', '')
        )
        return alert


class PriceAlertManager:
    """价格预警管理器"""
    
    def __init__(self, data_file: str = "data/alerts.json"):
        """
        Parameters
        ----------
        data_file : str
            预警配置文件路径
        """
        self.data_file = data_file
        self.alerts: Dict[str, PriceAlert] = {}
        self.callbacks: List[Callable] = []  # 预警触发回调
        self._load_alerts()
    
    def create_alert(
        self,
        symbol: str,
        name: str,
        alert_type: AlertType,
        condition_value: float,
        notification_methods: List[str] = None,
        notes: str = "",
        expires_days: int = 30
    ) -> PriceAlert:
        """
        创建价格预警
        
        Parameters
        ----------
        symbol : str
            股票代码
        name : str
            股票名称
        alert_type : AlertType
            预警类型
        condition_value : float
            触发条件值
        notification_methods : List[str]
            通知方式 ['email', 'wechat', 'sms']
        notes : str
            备注
        expires_days : int
            过期天数
        
        Returns
        -------
        PriceAlert
            创建的预警对象
        """
        alert_id = f"{symbol}_{alert_type.value}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        alert = PriceAlert(
            id=alert_id,
            symbol=symbol,
            name=name,
            alert_type=alert_type,
            condition_value=condition_value,
            notification_methods=notification_methods or ['email'],
            notes=notes,
            expires_at=datetime.now() + timedelta(days=expires_days)
        )
        
        self.alerts[alert_id] = alert
        self._save_alerts()
        
        return alert
    
    def create_price_breakout_alert(
        self,
        symbol: str,
        name: str,
        breakout_price: float,
        above: bool = True,
        **kwargs
    ) -> PriceAlert:
        """创建价格突破预警"""
        alert_type = AlertType.PRICE_ABOVE if above else AlertType.PRICE_BELOW
        return self.create_alert(symbol, name, alert_type, breakout_price, **kwargs)
    
    def create_ma_cross_alert(
        self,
        symbol: str,
        name: str,
        ma_type: str = "MA5",
        cross_above: bool = True,
        **kwargs
    ) -> PriceAlert:
        """创建均线交叉预警"""
        alert_type = AlertType.MA_CROSS_ABOVE if cross_above else AlertType.MA_CROSS_BELOW
        return self.create_alert(symbol, name, alert_type, 0, **kwargs)
    
    def create_rsi_alert(
        self,
        symbol: str,
        name: str,
        overbought: float = 70,
        oversold: float = 30,
        **kwargs
    ) -> List[PriceAlert]:
        """创建 RSI 预警（超买和超卖）"""
        alerts = []
        
        # 超买预警
        alerts.append(self.create_alert(
            symbol, name, AlertType.RSI_OVERBOUGHT, overbought, **kwargs
        ))
        
        # 超卖预警
        alerts.append(self.create_alert(
            symbol, name, AlertType.RSI_OVERSOLD, oversold, **kwargs
        ))
        
        return alerts
    
    def create_stop_loss_alert(
        self,
        symbol: str,
        name: str,
        stop_price: float,
        **kwargs
    ) -> PriceAlert:
        """创建止损预警"""
        return self.create_alert(symbol, name, AlertType.STOP_LOSS, stop_price, **kwargs)
    
    def create_take_profit_alert(
        self,
        symbol: str,
        name: str,
        target_price: float,
        **kwargs
    ) -> PriceAlert:
        """创建止盈预警"""
        return self.create_alert(symbol, name, AlertType.TAKE_PROFIT, target_price, **kwargs)
    
    def cancel_alert(self, alert_id: str) -> bool:
        """取消预警"""
        if alert_id in self.alerts:
            self.alerts[alert_id].status = AlertStatus.CANCELLED
            self._save_alerts()
            return True
        return False
    
    def check_alerts(self, stock_data: pd.DataFrame) -> List[PriceAlert]:
        """
        检查预警是否触发
        
        Parameters
        ----------
        stock_data : pd.DataFrame
            股票数据（包含最新价格）
        
        Returns
        -------
        List[PriceAlert]
            触发的预警列表
        """
        triggered = []
        
        for alert_id, alert in self.alerts.items():
            if alert.status != AlertStatus.ACTIVE:
                continue
            
            # 检查是否过期
            if alert.expires_at and datetime.now() > alert.expires_at:
                alert.status = AlertStatus.EXPIRED
                continue
            
            # 获取最新数据
            if stock_data.empty:
                continue
            
            latest = stock_data.iloc[-1]
            current_price = latest.get('close', 0)
            
            # 检查预警条件
            is_triggered = self._check_alert_condition(alert, latest, current_price)
            
            if is_triggered:
                alert.status = AlertStatus.TRIGGERED
                alert.triggered_at = datetime.now()
                alert.current_value = current_price
                triggered.append(alert)
                
                # 触发回调
                self._trigger_callbacks(alert)
        
        if triggered:
            self._save_alerts()
        
        return triggered
    
    def _check_alert_condition(
        self,
        alert: PriceAlert,
        latest: pd.Series,
        current_price: float
    ) -> bool:
        """检查预警条件"""
        alert_type = alert.alert_type
        
        if alert_type == AlertType.PRICE_ABOVE:
            return current_price >= alert.condition_value
        
        elif alert_type == AlertType.PRICE_BELOW:
            return current_price <= alert.condition_value
        
        elif alert_type == AlertType.MA_CROSS_ABOVE:
            # 检查价格是否上穿均线
            ma_col = alert.notes or 'ma5'
            if ma_col in latest:
                return current_price > latest[ma_col]
            return False
        
        elif alert_type == AlertType.MA_CROSS_BELOW:
            ma_col = alert.notes or 'ma5'
            if ma_col in latest:
                return current_price < latest[ma_col]
            return False
        
        elif alert_type == AlertType.RSI_OVERBOUGHT:
            if 'rsi' in latest:
                return latest['rsi'] >= alert.condition_value
            return False
        
        elif alert_type == AlertType.RSI_OVERSOLD:
            if 'rsi' in latest:
                return latest['rsi'] <= alert.condition_value
            return False
        
        elif alert_type == AlertType.VOLUME_SPIKE:
            if 'vol' in latest and 'vol_ma5' in latest:
                return latest['vol'] >= alert.condition_value * latest['vol_ma5']
            return False
        
        elif alert_type == AlertType.BOLLINGER_BREAKOUT:
            if 'boll_upper' in latest:
                return current_price >= latest['boll_upper']
            return False
        
        elif alert_type == AlertType.STOP_LOSS:
            return current_price <= alert.condition_value
        
        elif alert_type == AlertType.TAKE_PROFIT:
            return current_price >= alert.condition_value
        
        return False
    
    def register_callback(self, callback: Callable):
        """注册预警触发回调"""
        self.callbacks.append(callback)
    
    def _trigger_callbacks(self, alert: PriceAlert):
        """触发回调"""
        for callback in self.callbacks:
            try:
                callback(alert)
            except Exception as e:
                print(f"回调执行失败：{e}")
    
    def get_active_alerts(self) -> List[PriceAlert]:
        """获取所有活跃预警"""
        return [a for a in self.alerts.values() if a.status == AlertStatus.ACTIVE]
    
    def get_triggered_alerts(self, hours: int = 24) -> List[PriceAlert]:
        """获取最近触发的预警"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [
            a for a in self.alerts.values()
            if a.status == AlertStatus.TRIGGERED and a.triggered_at and a.triggered_at > cutoff
        ]
    
    def _save_alerts(self):
        """保存预警到文件"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        data = {
            alert_id: alert.to_dict()
            for alert_id, alert in self.alerts.items()
        }
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _load_alerts(self):
        """从文件加载预警"""
        if not os.path.exists(self.data_file):
            return
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.alerts = {
                alert_id: PriceAlert.from_dict(alert_data)
                for alert_id, alert_data in data.items()
            }
        except Exception as e:
            print(f"加载预警失败：{e}")
            self.alerts = {}
    
    def delete_alert(self, alert_id: str) -> bool:
        """删除预警"""
        if alert_id in self.alerts:
            del self.alerts[alert_id]
            self._save_alerts()
            return True
        return False
    
    def clear_expired_alerts(self) -> int:
        """清理过期预警"""
        now = datetime.now()
        expired = [
            aid for aid, a in self.alerts.items()
            if a.expires_at and now > a.expires_at
        ]
        
        for aid in expired:
            del self.alerts[aid]
        
        if expired:
            self._save_alerts()
        
        return len(expired)
