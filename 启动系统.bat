@echo off
chcp 65001 >nul
title 港口集装箱调度系统 - 一键启动
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "%~dp0start.ps1"
if errorlevel 1 (
    echo.
    echo 启动过程中出现错误，请查看上方信息
    pause
)
