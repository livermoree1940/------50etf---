#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GitHub Actions 快速配置和测试工具
一键完成所有配置检查和功能测试
"""

import os
import sys
import subprocess

def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n🔄 {description}")
    print("-" * 50)
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ 成功: {description}")
            if result.stdout:
                print(f"输出: {result.stdout.strip()}")
        else:
            print(f"❌ 失败: {description}")
            if result.stderr:
                print(f"错误: {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False

def main():
    """主函数：运行完整的配置和测试流程"""
    print("🚀 GitHub Actions 快速配置测试工具")
    print("=" * 60)
    
    # 步骤1：检查环境变量
    print("\n📋 步骤1: 检查环境变量配置")
    print("-" * 60)
    success1 = run_command("python check_github_secrets.py", "检查GitHub Secrets配置")
    
    if not success1:
        print("\n❌ 环境变量检查失败，请先配置GitHub Secrets")
        print("📖 参考文档: GITHUB_SECRETS_SETUP.md")
        return False
    
    # 步骤2：测试邮件功能
    print("\n📧 步骤2: 测试邮件发送功能")
    print("-" * 60)
    success2 = run_command("python test_email.py", "测试邮件发送")
    
    # 步骤3：验证Python环境
    print("\n🐍 步骤3: 验证Python环境和依赖")
    print("-" * 60)
    success3 = run_command("python -c "import akshare, pandas, matplotlib; print('依赖检查通过')""", "检查Python依赖")
    
    # 步骤4：检查工作流文件
    print("\n📁 步骤4: 检查GitHub Actions工作流")
    print("-" * 60)
    workflow_files = [
        ".github/workflows/stock-analysis.yml",
        ".github/workflows/test-email.yml"
    ]
    
    all_workflows_ok = True
    for workflow_file in workflow_files:
        if os.path.exists(workflow_file):
            print(f"✅ 找到工作流文件: {workflow_file}")
        else:
            print(f"❌ 缺少工作流文件: {workflow_file}")
            all_workflows_ok = False
    
    # 步骤5：显示配置总结
    print("\n📊 配置总结")
    print("=" * 60)
    
    total_checks = 4
    passed_checks = sum([success1, success2, success3, all_workflows_ok])
    
    print(f"检查项目: {total_checks}")
    print(f"通过项目: {passed_checks}")
    print(f"通过率: {passed_checks/total_checks*100:.1f}%")
    
    if passed_checks == total_checks:
        print("\n🎉 所有检查通过！系统配置完成")
        print("\n🚀 下一步操作：")
        print("1. 推送代码到GitHub main分支")
        print("2. 在GitHub Actions页面查看运行状态")
        print("3. 等待定时任务或手动触发")
        return True
    else:
        print(f"\n⚠️  有 {total_checks - passed_checks} 项检查未通过")
        print("\n🔧 建议操作：")
        if not success1:
            print("- 配置GitHub Secrets（参考GITHUB_SECRETS_SETUP.md）")
        if not success2:
            print("- 检查邮件配置和网络连接")
        if not success3:
            print("- 安装Python依赖包（pip install -r requirements.txt）")
        if not all_workflows_ok:
            print("- 检查工作流文件是否存在")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)