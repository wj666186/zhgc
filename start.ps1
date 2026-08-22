# ============================================================
# 港口集装箱调度与物流协作系统 - 一键启动脚本
# 启动顺序：AI服务(5000) -> 后端SpringBoot(8080) -> 前端Vue(5173)
# ============================================================

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  港口集装箱调度与物流协作系统" -ForegroundColor Cyan
Write-Host "  一键启动" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ---------- 工具检查 ----------
function Check-Tool {
    param($name, $cmd)
    $tool = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($tool) {
        Write-Host "  [OK] $name" -ForegroundColor Green
        return $true
    } else {
        Write-Host "  [缺失] $name (请先安装)" -ForegroundColor Red
        return $false
    }
}

Write-Host "[1/4] 环境检查..." -ForegroundColor Yellow
$hasJava = Check-Tool "Java" "java"
$hasNode = Check-Tool "Node.js" "node"
$hasPython = Check-Tool "Python" "python"
Write-Host ""

if (-not $hasJava) {
    Write-Host "错误：未检测到 Java，无法启动后端" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}
if (-not $hasNode) {
    Write-Host "错误：未检测到 Node.js，无法启动前端" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

# ---------- Java 17 检测与切换（Spring Boot 3.x 需要 Java 17+）----------
function Find-Java17 {
    $searchPaths = @(
        "$env:USERPROFILE\.jdks",
        "C:\Program Files\Java",
        "C:\Program Files\Eclipse Adoptium",
        "C:\Program Files\Microsoft",
        "C:\Program Files\Zulu",
        "C:\Java"
    )
    foreach ($base in $searchPaths) {
        if (-not (Test-Path $base)) { continue }
        $jdks = Get-ChildItem $base -Directory -ErrorAction SilentlyContinue | Where-Object {
            $_.Name -match "17|jdk-17|jdk17|21|jdk-21"
        }
        foreach ($jdk in $jdks) {
            $javaExe = Join-Path $jdk.FullName "bin\java.exe"
            if (Test-Path $javaExe) {
                return $jdk.FullName
            }
        }
    }
    return $null
}

$oldEAP = $ErrorActionPreference
$ErrorActionPreference = "Continue"
$javaVer = (& java -version 2>&1 | Select-Object -First 1) -replace '.*version "([^"]+)".*', '$1'
$ErrorActionPreference = $oldEAP
$javaMajor = ($javaVer -split '\.')[0]
if ($javaMajor -lt 17) {
    Write-Host "  当前 Java 版本: $javaVer（Spring Boot 3.x 需要 Java 17+）" -ForegroundColor Yellow
    $java17Path = Find-Java17
    if ($java17Path) {
        Write-Host "  找到 Java 17: $java17Path" -ForegroundColor Green
        $env:JAVA_HOME = $java17Path
        $env:PATH = "$java17Path\bin;$env:PATH"
        $ErrorActionPreference = "Continue"
        $newVer = (& java -version 2>&1 | Select-Object -First 1) -replace '.*version "([^"]+)".*', '$1'
        $ErrorActionPreference = $oldEAP
        Write-Host "  已切换到 Java: $newVer" -ForegroundColor Green
    } else {
        Write-Host "  错误：未找到 Java 17+，请安装 JDK 17 或更高版本" -ForegroundColor Red
        Write-Host "  下载地址: https://adoptium.net/" -ForegroundColor Yellow
        Read-Host "按回车键退出"
        exit 1
    }
} else {
    Write-Host "  Java 版本: $javaVer ✅" -ForegroundColor Green
}
Write-Host ""

# ---------- 端口检查 ----------
function Test-Port {
    param($port)
    $conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    return ($null -ne $conn)
}

$ports = @{6379="Redis"; 5000="AI服务"; 8080="后端"; 5173="前端"}
$portConflict = $false
foreach ($p in $ports.Keys) {
    if (Test-Port $p) {
        Write-Host "  [警告] 端口 $p ($($ports[$p])) 已被占用" -ForegroundColor Yellow
        $portConflict = $true
    }
}
if ($portConflict) {
    Write-Host ""
    $kill = Read-Host "端口被占用，是否终止占用进程？(y/N)"
    if ($kill -eq 'y' -or $kill -eq 'Y') {
        foreach ($p in $ports.Keys) {
            $conns = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue
            foreach ($c in $conns) {
                try { Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue } catch {}
            }
        }
        Write-Host "  已终止占用进程" -ForegroundColor Green
        Start-Sleep -Seconds 2
    }
}
Write-Host ""

# ---------- 启动 Redis ----------
Write-Host "[2/5] 启动 Redis (端口 6379)..." -ForegroundColor Yellow
$redisPath = Join-Path $ProjectRoot "redis"
$redisExe = Join-Path $redisPath "redis-server.exe"
if (Test-Path $redisExe) {
    $redisBat = Join-Path $redisPath "start-redis.bat"
    & cmd /c start "Redis Server" "$redisBat"
    Start-Sleep -Seconds 3
    $redisReady = Get-NetTCPConnection -LocalPort 6379 -State Listen -ErrorAction SilentlyContinue
    if ($redisReady) {
        Write-Host "  Redis 已启动 ✅" -ForegroundColor Green
    } else {
        Write-Host "  Redis 启动中..." -ForegroundColor Yellow
    }
} else {
    Write-Host "  [警告] 未找到 redis-server.exe，后端可能无法启动" -ForegroundColor Red
}
Start-Sleep -Seconds 1

# ---------- 启动AI服务 ----------
Write-Host "[3/5] 启动 AI 服务 (端口 5000)..." -ForegroundColor Yellow
if ($hasPython) {
    $aiPath = Join-Path $ProjectRoot "ai-server"
    if (Test-Path $aiPath) {
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$aiPath'; python app.py" -WindowStyle Normal
        Write-Host "  AI 服务启动中..." -ForegroundColor Green
    } else {
        Write-Host "  [跳过] ai-server 目录不存在" -ForegroundColor DarkGray
    }
} else {
    Write-Host "  [跳过] 未检测到 Python" -ForegroundColor DarkGray
}
Start-Sleep -Seconds 3

# ---------- 启动后端 ----------
Write-Host "[4/5] 启动后端 Spring Boot (端口 8080)..." -ForegroundColor Yellow
$backendPath = Join-Path $ProjectRoot "port-schedule-server"
if (Test-Path $backendPath) {
    $mvnw = Join-Path $backendPath "mvnw.cmd"
    if (Test-Path $mvnw) {
        $backendCmd = "cd '$backendPath'; .\mvnw.cmd spring-boot:run"
    } else {
        $backendCmd = "cd '$backendPath'; mvn spring-boot:run"
    }
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal
    Write-Host "  后端启动中（首次启动需下载依赖，约1-3分钟）..." -ForegroundColor Green
} else {
    Write-Host "  [错误] port-schedule-server 目录不存在" -ForegroundColor Red
}
Start-Sleep -Seconds 5

# ---------- 启动前端 ----------
Write-Host "[5/5] 启动前端 Vue (端口 5173)..." -ForegroundColor Yellow
$frontendPath = Join-Path $ProjectRoot "port-web"
if (Test-Path $frontendPath) {
    $nodeModules = Join-Path $frontendPath "node_modules"
    if (-not (Test-Path $nodeModules)) {
        Write-Host "  首次启动，安装依赖中..." -ForegroundColor Yellow
        Set-Location $frontendPath
        npm install
        Set-Location $ProjectRoot
    }
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; npm run dev" -WindowStyle Normal
    Write-Host "  前端启动中..." -ForegroundColor Green
} else {
    Write-Host "  [错误] port-web 目录不存在" -ForegroundColor Red
}

# ---------- 等待并打开浏览器 ----------
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  服务启动中，请等待..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$maxWait = 120
$waited = 0
while ($waited -lt $maxWait) {
    Start-Sleep -Seconds 5
    $waited += 5
    $backendReady = Test-Port 8080
    $frontendReady = Test-Port 5173
    if ($backendReady -and $frontendReady) {
        Write-Host ""
        Write-Host "  后端就绪: http://localhost:8080" -ForegroundColor Green
        Write-Host "  前端就绪: http://localhost:5173" -ForegroundColor Green
        Write-Host "  AI服务:  http://localhost:5000/health" -ForegroundColor Green
        Write-Host ""
        Write-Host "  正在打开浏览器..." -ForegroundColor Cyan
        Start-Process "http://localhost:5173"
        break
    }
    if ($waited % 15 -eq 0) {
        Write-Host "  已等待 ${waited}s... 后端:$($backendReady) 前端:$($frontendReady)" -ForegroundColor DarkGray
    }
}

if ($waited -ge $maxWait) {
    Write-Host ""
    Write-Host "  启动超时，请手动检查各服务窗口的日志输出" -ForegroundColor Yellow
    Write-Host "  前端地址: http://localhost:5173" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "  测试账号：admin / 123456（管理员）" -ForegroundColor White
Write-Host "             operator / 123456（调度员）" -ForegroundColor White
Write-Host ""
Write-Host "  关闭本窗口不会停止服务，请在各服务窗口按 Ctrl+C 停止" -ForegroundColor DarkGray
Write-Host ""
Read-Host "按回车键关闭本窗口"
