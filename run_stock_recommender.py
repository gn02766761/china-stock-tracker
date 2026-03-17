"""
股票推荐系统 - 独立运行版本

基于多策略信号综合评分，推荐值得关注的股票
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime
from stock_recommender import StockRecommender, create_sample_data
from utils.data_collector import StockDataCollector, get_default_start_end_dates
import warnings
warnings.filterwarnings('ignore')


# 默认股票池（精选 50 只热门股票，使用真实价格范围）
DEFAULT_STOCK_POOL = {
    # 银行金融（股价 5-50 元）
    '000001': '平安银行',  # ~12 元
    '000002': '万科 A',    # ~8 元
    '600000': '浦发银行',  # ~8 元
    '600036': '招商银行',  # ~35 元
    '601318': '中国平安',  # ~45 元
    '601398': '工商银行',  # ~5 元
    
    # 消费（股价 10-2000 元）
    '000858': '五粮液',    # ~150 元
    '600519': '贵州茅台',  # ~1500 元
    '600809': '山西汾酒',  # ~200 元
    '600887': '伊利股份',  # ~30 元
    '000333': '美的集团',  # ~60 元
    '000651': '格力电器',  # ~40 元
    '600690': '海尔智家',  # ~25 元
    
    # 科技（股价 10-100 元）
    '000063': '中兴通讯',  # ~30 元
    '000725': '京东方 A',  # ~4 元
    '002230': '科大讯飞',  # ~50 元
    '002415': '海康威视',  # ~30 元
    '300059': '东方财富',  # ~15 元
    '300750': '宁德时代',  # ~200 元
    '603019': '中科曙光',  # ~40 元
    
    # 医药（股价 20-150 元）
    '000538': '云南白药',  # ~55 元
    '002007': '华兰生物',  # ~20 元
    '300122': '智飞生物',  # ~40 元
    '300760': '迈瑞医疗',  # ~300 元
    '600276': '恒瑞医药',  # ~45 元
    '600436': '片仔癀',    # ~250 元
    '603259': '药明康德',  # ~70 元
    
    # 新能源（股价 20-100 元）
    '002594': '比亚迪',    # ~250 元
    '300014': '亿纬锂能',  # ~45 元
    '300274': '阳光电源',  # ~70 元
    '601012': '隆基股份',  # ~20 元
    '603799': '华友钴业',  # ~35 元
    
    # 其他
    '002001': '新和成',
    '002142': '宁波银行',
    '002304': '洋河股份',
    '300124': '汇川技术',
    '600030': '中信证券',
    '600031': '三一重工',
    '600309': '万华化学',
    '600585': '海螺水泥',
    '601888': '中国中免',
}


class StockPoolManager:
    """股票池管理器"""
    
    def __init__(self):
        self.stock_pool = DEFAULT_STOCK_POOL.copy()
        self.collector = StockDataCollector()
    
    def add_stock(self, symbol: str, name: str = ''):
        """添加股票到股票池"""
        self.stock_pool[symbol] = name
    
    def remove_stock(self, symbol: str):
        """从股票池移除股票"""
        if symbol in self.stock_pool:
            del self.stock_pool[symbol]
    
    def get_stock_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取股票数据"""
        data = self.collector.get_stock_data(symbol, start_date, end_date)
        if data is not None and not data.empty:
            # 计算技术指标
            data = self.collector.calculate_technical_indicators(data)
        return data
    
    def fetch_all_data(self, start_date: str = None, end_date: str = None) -> dict:
        """获取所有股票数据"""
        if start_date is None or end_date is None:
            start_date, end_date = get_default_start_end_dates()
        
        data_dict = {}
        print(f"获取股票数据 (共{len(self.stock_pool)}只股票)...")
        
        for i, (symbol, name) in enumerate(self.stock_pool.items(), 1):
            try:
                print(f"[{i}/{len(self.stock_pool)}] {symbol} {name}...", end=' ')
                data = self.get_stock_data(symbol, start_date, end_date)
                if data is not None and not data.empty:
                    data_dict[symbol] = data
                    print(f"成功 ({len(data)}天)")
                else:
                    print("失败")
            except Exception as e:
                print(f"错误：{e}")
        
        return data_dict
    
    def get_selected_stocks(self, symbols: list) -> dict:
        """获取选中的股票"""
        return {s: self.stock_pool.get(s, '') for s in symbols if s in self.stock_pool}


def run_recommendation_demo():
    """运行推荐演示"""
    print("=" * 70)
    print("股票推荐系统")
    print("=" * 70)
    
    # 选择模式
    print("\n选择分析模式:")
    print("1. 使用示例数据演示 (快速)")
    print("2. 分析单只股票")
    print("3. 分析股票池 (多只股票)")
    print("4. 自定义股票列表")
    
    choice = input("\n请输入选择 (1-4, 默认 1): ").strip()
    
    recommender = StockRecommender()
    pool_manager = StockPoolManager()
    
    if choice == '1':
        # 示例数据
        print("\n使用示例数据...")
        stock_data = create_sample_data()
        recommender.analyze_multiple_stocks(stock_data)
        recommender.print_recommendations(top_n=10)
        
    elif choice == '2':
        # 单只股票
        symbol = input("请输入股票代码 (默认 000001): ").strip() or '000001'
        name = pool_manager.stock_pool.get(symbol, '')
        
        print(f"\n获取 {symbol} {name} 的数据...")
        start_date, end_date = get_default_start_end_dates()
        data = pool_manager.get_stock_data(symbol, start_date, end_date)
        
        if data is not None and not data.empty:
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
            
            # 生成报告
            try:
                save = input("\n是否保存报告？(y/n, 默认 y): ").strip().lower()
            except EOFError:
                save = 'y'
            if save != 'n':
                recommender.generate_report(save_path=f'data/stock_rec_{symbol}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md')
        else:
            print(f"无法获取 {symbol} 的数据")
    
    elif choice == '3':
        # 股票池
        print(f"\n股票池共有 {len(pool_manager.stock_pool)} 只股票")
        print("分析前 10 只股票...")
        
        # 选择前 10 只股票
        selected = list(pool_manager.stock_pool.keys())[:10]
        stock_data = pool_manager.fetch_all_data()
        
        # 只分析选中的
        filtered_data = {k: v for k, v in stock_data.items() if k in selected}
        
        if filtered_data:
            recommender.analyze_multiple_stocks(filtered_data)
            recommender.print_recommendations(top_n=10)
            
            # 显示买入推荐
            buy_recs = recommender.get_buy_recommendations(top_n=5)
            if buy_recs:
                print("\n" + "="*60)
                print("买入推荐")
                print("="*60)
                for signal in buy_recs:
                    print(f"  {signal.symbol} {signal.name}: {signal.recommendation} (评分：{signal.score:.2f})")
    
    elif choice == '4':
        # 自定义股票列表
        print("\n请输入股票代码，用空格或逗号分隔")
        print("例如：000001 000002 600000 或 000001,000002,600000")
        
        input_str = input("股票代码：").strip()
        if not input_str:
            input_str = '000001 000002 600000'
        
        # 解析股票代码
        symbols = [s.strip() for s in input_str.replace(',', ' ').split()]
        
        print(f"\n分析股票：{symbols}")
        stock_data = pool_manager.fetch_all_data()
        
        # 过滤
        filtered_data = {k: v for k, v in stock_data.items() if k in symbols}
        
        if filtered_data:
            recommender.analyze_multiple_stocks(filtered_data)
            recommender.print_recommendations(top_n=len(symbols))
        else:
            print("无法获取任何股票数据")
    
    else:
        print("无效选择")
        return
    
    print("\n" + "="*70)
    print("分析完成!")
    print("="*70)
    
    # 保存推荐列表
    if recommender.stock_signals:
        try:
            save_list = input("\n是否保存推荐列表？(y/n, 默认 y): ").strip().lower()
            if save_list != 'n':
                report_path = f'data/stock_recommendations_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
                recommender.generate_report(save_path=report_path)
        except EOFError:
            # 自动保存
            report_path = f'data/stock_recommendations_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
            recommender.generate_report(save_path=report_path)


if __name__ == "__main__":
    # 确保 data 目录存在
    if not os.path.exists('data'):
        os.makedirs('data')
    
    run_recommendation_demo()
