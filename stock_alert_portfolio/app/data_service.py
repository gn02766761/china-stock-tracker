"""
数据获取模块
复用现有项目的数据收集功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, List


class StockDataService:
    """股票数据服务类"""
    
    def __init__(self):
        self.cache = {}  # 简单的数据缓存
        self.cache_expiry = 300  # 缓存过期时间 (秒)
    
    def _get_stock_suffix(self, stock_code: str) -> str:
        """根据股票代码添加市场后缀"""
        if stock_code.startswith('6'):
            return f"{stock_code}.SS"  # 上海证券交易所
        elif stock_code.startswith('0') or stock_code.startswith('3'):
            return f"{stock_code}.SZ"  # 深圳证券交易所
        return stock_code
    
    def get_stock_data(self, stock_code: str, days: int = 60) -> Optional[pd.DataFrame]:
        """
        获取股票历史数据
        
        Args:
            stock_code: 股票代码
            days: 获取天数
            
        Returns:
            DataFrame 包含 OHLCV 数据
        """
        # 检查缓存
        cache_key = f"{stock_code}_{days}"
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if (datetime.now() - timestamp).total_seconds() < self.cache_expiry:
                return data
        
        try:
            symbol = self._get_stock_suffix(stock_code)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 使用 yfinance 获取数据
            df = yf.download(symbol, start=start_date, end=end_date, progress=False)
            
            if df.empty:
                return None
            
            # 处理列名
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            df = df.reset_index()
            
            # 标准化列名
            column_mapping = {
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'vol',
                'Adj Close': 'adj_close'
            }
            df = df.rename(columns=column_mapping)
            
            # 确保有日期列
            if 'Date' in df.columns:
                df['date'] = df['Date']
            
            # 缓存数据
            self.cache[cache_key] = (df, datetime.now())
            
            return df
            
        except Exception as e:
            print(f"获取数据失败 {stock_code}: {e}")
            return None
    
    def get_current_price(self, stock_code: str) -> Optional[float]:
        """获取当前价格 (最新收盘价)"""
        data = self.get_stock_data(stock_code, days=5)
        if data is not None and not data.empty:
            return data['close'].iloc[-1]
        return None
    
    def get_price_change(self, stock_code: str) -> Optional[float]:
        """获取涨跌幅 (%)"""
        data = self.get_stock_data(stock_code, days=5)
        if data is not None and len(data) >= 2:
            current = data['close'].iloc[-1]
            previous = data['close'].iloc[-2]
            return ((current - previous) / previous) * 100
        return None
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算技术指标
        
        Args:
            df: 股票数据 DataFrame
            
        Returns:
            添加技术指标后的 DataFrame
        """
        if df is None or df.empty:
            return df
        
        df = df.copy()
        
        # 移动平均线
        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma10'] = df['close'].rolling(window=10).mean()
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['ma60'] = df['close'].rolling(window=20).mean()
        
        # EMA
        df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
        
        # MACD
        df['macd'] = df['ema12'] - df['ema26']
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # 布林带
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        
        return df
    
    def get_stock_info(self, stock_code: str) -> dict:
        """获取股票基本信息"""
        try:
            symbol = self._get_stock_suffix(stock_code)
            stock = yf.Ticker(symbol)
            info = stock.info
            
            return {
                'name': info.get('shortName', stock_code),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'pb_ratio': info.get('priceToBook', 0),
            }
        except Exception as e:
            return {
                'name': stock_code,
                'sector': 'N/A',
                'industry': 'N/A',
                'market_cap': 0,
                'pe_ratio': 0,
                'pb_ratio': 0,
            }
