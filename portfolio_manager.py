"""
投资组合管理模块

跟踪和管理股票投资组合，记录交易和盈亏
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from stock_database import StockDatabase
import sqlite3


class Position:
    """持仓类"""
    
    def __init__(self, symbol: str, shares: int, avg_cost: float):
        self.symbol = symbol
        self.shares = shares
        self.avg_cost = avg_cost
        self.current_price = 0.0
        self.buy_dates: List[datetime] = []
        self.sell_dates: List[datetime] = []
    
    def update_price(self, price: float):
        """更新当前价格"""
        self.current_price = price
    
    @property
    def market_value(self) -> float:
        """市值"""
        return self.shares * self.current_price
    
    @property
    def cost_basis(self) -> float:
        """成本"""
        return self.shares * self.avg_cost
    
    @property
    def unrealized_pnl(self) -> float:
        """未实现盈亏"""
        return self.market_value - self.cost_basis
    
    @property
    def unrealized_pnl_pct(self) -> float:
        """未实现盈亏百分比"""
        if self.cost_basis == 0:
            return 0.0
        return (self.unrealized_pnl / self.cost_basis) * 100
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'symbol': self.symbol,
            'shares': self.shares,
            'avg_cost': self.avg_cost,
            'current_price': self.current_price,
            'market_value': self.market_value,
            'cost_basis': self.cost_basis,
            'unrealized_pnl': self.unrealized_pnl,
            'unrealized_pnl_pct': self.unrealized_pnl_pct
        }


class Portfolio:
    """投资组合类"""
    
    def __init__(self, initial_cash: float = 1000000.0, db_path: str = 'data/portfolio.db'):
        """
        初始化投资组合
        
        Parameters
        ----------
        initial_cash : float
            初始资金
        db_path : str
            数据库路径
        """
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: Dict[str, Position] = {}
        self.db_path = db_path
        self.trade_history: List[Dict] = []
        
        # 初始化数据库
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                trade_date TEXT,
                trade_type TEXT,
                shares INTEGER,
                price REAL,
                amount REAL,
                commission REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio_snapshot (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_date TEXT,
                cash REAL,
                total_value REAL,
                total_cost REAL,
                total_pnl REAL,
                pnl_pct REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def buy(self, symbol: str, shares: int, price: float, 
            trade_date: str = None, commission_rate: float = 0.0003):
        """
        买入
        
        Parameters
        ----------
        symbol : str
            股票代码
        shares : int
            股数
        price : float
            价格
        trade_date : str
            交易日期
        commission_rate : float
            佣金费率
        """
        if trade_date is None:
            trade_date = datetime.now().strftime('%Y%m%d')
        
        amount = shares * price
        commission = amount * commission_rate
        total_cost = amount + commission
        
        if total_cost > self.cash:
            print(f"资金不足！需要 {total_cost:.2f}, 可用 {self.cash:.2f}")
            return False
        
        # 更新持仓
        if symbol in self.positions:
            position = self.positions[symbol]
            old_cost = position.shares * position.avg_cost
            new_shares = position.shares + shares
            new_cost = old_cost + amount
            position.avg_cost = new_cost / new_shares if new_shares > 0 else price
            position.shares = new_shares
        else:
            self.positions[symbol] = Position(symbol, shares, price)
        
        # 更新现金
        self.cash -= total_cost
        
        # 记录交易
        self.trade_history.append({
            'symbol': symbol,
            'trade_date': trade_date,
            'trade_type': 'BUY',
            'shares': shares,
            'price': price,
            'amount': amount,
            'commission': commission
        })
        
        # 保存到数据库
        self._save_trade(symbol, trade_date, 'BUY', shares, price, amount, commission)
        
        print(f"买入 {symbol} {shares} 股 @ {price:.2f}, 总计 {total_cost:.2f}")
        return True
    
    def sell(self, symbol: str, shares: int, price: float,
             trade_date: str = None, commission_rate: float = 0.0003):
        """
        卖出
        
        Parameters
        ----------
        symbol : str
            股票代码
        shares : int
            股数
        price : float
            价格
        trade_date : str
            交易日期
        commission_rate : float
            佣金费率
        """
        if trade_date is None:
            trade_date = datetime.now().strftime('%Y%m%d')
        
        if symbol not in self.positions:
            print(f"没有 {symbol} 的持仓")
            return False
        
        position = self.positions[symbol]
        
        if shares > position.shares:
            print(f"持仓不足！持有 {position.shares}, 卖出 {shares}")
            return False
        
        amount = shares * price
        commission = amount * commission_rate
        net_proceeds = amount - commission
        
        # 更新持仓
        position.shares -= shares
        if position.shares == 0:
            del self.positions[symbol]
        
        # 更新现金
        self.cash += net_proceeds
        
        # 记录交易
        self.trade_history.append({
            'symbol': symbol,
            'trade_date': trade_date,
            'trade_type': 'SELL',
            'shares': shares,
            'price': price,
            'amount': amount,
            'commission': commission
        })
        
        # 保存到数据库
        self._save_trade(symbol, trade_date, 'SELL', shares, price, amount, commission)
        
        print(f"卖出 {symbol} {shares} 股 @ {price:.2f}, 净得 {net_proceeds:.2f}")
        return True
    
    def _save_trade(self, symbol: str, trade_date: str, trade_type: str,
                    shares: int, price: float, amount: float, commission: float):
        """保存交易到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades (symbol, trade_date, trade_type, shares, price, amount, commission)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, trade_date, trade_type, shares, price, amount, commission))
        
        conn.commit()
        conn.close()
    
    def update_prices(self, price_dict: Dict[str, float]):
        """
        更新持仓价格
        
        Parameters
        ----------
        price_dict : Dict[str, float]
            股票代码 -> 价格 的字典
        """
        for symbol, price in price_dict.items():
            if symbol in self.positions:
                self.positions[symbol].update_price(price)
    
    def get_total_value(self) -> float:
        """获取总价值"""
        position_value = sum(pos.market_value for pos in self.positions.values())
        return self.cash + position_value
    
    def get_total_pnl(self) -> float:
        """获取总盈亏"""
        return self.get_total_value() - self.initial_cash
    
    def get_total_pnl_pct(self) -> float:
        """获取总盈亏百分比"""
        return (self.get_total_pnl() / self.initial_cash) * 100
    
    def get_position_summary(self) -> pd.DataFrame:
        """获取持仓汇总"""
        data = [pos.to_dict() for pos in self.positions.values()]
        if not data:
            return pd.DataFrame()
        return pd.DataFrame(data)
    
    def get_portfolio_summary(self) -> Dict:
        """获取组合汇总"""
        total_value = self.get_total_value()
        total_pnl = self.get_total_pnl()
        total_pnl_pct = self.get_total_pnl_pct()
        
        position_values = {
            symbol: pos.market_value for symbol, pos in self.positions.items()
        }
        
        # 计算持仓占比
        weights = {
            symbol: value / total_value if total_value > 0 else 0
            for symbol, value in position_values.items()
        }
        
        return {
            'cash': self.cash,
            'total_value': total_value,
            'total_pnl': total_pnl,
            'total_pnl_pct': total_pnl_pct,
            'position_count': len(self.positions),
            'positions': position_values,
            'weights': weights
        }
    
    def save_snapshot(self):
        """保存组合快照"""
        conn = sqlite3.connect(self.db_path)
        
        summary = self.get_portfolio_summary()
        total_cost = sum(pos.cost_basis for pos in self.positions.values())
        
        df = pd.DataFrame([{
            'snapshot_date': datetime.now().strftime('%Y%m%d'),
            'cash': summary['cash'],
            'total_value': summary['total_value'],
            'total_cost': total_cost,
            'total_pnl': summary['total_pnl'],
            'pnl_pct': summary['total_pnl_pct']
        }])
        
        df.to_sql('portfolio_snapshot', conn, if_exists='append', index=False)
        conn.close()
    
    def get_trade_history(self, symbol: str = None) -> pd.DataFrame:
        """获取交易历史"""
        conn = sqlite3.connect(self.db_path)
        
        if symbol:
            query = "SELECT * FROM trades WHERE symbol = ? ORDER BY trade_date DESC"
            df = pd.read_sql_query(query, conn, params=(symbol,))
        else:
            df = pd.read_sql_query("SELECT * FROM trades ORDER BY trade_date DESC", conn)
        
        conn.close()
        return df
    
    def print_summary(self):
        """打印组合摘要"""
        summary = self.get_portfolio_summary()
        
        print("\n" + "=" * 60)
        print("投资组合摘要")
        print("=" * 60)
        print(f"初始资金：{self.initial_cash:,.2f}")
        print(f"现金：{summary['cash']:,.2f}")
        print(f"持仓数量：{summary['position_count']}")
        print(f"总资产：{summary['total_value']:,.2f}")
        print(f"总盈亏：{summary['total_pnl']:,.2f} ({summary['total_pnl_pct']:.2f}%)")
        
        # 持仓详情
        position_df = self.get_position_summary()
        if not position_df.empty:
            print("\n持仓详情:")
            print(position_df[['symbol', 'shares', 'current_price', 'market_value', 
                              'unrealized_pnl', 'unrealized_pnl_pct']].to_string(index=False))
        
        print("=" * 60)


def run_portfolio_demo():
    """运行投资组合演示"""
    print("=" * 60)
    print("投资组合管理演示")
    print("=" * 60)
    
    # 创建组合
    portfolio = Portfolio(initial_cash=1000000)
    
    # 模拟交易
    print("\n执行模拟交易...")
    
    # 买入
    portfolio.buy('000001', 1000, 50.00, '20260115')
    portfolio.buy('600519', 200, 1500.00, '20260116')
    portfolio.buy('300750', 500, 300.00, '20260117')
    
    # 更新价格
    portfolio.update_prices({
        '000001': 55.00,
        '600519': 1600.00,
        '300750': 320.00
    })
    
    # 打印摘要
    portfolio.print_summary()
    
    # 卖出
    print("\n执行卖出...")
    portfolio.sell('000001', 500, 55.00, '20260215')
    
    # 获取交易历史
    print("\n交易历史:")
    history = portfolio.get_trade_history()
    print(history[['symbol', 'trade_date', 'trade_type', 'shares', 'price', 'amount']].to_string(index=False))
    
    # 保存快照
    portfolio.save_snapshot()
    
    print("\n演示完成!")


if __name__ == "__main__":
    run_portfolio_demo()
