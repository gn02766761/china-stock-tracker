"""
股票预警监控 Web 界面

提供预警设置和监控管理的交互式界面
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from price_alert import PriceAlertManager, PriceAlert, AlertType, AlertStatus
from realtime_monitor import RealtimeMonitor, SimpleMonitor
from notification_service import NotificationService


def init_session_state():
    """初始化会话状态"""
    if 'alert_manager' not in st.session_state:
        st.session_state.alert_manager = PriceAlertManager()
    if 'simple_monitor' not in st.session_state:
        st.session_state.simple_monitor = SimpleMonitor(st.session_state.alert_manager)
    if 'notification_service' not in st.session_state:
        st.session_state.notification_service = NotificationService()


def main():
    """主函数"""
    init_session_state()
    
    st.set_page_config(
        page_title="股票预警监控",
        page_icon="🚨",
        layout="wide"
    )
    
    # 侧边栏
    with st.sidebar:
        st.markdown("## 🚨 预警监控")
        
        menu = st.radio(
            "选择功能",
            ["📋 预警列表", "➕ 设置预警", "⚙️ 通知配置", "📊 监控状态"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # 快速统计
        active_alerts = st.session_state.alert_manager.get_active_alerts()
        triggered_alerts = st.session_state.alert_manager.get_triggered_alerts(hours=24)
        
        st.metric("活跃预警", len(active_alerts))
        st.metric("24 小时触发", len(triggered_alerts))
    
    # 主内容
    if menu == "📋 预警列表":
        render_alert_list()
    elif menu == "➕ 设置预警":
        render_setup_alert()
    elif menu == "⚙️ 通知配置":
        render_notification_config()
    elif menu == "📊 监控状态":
        render_monitor_status()


def render_alert_list():
    """渲染预警列表"""
    st.markdown("## 📋 预警列表")
    
    # 选项卡
    tab1, tab2, tab3 = st.tabs(["活跃预警", "已触发", "全部"])
    
    with tab1:
        alerts = st.session_state.alert_manager.get_active_alerts()
        
        if alerts:
            data = []
            for alert in alerts:
                data.append({
                    'ID': alert.id,
                    '股票代码': alert.symbol,
                    '股票名称': alert.name,
                    '类型': alert.alert_type.value,
                    '条件值': alert.condition_value,
                    '备注': alert.notes,
                    '过期时间': alert.expires_at.strftime('%Y-%m-%d %H:%M') if alert.expires_at else '无'
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # 操作
            st.markdown("### 操作")
            col1, col2 = st.columns(2)
            
            with col1:
                alert_to_cancel = st.selectbox(
                    "取消预警",
                    options=[a.id for a in alerts],
                    format_func=lambda x: f"{x}"
                )
                
                if st.button("取消选中预警"):
                    st.session_state.alert_manager.cancel_alert(alert_to_cancel)
                    st.success(f"预警 {alert_to_cancel} 已取消")
                    st.rerun()
            
            with col2:
                if st.button("清理过期预警"):
                    count = st.session_state.alert_manager.clear_expired_alerts()
                    st.info(f"清理了 {count} 个过期预警")
                    st.rerun()
        else:
            st.info("暂无活跃预警")
    
    with tab2:
        alerts = st.session_state.alert_manager.get_triggered_alerts(hours=24)
        
        if alerts:
            data = []
            for alert in alerts:
                data.append({
                    'ID': alert.id,
                    '股票代码': alert.symbol,
                    '股票名称': alert.name,
                    '类型': alert.alert_type.value,
                    '条件值': alert.condition_value,
                    '当前值': alert.current_value,
                    '触发时间': alert.triggered_at.strftime('%Y-%m-%d %H:%M:%S') if alert.triggered_at else 'N/A'
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("最近 24 小时无触发的预警")
    
    with tab3:
        all_alerts = list(st.session_state.alert_manager.alerts.values())
        
        if all_alerts:
            data = []
            for alert in all_alerts:
                data.append({
                    'ID': alert.id,
                    '股票代码': alert.symbol,
                    '股票名称': alert.name,
                    '类型': alert.alert_type.value,
                    '状态': alert.status.value,
                    '条件值': alert.condition_value,
                    '创建时间': alert.created_at.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("暂无任何预警")


def render_setup_alert():
    """渲染设置预警页面"""
    st.markdown("## ➕ 设置预警")
    
    # 预警类型选择
    alert_type = st.selectbox(
        "预警类型",
        [
            "价格突破预警",
            "止损止盈预警",
            "均线交叉预警",
            "RSI 超买超卖预警",
            "成交量突破预警"
        ]
    )
    
    st.markdown("### 股票信息")
    col1, col2 = st.columns(2)
    
    with col1:
        symbol = st.text_input("股票代码", value="000001", max_chars=6)
    
    with col2:
        name = st.text_input("股票名称", value="平安银行")
    
    st.markdown("### 预警条件")
    
    if alert_type == "价格突破预警":
        breakout_type = st.radio(
            "突破方向",
            ["向上突破", "向下跌破"]
        )
        
        target_price = st.number_input(
            "目标价格",
            min_value=0.01,
            max_value=10000.0,
            value=10.0,
            step=0.01
        )
        
        if st.button("设置价格预警", type="primary"):
            above = breakout_type == "向上突破"
            direction = "突破" if above else "跌破"
            
            st.session_state.simple_monitor.set_price_alert(
                symbol, name, target_price, above=above
            )
            
            st.success(f"✓ 已设置预警：{symbol} - {direction}{target_price:.2f}")
    
    elif alert_type == "止损止盈预警":
        current_price = st.number_input(
            "当前价格",
            min_value=0.01,
            max_value=10000.0,
            value=10.0,
            step=0.01
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            stop_loss_pct = st.number_input(
                "止损比例 (%)",
                min_value=0.0,
                max_value=100.0,
                value=5.0,
                step=0.5
            )
        
        with col2:
            take_profit_pct = st.number_input(
                "止盈比例 (%)",
                min_value=0.0,
                max_value=1000.0,
                value=10.0,
                step=0.5
            )
        
        if st.button("设置止损止盈预警", type="primary"):
            st.session_state.simple_monitor.set_stop_loss_take_profit(
                symbol, name, current_price,
                stop_loss_pct=stop_loss_pct,
                take_profit_pct=take_profit_pct
            )
            
            stop_price = current_price * (1 - stop_loss_pct / 100)
            target_price = current_price * (1 + take_profit_pct / 100)
            
            st.success(f"✓ 已设置：止损{stop_price:.2f}, 止盈{target_price:.2f}")
    
    elif alert_type == "RSI 超买超卖预警":
        col1, col2 = st.columns(2)
        
        with col1:
            overbought = st.number_input(
                "超买线",
                min_value=50,
                max_value=100,
                value=70
            )
        
        with col2:
            oversold = st.number_input(
                "超卖线",
                min_value=0,
                max_value=50,
                value=30
            )
        
        if st.button("设置 RSI 预警", type="primary"):
            alerts = st.session_state.simple_monitor.alert_manager.create_rsi_alert(
                symbol, name,
                overbought=overbought,
                oversold=oversold,
                notification_methods=['console']
            )
            
            st.success(f"✓ 已设置 RSI 预警：超买{overbought}, 超卖{oversold}")
    
    elif alert_type == "成交量突破预警":
        volume_multiplier = st.number_input(
            "成交量倍数",
            min_value=1.0,
            max_value=100.0,
            value=2.0,
            step=0.5,
            help="当日成交量超过均量的倍数"
        )
        
        if st.button("设置成交量预警", type="primary"):
            st.session_state.simple_monitor.alert_manager.create_alert(
                symbol=symbol,
                name=name,
                alert_type=AlertType.VOLUME_SPIKE,
                condition_value=volume_multiplier,
                notification_methods=['console'],
                notes=f"成交量超过{volume_multiplier}倍均量"
            )
            
            st.success(f"✓ 已设置成交量预警：{volume_multiplier}倍")
    
    # 通知方式
    st.markdown("### 📬 通知方式")
    notification_methods = st.multiselect(
        "选择通知方式",
        ["控制台", "邮件", "微信", "短信"],
        default=["控制台"]
    )
    
    # 有效期
    st.markdown("### ⏰ 有效期")
    expires_days = st.slider(
        "预警有效期（天）",
        min_value=1,
        max_value=365,
        value=30
    )


def render_notification_config():
    """渲染通知配置页面"""
    st.markdown("## ⚙️ 通知配置")
    
    notification_service = st.session_state.notification_service
    
    # 邮件配置
    st.markdown("### 📧 邮件通知")
    
    with st.expander("配置邮件通知", expanded=False):
        smtp_server = st.text_input("SMTP 服务器", value="smtp.qq.com")
        smtp_port = st.number_input("SMTP 端口", value=587)
        sender = st.text_input("发件人邮箱")
        password = st.text_input("邮箱密码/授权码", type="password")
        receivers = st.text_area(
            "收件人列表",
            value="receiver1@email.com",
            help="每行一个邮箱地址"
        )
        
        if st.button("保存邮件配置"):
            receiver_list = [r.strip() for r in receivers.split('\n') if r.strip()]
            
            notification_service.setup_email(
                smtp_server=smtp_server,
                smtp_port=smtp_port,
                sender=sender,
                password=password,
                receivers=receiver_list
            )
            
            st.success("✓ 邮件配置已保存")
    
    # 微信配置
    st.markdown("### 💬 微信通知")
    
    with st.expander("配置微信通知 (ServerChan)", expanded=False):
        st.info("ServerChan 是一个免费的微信推送服务，访问 https://sct.ftqq.com/ 获取推送 key")
        
        serverchan_key = st.text_input("ServerChan 推送 key", type="password")
        
        if st.button("保存微信配置"):
            notification_service.setup_wechat_serverchan(serverchan_key)
            st.success("✓ 微信配置已保存")
    
    # 测试通知
    st.markdown("### 🧪 测试通知")
    
    if st.button("发送测试通知"):
        notification_service.test_notification('console')
        st.success("✓ 测试通知已发送")


def render_monitor_status():
    """渲染监控状态页面"""
    st.markdown("## 📊 监控状态")
    
    # 监控状态
    st.markdown("### 实时监控状态")
    
    simple_monitor = st.session_state.simple_monitor
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("监控股票", len(simple_monitor.watchlist))
    
    with col2:
        active = st.session_state.alert_manager.get_active_alerts()
        st.metric("活跃预警", len(active))
    
    with col3:
        triggered = st.session_state.alert_manager.get_triggered_alerts(hours=24)
        st.metric("24 小时触发", len(triggered))
    
    with col4:
        st.metric("通知服务", "已配置")
    
    # 预警统计
    st.markdown("### 预警统计")
    
    all_alerts = list(st.session_state.alert_manager.alerts.values())
    
    if all_alerts:
        # 按类型统计
        type_counts = {}
        status_counts = {}
        
        for alert in all_alerts:
            type_name = alert.alert_type.value
            status_name = alert.status.value
            
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
            status_counts[status_name] = status_counts.get(status_name, 0) + 1
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**按类型统计**")
            for type_name, count in type_counts.items():
                st.write(f"- {type_name}: {count}")
        
        with col2:
            st.markdown("**按状态统计**")
            for status_name, count in status_counts.items():
                st.write(f"- {status_name}: {count}")
    else:
        st.info("暂无预警数据")
    
    # 手动触发测试
    st.markdown("### 🧪 手动触发测试")
    
    col1, col2 = st.columns(2)
    
    with col1:
        test_symbol = st.text_input("测试股票代码", value="000001")
    
    with col2:
        test_price = st.number_input("测试价格", value=10.0, step=0.01)
    
    if st.button("手动检查预警"):
        triggered = simple_monitor.check_manual(test_symbol, test_price)
        
        if triggered:
            st.warning(f"触发 {len(triggered)} 个预警")
            for alert in triggered:
                st.write(f"- {alert.name}: {alert.alert_type.value}")
        else:
            st.info("无预警触发")


if __name__ == "__main__":
    main()
