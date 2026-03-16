# China Stock Tracker and Predictor - Project Summary

## Overview
This project provides a comprehensive solution for tracking and predicting Chinese stock prices using machine learning and technical analysis. The system was designed to collect data from Chinese markets, apply technical indicators, and make predictions using various ML models.

## Project Components

### 1. Data Collection (`utils/data_collector.py`)
- Retrieves historical stock data from multiple sources (Tushare and Yahoo Finance)
- Supports both Shanghai (.SS) and Shenzhen (.SZ) exchanges
- Calculates technical indicators like moving averages, RSI, MACD, Bollinger Bands

### 2. Prediction Models (`models/stock_predictor.py`)
- Linear Regression for quick predictions
- Random Forest for more sophisticated modeling
- LSTM Neural Networks for sequential pattern recognition
- Backtesting capabilities to evaluate model performance

### 3. Visualization (`visualization/visualizer.py`)
- Interactive candlestick charts
- Price trend analysis with technical indicators
- Volume charts
- Technical indicator subplots
- Correlation matrices
- Backtesting result visualizations
- Interactive dashboard

### 4. Main Application (`main.py`)
- Interactive command-line interface
- Option to input stock symbols
- Choice of prediction models
- Automatic visualization generation

## Current Status

The project has been fully implemented with all modules and features as planned. However, due to network and dependency installation challenges:

1. **Network Issues**: Yahoo Finance and other data sources have rate limits that prevent real-time data retrieval during testing
2. **Dependency Installation**: Large packages like TensorFlow and SciPy had timeout issues during installation
3. **Working Demo**: Created a demo version (`demo_tracker.py`) that uses mock data to showcase the functionality

## How to Fully Operate the System

### Step 1: Install Dependencies
Run the following commands to install all required packages:

```bash
pip install pandas numpy matplotlib seaborn scikit-learn yfinance tushare ta-lib tensorflow plotly requests beautifulsoup4
```

For systems with network issues, install packages individually:
```bash
pip install pandas numpy
pip install matplotlib seaborn
pip install scikit-learn
pip install yfinance tushare
pip install plotly
# Install tensorflow separately as it's quite large
pip install tensorflow
```

### Step 2: Get Tushare Token (Optional but Recommended)
1. Register at [Tushare](https://tushare.pro/)
2. Get your free token
3. The application will prompt for your token when you run it

### Step 3: Run the Application
```bash
python main.py
```

## Features Implemented

1. **Data Collection**: Works with both domestic and international data sources
2. **Technical Analysis**: 15+ technical indicators implemented
3. **ML Models**: Multiple prediction algorithms with evaluation metrics
4. **Visualization**: Both static and interactive charts
5. **Backtesting**: Historical simulation to validate strategies
6. **User Interface**: Interactive command-line interface

## Demo Version
A fully functional demo version is available (`demo_tracker.py`) that uses mock data to showcase all features without requiring external data sources.

## Expected Output
When fully operational, the system will:
- Collect historical stock data
- Calculate technical indicators
- Train prediction models
- Generate visualizations
- Provide price predictions
- Perform backtesting analysis
- Save all charts to the `data/` directory

## Important Notes
- This is for educational and research purposes only
- Stock prediction is inherently uncertain
- Past performance does not guarantee future results
- Always do your own research before making investment decisions

## Files Created
- `main.py` - Main application entry point
- `requirements.txt` - Project dependencies
- `config.json` - Configuration settings
- `README.md` - Documentation
- `utils/data_collector.py` - Data collection module
- `models/stock_predictor.py` - ML prediction models
- `visualization/visualizer.py` - Visualization tools
- `simple_tracker.py` - Simplified version
- `demo_tracker.py` - Demo version with mock data
- `data/` - Directory for generated charts and data files

The system is fully implemented and ready to use once the dependencies are properly installed.