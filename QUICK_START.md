# 快速启动指南 - 中国股票分析系统

## 🚀 5 分钟快速开始

### 方式 1: Web 可视化界面（推荐新手）

```bash
# 1. 安装 Web 依赖（约 2 分钟）
pip install -r requirements_web.txt

# 2. 启动 Web 仪表盘
streamlit run web_app/dashboard.py
```

**访问**: http://localhost:8501

**功能**:
- 📊 交互式 K 线图
- 🎯 股票推荐列表
- 🔍 股票筛选器
- 💼 投资组合管理

---

### 方式 2: 命令行界面

```bash
# 1. 安装基础依赖
pip install -r requirements.txt

# 2. 配置 Tushare token（可选）
set TUSHARE_TOKEN=your_token_here

# 3. 运行主程序
python main.py
```

**功能**:
- 策略分析
- 股票推荐
- 回测比较

---

### 方式 3: 实时监控预警

```bash
# 1. 运行演示程序测试功能
python run_monitor_demo.py

# 2. 启动监控服务
python start_monitor.py
```

**功能**:
- 🚨 价格预警
- 📧 邮件通知
- 💬 微信推送

---

## 📋 使用场景

### 场景 1: 我想看股票分析图表

```bash
streamlit run web_app/dashboard.py
# 访问 http://localhost:8501
# 输入股票代码 → 点击"开始分析"
```

### 场景 2: 我想获取股票推荐

**Web 方式**:
```bash
streamlit run web_app/dashboard.py
# 点击"股票推荐"菜单
```

**命令行方式**:
```bash
python run_stock_recommender.py
```

### 场景 3: 我想设置止损预警

**Web 方式**:
```bash
streamlit run web_app/alert_dashboard.py
# 点击"设置预警" → 选择"止损止盈预警"
```

**Python 方式**:
```python
from price_alert import PriceAlertManager

manager = PriceAlertManager()
manager.create_stop_loss_alert(
    symbol="000001",
    name="平安银行",
    stop_price=9.5
)
```

### 场景 4: 我想筛选股票

**Web 方式**:
```bash
streamlit run web_app/dashboard.py
# 点击"股票筛选"菜单
```

**Python 方式**:
```python
from stock_screener import StockScreener

screener = StockScreener()
results = screener.screen_by_recommendation(
    recommendation=['STRONG_BUY']
)
print(results)
```

---

## 🔧 快速配置

### Tushare Token 配置

```bash
# 获取 token: https://tushare.pro/
set TUSHARE_TOKEN=your_token_here
```

### 邮件通知配置

```python
from notification_service import NotificationService

service = NotificationService()
service.setup_email(
    smtp_server="smtp.qq.com",
    smtp_port=587,
    sender="your_email@qq.com",
    password="your_auth_code",
    receivers=["receiver@email.com"]
)
```

### 微信通知配置

1. 访问 https://sct.ftqq.com/
2. 获取 ServerChan 推送 key
3. 在 Web 界面配置

---

## 📊 功能对比

| 功能 | Web 界面 | 命令行 | 说明 |
|------|---------|--------|------|
| 股票分析 | ✅ | ✅ | Web 界面更直观 |
| 股票推荐 | ✅ | ✅ | 功能相同 |
| 股票筛选 | ✅ | ✅ | Web 界面更友好 |
| 投资组合 | ✅ | ✅ | 功能相同 |
| 价格预警 | ✅ | ✅ | Web 界面更易用 |
| 实时监控 | ✅ | ✅ | 命令行更灵活 |
| 策略回测 | ✅ | ✅ | 功能相同 |
| 通知配置 | ✅ | ✅ | Web 界面更简单 |

---

## ❓ 常见问题速查

### Q: Streamlit 无法启动？
```bash
pip install -r requirements_web.txt
```

### Q: 如何修改 Web 端口？
```bash
streamlit run web_app/dashboard.py --server.port 8502
```

### Q: 预警数据存在哪里？
```
data/alerts.json
```

### Q: 如何停止监控？
```
按 Ctrl+C
```

### Q: 如何清除所有预警？
```python
from price_alert import PriceAlertManager
manager = PriceAlertManager()
manager.alerts.clear()
manager._save_alerts()
```

---

## 📖 详细文档

- **Web 使用指南**: [WEB_APP_GUIDE.md](WEB_APP_GUIDE.md)
- **项目总结**: [WEB_APP_SUMMARY.md](WEB_APP_SUMMARY.md)
- **主文档**: [README.md](README.md)

---

## 🎯 推荐流程

### 新手推荐流程

1. **安装依赖** (2 分钟)
   ```bash
   pip install -r requirements_web.txt
   ```

2. **启动 Web 界面**
   ```bash
   streamlit run web_app/dashboard.py
   ```

3. **查看股票分析**
   - 输入股票代码 `000001`
   - 点击"开始分析"
   - 查看 K 线图和推荐

4. **设置预警**（可选）
   ```bash
   streamlit run web_app/alert_dashboard.py
   ```

5. **运行演示**（可选）
   ```bash
   python run_monitor_demo.py
   ```

---

*版本：v4.0*
*最后更新：2026 年 3 月 22 日*
