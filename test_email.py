#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
邮件功能测试脚本
用于验证邮件发送功能是否正常工作
"""

import os
import sys
from utils_email import send_email_if_signal

def test_email_function():
    """测试邮件发送功能"""
    print("开始测试邮件发送功能...")
    
    # 获取环境变量
    qq_email = os.getenv('QQ_EMAIL')
    auth_code = os.getenv('AUTH_CODE')
    receiver = os.getenv('RECEIVER')
    
    if not all([qq_email, auth_code, receiver]):
        print("❌ 环境变量配置不完整，请检查以下变量：")
        print(f"QQ_EMAIL: {'已设置' if qq_email else '未设置'}")
        print(f"AUTH_CODE: {'已设置' if auth_code else '未设置'}")
        print(f"RECEIVER: {'已设置' if receiver else '未设置'}")
        return False
    
    print(f"发件人: {qq_email}")
    print(f"收件人: {receiver}")
    
    # 测试发送邮件
    try:
        subject = "股票分析系统 - 测试邮件"
        body = """
        这是一封测试邮件，用于验证股票分析系统的邮件发送功能。
        
        如果收到此邮件，说明邮件配置正确，可以正常接收买卖信号提醒。
        
        系统配置信息：
        - 发件人：{}
        - 收件人：{}
        - 发送时间：{}
        
        请确保将此邮箱地址添加到您的通讯录中，避免邮件被误判为垃圾邮件。
        """.format(qq_email, receiver, "测试时间")
        
        # 调用邮件发送函数
        success = send_email_if_signal(subject, body, image_path=None)
        
        if success:
            print("✅ 邮件发送成功！请检查收件箱。")
            return True
        else:
            print("❌ 邮件发送失败，请检查配置和网络连接。")
            return False
            
    except Exception as e:
        print(f"❌ 邮件发送异常: {e}")
        return False

if __name__ == "__main__":
    success = test_email_function()
    sys.exit(0 if success else 1)