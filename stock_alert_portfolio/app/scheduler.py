"""
定时任务调度器
用于后台运行预警检查
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import config
from database.database_manager import DatabaseManager
from app.data_service import StockDataService
from app.alert_engine import AlertEngine
from notifications.notifier import NotificationService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOGS_DIR / 'alert_scheduler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class AlertScheduler:
    """预警调度器"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.db = DatabaseManager(config.DATABASE_URL)
        self.data_service = StockDataService()
        self.alert_engine = AlertEngine(self.db, self.data_service)
        self.notifier = NotificationService()
        self.running = False
    
    def check_alerts_job(self):
        """预警检查任务"""
        logger.info("开始执行预警检查...")
        
        try:
            # 运行预警检查
            triggered_alerts = self.alert_engine.run_all_checks()
            
            # 获取检查摘要
            summary = self.alert_engine.get_check_summary()
            logger.info(f"检查完成：{summary}")
            
            # 发送通知
            if triggered_alerts:
                logger.info(f"发现 {len(triggered_alerts)} 条预警")
                
                # 打印预警信息
                for alert in triggered_alerts:
                    logger.info(f"预警：{alert['message']}")
                
                # 发送通知
                if config.EMAIL_ENABLED or config.DINGTALK_ENABLED:
                    success_count = self.notifier.send_alert_notifications(triggered_alerts)
                    logger.info(f"成功发送 {success_count} 个通知")
                else:
                    logger.info("通知未启用，跳过发送")
            else:
                logger.info("无预警触发")
        
        except Exception as e:
            logger.error(f"预警检查失败：{e}", exc_info=True)
    
    def start(self):
        """启动调度器"""
        if self.running:
            logger.warning("调度器已在运行中")
            return
        
        # 添加定时任务
        self.scheduler.add_job(
            self.check_alerts_job,
            trigger=IntervalTrigger(seconds=config.CHECK_INTERVAL),
            id='alert_check',
            name='预警检查',
            replace_existing=True
        )
        
        # 启动调度器
        self.scheduler.start()
        self.running = True
        
        logger.info(f"预警调度器已启动，检查间隔：{config.CHECK_INTERVAL}秒")
        logger.info("按 Ctrl+C 退出")
    
    def stop(self):
        """停止调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.running = False
            logger.info("预警调度器已停止")
    
    def run_once(self):
        """立即执行一次检查"""
        self.check_alerts_job()


def main():
    """主函数"""
    print("=" * 60)
    print("股票预警调度器")
    print("=" * 60)
    print(f"数据库：{config.DATABASE_URL}")
    print(f"检查间隔：{config.CHECK_INTERVAL}秒")
    print(f"邮件通知：{'已启用' if config.EMAIL_ENABLED else '未启用'}")
    print(f"钉钉通知：{'已启用' if config.DINGTALK_ENABLED else '未启用'}")
    print("=" * 60)
    
    scheduler = AlertScheduler()
    
    try:
        scheduler.start()
        
        # 保持运行
        import time
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n正在停止...")
        scheduler.stop()
        print("已退出")


if __name__ == "__main__":
    main()
