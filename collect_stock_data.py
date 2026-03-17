"""
股票数据收集器

从 2026 年 1 月至今收集股票价格和技术指标数据
存储到 SQLite 数据库供推荐系统使用
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict
import warnings
warnings.filterwarnings('ignore')

from stock_database import StockDatabase
from utils.data_collector import StockDataCollector


class StockDataCollectorDB:
    """股票数据收集器（数据库版）"""
    
    def __init__(self, db_path: str = 'data/stock_data.db'):
        """
        初始化收集器
        
        Parameters
        ----------
        db_path : str
            数据库路径
        """
        self.db = StockDatabase(db_path)
        self.collector = StockDataCollector()
    
    def collect_stock_data(self, symbol: str, name: str = '',
                          start_date: str = '20260101',
                          end_date: str = None,
                          save_indicators: bool = True) -> bool:
        """
        收集单只股票数据
        
        Parameters
        ----------
        symbol : str
            股票代码
        name : str
            股票名称
        start_date : str
            开始日期，格式 YYYYMMDD
        end_date : str
            结束日期，默认今天
        save_indicators : bool
            是否保存技术指标
        
        Returns
        -------
        bool
            是否成功
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        
        print(f"\n收集 {symbol} {name} 的数据...")
        print(f"日期范围：{start_date} 至 {end_date}")
        
        try:
            # 获取股票数据
            data = self.collector.get_stock_data(symbol, start_date, end_date)
            
            if data is None or data.empty:
                print(f"  ⚠ 无法获取 {symbol} 的数据")
                return False
            
            print(f"  ✓ 获取到 {len(data)} 条价格数据")
            
            # 保存股票信息
            self.db.insert_stock_info(symbol, name)
            
            # 准备价格数据
            prices_df = data.copy()
            prices_df['trade_date'] = prices_df.index.strftime('%Y%m%d')
            
            if 'pre_close' not in prices_df.columns:
                prices_df['pre_close'] = prices_df['close'].shift(1)
            if 'change' not in prices_df.columns:
                prices_df['change'] = prices_df['close'] - prices_df['pre_close']
            if 'pct_chg' not in prices_df.columns:
                prices_df['pct_chg'] = (prices_df['change'] / prices_df['pre_close']) * 100
            
            # 保存价格数据
            self.db.insert_daily_prices(symbol, prices_df)
            print(f"  ✓ 价格数据已保存")
            
            # 计算并保存技术指标
            if save_indicators:
                data_with_indicators = self.collector.calculate_technical_indicators(data)
                
                indicators_df = data_with_indicators.copy()
                indicators_df['trade_date'] = indicators_df.index.strftime('%Y%m%d')
                
                # 计算额外指标
                indicators_df = self._calculate_all_indicators(indicators_df)
                
                self.db.insert_technical_indicators(symbol, indicators_df)
                print(f"  ✓ 技术指标已保存")
                
                # 计算趋势信号
                trend_signals = self._calculate_trend_signals(symbol, indicators_df)
                for trade_date, signal_data in trend_signals.items():
                    self.db.insert_trend_signal(symbol, trade_date, signal_data)
                print(f"  ✓ 趋势信号已保存")
            
            return True
            
        except Exception as e:
            print(f"  ✗ 错误：{e}")
            return False
    
    def _calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算所有技术指标"""
        # 基础指标已在 calculate_technical_indicators 中计算
        
        # 添加 MA60
        df['ma60'] = df['close'].rolling(window=60).mean()
        
        # 计算 KDJ
        low_9 = df['low'].rolling(window=9).min()
        high_9 = df['high'].rolling(window=9).max()
        rsv = (df['close'] - low_9) / (high_9 - low_9) * 100
        df['kdj_k'] = rsv.ewm(com=2).mean()
        df['kdj_d'] = df['kdj_k'].ewm(com=2).mean()
        df['kdj_j'] = 3 * df['kdj_k'] - 2 * df['kdj_d']
        
        # 计算 ATR
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df['atr'] = tr.rolling(window=14).mean()
        
        # 计算 OBV
        df['obv'] = (np.sign(df['close'].diff()) * df['vol']).fillna(0).cumsum()
        
        return df
    
    def _calculate_trend_signals(self, symbol: str, data: pd.DataFrame) -> Dict:
        """计算趋势信号"""
        signals = {}
        
        for idx in range(20, len(data)):
            subset = data.iloc[:idx+1].copy()
            latest = subset.iloc[-1]
            trade_date = latest['trade_date']
            
            # 均线趋势
            ma_trend = 'BULLISH' if latest['close'] > latest.get('ma20', 0) else 'BEARISH'
            
            # MACD 趋势
            macd = latest.get('macd', 0)
            macd_signal = latest.get('macd_signal', 0)
            macd_trend = 'BULLISH' if macd > macd_signal else 'BEARISH'
            
            # RSI 状态
            rsi = latest.get('rsi', 50)
            if rsi > 70:
                rsi_status = 'OVERBOUGHT'
            elif rsi < 30:
                rsi_status = 'OVERSOLD'
            else:
                rsi_status = 'NEUTRAL'
            
            # 成交量状态
            avg_vol_5 = subset['vol'].tail(5).mean()
            avg_vol_20 = subset['vol'].tail(20).mean()
            if avg_vol_5 > avg_vol_20 * 1.5:
                volume_status = 'HIGH'
            elif avg_vol_5 < avg_vol_20 * 0.5:
                volume_status = 'LOW'
            else:
                volume_status = 'NORMAL'
            
            # 综合信号评分 (-10 到 10)
            score = 0
            
            # 均线评分
            if ma_trend == 'BULLISH':
                score += 2
                if latest['close'] > latest.get('ma5', 0) > latest.get('ma10', 0):
                    score += 1
            else:
                score -= 2
            
            # MACD 评分
            if macd_trend == 'BULLISH':
                score += 2
                if macd > 0:
                    score += 1
            else:
                score -= 2
            
            # RSI 评分
            if rsi_status == 'OVERSOLD':
                score += 2
            elif rsi_status == 'OVERBOUGHT':
                score -= 2
            
            # 成交量评分
            if volume_status == 'HIGH' and ma_trend == 'BULLISH':
                score += 1
            elif volume_status == 'HIGH' and ma_trend == 'BEARISH':
                score -= 1
            
            # 确定推荐
            if score >= 7:
                recommendation = 'STRONG_BUY'
            elif score >= 4:
                recommendation = 'BUY'
            elif score >= -4:
                recommendation = 'HOLD'
            elif score >= -7:
                recommendation = 'SELL'
            else:
                recommendation = 'STRONG_SELL'
            
            # 趋势强度
            if abs(score) >= 7:
                trend_strength = 'STRONG'
            elif abs(score) >= 4:
                trend_strength = 'MODERATE'
            else:
                trend_strength = 'WEAK'
            
            signals[trade_date] = {
                'trend_type': ma_trend,
                'trend_strength': trend_strength,
                'signal_type': 'BUY' if score > 0 else 'SELL',
                'signal_score': score,
                'ma_trend': ma_trend,
                'macd_trend': macd_trend,
                'rsi_status': rsi_status,
                'volume_status': volume_status,
                'recommendation': recommendation
            }
        
        return signals
    
    def collect_stock_pool(self, stock_pool: Dict[str, str],
                          start_date: str = '20260101') -> Dict:
        """
        收集股票池数据
        
        Parameters
        ----------
        stock_pool : Dict[str, str]
            股票代码 -> 名称的字典
        start_date : str
            开始日期
        
        Returns
        -------
        Dict
            收集结果统计
        """
        results = {'success': 0, 'failed': 0, 'symbols': []}
        
        total = len(stock_pool)
        for i, (symbol, name) in enumerate(stock_pool.items(), 1):
            print(f"\n[{i}/{total}] 处理 {symbol} {name}")
            print("-" * 50)
            
            success = self.collect_stock_data(symbol, name, start_date)
            
            if success:
                results['success'] += 1
                results['symbols'].append(symbol)
            else:
                results['failed'] += 1
        
        print("\n" + "=" * 50)
        print("数据收集完成")
        print(f"成功：{results['success']} 只股票")
        print(f"失败：{results['failed']} 只股票")
        
        return results
    
    def get_collected_stocks(self) -> pd.DataFrame:
        """获取已收集的股票列表"""
        query = "SELECT symbol, name, market, industry FROM stocks ORDER BY symbol"
        return pd.read_sql_query(query, self.db.conn)
    
    def analyze_stock_pool(self, symbols: List[str] = None) -> pd.DataFrame:
        """
        分析股票池
        
        Parameters
        ----------
        symbols : List[str]
            股票代码列表，None 表示所有股票
        
        Returns
        -------
        pd.DataFrame
            分析结果
        """
        if symbols is None:
            stocks_df = self.get_collected_stocks()
            symbols = stocks_df['symbol'].tolist()
        
        return self.db.get_stock_pool_analysis(symbols)
    
    def close(self):
        """关闭数据库连接"""
        self.db.close()


# 默认股票池（精选 50 只热门股票）
DEFAULT_STOCK_POOL = {
    # 银行金融
    '000001': '平安银行',
    '000002': '万科 A',
    '600000': '浦发银行',
    '600036': '招商银行',
    '601318': '中国平安',
    '601398': '工商银行',
    
    # 消费
    '000858': '五粮液',
    '600519': '贵州茅台',
    '600809': '山西汾酒',
    '600887': '伊利股份',
    '000333': '美的集团',
    '000651': '格力电器',
    '600690': '海尔智家',
    
    # 科技
    '000063': '中兴通讯',
    '000725': '京东方 A',
    '002230': '科大讯飞',
    '002415': '海康威视',
    '300059': '东方财富',
    '300750': '宁德时代',
    '603019': '中科曙光',
    
    # 医药
    '000538': '云南白药',
    '002007': '华兰生物',
    '300122': '智飞生物',
    '300760': '迈瑞医疗',
    '600276': '恒瑞医药',
    '600436': '片仔癀',
    '603259': '药明康德',
    
    # 新能源
    '002594': '比亚迪',
    '300014': '亿纬锂能',
    '300274': '阳光电源',
    '601012': '隆基股份',
    '603799': '华友钴业',
    
    # 其他
    '000001': '平安银行',
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


def main():
    """主函数"""
    print("=" * 70)
    print("股票数据收集器")
    print("=" * 70)
    
    # 选择模式
    print("\n选择收集模式:")
    print("1. 收集默认股票池 (50 只热门股票)")
    print("2. 收集单只股票")
    print("3. 自定义股票列表")
    print("4. 创建示例数据")
    
    choice = input("\n请输入选择 (1-4, 默认 1): ").strip() or '1'
    
    collector = StockDataCollectorDB()
    
    if choice == '1':
        # 默认股票池
        print(f"\n收集 {len(DEFAULT_STOCK_POOL)} 只热门股票数据...")
        print("数据期间：2026 年 1 月至今")
        
        results = collector.collect_stock_pool(DEFAULT_STOCK_POOL, '20260101')
        
        # 显示分析结果
        if results['success'] > 0:
            print("\n股票池分析:")
            analysis = collector.analyze_stock_pool(results['symbols'][:10])
            if not analysis.empty:
                print(analysis[['symbol', 'name', 'signal_score', 'recommendation', 'price']].to_string())
    
    elif choice == '2':
        # 单只股票
        symbol = input("请输入股票代码 (默认 000001): ").strip() or '000001'
        name = DEFAULT_STOCK_POOL.get(symbol, '')
        name_input = input(f"股票名称 (默认 {name}): ").strip()
        name = name_input or name
        
        collector.collect_stock_data(symbol, name, '20260101')
        
        # 显示趋势分析
        trend = collector.db.get_price_trend_analysis(symbol)
        if trend:
            print(f"\n趋势分析:")
            for key, value in trend.items():
                print(f"  {key}: {value}")
    
    elif choice == '3':
        # 自定义股票列表
        print("\n请输入股票代码，用空格或逗号分隔")
        input_str = input("股票代码：").strip()
        
        if not input_str:
            input_str = '000001 000002 600519'
        
        symbols = [s.strip() for s in input_str.replace(',', ' ').split()]
        
        custom_pool = {s: DEFAULT_STOCK_POOL.get(s, '') for s in symbols}
        collector.collect_stock_pool(custom_pool, '20260101')
    
    elif choice == '4':
        # 示例数据
        print("\n创建示例数据...")
        from stock_database import create_sample_database
        create_sample_database()
    
    else:
        print("无效选择")
    
    collector.close()
    
    print("\n" + "=" * 70)
    print("数据收集完成!")
    print("=" * 70)
    print(f"\n数据库位置：data/stock_data.db")
    print("可以使用以下工具分析数据:")
    print("  - run_stock_recommender.py - 股票推荐")
    print("  - main.py - 主程序")


if __name__ == "__main__":
    main()
