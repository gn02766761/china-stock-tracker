"""
Streamlit Web 仪表板 - 主页面
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import config
from database.database_manager import DatabaseManager
from app.data_service import StockDataService
from app.portfolio_manager import PortfolioManager
from app.alert_engine import AlertEngine
from notifications.notifier import NotificationService


# 页面配置
st.set_page_config(
    page_title="股票智能预警与投资组合管理系统",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化服务
@st.cache_resource
def init_services():
    """初始化服务"""
    db = DatabaseManager(config.DATABASE_URL)
    data_service = StockDataService()
    portfolio_manager = PortfolioManager(db, data_service)
    alert_engine = AlertEngine(db, data_service)
    notifier = NotificationService()
    return db, data_service, portfolio_manager, alert_engine, notifier


db, data_service, portfolio_manager, alert_engine, notifier = init_services()


def render_sidebar():
    """渲染侧边栏"""
    st.sidebar.title("🎯 功能菜单")
    
    menu_options = {
        "📊 投资组合总览": "portfolio",
        "🔔 预警管理": "alerts",
        "📈 股票分析": "analysis",
        "⚙️ 设置": "settings"
    }
    
    selection = st.sidebar.radio("选择功能", list(menu_options.keys()))
    return menu_options[selection]


def render_portfolio_page():
    """渲染投资组合页面"""
    st.title("📊 投资组合总览")
    
    # 获取投资组合摘要
    summary = portfolio_manager.get_portfolio_summary()
    
    # 顶部指标卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="总市值 (元)",
            value=f"{summary['total_market_value']:.2f}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="总投入 (元)",
            value=f"{summary['total_invested']:.2f}",
            delta=None
        )
    
    with col3:
        st.metric(
            label="总盈亏 (元)",
            value=f"{summary['total_profit_loss']:.2f}",
            delta=f"{summary['profit_loss_rate']:.2f}%",
            delta_color="normal" if summary['total_profit_loss'] >= 0 else "inverse"
        )
    
    with col4:
        st.metric(
            label="持仓数量",
            value=summary['total_holdings'],
            delta=None
        )
    
    st.divider()
    
    # 图表区域
    if summary['total_holdings'] > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # 持仓分布饼图
            chart_data = portfolio_manager.get_portfolio_chart_data()
            if chart_data and 'pie' in chart_data:
                fig = px.pie(
                    values=chart_data['pie']['values'],
                    names=chart_data['pie']['labels'],
                    title='📦 持仓分布',
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 盈亏柱状图
            if chart_data and 'bar' in chart_data:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=chart_data['bar']['labels'],
                    y=chart_data['bar']['profit_loss'],
                    marker_color=chart_data['bar']['colors'],
                    name='盈亏'
                ))
                fig.update_layout(
                    title='💰 持仓盈亏',
                    xaxis_title='股票代码',
                    yaxis_title='盈亏 (元)',
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # 持仓明细表格
        st.subheader("📋 持仓明细")
        
        if summary['positions']:
            df = pd.DataFrame(summary['positions'])
            
            # 格式化显示
            display_df = df[['stock_code', 'stock_name', 'shares', 'avg_cost', 
                            'current_price', 'profit_loss', 'profit_loss_rate']].copy()
            display_df.columns = ['股票代码', '股票名称', '持仓数量', '平均成本', 
                                 '当前价格', '盈亏金额', '盈亏率']
            
            # 格式化数值列
            display_df['平均成本'] = display_df['平均成本'].apply(lambda x: f"{x:.2f}")
            display_df['当前价格'] = display_df['当前价格'].apply(lambda x: f"{x:.2f}")
            display_df['盈亏金额'] = display_df['盈亏金额'].apply(lambda x: f"{x:.2f}")
            display_df['盈亏率'] = display_df['盈亏率'].apply(lambda x: f"{x:+.2f}%")
            
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("暂无持仓数据")
    else:
        st.info("📭 暂无持仓，请添加股票持仓")


def render_alerts_page():
    """渲染预警管理页面"""
    st.title("🔔 预警管理")
    
    # 选项卡
    tab1, tab2, tab3 = st.tabs(["新增预警", "预警列表", "预警日志"])
    
    with tab1:
        st.subheader("添加价格预警")
        
        col1, col2 = st.columns(2)
        
        with col1:
            alert_stock_code = st.text_input("股票代码", placeholder="例如：000001")
            alert_stock_name = st.text_input("股票名称", placeholder="例如：平安银行")
        
        with col2:
            alert_type = st.selectbox(
                "预警类型",
                ["price_above", "price_below", "change_above", "change_below"],
                format_func=lambda x: {
                    "price_above": "价格突破",
                    "price_below": "价格跌破",
                    "change_above": "涨幅超过",
                    "change_below": "跌幅超过"
                }[x]
            )
            threshold_value = st.number_input("阈值", min_value=0.0, step=0.01)
        
        if st.button("添加预警", key="add_price_alert"):
            if alert_stock_code and threshold_value:
                db.add_price_alert(alert_stock_code, alert_stock_name, alert_type, threshold_value)
                st.success(f"已添加预警：{alert_stock_code}")
                st.rerun()
            else:
                st.error("请填写股票代码和阈值")
        
        st.divider()
        
        st.subheader("添加技术指标预警")
        
        col3, col4 = st.columns(2)
        
        with col3:
            tech_stock_code = st.text_input("股票代码 (技术指标)", placeholder="例如：000001")
            tech_stock_name = st.text_input("股票名称 (技术指标)", placeholder="例如：平安银行")
        
        with col4:
            indicator = st.selectbox(
                "技术指标",
                ["RSI", "MACD", "MA5", "MA10", "MA20", "MA60", "BB"]
            )
            condition = st.selectbox(
                "条件",
                ["cross_above", "cross_below", "above", "below", "touch_upper", "touch_lower"],
                format_func=lambda x: {
                    "cross_above": "上穿",
                    "cross_below": "下穿",
                    "above": "高于",
                    "below": "低于",
                    "touch_upper": "触及上轨",
                    "touch_lower": "触及下轨"
                }[x]
            )
            tech_threshold = st.number_input("阈值", min_value=0.0, step=0.01, key="tech_threshold")
        
        if st.button("添加技术指标预警", key="add_tech_alert"):
            if tech_stock_code and tech_threshold:
                db.add_technical_alert(tech_stock_code, tech_stock_name, indicator, condition, tech_threshold)
                st.success(f"已添加技术指标预警：{tech_stock_code} - {indicator}")
                st.rerun()
            else:
                st.error("请填写股票代码和阈值")
    
    with tab2:
        st.subheader("价格预警列表")
        
        price_alerts = db.get_active_price_alerts()
        
        if price_alerts:
            alert_data = []
            for alert in price_alerts:
                current_price = data_service.get_current_price(alert.stock_code)
                alert_data.append({
                    "ID": alert.id,
                    "股票代码": alert.stock_code,
                    "股票名称": alert.stock_name,
                    "类型": alert.alert_type,
                    "阈值": f"{alert.threshold_value:.2f}",
                    "当前价": f"{current_price:.2f}" if current_price else "N/A",
                    "状态": "✅ 激活" if alert.is_active else "❌ 停用",
                    "触发次数": alert.trigger_count
                })
            
            alert_df = pd.DataFrame(alert_data)
            st.dataframe(alert_df, use_container_width=True)
            
            # 操作区域
            st.subheader("操作")
            col1, col2 = st.columns(2)
            
            with col1:
                delete_id = st.number_input("删除预警 ID", min_value=0, step=1, key="delete_price")
                if st.button("删除价格预警"):
                    db.delete_alert(delete_id, alert_type='price')
                    st.success("已删除预警")
                    st.rerun()
            
            with col2:
                toggle_id = st.number_input("切换预警状态 ID", min_value=0, step=1, key="toggle_price")
                if st.button("切换预警状态"):
                    db.toggle_alert(toggle_id, alert_type='price')
                    st.success("已切换状态")
                    st.rerun()
        else:
            st.info("暂无价格预警")
        
        st.divider()
        
        st.subheader("技术指标预警列表")
        
        tech_alerts = db.get_active_technical_alerts()
        
        if tech_alerts:
            tech_data = []
            for alert in tech_alerts:
                tech_data.append({
                    "ID": alert.id,
                    "股票代码": alert.stock_code,
                    "股票名称": alert.stock_name,
                    "指标": alert.indicator,
                    "条件": alert.condition,
                    "阈值": f"{alert.threshold_value:.2f}",
                    "状态": "✅ 激活" if alert.is_active else "❌ 停用",
                    "触发次数": alert.trigger_count
                })
            
            tech_df = pd.DataFrame(tech_data)
            st.dataframe(tech_df, use_container_width=True)
            
            # 操作区域
            st.subheader("操作")
            col1, col2 = st.columns(2)
            
            with col1:
                delete_id = st.number_input("删除预警 ID", min_value=0, step=1, key="delete_tech")
                if st.button("删除技术指标预警"):
                    db.delete_alert(delete_id, alert_type='technical')
                    st.success("已删除预警")
                    st.rerun()
            
            with col2:
                toggle_id = st.number_input("切换预警状态 ID", min_value=0, step=1, key="toggle_tech")
                if st.button("切换预警状态"):
                    db.toggle_alert(toggle_id, alert_type='technical')
                    st.success("已切换状态")
                    st.rerun()
        else:
            st.info("暂无技术指标预警")
    
    with tab3:
        st.subheader("预警触发日志")
        
        logs = db.get_alert_logs(limit=50)
        
        if logs:
            log_data = []
            for log in logs:
                log_data.append({
                    "时间": log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    "类型": "价格" if log.alert_type == 'price' else "技术指标",
                    "股票代码": log.stock_code,
                    "股票名称": log.stock_name,
                    "触发值": f"{log.trigger_value:.2f}" if log.trigger_value else "N/A",
                    "消息": log.message[:50] + "..." if len(log.message) > 50 else log.message,
                    "已通知": "✅" if log.notified else "❌"
                })
            
            log_df = pd.DataFrame(log_data)
            st.dataframe(log_df, use_container_width=True)
        else:
            st.info("暂无预警日志")


def render_analysis_page():
    """渲染股票分析页面"""
    st.title("📈 股票分析")
    
    # 输入股票代码
    col1, col2 = st.columns([3, 1])
    
    with col1:
        stock_code = st.text_input("股票代码", placeholder="例如：000001", value="000001")
    
    with col2:
        days = st.number_input("获取天数", min_value=10, max_value=365, value=60)
    
    if st.button("分析"):
        if stock_code:
            # 获取数据
            with st.spinner("正在获取数据..."):
                df = data_service.get_stock_data(stock_code, days)
            
            if df is not None and not df.empty:
                # 计算技术指标
                df = data_service.calculate_technical_indicators(df)
                
                # 基本信息
                stock_info = data_service.get_stock_info(stock_code)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("股票名称", stock_info.get('name', 'N/A'))
                with col2:
                    st.metric("当前价格", f"{df['close'].iloc[-1]:.2f} 元")
                with col3:
                    change = ((df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2] * 100)
                    st.metric("涨跌幅", f"{change:.2f}%", 
                             delta=f"{change:.2f}%" if change > 0 else f"{change:.2f}%")
                
                st.divider()
                
                # K 线图
                st.subheader("K 线图")
                
                fig = go.Figure(data=[go.Candlestick(
                    x=df['date'] if 'date' in df.columns else df.index,
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='K 线'
                )])
                
                fig.update_layout(
                    title=f"{stock_code} K 线图",
                    yaxis_title="价格 (元)",
                    xaxis_rangeslider_visible=False,
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # 技术指标图
                st.subheader("技术指标")
                
                tab1, tab2, tab3 = st.tabs(["MA", "MACD", "RSI"])
                
                with tab1:
                    fig_ma = go.Figure()
                    fig_ma.add_trace(go.Scatter(
                        x=df['date'] if 'date' in df.columns else df.index,
                        y=df['close'],
                        name='收盘价'
                    ))
                    fig_ma.add_trace(go.Scatter(
                        x=df['date'] if 'date' in df.columns else df.index,
                        y=df['ma5'],
                        name='MA5'
                    ))
                    fig_ma.add_trace(go.Scatter(
                        x=df['date'] if 'date' in df.columns else df.index,
                        y=df['ma10'],
                        name='MA10'
                    ))
                    fig_ma.add_trace(go.Scatter(
                        x=df['date'] if 'date' in df.columns else df.index,
                        y=df['ma20'],
                        name='MA20'
                    ))
                    fig_ma.update_layout(title="移动平均线", height=400)
                    st.plotly_chart(fig_ma, use_container_width=True)
                
                with tab2:
                    fig_macd = go.Figure()
                    fig_macd.add_trace(go.Scatter(
                        x=df['date'] if 'date' in df.columns else df.index,
                        y=df['macd'],
                        name='MACD'
                    ))
                    fig_macd.add_trace(go.Scatter(
                        x=df['date'] if 'date' in df.columns else df.index,
                        y=df['macd_signal'],
                        name='Signal'
                    ))
                    fig_macd.add_trace(go.Bar(
                        x=df['date'] if 'date' in df.columns else df.index,
                        y=df['macd_hist'],
                        name='Histogram'
                    ))
                    fig_macd.update_layout(title="MACD", height=400)
                    st.plotly_chart(fig_macd, use_container_width=True)
                
                with tab3:
                    fig_rsi = go.Figure()
                    fig_rsi.add_trace(go.Scatter(
                        x=df['date'] if 'date' in df.columns else df.index,
                        y=df['rsi'],
                        name='RSI'
                    ))
                    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="超买")
                    fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="超卖")
                    fig_rsi.update_layout(title="RSI", height=400)
                    st.plotly_chart(fig_rsi, use_container_width=True)
                
            else:
                st.error(f"无法获取股票 {stock_code} 的数据")
        else:
            st.error("请输入股票代码")


def render_settings_page():
    """渲染设置页面"""
    st.title("⚙️ 设置")
    
    st.subheader("通知配置")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**邮件通知**")
        st.write(f"状态：{'✅ 已启用' if config.EMAIL_ENABLED else '❌ 未启用'}")
        st.write(f"SMTP: {config.EMAIL_HOST}:{config.EMAIL_PORT}")
        st.write(f"发件人：{config.EMAIL_USER or '未配置'}")
    
    with col2:
        st.write("**钉钉通知**")
        st.write(f"状态：{'✅ 已启用' if config.DINGTALK_ENABLED else '❌ 未启用'}")
        webhook_display = config.DINGTALK_WEBHOOK[:20] + "..." if config.DINGTALK_WEBHOOK else "未配置"
        st.write(f"Webhook: {webhook_display}")
    
    st.divider()
    
    st.subheader("系统信息")
    
    st.write(f"**数据库**: {config.DATABASE_URL}")
    st.write(f"**检查间隔**: {config.CHECK_INTERVAL} 秒")
    st.write(f"**默认监控股票**: {', '.join(config.DEFAULT_STOCKS)}")
    
    st.divider()
    
    st.subheader("手动操作")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("立即检查预警", use_container_width=True):
            with st.spinner("正在检查预警..."):
                triggered = alert_engine.run_all_checks()
                
                if triggered:
                    st.success(f"发现 {len(triggered)} 条预警!")
                    for alert in triggered:
                        st.warning(alert['message'])
                    
                    # 发送通知
                    if config.EMAIL_ENABLED or config.DINGTALK_ENABLED:
                        notifier.send_alert_notifications(triggered)
                        st.info("已发送通知")
                else:
                    st.info("暂无预警触发")
    
    with col2:
        if st.button("发送测试通知", use_container_width=True):
            if config.EMAIL_ENABLED:
                notifier.send_email("测试通知", "这是一封测试邮件", config.EMAIL_TO)
                st.success("测试邮件已发送")
            if config.DINGTALK_ENABLED:
                notifier.send_dingtalk("这是一条测试消息")
                st.success("测试钉钉消息已发送")


def run_manual_check():
    """运行手动预警检查"""
    triggered = alert_engine.run_all_checks()
    
    if triggered:
        if config.EMAIL_ENABLED or config.DINGTALK_ENABLED:
            notifier.send_alert_notifications(triggered)


def main():
    """主函数"""
    # 渲染侧边栏
    page = render_sidebar()
    
    # 渲染页面
    if page == "portfolio":
        render_portfolio_page()
    elif page == "alerts":
        render_alerts_page()
    elif page == "analysis":
        render_analysis_page()
    elif page == "settings":
        render_settings_page()
    
    # 自动预警检查 (使用 session state 控制)
    if 'last_check' not in st.session_state:
        st.session_state.last_check = datetime.now()
    
    time_since_check = (datetime.now() - st.session_state.last_check).total_seconds()
    
    if time_since_check >= config.CHECK_INTERVAL:
        run_manual_check()
        st.session_state.last_check = datetime.now()


if __name__ == "__main__":
    main()
