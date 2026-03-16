import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Set style for matplotlib
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class StockVisualizer:
    """
    A class to visualize stock data and predictions
    """
    
    def __init__(self):
        pass
    
    def plot_candlestick_chart(self, df, title="Stock Candlestick Chart"):
        """
        Create a candlestick chart for stock data
        """
        fig = go.Figure(data=[go.Candlestick(x=df.index,
                                             open=df['open'],
                                             high=df['high'],
                                             low=df['low'],
                                             close=df['close'])])
        
        fig.update_layout(
            title=title,
            xaxis_title='Date',
            yaxis_title='Price',
            xaxis_rangeslider_visible=False
        )
        
        return fig
    
    def plot_price_with_indicators(self, df, title="Stock Price with Technical Indicators"):
        """
        Plot stock price with technical indicators
        """
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Plot closing price
        ax.plot(df.index, df['close'], label='Close Price', linewidth=2)
        
        # Plot moving averages if available
        if 'MA5' in df.columns:
            ax.plot(df.index, df['MA5'], label='MA5', alpha=0.7)
        if 'MA10' in df.columns:
            ax.plot(df.index, df['MA10'], label='MA10', alpha=0.7)
        if 'MA20' in df.columns:
            ax.plot(df.index, df['MA20'], label='MA20', alpha=0.7)
        if 'MA30' in df.columns:
            ax.plot(df.index, df['MA30'], label='MA30', alpha=0.7)
        
        # Plot Bollinger Bands if available
        if 'BB_upper' in df.columns and 'BB_lower' in df.columns:
            ax.fill_between(df.index, df['BB_upper'], df['BB_lower'], 
                           alpha=0.1, label='Bollinger Bands')
            ax.plot(df.index, df['BB_upper'], linestyle='--', alpha=0.5)
            ax.plot(df.index, df['BB_lower'], linestyle='--', alpha=0.5)
            ax.plot(df.index, df['BB_middle'], linestyle='--', alpha=0.7, label='BB Middle')
        
        ax.set_title(title)
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.legend(loc='best')
        ax.grid(True, linestyle='--', alpha=0.6)
        
        plt.tight_layout()
        return fig
    
    def plot_volume(self, df, title="Trading Volume"):
        """
        Plot trading volume
        """
        fig, ax = plt.subplots(figsize=(14, 6))
        
        ax.bar(df.index, df['vol'], alpha=0.7, width=1.0)
        ax.set_title(title)
        ax.set_xlabel('Date')
        ax.set_ylabel('Volume')
        ax.grid(True, linestyle='--', alpha=0.6)
        
        plt.tight_layout()
        return fig
    
    def plot_technical_indicators(self, df):
        """
        Plot multiple technical indicators in subplots
        """
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Price with Moving Averages', 'RSI', 'MACD'),
            row_width=[0.33, 0.33, 0.33]
        )
        
        # Plot price and moving averages
        fig.add_trace(go.Scatter(x=df.index, y=df['close'], name='Close'), row=1, col=1)
        if 'MA5' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['MA5'], name='MA5'), row=1, col=1)
        if 'MA10' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['MA10'], name='MA10'), row=1, col=1)
        if 'MA20' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name='MA20'), row=1, col=1)
        
        # Plot RSI
        if 'RSI' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI'), row=2, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        # Plot MACD
        if 'MACD' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD'), row=3, col=1)
        if 'MACD_signal' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['MACD_signal'], name='MACD Signal'), row=3, col=1)
        
        fig.update_layout(height=800, title_text="Technical Indicators Analysis")
        return fig
    
    def plot_predictions_vs_actual(self, actual_df, predictions, title="Actual vs Predicted Prices"):
        """
        Plot actual vs predicted prices
        """
        fig, ax = plt.subplots(figsize=(14, 8))
        
        ax.plot(actual_df.index, actual_df['close'], label='Actual Price', linewidth=2)
        ax.plot(actual_df.index[-len(predictions):], predictions, 
                label='Predicted Price', linestyle='--', linewidth=2)
        
        ax.set_title(title)
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.legend(loc='best')
        ax.grid(True, linestyle='--', alpha=0.6)
        
        plt.tight_layout()
        return fig
    
    def plot_backtest_results(self, backtest_df, title="Backtest Results"):
        """
        Plot backtesting results
        """
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        
        # Plot actual vs predicted prices
        axes[0].plot(backtest_df['date'], backtest_df['actual'], 
                     label='Actual Price', linewidth=2)
        axes[0].plot(backtest_df['date'], backtest_df['predicted'], 
                     label='Predicted Price', linestyle='--', linewidth=2)
        axes[0].set_title(f'{title} - Actual vs Predicted')
        axes[0].set_ylabel('Price')
        axes[0].legend()
        axes[0].grid(True, linestyle='--', alpha=0.6)
        
        # Plot prediction errors
        axes[1].bar(backtest_df['date'], backtest_df['error'], 
                    alpha=0.7, width=1.0, label='Prediction Error')
        axes[1].set_title('Prediction Errors Over Time')
        axes[1].set_xlabel('Date')
        axes[1].set_ylabel('Absolute Error')
        axes[1].legend()
        axes[1].grid(True, linestyle='--', alpha=0.6)
        
        plt.tight_layout()
        return fig
    
    def plot_correlation_matrix(self, df, title="Feature Correlation Matrix"):
        """
        Plot correlation matrix of features
        """
        # Select numeric columns for correlation
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        corr_matrix = df[numeric_cols].corr()
        
        plt.figure(figsize=(12, 10))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                    square=True, fmt='.2f')
        plt.title(title)
        plt.tight_layout()
        return plt.gcf()


def create_dashboard(df, title="Stock Analysis Dashboard"):
    """
    Create an interactive dashboard combining multiple visualizations
    """
    # Create subplots
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        specs=[[{"secondary_y": False}], [{"secondary_y": False}],
               [{"secondary_y": False}], [{"secondary_y": True}]],
        subplot_titles=('Price & Moving Averages', 'Volume', 'RSI', 'MACD')
    )
    
    # Price and moving averages
    fig.add_trace(go.Scatter(x=df.index, y=df['close'], name='Close', line=dict(color='blue')), 
                  row=1, col=1)
    if 'MA5' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['MA5'], name='MA5', line=dict(color='orange')), 
                      row=1, col=1)
    if 'MA20' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name='MA20', line=dict(color='red')), 
                      row=1, col=1)
    
    # Volume
    fig.add_trace(go.Bar(x=df.index, y=df['vol'], name='Volume', marker_color='lightgray', opacity=0.7), 
                  row=2, col=1)
    
    # RSI
    if 'RSI' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')), 
                      row=3, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    
    # MACD
    if 'MACD' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='cyan')), 
                      row=4, col=1, secondary_y=False)
    if 'MACD_signal' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD_signal'], name='MACD Signal', line=dict(color='magenta')), 
                      row=4, col=1, secondary_y=False)
    
    # Update layout
    fig.update_layout(height=800, title_text=f"{title} - Interactive Dashboard", showlegend=True)
    fig.update_xaxes(title_text="Date", row=4, col=1)
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_yaxes(title_text="RSI", row=3, col=1)
    fig.update_yaxes(title_text="MACD", row=4, col=1, secondary_y=False)
    
    return fig


if __name__ == "__main__":
    print("Stock Visualization Module - Contains classes and functions for visualizing stock data and predictions")