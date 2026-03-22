# China Stock Tracker and Predictor - 中国股票分析推荐系统

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 项目简介

本项目是一个**完整的中国股票分析和推荐系统**，集成了：
- ✅ **6 种经典市场策略**（趋势跟踪、均值回归、动量、布林带、MACD、RSI）
- ✅ **股票推荐引擎**（多策略综合评分）
- ✅ **Tushare 数据导入**（真实 A 股数据）
- ✅ **股票筛选器**（多种筛选条件）
- ✅ **投资组合管理**
- ✅ **策略回测引擎**
- ✅ **SQLite 数据库存储**
- ✅ **Web 可视化仪表盘**（新增）⭐
- ✅ **实时行情预警**（新增）⭐

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

**核心依赖**:
- pandas, numpy - 数据处理
- tushare - A 股数据源（需要 token）
- scikit-learn - 机器学习
- matplotlib, seaborn, plotly - 可视化

### 2. 配置 Tushare Token（推荐）

```bash
# 获取 token: https://tushare.pro/
set TUSHARE_TOKEN=your_token_here
```

### 3. 导入股票数据

```bash
python import_tushare_data.py
# 选择 1: 导入热门股票 (30 只)
```

### 4. 运行主程序

```bash
python main.py
```

### 5. 获取股票推荐

```bash
python run_stock_recommender.py
```

---

## 🆕 Web 可视化与实时监控（新增）

### 方式 1: 启动 Web 仪表盘（推荐）

```bash
# 步骤 1: 安装 Web 依赖
pip install -r requirements_web.txt

# 步骤 2: 启动股票分析仪表盘
streamlit run web_app/dashboard.py

# 步骤 3: 启动预警监控面板（新窗口）
streamlit run web_app/alert_dashboard.py
```

**访问地址**: 
- 主仪表盘：http://localhost:8501
- 预警监控：http://localhost:8502

### 方式 2: 使用启动脚本

```bash
python start_monitor.py
# 选择菜单选项启动对应服务
```

### 方式 3: 运行演示程序

```bash
# 测试预警和通知功能
python run_monitor_demo.py
```

### 功能特性

| 功能 | 说明 | 状态 |
|------|------|------|
| 📊 **交互式 K 线图** | Plotly 可视化，支持缩放 | ✅ |
| 🎯 **智能股票推荐** | 6 种策略综合评分 | ✅ |
| 🔍 **股票筛选器** | 多维度条件筛选 | ✅ |
| 🚨 **实时价格预警** | 止损止盈自动通知 | ✅ |
| 💼 **投资组合管理** | 持仓跟踪与盈亏计算 | ✅ |
| 📈 **策略回测** | 策略收益对比 | ✅ |
| 📧 **邮件通知** | SMTP 邮件推送 | ✅ |
| 💬 **微信通知** | ServerChan 推送 | ✅ |

---

## 📦 项目结构

```
China_stock_trade/
├── 主程序
│   ├── main.py                          # 主程序入口
│   ├── strategy_analyzer.py             # 策略分析器
│   ├── stock_recommender.py             # 股票推荐引擎
│   ├── stock_screener.py                # 股票筛选器
│   ├── stock_database.py                # 数据库模块
│   ├── portfolio_manager.py             # 投资组合管理
│   ├── import_tushare_data.py           # Tushare 数据导入 ⭐
│   ├── update_prices.py                 # 价格更新器
│   ├── run_strategy_demo.py             # 策略演示
│   └── run_stock_recommender.py         # 推荐系统 UI
│
├── Web 可视化（新增）⭐
│   ├── web_app/
│   │   ├── dashboard.py                 # 股票分析仪表盘 ⭐
│   │   └── alert_dashboard.py           # 预警监控面板 ⭐
│   ├── start_monitor.py                 # 启动脚本
│   └── run_monitor_demo.py              # 演示程序
│
├── 实时监控（新增）⭐
│   ├── realtime_monitor.py              # 实时监控引擎 ⭐
│   ├── price_alert.py                   # 价格预警模块 ⭐
│   └── notification_service.py          # 通知服务 ⭐
│
├── 策略模块 (strategies/)
│   ├── base_strategy.py                 # 基础策略类
│   ├── trend_following.py               # 趋势跟踪策略
│   ├── mean_reversion.py                # 均值回归策略
│   ├── momentum.py                      # 动量策略
│   ├── bollinger_bands.py               # 布林带策略
│   ├── macd_cross.py                    # MACD 交叉策略
│   ├── rsi_strategy.py                  # RSI 策略
│   └── backtester.py                    # 策略回测引擎
│
├── 原有模块
│   ├── models/stock_predictor.py        # ML 预测模型
│   ├── utils/data_collector.py          # 数据收集
│   └── visualization/visualizer.py      # 可视化模块
│
├── 数据
│   ├── data/
│   │   ├── stock_data.db                # 股票数据库 (SQLite)
│   │   ├── portfolio.db                 # 组合管理数据库
│   │   ├── alerts.json                  # 预警配置（新增）⭐
│   │   ├── stock_recommendations_*.md   # 推荐报告
│   │   └── screen_*.csv                 # 筛选结果
│   └── queries.sql                      # SQL 查询集
│
├── 配置
│   └── config/
│       └── config.json                  # 系统配置 ⭐
│
└── 文档
    ├── README.md                        # 本文件
    ├── WEB_APP_GUIDE.md                 # Web 应用使用指南 ⭐
    ├── IMPORT_TUSHARE_GUIDE.md          # Tushare 导入指南
    ├── DATABASE_GUIDE.md                # 数据库使用指南
    ├── STOCK_RECOMMENDER_README.md      # 推荐系统说明
    ├── STRATEGIES_README.md             # 策略详细说明
    └── INSTALL_TENSORFLOW.md            # TensorFlow 安装指南
```

---

## 💡 核心功能

### 1. 市场策略分析（6 种策略）

| 策略 | 原理 | 适用市场 | 权重 |
|------|------|----------|------|
| **趋势跟踪** | 双均线交叉 | 趋势市 | 1.5 |
| **动量策略** | 追涨杀跌 | 趋势市 | 1.3 |
| **MACD 交叉** | 指标交叉 | 趋势市 | 1.2 |
| **布林带** | 触及轨道 | 震荡市 | 1.0 |
| **均值回归** | 价格回归均线 | 震荡市 | 1.0 |
| **RSI** | 超买超卖 | 震荡市 | 1.0 |

### 2. 股票推荐系统

**评分系统**: -10 到 10 分

| 评分 | 推荐等级 | 含义 |
|------|---------|------|
| 7-10 | STRONG_BUY | 强烈买入 ⭐⭐⭐ |
| 4-7 | BUY | 买入 ⭐⭐ |
| -4-4 | HOLD | 持有 ⭐ |
| -7--4 | SELL | 卖出 ⚠️ |
| -10--7 | STRONG_SELL | 强烈卖出 ⚠️⚠️ |

**输出内容**:
- 综合评分
- 推荐等级
- 目标价和止损价
- 风险评估（LOW/MEDIUM/HIGH）
- 详细推荐原因

### 3. Tushare 数据导入

**支持**:
- ✅ A 股主板（上海/深圳）
- ✅ 创业板
- ✅ 科创板
- ✅ 自动计算技术指标
- ✅ 自动生成趋势信号

**使用方法**:
```bash
python import_tushare_data.py
# 选择 1: 导入热门股票 (30 只)
```

### 4. 股票筛选器

**筛选条件**:
- 按推荐等级筛选
- 按技术指标筛选
- 均线金叉筛选
- RSI 超卖筛选
- 成交量突破筛选
- 高动量筛选
- 自定义筛选

**使用方法**:
```bash
python stock_screener.py
```

### 5. 投资组合管理

**功能**:
- 买入/卖出交易记录
- 持仓跟踪
- 盈亏计算
- 组合快照
- 交易历史

**使用方法**:
```bash
python portfolio_manager.py
```

---

## 📊 策略回测结果

**测试数据**: 260 天模拟数据

| 策略 | 总收益 (%) | 胜率 (%) | 夏普比率 | 最大回撤 (%) |
|------|-----------|---------|---------|------------|
| **Bollinger Bands** | **17.04** | 80.00 | **0.87** | 16.47 |
| Trend Following | 15.47 | 57.14 | 0.77 | 13.31 |
| Mean Reversion | 13.35 | **80.00** | 0.68 | 16.47 |
| MACD Cross | 8.95 | 50.00 | 0.47 | 17.39 |
| RSI | 6.85 | 75.00 | 0.42 | 17.89 |
| Momentum | 3.26 | 60.00 | 0.24 | **11.83** |

**最佳策略**:
- 🏆 总收益最高：Bollinger Bands (17.04%)
- 🏆 夏普比率最高：Bollinger Bands (0.87)
- 🏆 胜率最高：Mean Reversion (80.00%)
- 🏆 回撤最小：Momentum (11.83%)

---

## 🔧 使用示例

### 示例 1: 导入真实数据并分析

```bash
# 1. 配置 token
set TUSHARE_TOKEN=your_token

# 2. 导入数据
python import_tushare_data.py
# 选择 1: 导入热门股票

# 3. 运行分析
python main.py
# 输入股票代码
# 选择分析模式
```

### 示例 2: 获取股票推荐

```bash
python run_stock_recommender.py
# 选择 1: 更新价格并分析全部
```

### 示例 3: 筛选股票

```bash
python stock_screener.py
# 选择 1: 强烈买入股票
```

### 示例 4: 使用 Python API

```python
from stock_recommender import StockRecommender

recommender = StockRecommender()
signal = recommender.analyze_stock(data, '000001', '平安银行')

print(f"推荐：{signal.recommendation}")
print(f"评分：{signal.score:.2f}")
print(f"目标价：{signal.target_price}")
print(f"止损价：{signal.stop_loss}")
```

### 示例 5: SQL 查询

```sql
-- 查询最新推荐
SELECT symbol, trade_date, signal_score, recommendation
FROM trend_signals
WHERE recommendation = 'STRONG_BUY'
ORDER BY trade_date DESC
LIMIT 10;
```

---

## 📖 文档索引

| 文档 | 说明 |
|------|------|
| [README.md](README.md) | 项目总览（本文件） |
| [WEB_APP_GUIDE.md](WEB_APP_GUIDE.md) | Web 应用使用指南 ⭐⭐⭐ |
| [WEB_APP_SUMMARY.md](WEB_APP_SUMMARY.md) | Web 项目总结 ⭐⭐ |
| [IMPORT_TUSHARE_GUIDE.md](IMPORT_TUSHARE_GUIDE.md) | Tushare 数据导入指南 |
| [DATABASE_GUIDE.md](DATABASE_GUIDE.md) | 数据库使用指南 |
| [STOCK_RECOMMENDER_README.md](STOCK_RECOMMENDER_README.md) | 推荐系统说明 |
| [STRATEGIES_README.md](STRATEGIES_README.md) | 策略详细说明 |
| [TEST_REPORT.md](TEST_REPORT.md) | 测试报告 |
| [INSTALL_TENSORFLOW.md](INSTALL_TENSORFLOW.md) | TensorFlow 安装指南 |
| [queries.sql](queries.sql) | SQL 查询集 |

---

## ⚠️ 风险提示

1. **仅供参考**: 不构成投资建议
2. **历史不代表未来**: 回测成绩不代表未来表现
3. **股市有风险**: 投资需谨慎，可能损失本金
4. **及时止损**: 建议设置止损位
5. **分散投资**: 不要全仓单只股票
6. **数据延迟**: Tushare 数据可能有延迟

---

## 🏆 项目亮点

1. ✅ **6 种经典策略**综合评分
2. ✅ **Tushare Pro**真实数据支持
3. ✅ **SQLite 数据库**存储
4. ✅ **12 种 SQL 查询**模板
5. ✅ **股票筛选器**多种条件
6. ✅ **投资组合管理**功能
7. ✅ **详细文档**支持（8 个文档）
8. ✅ **交互式 UI**界面
9. ✅ **API 可扩展**设计
10. ✅ **策略回测**验证

---

## 📊 系统状态

### 已测试功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 策略分析 | ✅ 100% | 6 种策略正常工作 |
| 股票推荐 | ✅ 100% | 推荐引擎正常 |
| 数据导入 | ✅ 就绪 | 需要有效 token |
| 股票筛选 | ✅ 100% | 筛选器正常 |
| 组合管理 | ✅ 100% | 管理功能正常 |
| 回测引擎 | ✅ 100% | 回测正常 |

### 依赖包状态

| 包名 | 版本 | 状态 |
|------|------|------|
| pandas | 2.3.3 | ✅ |
| numpy | 2.0.2 | ✅ |
| tushare | 1.4.24 | ✅ |
| scikit-learn | 1.6.1 | ✅ |
| matplotlib | 3.9.4 | ✅ |
| seaborn | 0.13.2 | ✅ |
| plotly | 6.6.0 | ✅ |

---

## 🔧 常见问题

### Q1: 如何获取 Tushare token？

**A**: 
1. 访问 https://tushare.pro/
2. 免费注册账号
3. 登录后在个人中心获取 token
4. 基础数据免费使用

### Q2: 没有 token 能用吗？

**A**: 可以使用示例数据演示功能，但无法获取真实股价。

### Q3: 如何导入真实数据？

**A**: 
```bash
set TUSHARE_TOKEN=your_token
python import_tushare_data.py
```

### Q4: TensorFlow 必须安装吗？

**A**: 不必须。TensorFlow 仅用于 LSTM 深度学习预测，核心功能（策略分析、推荐）不需要 TensorFlow。

### Q5: 如何启动 Web 界面？

**A**:
```bash
# 安装依赖
pip install -r requirements_web.txt

# 启动 Web 仪表盘
streamlit run web_app/dashboard.py
```

### Q6: 如何设置价格预警？

**A**:
```python
from price_alert import PriceAlertManager

manager = PriceAlertManager()
manager.create_price_breakout_alert(
    symbol="000001",
    name="平安银行",
    breakout_price=10.5,
    above=True
)
```

### Q7: 如何配置邮件通知？

**A**:
1. 获取邮箱授权码（非登录密码）
2. 运行 `python run_monitor_demo.py` 测试
3. 或在 Web 界面配置通知设置

---

## 📝 更新日志

### v4.0 - Web 可视化与实时监控版 (2026-03-21) ⭐
- ✅ 添加 Streamlit Web 可视化仪表盘
- ✅ 添加实时行情监控引擎
- ✅ 添加价格预警系统
- ✅ 添加通知服务（邮件/微信）
- ✅ 添加预警监控 Web 界面
- ✅ 新增 10 个文件，约 3100 行代码
- ✅ 完善文档系统（2 个新文档）

### v3.0 - Tushare 数据导入版 (2026-03)
- ✅ 添加 Tushare 数据导入工具
- ✅ 添加股票筛选器
- ✅ 添加投资组合管理
- ✅ 完善文档系统
- ✅ 移除 Yahoo Finance 依赖
- ✅ 强制使用 Tushare token

### v2.0 - 市场策略增强版
- ✅ 6 种经典交易策略
- ✅ 完整策略回测引擎
- ✅ 策略比较和评估
- ✅ 策略分析报告生成

### v1.0 - 基础版
- ML 预测功能
- 技术指标计算
- 基础可视化

---

## 🎓 学习路径

### 初学者
1. 运行 `python run_strategy_demo.py` 查看策略演示
2. 阅读 [STRATEGIES_README.md](STRATEGIES_README.md) 了解策略
3. 运行 `python main.py` 分析股票
4. **新**: 启动 Web 界面 `streamlit run web_app/dashboard.py`

### 进阶用户
1. 配置 Tushare token
2. 导入真实数据：`python import_tushare_data.py`
3. 使用筛选器：`python stock_screener.py`
4. 管理投资组合：`python portfolio_manager.py`
5. **新**: 设置价格预警：`python run_monitor_demo.py`

### 高级用户
1. 修改策略参数
2. 添加自定义策略
3. 使用 SQL 查询深度分析
4. 扩展系统功能
5. **新**: 配置邮件/微信通知
6. **新**: 使用实时监控 API

---

## 📞 技术支持

- **问题反馈**: 查看文档或提交 Issue
- **文档**: 查看 [文档索引](#文档索引)
- **Tushare**: https://tushare.pro/

---

## 📜 免责声明

本工具仅供教育和研究用途，不构成财务建议。
股市有风险，投资需谨慎。
使用本系统进行的任何投资决策，风险由用户自行承担。

This tool is for educational and research purposes only. It is not financial advice.
Always do your own research and consult with qualified professionals before making investment decisions.

---

*最后更新：2026 年 3 月 22 日*
*版本：v4.0 - Web 可视化与实时监控版*
*测试状态：✅ 所有核心功能测试通过（演示程序运行成功）*
