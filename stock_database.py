"""
股票数据数据库模块

用于存储和查询股票历史价格、技术指标和趋势数据
支持 2026 年 1 月至今的数据收集
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import os


class StockDatabase:
    """股票数据库管理类"""
    
    def __init__(self, db_path: str = 'data/stock_data.db'):
        """
        初始化数据库
        
        Parameters
        ----------
        db_path : str
            数据库文件路径
        """
        self.db_path = db_path
        
        # 确保目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # 创建数据库连接
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        # 创建表
        self._create_tables()
    
    def _create_tables(self):
        """创建数据库表"""
        cursor = self.conn.cursor()
        
        # 股票基本信息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stocks (
                symbol TEXT PRIMARY KEY,
                name TEXT,
                market TEXT,
                industry TEXT,
                list_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 股票日线数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                trade_date TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                pre_close REAL,
                change REAL,
                pct_chg REAL,
                vol REAL,
                amount REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, trade_date),
                FOREIGN KEY (symbol) REFERENCES stocks(symbol)
            )
        ''')
        
        # 技术指标表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS technical_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                trade_date TEXT,
                ma5 REAL,
                ma10 REAL,
                ma20 REAL,
                ma30 REAL,
                ma60 REAL,
                ema12 REAL,
                ema26 REAL,
                macd REAL,
                macd_signal REAL,
                macd_hist REAL,
                rsi REAL,
                kdj_k REAL,
                kdj_d REAL,
                kdj_j REAL,
                bb_upper REAL,
                bb_middle REAL,
                bb_lower REAL,
                atr REAL,
                obv REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, trade_date),
                FOREIGN KEY (symbol) REFERENCES stocks(symbol)
            )
        ''')
        
        # 趋势信号表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trend_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                trade_date TEXT,
                trend_type TEXT,
                trend_strength TEXT,
                signal_type TEXT,
                signal_score REAL,
                ma_trend TEXT,
                macd_trend TEXT,
                rsi_status TEXT,
                volume_status TEXT,
                recommendation TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, trade_date),
                FOREIGN KEY (symbol) REFERENCES stocks(symbol)
            )
        ''')
        
        # 推荐记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                rec_date TEXT,
                price REAL,
                score REAL,
                recommendation TEXT,
                target_price REAL,
                stop_loss REAL,
                risk_level TEXT,
                reasons TEXT,
                result_price REAL,
                result_return REAL,
                is_success INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (symbol) REFERENCES stocks(symbol)
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_prices_symbol_date ON daily_prices(symbol, trade_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_indicators_symbol_date ON technical_indicators(symbol, trade_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trends_symbol_date ON trend_signals(symbol, trade_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_recs_symbol ON recommendations(symbol)')
        
        self.conn.commit()
    
    def insert_stock_info(self, symbol: str, name: str, market: str = 'A', 
                         industry: str = '', list_date: str = ''):
        """插入股票基本信息"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO stocks (symbol, name, market, industry, list_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (symbol, name, market, industry, list_date))
        self.conn.commit()
    
    def insert_daily_prices(self, symbol: str, prices_df: pd.DataFrame):
        """
        插入日线数据
        
        Parameters
        ----------
        symbol : str
            股票代码
        prices_df : pd.DataFrame
            价格数据，包含列：trade_date, open, high, low, close, pre_close, 
            change, pct_chg, vol, amount
        """
        cursor = self.conn.cursor()
        
        for _, row in prices_df.iterrows():
            cursor.execute('''
                INSERT OR REPLACE INTO daily_prices 
                (symbol, trade_date, open, high, low, close, pre_close, 
                 change, pct_chg, vol, amount)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                row.get('trade_date', ''),
                row.get('open', 0),
                row.get('high', 0),
                row.get('low', 0),
                row.get('close', 0),
                row.get('pre_close', 0),
                row.get('change', 0),
                row.get('pct_chg', 0),
                row.get('vol', 0),
                row.get('amount', 0)
            ))
        
        self.conn.commit()
    
    def insert_technical_indicators(self, symbol: str, indicators_df: pd.DataFrame):
        """
        插入技术指标数据
        
        Parameters
        ----------
        symbol : str
            股票代码
        indicators_df : pd.DataFrame
            技术指标数据
        """
        cursor = self.conn.cursor()
        
        for _, row in indicators_df.iterrows():
            cursor.execute('''
                INSERT OR REPLACE INTO technical_indicators 
                (symbol, trade_date, ma5, ma10, ma20, ma30, ma60,
                 ema12, ema26, macd, macd_signal, macd_hist,
                 rsi, kdj_k, kdj_d, kdj_j, bb_upper, bb_middle, 
                 bb_lower, atr, obv)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                        ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                row.get('trade_date', ''),
                row.get('ma5', 0),
                row.get('ma10', 0),
                row.get('ma20', 0),
                row.get('ma30', 0),
                row.get('ma60', 0),
                row.get('ema12', 0),
                row.get('ema26', 0),
                row.get('macd', 0),
                row.get('macd_signal', 0),
                row.get('macd_hist', 0),
                row.get('rsi', 0),
                row.get('kdj_k', 0),
                row.get('kdj_d', 0),
                row.get('kdj_j', 0),
                row.get('bb_upper', 0),
                row.get('bb_middle', 0),
                row.get('bb_lower', 0),
                row.get('atr', 0),
                row.get('obv', 0)
            ))
        
        self.conn.commit()
    
    def insert_trend_signal(self, symbol: str, trade_date: str, 
                           trend_data: Dict):
        """插入趋势信号"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO trend_signals 
            (symbol, trade_date, trend_type, trend_strength, signal_type,
             signal_score, ma_trend, macd_trend, rsi_status, volume_status,
             recommendation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            symbol,
            trade_date,
            trend_data.get('trend_type', ''),
            trend_data.get('trend_strength', ''),
            trend_data.get('signal_type', ''),
            trend_data.get('signal_score', 0),
            trend_data.get('ma_trend', ''),
            trend_data.get('macd_trend', ''),
            trend_data.get('rsi_status', ''),
            trend_data.get('volume_status', ''),
            trend_data.get('recommendation', 'HOLD')
        ))
        self.conn.commit()
    
    def get_stock_prices(self, symbol: str, start_date: str = '20260101', 
                        end_date: str = None) -> pd.DataFrame:
        """
        获取股票价格数据
        
        Parameters
        ----------
        symbol : str
            股票代码
        start_date : str
            开始日期，格式 YYYYMMDD
        end_date : str
            结束日期，默认今天
        
        Returns
        -------
        pd.DataFrame
            价格数据
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        
        query = '''
            SELECT * FROM daily_prices 
            WHERE symbol = ? AND trade_date BETWEEN ? AND ?
            ORDER BY trade_date ASC
        '''
        
        return pd.read_sql_query(query, self.conn, params=(symbol, start_date, end_date))
    
    def get_technical_indicators(self, symbol: str, 
                                start_date: str = '20260101') -> pd.DataFrame:
        """获取技术指标数据"""
        query = '''
            SELECT * FROM technical_indicators 
            WHERE symbol = ? AND trade_date >= ?
            ORDER BY trade_date ASC
        '''
        
        return pd.read_sql_query(query, self.conn, params=(symbol, start_date))
    
    def get_latest_trend_signals(self, symbol: str = None, 
                                limit: int = 100) -> pd.DataFrame:
        """
        获取最新的趋势信号
        
        Parameters
        ----------
        symbol : str, optional
            股票代码，None 表示所有股票
        limit : int
            返回记录数限制
        """
        if symbol:
            query = '''
                SELECT * FROM trend_signals 
                WHERE symbol = ?
                ORDER BY trade_date DESC
                LIMIT ?
            '''
            return pd.read_sql_query(query, self.conn, params=(symbol, limit))
        else:
            query = '''
                SELECT t.*, s.name 
                FROM trend_signals t
                LEFT JOIN stocks s ON t.symbol = s.symbol
                ORDER BY t.trade_date DESC, t.signal_score DESC
                LIMIT ?
            '''
            return pd.read_sql_query(query, self.conn, params=(limit,))
    
    def get_buy_recommendations(self, start_date: str = '20260101') -> pd.DataFrame:
        """获取买入推荐的股票"""
        query = '''
            SELECT * FROM recommendations 
            WHERE recommendation IN ('STRONG_BUY', 'BUY')
            AND rec_date >= ?
            ORDER BY rec_date DESC, score DESC
        '''
        
        return pd.read_sql_query(query, self.conn, params=(start_date,))
    
    def get_stock_pool_analysis(self, symbols: List[str]) -> pd.DataFrame:
        """
        获取股票池综合分析
        
        Parameters
        ----------
        symbols : List[str]
            股票代码列表
        
        Returns
        -------
        pd.DataFrame
            综合分析结果
        """
        if not symbols:
            return pd.DataFrame()
        
        placeholders = ','.join('?' * len(symbols))
        
        query = f'''
            SELECT 
                t.symbol,
                s.name,
                t.trade_date,
                t.signal_score,
                t.recommendation,
                t.trend_strength,
                d.close as price,
                d.pct_chg,
                d.vol
            FROM trend_signals t
            LEFT JOIN stocks s ON t.symbol = s.symbol
            LEFT JOIN daily_prices d ON t.symbol = d.symbol 
                AND t.trade_date = d.trade_date
            WHERE t.symbol IN ({placeholders})
            AND t.trade_date = (
                SELECT MAX(trade_date) FROM trend_signals 
                WHERE symbol = t.symbol
            )
            ORDER BY t.signal_score DESC
        '''
        
        return pd.read_sql_query(query, self.conn, params=symbols)
    
    def get_price_trend_analysis(self, symbol: str, 
                                start_date: str = '20260101') -> Dict:
        """
        获取价格趋势分析
        
        Parameters
        ----------
        symbol : str
            股票代码
        start_date : str
            开始日期
        
        Returns
        -------
        Dict
            趋势分析结果
        """
        # 获取价格数据
        prices = self.get_stock_prices(symbol, start_date)
        
        if prices.empty:
            return {}
        
        # 计算趋势指标
        latest = prices.iloc[-1]
        
        # 均线趋势
        ma5 = prices['close'].tail(5).mean()
        ma10 = prices['close'].tail(10).mean()
        ma20 = prices['close'].tail(20).mean()
        
        # 价格位置
        current_price = latest['close']
        price_vs_ma20 = (current_price - ma20) / ma20 * 100 if ma20 > 0 else 0
        
        # 成交量趋势
        avg_vol_5 = prices['vol'].tail(5).mean()
        avg_vol_20 = prices['vol'].tail(20).mean()
        vol_trend = (avg_vol_5 - avg_vol_20) / avg_vol_20 * 100 if avg_vol_20 > 0 else 0
        
        # 价格趋势
        price_change_5d = prices['close'].pct_change(5).iloc[-1] * 100 if len(prices) > 5 else 0
        price_change_10d = prices['close'].pct_change(10).iloc[-1] * 100 if len(prices) > 10 else 0
        
        return {
            'symbol': symbol,
            'trade_date': latest.get('trade_date', ''),
            'current_price': current_price,
            'ma5': ma5,
            'ma10': ma10,
            'ma20': ma20,
            'price_vs_ma20_pct': price_vs_ma20,
            'ma_trend': 'BULLISH' if current_price > ma20 else 'BEARISH',
            'vol_trend_pct': vol_trend,
            'price_change_5d': price_change_5d,
            'price_change_10d': price_change_10d,
            'trend_strength': 'STRONG' if abs(price_change_5d) > 5 else 'NORMAL'
        }
    
    def export_to_csv(self, symbol: str, output_path: str = None):
        """导出股票数据到 CSV"""
        if output_path is None:
            output_path = f'data/{symbol}_analysis.csv'
        
        # 获取价格和技术指标
        prices = self.get_stock_prices(symbol)
        indicators = self.get_technical_indicators(symbol)
        
        # 合并数据
        if not prices.empty:
            merged = pd.merge(prices, indicators, on=['symbol', 'trade_date'], how='left')
            merged.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"数据已导出到：{output_path}")
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def create_sample_database():
    """创建示例数据库用于测试"""
    db = StockDatabase()
    
    # 添加示例股票（使用真实股票信息）
    stocks = [
        ('000001', '平安银行', 'A', '银行', '19910403'),
        ('000002', '万科 A', 'A', '房地产', '19910129'),
        ('600519', '贵州茅台', 'A', '白酒', '20010827'),
    ]
    
    for symbol, name, market, industry, list_date in stocks:
        db.insert_stock_info(symbol, name, market, industry, list_date)
    
    # 添加示例数据（使用真实价格范围）
    np.random.seed(42)
    dates = pd.date_range(start='2026-01-01', end=datetime.now().strftime('%Y-%m-%d'), freq='B')
    
    # 真实价格范围
    stock_prices = {
        '000001': 15.0,   # 平安银行 ~15 元
        '000002': 8.0,    # 万科 A ~8 元
        '600519': 1500.0  # 贵州茅台 ~1500 元
    }
    
    for symbol in ['000001', '000002', '600519']:
        initial_price = stock_prices[symbol]
        # 使用更合理的波动率（日波动约 2-3%）
        returns = np.random.normal(0.0002, 0.025, len(dates))
        prices = initial_price * np.cumprod(1 + returns)
        
        # 确保价格在合理范围
        prices = np.clip(prices, initial_price * 0.5, initial_price * 2.0)
        
        prices_df = pd.DataFrame({
            'symbol': symbol,
            'trade_date': dates.strftime('%Y%m%d'),
            'open': prices * (1 + np.random.randn(len(prices)) * 0.005),
            'high': prices * (1 + np.abs(np.random.randn(len(prices)) * 0.015)),
            'low': prices * (1 - np.abs(np.random.randn(len(prices)) * 0.015)),
            'close': prices,
            'pre_close': np.roll(prices, 1),
            'change': np.diff(prices, prepend=prices[0]),
            'pct_chg': np.random.randn(len(prices)) * 2,
            'vol': np.random.randint(1000000, 50000000, len(prices)),
            'amount': np.random.randint(10000000, 500000000, len(prices))
        })
        
        # 确保 high >= close >= low
        prices_df['high'] = np.maximum(prices_df['high'], prices_df['close'])
        prices_df['low'] = np.minimum(prices_df['low'], prices_df['close'])
        
        db.insert_daily_prices(symbol, prices_df)
    
    print("示例数据库创建成功!")
    return db


if __name__ == "__main__":
    # 创建示例数据库
    db = create_sample_database()
    
    # 测试查询
    print("\n测试查询 000001 的价格数据:")
    prices = db.get_stock_prices('000001')
    print(f"获取到 {len(prices)} 条记录")
    print(prices.tail())
    
    # 测试趋势分析
    print("\n测试趋势分析:")
    trend = db.get_price_trend_analysis('000001')
    print(trend)
    
    db.close()
