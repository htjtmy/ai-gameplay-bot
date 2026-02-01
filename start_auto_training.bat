@echo off
REM 自动化训练快速启动脚本
REM 双击此文件即可启动训练流水线

echo ========================================
echo 自动化训练流水线启动
echo ========================================
echo.
echo 预计运行时间: 3-5小时
echo 日志保存位置: logs\
echo.
echo 流程: 数据增强 -^> 训练 -^> 评估 -^> 备份
echo.
pause

powershell -ExecutionPolicy Bypass -File "%~dp0start_auto_training.ps1"

pause
