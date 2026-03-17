# 股票推荐系统 - 完整功能总结

## 🎯 项目概述

本项目已增强为完整的**股票分析和推荐系统**，包含：
- ✅ 6 种经典市场策略
- ✅ 多策略信号综合评分
- ✅ 股票推荐引擎
- ✅ SQLite 数据库存储
- ✅ 2026 年 1 月至今数据收集
- ✅ 12 种 SQL 分析查询

---

## 📦 新增文件清单

### 核心模块
| 文件 | 功能 | 行数 |
|------|------|------|
| `stock_recommender.py` | 股票推荐引擎 | ~400 行 |
| `stock_database.py` | 数据库管理模块 | ~350 行 |
| `collect_stock_data.py` | 数据收集脚本 | ~300 行 |
| `run_stock_recommender.py` | 推荐系统 UI | ~310 行 |

### 策略模块 (strategies/)
| 文件 | 功能 |
|------|------|
| `base_strategy.py` | 基础策略类、信号、投资组合 |
| `trend_following.py` | 趋势跟踪策略 |
| `mean_reversion.py` | 均值回归策略 |
| `momentum.py` | 动量策略 |
| `bollinger_bands.py` | 布林带策略 |
| `macd_cross.py` | MACD 交叉策略 |
| `rsi_strategy.py` | RSI 策略 |
| `backtester.py` | 策略回测引擎 |

### 文档
| 文件 | 说明 |
|------|------|
| `queries.sql` | 12 种 SQL 分析查询 |
| `DATABASE_GUIDE.md` | 数据库使用指南 |
| `STOCK_RECOMMENDER_README.md` | 推荐系统说明 |
| `STRATEGIES_README.md` | 策略详细说明 |

### 更新文件
| 文件 | 更新内容 |
|------|----------|
| `main.py` | 添加股票推荐选项 |
| `README.md` | 更新为完整版说明 |

---

## 🚀 使用流程

### 方法 1: 完整流程（推荐新手）

```bash
# 步骤 1: 收集数据
python collect_stock_data.py
# 选择 1: 收集默认股票池

# 步骤 2: 获取推荐
python run_stock_recommender.py
# 选择 3: 分析股票池

# 步骤 3: 查看详细分析
python main.py
# 输入股票代码，选择 4: Get Stock Recommendation
```

### 方法 2: 快速演示

```bash
# 使用示例数据快速测试
python run_stock_recommender.py
# 选择 1: 使用示例数据演示
```

### 方法 3: 单只股票分析

```bash
python collect_stock_data.py
# 选择 2: 收集单只股票
# 输入：000001

python run_stock_recommender.py
# 选择 2: 分析单只股票
# 输入：000001
```

---

## 📊 推荐系统输出

### 综合评分系统

```
评分范围：-10 到 10

STRONG_BUY (7-10):  强烈买入 ⭐⭐⭐
BUY (4-7):          买入 ⭐⭐
HOLD (-4-4):        持有/观望 ⭐
SELL (-7--4):       卖出 ⚠️
STRONG_SELL (-10--7): 强烈卖出 ⚠️⚠️
```

### 输出示例

```
============================================================
股票：600000
============================================================
当前价格：182.43
综合评分：7.86
推荐等级：STRONG_BUY
风险等级：MEDIUM
目标价格：194.80
止损价格：173.15

推荐原因:
  - 强势金叉，趋势明显 (trend_following)
  - 动量强劲，成交量配合 (momentum)
  - MACD 金叉信号 (macd_cross)

策略信号详情:
  trend_following: 强烈买入
  mean_reversion: 持有
  momentum: 买入
  bollinger_bands: 持有
  macd_cross: 买入
  rsi: 持有

建议操作:
  🟢 强烈建议买入，多个策略发出买入信号
```

---

## 🗄️ 数据库功能

### 数据表结构

```sql
-- 股票基本信息
stocks (symbol, name, market, industry)

-- 日线价格
daily_prices (symbol, trade_date, open, high, low, close, vol)

-- 技术指标
technical_indicators (
  symbol, trade_date,
  ma5, ma10, ma20, ma30, ma60,
  ema12, ema26, macd, macd_signal, macd_hist,
  rsi, kdj_k, kdj_d, kdj_j,
  bb_upper, bb_middle, bb_lower,
  atr, obv
)

-- 趋势信号
trend_signals (
  symbol, trade_date,
  signal_score, recommendation,
  trend_strength, ma_trend, macd_trend,
  rsi_status, volume_status
)

-- 推荐记录
recommendations (
  symbol, rec_date, price, score,
  recommendation, target_price, stop_loss,
  risk_level, reasons
)
```

### SQL 查询示例

```sql
-- 获取强烈买入股票
SELECT symbol, name, signal_score, recommendation, price
FROM trend_signals t
LEFT JOIN stocks s ON t.symbol = s.symbol
LEFT JOIN daily_prices d ON t.symbol = d.symbol 
    AND t.trade_date = d.trade_date
WHERE t.recommendation = 'STRONG_BUY'
ORDER BY t.signal_score DESC;
```

---

## 📈 策略说明

### 1. 趋势跟踪 (Trend Following)
- **原理**: 双均线交叉
- **信号**: 金叉买入，死叉卖出
- **权重**: 1.5 (最高)

### 2. 动量策略 (Momentum)
- **原理**: 追涨杀跌
- **信号**: 强势 + 放量买入
- **权重**: 1.3

### 3. MACD 交叉
- **原理**: MACD 指标
- **信号**: 金叉/死叉
- **权重**: 1.2

### 4. 布林带 (Bollinger Bands)
- **原理**: 均值回归
- **信号**: 触及轨道买卖
- **权重**: 1.0

### 5. 均值回归 (Mean Reversion)
- **原理**: 价格回归均线
- **信号**: 超卖/超买
- **权重**: 1.0

### 6. RSI 策略
- **原理**: 相对强弱指标
- **信号**: RSI<30 买入，RSI>70 卖出
- **权重**: 1.0

---

## 🎯 股票池

### 默认股票池 (50 只)

**银行金融**: 平安银行、招商银行、工商银行、中国平安
**消费**: 贵州茅台、五粮液、美的集团、格力电器
**科技**: 中兴通讯、科大讯飞、海康威视、宁德时代
**医药**: 恒瑞医药、药明康德、片仔癀、迈瑞医疗
**新能源**: 比亚迪、隆基股份、阳光电源、华友钴业

### 自定义股票池

```python
from run_stock_recommender import StockPoolManager

pool = StockPoolManager()
pool.add_stock('000001', '平安银行')
pool.add_stock('600519', '贵州茅台')
```

---

## 📁 输出文件

### 1. 推荐报告 (Markdown)

位置：`data/stock_recommendations_YYYYMMDD_HHMMSS.md`

内容:
- 推荐摘要表格
- 重点推荐股票详情
- 推荐原因
- 风险提示

### 2. 股票分析数据 (CSV)

位置：`data/{symbol}_analysis.csv`

内容:
- 价格数据
- 技术指标
- 趋势信号

### 3. 数据库 (SQLite)

位置：`data/stock_data.db`

内容:
- 所有历史数据
- 技术指标
- 推荐记录

---

## 🔧 API 使用

### 推荐引擎 API

```python
from stock_recommender import StockRecommender

# 创建推荐引擎
recommender = StockRecommender()

# 分析单只股票
signal = recommender.analyze_stock(data, '000001', '平安银行')
print(f"推荐：{signal.recommendation}")
print(f"评分：{signal.score:.2f}")

# 分析多只股票
recommender.analyze_multiple_stocks(stock_data_dict)

# 获取买入推荐
buy_recs = recommender.get_buy_recommendations(top_n=5)
for s in buy_recs:
    print(f"{s.symbol}: {s.recommendation} ({s.score:.2f})")

# 生成报告
recommender.generate_report(save_path='report.md')
```

### 数据库 API

```python
from stock_database import StockDatabase

db = StockDatabase()

# 获取价格数据
prices = db.get_stock_prices('000001', '20260101')

# 获取技术指标
indicators = db.get_technical_indicators('000001')

# 趋势分析
trend = db.get_price_trend_analysis('000001')

# 股票池分析
analysis = db.get_stock_pool_analysis(['000001', '600519'])

db.close()
```

---

## ⚠️ 风险提示

1. **仅供参考**: 不构成投资建议
2. **历史不代表未来**: 回测成绩不代表未来表现
3. **股市有风险**: 投资需谨慎，可能损失本金
4. **及时止损**: 建议设置止损位
5. **分散投资**: 不要全仓单只股票

---

## 📖 文档索引

| 文档 | 说明 |
|------|------|
| [README.md](README.md) | 项目总览 |
| [DATABASE_GUIDE.md](DATABASE_GUIDE.md) | 数据库使用指南 |
| [STOCK_RECOMMENDER_README.md](STOCK_RECOMMENDER_README.md) | 推荐系统说明 |
| [STRATEGIES_README.md](STRATEGIES_README.md) | 策略详细说明 |
| [queries.sql](queries.sql) | SQL 查询集 |

---

## 🎓 学习路径

### 初学者
1. 阅读 README.md
2. 运行 `python run_stock_recommender.py` (选择 1)
3. 查看输出结果

### 进阶用户
1. 收集真实数据：`python collect_stock_data.py`
2. 分析股票池
3. 查看 SQL 查询：`queries.sql`

### 高级用户
1. 使用 API 自定义分析
2. 修改策略参数
3. 添加自定义策略

---

## 📊 系统架构

```
┌─────────────────────────────────────────────────┐
│              用户界面层                          │
│  main.py  run_stock_recommender.py             │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│              业务逻辑层                          │
│  stock_recommender.py  strategy_analyzer.py    │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│              策略模块层                          │
│  strategies/ (6 种策略)                         │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│              数据访问层                          │
│  stock_database.py  collect_stock_data.py      │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│              数据存储层                          │
│  data/stock_data.db (SQLite)                   │
└─────────────────────────────────────────────────┘
```

---

*最后更新：2026 年 3 月 16 日*
*版本：v2.0 - 股票推荐增强版*
