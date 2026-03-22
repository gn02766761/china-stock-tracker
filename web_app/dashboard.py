"""
股票推荐 Web 仪表盘 - Streamlit 应用

提供交互式股票分析、推荐和可视化界面
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock_recommender import StockRecommender
from strategy_analyzer import StockStrategyAnalyzer
from stock_screener import StockScreener
from utils.data_collector import StockDataCollector, get_default_start_end_dates
from stock_database import StockDatabase

# 页面配置
st.set_page_config(
    page_title="中国股票分析系统",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS 样式
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 1rem;
}
.metric-card {
    background-color: #f0f2f6;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
}
.buy-signal {
    color: #28a745;
    font-weight: bold;
}
.sell-signal {
    color: #dc3545;
    font-weight: bold;
}
.hold-signal {
    color: #ffc107;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """初始化会话状态"""
    if 'token' not in st.session_state:
        st.session_state.token = os.getenv('TUSHARE_TOKEN', '')
    if 'collector' not in st.session_state:
        st.session_state.collector = None
    if 'recommender' not in st.session_state:
        st.session_state.recommender = StockRecommender()
    if 'screener' not in st.session_state:
        st.session_state.screener = StockScreener()
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = StockStrategyAnalyzer()


def init_tushare():
    """初始化 Tushare"""
    if st.session_state.token:
        try:
            import tushare as ts
            ts.set_token(st.session_state.token)
            st.session_state.collector = StockDataCollector(token=st.session_state.token)
            return True
        except Exception as e:
            st.error(f"Tushare 初始化失败：{str(e)}")
            return False
    return False


def get_stock_data(symbol, start_date, end_date):
    """获取股票数据"""
    if st.session_state.collector:
        return st.session_state.collector.get_stock_data(symbol, start_date, end_date)
    return None


def plot_candlestick_chart(data, symbol):
    """绘制 K 线图"""
    fig = go.Figure()
    
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['open'],
        high=data['high'],
        low=data['low'],
        close=data['close'],
        name='K 线',
        increasing_line_color='#FF6B6B',
        decreasing_line_color='#4ECDC4'
    ))
    
    # 添加均线
    if 'ma5' in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data['ma5'], name='MA5', line=dict(color='#FFA500', width=1)))
    if 'ma10' in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data['ma10'], name='MA10', line=dict(color='#00BFFF', width=1)))
    if 'ma20' in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data['ma20'], name='MA20', line=dict(color='#9370DB', width=1)))
    
    fig.update_layout(
        title=f"{symbol} K 线图",
        yaxis_title="价格 (元)",
        xaxis_title="日期",
        template="plotly_dark",
        height=600,
        showlegend=True,
        xaxis_rangeslider_visible=False
    )
    
    return fig


def plot_strategy_signals(signals):
    """绘制策略信号雷达图"""
    categories = list(signals.keys())
    values = list(signals.values())
    
    # 将信号转换为 -2 到 2 的分数
    signal_map = {2: 2, 1: 1, 0: 0, -1: -1, -2: -2}
    values = [signal_map.get(v, 0) for v in values]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='策略信号',
        line_color='#1f77b4'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[-2, 2]
            )),
        showlegend=False,
        title="策略信号雷达图",
        height=400
    )
    
    return fig


def plot_recommendation_distribution(recommendations):
    """绘制推荐等级分布"""
    if recommendations.empty:
        return None
    
    dist = recommendations['recommendation'].value_counts()
    
    fig = px.bar(
        x=dist.index,
        y=dist.values,
        labels={'x': '推荐等级', 'y': '股票数量'},
        title='股票推荐等级分布',
        color=dist.index,
        color_discrete_map={
            'STRONG_BUY': '#28a745',
            'BUY': '#5cb85c',
            'HOLD': '#ffc107',
            'SELL': '#f0ad4e',
            'STRONG_SELL': '#dc3545'
        }
    )
    
    fig.update_layout(height=400, showlegend=False)
    return fig


def main():
    """主函数"""
    init_session_state()
    
    # 侧边栏
    with st.sidebar:
        st.markdown("## ⚙️ 设置")
        
        # Tushare Token 配置
        token_input = st.text_input(
            "Tushare Token",
            value=st.session_state.token,
            type="password",
            help="访问 https://tushare.pro/ 获取免费 token"
        )
        
        if token_input != st.session_state.token:
            st.session_state.token = token_input
            if token_input:
                os.environ['TUSHARE_TOKEN'] = token_input
                if init_tushare():
                    st.success("✓ Tushare 连接成功")
                else:
                    st.warning("⚠ Tushare 连接失败")
            else:
                st.session_state.collector = None
        
        st.markdown("---")
        
        # 主菜单
        st.markdown("## 📑 菜单")
        menu = st.radio(
            "选择功能",
            ["🏠 首页", "🔍 个股分析", "📊 股票推荐", "🎯 股票筛选", "📈 策略回测", "💼 投资组合"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### 📊 市场状态")
        st.info("ℹ️ 使用示例数据演示模式")
    
    # 主内容区
    if menu == "🏠 首页":
        render_home_page()
    elif menu == "🔍 个股分析":
        render_single_stock_analysis()
    elif menu == "📊 股票推荐":
        render_stock_recommendations()
    elif menu == "🎯 股票筛选":
        render_stock_screener()
    elif menu == "📈 策略回测":
        render_strategy_backtest()
    elif menu == "💼 投资组合":
        render_portfolio()


def render_home_page():
    """渲染首页"""
    st.markdown('<p class="main-header">📈 中国股票分析推荐系统</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # 核心功能卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🔍</h3>
            <h4>个股分析</h4>
            <p>6 种经典策略综合评分</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📊</h3>
            <h4>股票推荐</h4>
            <p>智能评分推荐系统</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🎯</h3>
            <h4>股票筛选</h4>
            <p>多维度条件筛选</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>💼</h3>
            <h4>投资组合</h3>
            <p>持仓跟踪与管理</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 快速操作
    st.markdown("### 🚀 快速开始")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📋 使用流程")
        st.markdown("""
        1. **配置 Token** - 在侧边栏输入 Tushare token
        2. **个股分析** - 输入股票代码进行详细分析
        3. **股票推荐** - 查看系统推荐的股票池
        4. **股票筛选** - 根据条件筛选目标股票
        5. **投资组合** - 管理持仓和跟踪盈亏
        """)
    
    with col2:
        st.markdown("#### 📊 策略说明")
        st.markdown("""
        | 策略 | 适用市场 | 权重 |
        |------|----------|------|
        | 趋势跟踪 | 趋势市 | 1.5 |
        | 动量策略 | 趋势市 | 1.3 |
        | MACD 交叉 | 趋势市 | 1.2 |
        | 布林带 | 震荡市 | 1.0 |
        | 均值回归 | 震荡市 | 1.0 |
        | RSI | 震荡市 | 1.0 |
        """)
    
    # 最新推荐
    st.markdown("---")
    st.markdown("### ⭐ 最新推荐股票")
    
    try:
        db = StockDatabase()
        latest_recs = db.get_latest_recommendations(limit=5)
        
        if not latest_recs.empty:
            # 美化显示
            display_df = latest_recs[['symbol', 'name', 'signal_score', 'recommendation', 'trade_date']].copy()
            display_df.columns = ['股票代码', '股票名称', '综合评分', '推荐等级', '日期']
            
            # 添加颜色
            def color_recommendation(val):
                colors = {
                    'STRONG_BUY': 'background-color: #28a745; color: white',
                    'BUY': 'background-color: #5cb85c; color: white',
                    'HOLD': 'background-color: #ffc107; color: black',
                    'SELL': 'background-color: #f0ad4e; color: white',
                    'STRONG_SELL': 'background-color: #dc3545; color: white'
                }
                return colors.get(val, '')
            
            st.dataframe(
                display_df.style.applymap(color_recommendation, subset=['推荐等级']),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("暂无推荐数据，请先运行股票推荐分析")
    except Exception as e:
        st.info("暂无推荐数据，请先运行股票推荐分析")


def render_single_stock_analysis():
    """渲染个股分析页面"""
    st.markdown("## 🔍 个股分析")
    
    # 输入股票代码
    col1, col2 = st.columns([2, 1])
    
    with col1:
        symbol = st.text_input("股票代码", value="000001", max_chars=6)
    
    with col2:
        st.markdown("### 示例股票")
        st.markdown("- 000001 平安银行")
        st.markdown("- 600519 贵州茅台")
        st.markdown("- 300750 宁德时代")
    
    if st.button("开始分析", type="primary"):
        with st.spinner(f"正在分析 {symbol}..."):
            # 获取数据
            start_date, end_date = get_default_start_end_dates()
            
            if st.session_state.collector:
                data = get_stock_data(symbol, start_date, end_date)
            else:
                # 使用示例数据
                st.info("ℹ️ 使用示例数据进行演示")
                data = generate_sample_data(symbol)
            
            if data is not None and not data.empty:
                # 计算技术指标
                if st.session_state.collector:
                    data = st.session_state.collector.calculate_technical_indicators(data)
                
                # 显示基本信息
                stock_name = symbol
                st.markdown(f"### {symbol} - {stock_name}")
                
                # K 线图
                st.plotly_chart(plot_candlestick_chart(data, symbol), use_container_width=True)
                
                # 策略分析
                st.markdown("### 📊 策略信号分析")
                
                result = st.session_state.analyzer.analyze_single_strategy(
                    'trend_following', data, verbose=False
                )
                
                if result:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("总收益", f"{result.get('total_return_pct', 0):.2f}%")
                    with col2:
                        st.metric("胜率", f"{result.get('win_rate', 0):.2f}%")
                    with col3:
                        st.metric("夏普比率", f"{result.get('sharpe_ratio', 0):.2f}")
                    with col4:
                        st.metric("最大回撤", f"{result.get('max_drawdown', 0):.2f}%")
                
                # 推荐分析
                st.markdown("### 🎯 推荐分析")
                
                signal = st.session_state.recommender.analyze_stock(data, symbol, stock_name)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # 推荐等级
                    rec_colors = {
                        'STRONG_BUY': '🟢 强烈买入',
                        'BUY': '🟢 买入',
                        'HOLD': '🟡 持有',
                        'SELL': '🔴 卖出',
                        'STRONG_SELL': '🔴 强烈卖出'
                    }
                    
                    st.markdown(f"**综合评分**: {signal.score:.2f}")
                    st.markdown(f"**推荐等级**: {rec_colors.get(signal.recommendation, signal.recommendation)}")
                    st.markdown(f"**风险等级**: {signal.risk_level}")
                    
                    if signal.target_price:
                        st.markdown(f"**目标价**: {signal.target_price:.2f}")
                    if signal.stop_loss:
                        st.markdown(f"**止损价**: {signal.stop_loss:.2f}")
                    
                    # 推荐原因
                    if signal.reasons:
                        st.markdown("**推荐原因**:")
                        for reason in signal.reasons[:5]:
                            st.markdown(f"- {reason}")
                
                with col2:
                    # 策略信号雷达图
                    if signal.signals:
                        fig = plot_strategy_signals(signal.signals)
                        st.plotly_chart(fig, use_container_width=True)
                
                # 技术指标
                st.markdown("### 📈 技术指标")
                
                tech_cols = ['close', 'ma5', 'ma10', 'ma20', 'rsi', 'macd', 'kdj_k', 'kdj_d']
                available_cols = [c for c in tech_cols if c in data.columns]
                
                if available_cols:
                    st.dataframe(data[available_cols].tail(10), use_container_width=True)
            else:
                st.error(f"无法获取 {symbol} 的数据，请检查股票代码是否正确")


def generate_sample_data(symbol):
    """生成示例数据"""
    dates = pd.date_range(end=datetime.now(), periods=260, freq='D')
    np.random.seed(hash(symbol) % 2**32 if symbol else 42)
    
    # 生成随机价格
    base_price = np.random.uniform(10, 100)
    returns = np.random.normal(0.0005, 0.02, 260)
    close = base_price * np.cumprod(1 + returns)
    
    data = pd.DataFrame({
        'trade_date': dates,
        'close': close,
        'open': close * (1 + np.random.uniform(-0.01, 0.01, 260)),
        'high': close * (1 + np.random.uniform(0, 0.03, 260)),
        'low': close * (1 - np.random.uniform(0, 0.03, 260)),
        'vol': np.random.uniform(1000000, 10000000, 260)
    })
    data.set_index('trade_date', inplace=True)
    
    return data


def render_stock_recommendations():
    """渲染股票推荐页面"""
    st.markdown("## 📊 股票推荐")
    
    # 获取推荐数据
    try:
        db = StockDatabase()
        recommendations = db.get_latest_recommendations(limit=50)
        
        if not recommendations.empty:
            # 推荐等级分布
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("### 推荐列表")
                
                # 美化显示
                display_df = recommendations[['symbol', 'name', 'signal_score', 'recommendation', 'trade_date']].copy()
                display_df.columns = ['股票代码', '股票名称', '综合评分', '推荐等级', '日期']
                
                # 添加颜色
                def color_score(val):
                    if val >= 7:
                        return 'color: #28a745; font-weight: bold'
                    elif val >= 4:
                        return 'color: #5cb85c'
                    elif val <= -7:
                        return 'color: #dc3545; font-weight: bold'
                    elif val <= -4:
                        return 'color: #f0ad4e'
                    return ''
                
                st.dataframe(
                    display_df.style.applymap(color_score, subset=['综合评分']),
                    use_container_width=True,
                    hide_index=True
                )
            
            with col2:
                fig = plot_recommendation_distribution(recommendations)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            
            # 强烈买入股票详情
            strong_buy = recommendations[recommendations['recommendation'] == 'STRONG_BUY']
            
            if not strong_buy.empty:
                st.markdown("### ⭐ 强烈买入股票")
                
                for _, row in strong_buy.head(5).iterrows():
                    with st.expander(f"{row['symbol']} - {row['name']} (评分：{row['signal_score']:.2f})"):
                        st.markdown(f"- **综合评分**: {row['signal_score']:.2f}")
                        st.markdown(f"- **推荐等级**: STRONG_BUY")
                        if 'target_price' in row and pd.notna(row['target_price']):
                            st.markdown(f"- **目标价**: {row['target_price']:.2f}")
                        if 'stop_loss' in row and pd.notna(row['stop_loss']):
                            st.markdown(f"- **止损价**: {row['stop_loss']:.2f}")
        else:
            st.info("暂无推荐数据，请先运行股票推荐分析")
            st.markdown("### 如何获取推荐？")
            st.markdown("""
            1. 运行命令行工具：`python run_stock_recommender.py`
            2. 选择"分析全部股票"选项
            3. 等待分析完成后刷新此页面
            """)
    except Exception as e:
        st.info("暂无推荐数据，请先运行股票推荐分析")


def render_stock_screener():
    """渲染股票筛选页面"""
    st.markdown("## 🎯 股票筛选")
    
    # 筛选条件
    st.markdown("### 筛选条件")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        screen_type = st.selectbox(
            "筛选类型",
            ["按推荐等级", "按技术指标", "均线金叉", "RSI 超卖", "成交量突破"]
        )
    
    with col2:
        if screen_type == "按推荐等级":
            rec_level = st.selectbox(
                "推荐等级",
                ["STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"]
            )
        elif screen_type == "按技术指标":
            tech_indicator = st.selectbox(
                "技术指标",
                ["MA 金叉", "MACD 金叉", "布林带突破"]
            )
    
    with col3:
        limit = st.number_input("显示数量", min_value=5, max_value=100, value=20)
    
    if st.button("开始筛选", type="primary"):
        try:
            screener = StockScreener()
            
            if screen_type == "按推荐等级":
                results = screener.screen_by_recommendation(
                    recommendation=[rec_level],
                    limit=limit
                )
            elif screen_type == "按技术指标":
                if tech_indicator == "MA 金叉":
                    results = screener.screen_by_ma_cross(limit=limit)
                elif tech_indicator == "MACD 金叉":
                    results = screener.screen_by_macd_cross(limit=limit)
                else:
                    results = screener.screen_by_bollinger_breakout(limit=limit)
            elif screen_type == "RSI 超卖":
                results = screener.screen_by_rsi_oversold(limit=limit)
            elif screen_type == "成交量突破":
                results = screener.screen_by_volume_breakout(limit=limit)
            else:
                results = None
            
            if results is not None and not results.empty:
                st.success(f"找到 {len(results)} 只符合条件的股票")
                st.dataframe(results, use_container_width=True, hide_index=True)
            else:
                st.info("未找到符合条件的股票")
        except Exception as e:
            st.error(f"筛选失败：{str(e)}")


def render_strategy_backtest():
    """渲染策略回测页面"""
    st.markdown("## 📈 策略回测")
    
    st.info("ℹ️ 此功能需要配置 Tushare token 并获取股票数据")
    
    # 策略选择
    strategies = {
        "趋势跟踪": "trend_following",
        "均值回归": "mean_reversion",
        "动量策略": "momentum",
        "布林带": "bollinger_bands",
        "MACD 交叉": "macd_cross",
        "RSI": "rsi"
    }
    
    selected_strategy = st.selectbox("选择策略", list(strategies.keys()))
    
    if st.button("运行回测"):
        st.markdown("### 回测结果")
        
        # 示例回测结果
        st.markdown("""
        | 策略 | 总收益 (%) | 胜率 (%) | 夏普比率 | 最大回撤 (%) |
        |------|-----------|---------|---------|------------|
        | 趋势跟踪 | 15.47 | 57.14 | 0.77 | 13.31 |
        | 均值回归 | 13.35 | 80.00 | 0.68 | 16.47 |
        | 动量策略 | 3.26 | 60.00 | 0.24 | 11.83 |
        | 布林带 | 17.04 | 80.00 | 0.87 | 16.47 |
        | MACD 交叉 | 8.95 | 50.00 | 0.47 | 17.39 |
        | RSI | 6.85 | 75.00 | 0.42 | 17.89 |
        """)
        
        # 回测图表
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=list(range(260)),
            y=np.random.randn(260).cumsum() + 100,
            name='策略收益',
            line=dict(color='#1f77b4', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=list(range(260)),
            y=np.random.randn(260).cumsum() * 0.5 + 100,
            name='基准收益',
            line=dict(color='#d62728', width=2, dash='dash')
        ))
        
        fig.update_layout(
            title="策略收益曲线",
            xaxis_title="交易日",
            yaxis_title="累计收益 (%)",
            template="plotly_dark",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)


def render_portfolio():
    """渲染投资组合页面"""
    st.markdown("## 💼 投资组合")
    
    st.info("ℹ️ 此功能需要配置 Tushare token 并获取实时价格")
    
    # 示例组合
    st.markdown("### 持仓概览")
    
    portfolio_data = pd.DataFrame({
        '股票代码': ['000001', '600519', '300750'],
        '股票名称': ['平安银行', '贵州茅台', '宁德时代'],
        '持仓数量': [1000, 200, 500],
        '成本价': [48.50, 1450.00, 280.00],
        '当前价': [52.30, 1580.00, 310.00],
        '持仓市值': [52300, 316000, 155000],
        '盈亏': [3800, 26000, 15000],
        '盈亏率': [7.84, 8.97, 10.71]
    })
    
    # 计算总计
    total_cost = (portfolio_data['持仓数量'] * portfolio_data['成本价']).sum()
    total_value = portfolio_data['持仓市值'].sum()
    total_pnl = portfolio_data['盈亏'].sum()
    total_pnl_pct = (total_pnl / total_cost) * 100
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("持仓市值", f"¥{total_value:,.2f}")
    
    with col2:
        st.metric("总盈亏", f"¥{total_pnl:,.2f}", f"{total_pnl_pct:.2f}%")
    
    with col3:
        st.metric("持仓数量", f"{len(portfolio_data)} 只")
    
    with col4:
        st.metric("可用资金", "¥499,850.00")
    
    # 持仓详情
    st.markdown("### 持仓详情")
    
    def color_pnl(val):
        if val > 0:
            return 'color: #28a745'
        elif val < 0:
            return 'color: #dc3545'
        return ''
    
    st.dataframe(
        portfolio_data.style.applymap(color_pnl, subset=['盈亏', '盈亏率']),
        use_container_width=True,
        hide_index=True
    )
    
    # 持仓分布图
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            values=portfolio_data['持仓市值'],
            names=portfolio_data['股票名称'],
            title='持仓市值分布'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            portfolio_data,
            x='股票名称',
            y='盈亏率',
            title='个股盈亏率',
            color='盈亏率',
            color_continuous_scale=['#dc3545', '#ffc107', '#28a745']
        )
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
