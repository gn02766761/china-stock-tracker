"""
股票推荐系统 - 增强版

支持实时价格更新和多股票分析
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime
from stock_recommender import StockRecommender
from update_prices import RealTimePriceUpdater
from utils.data_collector import StockDataCollector, get_default_start_end_dates
import warnings
warnings.filterwarnings('ignore')


# 默认股票池
DEFAULT_STOCK_POOL = {
    '000001': '平安银行',
    '000002': '万科 A',
    '600519': '贵州茅台',
    '000858': '五粮液',
    '600036': '招商银行',
}


def update_and_analyze(stock_pool: dict = None):
    """更新价格并分析"""
    if stock_pool is None:
        stock_pool = DEFAULT_STOCK_POOL
    
    print("\n" + "=" * 70)
    print("更新价格数据并分析")
    print("=" * 70)
    
    # 更新价格
    updater = RealTimePriceUpdater()
    print(f"\n更新 {len(stock_pool)} 只股票价格...")
    results = updater.update_stock_pool(stock_pool)
    updater.close()
    
    # 显示更新结果
    print("\n更新结果:")
    print("-" * 70)
    success_count = sum(1 for r in results if r['success'])
    print(f"成功：{success_count}/{len(stock_pool)}")
    
    for r in results:
        status = "✓" if r['success'] else "✗"
        price_str = f"{r['latest_price']:.2f}" if r['latest_price'] else "N/A"
        print(f"  {status} {r['symbol']}: {r['message']} (价格：{price_str})")
    
    return success_count > 0


def analyze_stocks(stock_pool: dict = None):
    """分析股票（不更新价格）"""
    if stock_pool is None:
        stock_pool = DEFAULT_STOCK_POOL
    
    print("\n" + "=" * 70)
    print("分析股票")
    print("=" * 70)
    
    recommender = StockRecommender()
    collector = StockDataCollector()
    start_date, end_date = get_default_start_end_dates()
    
    stock_data = {}
    for symbol, name in stock_pool.items():
        print(f"获取 {symbol} {name} 数据...")
        data = collector.get_stock_data(symbol, start_date, end_date)
        if data is not None and not data.empty:
            data = collector.calculate_technical_indicators(data)
            stock_data[symbol] = data
    
    if stock_data:
        print(f"\n分析 {len(stock_data)} 只股票...")
        recommender.analyze_multiple_stocks(stock_data)
        recommender.print_recommendations(top_n=len(stock_data))
        
        # 显示买入推荐
        buy_recs = recommender.get_buy_recommendations(top_n=5)
        if buy_recs:
            print("\n" + "=" * 60)
            print("买入推荐")
            print("=" * 60)
            for signal in buy_recs:
                print(f"  {signal.symbol} {signal.name}: {signal.recommendation} (评分：{signal.score:.2f}, 价格：{signal.price:.2f})")
        
        # 保存报告
        save = input("\n是否保存报告？(y/n, 默认 y): ").strip().lower()
        if save != 'n':
            report_path = f'data/stock_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
            recommender.generate_report(save_path=report_path)
    else:
        print("\n无法获取数据，请先更新价格")


def analyze_single_stock(symbol: str = '000001'):
    """分析单只股票"""
    print("\n" + "=" * 70)
    print(f"分析 {symbol}")
    print("=" * 70)
    
    # 先更新价格
    updater = RealTimePriceUpdater()
    from run_stock_recommender import DEFAULT_STOCK_POOL as POOL
    name = POOL.get(symbol, '')
    
    print(f"\n更新 {symbol} 价格...")
    result = updater.update_single_stock(symbol, name)
    
    if result['success']:
        print(f"最新价格：{result['latest_price']:.2f}")
    else:
        print(f"更新失败：{result['message']}")
    
    updater.close()
    
    # 分析
    recommender = StockRecommender()
    collector = StockDataCollector()
    start_date, end_date = get_default_start_end_dates()
    
    print(f"\n获取 {symbol} 数据...")
    data = collector.get_stock_data(symbol, start_date, end_date)
    
    if data is not None and not data.empty:
        data = collector.calculate_technical_indicators(data)
        signal = recommender.analyze_stock(data, symbol, name)
        
        print(f"\n{'='*60}")
        print(f"{symbol} {name} - 分析结果")
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
        
        # 建议操作
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
    else:
        print(f"\n无法获取 {symbol} 数据")


def main():
    """主函数"""
    print("=" * 70)
    print("股票推荐系统 - 增强版")
    print("=" * 70)
    
    print("\n选择功能:")
    print("1. 更新价格并分析全部 (推荐)")
    print("2. 分析股票池 (不更新)")
    print("3. 分析单只股票")
    print("4. 自定义股票分析")
    print("5. 仅更新价格")
    
    choice = input("\n请选择 (1-5, 默认 1): ").strip() or '1'
    
    if choice == '1':
        # 更新并分析
        if update_and_analyze():
            analyze_stocks()
    
    elif choice == '2':
        # 分析不更新
        analyze_stocks()
    
    elif choice == '3':
        # 单只股票
        try:
            symbol = input("股票代码 (默认 000001): ").strip() or '000001'
        except EOFError:
            symbol = '000001'
        analyze_single_stock(symbol)
    
    elif choice == '4':
        # 自定义
        print("\n输入股票代码，用空格分隔:")
        input_str = input("股票代码：").strip()
        if not input_str:
            input_str = '000001 000002 600519'
        
        symbols = [s.strip() for s in input_str.replace(',', ' ').split()]
        custom_pool = {s: DEFAULT_STOCK_POOL.get(s, '') for s in symbols}
        
        if update_and_analyze(custom_pool):
            analyze_stocks(custom_pool)
    
    elif choice == '5':
        # 仅更新
        update_and_analyze()
    
    else:
        print("无效选择")
    
    print("\n" + "=" * 70)
    print("完成!")
    print("=" * 70)


if __name__ == "__main__":
    main()
