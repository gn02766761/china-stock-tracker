"""
MACD 交叉策略 (MACD Cross Strategy)

基于 MACD 指标的动量策略：
- MACD 线上穿信号线：买入（金叉）
- MACD 线下穿信号线：卖出（死叉）
- MACD 柱状图变化：确认趋势强度
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from .base_strategy import BaseStrategy, Signal


class MACDCrossStrategy(BaseStrategy):
    """
    MACD 交叉策略
    
    Parameters
    ----------
    fast_period : int
        快线 EMA 周期，默认 12
    slow_period : int
        慢线 EMA 周期，默认 26
    signal_period : int
        信号线周期，默认 9
    use_histogram : bool
        是否使用柱状图确认，默认 True
    """
    
    def __init__(self, fast_period: int = 12, slow_period: int = 26,
                 signal_period: int = 9, use_histogram: bool = True):
        params = {
            'fast_period': fast_period,
            'slow_period': slow_period,
            'signal_period': signal_period,
            'use_histogram': use_histogram
        }
        super().__init__('MACD Cross', params)
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.use_histogram = use_histogram
        self.prev_macd = None
        self.prev_signal = None
    
    def calculate_macd(self, prices: pd.Series) -> Dict:
        """
        计算 MACD 指标
        
        Returns
        -------
        Dict
            包含 MACD 线、信号线、柱状图的字典
        """
        if len(prices) < self.slow_period + self.signal_period:
            return {
                'macd': None,
                'signal': None,
                'histogram': None,
                'divergence': None
            }
        
        # 计算 EMA
        ema_fast = prices.ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = prices.ewm(span=self.slow_period, adjust=False).mean()
        
        # MACD 线
        macd_line = ema_fast - ema_slow
        
        # 信号线
        signal_line = macd_line.ewm(span=self.signal_period, adjust=False).mean()
        
        # 柱状图
        histogram = macd_line - signal_line
        
        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        current_histogram = histogram.iloc[-1]
        
        # 前一期值
        prev_macd = macd_line.iloc[-2] if len(macd_line) > 1 else current_macd
        prev_signal = signal_line.iloc[-2] if len(signal_line) > 1 else current_signal
        prev_histogram = histogram.iloc[-2] if len(histogram) > 1 else current_histogram
        
        # 背离检测
        divergence = None
        if len(prices) >= 20:
            # 价格创新高但 MACD 未创新高 = 顶背离
            # 价格创新低但 MACD 未创新低 = 底背离
            recent_high = prices.tail(10).max()
            recent_low = prices.tail(10).min()
            
            if prices.iloc[-1] == recent_high and current_macd < macd_line.tail(10).max():
                divergence = 'bearish'  # 顶背离
            elif prices.iloc[-1] == recent_low and current_macd > macd_line.tail(10).min():
                divergence = 'bullish'  # 底背离
        
        return {
            'macd': current_macd,
            'signal': current_signal,
            'histogram': current_histogram,
            'prev_macd': prev_macd,
            'prev_signal': prev_signal,
            'prev_histogram': prev_histogram,
            'divergence': divergence
        }
    
    def generate_signal(self, data: pd.DataFrame) -> Signal:
        """
        生成 MACD 交叉信号
        
        信号规则：
        - 金叉（MACD 上穿信号线）：BUY
        - 死叉（MACD 下穿信号线）：SELL
        - 柱状图确认趋势强度
        """
        if len(data) < self.slow_period + self.signal_period:
            return Signal.HOLD
        
        prices = data['close']
        macd_data = self.calculate_macd(prices)
        
        if macd_data['macd'] is None:
            return Signal.HOLD
        
        macd = macd_data['macd']
        signal = macd_data['signal']
        prev_macd = macd_data['prev_macd']
        prev_signal = macd_data['prev_signal']
        histogram = macd_data['histogram']
        prev_histogram = macd_data['prev_histogram']
        
        # 金叉：MACD 从下方上穿信号线
        if prev_macd <= prev_signal and macd > signal:
            if self.use_histogram and histogram > 0:
                return Signal.STRONG_BUY
            return Signal.BUY
        
        # 死叉：MACD 从上方下穿信号线
        if prev_macd >= prev_signal and macd < signal:
            if self.use_histogram and histogram < 0:
                return Signal.STRONG_SELL
            return Signal.SELL
        
        # 柱状图增强信号
        if self.use_histogram:
            # 柱状图连续放大 - 趋势加强
            if histogram > prev_histogram > 0:
                return Signal.BUY  # 多头加强
            elif histogram < prev_histogram < 0:
                return Signal.SELL  # 空头加强
            
            # 柱状图背离
            if macd_data['divergence'] == 'bullish':
                return Signal.BUY
            elif macd_data['divergence'] == 'bearish':
                return Signal.SELL
        
        # MACD 在零轴上方 - 多头市场
        if macd > 0 and macd > signal:
            return Signal.BUY
        elif macd < 0 and macd < signal:
            return Signal.SELL
        
        return Signal.HOLD
    
    def get_macd_analysis(self, data: pd.DataFrame) -> Dict:
        """
        获取详细的 MACD 分析
        
        Returns
        -------
        Dict
            包含 MACD 各项指标的字典
        """
        if len(data) < self.slow_period + self.signal_period:
            return {
                'macd': 0.0,
                'signal': 0.0,
                'histogram': 0.0,
                'trend': 'neutral',
                'strength': 0.0,
                'divergence': None
            }
        
        prices = data['close']
        macd_data = self.calculate_macd(prices)
        
        macd = macd_data['macd']
        signal = macd_data['signal']
        histogram = macd_data['histogram']
        
        # 趋势判断
        if macd > signal and macd > 0:
            trend = 'bullish'
        elif macd < signal and macd < 0:
            trend = 'bearish'
        elif macd > signal:
            trend = 'weak_bullish'
        else:
            trend = 'weak_bearish'
        
        # 强度（基于柱状图）
        strength = abs(histogram) / abs(macd) if macd != 0 else 0
        
        return {
            'macd': macd,
            'signal': signal,
            'histogram': histogram,
            'trend': trend,
            'strength': strength,
            'divergence': macd_data['divergence']
        }


class MACDHistogramStrategy(BaseStrategy):
    """
    MACD 柱状图策略
    
    专注于 MACD 柱状图的变化来捕捉动量转变
    """
    
    def __init__(self, fast_period: int = 12, slow_period: int = 26,
                 signal_period: int = 9, consecutive_bars: int = 3):
        params = {
            'fast_period': fast_period,
            'slow_period': slow_period,
            'signal_period': signal_period,
            'consecutive_bars': consecutive_bars
        }
        super().__init__('MACD Histogram', params)
        self.consecutive_bars = consecutive_bars
    
    def generate_signal(self, data: pd.DataFrame) -> Signal:
        """基于柱状图连续变化生成信号"""
        if len(data) < 50:
            return Signal.HOLD
        
        prices = data['close']
        
        # 计算 MACD
        ema_fast = prices.ewm(span=12, adjust=False).mean()
        ema_slow = prices.ewm(span=26, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        
        # 检查柱状图连续变化
        increasing_count = 0
        decreasing_count = 0
        
        for i in range(self.consecutive_bars):
            if len(histogram) < i + 2:
                break
            
            current = histogram.iloc[-1 - i]
            prev = histogram.iloc[-2 - i]
            
            if current > prev:
                increasing_count += 1
            elif current < prev:
                decreasing_count += 1
        
        # 柱状图连续上升 - 动量转向多头
        if increasing_count >= self.consecutive_bars:
            return Signal.BUY
        
        # 柱状图连续下降 - 动量转向空头
        elif decreasing_count >= self.consecutive_bars:
            return Signal.SELL
        
        return Signal.HOLD
