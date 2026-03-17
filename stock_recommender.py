"""
股票推荐引擎 (Stock Recommender)

基于多策略信号和技术指标，为用户推荐值得关注的股票
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from strategies import (
    TrendFollowingStrategy,
    MeanReversionStrategy,
    MomentumStrategy,
    BollingerBandsStrategy,
    MACDCrossStrategy,
    RSIStrategy,
    StrategyBacktester
)


class StockSignal:
    """股票信号评分"""
    
    def __init__(self, symbol: str, name: str = ''):
        self.symbol = symbol
        self.name = name
        self.price = 0.0
        self.change_pct = 0.0
        self.volume = 0
        self.signals: Dict[str, int] = {}  # 策略名 -> 信号 (1=买入，-1=卖出，0=持有)
        self.score = 0.0  # 综合评分 (-10 到 10)
        self.recommendation = 'HOLD'  # STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL
        self.reasons: List[str] = []  # 推荐原因
        self.risk_level = 'MEDIUM'  # LOW, MEDIUM, HIGH
        self.target_price: Optional[float] = None
        self.stop_loss: Optional[float] = None
    
    def add_signal(self, strategy_name: str, signal: int):
        """添加策略信号"""
        self.signals[strategy_name] = signal
    
    def calculate_score(self):
        """计算综合评分"""
        if not self.signals:
            self.score = 0
            return
        
        # 各策略权重
        weights = {
            'trend_following': 1.5,    # 趋势跟踪权重较高
            'momentum': 1.3,           # 动量策略
            'macd_cross': 1.2,         # MACD
            'bollinger_bands': 1.0,    # 布林带
            'mean_reversion': 1.0,     # 均值回归
            'rsi': 1.0                 # RSI
        }
        
        total_weight = 0
        weighted_sum = 0
        
        for strategy, signal in self.signals.items():
            weight = weights.get(strategy, 1.0)
            weighted_sum += signal * weight
            total_weight += weight
        
        # 归一化到 -10 到 10
        if total_weight > 0:
            self.score = (weighted_sum / total_weight) * 10
        else:
            self.score = 0
    
    def determine_recommendation(self):
        """确定推荐等级"""
        if self.score >= 7:
            self.recommendation = 'STRONG_BUY'
        elif self.score >= 4:
            self.recommendation = 'BUY'
        elif self.score >= -4:
            self.recommendation = 'HOLD'
        elif self.score >= -7:
            self.recommendation = 'SELL'
        else:
            self.recommendation = 'STRONG_SELL'
    
    def add_reason(self, reason: str):
        """添加推荐原因"""
        self.reasons.append(reason)
    
    def set_price_targets(self, current_price: float, atr: float = None):
        """设置目标价和止损价"""
        self.price = current_price
        
        if self.recommendation in ['STRONG_BUY', 'BUY']:
            # 目标价：上方阻力位（简单使用 ATR 或百分比）
            if atr:
                self.target_price = current_price + 2 * atr
                self.stop_loss = current_price - 1.5 * atr
            else:
                self.target_price = current_price * 1.10  # 10% 上涨空间
                self.stop_loss = current_price * 0.95     # 5% 止损
        elif self.recommendation in ['STRONG_SELL', 'SELL']:
            if atr:
                self.target_price = current_price - 2 * atr
                self.stop_loss = current_price + 1.5 * atr
            else:
                self.target_price = current_price * 0.90  # 10% 下跌空间
                self.stop_loss = current_price * 1.05     # 5% 止损
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'symbol': self.symbol,
            'name': self.name,
            'price': self.price,
            'change_pct': self.change_pct,
            'score': round(self.score, 2),
            'recommendation': self.recommendation,
            'reasons': self.reasons,
            'target_price': self.target_price,
            'stop_loss': self.stop_loss,
            'risk_level': self.risk_level,
            'signals': self.signals
        }
    
    def __repr__(self):
        return f"StockSignal({self.symbol}, {self.recommendation}, Score: {self.score:.2f})"


class StockRecommender:
    """
    股票推荐引擎
    
    基于多策略信号综合评分，推荐值得关注的股票
    """
    
    def __init__(self):
        self.strategies = {
            'trend_following': TrendFollowingStrategy(short_period=5, long_period=20),
            'mean_reversion': MeanReversionStrategy(ma_period=20, std_threshold=2.0),
            'momentum': MomentumStrategy(lookback_period=20, signal_threshold=5.0),
            'bollinger_bands': BollingerBandsStrategy(period=20, std_dev=2.0),
            'macd_cross': MACDCrossStrategy(fast_period=12, slow_period=26, signal_period=9),
            'rsi': RSIStrategy(period=14, oversold=30, overbought=70)
        }
        self.stock_signals: List[StockSignal] = []
    
    def analyze_stock(self, data: pd.DataFrame, symbol: str = '', name: str = '') -> StockSignal:
        """
        分析单只股票
        
        Parameters
        ----------
        data : pd.DataFrame
            股票历史数据
        symbol : str
            股票代码
        name : str
            股票名称
        
        Returns
        -------
        StockSignal
            股票信号对象
        """
        signal = StockSignal(symbol, name)
        
        if data is None or len(data) < 30:
            signal.add_reason('数据不足')
            return signal
        
        # 获取最新价格信息
        signal.price = data['close'].iloc[-1]
        signal.change_pct = data['close'].pct_change().iloc[-1] * 100 if len(data) > 1 else 0
        signal.volume = data['vol'].iloc[-1] if 'vol' in data.columns else 0
        
        # 计算 ATR（平均真实波幅）
        atr = self._calculate_atr(data)
        
        # 运行所有策略
        for strategy_name, strategy in self.strategies.items():
            try:
                result_data = strategy.analyze(data.copy())
                latest_signal = strategy.signals[-1] if strategy.signals else 0
                signal.add_signal(strategy_name, latest_signal.value)
                
                # 添加策略原因
                self._add_strategy_reason(signal, strategy_name, latest_signal.value)
            except Exception as e:
                signal.add_signal(strategy_name, 0)
        
        # 计算综合评分
        signal.calculate_score()
        signal.determine_recommendation()
        
        # 设置目标价和止损
        signal.set_price_targets(signal.price, atr)
        
        # 评估风险等级
        self._evaluate_risk(signal, data)
        
        return signal
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> float:
        """计算平均真实波幅 (ATR)"""
        if len(data) < period + 1:
            return data['close'].std() if len(data) > 1 else data['close'].iloc[-1] * 0.02
        
        high = data['high']
        low = data['low']
        close = data['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean().iloc[-1]
        
        return atr
    
    def _add_strategy_reason(self, signal: StockSignal, strategy_name: str, sig_value: int):
        """添加策略原因"""
        reasons = {
            'trend_following': {
                1: '均线金叉，趋势向好',
                2: '强势金叉，趋势明显',
                -1: '均线死叉，趋势转弱',
                -2: '强势死叉，趋势向下'
            },
            'mean_reversion': {
                1: '价格超卖，可能反弹',
                2: '严重超卖，反弹概率大',
                -1: '价格超买，可能回调',
                -2: '严重超买，回调概率大'
            },
            'momentum': {
                1: '动量强劲，成交量配合',
                2: '动量非常强劲',
                -1: '动量转弱，成交量放大',
                -2: '动量非常疲弱'
            },
            'bollinger_bands': {
                1: '触及布林带下轨',
                2: '跌破下轨，可能反弹',
                -1: '触及布林带上轨',
                -2: '突破上轨，可能回调'
            },
            'macd_cross': {
                1: 'MACD 金叉信号',
                2: 'MACD 强势金叉',
                -1: 'MACD 死叉信号',
                -2: 'MACD 强势死叉'
            },
            'rsi': {
                1: 'RSI 超卖区域',
                2: 'RSI 严重超卖',
                -1: 'RSI 超买区域',
                -2: 'RSI 严重超买'
            }
        }
        
        if strategy_name in reasons and sig_value in reasons[strategy_name]:
            signal.add_reason(f"{reasons[strategy_name][sig_value]} ({strategy_name})")
    
    def _evaluate_risk(self, signal: StockSignal, data: pd.DataFrame):
        """评估风险等级"""
        if len(data) < 20:
            signal.risk_level = 'HIGH'
            return
        
        # 计算波动率
        returns = data['close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)  # 年化波动率
        
        # 计算最大回撤
        cummax = data['close'].cummax()
        drawdown = (data['close'] - cummax) / cummax
        max_drawdown = abs(drawdown.min()) * 100
        
        # 评估风险
        if volatility < 0.3 and max_drawdown < 15:
            signal.risk_level = 'LOW'
        elif volatility < 0.5 and max_drawdown < 25:
            signal.risk_level = 'MEDIUM'
        else:
            signal.risk_level = 'HIGH'
        
        if signal.risk_level == 'HIGH':
            signal.add_reason(f'高风险：波动率{volatility*100:.1f}%, 最大回撤{max_drawdown:.1f}%')
    
    def analyze_multiple_stocks(self, stock_data_dict: Dict[str, pd.DataFrame]) -> List[StockSignal]:
        """
        分析多只股票
        
        Parameters
        ----------
        stock_data_dict : Dict[str, pd.DataFrame]
            股票代码 -> 数据的字典
        
        Returns
        -------
        List[StockSignal]
            股票信号列表
        """
        self.stock_signals = []
        
        for symbol, data in stock_data_dict.items():
            signal = self.analyze_stock(data, symbol)
            self.stock_signals.append(signal)
        
        # 按评分排序
        self.stock_signals.sort(key=lambda x: x.score, reverse=True)
        
        return self.stock_signals
    
    def get_recommendations(self, min_score: float = 4.0, 
                           recommendation: str = None,
                           top_n: int = None) -> List[StockSignal]:
        """
        获取推荐股票
        
        Parameters
        ----------
        min_score : float
            最低评分阈值
        recommendation : str
            推荐等级过滤 (STRONG_BUY, BUY, etc.)
        top_n : int
            返回前 N 只股票
        
        Returns
        -------
        List[StockSignal]
            符合条件的股票信号
        """
        result = self.stock_signals
        
        # 过滤最低评分
        result = [s for s in result if s.score >= min_score]
        
        # 过滤推荐等级
        if recommendation:
            result = [s for s in result if s.recommendation == recommendation]
        
        # 返回前 N 只
        if top_n:
            result = result[:top_n]
        
        return result
    
    def get_buy_recommendations(self, top_n: int = 5) -> List[StockSignal]:
        """获取买入推荐的股票"""
        buys = [s for s in self.stock_signals if s.recommendation in ['STRONG_BUY', 'BUY']]
        return buys[:top_n]
    
    def print_recommendations(self, top_n: int = 10):
        """打印推荐列表"""
        print("\n" + "=" * 80)
        print("股票推荐列表")
        print("=" * 80)
        
        if not self.stock_signals:
            print("暂无分析数据")
            return
        
        # 显示前 N 只股票
        for i, signal in enumerate(self.stock_signals[:top_n], 1):
            print(f"\n{i}. {signal.symbol} {signal.name}")
            print(f"   当前价格：{signal.price:.2f}")
            print(f"   综合评分：{signal.score:.2f}")
            print(f"   推荐等级：{signal.recommendation}")
            print(f"   风险等级：{signal.risk_level}")
            
            if signal.target_price:
                print(f"   目标价格：{signal.target_price:.2f}")
            if signal.stop_loss:
                print(f"   止损价格：{signal.stop_loss:.2f}")
            
            if signal.reasons:
                print(f"   推荐原因:")
                for reason in signal.reasons[:5]:  # 最多显示 5 个原因
                    print(f"     - {reason}")
        
        print("\n" + "=" * 80)
    
    def generate_report(self, save_path: str = None) -> str:
        """
        生成推荐报告
        
        Parameters
        ----------
        save_path : str
            报告保存路径
        
        Returns
        -------
        str
            报告内容
        """
        report = f"""
# 股票推荐报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 推荐摘要

| 排名 | 代码 | 名称 | 价格 | 评分 | 推荐 | 风险 |
|------|------|------|------|------|------|------|
"""
        for i, signal in enumerate(self.stock_signals[:20], 1):
            report += f"| {i} | {signal.symbol} | {signal.name} | {signal.price:.2f} | {signal.score:.2f} | {signal.recommendation} | {signal.risk_level} |\n"
        
        report += """
## 重点推荐股票

"""
        # 添加重点推荐（评分最高的 3 只）
        for signal in self.stock_signals[:3]:
            report += f"""
### {signal.symbol} - {signal.recommendation}

- **当前价格**: {signal.price:.2f}
- **综合评分**: {signal.score:.2f}
- **目标价格**: {signal.target_price:.2f if signal.target_price else 'N/A'}
- **止损价格**: {signal.stop_loss:.2f if signal.stop_loss else 'N/A'}
- **风险等级**: {signal.risk_level}

**推荐原因**:
"""
            for reason in signal.reasons:
                report += f"- {reason}\n"
        
        report += """
## 风险提示

1. 本报告仅供参考，不构成投资建议
2. 股市有风险，投资需谨慎
3. 请结合个人风险承受能力做出决策
4. 历史表现不代表未来收益

---
*报告由股票推荐引擎自动生成*
"""
        
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"报告已保存到：{save_path}")
        
        return report


def create_sample_data() -> Dict[str, pd.DataFrame]:
    """创建示例数据用于测试"""
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='B')
    
    stocks = {
        '000001': '平安银行',
        '000002': '万科 A',
        '600000': '浦发银行',
        '600036': '招商银行',
        '000858': '五粮液'
    }
    
    data_dict = {}
    for symbol in stocks.keys():
        # 生成不同的股价走势
        initial_price = np.random.uniform(20, 100)
        mu = np.random.uniform(-0.0002, 0.0008)
        sigma = np.random.uniform(0.015, 0.03)
        
        returns = np.random.normal(mu, sigma, len(dates))
        prices = initial_price * np.cumprod(1 + returns)
        prices = np.clip(prices, 10, 200)
        
        data = pd.DataFrame({
            'open': prices * (1 + np.random.randn(len(prices)) * 0.005),
            'high': np.maximum(prices * (1 + np.abs(np.random.randn(len(prices)) * 0.01)), prices),
            'low': np.minimum(prices * (1 - np.abs(np.random.randn(len(prices)) * 0.01)), prices),
            'close': prices,
            'vol': np.random.randint(2000000, 15000000, len(prices))
        }, index=dates)
        
        data['high'] = np.maximum(data['high'], data['close'])
        data['low'] = np.minimum(data['low'], data['close'])
        
        data_dict[symbol] = data
    
    return data_dict


if __name__ == "__main__":
    # 测试推荐引擎
    print("测试股票推荐引擎...")
    
    recommender = StockRecommender()
    stock_data = create_sample_data()
    
    # 分析所有股票
    recommender.analyze_multiple_stocks(stock_data)
    
    # 打印推荐
    recommender.print_recommendations(top_n=5)
    
    # 获取买入推荐
    print("\n" + "=" * 80)
    print("买入推荐股票")
    print("=" * 80)
    
    buy_recs = recommender.get_buy_recommendations(top_n=3)
    for signal in buy_recs:
        print(f"{signal.symbol}: {signal.recommendation} (评分：{signal.score:.2f})")
