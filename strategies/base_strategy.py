"""
基础策略类 - 所有交易策略的抽象基类
"""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from enum import Enum


class Signal(Enum):
    """交易信号类型"""
    BUY = 1           # 买入信号
    SELL = -1         # 卖出信号
    HOLD = 0          # 持有/观望
    STRONG_BUY = 2    # 强烈买入
    STRONG_SELL = -2  # 强烈卖出


class Trade:
    """表示一笔交易"""
    
    def __init__(self, entry_date: pd.Timestamp, entry_price: float, 
                 shares: int, direction: str = 'long'):
        self.entry_date = entry_date
        self.entry_price = entry_price
        self.shares = shares
        self.direction = direction  # 'long' or 'short'
        self.exit_date: Optional[pd.Timestamp] = None
        self.exit_price: Optional[float] = None
        self.pnl: float = 0.0
        self.return_pct: float = 0.0
    
    def close(self, exit_date: pd.Timestamp, exit_price: float):
        """平仓"""
        self.exit_date = exit_date
        self.exit_price = exit_price
        
        if self.direction == 'long':
            self.pnl = (exit_price - self.entry_price) * self.shares
        else:
            self.pnl = (self.entry_price - exit_price) * self.shares
        
        self.return_pct = (self.pnl / (self.entry_price * self.shares)) * 100
    
    def __repr__(self):
        return f"Trade({self.entry_date}, Entry: {self.entry_price:.2f}, Exit: {self.exit_price:.2f}, PnL: {self.pnl:.2f})"


class Portfolio:
    """模拟投资组合"""
    
    def __init__(self, initial_cash: float = 1000000.0):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: Dict[str, int] = {}  # symbol -> shares
        self.trades: List[Trade] = []
        self.current_trade: Optional[Trade] = None
        self.value_history: List[float] = []
    
    def open_position(self, date: pd.Timestamp, price: float, shares: int):
        """开仓"""
        cost = price * shares
        if cost > self.cash:
            shares = int(self.cash / price)  # 使用全部可用资金
            cost = price * shares
        
        if shares > 0:
            self.cash -= cost
            self.current_trade = Trade(date, price, shares)
    
    def close_position(self, date: pd.Timestamp, price: float):
        """平仓"""
        if self.current_trade:
            self.current_trade.close(date, price)
            self.trades.append(self.current_trade)
            self.cash += self.current_trade.exit_price * self.current_trade.shares
            self.current_trade = None
    
    def get_total_value(self, current_price: float) -> float:
        """获取总价值"""
        position_value = sum(self.positions.values()) * current_price if self.positions else 0
        if self.current_trade:
            position_value = self.current_trade.shares * current_price
        return self.cash + position_value
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        if not self.trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'total_return_pct': 0.0,
                'avg_return_pct': 0.0,
                'max_drawdown': 0.0,
                'sharpe_ratio': 0.0
            }
        
        winning = [t for t in self.trades if t.pnl > 0]
        losing = [t for t in self.trades if t.pnl <= 0]
        
        total_pnl = sum(t.pnl for t in self.trades)
        returns = [t.return_pct for t in self.trades]
        
        # 计算最大回撤
        cumulative_returns = np.cumprod([1 + r/100 for r in returns])
        peak = np.maximum.accumulate(cumulative_returns)
        drawdown = (peak - cumulative_returns) / peak
        max_drawdown = np.max(drawdown) * 100 if len(drawdown) > 0 else 0
        
        # 计算夏普比率
        if len(returns) > 1:
            avg_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe_ratio = (avg_return / std_return) * np.sqrt(252) if std_return > 0 else 0
        else:
            sharpe_ratio = 0
        
        return {
            'total_trades': len(self.trades),
            'winning_trades': len(winning),
            'losing_trades': len(losing),
            'win_rate': len(winning) / len(self.trades) * 100,
            'total_pnl': total_pnl,
            'total_return_pct': (total_pnl / self.initial_cash) * 100,
            'avg_return_pct': np.mean(returns),
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio
        }


class BaseStrategy(ABC):
    """
    所有交易策略的抽象基类
    """
    
    def __init__(self, name: str, params: Optional[Dict] = None):
        self.name = name
        self.params = params or {}
        self.signals: List[Signal] = []
        self.signal_dates: List[pd.Timestamp] = []
    
    @abstractmethod
    def generate_signal(self, data: pd.DataFrame) -> Signal:
        """
        根据市场数据生成交易信号
        
        Parameters
        ----------
        data : pd.DataFrame
            包含 OHLCV 和技术指标的数据
        
        Returns
        -------
        Signal
            交易信号 (BUY, SELL, HOLD 等)
        """
        pass
    
    def analyze(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        分析数据并生成信号序列
        
        Parameters
        ----------
        data : pd.DataFrame
            历史市场数据
        
        Returns
        -------
        pd.DataFrame
            包含信号的数据
        """
        signals = []
        dates = []
        
        for idx in range(len(data)):
            subset = data.iloc[:idx+1].copy()
            signal = self.generate_signal(subset)
            signals.append(signal)
            dates.append(data.index[idx])
        
        self.signals = signals
        self.signal_dates = dates
        
        result = data.copy()
        result['signal'] = [s.value for s in signals]
        result['signal_name'] = [s.name for s in signals]
        
        return result
    
    def backtest(self, data: pd.DataFrame, initial_cash: float = 1000000.0) -> Portfolio:
        """
        回测策略
        
        Parameters
        ----------
        data : pd.DataFrame
            历史市场数据
        initial_cash : float
            初始资金
        
        Returns
        -------
        Portfolio
            回测结果
        """
        portfolio = Portfolio(initial_cash)
        result_data = self.analyze(data)
        
        for idx in range(len(result_data)):
            row = result_data.iloc[idx]
            signal = self.signals[idx]
            price = row['close']
            date = result_data.index[idx]
            
            if signal in [Signal.BUY, Signal.STRONG_BUY] and portfolio.current_trade is None:
                # 确定买入股数
                shares = int(portfolio.cash * 0.95 / price)  # 使用 95% 资金
                if shares > 0:
                    portfolio.open_position(date, price, shares)
            
            elif signal in [Signal.SELL, Signal.STRONG_SELL] and portfolio.current_trade is not None:
                portfolio.close_position(date, price)
            
            # 记录组合价值
            portfolio.value_history.append(portfolio.get_total_value(price))
        
        return portfolio
    
    def get_params_info(self) -> str:
        """获取参数信息"""
        return f"{self.name}: {self.params}"
    
    def __repr__(self):
        return f"{self.name}(params={self.params})"
