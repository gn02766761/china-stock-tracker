@echo off
echo ========================================
echo 股票智能预警与投资组合管理系统
echo ========================================
echo.
echo 正在安装依赖...
pip install -r requirements.txt
echo.
echo 初始化数据库...
python main.py init
echo.
echo ========================================
echo 安装完成!
echo ========================================
echo.
echo 使用方法:
echo   1. 编辑 config\.env 文件配置您的参数
echo   2. 运行 Web 仪表板：python main.py web
echo   3. 或运行后台调度器：python main.py scheduler
echo.
pause
