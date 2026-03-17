"""
股票分析系统 - 简化版主程序

基于 Tushare 数据源的股票分析和推荐系统
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from datetime import datetime
from utils.data_collector import StockDataCollector, get_default_start_end_dates
from strategy_analyzer import StockStrategyAnalyzer
from stock_recommender import StockRecommender
import warnings
warnings.filterwarnings('ignore')


def main():
    """主函数"""
    print("=" * 70)
    print("中国股票分析推荐系统")
    print("=" * 70)
    
    # 初始化模块
    print("\n初始化系统...")
    
    # 检查 Tushare token
    token = None
    try:
        import tushare as ts
        import os
        token = os.getenv('TUSHARE_TOKEN')
        
        if not token:
            print("=" * 70)
            print("Tushare 配置")
            print("=" * 70)
            print("\n访问 https://tushare.pro/ 注册获取免费 token")
            try:
                token = input("请输入 Tushare token (或按回车跳过): ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n⚠ 未配置 token，部分功能受限")
            
            if token:
                ts.set_token(token)
                print("✓ Tushare token 已配置")
            else:
                print("⚠ 未配置 token，部分功能受限")
        else:
            ts.set_token(token)
            print("✓ 从环境变量加载 Tushare token")
            
    except ImportError:
        print("⚠ 未安装 tushare")
        print("安装：pip install tushare")
    
    collector = StockDataCollector(token=token)
    strategy_analyzer = StockStrategyAnalyzer(initial_cash=1000000)
    recommender = StockRecommender()
    
    # 获取用户输入
    print("\n请输入股票代码:")
    print("示例：000001 (平安银行), 600519 (贵州茅台)")
    try:
        stock_symbol = input("股票代码：").strip()
    except (EOFError, KeyboardInterrupt):
        stock_symbol = '000001'
    
    if not stock_symbol:
        print("使用默认股票：000001 (平安银行)")
        stock_symbol = '000001'
    
    # 获取日期范围
    start_date, end_date = get_default_start_end_dates()
    print(f"\n日期范围：{start_date} 至 {end_date}")
    
    # 收集数据
    print(f"\n获取 {stock_symbol} 数据...")
    
    if token:
        stock_data = collector.get_stock_data(stock_symbol, start_date, end_date)
    else:
        print("⚠ 未配置 Tushare token，无法获取真实数据")
        print("请先配置 token 后重试")
        return
    
    if stock_data is None or stock_data.empty:
        print(f"无法获取 {stock_symbol} 的数据")
        print("请检查股票代码是否正确")
        return
    
    print(f"✓ 成功获取 {len(stock_data)} 条记录")
    
    # 计算技术指标
    print("\n计算技术指标...")
    stock_data = collector.calculate_technical_indicators(stock_data)
    
    # 显示最新数据
    print(f"\n{stock_symbol} 最新数据:")
    print(stock_data[['open', 'high', 'low', 'close', 'vol']].tail())
    
    # 主菜单
    print("\n" + "=" * 70)
    print("选择分析模式:")
    print("=" * 70)
    print("1. 市场策略分析 (单只股票)")
    print("2. 比较所有策略")
    print("3. 股票推荐分析")
    print("4. 退出")
    
    try:
        mode_choice = input("\n请选择 (1-4, 默认 1): ").strip() or '1'
    except (EOFError, KeyboardInterrupt):
        mode_choice = '1'
    
    if mode_choice == '1':
        # 单个策略分析
        run_strategy_analysis(stock_symbol, stock_data, strategy_analyzer)
    elif mode_choice == '2':
        # 比较所有策略
        run_strategy_comparison(stock_symbol, stock_data, strategy_analyzer)
    elif mode_choice == '3':
        # 股票推荐
        run_stock_recommendation(stock_data, stock_symbol, recommender)
    elif mode_choice == '4':
        print("\n感谢使用，再见!")
        return
    else:
        print("无效选择")
        return
    
    print("\n" + "=" * 70)
    print("分析完成!")
    print("=" * 70)


def run_strategy_analysis(stock_symbol, stock_data, strategy_analyzer):
    """运行单个策略分析"""
    print("\n" + "=" * 70)
    print("可用交易策略")
    print("=" * 70)
    print("1. 趋势跟踪 (双均线)")
    print("2. 均值回归")
    print("3. 动量策略")
    print("4. 布林带")
    print("5. MACD 交叉")
    print("6. RSI")
    
    try:
        strategy_choice = input("\n请选择 (1-6, 默认 1): ").strip() or '1'
    except (EOFError, KeyboardInterrupt):
        strategy_choice = '1'
    
    strategy_map = {
        '1': 'trend_following',
        '2': 'mean_reversion',
        '3': 'momentum',
        '4': 'bollinger_bands',
        '5': 'macd_cross',
        '6': 'rsi'
    }
    
    strategy_name = strategy_map.get(strategy_choice, 'trend_following')
    
    print(f"\n分析策略：{strategy_name}...")
    result = strategy_analyzer.analyze_single_strategy(strategy_name, stock_data, verbose=True)
    
    if result:
        print(f"\n策略：{result['strategy_name']}")
        print(f"总收益：{result['total_return_pct']:.2f}%")
        print(f"胜率：{result['win_rate']:.2f}%")
        print(f"夏普比率：{result['sharpe_ratio']:.2f}")
        print(f"最大回撤：{result['max_drawdown']:.2f}%")


def run_strategy_comparison(stock_symbol, stock_data, strategy_analyzer):
    """运行策略比较"""
    print("\n" + "=" * 70)
    print("比较所有交易策略")
    print("=" * 70)
    
    comparison_df = strategy_analyzer.compare_all_strategies(stock_data)
    
    if not comparison_df.empty:
        print("\n策略比较结果:")
        print(comparison_df.to_string())


def run_stock_recommendation(stock_data, stock_symbol, recommender):
    """运行股票推荐功能"""
    print("\n" + "=" * 70)
    print("股票推荐分析")
    print("=" * 70)
    
    signal = recommender.analyze_stock(stock_data, stock_symbol)
    
    print(f"\n{'='*60}")
    print(f"{stock_symbol} - 分析结果")
    print(f"{'='*60}")
    print(f"当前价格：{signal.price:.2f}")
    print(f"综合评分：{signal.score:.2f}")
    print(f"推荐等级：{signal.recommendation}")
    print(f"风险等级：{signal.risk_level}")
    
    if signal.target_price:
        print(f"目标价格：{signal.target_price:.2f}")
    if signal.stop_loss:
        print(f"止损价格：{signal.stop_loss:.2f}")
    
    if signal.reasons:
        print(f"\n推荐原因:")
        for reason in signal.reasons[:5]:
            print(f"  - {reason}")
    
    print(f"\n策略信号:")
    for strategy, sig_value in signal.signals.items():
        sig_name = {1: '买入', 2: '强烈买入', -1: '卖出', -2: '强烈卖出', 0: '持有'}.get(sig_value, '未知')
        print(f"  {strategy}: {sig_name}")
    
    print(f"\n建议操作:")
    if signal.recommendation == 'STRONG_BUY':
        print("  🟢 强烈建议买入")
    elif signal.recommendation == 'BUY':
        print("  🟢 建议买入")
    elif signal.recommendation == 'HOLD':
        print("  🟡 持有/观望")
    elif signal.recommendation == 'SELL':
        print("  🔴 建议卖出")
    else:
        print("  🔴 强烈卖出")


if __name__ == "__main__":
    main()
