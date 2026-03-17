"""
实时价格更新模块

从数据源获取最新股票价格并更新到数据库
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

from utils.data_collector import StockDataCollector
from stock_database import StockDatabase


class RealTimePriceUpdater:
    """实时价格更新器"""

    def __init__(self, db_path: str = 'data/stock_data.db', token: str = None):
        """
        初始化更新器

        Parameters
        ----------
        db_path : str
            数据库路径
        token : str, optional
            Tushare token
        """
        self.db = StockDatabase(db_path)
        self.token = token
        self.collector = self._init_collector()

    def _init_collector(self):
        """初始化数据收集器（必须配置 Tushare token）"""
        try:
            import tushare as ts
            
            if self.token:
                ts.set_token(self.token)
                print("✓ Tushare token 已配置")
                return StockDataCollector(token=self.token)
            
            # 尝试从环境变量获取
            import os
            env_token = os.getenv('TUSHARE_TOKEN')
            if env_token:
                ts.set_token(env_token)
                print("✓ 从环境变量加载 Tushare token")
                self.token = env_token
                return StockDataCollector(token=self.token)
            
            # 必须配置 token
            print("=" * 70)
            print("错误：未配置 Tushare token")
            print("=" * 70)
            print("\n必须配置 Tushare token 才能获取股票数据")
            print("\n配置步骤:")
            print("1. 访问 https://tushare.pro/ 注册账号")
            print("2. 登录后在个人中心获取 token")
            print("3. 重新运行本程序并输入 token")
            print("\n或者设置环境变量:")
            print("  Windows: set TUSHARE_TOKEN=your_token")
            print("  Linux/Mac: export TUSHARE_TOKEN=your_token")
            print("=" * 70)
            
            # 尝试让用户输入 token
            try:
                token_input = input("\n请输入 Tushare token: ").strip()
                
                if token_input:
                    ts.set_token(token_input)
                    self.token = token_input
                    print("✓ Tushare token 已配置")
                    return StockDataCollector(token=self.token)
                else:
                    print("\n错误：必须提供 Tushare token")
                    return None
            except (EOFError, KeyboardInterrupt):
                print("\n错误：必须提供 Tushare token")
                return None
            
        except ImportError:
            print("⚠ 未安装 tushare")
            print("安装：pip install tushare")
            return None
    
    def update_single_stock(self, symbol: str, name: str = '') -> Dict:
        """
        更新单只股票价格（从 Tushare 获取真实数据）

        Parameters
        ----------
        symbol : str
            股票代码
        name : str
            股票名称

        Returns
        -------
        Dict
            更新结果
        """
        result = {
            'symbol': symbol,
            'success': False,
            'message': '',
            'new_records': 0,
            'latest_price': None,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_source': 'Tushare Pro'
        }

        # 检查是否配置了 token
        if not self.token:
            result['message'] = '错误：必须配置 Tushare token'
            return result

        try:
            # 获取数据库中最后更新日期
            last_date_query = """
                SELECT MAX(trade_date) as last_date
                FROM daily_prices
                WHERE symbol = ?
            """
            last_date_df = pd.read_sql_query(last_date_query, self.db.conn, params=(symbol,))

            if not last_date_df.empty and pd.notna(last_date_df['last_date'].iloc[0]):
                last_date = last_date_df['last_date'].iloc[0]
                # 转换为日期格式
                if isinstance(last_date, str):
                    last_date = datetime.strptime(last_date, '%Y%m%d')
                
                # 检查是否需要更新
                days_since_last = (datetime.now() - last_date).days
                if days_since_last < 1:
                    result['message'] = '数据已是最新'
                    result['success'] = True
                    # 获取最新价格
                    latest_data = self.db.get_stock_prices(symbol)
                    if not latest_data.empty:
                        result['latest_price'] = latest_data['close'].iloc[-1]
                    return result
                
                start_date = (last_date + timedelta(days=1)).strftime('%Y%m%d')
            else:
                # 如果没有数据，从 2026 年 1 月 1 日开始
                start_date = '20260101'

            end_date = datetime.now().strftime('%Y%m%d')

            # 从 Tushare 获取新数据
            print(f"从 Tushare 获取 {symbol} 数据：{start_date} 至 {end_date}")
            data = self.collector.get_stock_data(symbol, start_date, end_date)

            if data is None or data.empty:
                result['message'] = 'Tushare 无数据，请检查 token 或股票代码'
                return result

            # 保存股票信息
            if name:
                self.db.insert_stock_info(symbol, name)

            # 准备价格数据
            prices_df = data.copy()
            prices_df['trade_date'] = prices_df.index.strftime('%Y%m%d')

            if 'pre_close' not in prices_df.columns:
                prices_df['pre_close'] = prices_df['close'].shift(1)
            if 'change' not in prices_df.columns:
                prices_df['change'] = prices_df['close'] - prices_df['pre_close']
            if 'pct_chg' not in prices_df.columns:
                prices_df['pct_chg'] = (prices_df['change'] / prices_df['pre_close'] * 100).fillna(0)

            # 保存价格数据
            old_count = self.db.get_stock_prices(symbol).shape[0]
            self.db.insert_daily_prices(symbol, prices_df)

            # 计算技术指标
            data_with_indicators = self.collector.calculate_technical_indicators(data)
            indicators_df = data_with_indicators.copy()
            indicators_df['trade_date'] = indicators_df.index.strftime('%Y%m%d')
            indicators_df = self._calculate_all_indicators(indicators_df)
            self.db.insert_technical_indicators(symbol, indicators_df)

            # 更新趋势信号
            trend_signals = self._calculate_trend_signals(symbol, indicators_df)
            for trade_date, signal_data in trend_signals.items():
                self.db.insert_trend_signal(symbol, trade_date, signal_data)

            new_count = self.db.get_stock_prices(symbol).shape[0]
            result['new_records'] = new_count - old_count
            result['latest_price'] = data['close'].iloc[-1]
            result['success'] = True
            
            if result['new_records'] > 0:
                result['message'] = f'更新成功，新增 {result["new_records"]} 条记录'
            else:
                result['message'] = '数据已是最新，无新增记录'

        except Exception as e:
            result['message'] = f'更新失败：{str(e)}'

        return result
    
    def update_stock_pool(self, stock_pool: Dict[str, str], 
                         show_progress: bool = True) -> List[Dict]:
        """
        更新股票池价格
        
        Parameters
        ----------
        stock_pool : Dict[str, str]
            股票代码 -> 名称 的字典
        show_progress : bool
            是否显示进度
        
        Returns
        -------
        List[Dict]
            更新结果列表
        """
        results = []
        total = len(stock_pool)
        
        for i, (symbol, name) in enumerate(stock_pool.items(), 1):
            if show_progress:
                print(f"\n[{i}/{total}] 更新 {symbol} {name}")
                print("-" * 50)
            
            result = self.update_single_stock(symbol, name)
            results.append(result)
            
            if result['success']:
                print(f"  ✓ {result['message']}")
                if result['latest_price']:
                    print(f"  最新价格：{result['latest_price']:.2f}")
            else:
                print(f"  ✗ {result['message']}")
        
        return results
    
    def _calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算所有技术指标"""
        # MA60
        df['ma60'] = df['close'].rolling(window=60).mean()
        
        # KDJ
        low_9 = df['low'].rolling(window=9).min()
        high_9 = df['high'].rolling(window=9).max()
        rsv = (df['close'] - low_9) / (high_9 - low_9) * 100
        df['kdj_k'] = rsv.ewm(com=2).mean()
        df['kdj_d'] = df['kdj_k'].ewm(com=2).mean()
        df['kdj_j'] = 3 * df['kdj_k'] - 2 * df['kdj_d']
        
        # ATR
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df['atr'] = tr.rolling(window=14).mean()
        
        # OBV
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
            
            # 综合信号评分
            score = 0
            
            if ma_trend == 'BULLISH':
                score += 2
                if latest['close'] > latest.get('ma5', 0) > latest.get('ma10', 0):
                    score += 1
            else:
                score -= 2
            
            if macd_trend == 'BULLISH':
                score += 2
                if macd > 0:
                    score += 1
            else:
                score -= 2
            
            if rsi_status == 'OVERSOLD':
                score += 2
            elif rsi_status == 'OVERBOUGHT':
                score -= 2
            
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
    
    def get_update_summary(self, symbols: List[str] = None) -> pd.DataFrame:
        """
        获取更新摘要
        
        Parameters
        ----------
        symbols : List[str]
            股票代码列表
        
        Returns
        -------
        pd.DataFrame
            更新摘要
        """
        if symbols is None:
            query = "SELECT DISTINCT symbol FROM daily_prices"
            df = pd.read_sql_query(query, self.db.conn)
            symbols = df['symbol'].tolist()
        
        summary_data = []
        for symbol in symbols:
            prices = self.db.get_stock_prices(symbol)
            if not prices.empty:
                latest = prices.iloc[-1]
                summary_data.append({
                    'symbol': symbol,
                    'last_date': latest['trade_date'],
                    'last_price': latest['close'],
                    'last_change': latest.get('pct_chg', 0),
                    'total_records': len(prices)
                })
        
        return pd.DataFrame(summary_data)
    
    def close(self):
        """关闭数据库连接"""
        self.db.close()


def run_price_update():
    """运行价格更新"""
    print("=" * 70)
    print("股票价格更新器 - Tushare 数据源")
    print("=" * 70)

    updater = RealTimePriceUpdater()

    # 默认股票池
    stock_pool = {
        '000001': '平安银行',
        '000002': '万科 A',
        '600519': '贵州茅台',
    }

    print("\n选择更新模式:")
    print("1. 更新默认股票池 (3 只)")
    print("2. 更新单只股票")
    print("3. 自定义股票列表")
    print("4. 查看更新摘要")

    try:
        choice = input("\n请选择 (1-4, 默认 1): ").strip() or '1'
    except EOFError:
        choice = '1'

    if choice == '1':
        results = updater.update_stock_pool(stock_pool)

    elif choice == '2':
        try:
            symbol = input("股票代码 (默认 000001): ").strip() or '000001'
            name = stock_pool.get(symbol, '')
            try:
                name_input = input(f"股票名称 (默认 {name}): ").strip()
                name = name_input or name
            except EOFError:
                pass
        except EOFError:
            symbol = '000001'
            name = '平安银行'

        result = updater.update_single_stock(symbol, name)
        if result['success']:
            print(f"\n更新成功!")
            print(f"最新价格：{result['latest_price']:.2f}")
        else:
            print(f"\n更新失败：{result['message']}")

    elif choice == '3':
        print("\n输入股票代码，用空格分隔:")
        try:
            input_str = input("股票代码：").strip()
        except EOFError:
            input_str = '000001 000002 600519'
        
        if not input_str:
            input_str = '000001 000002 600519'

        symbols = [s.strip() for s in input_str.replace(',', ' ').split()]
        custom_pool = {s: stock_pool.get(s, '') for s in symbols}
        results = updater.update_stock_pool(custom_pool)

    elif choice == '4':
        summary = updater.get_update_summary()
        print("\n更新摘要:")
        print(summary.to_string(index=False))

    else:
        print("无效选择")

    updater.close()
    print("\n" + "=" * 70)
    print("更新完成!")
    print("=" * 70)


if __name__ == "__main__":
    run_price_update()
