import pandas as pd
import numpy as np
import tushare as ts
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class StockDataCollector:
    """
    A class to collect China stock market data from various sources
    """
    
    def __init__(self, token=None):
        """
        Initialize the collector with tushare token if available
        """
        if token:
            ts.set_token(token)
            self.pro = ts.pro_api()
        else:
            # If no token, we'll use yfinance as fallback
            self.pro = None
    
    def get_china_stock_list(self):
        """
        Get the list of all China stocks
        """
        if self.pro:
            try:
                # Get stock list from tushare
                stock_list = self.pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
                return stock_list
            except Exception as e:
                print(f"Error getting stock list from tushare: {e}")
                return None
        else:
            print("Tushare token not provided, returning empty list")
            return pd.DataFrame(columns=['ts_code', 'symbol', 'name', 'area', 'industry', 'list_date'])
    
    def get_stock_data_tushare(self, symbol, start_date, end_date):
        """
        Get historical stock data using tushare
        """
        if not self.pro:
            raise ValueError("Tushare token not provided")
        
        try:
            df = self.pro.daily(ts_code=symbol, start_date=start_date, end_date=end_date)
            # Convert date column to datetime
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            df.set_index('trade_date', inplace=True)
            # Sort by date
            df.sort_index(inplace=True)
            return df
        except Exception as e:
            print(f"Error getting data for {symbol}: {e}")
            return None
    
    def get_stock_data_yfinance(self, symbol, start_date, end_date):
        """
        Get historical stock data using Yahoo Finance
        Note: Need to format symbols appropriately for China stocks
        """
        try:
            # Format symbol for Yahoo Finance (add .SS or .SZ for Shanghai/Shenzhen)
            if symbol.endswith('.SH'):
                formatted_symbol = symbol.replace('.SH', '.SS')
            elif not any(symbol.endswith(ext) for ext in ['.SS', '.SZ']):
                # Try both extensions for Chinese stocks
                formatted_symbol = symbol + '.SS'
            
            stock = yf.Ticker(formatted_symbol)
            df = stock.history(start=start_date, end=end_date)
            
            if df.empty:
                # Try with .SZ extension if .SS didn't work
                formatted_symbol = symbol + '.SZ'
                stock = yf.Ticker(formatted_symbol)
                df = stock.history(start=start_date, end=end_date)
                
            if not df.empty:
                # Rename columns to match tushare format
                df.rename(columns={
                    'Open': 'open',
                    'High': 'high', 
                    'Low': 'low',
                    'Close': 'close',
                    'Volume': 'vol',
                    'Adj Close': 'adj_close'
                }, inplace=True)
                
                # Calculate daily change
                df['pct_chg'] = df['close'].pct_change() * 100
                df['change'] = df['close'].diff()
            
            return df
        except Exception as e:
            print(f"Error getting data for {symbol} from Yahoo Finance: {e}")
            return None
    
    def get_stock_data(self, symbol, start_date, end_date, source='auto'):
        """
        Get historical stock data with automatic source selection
        """
        if source == 'tushare' and self.pro:
            return self.get_stock_data_tushare(symbol, start_date, end_date)
        elif source == 'yfinance':
            return self.get_stock_data_yfinance(symbol, start_date, end_date)
        else:
            # Auto-select: try tushare first, fall back to yfinance
            if self.pro:
                data = self.get_stock_data_tushare(symbol, start_date, end_date)
                if data is not None and not data.empty:
                    return data
            
            # Fallback to yfinance
            return self.get_stock_data_yfinance(symbol, start_date, end_date)
    
    def calculate_technical_indicators(self, df):
        """
        Calculate technical indicators for the stock data
        """
        # Simple Moving Averages
        df['MA5'] = df['close'].rolling(window=5).mean()
        df['MA10'] = df['close'].rolling(window=10).mean()
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['MA30'] = df['close'].rolling(window=30).mean()
        
        # Exponential Moving Averages
        df['EMA12'] = df['close'].ewm(span=12).mean()
        df['EMA26'] = df['close'].ewm(span=26).mean()
        
        # MACD
        df['MACD'] = df['EMA12'] - df['EMA26']
        df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_histogram'] = df['MACD'] - df['MACD_signal']
        
        # RSI (Relative Strength Index)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['BB_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
        df['BB_lower'] = df['BB_middle'] - (bb_std * 2)
        
        # Volatility (20-day standard deviation)
        df['volatility'] = df['close'].rolling(window=20).std()
        
        # Price Rate of Change
        df['ROC'] = ((df['close'] - df['close'].shift(10)) / df['close'].shift(10)) * 100
        
        return df


def get_default_start_end_dates():
    """
    Get default start and end dates for data collection
    """
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
    return start_date, end_date


if __name__ == "__main__":
    # Example usage
    collector = StockDataCollector()
    start_date, end_date = get_default_start_end_dates()
    
    # Get data for a sample stock (Ping An Bank as example)
    stock_data = collector.get_stock_data('000001', start_date, end_date)
    
    if stock_data is not None:
        print(f"Retrieved {len(stock_data)} days of data")
        print(stock_data.head())
    else:
        print("Failed to retrieve stock data")