# 股票板块60日线分析系统

这是一个基于Python的股票分析系统，用于分析指定板块中股票站上60日均线的比例，并提供买卖信号提醒。

## 功能特点

- **多数据源支持**：腾讯、新浪、东财接口自动切换
- **邮件提醒**：当60日线比例达到买卖阈值时自动发送邮件
- **可视化图表**：生成指数走势和60日线比例图表
- **GitHub Actions自动化**：定时运行，无需手动操作
- **缓存机制**：本地缓存股票数据，提高运行效率

## 文件结构

```
├── 通信.py                    # 主要分析脚本
├── utils_email.py             # 邮件发送工具
├── requirements.txt           # Python依赖
├── .github/workflows/         # GitHub Actions工作流
│   └── stock-analysis.yml    # 自动化运行配置
└── .env.example              # 环境变量配置示例
```

## 本地运行

### 1. 环境准备

```bash
# 创建conda环境
conda create -n ak python=3.9
conda activate ak

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制`.env.example`为`.env`并填写你的配置：

```bash
cp .env.example .env
# 编辑.env文件，填入你的邮箱配置
```

### 3. 运行脚本

```bash
# 使用默认配置（银行板块，申万数据源）
python 通信.py

# 或者修改脚本开头的配置参数
```

## GitHub Actions配置

### 1. 触发方式
- **自动触发**：每次推送到main/master分支时自动运行
- **定时运行**：每天上午9:00和下午15:30自动运行（A股开盘和收盘后）
- **手动触发**：在GitHub Actions页面手动运行

### 2. 配置GitHub Secrets

在GitHub仓库的 `Settings -> Secrets and variables -> Actions` 中添加以下secrets：

- `QQ_EMAIL`: 你的QQ邮箱地址
- `AUTH_CODE`: QQ邮箱SMTP授权码（不是密码）
- `RECEIVER`: 接收邮件的邮箱地址

### 2. 获取QQ邮箱SMTP授权码

1. 登录QQ邮箱网页版
2. 点击"设置" -> "账户"
3. 找到"POP3/SMTP服务"，点击"生成授权码"
4. 按照提示发送短信获取授权码

### 3. 定时运行

默认配置：
- 每天上午9:00（北京时间）
- 每天下午15:30（北京时间）

可以在 `.github/workflows/stock-analysis.yml` 中修改cron表达式来自定义运行时间。

### 4. 手动触发

在GitHub仓库的Actions页面，可以手动运行工作流：
- 可以选择不同的板块名称
- 可以选择数据源类型（xml/sw）

## 配置参数说明

在脚本开头可以修改以下参数：

```python
BLOCK_NAME      = "银行"           # 板块中文名
SOURCE_TYPE     = "sw"            # "xml" 或 "sw" 二选一
XML_PATH        = r"F:\Program Files\同花顺远航版\bin\users\mx_713570454\blockstockV3.xml"
XML_BLOCK_NAME  = "通信"           # xml 里 <Block name="xxx">
SW_INDEX_CODE   = 801770          # 申万行业指数代码
BUY_THRESHOLD   = 30              # 买入信号阈值（%）
SELL_THRESHOLD  = 70              # 卖出信号阈值（%）
ANALYSIS_DAYS   = 900             # 分析天数
MAX_THREADS     = 10              # 最大线程数
CACHE_DIR       = r"D:\stock_cache"  # 缓存目录
```

## 输出结果

- **控制台输出**：详细的分析结果和信号提醒
- **图表文件**：`{板块名}_板块分析_{日期}.png`
- **邮件通知**：当触发买卖信号时发送邮件（包含图表附件）

## 注意事项

1. **数据源稳定性**：腾讯和新浪接口可能会有不稳定的情况，系统会自动切换到东财接口
2. **邮件发送限制**：QQ邮箱有每日发送限制，注意不要频繁触发
3. **GitHub Actions限制**：免费账户有每月2000分钟的运行时间限制
4. **缓存清理**：定期清理`CACHE_DIR`中的缓存文件，避免占用过多磁盘空间

## 更新日志

- v1.0: 基础功能实现
- v1.1: 添加多数据源支持
- v1.2: 添加GitHub Actions自动化
- v1.3: 优化邮件发送功能

## 问题反馈

如有问题，请在GitHub Issues中反馈。