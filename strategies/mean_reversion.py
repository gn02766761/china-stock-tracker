"""
均值回归策略 (Mean Reversion Strategy)

基于价格会回归均值的假设：
- 当价格远低于均线时买入
- 当价格远高于均线时卖出
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from .base_strategy import BaseStrategy, Signal


class MeanReversionStrategy(BaseStrategy):
    """
    均值回归策略
    
    Parameters
    ----------
    ma_period : int
        均线周期，默认 20
    std_threshold : float
        标准差阈值（多少倍标准差触发信号），默认 2.0
    use_bollinger : bool
        是否使用布林带逻辑，默认 True
    """
    
    def __init__(self, ma_period: int = 20, std_threshold: float = 2.0, 
                 use_bollinger: bool = True):
        params = {
            'ma_period': ma_period,
            'std_threshold': std_threshold,
            'use_bollinger': use_bollinger
        }
        super().__init__('Mean Reversion', params)
        self.ma_period = ma_period
        self.std_threshold = std_threshold
        self.use_bollinger = use_bollinger
    
    def _calculate_zscore(self, prices: pd.Series) -> float:
        """计算价格的 Z-Score"""
        if len(prices) < self.ma_period:
            return 0.0
        
        ma = prices.tail(self.ma_period).mean()
        std = prices.tail(self.ma_period).std()
        
        if std == 0:
            return 0.0
        
        current_price = prices.iloc[-1]
        zscore = (current_price - ma) / std
        
        return zscore
    
    def generate_signal(self, data: pd.DataFrame) -> Signal:
        """
        生成均值回归信号
        
        信号规则：
        - Z-Score < -threshold：价格过低，买入
        - Z-Score > threshold：价格过高，卖出
        - 其他：持有
        """
        if len(data) < self.ma_period:
            return Signal.HOLD
        
        prices = data['close']
        zscore = self._calculate_zscore(prices)
        
        # 价格低于均值 2 倍标准差 - 超卖，买入
        if zscore < -self.std_threshold:
            return Signal.BUY
        
        # 价格高于均值 2 倍标准差 - 超买，卖出
        elif zscore > self.std_threshold:
            return Signal.SELL
        
        # 价格低于均值 1.5 倍标准差 - 较强买入信号
        elif zscore < -self.std_threshold * 0.75:
            return Signal.STRONG_BUY
        
        # 价格高于均值 1.5 倍标准差 - 较强卖出信号
        elif zscore > self.std_threshold * 0.75:
            return Signal.STRONG_SELL
        
        return Signal.HOLD
    
    def get_mean_reversion_potential(self, data: pd.DataFrame) -> Dict:
        """
        获取均值回归潜力指标
        
        Returns
        -------
        Dict
            包含回归潜力信息的字典
        """
        if len(data) < self.ma_period:
            return {
                'zscore': 0.0,
                'distance_from_ma': 0.0,
                'direction': 'neutral'
            }
        
        prices = data['close']
        ma = prices.tail(self.ma_period).mean()
        std = prices.tail(self.ma_period).std()
        current_price = prices.iloc[-1]
        
        zscore = self._calculate_zscore(prices)
        distance_pct = (current_price - ma) / ma * 100
        
        if zscore < -self.std_threshold:
            direction = 'oversold'  # 超卖
        elif zscore > self.std_threshold:
            direction = 'overbought'  # 超买
        else:
            direction = 'neutral'
        
        return {
            'zscore': zscore,
            'distance_from_ma': distance_pct,
            'direction': direction,
            'ma_value': ma,
            'std_value': std
        }


class PairsTradingStrategy(BaseStrategy):
    """
    配对交易策略（统计套利）
    
    寻找两个高度相关的股票，当它们的价差偏离历史均值时进行交易
    """
    
    def __init__(self, lookback_period: int = 60, entry_threshold: float = 2.0,
                 exit_threshold: float = 0.5):
        params = {
            'lookback_period': lookback_period,
            'entry_threshold': entry_threshold,
            'exit_threshold': exit_threshold
        }
        super().__init__('Pairs Trading', params)
        self.lookback_period = lookback_period
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.hedge_ratio = None
    
    def calculate_spread(self, price_a: pd.Series, price_b: pd.Series) -> pd.Series:
        """计算两只股票的价差"""
        # 使用 OLS 计算对冲比率
        if len(price_a) < self.lookback_period or len(price_b) < self.lookback_period:
            return pd.Series()
        
        # 简化版本：假设 1:1 对冲
        spread = price_a - price_b
        return spread
    
    def generate_signal(self, data: pd.DataFrame) -> Signal:
        """
        生成配对交易信号
        
        注意：这个策略需要两只股票的数据，这里简化为单只股票的自回归
        """
        if len(data) < self.lookback_period:
            return Signal.HOLD
        
        # 简化版本：使用价格与移动均值的偏离
        prices = data['close']
        ma = prices.rolling(window=self.lookback_period).mean()
        std = prices.rolling(window=self.lookback_period).std()
        
        spread = prices - ma
        zscore = spread / std
        
        current_zscore = zscore.iloc[-1]
        prev_zscore = zscore.iloc[-2] if len(zscore) > 1 else 0
        
        # 价差从极端位置回归
        if abs(prev_zscore) > self.entry_threshold and abs(current_zscore) < self.exit_threshold:
            if prev_zscore > 0:
                return Signal.BUY  # 价差回归，买入
            else:
                return Signal.SELL
        
        # 价差扩大到阈值外
        if current_zscore > self.entry_threshold:
            return Signal.SELL  # 价差过大，卖出
        elif current_zscore < -self.entry_threshold:
            return Signal.BUY  # 价差过小，买入
        
        return Signal.HOLD
