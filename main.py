import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.data_collector import StockDataCollector, get_default_start_end_dates
from models.stock_predictor import StockPredictor, backtest_strategy
from visualization.visualizer import StockVisualizer, create_dashboard
import warnings
warnings.filterwarnings('ignore')

def main():
    """
    Main function to run the China stock tracker and predictor
    """
    print("="*60)
    print("Welcome to China Stock Tracker and Predictor")
    print("="*60)
    
    # Initialize modules
    collector = StockDataCollector()  # Initialize without token initially
    predictor = StockPredictor()
    visualizer = StockVisualizer()
    
    # Get user input
    print("\nPlease enter the stock symbol (e.g., '000001' for Ping An Bank):")
    stock_symbol = input("Stock Symbol: ").strip()
    
    if not stock_symbol:
        print("Using default stock: 000001 (Ping An Bank)")
        stock_symbol = '000001'
    
    # Get date range
    print("\nGetting default date range (last year)...")
    start_date, end_date = get_default_start_end_dates()
    print(f"Start Date: {start_date}, End Date: {end_date}")
    
    # Collect data
    print(f"\nCollecting data for {stock_symbol}...")
    stock_data = collector.get_stock_data(stock_symbol, start_date, end_date)
    
    if stock_data is None or stock_data.empty:
        print(f"Failed to retrieve data for {stock_symbol}. Trying with .SS extension...")
        # Try with .SS extension
        stock_data = collector.get_stock_data(stock_symbol + '.SS', start_date, end_date)
        
        if stock_data is None or stock_data.empty:
            print(f"Also failed with .SS extension. Trying .SZ extension...")
            stock_data = collector.get_stock_data(stock_symbol + '.SZ', start_date, end_date)
    
    if stock_data is None or stock_data.empty:
        print(f"Failed to retrieve data for {stock_symbol} from all sources.")
        print("Make sure you have internet connection and the stock symbol is correct.")
        print("For Chinese stocks, common formats are:")
        print("- Shenzhen stocks: 000xxx.SZ or 000xxx")
        print("- Shanghai stocks: 600xxx.SS or 600xxx")
        return
    
    print(f"Successfully retrieved {len(stock_data)} days of data for {stock_symbol}")
    
    # Calculate technical indicators
    print("Calculating technical indicators...")
    stock_data = collector.calculate_technical_indicators(stock_data)
    
    # Display basic info
    print(f"\nLatest data for {stock_symbol}:")
    print(stock_data[['open', 'high', 'low', 'close', 'vol']].tail())
    
    # Ask user for prediction method
    print("\nSelect prediction method:")
    print("1. Linear Regression (faster)")
    print("2. Random Forest (more accurate)")
    choice = input("Enter choice (1 or 2, default 1): ").strip()
    
    if choice == '2':
        model_type = 'random_forest'
        print("Training Random Forest model...")
        predictor.train_random_forest(stock_data)
    else:
        model_type = 'linear'
        print("Training Linear Regression model...")
        predictor.train_linear_regression(stock_data)
    
    # Make prediction for next day
    print("\nMaking prediction for next trading day...")
    try:
        next_day_prediction = predictor.predict(stock_data, model_type=model_type)
        current_price = stock_data['close'].iloc[-1]
        
        print(f"Current price: {current_price:.2f}")
        print(f"Predicted next day price: {next_day_prediction:.2f}")
        print(f"Predicted change: {((next_day_prediction - current_price) / current_price) * 100:.2f}%")
    except Exception as e:
        print(f"Could not make prediction: {e}")
    
    # Perform backtesting
    print("\nPerforming backtesting (last 30 days)...")
    try:
        backtest_results = backtest_strategy(stock_data.tail(60), predictor, prediction_days=30)
        print(f"Backtest completed for {len(backtest_results)} days")
    except Exception as e:
        print(f"Backtesting failed: {e}")
    
    # Visualizations
    print("\nGenerating visualizations...")
    
    # 1. Price with indicators
    try:
        fig1 = visualizer.plot_price_with_indicators(stock_data, f"{stock_symbol} - Price with Indicators")
        fig1.savefig(f'data/{stock_symbol}_price_indicators.png')
        print("Saved: data/{stock_symbol}_price_indicators.png")
    except Exception as e:
        print(f"Error creating price chart: {e}")
    
    # 2. Volume chart
    try:
        fig2 = visualizer.plot_volume(stock_data, f"{stock_symbol} - Trading Volume")
        fig2.savefig(f'data/{stock_symbol}_volume.png')
        print("Saved: data/{stock_symbol}_volume.png")
    except Exception as e:
        print(f"Error creating volume chart: {e}")
    
    # 3. Technical indicators
    try:
        fig3 = visualizer.plot_technical_indicators(stock_data)
        fig3.write_html(f"data/{stock_symbol}_tech_indicators.html")
        print("Saved: data/{stock_symbol}_tech_indicators.html")
    except Exception as e:
        print(f"Error creating technical indicators chart: {e}")
    
    # 4. Dashboard
    try:
        fig4 = create_dashboard(stock_data, f"{stock_symbol} - Analysis Dashboard")
        fig4.write_html(f"data/{stock_symbol}_dashboard.html")
        print("Saved: data/{stock_symbol}_dashboard.html")
    except Exception as e:
        print(f"Error creating dashboard: {e}")
    
    # 5. Correlation matrix
    try:
        fig5 = visualizer.plot_correlation_matrix(stock_data)
        fig5.savefig(f'data/{stock_symbol}_correlation_matrix.png')
        print("Saved: data/{stock_symbol}_correlation_matrix.png")
    except Exception as e:
        print(f"Error creating correlation matrix: {e}")
    
    # Backtest results visualization
    if 'backtest_results' in locals() and not backtest_results.empty:
        try:
            fig6 = visualizer.plot_backtest_results(backtest_results, f"{stock_symbol} - Backtest Results")
            fig6.savefig(f'data/{stock_symbol}_backtest_results.png')
            print("Saved: data/{stock_symbol}_backtest_results.png")
        except Exception as e:
            print(f"Error creating backtest chart: {e}")
    
    print("\n" + "="*60)
    print("Analysis Complete!")
    print("Generated files are saved in the 'data' directory")
    print("HTML files can be opened in a web browser for interactive charts")
    print("PNG files contain static charts")
    print("="*60)
    
    # Ask if user wants to see more options
    print("\nAdditional options:")
    print("1. Analyze another stock")
    print("2. Exit")
    option = input("Enter your choice: ").strip()
    
    if option == '1':
        main()  # Recursive call to analyze another stock
    else:
        print("Thank you for using China Stock Tracker and Predictor!")


def setup_tushare():
    """
    Helper function to set up tushare token if available
    """
    print("If you have a Tushare token for more comprehensive data access:")
    print("Visit https://tushare.pro/ to register and get a free token")
    token = input("Enter your Tushare token (or press Enter to skip): ").strip()
    
    if token:
        try:
            import tushare as ts
            ts.set_token(token)
            pro = ts.pro_api()
            # Test the token
            df = pro.query('trade_cal', exchange='', start_date='20230101', end_date='20230102')
            print("Tushare token validated successfully!")
            return token
        except Exception as e:
            print(f"Error validating token: {e}")
            return None
    return None


if __name__ == "__main__":
    # Check if user wants to set up tushare
    print("Setting up China Stock Tracker and Predictor")
    token = setup_tushare()
    
    # Run main application
    main()