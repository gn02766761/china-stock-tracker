"""
Market Strategies Module for China Stock Trading
包含多种 A 股市场交易策略
"""

from .base_strategy import BaseStrategy
from .trend_following import TrendFollowingStrategy
from .mean_reversion import MeanReversionStrategy
from .momentum import MomentumStrategy
from .bollinger_bands import BollingerBandsStrategy
from .macd_cross import MACDCrossStrategy
from .rsi_strategy import RSIStrategy
from .backtester import StrategyBacktester

__all__ = [
    'BaseStrategy',
    'TrendFollowingStrategy',
    'MeanReversionStrategy',
    'MomentumStrategy',
    'BollingerBandsStrategy',
    'MACDCrossStrategy',
    'RSIStrategy',
    'StrategyBacktester'
]
