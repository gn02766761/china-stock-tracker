"""
股票预警监控示例脚本

演示如何使用预警和监控系统
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from price_alert import PriceAlertManager, AlertType
from realtime_monitor import SimpleMonitor
from notification_service import NotificationService


def demo_price_alert():
    """演示价格预警"""
    print("\n" + "=" * 60)
    print("示例 1: 价格预警")
    print("=" * 60)
    
    # 创建预警管理器
    manager = PriceAlertManager()
    
    # 创建价格突破预警
    alert = manager.create_price_breakout_alert(
        symbol="000001",
        name="平安银行",
        breakout_price=10.5,
        above=True,
        notification_methods=['console'],
        notes="突破 10.5 元阻力位"
    )
    
    print(f"✓ 创建预警：{alert.symbol} - {alert.name}")
    print(f"  类型：{alert.alert_type.value}")
    print(f"  条件：突破 {alert.condition_value}")
    
    # 列出所有预警
    manager.list_alerts() if hasattr(manager, 'list_alerts') else None
    
    return manager


def demo_stop_loss_take_profit():
    """演示止损止盈预警"""
    print("\n" + "=" * 60)
    print("示例 2: 止损止盈预警")
    print("=" * 60)
    
    monitor = SimpleMonitor()
    
    # 设置止损止盈
    monitor.set_stop_loss_take_profit(
        symbol="000001",
        name="平安银行",
        current_price=10.0,
        stop_loss_pct=5.0,
        take_profit_pct=10.0
    )
    
    # 显示预警列表
    monitor.list_alerts()
    
    # 模拟价格变动测试
    print("\n--- 测试预警触发 ---")
    print("模拟价格涨到 11.0 元（触发止盈）:")
    monitor.check_manual("000001", 11.0)
    
    return monitor


def demo_rsi_alert():
    """演示 RSI 预警"""
    print("\n" + "=" * 60)
    print("示例 3: RSI 超买超卖预警")
    print("=" * 60)
    
    manager = PriceAlertManager()
    
    # 创建 RSI 预警
    alerts = manager.create_rsi_alert(
        symbol="600519",
        name="贵州茅台",
        overbought=70,
        oversold=30,
        notification_methods=['console']
    )
    
    print(f"✓ 创建 RSI 预警：{len(alerts)}个")
    for alert in alerts:
        print(f"  - {alert.alert_type.value}: {alert.condition_value}")
    
    return manager


def demo_monitoring():
    """演示实时监控"""
    print("\n" + "=" * 60)
    print("示例 4: 实时监控（模拟）")
    print("=" * 60)
    
    monitor = SimpleMonitor()
    
    # 添加监控股票
    monitor.add_stock("000001", "平安银行")
    monitor.add_stock("600519", "贵州茅台")
    
    # 设置预警
    monitor.set_price_alert(
        "000001", "平安银行",
        target_price=10.5,
        above=True
    )
    
    monitor.set_price_alert(
        "000001", "平安银行",
        target_price=9.5,
        above=False
    )
    
    # 显示监控状态
    print(f"\n监控股票：{len(monitor.watchlist)}只")
    print(f"活跃预警：{len(monitor.alert_manager.get_active_alerts())}个")
    
    # 模拟检查
    print("\n--- 模拟价格检查 ---")
    test_prices = [10.0, 10.3, 10.6, 9.8, 9.4]
    
    for price in test_prices:
        print(f"\n当前价格：{price}")
        monitor.check_manual("000001", price)
    
    return monitor


def demo_notification():
    """演示通知服务"""
    print("\n" + "=" * 60)
    print("示例 5: 通知服务")
    print("=" * 60)
    
    service = NotificationService()
    
    # 测试控制台通知
    print("\n测试控制台通知:")
    service.test_notification('console')
    
    # 显示配置
    print("\n当前通知配置:")
    print(f"  邮件：{'已启用' if service.config.get('email', {}).get('enabled') else '未启用'}")
    print(f"  微信：{'已启用' if service.config.get('wechat', {}).get('enabled') else '未启用'}")
    print(f"  短信：{'已启用' if service.config.get('sms', {}).get('enabled') else '未启用'}")
    print(f"  控制台：{'已启用' if service.config.get('console', {}).get('enabled') else '未启用'}")
    
    return service


def run_all_demos():
    """运行所有演示"""
    print("\n" + "=" * 70)
    print("股票预警监控系统 - 演示程序")
    print("=" * 70)
    
    # 演示 1: 价格预警
    demo_price_alert()
    
    # 演示 2: 止损止盈
    demo_stop_loss_take_profit()
    
    # 演示 3: RSI 预警
    demo_rsi_alert()
    
    # 演示 4: 实时监控
    demo_monitoring()
    
    # 演示 5: 通知服务
    demo_notification()
    
    print("\n" + "=" * 70)
    print("演示完成!")
    print("=" * 70)
    print("\n下一步:")
    print("1. 启动 Web 界面：streamlit run web_app/dashboard.py")
    print("2. 启动预警面板：streamlit run web_app/alert_dashboard.py")
    print("3. 启动监控服务：python start_monitor.py")
    print("=" * 70)


if __name__ == "__main__":
    run_all_demos()
