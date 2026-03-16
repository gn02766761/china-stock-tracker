"""
命令行工具
提供便捷的 CLI 操作
"""
import click
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import config
from database.database_manager import DatabaseManager
from app.data_service import StockDataService
from app.portfolio_manager import PortfolioManager
from app.alert_engine import AlertEngine
from notifications.notifier import NotificationService


# 初始化服务
db = DatabaseManager(config.DATABASE_URL)
data_service = StockDataService()
portfolio_manager = PortfolioManager(db, data_service)
alert_engine = AlertEngine(db, data_service)
notifier = NotificationService()


@click.group()
def cli():
    """股票智能预警与投资组合管理系统 CLI"""
    pass


@cli.group()
def portfolio():
    """投资组合管理"""
    pass


@portfolio.command('add')
@click.option('--code', required=True, help='股票代码')
@click.option('--name', default='', help='股票名称')
@click.option('--shares', required=True, type=float, help='持仓数量')
@click.option('--cost', required=True, type=float, help='平均成本')
@click.option('--notes', default='', help='备注')
def add_position(code, name, shares, cost, notes):
    """添加持仓"""
    if not name:
        info = data_service.get_stock_info(code)
        name = info.get('name', code)
    
    holding_id = portfolio_manager.add_position(code, name, shares, cost, notes)
    click.echo(f"✅ 已添加持仓，ID: {holding_id}")


@portfolio.command('list')
def list_positions():
    """列出所有持仓"""
    summary = portfolio_manager.get_portfolio_summary()
    
    if summary['total_holdings'] == 0:
        click.echo("📭 暂无持仓")
        return
    
    click.echo(f"\n📊 投资组合摘要")
    click.echo(f"总市值：{summary['total_market_value']:.2f} 元")
    click.echo(f"总投入：{summary['total_invested']:.2f} 元")
    click.echo(f"总盈亏：{summary['total_profit_loss']:.2f} 元 ({summary['profit_loss_rate']:.2f}%)")
    click.echo(f"持仓数量：{summary['total_holdings']}")
    
    click.echo(f"\n📋 持仓明细:")
    for pos in summary['positions']:
        click.echo(f"  {pos['stock_name']}({pos['stock_code']}): "
                  f"{pos['shares']}股 × {pos['avg_cost']:.2f}元 = "
                  f"{pos['market_value']:.2f}元 "
                  f"({'+' if pos['profit_loss'] >= 0 else ''}{pos['profit_loss']:.2f}元, "
                  f"{'+' if pos['profit_loss_rate'] >= 0 else ''}{pos['profit_loss_rate']:.2f}%)")


@portfolio.command('remove')
@click.option('--id', 'holding_id', required=True, type=int, help='持仓 ID')
def remove_position(holding_id):
    """删除持仓"""
    if portfolio_manager.delete_position(holding_id):
        click.echo(f"✅ 已删除持仓 ID: {holding_id}")
    else:
        click.echo(f"❌ 删除失败，未找到持仓 ID: {holding_id}")


@cli.group()
def alert():
    """预警管理"""
    pass


@alert.command('add-price')
@click.option('--code', required=True, help='股票代码')
@click.option('--name', default='', help='股票名称')
@click.option('--type', 'alert_type', required=True, 
              type=click.Choice(['price_above', 'price_below', 'change_above', 'change_below']),
              help='预警类型')
@click.option('--threshold', required=True, type=float, help='阈值')
def add_price_alert(code, name, alert_type, threshold):
    """添加价格预警"""
    if not name:
        info = data_service.get_stock_info(code)
        name = info.get('name', code)
    
    alert_id = db.add_price_alert(code, name, alert_type, threshold)
    click.echo(f"✅ 已添加价格预警，ID: {alert_id}")


@alert.command('add-tech')
@click.option('--code', required=True, help='股票代码')
@click.option('--name', default='', help='股票名称')
@click.option('--indicator', required=True, 
              type=click.Choice(['RSI', 'MACD', 'MA5', 'MA10', 'MA20', 'MA60', 'BB']),
              help='技术指标')
@click.option('--condition', required=True,
              type=click.Choice(['cross_above', 'cross_below', 'above', 'below', 'touch_upper', 'touch_lower']),
              help='条件')
@click.option('--threshold', required=True, type=float, help='阈值')
def add_technical_alert(code, name, indicator, condition, threshold):
    """添加技术指标预警"""
    if not name:
        info = data_service.get_stock_info(code)
        name = info.get('name', code)
    
    alert_id = db.add_technical_alert(code, name, indicator, condition, threshold)
    click.echo(f"✅ 已添加技术指标预警，ID: {alert_id}")


@alert.command('list')
def list_alerts():
    """列出所有预警"""
    price_alerts = db.get_active_price_alerts()
    tech_alerts = db.get_active_technical_alerts()
    
    if not price_alerts and not tech_alerts:
        click.echo("🔔 暂无预警")
        return
    
    click.echo("\n📍 价格预警:")
    for alert in price_alerts:
        click.echo(f"  ID:{alert.id} - {alert.stock_name}({alert.stock_code}): "
                  f"{alert.alert_type} {alert.threshold_value} "
                  f"(触发{alert.trigger_count}次)")
    
    click.echo("\n📈 技术指标预警:")
    for alert in tech_alerts:
        click.echo(f"  ID:{alert.id} - {alert.stock_name}({alert.stock_code}): "
                  f"{alert.indicator} {alert.condition} {alert.threshold_value} "
                  f"(触发{alert.trigger_count}次)")


@alert.command('check')
def check_alerts():
    """立即检查预警"""
    click.echo("🔍 正在检查预警...")
    
    triggered = alert_engine.run_all_checks()
    summary = alert_engine.get_check_summary()
    
    click.echo(f"\n检查时间：{summary['check_time']}")
    click.echo(f"触发预警：{summary['total_triggered']}条")
    
    if triggered:
        for alert in triggered:
            click.echo(f"  ⚠️ {alert['message']}")
        
        # 发送通知
        if config.EMAIL_ENABLED or config.DINGTALK_ENABLED:
            notifier.send_alert_notifications(triggered)
            click.echo("\n📤 已发送通知")
    else:
        click.echo("暂无预警触发")


@cli.command('web')
@click.option('--host', default='0.0.0.0', help='监听地址')
@click.option('--port', default=8501, help='端口号')
def run_web(host, port):
    """启动 Web 仪表板"""
    click.echo(f"🌐 启动 Web 仪表板...")
    click.echo(f"访问地址：http://localhost:{port}")
    
    os.system(f"streamlit run app/dashboard.py --server.address {host} --server.port {port}")


@cli.command('scheduler')
def run_scheduler():
    """启动预警调度器"""
    click.echo("⏰ 启动预警调度器...")
    
    os.system(f"python app/scheduler.py")


@cli.command('init')
def init_database():
    """初始化数据库"""
    click.echo("🗄️ 初始化数据库...")
    # 重新创建数据库管理器会创建表
    db = DatabaseManager(config.DATABASE_URL)
    click.echo("✅ 数据库初始化完成")


if __name__ == '__main__':
    cli()
