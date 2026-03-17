"""
RSI 超买超卖策略 (RSI Strategy)

基于相对强弱指标 RSI 的均值回归策略：
- RSI < 30：超卖，买入
- RSI > 70：超买，卖出
- RSI 背离：趋势反转信号
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from .base_strategy import BaseStrategy, Signal


class RSIStrategy(BaseStrategy):
    """
    RSI 超买超卖策略
    
    Parameters
    ----------
    period : int
        RSI 计算周期，默认 14
    oversold : float
        超卖阈值，默认 30
    overbought : float
        超买阈值，默认 70
    use_divergence : bool
        是否使用背离信号，默认 True
    """
    
    def __init__(self, period: int = 14, oversold: float = 30,
                 overbought: float = 70, use_divergence: bool = True):
        params = {
            'period': period,
            'oversold': oversold,
            'overbought': overbought,
            'use_divergence': use_divergence
        }
        super().__init__('RSI', params)
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        self.use_divergence = use_divergence
    
    def calculate_rsi(self, prices: pd.Series) -> float:
        """
        计算 RSI
        
        Returns
        -------
        float
            RSI 值
        """
        if len(prices) < self.period + 1:
            return 50.0
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        
        # 避免除以零
        mask = loss == 0
        if mask.any():
            rs = gain / loss.replace(0, np.nan)
            rs = rs.fillna(100)  # 如果没有损失，RSI 为 100
        else:
            rs = gain / loss
        
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]
    
    def _get_rsi_series(self, prices: pd.Series) -> pd.Series:
        """获取 RSI 序列"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        
        mask = loss == 0
        if mask.any():
            rs = gain / loss.replace(0, np.nan)
            rs = rs.fillna(100)
        else:
            rs = gain / loss
        
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def detect_divergence(self, data: pd.DataFrame) -> Optional[str]:
        """
        检测 RSI 背离
        
        Returns
        -------
        Optional[str]
            'bullish' (底背离), 'bearish' (顶背离), or None
        """
        if len(data) < 20:
            return None
        
        prices = data['close']
        rsi = self._get_rsi_series(prices)
        
        # 寻找价格高点和 RSI 高点
        lookback = 10
        
        # 顶背离：价格创新高，RSI 未创新高
        recent_price_high = prices.tail(lookback).max()
        price_high_idx = prices.tail(lookback).idxmax()
        
        # 找到对应时间的 RSI
        rsi_at_high = rsi.loc[price_high_idx] if price_high_idx in rsi.index else rsi.iloc[-1]
        prev_rsi_high = rsi.iloc[-lookback-10:-lookback].max() if len(rsi) > 20 else rsi.iloc[:-lookback].max()
        
        if prices.iloc[-1] > recent_price_high and rsi.iloc[-1] < prev_rsi_high:
            return 'bearish'  # 顶背离
        
        # 底背离：价格创新低，RSI 未创新低
        recent_price_low = prices.tail(lookback).min()
        price_low_idx = prices.tail(lookback).idxmin()
        
        rsi_at_low = rsi.loc[price_low_idx] if price_low_idx in rsi.index else rsi.iloc[-1]
        prev_rsi_low = rsi.iloc[-lookback-10:-lookback].min() if len(rsi) > 20 else rsi.iloc[:-lookback].min()
        
        if prices.iloc[-1] < recent_price_low and rsi.iloc[-1] > prev_rsi_low:
            return 'bullish'  # 底背离
        
        return None
    
    def generate_signal(self, data: pd.DataFrame) -> Signal:
        """
        生成 RSI 策略信号
        
        信号规则：
        - RSI < oversold：超卖，买入
        - RSI > overbought：超买，卖出
        - 背离信号：趋势反转
        """
        if len(data) < self.period + 1:
            return Signal.HOLD
        
        prices = data['close']
        rsi = self.calculate_rsi(prices)
        
        # 超卖区域 - 买入
        if rsi < self.oversold:
            return Signal.BUY
        
        # 超买区域 - 卖出
        elif rsi > self.overbought:
            return Signal.SELL
        
        # 接近超卖 - 较强买入信号
        elif rsi < self.oversold + 5:
            return Signal.STRONG_BUY
        
        # 接近超买 - 较强卖出信号
        elif rsi > self.overbought - 5:
            return Signal.STRONG_SELL
        
        # 背离信号
        if self.use_divergence:
            divergence = self.detect_divergence(data)
            if divergence == 'bullish':
                return Signal.BUY
            elif divergence == 'bearish':
                return Signal.SELL
        
        # RSI 从超卖区反弹
        if len(data) > self.period + 1:
            prev_rsi = self.calculate_rsi(prices.iloc[:-1])
            if prev_rsi < self.oversold and rsi > self.oversold:
                return Signal.BUY  # RSI 从超卖区回升
            elif prev_rsi > self.overbought and rsi < self.overbought:
                return Signal.SELL  # RSI 从超买区回落
        
        return Signal.HOLD
    
    def get_rsi_analysis(self, data: pd.DataFrame) -> Dict:
        """
        获取详细的 RSI 分析
        
        Returns
        -------
        Dict
            包含 RSI 各项指标的字典
        """
        if len(data) < self.period + 1:
            return {
                'rsi': 50.0,
                'zone': 'neutral',
                'divergence': None,
                'trend': 'neutral'
            }
        
        prices = data['close']
        rsi = self.calculate_rsi(prices)
        
        # 判断区域
        if rsi < self.oversold:
            zone = 'oversold'
        elif rsi > self.overbought:
            zone = 'overbought'
        elif rsi < 50:
            zone = 'weak'
        else:
            zone = 'strong'
        
        # 趋势
        if rsi > 50:
            trend = 'bullish'
        else:
            trend = 'bearish'
        
        # 背离
        divergence = self.detect_divergence(data) if self.use_divergence else None
        
        return {
            'rsi': rsi,
            'zone': zone,
            'trend': trend,
            'divergence': divergence
        }


class RSICenterlineStrategy(BaseStrategy):
    """
    RSI 中轴策略
    
    基于 RSI 穿越 50 中轴线的策略
    - RSI 上穿 50：买入
    - RSI 下穿 50：卖出
    """
    
    def __init__(self, period: int = 14):
        params = {
            'period': period
        }
        super().__init__('RSI Centerline', params)
        self.period = period
    
    def generate_signal(self, data: pd.DataFrame) -> Signal:
        """生成 RSI 中轴交叉信号"""
        if len(data) < self.period + 2:
            return Signal.HOLD
        
        prices = data['close']
        
        # 计算 RSI 序列
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        
        mask = loss == 0
        if mask.any():
            rs = gain / loss.replace(0, np.nan)
            rs = rs.fillna(100)
        else:
            rs = gain / loss
        
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1]
        prev_rsi = rsi.iloc[-2]
        
        # 上穿 50
        if prev_rsi <= 50 and current_rsi > 50:
            return Signal.BUY
        
        # 下穿 50
        elif prev_rsi >= 50 and current_rsi < 50:
            return Signal.SELL
        
        # 在 50 上方 - 多头
        elif current_rsi > 55:
            return Signal.BUY
        
        # 在 50 下方 - 空头
        elif current_rsi < 45:
            return Signal.SELL
        
        return Signal.HOLD
