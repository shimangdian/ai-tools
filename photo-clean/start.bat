@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Photo Clean 一键启动脚本 (Windows)

REM 设置项目配置
set "PROJECT_NAME=Photo Clean"
set "PROJECT_DIR=%~dp0"
set "COMPOSE_FILE=%PROJECT_DIR%docker-compose.yml"
set "DATA_DIR=%PROJECT_DIR%data"
set "ENV_FILE=%PROJECT_DIR%backend\.env"
set "ENV_EXAMPLE=%PROJECT_DIR%backend\.env.example"

REM 显示欢迎信息
cls
echo ==================================================
echo         %PROJECT_NAME% - 一键启动脚本
echo ==================================================
echo.

REM 检查 Docker 是否安装
echo [INFO] 检查 Docker 环境...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 未检测到 Docker，请先安装 Docker Desktop
    pause
    exit /b 1
)

docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker 未运行，请启动 Docker Desktop
    pause
    exit /b 1
)

echo [SUCCESS] Docker 环境检查通过
echo.

REM 检查 Docker Compose
echo [INFO] 检查 Docker Compose...
docker compose version >nul 2>&1
if errorlevel 1 (
    docker-compose version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] 未检测到 Docker Compose
        pause
        exit /b 1
    )
    set "DOCKER_COMPOSE=docker-compose"
) else (
    set "DOCKER_COMPOSE=docker compose"
)

echo [SUCCESS] Docker Compose 检查通过
echo.

REM 创建必要的目录
echo [INFO] 创建必要的目录...
if not exist "%DATA_DIR%\trash" mkdir "%DATA_DIR%\trash"
if not exist "%DATA_DIR%\db" mkdir "%DATA_DIR%\db"
echo [SUCCESS] 目录创建完成
echo.

REM 配置环境变量
echo [INFO] 检查环境配置...
if not exist "%ENV_FILE%" (
    if exist "%ENV_EXAMPLE%" (
        echo [WARNING] 未找到 .env 文件，正在从 .env.example 创建...
        copy "%ENV_EXAMPLE%" "%ENV_FILE%" >nul
        echo [SUCCESS] 环境配置文件已创建
        echo [WARNING] 请检查 backend\.env 文件并根据需要修改配置
    ) else (
        echo [ERROR] 未找到 .env.example 文件
        pause
        exit /b 1
    )
) else (
    echo [SUCCESS] 环境配置已存在
)
echo.

REM 检查是否存在运行中的容器
echo [INFO] 检查是否存在运行中的容器...
%DOCKER_COMPOSE% -f "%COMPOSE_FILE%" ps -q 2>nul | findstr "." >nul
if not errorlevel 1 (
    echo [WARNING] 发现运行中的容器，正在停止...
    %DOCKER_COMPOSE% -f "%COMPOSE_FILE%" down
    echo [SUCCESS] 旧容器已停止
) else (
    echo [INFO] 没有需要清理的容器
)
echo.

REM 构建并启动服务
echo ==================================================
echo [INFO] 开始构建并启动服务...
echo ==================================================
echo.

cd /d "%PROJECT_DIR%"

echo [INFO] 正在构建 Docker 镜像（首次运行可能需要较长时间）...
%DOCKER_COMPOSE% -f "%COMPOSE_FILE%" build

echo.
echo ==================================================
echo.

echo [INFO] 正在启动服务...
%DOCKER_COMPOSE% -f "%COMPOSE_FILE%" up -d

if errorlevel 1 (
    echo [ERROR] 服务启动失败
    pause
    exit /b 1
)

echo [SUCCESS] 服务启动成功
echo.

REM 等待服务就绪
echo [INFO] 等待服务就绪...
set /a count=0
:wait_loop
if !count! geq 60 goto wait_timeout

docker ps | findstr "photo-clean-backend" >nul 2>&1
if errorlevel 1 goto wait_next

docker ps | findstr "photo-clean-frontend" >nul 2>&1
if errorlevel 1 goto wait_next

REM 检查服务是否可访问
curl -s http://localhost:8080 >nul 2>&1
if not errorlevel 1 (
    echo.
    echo [SUCCESS] 服务已就绪
    goto wait_done
)

:wait_next
timeout /t 2 /nobreak >nul
set /a count+=2
echo|set /p="."
goto wait_loop

:wait_timeout
echo.
echo [WARNING] 服务启动超时，请检查容器日志

:wait_done
echo.

REM 显示服务状态
echo ==================================================
echo [INFO] 服务状态:
echo ==================================================
%DOCKER_COMPOSE% -f "%COMPOSE_FILE%" ps
echo.

REM 显示访问信息
echo ==================================================
echo 服务已成功启动！
echo ==================================================
echo.

REM 获取本机 IP
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set "LOCAL_IP=%%a"
    set "LOCAL_IP=!LOCAL_IP: =!"
    goto :ip_found
)
set "LOCAL_IP=your-ip"
:ip_found

echo 访问地址:
echo   本地访问: http://localhost:8080
echo   网络访问: http://!LOCAL_IP!:8080
echo.
echo 常用命令:
echo   查看日志: docker-compose logs -f
echo   停止服务: docker-compose down
echo   重启服务: docker-compose restart
echo   查看状态: docker-compose ps
echo.
echo 数据目录:
echo   回收站: %DATA_DIR%\trash
echo   数据库: %DATA_DIR%\db
echo.
echo ==================================================
echo.

pause
