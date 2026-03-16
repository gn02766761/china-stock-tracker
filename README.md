# China Stock Tracker and Predictor

This project provides a comprehensive solution for tracking and predicting Chinese stock prices using machine learning and technical analysis.

## Features

- **Data Collection**: Retrieve historical stock data for Chinese markets (Shanghai and Shenzhen)
- **Technical Indicators**: Calculate popular indicators like MA, EMA, MACD, RSI, Bollinger Bands
- **Machine Learning Models**: Multiple prediction models (Linear Regression, Random Forest, LSTM)
- **Visualization**: Interactive and static charts for data analysis
- **Backtesting**: Historical simulation to evaluate prediction accuracy

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone or download this repository
2. Install required packages:
```bash
pip install -r requirements.txt
```

If you encounter network timeouts during installation (common with large packages), install packages individually:
```bash
pip install pandas numpy matplotlib seaborn
pip install scikit-learn
pip install yfinance tushare
pip install plotly
pip install tensorflow  # This is large and may take time
```

### Troubleshooting Installation Issues

If you face network timeout issues during installation:

1. **Retry with timeout settings**:
```bash
pip install --timeout 600 package_name
```

2. **Use a different pip index**:
```bash
pip install -i https://pypi.org/simple/ package_name
```

3. **Install packages one by one** rather than all at once

### Additional Setup for Enhanced Data Access

For more comprehensive data access, you can use Tushare:
1. Register at [Tushare](https://tushare.pro/) to get a free token
2. The application will prompt you to enter your token when you run it

### Alternative: Try the Demo Version

If installation proves challenging, try the demo version that uses mock data:
```bash
python demo_tracker.py
```
This will showcase all features without requiring external data sources or complex dependencies.

## Usage

Run the main application:
```bash
python main.py
```

Follow the prompts to:
1. Enter a Chinese stock symbol (e.g., '000001' for Ping An Bank)
2. Select a prediction model
3. View results and visualizations

## Project Structure

```
China_stock_trade/
├── main.py                 # Main application entry point
├── requirements.txt        # Project dependencies
├── data/                   # Generated charts and data files
├── models/
│   └── stock_predictor.py  # ML models for prediction
├── utils/
│   └── data_collector.py   # Data collection utilities
└── visualization/
    └── visualizer.py       # Chart generation utilities
```

## Data Sources

The application uses multiple data sources:
- **Yahoo Finance**: For general stock data (fallback)
- **Tushare**: For more comprehensive Chinese market data (optional with token)

## Models

The project implements three prediction models:

1. **Linear Regression**: Fast and interpretable
2. **Random Forest**: More complex, often more accurate
3. **LSTM Neural Network**: Deep learning approach for sequential patterns

## Visualizations

The application generates several types of visualizations:

- Interactive dashboard with multiple panels
- Candlestick charts
- Technical indicator plots
- Volume charts
- Backtesting results
- Correlation matrices

## Output Files

After running the analysis, you'll find these files in the `data/` directory:
- PNG files: Static charts
- HTML files: Interactive charts that can be opened in a web browser

## Limitations

- Stock prediction is inherently uncertain
- Past performance does not guarantee future results
- Market conditions can change rapidly
- Free data sources may have limitations on frequency and completeness

## Disclaimer

This tool is for educational and research purposes only. It is not financial advice. 
Always do your own research and consult with qualified professionals before making investment decisions.