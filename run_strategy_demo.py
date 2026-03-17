"""
市场策略快速演示脚本

演示如何使用策略分析系统进行股票策略回测
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime
from strategy_analyzer import StockStrategyAnalyzer


def run_demo():
    """运行策略演示"""
    print("=" * 60)
    print("中国市场策略分析系统 - 演示")
    print("=" * 60)
    
    # 生成模拟数据（如果无法获取真实数据）
    print("\n生成模拟股票数据...")
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='B')
    np.random.seed(42)
    
    # 模拟股价走势（包含趋势和震荡）
    initial_price = 50
    # 使用几何布朗运动模拟更合理的股价
    mu = 0.0005  # 日均收益率
    sigma = 0.02  # 日波动率
    
    returns = np.random.normal(mu, sigma, len(dates))
    prices = initial_price * np.cumprod(1 + returns)
    
    # 确保价格在合理范围
    prices = np.clip(prices, 10, 200)
    
    data = pd.DataFrame({
        'open': prices * (1 + np.random.randn(len(prices)) * 0.005),
        'high': np.maximum(prices * (1 + np.abs(np.random.randn(len(prices)) * 0.01)), prices),
        'low': np.minimum(prices * (1 - np.abs(np.random.randn(len(prices)) * 0.01)), prices),
        'close': prices,
        'vol': np.random.randint(2000000, 15000000, len(prices))
    }, index=dates)
    
    # 确保 high >= close >= low
    data['high'] = np.maximum(data['high'], data['close'])
    data['low'] = np.minimum(data['low'], data['close'])
    
    print(f"数据期间：{data.index[0].strftime('%Y-%m-%d')} 至 {data.index[-1].strftime('%Y-%m-%d')}")
    print(f"数据天数：{len(data)}")
    print(f"价格范围：{data['close'].min():.2f} - {data['close'].max():.2f}")
    
    # 创建策略分析器
    print("\n初始化策略分析器...")
    analyzer = StockStrategyAnalyzer(initial_cash=1000000)
    
    print(f"可用策略：{list(analyzer.strategies.keys())}")
    
    # 比较所有策略
    print("\n" + "=" * 60)
    print("开始策略回测比较...")
    print("=" * 60)
    
    comparison_df = analyzer.compare_all_strategies(data)
    
    if not comparison_df.empty:
        print("\n" + "=" * 80)
        print("策略比较结果")
        print("=" * 80)
        print(comparison_df.to_string())
        
        # 找出最佳策略
        print("\n" + "=" * 60)
        print("最佳策略")
        print("=" * 60)
        
        best_return = comparison_df['总收益 (%)'].idxmax()
        best_sharpe = comparison_df['夏普比率'].idxmax()
        best_winrate = comparison_df['胜率 (%)'].idxmax()
        lowest_drawdown = comparison_df['最大回撤 (%)'].idxmin()
        
        print(f"🏆 总收益最高：{best_return} ({float(comparison_df.loc[best_return, '总收益 (%)']):.2f}%)")
        print(f"🏆 夏普比率最高：{best_sharpe} ({float(comparison_df.loc[best_sharpe, '夏普比率']):.2f})")
        print(f"🏆 胜率最高：{best_winrate} ({float(comparison_df.loc[best_winrate, '胜率 (%)']):.2f}%)")
        print(f"🏆 回撤最小：{lowest_drawdown} ({float(comparison_df.loc[lowest_drawdown, '最大回撤 (%)']):.2f}%)")
    
    # 生成详细报告
    print("\n" + "=" * 60)
    print("生成策略分析报告...")
    print("=" * 60)
    
    report = analyzer.generate_strategy_report(data, save_dir='data')
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)
    print("\n查看结果：")
    print("- 策略报告：data/strategy_report_*.md")
    print("- 运行 python main.py 进行真实股票分析")
    
    return comparison_df


def show_strategy_introduction():
    """显示策略介绍"""
    print("\n" + "=" * 60)
    print("交易策略介绍")
    print("=" * 60)
    
    strategies = {
        'trend_following': {
            'name': '趋势跟踪策略',
            'desc': '基于双均线交叉，金叉买入，死叉卖出',
            'market': '趋势明显的牛市或熊市'
        },
        'mean_reversion': {
            'name': '均值回归策略',
            'desc': '价格低于均线 2 倍标准差买入，高于卖出',
            'market': '震荡市'
        },
        'momentum': {
            'name': '动量策略',
            'desc': '追涨杀跌，近期强势且放量时买入',
            'market': '趋势强劲的市场'
        },
        'bollinger_bands': {
            'name': '布林带策略',
            'desc': '价格触及下轨买入，触及上轨卖出',
            'market': '震荡市'
        },
        'macd_cross': {
            'name': 'MACD 交叉策略',
            'desc': 'MACD 金叉买入，死叉卖出',
            'market': '趋势市场'
        },
        'rsi': {
            'name': 'RSI 策略',
            'desc': 'RSI<30 超卖买入，RSI>70 超买卖出',
            'market': '震荡市'
        }
    }
    
    for key, info in strategies.items():
        print(f"\n{info['name']}")
        print(f"  原理：{info['desc']}")
        print(f"  适用：{info['market']}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='中国市场策略分析系统')
    parser.add_argument('--demo', action='store_true', help='运行演示')
    parser.add_argument('--intro', action='store_true', help='显示策略介绍')
    
    args = parser.parse_args()
    
    if args.intro:
        show_strategy_introduction()
    elif args.demo:
        run_demo()
    else:
        # 默认运行演示
        run_demo()
