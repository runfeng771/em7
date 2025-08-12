from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
from flask_migrate import Migrate
from models import db, Account, EmailConfig, LoginLog, ScheduledTask
from config import Config
import requests
import base64
import ddddocr
import json
import time
import re
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timedelta
import os
import sys
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import threading
import atexit

app = Flask(__name__)
app.config.from_object(Config)

# 初始化数据库
db.init_app(app)
migrate = Migrate(app, db)

# 初始化OCR识别器
ocr = ddddocr.DdddOcr()

# 创建日志目录
if not os.path.exists(Config.LOG_DIR):
    os.makedirs(Config.LOG_DIR)

# 设置日志
def setup_logging():
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(Config.LOG_DIR, f"login_{today}.log")
    
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("AutoLogin")

logger = setup_logging()

# 固定公钥（用于第一次加密）
FIRST_PUBLIC_KEY = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDNR7I+SpqIZM5w3Aw4lrUlhrs7VurKbeViYXNhOfIgP/4acsWvJy5dPb/FejzUiv2cAiz5As2DJEQYEM10LvnmpnKx9Dq+QDo7WXnT6H2szRtX/8Q56Rlzp9bJMlZy7/i0xevlDrWZMWqx2IK3ZhO9+0nPu4z4SLXaoQGIrs7JxwIDAQAB"

# 自动登录类
class AutoLogin:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "Referer": "https://cms.ayybyyy.com/"
        }
        self.max_attempts = 5

    def get_token(self):
        url = "https://cmsapi3.qiucheng-wangluo.com/cms-api/token/generateCaptchaToken"
        try:
            response = self.session.post(url, headers=self.headers)
            if response.status_code == 200:
                result = response.json()
                if result.get("iErrCode") == 0:
                    return result.get("result")
            logger.error(f"获取token失败: {response.text}")
        except Exception as e:
            logger.error(f"获取token时发生异常: {str(e)}")
        return None

    def get_captcha(self, token):
        url = "https://cmsapi3.qiucheng-wangluo.com/cms-api/captcha"
        data = {"token": token}
        try:
            response = self.session.post(url, headers=self.headers, data=data)
            if response.status_code == 200:
                result = response.json()
                if result.get("iErrCode") == 0:
                    return result.get("result")
            logger.error(f"获取验证码失败: {response.text}")
        except Exception as e:
            logger.error(f"获取验证码时发生异常: {str(e)}")
        return None

    def recognize_captcha(self, captcha_base64):
        try:
            captcha_img = base64.b64decode(captcha_base64)
            captcha_text = ocr.classification(captcha_img)
            captcha_text = re.sub(r'[^a-zA-Z0-9]', '', captcha_text)
            if len(captcha_text) > 4:
                captcha_text = captcha_text[:4]
            return captcha_text.upper()
        except Exception as e:
            logger.error(f"识别验证码时发生异常: {str(e)}")
            return None

    def load_public_key(self, key_str):
        try:
            if "-----BEGIN" in key_str:
                return serialization.load_pem_public_key(key_str.encode(), backend=default_backend())
            else:
                try:
                    der_data = base64.b64decode(key_str)
                    return serialization.load_der_public_key(der_data, backend=default_backend())
                except:
                    hex_str = re.sub(r'\s+', '', key_str)
                    if len(hex_str) % 2 != 0:
                        hex_str = '0' + hex_str
                    der_data = bytes.fromhex(hex_str)
                    return serialization.load_der_public_key(der_data, backend=default_backend())
        except Exception as e:
            logger.error(f"加载公钥时发生异常: {str(e)}")
            return None

    def rsa_encrypt_long(self, text, public_key_str):
        try:
            public_key = self.load_public_key(public_key_str)
            if not public_key:
                return None
            
            key_size = public_key.key_size // 8
            max_block_size = key_size - 11
            
            encrypted_blocks = []
            for i in range(0, len(text), max_block_size):
                block = text[i:i + max_block_size]
                encrypted_block = public_key.encrypt(
                    block.encode('utf-8'),
                    padding.PKCS1v15()
                )
                encrypted_blocks.append(encrypted_block)
            
            encrypted_data = b''.join(encrypted_blocks)
            return base64.b64encode(encrypted_data).decode('utf-8')
        except Exception as e:
            logger.error(f"RSA长文本加密时发生异常: {str(e)}")
            return None

    def login(self, account, password, captcha, token, account_name="未知账号"):
        url = "https://cmsapi3.qiucheng-wangluo.com/cms-api/login"
        
        first_encrypted_password = self.rsa_encrypt_long(password, FIRST_PUBLIC_KEY)
        if not first_encrypted_password:
            return None
        
        second_encrypted_password = self.rsa_encrypt_long(first_encrypted_password, token)
        if not second_encrypted_password:
            return None
        
        encrypted_account = self.rsa_encrypt_long(account, token)
        if not encrypted_account:
            return None
        
        data = {
            "account": encrypted_account,
            "data": second_encrypted_password,
            "safeCode": captcha,
            "token": token,
            "locale": "zh"
        }
        
        try:
            response = self.session.post(url, headers=self.headers, data=data)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"登录时发生异常: {str(e)}")
        return None

    def get_club_list(self, token, account_name="未知账号"):
        url = "https://cmsapi3.qiucheng-wangluo.com/cms-api/club/getClubList"
        headers = {
            "accept": "application/json, text/javascript",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"",
            "sec-ch-ua-mobile": "?0",
            "token": token,
            "referrer": "https://cms.ayybyyy.com/"
        }
        
        try:
            response = requests.post(url, headers=headers)
            if response.status_code == 200:
                result = response.json()
                if result.get("iErrCode") == 0:
                    club_data = result.get("result")
                    if isinstance(club_data, list) and len(club_data) > 0:
                        club_info = club_data[0]
                        logger.info(f"[{account_name}] 俱乐部信息: {club_info}")
                        return club_info
                    elif isinstance(club_data, dict):
                        logger.info(f"[{account_name}] 俱乐部信息: {club_data}")
                        return club_data
        except Exception as e:
            logger.error(f"获取俱乐部列表时发生异常: {str(e)}")
        return None

    def login_account(self, account_info):
        account_name = account_info.get("name", "未知账号")
        account = account_info["account"]
        password = account_info["password"]
        
        logger.info(f"开始为账号 [{account_name}] 执行自动登录流程...")
        
        for attempt in range(1, self.max_attempts + 1):
            logger.info(f"尝试第 {attempt} 次登录 [{account_name}]...")
            
            token = self.get_token()
            if not token:
                time.sleep(2)
                continue
            
            captcha_base64 = self.get_captcha(token)
            if not captcha_base64:
                time.sleep(2)
                continue
            
            captcha_text = self.recognize_captcha(captcha_base64)
            if not captcha_text or len(captcha_text) != 4:
                time.sleep(2)
                continue
            
            login_result = self.login(account, password, captcha_text, token, account_name)
            
            if login_result:
                if login_result.get("iErrCode") == 0:
                    logger.info(f"[{account_name}] 登录成功!")
                    
                    # 记录登录成功日志
                    log_entry = LoginLog(
                        account_id=account_info.get('id'),
                        status='success',
                        message='登录成功',
                        details=json.dumps(login_result, ensure_ascii=False)
                    )
                    db.session.add(log_entry)
                    db.session.commit()
                    
                    # 获取俱乐部列表
                    club_info = self.get_club_list(token, account_name)
                    if club_info:
                        logger.info(f"[{account_name}] 获取俱乐部列表成功")
                    
                    return True
                else:
                    error_msg = login_result.get("sErrMsg", "未知错误")
                    logger.error(f"[{account_name}] 登录失败: {error_msg}")
                    
                    # 记录登录失败日志
                    log_entry = LoginLog(
                        account_id=account_info.get('id'),
                        status='failed',
                        message=error_msg,
                        details=json.dumps(login_result, ensure_ascii=False)
                    )
                    db.session.add(log_entry)
                    db.session.commit()
                    
                    if "验证码" in error_msg:
                        time.sleep(1)
                        continue
            
            if attempt < self.max_attempts:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
        
        logger.error(f"[{account_name}] 已达到最大尝试次数 {self.max_attempts}，登录失败")
        return False

    def run_all_accounts(self):
        accounts = Account.query.filter_by(is_active=True).all()
        success_count = 0
        
        for account in accounts:
            account_info = {
                'id': account.id,
                'account': account.account,
                'password': account.password,
                'name': account.name
            }
            
            if self.login_account(account_info):
                success_count += 1
            time.sleep(3)
        
        logger.info(f"自动登录流程完成，成功: {success_count}/{len(accounts)}")
        
        # 发送日志邮件
        self.send_log_email()
        
        return success_count, len(accounts)

    def send_log_email(self):
        try:
            email_config = EmailConfig.query.filter_by(is_active=True).first()
            if not email_config:
                logger.warning("未找到有效的邮件配置")
                return False
            
            today = datetime.now().strftime("%Y-%m-%d")
            log_file = os.path.join(Config.LOG_DIR, f"login_{today}.log")
            
            if not os.path.exists(log_file):
                logger.warning("日志文件不存在，无法发送邮件")
                return False
            
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            if not log_content.strip():
                logger.info("日志内容为空，不发送邮件")
                return False
            
            subject = f"自动登录日志 - {today}"
            message = MIMEText(log_content, 'plain', 'utf-8')
            message['From'] = Header(email_config.sender_email)
            message['To'] = Header(email_config.receiver_email)
            message['Subject'] = Header(subject, 'utf-8')
            
            with smtplib.SMTP_SSL(
                email_config.smtp_server,
                email_config.smtp_port
            ) as server:
                server.login(
                    email_config.sender_email,
                    email_config.sender_password
                )
                server.sendmail(
                    email_config.sender_email,
                    [email_config.receiver_email],
                    message.as_string()
                )
            
            logger.info(f"日志邮件已成功发送到 {email_config.receiver_email}")
            return True
        except Exception as e:
            logger.error(f"发送邮件时发生错误: {str(e)}")
            return False

# 创建自动登录实例
auto_login = AutoLogin()

# 定时任务调度器
scheduler = BackgroundScheduler()
scheduler.start()

# 添加定时任务
def add_scheduled_tasks():
    # 每天早上9:30执行登录
    scheduler.add_job(
        func=auto_login.run_all_accounts,
        trigger=CronTrigger(hour=9, minute=30),
        id='daily_login_9_30',
        name='每日登录任务(9:30)',
        replace_existing=True
    )
    
    # 每天中午11:50执行登录
    scheduler.add_job(
        func=auto_login.run_all_accounts,
        trigger=CronTrigger(hour=11, minute=50),
        id='daily_login_11_50',
        name='每日登录任务(11:50)',
        replace_existing=True
    )

# 初始化数据库
def init_db():
    with app.app_context():
        db.create_all()
        
        # 检查是否有默认账号
        if Account.query.count() == 0:
            default_account = Account(
                account="tbh2356@126.com",
                password="112233qq",
                name="tbh2356@126.com"
            )
            db.session.add(default_account)
        
        # 检查是否有默认邮件配置
        if EmailConfig.query.count() == 0:
            default_email = EmailConfig(
                smtp_server="smtp.email.cn",
                smtp_port=465,
                sender_email="18@HH.email.cn",
                sender_password="yuHKfnKvCqmw6HNN",
                receiver_email="Steven@HH.email.cn"
            )
            db.session.add(default_email)
        
        db.session.commit()
        logger.info("数据库初始化完成")

# 路由定义
@app.route('/')
def index():
    accounts = Account.query.all()
    email_configs = EmailConfig.query.all()
    return render_template('index.html', accounts=accounts, email_configs=email_configs)

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    accounts = Account.query.all()
    return jsonify([account.to_dict() for account in accounts])

@app.route('/api/accounts', methods=['POST'])
def add_account():
    data = request.json
    account = Account(
        account=data['account'],
        password=data['password'],
        name=data['name'],
        is_active=data.get('is_active', True)
    )
    db.session.add(account)
    db.session.commit()
    return jsonify(account.to_dict())

@app.route('/api/accounts/<int:account_id>', methods=['PUT'])
def update_account(account_id):
    account = Account.query.get_or_404(account_id)
    data = request.json
    account.account = data.get('account', account.account)
    account.password = data.get('password', account.password)
    account.name = data.get('name', account.name)
    account.is_active = data.get('is_active', account.is_active)
    db.session.commit()
    return jsonify(account.to_dict())

@app.route('/api/accounts/<int:account_id>', methods=['DELETE'])
def delete_account(account_id):
    account = Account.query.get_or_404(account_id)
    db.session.delete(account)
    db.session.commit()
    return jsonify({'message': '账号删除成功'})

@app.route('/api/login/<int:account_id>', methods=['POST'])
def manual_login(account_id):
    account = Account.query.get_or_404(account_id)
    account_info = {
        'id': account.id,
        'account': account.account,
        'password': account.password,
        'name': account.name
    }
    
    # 在新线程中执行登录，避免阻塞
    def login_thread():
        auto_login.login_account(account_info)
    
    thread = threading.Thread(target=login_thread)
    thread.start()
    
    return jsonify({'message': f'正在为账号 [{account.name}] 执行登录...'})

@app.route('/api/login/all', methods=['POST'])
def login_all_accounts():
    # 在新线程中执行登录，避免阻塞
    def login_thread():
        auto_login.run_all_accounts()
    
    thread = threading.Thread(target=login_thread)
    thread.start()
    
    return jsonify({'message': '正在为所有账号执行登录...'})

@app.route('/api/logs', methods=['GET'])
def get_logs():
    date_filter = request.args.get('date')
    account_filter = request.args.get('account_id')
    status_filter = request.args.get('status')
    
    query = LoginLog.query
    
    if date_filter:
        start_date = datetime.strptime(date_filter, '%Y-%m-%d')
        end_date = start_date + timedelta(days=1)
        query = query.filter(LoginLog.created_at >= start_date, LoginLog.created_at < end_date)
    
    if account_filter:
        query = query.filter(LoginLog.account_id == account_filter)
    
    if status_filter:
        query = query.filter(LoginLog.status == status_filter)
    
    logs = query.order_by(LoginLog.created_at.desc()).limit(100).all()
    return jsonify([log.to_dict() for log in logs])

@app.route('/api/logs/clear', methods=['POST'])
def clear_logs():
    date_filter = request.json.get('date')
    
    query = LoginLog.query
    
    if date_filter:
        start_date = datetime.strptime(date_filter, '%Y-%m-%d')
        end_date = start_date + timedelta(days=1)
        query = query.filter(LoginLog.created_at >= start_date, LoginLog.created_at < end_date)
    
    count = query.count()
    query.delete()
    db.session.commit()
    
    return jsonify({'message': f'已清除 {count} 条日志记录'})

@app.route('/api/email_configs', methods=['GET'])
def get_email_configs():
    configs = EmailConfig.query.all()
    return jsonify([config.to_dict() for config in configs])

@app.route('/api/email_configs', methods=['POST'])
def add_email_config():
    data = request.json
    config = EmailConfig(
        smtp_server=data['smtp_server'],
        smtp_port=data['smtp_port'],
        sender_email=data['sender_email'],
        sender_password=data['sender_password'],
        receiver_email=data['receiver_email'],
        is_active=data.get('is_active', True)
    )
    db.session.add(config)
    db.session.commit()
    return jsonify(config.to_dict())

@app.route('/api/email_configs/<int:config_id>', methods=['PUT'])
def update_email_config(config_id):
    config = EmailConfig.query.get_or_404(config_id)
    data = request.json
    config.smtp_server = data.get('smtp_server', config.smtp_server)
    config.smtp_port = data.get('smtp_port', config.smtp_port)
    config.sender_email = data.get('sender_email', config.sender_email)
    config.sender_password = data.get('sender_password', config.sender_password)
    config.receiver_email = data.get('receiver_email', config.receiver_email)
    config.is_active = data.get('is_active', config.is_active)
    db.session.commit()
    return jsonify(config.to_dict())

@app.route('/api/email_configs/<int:config_id>', methods=['DELETE'])
def delete_email_config(config_id):
    config = EmailConfig.query.get_or_404(config_id)
    db.session.delete(config)
    db.session.commit()
    return jsonify({'message': '邮件配置删除成功'})

@app.route('/api/scheduler/status', methods=['GET'])
def get_scheduler_status():
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            'id': job.id,
            'name': job.name,
            'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
            'trigger': str(job.trigger)
        })
    return jsonify({'jobs': jobs, 'running': scheduler.running})

@app.route('/api/scheduler/run', methods=['POST'])
def run_scheduler_job():
    auto_login.run_all_accounts()
    return jsonify({'message': '定时任务执行完成'})

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'timestamp': datetime.utcnow().isoformat()})

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# 应用关闭时清理
atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    init_db()
    add_scheduled_tasks()
    app.run(host='0.0.0.0', port=10000, debug=True)
