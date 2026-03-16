import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

def generate_mock_stock_data(days=180, start_price=100):
    """
    Generate mock stock data for demonstration purposes
    """
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    # Filter out weekends
    dates = dates[dates.weekday < 5]  # Monday to Friday
    
    # Generate realistic-looking stock prices with trend and volatility
    np.random.seed(42)  # For reproducible results
    returns = np.random.normal(0.0005, 0.02, len(dates))  # Daily returns ~0.05% average, 2% std
    prices = [start_price]
    
    for ret in returns[1:]:
        new_price = prices[-1] * (1 + ret)
        prices.append(new_price)
    
    df = pd.DataFrame({
        'close': prices,
        'open': [p * np.random.uniform(0.99, 1.01) for p in prices],
        'high': [p * np.random.uniform(1.005, 1.03) for p in prices],
        'low': [p * np.random.uniform(0.97, 0.995) for p in prices],
        'volume': np.random.randint(1000000, 10000000, len(prices))
    }, index=dates)
    
    # Ensure OHLC constraints
    for idx in df.index:
        df.loc[idx, 'open'] = max(df.loc[idx, 'low'], min(df.loc[idx, 'high'], df.loc[idx, 'open']))
        df.loc[idx, 'close'] = max(df.loc[idx, 'low'], min(df.loc[idx, 'high'], df.loc[idx, 'close']))
    
    # Calculate daily change
    df['pct_chg'] = df['close'].pct_change() * 100
    df['change'] = df['close'].diff()
    
    return df.dropna()

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
    # Use last 30 days of data for prediction
    recent_data = df.tail(30)
    
    if len(recent_data) < 10:  # Need at least 10 data points
        return df['close'].iloc[-1]  # Return last known price if insufficient data
    
    # Prepare features (using day index as x-axis)
    X = np.arange(len(recent_data))
    y = recent_data['close'].values
    
    # Calculate slope and intercept for simple linear regression
    n = len(X)
    sum_x = np.sum(X)
    sum_y = np.sum(y)
    sum_xy = np.sum(X * y)
    sum_x2 = np.sum(X ** 2)
    
    # Linear regression formula: y = mx + b
    m = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
    b = (sum_y - m * sum_x) / n
    
    # Predict next day (index = len(recent_data))
    next_day = len(recent_data)
    predicted_price = m * next_day + b
    
    return predicted_price

def plot_stock_analysis(df, symbol):
    """
    Plot stock analysis with technical indicators
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f'Stock Analysis for {symbol} (Mock Data)', fontsize=16)
    
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
    Main function to run the demo China stock tracker
    """
    print("="*60)
    print("Welcome to Demo China Stock Tracker and Predictor")
    print("(Using Mock Data for Demonstration)")
    print("="*60)
    
    # Generate mock data
    print("\nGenerating mock stock data for demonstration...")
    stock_data = generate_mock_stock_data(days=180, start_price=100)
    
    print(f"Successfully generated {len(stock_data)} days of mock data")
    
    # Calculate technical indicators
    print("Calculating technical indicators...")
    stock_data = calculate_simple_technical_indicators(stock_data)
    
    # Display basic info
    print(f"\nLatest mock data:")
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
    fig = plot_stock_analysis(stock_data, "Demo Stock (Mock Data)")
    
    # Save the plot
    os.makedirs('data', exist_ok=True)  # Ensure data directory exists
    filename = 'data/demo_stock_analysis.png'
    fig.savefig(filename)
    print(f"Chart saved as {filename}")
    
    # Show the plot
    plt.show()
    
    print("\n" + "="*60)
    print("Demo Analysis Complete!")
    print(f"Chart saved in the 'data' directory as {filename}")
    print("\nNote: This demo uses mock data to illustrate functionality.")
    print("In a real implementation, you would connect to live data sources.")
    print("The full application includes additional features like:")
    print("- Real-time data collection from multiple sources")
    print("- Advanced ML prediction models (Random Forest, LSTM)")
    print("- Interactive visualizations with Plotly")
    print("- Backtesting capabilities")
    print("="*60)

if __name__ == "__main__":
    main()