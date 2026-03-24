@echo off
REM 12321 投诉量监控 - 任务计划启动脚本
REM 自动启动并静默运行 scheduler.py，窗口自动隐藏

chcp 65001 >nul
cd /d "%~dp0"

REM 检查 Python 是否在 PATH 中，若不在则使用完整路径（需根据实际情况修改）
python scheduler.py

pause
