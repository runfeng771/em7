# 项目结构说明

```
flask_app/
├── app.py                    # Flask主应用文件
├── config.py                 # 配置文件
├── models.py                 # 数据库模型
├── requirements.txt          # Python依赖包列表
├── runtime.txt              # Python版本指定（用于Render）
├── Procfile                 # Render部署配置
├── Dockerfile               # Docker构建文件
├── docker-compose.yml       # Docker Compose配置
├── test.py                  # 测试脚本
├── README.md                # 项目说明文档
├── start.sh                 # Linux/Mac启动脚本
├── start.bat                # Windows启动脚本
├── deploy.sh                # Render部署脚本
├── project_structure.md     # 项目结构说明（本文件）
│
├── templates/               # HTML模板目录
│   ├── layout.html          # 基础模板
│   └── index.html           # 主页面模板
│
├── static/                  # 静态文件目录
│   ├── css/                 # CSS样式文件
│   │   └── style.css        # 主样式文件
│   └── js/                  # JavaScript文件
│       └── app.js           # 主JavaScript文件
│
├── logs/                    # 日志文件目录（运行时创建）
└── auto_login.db            # SQLite数据库文件（运行时创建）
```

## 文件说明

### 核心文件

- **app.py**: Flask应用的主文件，包含所有路由和业务逻辑
- **config.py**: 应用配置文件，包含数据库、邮件、日志等配置
- **models.py**: 数据库模型定义，包含账号、邮件配置、日志等模型
- **requirements.txt**: Python依赖包列表，用于pip安装

### 部署文件

- **runtime.txt**: 指定Python版本（用于Render部署）
- **Procfile**: Render部署配置文件，指定启动命令
- **Dockerfile**: Docker构建文件，用于容器化部署
- **docker-compose.yml**: Docker Compose配置文件，用于本地Docker开发
- **deploy.sh**: Render部署脚本

### 启动脚本

- **start.sh**: Linux/Mac系统启动脚本
- **start.bat**: Windows系统启动脚本
- **test.py**: 测试脚本，用于验证系统功能

### 前端文件

- **templates/layout.html**: 基础HTML模板，包含导航栏和公共元素
- **templates/index.html**: 主页面模板，包含所有功能界面
- **static/css/style.css**: 主样式文件，包含所有CSS样式
- **static/js/app.js**: 主JavaScript文件，包含所有前端逻辑

### 运行时文件

- **logs/**: 日志文件目录，存储每日登录日志
- **auto_login.db**: SQLite数据库文件，存储所有数据

## 功能模块

### 1. 账号管理模块
- 文件: `app.py` (Account相关路由)
- 模型: `models.py` (Account类)
- 界面: `templates/index.html` (账号管理部分)
- 功能: 添加、编辑、删除、启用/禁用账号

### 2. 自动登录模块
- 文件: `app.py` (AutoLogin类)
- 功能: 验证码识别、RSA加密、登录请求、获取俱乐部列表
- 支持: 单账号登录、批量登录、定时登录

### 3. 日志管理模块
- 文件: `app.py` (日志相关路由)
- 模型: `models.py` (LoginLog类)
- 界面: `templates/index.html` (日志查看部分)
- 功能: 日志记录、筛选、查看、清空

### 4. 邮件配置模块
- 文件: `app.py` (邮件配置相关路由)
- 模型: `models.py` (EmailConfig类)
- 界面: `templates/index.html` (邮件配置部分)
- 功能: 邮件服务器配置、日志邮件发送

### 5. 定时任务模块
- 文件: `app.py` (APScheduler相关代码)
- 功能: 定时自动登录、任务状态监控
- 默认: 每天9:30和11:50执行

### 6. 前端界面模块
- 文件: `templates/` 和 `static/`
- 功能: 响应式设计、实时更新、用户交互
- 特性: 现代化UI、移动端适配、自动刷新

## 数据库结构

### Account表 (账号表)
- id: 主键
- account: 登录账号
- password: 登录密码
- name: 账号名称
- is_active: 是否启用
- created_at: 创建时间
- updated_at: 更新时间

### EmailConfig表 (邮件配置表)
- id: 主键
- smtp_server: SMTP服务器
- smtp_port: SMTP端口
- sender_email: 发件人邮箱
- sender_password: 发件人密码
- receiver_email: 收件人邮箱
- is_active: 是否启用
- created_at: 创建时间
- updated_at: 更新时间

### LoginLog表 (登录日志表)
- id: 主键
- account_id: 账号ID (外键)
- status: 登录状态 (success/failed)
- message: 日志消息
- details: 详细信息 (JSON)
- created_at: 创建时间

### ScheduledTask表 (定时任务表)
- id: 主键
- name: 任务名称
- description: 任务描述
- cron_expression: Cron表达式
- is_active: 是否启用
- last_run: 上次运行时间
- next_run: 下次运行时间
- created_at: 创建时间
- updated_at: 更新时间

## API接口

### 账号管理API
- `GET /api/accounts` - 获取所有账号
- `POST /api/accounts` - 添加账号
- `PUT /api/accounts/<id>` - 更新账号
- `DELETE /api/accounts/<id>` - 删除账号

### 登录操作API
- `POST /api/login/<id>` - 手动登录指定账号
- `POST /api/login/all` - 登录所有账号

### 日志管理API
- `GET /api/logs` - 获取日志 (支持筛选)
- `POST /api/logs/clear` - 清空日志

### 邮件配置API
- `GET /api/email_configs` - 获取邮件配置
- `POST /api/email_configs` - 添加邮件配置
- `PUT /api/email_configs/<id>` - 更新邮件配置
- `DELETE /api/email_configs/<id>` - 删除邮件配置

### 定时任务API
- `GET /api/scheduler/status` - 获取定时任务状态
- `POST /api/scheduler/run` - 手动执行定时任务

### 系统API
- `GET /api/health` - 健康检查
- `GET /static/<path>` - 静态文件

## 部署方式

### 1. 本地部署
```bash
# Linux/Mac
./start.sh

# Windows
start.bat
```

### 2. Docker部署
```bash
# 构建并运行
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 3. Render部署
```bash
# 使用部署脚本
./deploy.sh

# 或手动部署到Render
git push render main
```

## 配置说明

### 环境变量
- `FLASK_APP`: Flask应用文件名
- `FLASK_ENV`: 运行环境 (development/production)
- `SECRET_KEY`: 应用密钥
- `DATABASE_URL`: 数据库连接字符串
- `MAIL_SERVER`: SMTP服务器
- `MAIL_PORT`: SMTP端口
- `MAIL_USERNAME`: 邮件用户名
- `MAIL_PASSWORD`: 邮件密码

### 默认配置
- 默认账号: tbh2356@126.com / 112233qq
- 默认邮件: 18@HH.email.cn -> Steven@HH.email.cn
- 定时任务: 每天9:30和11:50
- 自动刷新: 20秒
- 防闲置检查: 20秒

## 注意事项

1. **安全性**: 生产环境请修改默认SECRET_KEY
2. **数据库**: 首次运行会自动创建数据库和表
3. **日志**: 日志文件按日期分割，存储在logs目录
4. **端口**: 默认使用5000端口
5. **依赖**: 确保所有Python依赖正确安装
6. **OCR**: ddddocr需要系统支持，可能需要额外安装依赖

## 开发说明

### 添加新功能
1. 修改数据库模型 (`models.py`)
2. 添加后端路由 (`app.py`)
3. 更新前端界面 (`templates/` 和 `static/`)
4. 更新API文档
5. 测试功能

### 调试模式
```bash
export FLASK_ENV=development
python app.py
```

### 日志级别
- DEBUG: 详细调试信息
- INFO: 一般信息
- WARNING: 警告信息
- ERROR: 错误信息

## 常见问题

1. **端口占用**: 修改app.py中的端口号
2. **依赖问题**: 使用虚拟环境安装依赖
3. **数据库问题**: 删除auto_login.db重新初始化
4. **OCR问题**: 确保系统支持ddddocr
5. **邮件问题**: 检查SMTP配置和网络连接