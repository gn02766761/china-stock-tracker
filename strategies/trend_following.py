"""
趋势跟踪策略 (Trend Following Strategy)

基于移动平均线的趋势跟踪策略：
- 当短期均线上穿长期均线时买入（金叉）
- 当短期均线下穿长期均线时卖出（死叉）
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from .base_strategy import BaseStrategy, Signal


class TrendFollowingStrategy(BaseStrategy):
    """
    双均线趋势跟踪策略
    
    Parameters
    ----------
    short_period : int
        短期均线周期，默认 5
    long_period : int
        长期均线周期，默认 20
    use_ema : bool
        是否使用指数均线，默认 False（使用简单均线）
    """
    
    def __init__(self, short_period: int = 5, long_period: int = 20, 
                 use_ema: bool = False):
        params = {
            'short_period': short_period,
            'long_period': long_period,
            'use_ema': use_ema
        }
        super().__init__('Trend Following', params)
        self.short_period = short_period
        self.long_period = long_period
        self.use_ema = use_ema
        self.prev_short_ma = None
        self.prev_long_ma = None
    
    def _calculate_ma(self, prices: pd.Series) -> tuple:
        """计算短期和长期均线"""
        if len(prices) < self.long_period:
            return None, None
        
        if self.use_ema:
            short_ma = prices.ewm(span=self.short_period).mean().iloc[-1]
            long_ma = prices.ewm(span=self.long_period).mean().iloc[-1]
            prev_short = prices.ewm(span=self.short_period).mean().iloc[-2] if len(prices) > 1 else None
            prev_long = prices.ewm(span=self.long_period).mean().iloc[-2] if len(prices) > 1 else None
        else:
            short_ma = prices.tail(self.short_period).mean()
            long_ma = prices.tail(self.long_period).mean()
            prev_short = prices.iloc[-self.short_period-1:-1].mean() if len(prices) > self.short_period else None
            prev_long = prices.iloc[-self.long_period-1:-1].mean() if len(prices) > self.long_period else None
        
        return short_ma, long_ma, prev_short, prev_long
    
    def generate_signal(self, data: pd.DataFrame) -> Signal:
        """
        生成趋势跟踪信号
        
        信号规则：
        - 金叉（短期上穿长期）：BUY
        - 死叉（短期下穿长期）：SELL
        - 其他情况：HOLD
        """
        if len(data) < self.long_period + 1:
            return Signal.HOLD
        
        prices = data['close']
        
        # 计算当前和前一期的均线
        result = self._calculate_ma(prices)
        if result[0] is None:
            return Signal.HOLD
        
        short_ma, long_ma, prev_short, prev_long = result
        
        if prev_short is None or prev_long is None:
            return Signal.HOLD
        
        # 检测金叉和死叉
        if prev_short <= prev_long and short_ma > long_ma:
            # 金叉 - 买入信号
            return Signal.BUY
        elif prev_short >= prev_long and short_ma < long_ma:
            # 死叉 - 卖出信号
            return Signal.SELL
        
        # 趋势确认 - 可以加强信号
        if short_ma > long_ma * 1.02:  # 短期均线高于长期 2% 以上
            return Signal.STRONG_BUY
        elif short_ma < long_ma * 0.98:  # 短期均线低于长期 2% 以上
            return Signal.STRONG_SELL
        
        return Signal.HOLD
    
    def get_trend_strength(self, data: pd.DataFrame) -> float:
        """
        计算趋势强度
        
        Returns
        -------
        float
            趋势强度指标 (0-1)，值越大表示趋势越强
        """
        if len(data) < self.long_period:
            return 0.0
        
        prices = data['close']
        short_ma, long_ma, _, _ = self._calculate_ma(prices)
        
        if long_ma == 0:
            return 0.0
        
        # 计算均线偏离度
        deviation = abs(short_ma - long_ma) / long_ma
        
        # 归一化到 0-1 范围
        strength = min(deviation / 0.1, 1.0)  # 10% 偏离度为最大值
        
        return strength


class TripleMAStrategy(BaseStrategy):
    """
    三均线策略
    
    使用三条均线（短、中、长）来确认趋势：
    - 多头排列：短 > 中 > 长，买入
    - 空头排列：短 < 中 < 长，卖出
    """
    
    def __init__(self, short_period: int = 5, medium_period: int = 10, 
                 long_period: int = 20):
        params = {
            'short_period': short_period,
            'medium_period': medium_period,
            'long_period': long_period
        }
        super().__init__('Triple MA', params)
        self.short_period = short_period
        self.medium_period = medium_period
        self.long_period = long_period
    
    def generate_signal(self, data: pd.DataFrame) -> Signal:
        """生成三均线策略信号"""
        if len(data) < self.long_period:
            return Signal.HOLD
        
        prices = data['close']
        
        short_ma = prices.tail(self.short_period).mean()
        medium_ma = prices.tail(self.medium_period).mean()
        long_ma = prices.tail(self.long_period).mean()
        
        # 多头排列
        if short_ma > medium_ma > long_ma:
            return Signal.BUY
        
        # 空头排列
        elif short_ma < medium_ma < long_ma:
            return Signal.SELL
        
        return Signal.HOLD
