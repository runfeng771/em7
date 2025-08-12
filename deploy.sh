#!/bin/bash

# Render部署脚本

echo "=== 自动登录管理系统部署脚本 ==="
echo

# 检查Git是否初始化
if [ ! -d ".git" ]; then
    echo "初始化Git仓库..."
    git init
    git add .
    git commit -m "Initial commit"
fi

# 检查是否已安装Render CLI
if ! command -v render &> /dev/null; then
    echo "Render CLI未安装，请先安装:"
    echo "npm install -g @render/cli"
    exit 1
fi

# 检查是否已登录Render
echo "检查Render登录状态..."
render whoami || {
    echo "请先登录Render:"
    echo "render login"
    exit 1
}

# 创建Web服务
echo "创建Render Web服务..."
render create web service --name auto-login-system --type python --region oregon

# 设置环境变量
echo "设置环境变量..."
render env set FLASK_APP=app.py
render env set FLASK_ENV=production
render env set SECRET_KEY=your-secret-key-here-$(date +%s)
render env set DATABASE_URL=sqlite:///auto_login.db

# 部署
echo "部署到Render..."
render deploy

echo
echo "部署完成！"
echo "请访问Render控制台查看应用状态和URL。"
echo
echo "注意事项:"
echo "1. 首次部署可能需要几分钟时间"
echo "2. 请在Render控制台中检查日志"
echo "3. 确保所有依赖都正确安装"
echo "4. 如有问题，请查看Render的构建日志"