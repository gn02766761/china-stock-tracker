"""
从 Tushare 导入股票数据到 SQL 数据库

支持批量导入 A 股股票历史数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import warnings
warnings.filterwarnings('ignore')

from stock_database import StockDatabase


class TushareDataImporter:
    """Tushare 数据导入器"""
    
    def __init__(self, db_path: str = 'data/stock_data.db', token: str = None):
        """
        初始化导入器
        
        Parameters
        ----------
        db_path : str
            数据库路径
        token : str
            Tushare token
        """
        self.db = StockDatabase(db_path)
        self.token = token
        self.pro = None
        
        # 初始化 Tushare
        self._init_tushare()
    
    def _init_tushare(self):
        """初始化 Tushare Pro"""
        try:
            import tushare as ts
            
            if self.token:
                ts.set_token(self.token)
                self.pro = ts.pro_api()
                print("✓ Tushare Pro 初始化成功")
            else:
                # 尝试从环境变量获取
                env_token = os.getenv('TUSHARE_TOKEN')
                if env_token:
                    ts.set_token(env_token)
                    self.pro = ts.pro_api()
                    self.token = env_token
                    print("✓ 从环境变量加载 Tushare token")
                else:
                    print("=" * 70)
                    print("错误：未配置 Tushare token")
                    print("=" * 70)
                    print("\n获取 token 步骤:")
                    print("1. 访问 https://tushare.pro/ 注册账号")
                    print("2. 登录后在个人中心获取 token")
                    print("3. 重新运行本程序并输入 token")
                    print("\n或者设置环境变量:")
                    print("  Windows: set TUSHARE_TOKEN=your_token")
                    print("  Linux/Mac: export TUSHARE_TOKEN=your_token")
                    print("=" * 70)
                    
                    try:
                        token_input = input("\n请输入 Tushare token: ").strip()
                        if token_input:
                            ts.set_token(token_input)
                            self.pro = ts.pro_api()
                            self.token = token_input
                            print("✓ Tushare token 已配置")
                        else:
                            print("\n错误：必须提供 Tushare token")
                            self.pro = None
                    except (EOFError, KeyboardInterrupt):
                        print("\n错误：必须提供 Tushare token")
                        self.pro = None
                        
        except ImportError:
            print("⚠ 未安装 tushare")
            print("安装：pip install tushare")
            self.pro = None
    
    def get_stock_list(self) -> pd.DataFrame:
        """
        获取 A 股股票列表
        
        Returns
        -------
        pd.DataFrame
            股票列表
        """
        if not self.pro:
            print("错误：Tushare 未初始化")
            return pd.DataFrame()
        
        try:
            print("获取 A 股股票列表...")
            stock_list = self.pro.stock_basic(
                exchange='',
                list_status='L',
                fields='ts_code,symbol,name,area,industry,list_date'
            )
            
            print(f"✓ 获取到 {len(stock_list)} 只股票")
            return stock_list
            
        except Exception as e:
            print(f"错误：{e}")
            return pd.DataFrame()
    
    def import_stock_data(self, ts_code: str, name: str = '',
                         start_date: str = '20260101',
                         end_date: str = None) -> bool:
        """
        导入单只股票数据
        
        Parameters
        ----------
        ts_code : str
            Tushare 股票代码（如：000001.SZ）
        name : str
            股票名称
        start_date : str
            开始日期，格式 YYYYMMDD
        end_date : str
            结束日期，默认今天
        
        Returns
        -------
        bool
            是否成功
        """
        if not self.pro:
            return False
        
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        
        # 提取纯数字代码
        symbol = ts_code.split('.')[0]
        
        try:
            print(f"导入 {ts_code} {name} 数据：{start_date} 至 {end_date}")
            
            # 获取日线数据
            df = self.pro.daily(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )
            
            if df is None or df.empty:
                print(f"  ⚠ 无数据")
                return False
            
            print(f"  ✓ 获取到 {len(df)} 条记录")
            
            # 保存股票信息
            self.db.insert_stock_info(symbol, name)
            
            # 准备价格数据
            df = df.sort_values('trade_date')
            df['trade_date'] = df['trade_date'].astype(str)
            
            # 保存价格数据
            self.db.insert_daily_prices(symbol, df)
            print(f"  ✓ 价格数据已保存")
            
            # 计算并保存技术指标
            df_indexed = df.set_index('trade_date')
            data_with_indicators = self._calculate_indicators(df_indexed)
            indicators_df = data_with_indicators.copy()
            indicators_df['trade_date'] = indicators_df.index
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
    
    def import_stock_pool(self, stock_list: List[Dict],
                         start_date: str = '20260101',
                         end_date: str = None) -> Dict:
        """
        批量导入股票池数据
        
        Parameters
        ----------
        stock_list : List[Dict]
            股票列表，包含 ts_code 和 name
        start_date : str
            开始日期
        end_date : str
            结束日期
        
        Returns
        -------
        Dict
            导入结果统计
        """
        results = {'success': 0, 'failed': 0, 'symbols': []}
        total = len(stock_list)
        
        for i, stock in enumerate(stock_list, 1):
            ts_code = stock.get('ts_code', '')
            name = stock.get('name', '')
            
            print(f"\n[{i}/{total}] 导入 {ts_code} {name}")
            print("-" * 50)
            
            success = self.import_stock_data(ts_code, name, start_date, end_date)
            
            if success:
                results['success'] += 1
                results['symbols'].append(ts_code.split('.')[0])
            else:
                results['failed'] += 1
        
        print("\n" + "=" * 50)
        print("导入完成")
        print(f"成功：{results['success']} 只股票")
        print(f"失败：{results['failed']} 只股票")
        
        return results
    
    def import_top_stocks(self, count: int = 50,
                         start_date: str = '20260101',
                         end_date: str = None) -> Dict:
        """
        导入热门股票数据
        
        Parameters
        ----------
        count : int
            导入股票数量
        start_date : str
            开始日期
        end_date : str
            结束日期
        
        Returns
        -------
        Dict
            导入结果
        """
        # 热门股票池（手动选择）
        top_stocks = [
            # 银行金融
            {'ts_code': '000001.SZ', 'name': '平安银行'},
            {'ts_code': '000002.SZ', 'name': '万科 A'},
            {'ts_code': '600000.SH', 'name': '浦发银行'},
            {'ts_code': '600036.SH', 'name': '招商银行'},
            {'ts_code': '601318.SH', 'name': '中国平安'},
            {'ts_code': '601398.SH', 'name': '工商银行'},
            
            # 消费
            {'ts_code': '000858.SZ', 'name': '五粮液'},
            {'ts_code': '600519.SH', 'name': '贵州茅台'},
            {'ts_code': '600809.SH', 'name': '山西汾酒'},
            {'ts_code': '600887.SH', 'name': '伊利股份'},
            {'ts_code': '000333.SZ', 'name': '美的集团'},
            {'ts_code': '000651.SZ', 'name': '格力电器'},
            
            # 科技
            {'ts_code': '000063.SZ', 'name': '中兴通讯'},
            {'ts_code': '000725.SZ', 'name': '京东方 A'},
            {'ts_code': '002230.SZ', 'name': '科大讯飞'},
            {'ts_code': '002415.SZ', 'name': '海康威视'},
            {'ts_code': '300059.SZ', 'name': '东方财富'},
            {'ts_code': '300750.SZ', 'name': '宁德时代'},
            
            # 医药
            {'ts_code': '000538.SZ', 'name': '云南白药'},
            {'ts_code': '002007.SZ', 'name': '华兰生物'},
            {'ts_code': '300122.SZ', 'name': '智飞生物'},
            {'ts_code': '300760.SZ', 'name': '迈瑞医疗'},
            {'ts_code': '600276.SH', 'name': '恒瑞医药'},
            {'ts_code': '600436.SH', 'name': '片仔癀'},
            
            # 新能源
            {'ts_code': '002594.SZ', 'name': '比亚迪'},
            {'ts_code': '300014.SZ', 'name': '亿纬锂能'},
            {'ts_code': '300274.SZ', 'name': '阳光电源'},
            {'ts_code': '601012.SH', 'name': '隆基股份'},
            {'ts_code': '603799.SH', 'name': '华友钴业'},
        ]
        
        # 限制数量
        if count < len(top_stocks):
            stock_pool = top_stocks[:count]
        else:
            stock_pool = top_stocks
        
        print(f"导入 {len(stock_pool)} 只热门股票数据...")
        return self.import_stock_pool(stock_pool, start_date, end_date)
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算基础技术指标"""
        # 均线
        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma10'] = df['close'].rolling(window=10).mean()
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['ma30'] = df['close'].rolling(window=30).mean()
        
        # EMA
        df['ema12'] = df['close'].ewm(span=12).mean()
        df['ema26'] = df['close'].ewm(span=26).mean()
        
        # MACD
        df['macd'] = df['ema12'] - df['ema26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # 布林带
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        
        return df
    
    def _calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算所有技术指标"""
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
            
            ma_trend = 'BULLISH' if latest['close'] > latest.get('ma20', 0) else 'BEARISH'
            macd = latest.get('macd', 0)
            macd_signal = latest.get('macd_signal', 0)
            macd_trend = 'BULLISH' if macd > macd_signal else 'BEARISH'
            
            rsi = latest.get('rsi', 50)
            if rsi > 70:
                rsi_status = 'OVERBOUGHT'
            elif rsi < 30:
                rsi_status = 'OVERSOLD'
            else:
                rsi_status = 'NEUTRAL'
            
            score = 0
            if ma_trend == 'BULLISH':
                score += 2
            else:
                score -= 2
            
            if macd_trend == 'BULLISH':
                score += 2
            else:
                score -= 2
            
            if rsi_status == 'OVERSOLD':
                score += 2
            elif rsi_status == 'OVERBOUGHT':
                score -= 2
            
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
            
            signals[trade_date if isinstance(trade_date, str) else str(trade_date)] = {
                'trend_type': ma_trend,
                'trend_strength': 'STRONG' if abs(score) >= 7 else 'MODERATE' if abs(score) >= 4 else 'WEAK',
                'signal_type': 'BUY' if score > 0 else 'SELL',
                'signal_score': score,
                'ma_trend': ma_trend,
                'macd_trend': macd_trend,
                'rsi_status': rsi_status,
                'volume_status': 'NORMAL',
                'recommendation': recommendation
            }
        
        return signals
    
    def get_database_summary(self) -> pd.DataFrame:
        """获取数据库摘要"""
        return self.db.get_collected_stocks()
    
    def close(self):
        """关闭数据库连接"""
        self.db.close()


def main():
    """主函数"""
    print("=" * 70)
    print("Tushare 数据导入工具")
    print("=" * 70)
    
    importer = TushareDataImporter()
    
    if not importer.pro:
        print("\n错误：Tushare 未初始化，无法导入数据")
        return
    
    print("\n选择导入模式:")
    print("1. 导入热门股票 (30 只)")
    print("2. 导入单只股票")
    print("3. 自定义股票列表")
    print("4. 查看数据库摘要")
    
    try:
        choice = input("\n请选择 (1-4, 默认 1): ").strip() or '1'
    except (EOFError, KeyboardInterrupt):
        choice = '1'
    
    if choice == '1':
        # 导入热门股票
        print("\n导入热门股票数据...")
        results = importer.import_top_stocks(count=30)
        
    elif choice == '2':
        # 单只股票
        ts_code = input("请输入 Tushare 代码 (如 000001.SZ): ").strip()
        if not ts_code:
            ts_code = '000001.SZ'
        
        name = input("股票名称：").strip()
        
        importer.import_stock_data(ts_code, name, '20260101')
        
    elif choice == '3':
        # 自定义列表
        print("\n输入股票代码，用空格分隔")
        print("格式：代码 1.市场 代码 2.市场 ...")
        print("示例：000001.SZ 600519.SH 000858.SZ")
        
        try:
            input_str = input("股票代码：").strip()
        except (EOFError, KeyboardInterrupt):
            input_str = '000001.SZ 600519.SH'
        
        if not input_str:
            input_str = '000001.SZ 600519.SH'
        
        codes = [s.strip() for s in input_str.replace(',', ' ').split()]
        stock_list = [{'ts_code': code, 'name': ''} for code in codes]
        
        importer.import_stock_pool(stock_list)
        
    elif choice == '4':
        # 查看摘要
        summary = importer.get_database_summary()
        print("\n数据库摘要:")
        if not summary.empty:
            print(summary.to_string(index=False))
        else:
            print("数据库为空")
    
    else:
        print("无效选择")
    
    importer.close()
    
    print("\n" + "=" * 70)
    print("导入完成!")
    print("=" * 70)
    print(f"\n数据库位置：data/stock_data.db")


if __name__ == "__main__":
    main()
