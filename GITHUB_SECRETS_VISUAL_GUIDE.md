# GitHub Secrets 可视化配置步骤

## 🖼️ 详细截图指南

### 步骤1：进入GitHub仓库设置

```
GitHub仓库首页 → Settings → Secrets and variables → Actions
```

**预期界面：**
你会看到一个绿色的「New repository secret」按钮

### 步骤2：添加第一个Secret（QQ_EMAIL）

**界面操作：**
1. 点击「New repository secret」
2. 在「Name」输入框中输入：`QQ_EMAIL`
3. 在「Secret」输入框中输入你的QQ邮箱地址
4. 点击「Add secret」按钮

**截图说明：**
```
┌─────────────────────────────────────┐
│ New secret                          │
├─────────────────────────────────────┤
│ Name: [QQ_EMAIL___________________] │
│                                     │
│ Secret: [your_qq@qq.com__________] │
│                                     │
│ [Add secret] [Cancel]                │
└─────────────────────────────────────┘
```

### 步骤3：添加第二个Secret（AUTH_CODE）

**界面操作：**
1. 再次点击「New repository secret」
2. 在「Name」输入框中输入：`AUTH_CODE`
3. 在「Secret」输入框中输入你的16位SMTP授权码
4. 点击「Add secret」按钮

**截图说明：**
```
┌─────────────────────────────────────┐
│ New secret                          │
├─────────────────────────────────────┤
│ Name: [AUTH_CODE__________________] │
│                                     │
│ Secret: [16位授权码________________] │
│                                     │
│ [Add secret] [Cancel]                │
└─────────────────────────────────────┘
```

### 步骤4：添加第三个Secret（RECEIVER）

**界面操作：**
1. 再次点击「New repository secret」
2. 在「Name」输入框中输入：`RECEIVER`
3. 在「Secret」输入框中输入接收邮件的邮箱地址
4. 点击「Add secret」按钮

## ✅ 配置完成后的界面

**预期结果：**
```
┌─────────────────────────────────────┐
│ Repository secrets                  │
├─────────────────────────────────────┤
│ ✅ QQ_EMAIL      Updated 1 minute ago│
│ ✅ AUTH_CODE     Updated 2 minutes ago│
│ ✅ RECEIVER      Updated 3 minutes ago│
│                                     │
│ [New repository secret]             │
└─────────────────────────────────────┘
```

## 🎯 验证配置成功

### 方法一：查看Secrets列表
- 应该能看到3个绿色的✅标记
- 显示"Updated"时间

### 方法二：运行测试
1. 进入「Actions」页面
2. 选择「测试邮件功能」
3. 点击「Run workflow」
4. 等待运行结果

## ⚠️ 常见界面问题

### 问题1：找不到Settings选项
**解决方案：**
- 确保你是仓库的所有者或有管理员权限
- 登录GitHub账号
- 确认在正确的仓库页面

### 问题2：没有Secrets and variables选项
**解决方案：**
- 确认你有足够的权限
- 检查是否在个人仓库而不是组织仓库
- 尝试刷新页面

### 问题3：Add secret按钮灰色
**解决方案：**
- 确保Name和Secret都填写完整
- 检查Name是否符合命名规范（只能包含字母、数字、下划线）
- Secret长度不能为0

## 🚀 下一步操作

配置完成后：
1. ✅ 返回项目主页
2. ✅ 运行 `python quick_setup.py` 进行完整测试
3. ✅ 推送代码到main分支触发自动运行
4. ✅ 在Actions页面查看运行状态

## 📞 界面操作支持

如果在配置过程中遇到问题：
1. 截图当前界面状态
2. 记录具体的操作步骤
3. 查看浏览器控制台是否有错误信息
4. 尝试使用不同的浏览器

---
**记住：** 配置完成后，每次推送到main分支都会自动触发股票分析！📈