# 自动登录管理系统

一个基于Flask的自动登录管理系统，支持多账号管理、定时登录、日志查看等功能。

## 功能特性

- 🚀 **多账号管理**: 添加、编辑、删除多个登录账号
- 🔐 **自动登录**: 支持手动单账号登录和批量登录
- 📊 **日志系统**: 实时查看登录日志，支持筛选和自动刷新
- 📧 **邮件通知**: 登录结果自动发送到指定邮箱
- ⏰ **定时任务**: 支持定时自动登录（每天9:30和11:50）
- 🎨 **美观界面**: 现代化的响应式设计，支持移动端
- 🔄 **防闲置**: 每20秒自动发送健康检查，防止服务器休眠

## 技术栈

- **后端**: Flask, SQLAlchemy, APScheduler
- **前端**: Bootstrap 5, jQuery, Font Awesome
- **OCR识别**: ddddocr
- **加密**: cryptography
- **数据库**: SQLite

## 快速开始

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd flask_app
```

### 2. 运行启动脚本

```bash
chmod +x start.sh
./start.sh
```

### 3. 访问应用

打开浏览器访问: http://localhost:5000

## 手动安装

### 1. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 初始化数据库

```bash
python3 -c "from app import app, init_db; init_db()"
```

### 4. 启动应用

```bash
python3 app.py
```

## 使用说明

### 账号管理

1. **添加账号**: 点击"添加账号"按钮，填写账号信息
2. **编辑账号**: 点击账号右侧的编辑按钮
3. **删除账号**: 点击账号右侧的删除按钮
4. **手动登录**: 点击账号右侧的登录按钮

### 日志查看

1. **筛选日志**: 可按日期、账号、状态筛选
2. **自动刷新**: 支持5秒、10秒、20秒、30秒自动刷新
3. **清空日志**: 可按日期清空日志或全部清空

### 邮件配置

1. **添加配置**: 点击"添加邮件配置"按钮
2. **SMTP设置**: 填写SMTP服务器、端口、发件人信息
3. **收件人设置**: 设置接收日志的邮箱地址

### 定时任务

系统默认配置了两个定时任务：
- 每天9:30自动执行登录
- 每天11:50自动执行登录

可以手动执行定时任务或查看任务状态。

## 部署到Render

### 1. 准备项目

确保项目包含以下文件：
- `app.py` - 主应用文件
- `requirements.txt` - 依赖文件
- `config.py` - 配置文件
- `templates/` - 模板目录
- `static/` - 静态文件目录

### 2. 创建Render服务

1. 登录 [Render](https://render.com)
2. 创建新的Web Service
3. 选择Python环境
4. 连接GitHub仓库
5. 配置环境变量（可选）

### 3. 环境变量配置

在Render的Environment选项卡中添加以下环境变量：

```bash
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///auto_login.db
```

### 4. 启动命令

设置启动命令：
```bash
python app.py
```

## 默认配置

### 默认账号
- 账号: tbh2356@126.com
- 密码: 112233qq
- 名称: tbh2356@126.com

### 默认邮件配置
- SMTP服务器: smtp.email.cn
- 端口: 465
- 发件人: 18@HH.email.cn
- 收件人: Steven@HH.email.cn

## 目录结构

```
flask_app/
├── app.py                 # 主应用文件
├── config.py             # 配置文件
├── models.py             # 数据库模型
├── requirements.txt      # 依赖文件
├── start.sh             # 启动脚本
├── templates/           # HTML模板
│   ├── layout.html      # 基础模板
│   └── index.html       # 主页面
├── static/              # 静态文件
│   ├── css/
│   │   └── style.css    # 样式文件
│   └── js/
│       └── app.js       # JavaScript文件
├── logs/                # 日志目录
└── auto_login.db        # 数据库文件
```

## API接口

### 账号管理
- `GET /api/accounts` - 获取所有账号
- `POST /api/accounts` - 添加账号
- `PUT /api/accounts/<id>` - 更新账号
- `DELETE /api/accounts/<id>` - 删除账号

### 登录操作
- `POST /api/login/<id>` - 手动登录指定账号
- `POST /api/login/all` - 登录所有账号

### 日志管理
- `GET /api/logs` - 获取日志
- `POST /api/logs/clear` - 清空日志

### 邮件配置
- `GET /api/email_configs` - 获取邮件配置
- `POST /api/email_configs` - 添加邮件配置
- `PUT /api/email_configs/<id>` - 更新邮件配置
- `DELETE /api/email_configs/<id>` - 删除邮件配置

### 定时任务
- `GET /api/scheduler/status` - 获取定时任务状态
- `POST /api/scheduler/run` - 手动执行定时任务

### 健康检查
- `GET /api/health` - 健康检查

## 注意事项

1. **安全性**: 生产环境请修改默认的SECRET_KEY
2. **数据库**: 首次运行会自动创建数据库和表
3. **日志**: 日志文件保存在`logs`目录下
4. **端口**: 默认使用5000端口，可通过环境变量修改
5. **防闲置**: 每20秒自动发送健康检查请求

## 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   lsof -i :5000
   kill -9 <PID>
   ```

2. **依赖安装失败**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **数据库初始化失败**
   ```bash
   rm -f auto_login.db
   python3 -c "from app import app, init_db; init_db()"
   ```

4. **OCR识别失败**
   ```bash
   pip install --upgrade ddddocr
   ```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题请提交Issue或联系开发者。