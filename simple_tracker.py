import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

def get_china_stock_data(symbol, start_date, end_date):
    """
    Get historical stock data for Chinese stocks using yfinance
    """
    try:
        # Format symbol for Yahoo Finance (add .SS or .SZ for Shanghai/Shenzhen)
        if symbol.endswith('.SH'):
            formatted_symbol = symbol.replace('.SH', '.SS')
        elif symbol.endswith('.SS') or symbol.endswith('.SZ'):
            formatted_symbol = symbol
        else:
            # Try both extensions for Chinese stocks
            formatted_symbol = symbol + '.SS'
        
        stock = yf.Ticker(formatted_symbol)
        df = stock.history(start=start_date, end=end_date)
        
        if df.empty:
            # Try with .SZ extension if .SS didn't work
            if not symbol.endswith('.SZ'):
                formatted_symbol = symbol + '.SZ'
                stock = yf.Ticker(formatted_symbol)
                df = stock.history(start=start_date, end=end_date)
            
        if not df.empty:
            # Rename columns to match standard format
            df.rename(columns={
                'Open': 'open',
                'High': 'high', 
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume',
                'Adj Close': 'adj_close'
            }, inplace=True)
            
            # Calculate daily change
            df['pct_chg'] = df['close'].pct_change() * 100
            df['change'] = df['close'].diff()
        
        return df, formatted_symbol
    except Exception as e:
        print(f"Error getting data for {symbol}: {e}")
        return None, None

def calculate_simple_technical_indicators(df):
    """
    Calculate simple technical indicators
    """
    # Simple Moving Averages
    df['MA5'] = df['close'].rolling(window=5).mean()
    df['MA10'] = df['close'].rolling(window=10).mean()
    df['MA20'] = df['close'].rolling(window=20).mean()
    
    # RSI (Relative Strength Index) - simplified
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
    
    return df

def predict_next_price_simple(df):
    """
    Simple prediction based on linear regression of recent prices
    """
    from sklearn.linear_model import LinearRegression
    
    # Use last 30 days of data for prediction
    recent_data = df.tail(30)
    
    if len(recent_data) < 10:  # Need at least 10 data points
        return df['close'].iloc[-1]  # Return last known price if insufficient data
    
    # Prepare features (using day index as x-axis)
    X = np.arange(len(recent_data)).reshape(-1, 1)
    y = recent_data['close'].values
    
    # Train simple linear model
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict next day
    next_day = np.array([[len(recent_data)]])  # Next index
    predicted_price = model.predict(next_day)[0]
    
    return predicted_price

def plot_stock_analysis(df, symbol):
    """
    Plot stock analysis with technical indicators
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f'Stock Analysis for {symbol}', fontsize=16)
    
    # Price and Moving Averages
    axes[0, 0].plot(df.index, df['close'], label='Close Price', linewidth=2)
    axes[0, 0].plot(df.index, df['MA5'], label='MA5', alpha=0.7)
    axes[0, 0].plot(df.index, df['MA10'], label='MA10', alpha=0.7)
    axes[0, 0].plot(df.index, df['MA20'], label='MA20', alpha=0.7)
    
    # Add Bollinger Bands if available
    if 'BB_upper' in df.columns:
        axes[0, 0].fill_between(df.index, df['BB_upper'], df['BB_lower'], alpha=0.1, label='Bollinger Bands')
        axes[0, 0].plot(df.index, df['BB_upper'], linestyle='--', alpha=0.5)
        axes[0, 0].plot(df.index, df['BB_lower'], linestyle='--', alpha=0.5)
        axes[0, 0].plot(df.index, df['BB_middle'], linestyle='--', alpha=0.7)
    
    axes[0, 0].set_title('Price with Moving Averages and Bollinger Bands')
    axes[0, 0].set_xlabel('Date')
    axes[0, 0].set_ylabel('Price')
    axes[0, 0].legend()
    axes[0, 0].grid(True, linestyle='--', alpha=0.6)
    
    # Volume
    axes[0, 1].bar(df.index, df['volume'], alpha=0.7, width=1.0)
    axes[0, 1].set_title('Trading Volume')
    axes[0, 1].set_xlabel('Date')
    axes[0, 1].set_ylabel('Volume')
    axes[0, 1].grid(True, linestyle='--', alpha=0.6)
    
    # RSI
    if 'RSI' in df.columns:
        axes[1, 0].plot(df.index, df['RSI'], label='RSI', color='purple')
        axes[1, 0].axhline(y=70, color='r', linestyle='--', label='Overbought (70)')
        axes[1, 0].axhline(y=30, color='g', linestyle='--', label='Oversold (30)')
        axes[1, 0].set_title('RSI Indicator')
        axes[1, 0].set_xlabel('Date')
        axes[1, 0].set_ylabel('RSI Value')
        axes[1, 0].legend()
        axes[1, 0].grid(True, linestyle='--', alpha=0.6)
    else:
        axes[1, 0].text(0.5, 0.5, 'RSI not available', horizontalalignment='center', 
                        verticalalignment='center', transform=axes[1, 0].transAxes, fontsize=14)
        axes[1, 0].set_title('RSI Indicator')
    
    # Price Change
    axes[1, 1].plot(df.index, df['pct_chg'], label='Daily Change (%)', color='orange')
    axes[1, 1].axhline(y=0, color='black', linestyle='-', alpha=0.3)
    axes[1, 1].set_title('Daily Percentage Change')
    axes[1, 1].set_xlabel('Date')
    axes[1, 1].set_ylabel('Change (%)')
    axes[1, 1].grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    return fig

def main():
    """
    Main function to run the simplified China stock tracker
    """
    print("="*60)
    print("Welcome to Simplified China Stock Tracker")
    print("="*60)
    
    # Use a Chinese stock symbol that's more accessible
    stock_symbol = '600519.SS'  # Kweichow Moutai - a major Chinese company
    print(f"\nUsing Chinese stock symbol: {stock_symbol} (Kweichow Moutai)")
    
    # Get date range (last 6 months)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
    
    print(f"Start Date: {start_date}, End Date: {end_date}")
    
    # Collect data
    print(f"\nCollecting data for {stock_symbol}...")
    stock_data, actual_symbol = get_china_stock_data(stock_symbol, start_date, end_date)
    
    if stock_data is None or stock_data.empty:
        print(f"Failed to retrieve data for {stock_symbol}.")
        print("Make sure you have internet connection and the stock symbol is correct.")
        print("For Chinese stocks, common formats are:")
        print("- Shenzhen stocks: 000xxx.SZ or 000xxx")
        print("- Shanghai stocks: 600xxx.SS or 600xxx")
        return
    
    print(f"Successfully retrieved {len(stock_data)} days of data for {actual_symbol}")
    
    # Calculate technical indicators
    print("Calculating technical indicators...")
    stock_data = calculate_simple_technical_indicators(stock_data)
    
    # Display basic info
    print(f"\nLatest data for {actual_symbol}:")
    print(stock_data[['open', 'high', 'low', 'close', 'volume']].tail())
    
    # Make prediction for next day
    print("\nMaking prediction for next trading day...")
    predicted_price = predict_next_price_simple(stock_data)
    current_price = stock_data['close'].iloc[-1]
    
    print(f"Current price: {current_price:.2f}")
    print(f"Predicted next day price: {predicted_price:.2f}")
    print(f"Predicted change: {((predicted_price - current_price) / current_price) * 100:.2f}%")
    
    # Create visualizations
    print("\nGenerating visualizations...")
    fig = plot_stock_analysis(stock_data, actual_symbol)
    
    # Save the plot
    filename = f'data/{stock_symbol}_analysis.png'
    os.makedirs('data', exist_ok=True)  # Ensure data directory exists
    fig.savefig(filename)
    print(f"Chart saved as {filename}")
    
    print("\n" + "="*60)
    print("Analysis Complete!")
    print(f"Chart saved in the 'data' directory as {filename}")
    print("Note: This is a simplified version focusing on core functionality.")
    print("More advanced features require additional packages.")
    print("="*60)

if __name__ == "__main__":
    main()