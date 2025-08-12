#!/bin/bash

# 自动登录管理系统启动脚本

echo "正在启动自动登录管理系统..."

# 检查Python版本
python_version=$(python3 --version 2>&1)
if [[ $? -ne 0 ]]; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

echo "检测到Python版本: $python_version"

# 检查是否存在虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
    if [[ $? -ne 0 ]]; then
        echo "错误: 创建虚拟环境失败"
        exit 1
    fi
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装依赖包..."
pip install -r requirements.txt

# 初始化数据库
echo "初始化数据库..."
python3 -c "from app import app, init_db; init_db()"

# 创建日志目录
mkdir -p logs

# 启动应用
echo "启动Flask应用..."
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务"

# 设置环境变量
export FLASK_APP=app.py
export FLASK_ENV=development

# 启动Flask应用
python3 app.py