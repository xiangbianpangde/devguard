@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在启动仪表盘服务并打开浏览器...
echo 关闭此窗口即停止服务。
python start_server.py
pause
