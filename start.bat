@echo off
echo 正在启动自动登录管理系统...

REM 检查Python版本
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

echo 检测到Python版本
python --version

REM 检查是否存在虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo 错误: 创建虚拟环境失败
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo 安装依赖包...
pip install -r requirements.txt

REM 初始化数据库
echo 初始化数据库...
python -c "from app import app, init_db; init_db()"

REM 创建日志目录
if not exist "logs" mkdir logs

REM 启动应用
echo 启动Flask应用...
echo 访问地址: http://localhost:5000
echo 按 Ctrl+C 停止服务

REM 设置环境变量
set FLASK_APP=app.py
set FLASK_ENV=development

REM 启动Flask应用
python app.py

pause