# Web 可视化与实时监控使用指南

## 📋 目录

1. [快速开始](#快速开始)
2. [Web 仪表盘功能](#web-仪表盘功能)
3. [实时预警功能](#实时预警功能)
4. [通知配置](#通知配置)
5. [常见问题](#常见问题)

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements_web.txt
```

**核心依赖**:
- `streamlit` - Web 界面框架
- `plotly` - 交互式图表
- `pandas`, `numpy` - 数据处理
- `tushare` - 股票数据（可选）

### 2. 启动 Web 仪表盘

```bash
# 股票分析主仪表盘
streamlit run web_app/dashboard.py

# 预警监控面板
streamlit run web_app/alert_dashboard.py
```

### 3. 访问界面

启动后会自动打开浏览器，访问地址：
```
http://localhost:8501
```

---

## 📊 Web 仪表盘功能

### 主仪表盘 (dashboard.py)

#### 🏠 首页
- 功能卡片展示
- 最新推荐股票
- 使用流程说明
- 策略权重表格

#### 🔍 个股分析
- 输入股票代码进行详细分析
- K 线图（含均线）
- 策略信号分析
- 推荐等级和评分
- 技术指标详情

**使用示例**:
1. 输入股票代码（如 `000001`）
2. 点击"开始分析"
3. 查看 K 线图和策略信号
4. 获取推荐等级和目标价

#### 📊 股票推荐
- 推荐等级分布图
- 推荐股票列表
- 强烈买入股票详情
- 综合评分排序

#### 🎯 股票筛选
支持多种筛选条件：
- 按推荐等级筛选
- 按技术指标筛选
- 均线金叉筛选
- RSI 超卖筛选
- 成交量突破筛选

#### 📈 策略回测
- 选择策略进行回测
- 查看收益曲线对比
- 策略绩效指标

#### 💼 投资组合
- 持仓概览
- 盈亏计算
- 持仓分布图
- 个股盈亏率

---

## 🚨 实时预警功能

### 预警监控面板 (alert_dashboard.py)

启动命令：
```bash
streamlit run web_app/alert_dashboard.py
```

#### 📋 预警列表
- **活跃预警**: 正在监控中的预警
- **已触发**: 最近 24 小时触发的预警
- **全部**: 所有历史预警记录

#### ➕ 设置预警

**1. 价格突破预警**
- 设置目标价格
- 选择突破方向（向上/向下）
- 示例：当股价突破 10 元时触发

**2. 止损止盈预警**
- 输入当前价格
- 设置止损比例（如 5%）
- 设置止盈比例（如 10%）
- 自动计算止损价和止盈价

**3. RSI 超买超卖预警**
- 设置超买线（默认 70）
- 设置超卖线（默认 30）
- 当 RSI 超出范围时触发

**4. 成交量突破预警**
- 设置成交量倍数（如 2 倍）
- 当成交量超过均量指定倍数时触发

#### ⚙️ 通知配置

**邮件通知配置**:
1. 输入 SMTP 服务器（如 `smtp.qq.com`）
2. 输入 SMTP 端口（如 `587`）
3. 输入发件人邮箱
4. 输入邮箱授权码（非登录密码）
5. 输入收件人列表

**微信通知配置**:
1. 访问 https://sct.ftqq.com/ 注册
2. 获取 ServerChan 推送 key
3. 在配置中输入 key

#### 📊 监控状态
- 监控股票数量
- 活跃预警数量
- 24 小时触发统计
- 预警类型分布

---

## 🔔 通知配置

### 配置文件位置

```
config/config.json
```

### 邮件通知配置示例

```json
{
  "email": {
    "enabled": true,
    "smtp_server": "smtp.qq.com",
    "smtp_port": 587,
    "sender": "your_email@qq.com",
    "password": "your_auth_code",
    "receivers": ["receiver1@email.com"]
  }
}
```

### 获取邮箱授权码

**QQ 邮箱**:
1. 登录邮箱
2. 设置 → 账户
3. 开启 POP3/SMTP 服务
4. 生成授权码

**163 邮箱**:
1. 登录邮箱
2. 设置 → POP3/SMTP/IMAP
3. 开启 SMTP 服务
4. 获取授权码

### ServerChan 微信推送

1. 访问 https://sct.ftqq.com/
2. 微信扫码登录
3. 获取 SendKey
4. 在配置中填入 SendKey

---

## 💻 命令行使用

### 创建价格预警

```python
from price_alert import PriceAlertManager

manager = PriceAlertManager()

# 创建价格突破预警
manager.create_price_breakout_alert(
    symbol="000001",
    name="平安银行",
    breakout_price=10.5,
    above=True,  # 向上突破
    notification_methods=['email', 'wechat']
)

# 创建止损预警
manager.create_stop_loss_alert(
    symbol="000001",
    name="平安银行",
    stop_price=9.5
)

# 创建止盈预警
manager.create_take_profit_alert(
    symbol="000001",
    name="平安银行",
    target_price=12.0
)
```

### 实时监控

```python
from realtime_monitor import RealtimeMonitor
from price_alert import PriceAlertManager

# 初始化
alert_manager = PriceAlertManager()
monitor = RealtimeMonitor(
    tushare_token="your_token",
    alert_manager=alert_manager
)

# 添加监控股票
monitor.add_to_watchlist(["000001", "600519", "300750"])

# 开始监控（60 秒检查一次）
monitor.start_monitoring(interval=60, blocking=True)
```

### 简易监控（无需 Token）

```python
from realtime_monitor import SimpleMonitor

monitor = SimpleMonitor()

# 添加股票
monitor.add_stock("000001", "平安银行")

# 设置价格预警
monitor.set_price_alert(
    "000001", "平安银行",
    target_price=10.5,
    above=True
)

# 设置止损止盈
monitor.set_stop_loss_take_profit(
    "000001", "平安银行",
    current_price=10.0,
    stop_loss_pct=5.0,
    take_profit_pct=10.0
)

# 手动检查
monitor.check_manual("000001", current_price=10.6)
```

---

## 🧪 测试

### 测试通知

```python
from notification_service import NotificationService

service = NotificationService()

# 测试控制台通知
service.test_notification('console')

# 测试邮件通知
service.test_notification('email')

# 测试微信通知
service.test_notification('wechat')
```

### 测试预警流程

```python
from price_alert import PriceAlertManager, AlertType
from notification_service import NotificationService

# 创建预警
manager = PriceAlertManager()
alert = manager.create_alert(
    symbol="000001",
    name="平安银行",
    alert_type=AlertType.PRICE_ABOVE,
    condition_value=10.0
)

# 创建通知服务
service = NotificationService()

# 模拟触发
alert.status = "triggered"
alert.current_value = 10.5
alert.triggered_at = datetime.now()

# 发送通知
service.send_alert_notification(alert)
```

---

## ❓ 常见问题

### Q1: Streamlit 无法启动？

**A**: 检查是否安装了依赖：
```bash
pip install -r requirements_web.txt
```

### Q2: 如何修改 Web 界面端口？

**A**: 使用 `--server.port` 参数：
```bash
streamlit run web_app/dashboard.py --server.port 8502
```

### Q3: 邮件发送失败？

**A**: 
1. 确认 SMTP 服务器和端口正确
2. 使用授权码而非登录密码
3. 检查邮箱是否开启了 SMTP 服务

### Q4: 预警不触发？

**A**:
1. 检查预警状态是否为"active"
2. 确认当前价格是否达到触发条件
3. 检查预警是否已过期

### Q5: 如何在后台运行监控？

**A**: 使用 `nohup`（Linux/Mac）:
```bash
nohup python monitor_script.py &
```

Windows 可以使用任务计划程序。

### Q6: 预警数据保存在哪里？

**A**: 默认保存在 `data/alerts.json`

### Q7: 如何清除所有预警？

**A**: 
```python
from price_alert import PriceAlertManager

manager = PriceAlertManager()
manager.alerts.clear()
manager._save_alerts()
```

---

## 📝 最佳实践

### 1. 合理设置预警

- 止损位：建议 5-8%
- 止盈位：建议 10-20%
- 价格突破：参考技术阻力位

### 2. 选择通知方式

- **控制台**: 开发测试用
- **邮件**: 正式使用，稳定可靠
- **微信**: 实时性强，适合手机接收

### 3. 定期清理

- 每周清理过期预警
- 查看已触发预警记录
- 调整不合理的预警位

### 4. 监控频率

- 短线交易：30-60 秒检查一次
- 中线交易：5-10 分钟检查一次
- 长线投资：1 小时检查一次

---

## 🎯 使用场景

### 场景 1: 短线交易监控

```python
# 设置紧密的止损止盈
monitor.set_stop_loss_take_profit(
    "000001", "平安银行",
    current_price=10.0,
    stop_loss_pct=3.0,   # 3% 止损
    take_profit_pct=5.0  # 5% 止盈
)

# 高频监控
monitor.start_monitoring(interval=30)
```

### 场景 2: 突破交易

```python
# 设置突破预警
manager.create_price_breakout_alert(
    "600519", "贵州茅台",
    breakout_price=1800,
    above=True,
    notification_methods=['wechat']
)
```

### 场景 3: 价值投资

```python
# 设置 RSI 超卖预警（寻找买入机会）
manager.create_rsi_alert(
    "000001", "平安银行",
    overbought=70,
    oversold=20,  # 更低的超卖线
    notification_methods=['email']
)
```

---

## 📞 技术支持

- 查看项目文档
- 检查日志文件
- 提交 Issue 反馈问题

---

*最后更新：2026 年 3 月 21 日*
*版本：v1.0 - Web 可视化版*
