"""
布林带策略 (Bollinger Bands Strategy)

基于布林带的均值回归和突破策略：
- 价格触及下轨：买入
- 价格触及上轨：卖出
- 价格突破布林带：趋势跟随
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from .base_strategy import BaseStrategy, Signal


class BollingerBandsStrategy(BaseStrategy):
    """
    布林带策略
    
    Parameters
    ----------
    period : int
        布林带周期，默认 20
    std_dev : float
        标准差倍数，默认 2.0
    use_breakout : bool
        是否启用突破模式，默认 False
    """
    
    def __init__(self, period: int = 20, std_dev: float = 2.0, 
                 use_breakout: bool = False):
        params = {
            'period': period,
            'std_dev': std_dev,
            'use_breakout': use_breakout
        }
        super().__init__('Bollinger Bands', params)
        self.period = period
        self.std_dev = std_dev
        self.use_breakout = use_breakout
    
    def calculate_bollinger_bands(self, prices: pd.Series) -> Dict:
        """
        计算布林带
        
        Returns
        -------
        Dict
            包含上轨、中轨、下轨的字典
        """
        if len(prices) < self.period:
            return {
                'upper': None,
                'middle': None,
                'lower': None,
                'bandwidth': None,
                'percent_b': None
            }
        
        middle = prices.tail(self.period).mean()
        std = prices.tail(self.period).std()
        upper = middle + self.std_dev * std
        lower = middle - self.std_dev * std
        
        current_price = prices.iloc[-1]
        bandwidth = (upper - lower) / middle * 100 if middle != 0 else 0
        percent_b = (current_price - lower) / (upper - lower) if upper != lower else 0.5
        
        return {
            'upper': upper,
            'middle': middle,
            'lower': lower,
            'bandwidth': bandwidth,
            'percent_b': percent_b,
            'std': std
        }
    
    def generate_signal(self, data: pd.DataFrame) -> Signal:
        """
        生成布林带策略信号
        
        标准模式（均值回归）：
        - 触及下轨：BUY
        - 触及上轨：SELL
        
        突破模式（趋势跟随）：
        - 突破上轨：BUY
        - 跌破下轨：SELL
        """
        if len(data) < self.period:
            return Signal.HOLD
        
        prices = data['close']
        bb = self.calculate_bollinger_bands(prices)
        
        if bb['upper'] is None:
            return Signal.HOLD
        
        current_price = prices.iloc[-1]
        
        if self.use_breakout:
            # 突破模式
            if current_price > bb['upper']:
                return Signal.BUY  # 向上突破
            elif current_price < bb['lower']:
                return Signal.SELL  # 向下跌破
        else:
            # 均值回归模式
            if current_price <= bb['lower'] * 1.001:  # 触及或跌破下轨
                return Signal.BUY
            elif current_price >= bb['upper'] * 0.999:  # 触及或突破上轨
                return Signal.SELL
            
            # 接近轨道时的强信号
            if bb['percent_b'] < 0.1:  # 非常接近下轨
                return Signal.STRONG_BUY
            elif bb['percent_b'] > 0.9:  # 非常接近上轨
                return Signal.STRONG_SELL
        
        return Signal.HOLD
    
    def get_band_position(self, data: pd.DataFrame) -> Dict:
        """
        获取价格在布林带中的位置信息
        
        Returns
        -------
        Dict
            包含位置信息的字典
        """
        if len(data) < self.period:
            return {
                'position': 'unknown',
                'percent_b': 0.0,
                'bandwidth': 0.0,
                'squeeze': False
            }
        
        prices = data['close']
        bb = self.calculate_bollinger_bands(prices)
        
        percent_b = bb['percent_b']
        bandwidth = bb['bandwidth']
        
        # 判断位置
        if percent_b < 0.2:
            position = 'near_lower'  # 靠近下轨
        elif percent_b > 0.8:
            position = 'near_upper'  # 靠近上轨
        elif percent_b < 0.4:
            position = 'below_middle'  # 中轨下方
        elif percent_b > 0.6:
            position = 'above_middle'  # 中轨上方
        else:
            position = 'near_middle'  # 靠近中轨
        
        # 布林带挤压（低波动率，可能即将突破）
        # 使用历史带宽的百分位来判断
        squeeze = bandwidth < 10  # 带宽小于 10% 视为挤压
        
        return {
            'position': position,
            'percent_b': percent_b,
            'bandwidth': bandwidth,
            'squeeze': squeeze,
            'upper': bb['upper'],
            'middle': bb['middle'],
            'lower': bb['lower']
        }


class BollingerBandsBreakoutStrategy(BaseStrategy):
    """
    布林带突破策略
    
    专门用于捕捉布林带突破后的趋势行情
    """
    
    def __init__(self, period: int = 20, std_dev: float = 2.0,
                 confirmation_bars: int = 2):
        params = {
            'period': period,
            'std_dev': std_dev,
            'confirmation_bars': confirmation_bars
        }
        super().__init__('BB Breakout', params)
        self.period = period
        self.std_dev = std_dev
        self.confirmation_bars = confirmation_bars
    
    def generate_signal(self, data: pd.DataFrame) -> Signal:
        """生成布林带突破信号"""
        if len(data) < self.period + self.confirmation_bars:
            return Signal.HOLD
        
        prices = data['close']
        
        # 计算布林带
        middle = prices.rolling(window=self.period).mean()
        std = prices.rolling(window=self.period).std()
        upper = middle + self.std_dev * std
        lower = middle - self.std_dev * std
        
        # 检查连续突破
        upper_breakout_count = 0
        lower_breakout_count = 0
        
        for i in range(self.confirmation_bars):
            idx = -1 - i
            if prices.iloc[idx] > upper.iloc[idx]:
                upper_breakout_count += 1
            elif prices.iloc[idx] < lower.iloc[idx]:
                lower_breakout_count += 1
        
        # 确认突破
        if upper_breakout_count >= self.confirmation_bars:
            return Signal.BUY
        elif lower_breakout_count >= self.confirmation_bars:
            return Signal.SELL
        
        return Signal.HOLD
