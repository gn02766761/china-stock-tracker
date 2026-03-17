"""
动量策略 (Momentum Strategy)

基于动量效应：
- 买入近期表现强势的股票
- 卖出近期表现弱势的股票
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from .base_strategy import BaseStrategy, Signal


class MomentumStrategy(BaseStrategy):
    """
    动量策略
    
    Parameters
    ----------
    lookback_period : int
        动量计算周期，默认 20
    signal_threshold : float
        信号阈值（收益率超过多少触发信号），默认 5.0（5%）
    use_volume : bool
        是否结合成交量，默认 True
    """
    
    def __init__(self, lookback_period: int = 20, signal_threshold: float = 5.0,
                 use_volume: bool = True):
        params = {
            'lookback_period': lookback_period,
            'signal_threshold': signal_threshold,
            'use_volume': use_volume
        }
        super().__init__('Momentum', params)
        self.lookback_period = lookback_period
        self.signal_threshold = signal_threshold
        self.use_volume = use_volume
    
    def calculate_momentum(self, prices: pd.Series) -> float:
        """
        计算动量指标
        
        Returns
        -------
        float
            动量值（百分比收益率）
        """
        if len(prices) < self.lookback_period:
            return 0.0
        
        momentum = (prices.iloc[-1] - prices.iloc[-self.lookback_period]) / prices.iloc[-self.lookback_period] * 100
        return momentum
    
    def calculate_volume_momentum(self, data: pd.DataFrame) -> float:
        """
        计算成交量动量
        
        Returns
        -------
        float
            成交量动量指标
        """
        if 'vol' not in data.columns or len(data) < self.lookback_period:
            return 0.0
        
        volumes = data['vol']
        avg_volume = volumes.tail(self.lookback_period).mean()
        prev_avg_volume = volumes.iloc[-self.lookback_period-1:-1].mean() if len(volumes) > self.lookback_period else avg_volume
        
        if prev_avg_volume == 0:
            return 0.0
        
        volume_momentum = (avg_volume - prev_avg_volume) / prev_avg_volume * 100
        return volume_momentum
    
    def generate_signal(self, data: pd.DataFrame) -> Signal:
        """
        生成动量策略信号
        
        信号规则：
        - 动量 > threshold 且成交量放大：BUY/STRONG_BUY
        - 动量 < -threshold 且成交量放大：SELL/STRONG_SELL
        - 其他：HOLD
        """
        if len(data) < self.lookback_period:
            return Signal.HOLD
        
        prices = data['close']
        price_momentum = self.calculate_momentum(prices)
        
        # 结合成交量分析
        if self.use_volume:
            volume_momentum = self.calculate_volume_momentum(data)
            volume_confirmed = volume_momentum > 10  # 成交量放大 10% 以上
        else:
            volume_confirmed = True
        
        # 强动量 - 买入
        if price_momentum > self.signal_threshold * 1.5:
            if volume_confirmed:
                return Signal.STRONG_BUY
            return Signal.BUY
        
        # 强动量 - 卖出
        elif price_momentum < -self.signal_threshold * 1.5:
            if volume_confirmed:
                return Signal.STRONG_SELL
            return Signal.SELL
        
        # 中等动量
        elif price_momentum > self.signal_threshold:
            return Signal.BUY
        
        elif price_momentum < -self.signal_threshold:
            return Signal.SELL
        
        return Signal.HOLD
    
    def get_momentum_indicators(self, data: pd.DataFrame) -> Dict:
        """
        获取动量相关指标
        
        Returns
        -------
        Dict
            包含多个动量指标的字典
        """
        if len(data) < self.lookback_period:
            return {
                'price_momentum': 0.0,
                'volume_momentum': 0.0,
                'momentum_score': 0.0,
                'trend': 'neutral'
            }
        
        prices = data['close']
        
        # 价格动量
        price_momentum = self.calculate_momentum(prices)
        
        # 成交量动量
        volume_momentum = self.calculate_volume_momentum(data) if self.use_volume else 0.0
        
        # 综合动量得分
        momentum_score = price_momentum
        if self.use_volume:
            momentum_score += volume_momentum * 0.3  # 成交量权重 30%
        
        # 趋势判断
        if momentum_score > self.signal_threshold:
            trend = 'bullish'
        elif momentum_score < -self.signal_threshold:
            trend = 'bearish'
        else:
            trend = 'neutral'
        
        return {
            'price_momentum': price_momentum,
            'volume_momentum': volume_momentum,
            'momentum_score': momentum_score,
            'trend': trend
        }


class RSIMomentumStrategy(BaseStrategy):
    """
    RSI 动量策略
    
    结合 RSI 和动量指标
    """
    
    def __init__(self, rsi_period: int = 14, momentum_period: int = 20,
                 overbought: float = 70, oversold: float = 30):
        params = {
            'rsi_period': rsi_period,
            'momentum_period': momentum_period,
            'overbought': overbought,
            'oversold': oversold
        }
        super().__init__('RSI Momentum', params)
        self.rsi_period = rsi_period
        self.momentum_period = momentum_period
        self.overbought = overbought
        self.oversold = oversold
    
    def calculate_rsi(self, prices: pd.Series) -> float:
        """计算 RSI"""
        if len(prices) < self.rsi_period + 1:
            return 50.0
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]
    
    def generate_signal(self, data: pd.DataFrame) -> Signal:
        """生成 RSI 动量信号"""
        if len(data) < max(self.rsi_period, self.momentum_period):
            return Signal.HOLD
        
        prices = data['close']
        rsi = self.calculate_rsi(prices)
        
        # 计算动量
        momentum_strategy = MomentumStrategy(lookback_period=self.momentum_period)
        momentum = momentum_strategy.calculate_momentum(prices)
        
        # RSI 超卖 + 正动量 = 买入
        if rsi < self.oversold and momentum > 0:
            return Signal.BUY
        
        # RSI 超买 + 负动量 = 卖出
        elif rsi > self.overbought and momentum < 0:
            return Signal.SELL
        
        # RSI 从超卖区反弹
        elif rsi < self.oversold + 5 and momentum > 2:
            return Signal.STRONG_BUY
        
        # RSI 从超买区回落
        elif rsi > self.overbought - 5 and momentum < -2:
            return Signal.STRONG_SELL
        
        return Signal.HOLD
