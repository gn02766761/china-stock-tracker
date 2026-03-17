"""
策略回测引擎 (Strategy Backtester)

用于回测和比较多个交易策略的性能
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from .base_strategy import BaseStrategy, Signal, Portfolio, Trade


class StrategyBacktester:
    """
    策略回测引擎
    
    功能：
    - 单个策略回测
    - 多个策略比较
    - 性能指标计算
    - 交易记录分析
    """
    
    def __init__(self, initial_cash: float = 1000000.0, 
                 commission_rate: float = 0.0003,
                 slippage: float = 0.001):
        """
        Parameters
        ----------
        initial_cash : float
            初始资金
        commission_rate : float
            佣金费率（默认万分之三）
        slippage : float
            滑点（默认 0.1%）
        """
        self.initial_cash = initial_cash
        self.commission_rate = commission_rate
        self.slippage = slippage
        self.results: Dict[str, Dict] = {}
    
    def run_backtest(self, strategy: BaseStrategy, data: pd.DataFrame,
                     verbose: bool = True) -> Portfolio:
        """
        运行单个策略回测
        
        Parameters
        ----------
        strategy : BaseStrategy
            交易策略
        data : pd.DataFrame
            历史数据
        verbose : bool
            是否打印详细信息
        
        Returns
        -------
        Portfolio
            回测结果
        """
        portfolio = Portfolio(self.initial_cash)
        result_data = strategy.analyze(data.copy())
        
        trade_log = []
        
        for idx in range(len(result_data)):
            row = result_data.iloc[idx]
            signal = strategy.signals[idx]
            price = row['close']
            date = result_data.index[idx]
            
            # 应用滑点
            if signal in [Signal.BUY, Signal.STRONG_BUY]:
                exec_price = price * (1 + self.slippage)
            elif signal in [Signal.SELL, Signal.STRONG_SELL]:
                exec_price = price * (1 - self.slippage)
            else:
                exec_price = price
            
            # 执行交易
            if signal in [Signal.BUY, Signal.STRONG_BUY] and portfolio.current_trade is None:
                # 计算可买股数（考虑佣金）
                available_cash = portfolio.cash * 0.95  # 使用 95% 资金
                shares = int(available_cash / (exec_price * (1 + self.commission_rate)))
                
                if shares > 0:
                    cost = shares * exec_price * (1 + self.commission_rate)
                    portfolio.cash -= cost
                    portfolio.current_trade = Trade(date, exec_price, shares)
                    trade_log.append({
                        'date': date,
                        'type': 'BUY',
                        'price': exec_price,
                        'shares': shares,
                        'cost': cost
                    })
            
            elif signal in [Signal.SELL, Signal.STRONG_SELL] and portfolio.current_trade is not None:
                # 平仓
                portfolio.close_position(date, exec_price)
                
                # 扣除佣金
                sell_value = portfolio.trades[-1].exit_price * portfolio.trades[-1].shares
                commission = sell_value * self.commission_rate
                portfolio.cash -= commission
                
                trade_log.append({
                    'date': date,
                    'type': 'SELL',
                    'price': exec_price,
                    'shares': portfolio.trades[-1].shares,
                    'pnl': portfolio.trades[-1].pnl - commission
                })
            
            # 记录组合价值
            portfolio.value_history.append(portfolio.get_total_value(exec_price))
        
        # 如果还有未平仓的头寸，按最后价格平仓
        if portfolio.current_trade is not None:
            final_price = data['close'].iloc[-1]
            portfolio.close_position(data.index[-1], final_price)
            portfolio.value_history.append(portfolio.get_total_value(final_price))
        
        # 计算性能指标
        stats = portfolio.get_statistics()
        
        # 添加额外指标
        stats['strategy_name'] = strategy.name
        stats['total_value'] = portfolio.get_total_value(data['close'].iloc[-1])
        stats['value_history'] = portfolio.value_history
        
        # 计算夏普比率和最大回撤
        if len(portfolio.value_history) > 1:
            returns = pd.Series(portfolio.value_history).pct_change().dropna()
            
            # 年化夏普比率
            if returns.std() > 0:
                stats['sharpe_ratio'] = (returns.mean() / returns.std()) * np.sqrt(252)
            else:
                stats['sharpe_ratio'] = 0
            
            # 最大回撤
            cummax = pd.Series(portfolio.value_history).cummax()
            drawdown = (pd.Series(portfolio.value_history) - cummax) / cummax
            stats['max_drawdown'] = abs(drawdown.min()) * 100
        
        self.results[strategy.name] = stats
        
        if verbose:
            self._print_results(stats, trade_log)
        
        return portfolio
    
    def compare_strategies(self, strategies: List[BaseStrategy], 
                          data: pd.DataFrame) -> pd.DataFrame:
        """
        比较多个策略的性能
        
        Parameters
        ----------
        strategies : List[BaseStrategy]
            策略列表
        data : pd.DataFrame
            历史数据
        
        Returns
        -------
        pd.DataFrame
            策略比较结果
        """
        comparison = []
        
        for strategy in strategies:
            print(f"\n回测策略：{strategy.name}")
            print("-" * 40)
            
            portfolio = self.run_backtest(strategy, data, verbose=False)
            stats = self.results[strategy.name]
            
            comparison.append({
                '策略': strategy.name,
                '总收益 (%)': round(stats['total_return_pct'], 2),
                '总交易数': stats['total_trades'],
                '胜率 (%)': round(stats['win_rate'], 2),
                '平均收益 (%)': round(stats['avg_return_pct'], 2),
                '最大回撤 (%)': round(stats['max_drawdown'], 2),
                '夏普比率': round(stats['sharpe_ratio'], 2),
                '最终价值': round(stats['total_value'], 2)
            })
        
        comparison_df = pd.DataFrame(comparison)
        comparison_df.set_index('策略', inplace=True)
        
        print("\n" + "=" * 80)
        print("策略比较结果")
        print("=" * 80)
        print(comparison_df.to_string())
        
        return comparison_df
    
    def _print_results(self, stats: Dict, trade_log: List[Dict]):
        """打印回测结果"""
        print(f"\n策略：{stats['strategy_name']}")
        print("-" * 50)
        print(f"初始资金：{self.initial_cash:,.2f}")
        print(f"最终价值：{stats['total_value']:,.2f}")
        print(f"总收益率：{stats['total_return_pct']:.2f}%")
        print(f"总交易次数：{stats['total_trades']}")
        print(f"盈利交易：{stats['winning_trades']}")
        print(f"亏损交易：{stats['losing_trades']}")
        print(f"胜率：{stats['win_rate']:.2f}%")
        print(f"平均收益：{stats['avg_return_pct']:.2f}%")
        print(f"最大回撤：{stats['max_drawdown']:.2f}%")
        print(f"夏普比率：{stats['sharpe_ratio']:.2f}")
        
        if trade_log:
            print(f"\n交易记录 (前 5 笔):")
            for trade in trade_log[:5]:
                if trade['type'] == 'BUY':
                    print(f"  {trade['date'].strftime('%Y-%m-%d')} 买入 {trade['shares']} 股 @ {trade['price']:.2f}")
                else:
                    print(f"  {trade['date'].strftime('%Y-%m-%d')} 卖出 {trade['shares']} 股 @ {trade['price']:.2f}, 盈亏：{trade.get('pnl', 0):.2f}")
            
            if len(trade_log) > 5:
                print(f"  ... 还有 {len(trade_log) - 5} 笔交易")
    
    def plot_strategy_comparison(self, strategies: List[BaseStrategy],
                                 data: pd.DataFrame, save_path: str = None):
        """
        绘制策略比较图
        
        Parameters
        ----------
        strategies : List[BaseStrategy]
            策略列表
        data : pd.DataFrame
            历史数据
        save_path : str
            保存路径
        """
        try:
            import matplotlib.pyplot as plt
            
            fig, axes = plt.subplots(2, 1, figsize=(14, 10))
            
            # 绘制价值曲线
            for strategy in strategies:
                portfolio = Portfolio(self.initial_cash)
                result_data = strategy.analyze(data.copy())
                
                value_history = []
                for idx in range(len(result_data)):
                    signal = strategy.signals[idx]
                    price = result_data.iloc[idx]['close']
                    
                    if signal in [Signal.BUY, Signal.STRONG_BUY] and portfolio.current_trade is None:
                        shares = int(portfolio.cash * 0.95 / price)
                        if shares > 0:
                            portfolio.open_position(result_data.index[idx], price, shares)
                    elif signal in [Signal.SELL, Signal.STRONG_SELL] and portfolio.current_trade is not None:
                        portfolio.close_position(result_data.index[idx], price)
                    
                    value_history.append(portfolio.get_total_value(price))
                
                axes[0].plot(range(len(value_history)), value_history, 
                           label=strategy.name, linewidth=2)
            
            axes[0].set_title('策略价值曲线比较', fontsize=14)
            axes[0].set_xlabel('交易日')
            axes[0].set_ylabel('组合价值')
            axes[0].legend()
            axes[0].grid(True, alpha=0.3)
            
            # 绘制收益分布
            returns_data = []
            labels = []
            for strategy in strategies:
                if strategy.name in self.results:
                    stats = self.results[strategy.name]
                    returns_data.append(stats['total_return_pct'])
                    labels.append(strategy.name)
            
            if returns_data:
                colors = plt.cm.Set3(np.linspace(0, 1, len(returns_data)))
                bars = axes[1].bar(range(len(returns_data)), returns_data, color=colors)
                axes[1].set_xticks(range(len(returns_data)))
                axes[1].set_xticklabels(labels, rotation=45)
                axes[1].set_title('总收益率比较', fontsize=14)
                axes[1].set_ylabel('收益率 (%)')
                axes[1].grid(True, alpha=0.3, axis='y')
                
                # 在柱子上标注数值
                for bar, val in zip(bars, returns_data):
                    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                                f'{val:.1f}%', ha='center', va='bottom', fontsize=9)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                print(f"图表已保存到：{save_path}")
            
            plt.show()
            
        except Exception as e:
            print(f"绘制图表失败：{e}")
    
    def generate_report(self, strategy: BaseStrategy, data: pd.DataFrame,
                       save_path: str = None) -> str:
        """
        生成策略分析报告
        
        Parameters
        ----------
        strategy : BaseStrategy
            策略
        data : pd.DataFrame
            历史数据
        save_path : str
            报告保存路径
        
        Returns
        -------
        str
            报告内容
        """
        portfolio = self.run_backtest(strategy, data, verbose=False)
        stats = self.results[strategy.name]
        
        report = f"""
# {strategy.name} 策略回测报告

## 基本信息
- 回测期间：{data.index[0].strftime('%Y-%m-%d')} 至 {data.index[-1].strftime('%Y-%m-%d')}
- 初始资金：{self.initial_cash:,.2f}
- 数据天数：{len(data)}

## 策略参数
{strategy.get_params_info()}

## 性能指标

### 收益指标
- **总收益率**: {stats['total_return_pct']:.2f}%
- **平均交易收益**: {stats['avg_return_pct']:.2f}%
- **最终组合价值**: {stats['total_value']:,.2f}

### 风险指标
- **最大回撤**: {stats['max_drawdown']:.2f}%
- **夏普比率**: {stats['sharpe_ratio']:.2f}

### 交易统计
- **总交易次数**: {stats['total_trades']}
- **盈利交易**: {stats['winning_trades']}
- **亏损交易**: {stats['losing_trades']}
- **胜率**: {stats['win_rate']:.2f}%

## 评价
"""
        # 添加评价
        if stats['sharpe_ratio'] > 1.5:
            report += "- 风险调整后收益优秀\n"
        elif stats['sharpe_ratio'] > 1.0:
            report += "- 风险调整后收益良好\n"
        else:
            report += "- 风险调整后收益一般\n"
        
        if stats['win_rate'] > 60:
            report += "- 胜率较高\n"
        
        if stats['max_drawdown'] < 15:
            report += "- 回撤控制良好\n"
        elif stats['max_drawdown'] > 30:
            report += "- 回撤较大，需注意风险控制\n"
        
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"报告已保存到：{save_path}")
        
        return report
