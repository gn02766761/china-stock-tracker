"""
股票监控启动脚本

快速启动股票监控和预警系统
"""

import os
import sys
import subprocess
import time


def check_dependencies():
    """检查依赖是否安装"""
    required_packages = ['streamlit', 'plotly', 'pandas', 'numpy']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("⚠️ 缺少以下依赖包:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("\n请运行以下命令安装:")
        print("  pip install -r requirements_web.txt")
        return False
    
    return True


def start_dashboard(port=8501):
    """启动主仪表盘"""
    print(f"🚀 启动股票分析仪表盘...")
    print(f"📊 访问地址：http://localhost:{port}")
    print(f"按 Ctrl+C 停止服务\n")
    
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        "web_app/dashboard.py",
        f"--server.port={port}",
        "--server.headless=true"
    ]
    
    subprocess.run(cmd)


def start_alert_monitor(port=8502):
    """启动预警监控面板"""
    print(f"🚨 启动预警监控面板...")
    print(f"📊 访问地址：http://localhost:{port}")
    print(f"按 Ctrl+C 停止服务\n")
    
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        "web_app/alert_dashboard.py",
        f"--server.port={port}",
        "--server.headless=true"
    ]
    
    subprocess.run(cmd)


def start_monitor_script():
    """启动后台监控脚本"""
    print("🔍 启动实时监控服务...")
    
    # 检查配置文件
    if not os.path.exists("data/alerts.json"):
        print("ℹ️ 首次运行，将创建预警配置文件")
        os.makedirs("data", exist_ok=True)
    
    # 运行监控脚本
    from realtime_monitor import RealtimeMonitor, SimpleMonitor
    from price_alert import PriceAlertManager
    
    # 使用简易监控（无需 token）
    monitor = SimpleMonitor()
    
    print("\n" + "=" * 60)
    print("股票监控服务已启动")
    print("=" * 60)
    print("按 Ctrl+C 停止监控\n")
    
    try:
        # 显示活跃预警
        alerts = monitor.alert_manager.get_active_alerts()
        
        if alerts:
            print(f"📋 当前活跃预警：{len(alerts)}个")
            for alert in alerts:
                print(f"  - {alert.symbol}: {alert.alert_type.value} = {alert.condition_value}")
        else:
            print("⚠️ 暂无活跃预警")
            print("\n请在 Web 界面设置预警:")
            print("  streamlit run web_app/alert_dashboard.py")
        
        # 保持运行
        while True:
            time.sleep(60)
    
    except KeyboardInterrupt:
        print("\n\n⏹️ 监控服务已停止")


def show_menu():
    """显示菜单"""
    print("\n" + "=" * 60)
    print("股票监控系统启动菜单")
    print("=" * 60)
    print("1. 启动股票分析仪表盘 (端口 8501)")
    print("2. 启动预警监控面板 (端口 8502)")
    print("3. 启动后台监控服务")
    print("4. 同时启动所有服务")
    print("5. 退出")
    print("=" * 60)
    
    choice = input("请选择 (1-5): ").strip()
    return choice


def main():
    """主函数"""
    print("=" * 60)
    print("中国股票监控系统")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 显示菜单
    choice = show_menu()
    
    if choice == '1':
        start_dashboard()
    
    elif choice == '2':
        start_alert_monitor()
    
    elif choice == '3':
        start_monitor_script()
    
    elif choice == '4':
        print("\n🚀 启动所有服务...")
        
        # 启动仪表盘
        p1 = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run",
            "web_app/dashboard.py",
            "--server.port=8501",
            "--server.headless=true"
        ])
        
        # 启动预警面板
        p2 = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run",
            "web_app/alert_dashboard.py",
            "--server.port=8502",
            "--server.headless=true"
        ])
        
        print("\n✅ 所有服务已启动")
        print("📊 股票分析仪表盘：http://localhost:8501")
        print("🚨 预警监控面板：http://localhost:8502")
        print("\n按 Ctrl+C 停止所有服务\n")
        
        try:
            p1.wait()
            p2.wait()
        except KeyboardInterrupt:
            print("\n⏹️ 停止所有服务...")
            p1.terminate()
            p2.terminate()
    
    elif choice == '5':
        print("👋 再见!")
        return
    
    else:
        print("❌ 无效选择")


if __name__ == "__main__":
    main()
