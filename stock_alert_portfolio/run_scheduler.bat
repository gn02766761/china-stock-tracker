@echo off
echo ========================================
echo 启动股票预警后台调度器
echo ========================================
echo.
echo 正在启动预警监控...
echo 按 Ctrl+C 停止
echo.
python main.py scheduler
pause
