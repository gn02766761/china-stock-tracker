"""
股票策略分析器 - 整合所有市场策略的主模块

提供统一的接口来运行和比较不同的交易策略
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

from strategies import (
    BaseStrategy,
    TrendFollowingStrategy,
    MeanReversionStrategy,
    MomentumStrategy,
    BollingerBandsStrategy,
    MACDCrossStrategy,
    RSIStrategy,
    StrategyBacktester
)


class StockStrategyAnalyzer:
    """
    股票策略分析器
    
    整合多种交易策略，提供统一的分析和回测接口
    """
    
    def __init__(self, initial_cash: float = 1000000.0):
        """
        Parameters
        ----------
        initial_cash : float
            初始资金
        """
        self.initial_cash = initial_cash
        self.backtester = StrategyBacktester(initial_cash=initial_cash)
        self.strategies: Dict[str, BaseStrategy] = {}
        self.results: Dict = {}
        self._init_strategies()
    
    def _init_strategies(self):
        """初始化所有策略"""
        # 趋势跟踪策略
        self.strategies['trend_following'] = TrendFollowingStrategy(
            short_period=5,
            long_period=20,
            use_ema=False
        )
        
        # 三均线策略
        self.strategies['triple_ma'] = TrendFollowingStrategy(
            short_period=5,
            long_period=20,
            use_ema=False
        )
        
        # 均值回归策略
        self.strategies['mean_reversion'] = MeanReversionStrategy(
            ma_period=20,
            std_threshold=2.0,
            use_bollinger=True
        )
        
        # 动量策略
        self.strategies['momentum'] = MomentumStrategy(
            lookback_period=20,
            signal_threshold=5.0,
            use_volume=True
        )
        
        # 布林带策略
        self.strategies['bollinger_bands'] = BollingerBandsStrategy(
            period=20,
            std_dev=2.0,
            use_breakout=False
        )
        
        # MACD 交叉策略
        self.strategies['macd_cross'] = MACDCrossStrategy(
            fast_period=12,
            slow_period=26,
            signal_period=9,
            use_histogram=True
        )
        
        # RSI 策略
        self.strategies['rsi'] = RSIStrategy(
            period=14,
            oversold=30,
            overbought=70,
            use_divergence=True
        )
    
    def analyze_single_strategy(self, strategy_name: str, data: pd.DataFrame,
                                verbose: bool = True) -> Dict:
        """
        分析单个策略
        
        Parameters
        ----------
        strategy_name : str
            策略名称
        data : pd.DataFrame
            股票数据
        verbose : bool
            是否打印详细信息
        
        Returns
        -------
        Dict
            分析结果
        """
        if strategy_name not in self.strategies:
            print(f"策略 '{strategy_name}' 不存在")
            print(f"可用策略：{list(self.strategies.keys())}")
            return None
        
        strategy = self.strategies[strategy_name]
        print(f"\n{'='*60}")
        print(f"分析策略：{strategy.name}")
        print(f"{'='*60}")
        
        portfolio = self.backtester.run_backtest(strategy, data, verbose=verbose)
        
        self.results[strategy_name] = self.backtester.results[strategy_name]
        
        return self.results[strategy_name]
    
    def compare_all_strategies(self, data: pd.DataFrame,
                               selected_strategies: List[str] = None) -> pd.DataFrame:
        """
        比较所有（或指定）策略的性能
        
        Parameters
        ----------
        data : pd.DataFrame
            股票数据
        selected_strategies : List[str]
            要比较的策略列表，None 表示比较所有策略
        
        Returns
        -------
        pd.DataFrame
            比较结果
        """
        if selected_strategies:
            strategies_to_compare = [self.strategies[name] for name in selected_strategies 
                                     if name in self.strategies]
        else:
            strategies_to_compare = list(self.strategies.values())
        
        if len(strategies_to_compare) == 0:
            print("没有可用的策略进行比较")
            return pd.DataFrame()
        
        comparison_df = self.backtester.compare_strategies(strategies_to_compare, data)
        
        return comparison_df
    
    def get_best_strategy(self, data: pd.DataFrame, metric: str = 'sharpe_ratio') -> str:
        """
        获取表现最佳的策略
        
        Parameters
        ----------
        data : pd.DataFrame
            股票数据
        metric : str
            评估指标 ('sharpe_ratio', 'total_return_pct', 'win_rate', 'max_drawdown')
        
        Returns
        -------
        str
            最佳策略名称
        """
        if not self.results:
            self.compare_all_strategies(data)
        
        best_value = float('-inf') if metric in ['sharpe_ratio', 'total_return_pct', 'win_rate'] else float('inf')
        best_strategy = None
        
        for name, stats in self.results.items():
            if metric in stats:
                value = stats[metric]
                if (metric in ['sharpe_ratio', 'total_return_pct', 'win_rate'] and value > best_value) or \
                   (metric == 'max_drawdown' and value < best_value):
                    best_value = value
                    best_strategy = name
        
        return best_strategy
    
    def generate_strategy_report(self, data: pd.DataFrame, save_dir: str = 'data') -> str:
        """
        生成完整的策略分析报告
        
        Parameters
        ----------
        data : pd.DataFrame
            股票数据
        save_dir : str
            报告保存目录
        
        Returns
        -------
        str
            报告内容
        """
        # 比较所有策略
        comparison_df = self.compare_all_strategies(data)
        
        # 获取最佳策略
        best_sharpe = self.get_best_strategy(data, 'sharpe_ratio')
        best_return = self.get_best_strategy(data, 'total_return_pct')
        best_winrate = self.get_best_strategy(data, 'win_rate')
        lowest_drawdown = self.get_best_strategy(data, 'max_drawdown')
        
        # 生成报告
        report = f"""
# 股票策略分析报告

## 分析概览
- 分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 数据期间：{data.index[0].strftime('%Y-%m-%d')} 至 {data.index[-1].strftime('%Y-%m-%d')}
- 数据天数：{len(data)}
- 初始资金：{self.initial_cash:,.2f}

## 策略比较结果

{comparison_df.to_string()}

## 最佳策略

| 指标 | 最佳策略 |
|------|----------|
| 夏普比率最高 | {best_sharpe} |
| 总收益最高 | {best_return} |
| 胜率最高 | {best_winrate} |
| 回撤最小 | {lowest_drawdown} |

## 策略说明

### 1. 趋势跟踪策略 (Trend Following)
基于移动平均线的趋势跟踪策略，在牛市中表现优异。
- 金叉（短期均线上穿长期均线）：买入
- 死叉（短期均线下穿长期均线）：卖出

### 2. 均值回归策略 (Mean Reversion)
基于价格会回归均值的假设，在震荡市中表现较好。
- 价格远低于均线：买入
- 价格远高于均线：卖出

### 3. 动量策略 (Momentum)
追涨杀跌策略，适合趋势明显的市场。
- 近期涨幅大且成交量放大：买入
- 近期跌幅大且成交量放大：卖出

### 4. 布林带策略 (Bollinger Bands)
基于布林带的均值回归策略。
- 价格触及下轨：买入
- 价格触及上轨：卖出

### 5. MACD 交叉策略
基于 MACD 指标的动量策略。
- MACD 金叉：买入
- MACD 死叉：卖出

### 6. RSI 策略
基于相对强弱指标的超买超卖策略。
- RSI < 30（超卖）：买入
- RSI > 70（超买）：卖出

## 投资建议

1. **不同市场环境使用不同策略**：
   - 牛市：趋势跟踪、动量策略
   - 震荡市：均值回归、布林带策略
   - 熊市：空仓观望或使用反向策略

2. **组合使用多个策略**可以分散风险，提高稳定性

3. **注意风险控制**：
   - 设置止损位
   - 控制仓位
   - 定期再平衡

## 风险提示

- 历史回测结果不代表未来表现
- 策略可能存在过拟合风险
- 实际交易中存在滑点和交易成本
- 市场条件变化可能导致策略失效

---
*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # 保存报告
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        report_path = os.path.join(save_dir, f'strategy_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n报告已保存到：{report_path}")
        
        return report
    
    def run_strategy_visualization(self, strategy_name: str, data: pd.DataFrame,
                                   save_path: str = None):
        """
        运行策略可视化
        
        Parameters
        ----------
        strategy_name : str
            策略名称
        data : pd.DataFrame
            股票数据
        save_path : str
            图表保存路径
        """
        if strategy_name not in self.strategies:
            print(f"策略 '{strategy_name}' 不存在")
            return
        
        try:
            import matplotlib.pyplot as plt
            
            strategy = self.strategies[strategy_name]
            result_data = strategy.analyze(data.copy())
            
            fig, axes = plt.subplots(3, 1, figsize=(14, 10))
            
            # 1. 价格和信号
            ax1 = axes[0]
            ax1.plot(result_data.index, result_data['close'], label='Close Price', linewidth=1.5)
            
            # 标记买入信号
            buy_signals = result_data[result_data['signal'] == 1]
            sell_signals = result_data[result_data['signal'] == -1]
            strong_buy = result_data[result_data['signal'] == 2]
            strong_sell = result_data[result_data['signal'] == -2]
            
            ax1.scatter(buy_signals.index, buy_signals['close'], marker='^', color='red', 
                       s=100, label='Buy', zorder=5)
            ax1.scatter(sell_signals.index, sell_signals['close'], marker='v', color='green', 
                       s=100, label='Sell', zorder=5)
            ax1.scatter(strong_buy.index, strong_buy['close'], marker='^', color='darkred', 
                       s=150, label='Strong Buy', zorder=5)
            ax1.scatter(strong_sell.index, strong_sell['close'], marker='v', color='darkgreen', 
                       s=150, label='Strong Sell', zorder=5)
            
            ax1.set_title(f'{strategy.name} - 价格与交易信号', fontsize=14)
            ax1.set_ylabel('价格')
            ax1.legend(loc='upper left')
            ax1.grid(True, alpha=0.3)
            
            # 2. 组合价值曲线
            portfolio = self.backtester.run_backtest(strategy, data, verbose=False)
            ax2 = axes[1]
            ax2.plot(range(len(portfolio.value_history)), portfolio.value_history, 
                    linewidth=1.5, color='blue')
            ax2.axhline(y=self.initial_cash, color='gray', linestyle='--', 
                       label='Initial Cash', alpha=0.5)
            ax2.set_title(f'组合价值曲线 (最终：{portfolio.get_total_value(data["close"].iloc[-1]):,.2f})', 
                         fontsize=14)
            ax2.set_ylabel('组合价值')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # 3. 信号分布
            ax3 = axes[2]
            signal_counts = result_data['signal_name'].value_counts()
            colors = plt.cm.Set3(np.linspace(0, 1, len(signal_counts)))
            ax3.bar(range(len(signal_counts)), signal_counts.values, color=colors)
            ax3.set_xticks(range(len(signal_counts)))
            ax3.set_xticklabels(signal_counts.index, rotation=45)
            ax3.set_title('信号分布统计', fontsize=14)
            ax3.set_ylabel('次数')
            ax3.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                print(f"图表已保存到：{save_path}")
            
            plt.show()
            
        except Exception as e:
            print(f"可视化失败：{e}")


def main():
    """
    主函数 - 演示策略分析器的使用
    """
    print("=" * 60)
    print("股票策略分析系统")
    print("=" * 60)
    
    # 示例：使用模拟数据演示
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='B')
    np.random.seed(42)
    
    # 生成模拟股价数据
    initial_price = 100
    returns = np.random.randn(len(dates)) * 0.02 + 0.0005
    prices = initial_price * np.cumprod(1 + returns)
    
    data = pd.DataFrame({
        'open': prices * (1 + np.random.randn(len(prices)) * 0.01),
        'high': prices * (1 + np.abs(np.random.randn(len(prices)) * 0.01)),
        'low': prices * (1 - np.abs(np.random.randn(len(prices)) * 0.01)),
        'close': prices,
        'vol': np.random.randint(1000000, 10000000, len(prices))
    }, index=dates)
    
    # 创建分析器
    analyzer = StockStrategyAnalyzer(initial_cash=1000000)
    
    # 比较所有策略
    print("\n比较所有策略...")
    comparison = analyzer.compare_all_strategies(data)
    
    # 生成报告
    print("\n生成策略分析报告...")
    report = analyzer.generate_strategy_report(data)
    
    print("\n分析完成！")


if __name__ == "__main__":
    main()
