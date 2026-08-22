# ============================================================
# 港口集装箱调度系统 - 一键停止脚本
# 停止 AI服务(5000)、后端(8080)、前端(5173) 相关进程
# ============================================================

$ErrorActionPreference = "SilentlyContinue"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  停止港口集装箱调度系统所有服务" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ports = @(5000, 8080, 5173)
$stopped = 0

foreach ($port in $ports) {
    $conns = Get-NetTCPConnection -LocalPort $port -State Listen
    if ($conns) {
        foreach ($conn in $conns) {
            $proc = Get-Process -Id $conn.OwningProcess
            if ($proc) {
                Write-Host "  停止端口 $port (PID $($conn.OwningProcess) - $($proc.ProcessName))..." -ForegroundColor Yellow
                Stop-Process -Id $conn.OwningProcess -Force
                $stopped++
            }
        }
    } else {
        Write-Host "  端口 $port 未运行" -ForegroundColor DarkGray
    }
}

# 额外停止可能残留的 java/node/python 进程（可选）
Write-Host ""
$cleanup = Read-Host "是否同时终止所有 java/node/python 进程？(y/N)"
if ($cleanup -eq 'y' -or $cleanup -eq 'Y') {
    Get-Process java -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
    Write-Host "  已终止所有 java/node/python 进程" -ForegroundColor Green
}

Write-Host ""
Write-Host "  共停止 $stopped 个服务进程" -ForegroundColor Green
Write-Host ""
Start-Sleep -Seconds 2
