@echo off
chcp 65001 >nul
title 港口集装箱调度系统 - 停止服务
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "%~dp0stop.ps1"
