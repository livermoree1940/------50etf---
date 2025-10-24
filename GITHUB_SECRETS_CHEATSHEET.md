# GitHub Secrets 配置快速参考卡片

## 🚀 3步完成配置

### 第1步：获取QQ邮箱授权码
```
QQ邮箱 → 设置 → 账户 → POP3/SMTP服务 → 生成授权码
```

### 第2步：添加GitHub Secrets
进入：GitHub仓库 → Settings → Secrets and variables → Actions → New repository secret

| Name | Value | 说明 |
|------|-------|------|
| `QQ_EMAIL` | 123456@qq.com | 你的QQ邮箱 |
| `AUTH_CODE` | abcdef1234567890 | 16位SMTP授权码 |
| `RECEIVER` | receiver@example.com | 接收邮件的邮箱 |

### 第3步：验证配置
```bash
python quick_setup.py  # 一键测试所有功能
```

## 📋 检查清单

- [ ] QQ邮箱已开启SMTP服务
- [ ] 已获取16位授权码（不是QQ密码）
- [ ] 已添加3个必需的GitHub Secrets
- [ ] 已推送代码到GitHub
- [ ] 已测试邮件发送功能

## 🔧 常用命令

```bash
# 测试邮件功能
python test_email.py

# 检查Secrets配置
python check_github_secrets.py

# 一键完整测试
python quick_setup.py

# 本地运行分析脚本
python 通信.py
```

## 📞 问题排查

### 没收到邮件？
- 检查垃圾邮件文件夹
- 确认Secrets配置正确
- 运行测试脚本检查

### Actions运行失败？
- 查看Actions页面的错误日志
- 确认代码已推送到main分支
- 检查依赖包是否正确安装

### 授权码获取失败？
- 确保QQ邮箱已绑定手机号
- 检查手机能否接收短信
- 尝试使用其他浏览器

## 🎯 成功标志

✅ **配置成功后会：**
- 每次push到main分支自动运行分析
- 每天9:00和15:30定时分析
- 达到买卖阈值时自动发送邮件
- 生成可视化图表并保存

## 📚 相关文件

- `GITHUB_SECRETS_SETUP.md` - 详细配置指南
- `check_github_secrets.py` - Secrets配置检查
- `test_email.py` - 邮件功能测试
- `quick_setup.py` - 一键配置测试

---
**💡 提示**：配置完成后，每次更新代码推送到main分支都会自动触发股票分析！

**保存此卡片，方便随时查阅配置步骤**