"""
股票筛选器模块

基于技术指标和策略信号，筛选符合条件的股票
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
from stock_database import StockDatabase


class StockScreener:
    """股票筛选器"""
    
    def __init__(self, db_path: str = 'data/stock_data.db'):
        """
        初始化筛选器
        
        Parameters
        ----------
        db_path : str
            数据库路径
        """
        self.db = StockDatabase(db_path)
    
    def screen_by_recommendation(self, 
                                  recommendation: List[str] = None,
                                  min_score: float = None,
                                  max_risk: str = None) -> pd.DataFrame:
        """
        按推荐筛选股票
        
        Parameters
        ----------
        recommendation : List[str]
            推荐等级列表，如 ['STRONG_BUY', 'BUY']
        min_score : float
            最低评分
        max_risk : str
            最高风险等级 ('LOW', 'MEDIUM', 'HIGH')
        
        Returns
        -------
        pd.DataFrame
            筛选结果
        """
        # 获取最新趋势信号
        signals = self.db.get_latest_trend_signals(limit=1000)
        
        # 筛选
        if recommendation:
            signals = signals[signals['recommendation'].isin(recommendation)]
        
        if min_score is not None:
            signals = signals[signals['signal_score'] >= min_score]
        
        return signals
    
    def screen_by_technical(self,
                            ma_trend: str = None,
                            rsi_range: tuple = None,
                            macd_positive: bool = None,
                            volume_status: str = None) -> pd.DataFrame:
        """
        按技术指标筛选
        
        Parameters
        ----------
        ma_trend : str
            均线趋势 ('BULLISH' 或 'BEARISH')
        rsi_range : tuple
            RSI 范围 (min, max)
        macd_positive : bool
            MACD 是否为正
        volume_status : str
            成交量状态 ('HIGH', 'NORMAL', 'LOW')
        
        Returns
        -------
        pd.DataFrame
            筛选结果
        """
        signals = self.db.get_latest_trend_signals(limit=1000)
        
        if ma_trend:
            signals = signals[signals['ma_trend'] == ma_trend]
        
        if rsi_range:
            signals = signals[
                (signals['rsi_status'].map({
                    'OVERSOLD': 20,
                    'NEUTRAL': 50,
                    'OVERBOUGHT': 80
                }) >= rsi_range[0]) &
                (signals['rsi_status'].map({
                    'OVERSOLD': 20,
                    'NEUTRAL': 50,
                    'OVERBOUGHT': 80
                }) <= rsi_range[1])
            ]
        
        if macd_positive is not None:
            if macd_positive:
                signals = signals[signals['macd_trend'] == 'BULLISH']
            else:
                signals = signals[signals['macd_trend'] == 'BEARISH']
        
        if volume_status:
            signals = signals[signals['volume_status'] == volume_status]
        
        return signals
    
    def screen_golden_cross(self) -> pd.DataFrame:
        """筛选均线金叉股票"""
        query = '''
            SELECT 
                t.symbol,
                s.name,
                i.ma5,
                i.ma10,
                i.ma20,
                d.close as price,
                d.pct_chg,
                t.signal_score,
                t.recommendation
            FROM trend_signals t
            LEFT JOIN stocks s ON t.symbol = s.symbol
            LEFT JOIN daily_prices d 
                ON t.symbol = d.symbol AND t.trade_date = d.trade_date
            LEFT JOIN technical_indicators i 
                ON t.symbol = i.symbol AND t.trade_date = i.trade_date
            WHERE t.trade_date = (
                SELECT MAX(trade_date) FROM trend_signals 
                WHERE symbol = t.symbol
            )
            AND i.ma5 > i.ma10
            AND i.ma10 > i.ma20
            AND d.close > i.ma5
            ORDER BY t.signal_score DESC
        '''
        
        return pd.read_sql_query(query, self.db.conn)
    
    def screen_oversold(self, rsi_threshold: float = 30) -> pd.DataFrame:
        """筛选超卖股票"""
        query = '''
            SELECT 
                t.symbol,
                s.name,
                i.rsi,
                d.close as price,
                d.pct_chg,
                t.signal_score,
                t.recommendation
            FROM technical_indicators i
            LEFT JOIN stocks s ON i.symbol = s.symbol
            LEFT JOIN daily_prices d 
                ON i.symbol = d.symbol AND i.trade_date = d.trade_date
            LEFT JOIN trend_signals t
                ON i.symbol = t.symbol AND i.trade_date = t.trade_date
            WHERE i.rsi < ?
            AND i.trade_date = (
                SELECT MAX(trade_date) FROM technical_indicators 
                WHERE symbol = i.symbol
            )
            ORDER BY i.rsi ASC
        '''
        
        return pd.read_sql_query(query, self.db.conn, params=(rsi_threshold,))
    
    def screen_breakout(self, 
                        period: int = 20,
                        volume_multiplier: float = 2.0) -> pd.DataFrame:
        """筛选突破股票"""
        query = f'''
            SELECT 
                t.symbol,
                s.name,
                d.close as price,
                d.pct_chg,
                d.vol,
                (SELECT AVG(close) FROM daily_prices 
                 WHERE symbol = d.symbol 
                 AND trade_date >= date(d.trade_date, '-{period} days')
                ) as avg_price_{period}d,
                (SELECT AVG(vol) FROM daily_prices 
                 WHERE symbol = d.symbol 
                 AND trade_date >= date(d.trade_date, '-{period} days')
                ) as avg_vol,
                t.signal_score,
                t.recommendation
            FROM daily_prices d
            LEFT JOIN stocks s ON d.symbol = s.symbol
            LEFT JOIN trend_signals t
                ON d.symbol = t.symbol AND d.trade_date = t.trade_date
            WHERE d.trade_date = (
                SELECT MAX(trade_date) FROM daily_prices 
                WHERE symbol = d.symbol
            )
            AND d.vol > (
                SELECT AVG(vol) * {volume_multiplier} FROM daily_prices 
                WHERE symbol = d.symbol 
                AND trade_date >= date(d.trade_date, '-{period} days')
            )
            ORDER BY d.pct_chg DESC
        '''
        
        return pd.read_sql_query(query, self.db.conn)
    
    def screen_high_momentum(self, 
                             period: int = 10,
                             min_return: float = 5.0) -> pd.DataFrame:
        """筛选高动量股票"""
        query = f'''
            WITH price_returns AS (
                SELECT 
                    symbol,
                    trade_date,
                    close,
                    (close - LAG(close, {period}) OVER (PARTITION BY symbol ORDER BY trade_date)) 
                    / LAG(close, {period}) OVER (PARTITION BY symbol ORDER BY trade_date) * 100 as return_{period}d
                FROM daily_prices
            )
            SELECT 
                r.symbol,
                s.name,
                r.close as price,
                r.return_{period}d,
                t.signal_score,
                t.recommendation
            FROM price_returns r
            LEFT JOIN stocks s ON r.symbol = s.symbol
            LEFT JOIN trend_signals t
                ON r.symbol = t.symbol AND r.trade_date = t.trade_date
            WHERE r.trade_date = (
                SELECT MAX(trade_date) FROM daily_prices 
                WHERE symbol = r.symbol
            )
            AND r.return_{period}d >= ?
            ORDER BY r.return_{period}d DESC
        '''
        
        return pd.read_sql_query(query, self.db.conn, params=(min_return,))
    
    def create_custom_screen(self, conditions: Dict) -> pd.DataFrame:
        """
        创建自定义筛选
        
        Parameters
        ----------
        conditions : Dict
            筛选条件字典
            示例：
            {
                'min_score': 4,
                'ma_trend': 'BULLISH',
                'recommendation': ['STRONG_BUY', 'BUY'],
                'max_price': 100,
                'min_volume': 1000000
            }
        
        Returns
        -------
        pd.DataFrame
            筛选结果
        """
        signals = self.db.get_latest_trend_signals(limit=1000)
        
        # 应用条件
        if 'min_score' in conditions:
            signals = signals[signals['signal_score'] >= conditions['min_score']]
        
        if 'ma_trend' in conditions:
            signals = signals[signals['ma_trend'] == conditions['ma_trend']]
        
        if 'recommendation' in conditions:
            signals = signals[signals['recommendation'].isin(conditions['recommendation'])]
        
        if 'rsi_max' in conditions:
            signals = signals[signals['rsi'] <= conditions['rsi_max']]
        
        if 'rsi_min' in conditions:
            signals = signals[signals['rsi'] >= conditions['rsi_min']]
        
        return signals
    
    def save_screen_results(self, 
                           results: pd.DataFrame, 
                           screen_name: str,
                           save_path: str = None):
        """保存筛选结果"""
        if save_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = f'data/screen_{screen_name}_{timestamp}.csv'
        
        results.to_csv(save_path, index=False, encoding='utf-8-sig')
        print(f"筛选结果已保存到：{save_path}")
    
    def close(self):
        """关闭数据库连接"""
        self.db.close()


def run_screener_demo():
    """运行筛选器演示"""
    print("=" * 70)
    print("股票筛选器")
    print("=" * 70)
    
    screener = StockScreener()
    
    print("\n选择筛选模式:")
    print("1. 强烈买入股票 (STRONG_BUY)")
    print("2. 均线多头排列")
    print("3. RSI 超卖股票")
    print("4. 成交量突破")
    print("5. 高动量股票")
    print("6. 自定义筛选")
    
    choice = input("\n请输入选择 (1-6, 默认 1): ").strip() or '1'
    
    if choice == '1':
        # 强烈买入
        results = screener.screen_by_recommendation(
            recommendation=['STRONG_BUY'],
            min_score=7
        )
        print(f"\n找到 {len(results)} 只强烈买入股票")
        
    elif choice == '2':
        # 均线多头
        results = screener.screen_golden_cross()
        print(f"\n找到 {len(results)} 只均线多头排列股票")
        
    elif choice == '3':
        # RSI 超卖
        results = screener.screen_oversold(rsi_threshold=30)
        print(f"\n找到 {len(results)} 只 RSI 超卖股票")
        
    elif choice == '4':
        # 成交量突破
        results = screener.screen_breakout(
            period=20,
            volume_multiplier=2.0
        )
        print(f"\n找到 {len(results)} 只成交量突破股票")
        
    elif choice == '5':
        # 高动量
        results = screener.screen_high_momentum(
            period=10,
            min_return=5.0
        )
        print(f"\n找到 {len(results)} 只高动量股票")
        
    elif choice == '6':
        # 自定义
        print("\n输入筛选条件:")
        min_score = float(input("最低评分 (默认 4): ").strip() or '4')
        ma_trend = input("均线趋势 (BULLISH/BEARISH, 默认 BULLISH): ").strip() or 'BULLISH'
        
        results = screener.create_custom_screen({
            'min_score': min_score,
            'ma_trend': ma_trend,
            'recommendation': ['STRONG_BUY', 'BUY']
        })
        print(f"\n找到 {len(results)} 只符合条件的股票")
    
    else:
        print("无效选择")
        screener.close()
        return
    
    # 显示结果
    if not results.empty:
        print("\n" + "=" * 70)
        print("筛选结果")
        print("=" * 70)
        
        # 显示前 20 只
        display_cols = [col for col in ['symbol', 'name', 'price', 'signal_score', 
                       'recommendation', 'pct_chg'] if col in results.columns]
        print(results[display_cols].head(20).to_string(index=False))
        
        # 保存结果
        save = input("\n是否保存结果？(y/n, 默认 y): ").strip().lower()
        if save != 'n':
            screener.save_screen_results(results, f'screen_{choice}')
    
    screener.close()
    print("\n筛选完成!")


if __name__ == "__main__":
    run_screener_demo()
