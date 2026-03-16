# 股票智能预警与投资组合管理系统 - 快速开始指南

## 📦 项目已完成功能

### ✅ 已实现的核心模块

1. **数据库模块** (`database/database_manager.py`)
   - 股票持仓管理
   - 价格预警配置
   - 技术指标预警配置
   - 预警触发日志

2. **数据服务** (`app/data_service.py`)
   - 股票数据获取 (支持 A 股)
   - 技术指标计算 (MA, MACD, RSI, 布林带)
   - 数据缓存机制

3. **预警引擎** (`app/alert_engine.py`)
   - 价格预警检查
   - 技术指标预警检查
   - 防重复触发机制

4. **投资组合管理** (`app/portfolio_manager.py`)
   - 持仓盈亏计算
   - 投资组合分析
   - 数据可视化支持

5. **通知服务** (`notifications/notifier.py`)
   - 邮件通知
   - 钉钉机器人通知

6. **Web 仪表板** (`app/dashboard.py`)
   - Streamlit 交互式界面
   - 投资组合可视化
   - 预警配置管理

7. **定时调度器** (`app/scheduler.py`)
   - 后台自动预警检查
   - 可配置检查间隔

8. **命令行工具** (`main.py`)
   - 便捷的 CLI 操作

---

## 🚀 使用方法

### 方法 1: 使用批处理文件 (Windows)

#### 启动 Web 仪表板
```bash
双击运行：run_web.bat
```
访问 http://localhost:8501

#### 启动后台预警
```bash
双击运行：run_scheduler.bat
```

### 方法 2: 使用命令行

```bash
cd stock_alert_portfolio

# 查看帮助
python main.py --help

# 初始化数据库
python main.py init

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

# 启动 Web 仪表板
python main.py web

# 启动后台预警调度器
python main.py scheduler
```

---

## 📊 Web 仪表板功能

访问 http://localhost:8501 后，您将看到以下功能页面：

### 1. 📊 投资组合总览
- 总市值、总投入、总盈亏指标卡
- 持仓分布饼图
- 盈亏柱状图
- 持仓明细表格

### 2. 🔔 预警管理
- **新增预警** 选项卡
  - 添加价格预警 (突破/跌破/涨跌幅)
  - 添加技术指标预警 (RSI/MACD/MA/布林带)
- **预警列表** 选项卡
  - 查看所有激活的预警
  - 删除/切换预警状态
- **预警日志** 选项卡
  - 查看历史触发记录

### 3. 📈 股票分析
- 输入股票代码
- 查看 K 线图
- 技术指标分析 (MA/MACD/RSI)

### 4. ⚙️ 设置
- 查看通知配置状态
- 手动检查预警
- 发送测试通知

---

## 🔧 配置通知

### 配置邮件通知

编辑 `config\.env` 文件：

```env
EMAIL_ENABLED=true
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_TO=recipient@email.com
```

**注意**: Gmail 需要使用应用专用密码，而非登录密码。

### 配置钉钉通知

1. 在钉钉群中添加机器人
2. 选择"自定义"机器人
3. 复制 Webhook 地址
4. 编辑 `config\.env`:

```env
DINGTALK_ENABLED=true
DINGTALK_WEBHOOK=https://oapi.dingtalk.com/robot/send?access_token=xxx
```

---

## 📋 预警类型说明

### 价格预警

| 类型 | 说明 | 示例 |
|------|------|------|
| `price_above` | 价格突破指定值 | 股价突破 15 元 |
| `price_below` | 价格跌破指定值 | 股价跌破 10 元 |
| `change_above` | 涨幅超过指定百分比 | 涨幅超过 5% |
| `change_below` | 跌幅超过指定百分比 | 跌幅超过 3% |

### 技术指标预警

| 指标 | 条件 | 说明 |
|------|------|------|
| `RSI` | `below 30` | RSI 低于 30 (超卖) |
| `RSI` | `above 70` | RSI 高于 70 (超买) |
| `MACD` | `cross_above` | MACD 金叉 |
| `MACD` | `cross_below` | MACD 死叉 |
| `MA5/MA10/MA20` | `cross_below` | 股价下穿均线 |
| `MA5/MA10/MA20` | `cross_above` | 股价上穿均线 |
| `BB` | `touch_lower` | 触及布林带下轨 |
| `BB` | `touch_upper` | 触及布林带上轨 |

---

## ⚠️ 注意事项

1. **数据源限制**: 使用 Yahoo Finance 免费数据，可能有速率限制
2. **网络要求**: 需要稳定的网络连接获取实时数据
3. **预警延迟**: 检查间隔建议设置为 60 秒以上
4. **投资有风险**: 本系统仅供参考，不构成投资建议

---

## 🛠️ 故障排除

### 无法获取股票数据
```
错误：YFRateLimitError('Too Many Requests')
解决：等待几分钟后重试，或配置 Tushare Token
```

### Streamlit 无法启动
```bash
# 检查是否安装 streamlit
pip install streamlit

# 指定端口启动
python main.py web --port 8502
```

### 邮件发送失败
- 检查 SMTP 配置是否正确
- 使用应用专用密码
- 确认邮箱已开启 SMTP 服务

---

## 📁 项目文件说明

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
│   └── notifier.py           # 通知服务
├── config/
│   ├── settings.py           # 配置管理
│   └── .env                  # 环境变量配置
├── data/                     # 数据目录
├── logs/                     # 日志目录
├── main.py                   # 命令行入口
├── requirements.txt          # 依赖列表
├── README.md                 # 项目文档
├── run_web.bat              # 启动 Web 仪表板
├── run_scheduler.bat        # 启动预警调度器
└── setup.bat                # 安装脚本
```

---

## 🎯 下一步建议

1. **配置 Tushare Token**: 获取更稳定的 A 股数据源
2. **设置通知**: 配置邮件或钉钉通知
3. **添加持仓**: 录入您的实际持仓数据
4. **设置预警**: 根据您的需求配置预警条件
5. **启动监控**: 运行后台调度器自动监控

---

## 💡 使用示例

### 示例 1: 设置股价突破预警

```bash
# 添加持仓
python main.py portfolio add --code 600519 --name 贵州茅台 --shares 100 --cost 1800

# 设置突破预警
python main.py alert add-price --code 600519 --type price_above --threshold 2000

# 启动后台监控
python main.py scheduler
```

### 示例 2: 设置 RSI 超卖预警

```bash
# 添加技术指标预警
python main.py alert add-tech --code 000001 --indicator RSI --condition below --threshold 30

# 立即检查
python main.py alert check
```

### 示例 3: 查看投资业绩

```bash
# 查看持仓和盈亏
python main.py portfolio list
```

---

**🎉 系统已完成部署，祝您投资顺利！**
