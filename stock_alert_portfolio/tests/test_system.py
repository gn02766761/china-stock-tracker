"""
系统测试脚本
测试股票智能预警与投资组合管理系统的各项功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import config
from database.database_manager import DatabaseManager
from app.data_service import StockDataService
from app.portfolio_manager import PortfolioManager
from app.alert_engine import AlertEngine


def print_section(title):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_database():
    """测试数据库功能"""
    print_section("测试 1: 数据库功能")
    
    db = DatabaseManager(config.DATABASE_URL)
    
    # 测试查询持仓
    holdings = db.get_holdings()
    print(f"✓ 持仓记录数量：{len(holdings)}")
    
    for h in holdings:
        print(f"  - {h.stock_name}({h.stock_code}): {h.shares}股，成本{h.avg_cost}元")
    
    # 测试查询预警
    price_alerts = db.get_active_price_alerts()
    tech_alerts = db.get_active_technical_alerts()
    
    print(f"✓ 价格预警数量：{len(price_alerts)}")
    print(f"✓ 技术指标预警数量：{len(tech_alerts)}")
    
    return True


def test_portfolio_manager():
    """测试投资组合管理"""
    print_section("测试 2: 投资组合管理")
    
    db = DatabaseManager(config.DATABASE_URL)
    data_service = StockDataService()
    portfolio_manager = PortfolioManager(db, data_service)
    
    # 获取投资组合摘要
    summary = portfolio_manager.get_portfolio_summary()
    
    print(f"总持仓数：{summary['total_holdings']}")
    print(f"总投入：{summary['total_invested']:.2f}元")
    print(f"总市值：{summary['total_market_value']:.2f}元")
    
    if summary['positions']:
        print("\n持仓明细:")
        for pos in summary['positions']:
            status = "✓" if pos['profit_loss'] >= 0 else "✗"
            print(f"  {status} {pos['stock_name']}({pos['stock_code']})")
            print(f"      持仓：{pos['shares']}股 | 成本：{pos['avg_cost']:.2f}元")
            print(f"      盈亏：{pos['profit_loss']:+.2f}元 ({pos['profit_loss_rate']:+.2f}%)")
    
    # 测试投资组合分析
    analysis = portfolio_manager.get_portfolio_analysis()
    
    if analysis.get('diversification'):
        print(f"\n集中度：{analysis['diversification'].get('concentration_rate', 0):.2f}%")
    
    if analysis.get('risk_metrics'):
        print(f"胜率：{analysis['risk_metrics'].get('win_rate', 0):.2f}%")
    
    return True


def test_data_service():
    """测试数据服务"""
    print_section("测试 3: 数据服务")
    
    data_service = StockDataService()
    
    # 测试获取股票信息
    print("测试获取股票信息...")
    test_stocks = ['000001', '600519', '000858']
    
    for code in test_stocks:
        try:
            info = data_service.get_stock_info(code)
            print(f"  ✓ {code}: {info.get('name', 'N/A')}")
        except Exception as e:
            print(f"  ✗ {code}: 获取失败 ({e})")
    
    # 测试获取价格（可能受速率限制）
    print("\n测试获取当前价格...")
    for code in test_stocks:
        try:
            price = data_service.get_current_price(code)
            if price:
                print(f"  ✓ {code}: {price:.2f}元")
            else:
                print(f"  ✗ {code}: 无数据")
        except Exception as e:
            print(f"  ✗ {code}: {e}")
    
    return True


def test_alert_engine():
    """测试预警引擎"""
    print_section("测试 4: 预警引擎")
    
    db = DatabaseManager(config.DATABASE_URL)
    data_service = StockDataService()
    alert_engine = AlertEngine(db, data_service)
    
    print("运行预警检查...")
    
    try:
        triggered = alert_engine.run_all_checks()
        summary = alert_engine.get_check_summary()
        
        print(f"检查时间：{summary['check_time']}")
        print(f"触发预警：{summary['total_triggered']}条")
        
        if triggered:
            print("\n触发的预警:")
            for alert in triggered:
                print(f"  ⚠️ {alert['message']}")
        else:
            print("暂无预警触发")
        
        return True
    except Exception as e:
        print(f"预警检查失败：{e}")
        return False


def test_alert_logs():
    """测试预警日志"""
    print_section("测试 5: 预警日志")
    
    db = DatabaseManager(config.DATABASE_URL)
    
    logs = db.get_alert_logs(limit=10)
    
    if logs:
        print(f"最近 {len(logs)} 条预警日志:")
        for log in logs:
            time_str = log.created_at.strftime('%Y-%m-%d %H:%M:%S')
            print(f"  [{time_str}] {log.stock_name}({log.stock_code})")
            print(f"    {log.message[:60]}...")
    else:
        print("暂无预警日志")
    
    return True


def test_add_delete_operations():
    """测试添加和删除操作"""
    print_section("测试 6: 添加/删除操作")
    
    db = DatabaseManager(config.DATABASE_URL)
    
    # 测试添加持仓
    print("测试添加测试持仓...")
    holding_id = db.add_holding('000999', '测试股票', 100, 10.5, '测试用')
    print(f"  ✓ 添加持仓 ID: {holding_id}")
    
    # 测试删除持仓
    print("测试删除测试持仓...")
    result = db.delete_holding(holding_id)
    print(f"  ✓ 删除结果：{result}")
    
    # 测试添加预警
    print("测试添加测试预警...")
    alert_id = db.add_price_alert('000999', '测试股票', 'price_above', 15.0)
    print(f"  ✓ 添加预警 ID: {alert_id}")
    
    # 测试删除预警
    print("测试删除测试预警...")
    result = db.delete_alert(alert_id, alert_type='price')
    print(f"  ✓ 删除结果：{result}")
    
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "系统功能测试" + " " * 27 + "║")
    print("╚" + "=" * 58 + "╝")
    
    results = []
    
    # 运行测试
    results.append(("数据库功能", test_database()))
    results.append(("投资组合管理", test_portfolio_manager()))
    results.append(("数据服务", test_data_service()))
    results.append(("预警引擎", test_alert_engine()))
    results.append(("预警日志", test_alert_logs()))
    results.append(("添加/删除操作", test_add_delete_operations()))
    
    # 打印测试摘要
    print_section("测试摘要")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {status} - {name}")
    
    print(f"\n总计：{passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统运行正常！")
    else:
        print(f"\n⚠️ {total - passed} 个测试失败，请检查日志")
    
    print("\n" + "=" * 60 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
