"""
配置管理模块
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)


class Config:
    """系统配置类"""
    
    # 数据库配置
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./database/stock_portfolio.db')
    
    # Tushare 配置
    TUSHARE_TOKEN = os.getenv('TUSHARE_TOKEN', '')
    
    # 邮件通知配置
    EMAIL_ENABLED = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_USER = os.getenv('EMAIL_USER', '')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
    EMAIL_TO = os.getenv('EMAIL_TO', '')
    
    # 钉钉通知配置
    DINGTALK_ENABLED = os.getenv('DINGTALK_ENABLED', 'false').lower() == 'true'
    DINGTALK_WEBHOOK = os.getenv('DINGTALK_WEBHOOK', '')
    
    # 预警检查间隔 (秒)
    CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 60))
    
    # 默认监控股票列表
    DEFAULT_STOCKS = os.getenv('DEFAULT_STOCKS', '000001,600519,000858').split(',')
    
    # 项目根目录
    BASE_DIR = Path(__file__).parent.parent
    
    # 数据目录
    DATA_DIR = BASE_DIR / 'data'
    LOGS_DIR = BASE_DIR / 'logs'
    
    # 确保目录存在
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


config = Config()
