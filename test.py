#!/usr/bin/env python3
"""
自动登录管理系统测试脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试导入依赖"""
    try:
        print("测试导入依赖...")
        
        # 测试Flask
        from flask import Flask
        print("✓ Flask 导入成功")
        
        # 测试SQLAlchemy
        from flask_sqlalchemy import SQLAlchemy
        print("✓ SQLAlchemy 导入成功")
        
        # 测试requests
        import requests
        print("✓ requests 导入成功")
        
        # 测试ddddocr
        import ddddocr
        print("✓ ddddocr 导入成功")
        
        # 测试cryptography
        from cryptography.hazmat.primitives import serialization
        print("✓ cryptography 导入成功")
        
        # 测试APScheduler
        from apscheduler.schedulers.background import BackgroundScheduler
        print("✓ APScheduler 导入成功")
        
        print("所有依赖导入成功！")
        return True
        
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_app_creation():
    """测试应用创建"""
    try:
        print("\n测试应用创建...")
        
        from app import app, db
        
        # 测试应用创建
        assert app is not None
        print("✓ Flask 应用创建成功")
        
        # 测试数据库初始化
        with app.app_context():
            db.create_all()
            print("✓ 数据库初始化成功")
        
        print("应用创建测试通过！")
        return True
        
    except Exception as e:
        print(f"✗ 应用创建失败: {e}")
        return False

def test_models():
    """测试数据库模型"""
    try:
        print("\n测试数据库模型...")
        
        from models import Account, EmailConfig, LoginLog, ScheduledTask
        
        # 测试模型创建
        account = Account(
            account="test@example.com",
            password="test123",
            name="测试账号"
        )
        print("✓ Account 模型创建成功")
        
        email_config = EmailConfig(
            smtp_server="smtp.test.com",
            smtp_port=587,
            sender_email="test@test.com",
            sender_password="test123",
            receiver_email="receiver@test.com"
        )
        print("✓ EmailConfig 模型创建成功")
        
        login_log = LoginLog(
            status="test",
            message="测试日志"
        )
        print("✓ LoginLog 模型创建成功")
        
        scheduled_task = ScheduledTask(
            name="测试任务",
            description="测试定时任务",
            cron_expression="0 9 * * *"
        )
        print("✓ ScheduledTask 模型创建成功")
        
        print("数据库模型测试通过！")
        return True
        
    except Exception as e:
        print(f"✗ 数据库模型测试失败: {e}")
        return False

def test_routes():
    """测试路由"""
    try:
        print("\n测试路由...")
        
        from app import app
        
        # 获取所有路由
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(f"{rule.methods} {rule.rule}")
        
        print(f"✓ 发现 {len(routes)} 个路由:")
        for route in routes:
            print(f"  {route}")
        
        # 检查关键路由
        required_routes = [
            'GET /',
            'GET /api/accounts',
            'POST /api/accounts',
            'GET /api/logs',
            'GET /api/health'
        ]
        
        for required_route in required_routes:
            found = any(required_route in route for route in routes)
            if found:
                print(f"✓ 路由 {required_route} 存在")
            else:
                print(f"✗ 路由 {required_route} 不存在")
                return False
        
        print("路由测试通过！")
        return True
        
    except Exception as e:
        print(f"✗ 路由测试失败: {e}")
        return False

def test_auto_login():
    """测试自动登录类"""
    try:
        print("\n测试自动登录类...")
        
        from app import AutoLogin
        
        # 创建自动登录实例
        auto_login = AutoLogin()
        print("✓ AutoLogin 实例创建成功")
        
        # 检查方法存在
        methods = ['get_token', 'get_captcha', 'recognize_captcha', 'login', 'login_account']
        for method in methods:
            if hasattr(auto_login, method):
                print(f"✓ 方法 {method} 存在")
            else:
                print(f"✗ 方法 {method} 不存在")
                return False
        
        print("自动登录类测试通过！")
        return True
        
    except Exception as e:
        print(f"✗ 自动登录类测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("自动登录管理系统测试")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_app_creation,
        test_models,
        test_routes,
        test_auto_login
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ 测试异常: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 50)
    
    if failed == 0:
        print("🎉 所有测试通过！系统可以正常运行。")
        return True
    else:
        print("❌ 部分测试失败，请检查错误信息。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)