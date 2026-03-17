# 股票数据库使用指南

## 📌 概述

本项目使用 SQLite 数据库存储 2026 年 1 月至今的股票价格、技术指标和趋势信号数据，为股票推荐系统提供准确的数据支持。

---

## 🗄️ 数据库结构

### 数据表

| 表名 | 说明 | 主要字段 |
|------|------|----------|
| `stocks` | 股票基本信息 | symbol, name, market, industry |
| `daily_prices` | 日线价格数据 | symbol, trade_date, open, high, low, close, vol |
| `technical_indicators` | 技术指标 | MA, EMA, MACD, RSI, KDJ, Bollinger Bands, ATR |
| `trend_signals` | 趋势信号 | signal_score, recommendation, trend_strength |
| `recommendations` | 推荐记录 | score, target_price, stop_loss, result_return |

### 数据库位置

```
data/stock_data.db
```

---

## 🚀 快速开始

### 1. 收集股票数据

```bash
python collect_stock_data.py
```

**选择模式**:
1. 收集默认股票池 (50 只热门股票)
2. 收集单只股票
3. 自定义股票列表
4. 创建示例数据

### 2. 查看收集结果

```bash
python -c "
from stock_database import StockDatabase
db = StockDatabase()
print(db.get_collected_stocks())
db.close()
"
```

### 3. 使用推荐系统

```bash
python run_stock_recommender.py
```

---

## 📊 SQL 查询示例

### 查询 1: 获取最新趋势信号排名

```sql
SELECT 
    t.symbol,
    s.name,
    t.signal_score,
    t.recommendation,
    d.close as price
FROM trend_signals t
LEFT JOIN stocks s ON t.symbol = s.symbol
LEFT JOIN daily_prices d 
    ON t.symbol = d.symbol AND t.trade_date = d.trade_date
WHERE t.trade_date = (
    SELECT MAX(trade_date) FROM trend_signals 
    WHERE symbol = t.symbol
)
ORDER BY t.signal_score DESC
LIMIT 20;
```

### 查询 2: 获取强烈买入股票

```sql
SELECT 
    t.symbol,
    s.name,
    t.signal_score,
    t.recommendation,
    i.ma20,
    i.rsi,
    i.macd
FROM trend_signals t
LEFT JOIN stocks s ON t.symbol = s.symbol
LEFT JOIN daily_prices d 
    ON t.symbol = d.symbol AND t.trade_date = d.trade_date
LEFT JOIN technical_indicators i 
    ON t.symbol = i.symbol AND t.trade_date = i.trade_date
WHERE t.recommendation = 'STRONG_BUY'
ORDER BY t.signal_score DESC;
```

### 查询 3: 获取 RSI 超卖股票

```sql
SELECT 
    t.symbol,
    s.name,
    i.rsi,
    d.close as price
FROM technical_indicators i
LEFT JOIN stocks s ON i.symbol = s.symbol
LEFT JOIN daily_prices d 
    ON i.symbol = d.symbol AND i.trade_date = d.trade_date
WHERE i.rsi < 30
ORDER BY i.rsi ASC;
```

### 查询 4: 使用 Python 查询

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('data/stock_data.db')

# 查询强烈买入股票
query = """
SELECT symbol, name, signal_score, recommendation, price
FROM (
    SELECT 
        t.symbol,
        s.name,
        t.signal_score,
        t.recommendation,
        d.close as price,
        ROW_NUMBER() OVER (PARTITION BY t.symbol ORDER BY t.trade_date DESC) as rn
    FROM trend_signals t
    LEFT JOIN stocks s ON t.symbol = s.symbol
    LEFT JOIN daily_prices d ON t.symbol = d.symbol AND t.trade_date = d.trade_date
)
WHERE rn = 1 AND recommendation = 'STRONG_BUY'
ORDER BY signal_score DESC
"""

df = pd.read_sql_query(query, conn)
print(df)

conn.close()
```

---

## 📈 技术指标说明

### 均线系统

| 指标 | 周期 | 说明 |
|------|------|------|
| MA5 | 5 日 | 短期趋势 |
| MA10 | 10 日 | 短期趋势 |
| MA20 | 20 日 | 中期趋势（月线） |
| MA30 | 30 日 | 中期趋势 |
| MA60 | 60 日 | 长期趋势（季线） |

### MACD

| 字段 | 说明 |
|------|------|
| macd | MACD 线（快线 - 慢线） |
| macd_signal | 信号线（MACD 的 EMA） |
| macd_hist | 柱状图（MACD - Signal） |

**用法**:
- MACD > Signal: 金叉，看涨
- MACD < Signal: 死叉，看跌

### RSI

| 范围 | 状态 | 说明 |
|------|------|------|
| < 30 | OVERSOLD | 超卖，可能反弹 |
| 30-70 | NEUTRAL | 中性 |
| > 70 | OVERBOUGHT | 超买，可能回调 |

### 布林带

| 字段 | 说明 |
|------|------|
| bb_upper | 上轨（MA20 + 2σ） |
| bb_middle | 中轨（MA20） |
| bb_lower | 下轨（MA20 - 2σ） |

**用法**:
- 价格触及下轨：买入信号
- 价格触及上轨：卖出信号

---

## 🎯 趋势信号评分系统

### 评分标准

| 分数 | 推荐 | 含义 |
|------|------|------|
| 7-10 | STRONG_BUY | 强烈买入 |
| 4-7 | BUY | 买入 |
| -4-4 | HOLD | 持有/观望 |
| -7--4 | SELL | 卖出 |
| -10--7 | STRONG_SELL | 强烈卖出 |

### 评分因素

1. **均线趋势** (+/- 2 分)
   - 价格在 MA20 上方：+2
   - 价格在 MA20 下方：-2

2. **MACD 趋势** (+/- 2 分)
   - MACD > Signal: +2
   - MACD < Signal: -2

3. **RSI 状态** (+/- 2 分)
   - RSI < 30 (超卖): +2
   - RSI > 70 (超买): -2

4. **成交量** (+/- 1 分)
   - 放量上涨：+1
   - 放量下跌：-1

---

## 📁 数据收集流程

### 1. 初始化数据库

```python
from stock_database import StockDatabase

db = StockDatabase('data/stock_data.db')
db._create_tables()
```

### 2. 收集价格数据

```python
from utils.data_collector import StockDataCollector

collector = StockDataCollector()
data = collector.get_stock_data('000001', '20260101', '20260316')

# 保存到数据库
prices_df = data.copy()
prices_df['trade_date'] = prices_df.index.strftime('%Y%m%d')
db.insert_daily_prices('000001', prices_df)
```

### 3. 计算技术指标

```python
# 计算指标
data_with_indicators = collector.calculate_technical_indicators(data)

# 保存指标
indicators_df = data_with_indicators.copy()
indicators_df['trade_date'] = indicators_df.index.strftime('%Y%m%d')
db.insert_technical_indicators('000001', indicators_df)
```

### 4. 生成趋势信号

```python
# 在 collect_stock_data.py 中自动完成
# 趋势信号会自动保存到 trend_signals 表
```

---

## 🔧 数据库维护

### 清理旧数据

```sql
-- 删除 2026 年之前的数据
DELETE FROM daily_prices WHERE trade_date < '20260101';
DELETE FROM technical_indicators WHERE trade_date < '20260101';
DELETE FROM trend_signals WHERE trade_date < '20260101';
```

### 优化查询性能

```sql
-- 创建索引
CREATE INDEX IF NOT EXISTS idx_prices_symbol ON daily_prices(symbol);
CREATE INDEX IF NOT EXISTS idx_prices_date ON daily_prices(trade_date);
CREATE INDEX IF NOT EXISTS idx_signals_score ON trend_signals(signal_score DESC);
```

### 导出数据

```python
from stock_database import StockDatabase

db = StockDatabase()
db.export_to_csv('000001', 'data/000001_analysis.csv')
db.close()
```

---

## 📊 使用示例

### 示例 1: 获取推荐股票池

```python
from stock_database import StockDatabase

db = StockDatabase()

# 获取所有强烈买入股票
buy_stocks = db.get_latest_trend_signals(limit=50)
buy_stocks = buy_stocks[buy_stocks['recommendation'] == 'STRONG_BUY']

print(buy_stocks[['symbol', 'name', 'signal_score', 'recommendation']])

db.close()
```

### 示例 2: 分析单只股票

```python
db = StockDatabase()

# 获取价格和技术指标
prices = db.get_stock_prices('000001', '20260101')
indicators = db.get_technical_indicators('000001', '20260101')

# 趋势分析
trend = db.get_price_trend_analysis('000001')
print(f"当前价格：{trend['current_price']:.2f}")
print(f"均线趋势：{trend['ma_trend']}")
print(f"趋势强度：{trend['trend_strength']}")

db.close()
```

---

## ⚠️ 注意事项

1. **数据更新**: 建议每日收盘后更新数据
2. **备份数据库**: 定期备份 `data/stock_data.db`
3. **数据质量**: 检查数据完整性，避免缺失值
4. **权限管理**: 数据库文件设置适当权限

---

## 📖 相关文档

- [README.md](README.md) - 项目总览
- [STOCK_RECOMMENDER_README.md](STOCK_RECOMMENDER_README.md) - 推荐系统说明
- [queries.sql](queries.sql) - SQL 查询集

---

*最后更新：2026 年 3 月*
