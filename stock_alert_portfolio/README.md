# 股票智能预警与投资组合管理系统

一个功能完整的股票监控和投资组合管理系统，支持实时价格预警、技术指标预警、投资组合跟踪和可视化分析。

## ✨ 功能特性

### 📊 投资组合管理
- 添加/删除股票持仓
- 实时盈亏计算
- 持仓分布分析
- 投资业绩统计

### 🔔 智能预警系统
- **价格预警**: 价格突破/跌破、涨跌幅预警
- **技术指标预警**: RSI、MACD、移动平均线、布林带
- 支持邮件和钉钉通知
- 自动防重复触发机制

### 📈 股票分析
- K 线图可视化
- 技术指标分析 (MA, MACD, RSI, 布林带)
- 实时行情数据

### 🌐 Web 仪表板
- 基于 Streamlit 的交互式界面
- 投资组合可视化
- 预警配置管理
- 实时预警日志

### ⏰ 后台调度器
- 定时自动检查预警
- 可配置检查间隔
- 日志记录

## 🚀 快速开始

### 1. 安装依赖

```bash
cd stock_alert_portfolio
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制示例配置文件
copy config\.env.example config\.env
```

编辑 `config\.env` 文件，填入您的配置：

```env
# Tushare Token (可选)
TUSHARE_TOKEN=your_token

# 邮件通知配置
EMAIL_ENABLED=false
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_password
EMAIL_TO=recipient@email.com

# 钉钉通知配置
DINGTALK_ENABLED=false
DINGTALK_WEBHOOK=https://oapi.dingtalk.com/robot/send?access_token=xxx

# 数据库配置
DATABASE_URL=sqlite:///./database/stock_portfolio.db

# 预警检查间隔 (秒)
CHECK_INTERVAL=60
```

### 3. 初始化数据库

```bash
python main.py init
```

### 4. 启动应用

#### 方式一：Web 仪表板 (推荐)

```bash
python main.py web
```

访问 http://localhost:8501

#### 方式二：后台预警调度器

```bash
python main.py scheduler
```

#### 方式三：命令行操作

```bash
# 查看帮助
python main.py --help

# 添加持仓
python main.py portfolio add --code 000001 --name 平安银行 --shares 1000 --cost 12.5

# 查看持仓
python main.py portfolio list

# 添加价格预警
python main.py alert add-price --code 000001 --type price_above --threshold 15.0

# 添加技术指标预警
python main.py alert add-tech --code 000001 --indicator RSI --condition below --threshold 30

# 查看预警列表
python main.py alert list

# 立即检查预警
python main.py alert check
```

## 📁 项目结构

```
stock_alert_portfolio/
├── app/
│   ├── dashboard.py          # Streamlit Web 仪表板
│   ├── data_service.py       # 数据获取服务
│   ├── alert_engine.py       # 预警检查引擎
│   ├── portfolio_manager.py  # 投资组合管理
│   └── scheduler.py          # 定时任务调度器
├── database/
│   └── database_manager.py   # 数据库管理
├── notifications/
│   └── notifier.py           # 通知服务 (邮件/钉钉)
├── config/
│   ├── settings.py           # 配置管理
│   └── .env.example          # 环境变量示例
├── data/                     # 数据目录
├── logs/                     # 日志目录
├── main.py                   # 命令行入口
├── requirements.txt          # 依赖列表
└── README.md                 # 文档
```

## 📋 使用说明

### 投资组合管理

1. **添加持仓**
   - Web 界面：投资组合总览 → 添加持仓
   - CLI: `python main.py portfolio add --code 000001 --shares 1000 --cost 12.5`

2. **查看盈亏**
   - Web 界面自动显示实时盈亏
   - CLI: `python main.py portfolio list`

### 预警设置

1. **价格预警类型**
   - `price_above`: 价格突破指定值
   - `price_below`: 价格跌破指定值
   - `change_above`: 涨幅超过指定百分比
   - `change_below`: 跌幅超过指定百分比

2. **技术指标预警**
   - `RSI`: 相对强弱指标
   - `MACD`: 平滑异同移动平均线
   - `MA5/MA10/MA20/MA60`: 移动平均线
   - `BB`: 布林带

3. **通知方式**
   - 邮件通知：需要配置 SMTP
   - 钉钉通知：需要配置机器人 Webhook

### 预警触发条件示例

| 指标 | 条件 | 说明 |
|------|------|------|
| RSI | below 30 | 超卖信号 |
| RSI | above 70 | 超买信号 |
| MACD | cross_above | 金叉 |
| MACD | cross_below | 死叉 |
| MA20 | cross_below | 股价下穿 20 日均线 |
| BB | touch_lower | 触及布林带下轨 |

## 🔧 配置说明

### 邮件通知配置

以 Gmail 为例：
```env
EMAIL_ENABLED=true
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password  # 使用应用专用密码
EMAIL_TO=recipient@email.com
```

### 钉钉通知配置

1. 在钉钉群中添加机器人
2. 选择"自定义"机器人
3. 复制 Webhook 地址
4. 配置到 `.env` 文件：

```env
DINGTALK_ENABLED=true
DINGTALK_WEBHOOK=https://oapi.dingtalk.com/robot/send?access_token=xxx
```

## ⚠️ 注意事项

1. **数据源**: 使用 Yahoo Finance 获取数据，可能需要稳定的网络连接
2. **实时性**: 免费数据源有延迟，不适合高频交易
3. **预警频率**: 建议设置合理的检查间隔，避免过于频繁
4. **投资有风险**: 本系统仅供参考，不构成投资建议

## 🛠️ 故障排除

### 无法获取股票数据
- 检查网络连接
- 验证股票代码格式 (A 股需要添加.SZ 或.SS 后缀)
- 考虑配置 Tushare Token 获取更稳定的数据

### 邮件发送失败
- 检查 SMTP 配置
- 使用应用专用密码 (而非登录密码)
- 确认邮箱已开启 SMTP 服务

### Streamlit 无法启动
- 确认已安装 `streamlit`
- 检查端口是否被占用
- 尝试指定其他端口：`python main.py web --port 8502`

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
