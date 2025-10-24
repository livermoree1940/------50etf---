#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GitHub Secrets 配置检查工具
用于验证GitHub Actions所需的Secrets是否正确配置
"""

import os
import sys

def check_secrets_config():
    """检查环境变量配置状态"""
    print("🔍 正在检查GitHub Secrets配置...\n")
    
    # 需要检查的Secrets
    required_secrets = {
        'QQ_EMAIL': 'QQ邮箱地址（发件人）',
        'AUTH_CODE': 'QQ邮箱SMTP授权码',
        'RECEIVER': '接收邮件的邮箱地址'
    }
    
    # 可选的Secrets
    optional_secrets = {
        'BUY_THRESHOLD': '买入阈值（默认30%）',
        'SELL_THRESHOLD': '卖出阈值（默认70%）',
        'BLOCK_NAME': '板块名称（默认银行）'
    }
    
    print("📋 必需Secrets配置状态：")
    print("-" * 50)
    
    all_required_set = True
    for secret, description in required_secrets.items():
        value = os.getenv(secret)
        status = "✅ 已设置" if value else "❌ 未设置"
        print(f"{secret:<15} {status:<10} # {description}")
        if not value:
            all_required_set = False
    
    print(f"\n📋 可选Secrets配置状态：")
    print("-" * 50)
    
    for secret, description in optional_secrets.items():
        value = os.getenv(secret)
        status = "✅ 已设置" if value else "ℹ️  未设置（使用默认值）"
        print(f"{secret:<15} {status:<20} # {description}")
    
    print(f"\n🎯 配置建议：")
    print("-" * 50)
    
    if all_required_set:
        print("✅ 所有必需Secrets已配置完成！")
        print("📧 你可以运行测试脚本来验证邮件功能")
        print("🚀 推送代码到main分支将自动触发分析")
    else:
        print("❌ 还有必需Secrets未配置")
        print("📖 请参考 GITHUB_SECRETS_SETUP.md 进行配置")
        print("🔧 配置完成后再运行此检查工具")
    
    print(f"\n📚 相关文档：")
    print("- GITHUB_SECRETS_SETUP.md - 详细配置指南")
    print("- test_email.py - 邮件功能测试")
    print("- README.md - 项目使用说明")
    
    return all_required_set

def show_github_actions_info():
    """显示GitHub Actions相关信息"""
    print(f"\n🔄 GitHub Actions工作流信息：")
    print("-" * 50)
    print("📁 工作流文件：")
    print("  - .github/workflows/stock-analysis.yml")
    print("  - .github/workflows/test-email.yml")
    print()
    print("⏰ 触发方式：")
    print("  - 推送到main/master分支")
    print("  - 每天上午9:00和下午15:30")
    print("  - 手动触发")
    print()
    print("📊 输出结果：")
    print("  - 股票分析图表（PNG文件）")
    print("  - 运行日志（LOG文件）")
    print("  - 邮件通知（达到买卖信号时）")

if __name__ == "__main__":
    print("🚀 GitHub Secrets配置检查工具")
    print("=" * 60)
    
    success = check_secrets_config()
    show_github_actions_info()
    
    print(f"\n{'='*60}")
    if success:
        print("✅ 配置检查通过！系统可以正常运行")
    else:
        print("❌ 配置检查未通过，请完成配置后再试")
    
    sys.exit(0 if success else 1)