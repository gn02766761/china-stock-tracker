# Tushare 数据导入 SQL 指南

## 📌 功能概述

本工具用于从 **Tushare Pro** 导入真实的 A 股股票数据到 SQLite 数据库，包含：
- 股票价格数据（OHLCV）
- 技术指标（MA/MACD/RSI/KDJ/BB/ATR/OBV）
- 趋势信号（评分/推荐）

---

## 🚀 使用方法

### 方法 1: 使用导入工具（推荐）

```bash
python import_tushare_data.py
```

**选项**:
1. 导入热门股票 (30 只)
2. 导入单只股票
3. 自定义股票列表
4. 查看数据库摘要

### 方法 2: 使用 Python API

```python
from import_tushare_data import TushareDataImporter

# 创建导入器
importer = TushareDataImporter(token='your_token')

# 导入单只股票
importer.import_stock_data('000001.SZ', '平安银行', '20260101')

# 批量导入
stock_list = [
    {'ts_code': '000001.SZ', 'name': '平安银行'},
    {'ts_code': '600519.SH', 'name': '贵州茅台'}
]
importer.import_stock_pool(stock_list)

# 查看数据库摘要
summary = importer.get_database_summary()
print(summary)

importer.close()
```

### 方法 3: 设置环境变量后导入

```bash
# 设置 token
set TUSHARE_TOKEN=your_token

# 运行导入
python import_tushare_data.py
# 选择 1: 导入热门股票
```

---

## 📊 导入流程

### 1. 配置 Tushare Token

```bash
# 方法 1: 运行时输入
python import_tushare_data.py
# 输入 token

# 方法 2: 环境变量
set TUSHARE_TOKEN=your_token
python import_tushare_data.py
```

### 2. 选择导入模式

**模式 1: 热门股票**
- 导入 30 只热门 A 股
- 包含银行、消费、科技、医药、新能源
- 适合快速建立股票池

**模式 2: 单只股票**
- 导入指定股票
- 适合单独分析

**模式 3: 自定义列表**
- 导入自定义股票列表
- 适合特定投资组合

### 3. 数据处理

导入器自动完成：
1. 从 Tushare 获取日线数据
2. 计算技术指标
3. 生成趋势信号
4. 保存到 SQLite 数据库

---

## 📁 数据库结构

### 数据表

| 表名 | 说明 | 字段 |
|------|------|------|
| `stocks` | 股票基本信息 | symbol, name, market, industry |
| `daily_prices` | 日线价格 | symbol, trade_date, open, high, low, close, vol |
| `technical_indicators` | 技术指标 | MA, MACD, RSI, KDJ, BB, ATR, OBV |
| `trend_signals` | 趋势信号 | signal_score, recommendation, trend_strength |

### 查询示例

```sql
-- 查询最新价格
SELECT symbol, trade_date, close, pct_chg
FROM daily_prices
WHERE symbol = '000001'
ORDER BY trade_date DESC
LIMIT 10;

-- 查询技术指标
SELECT trade_date, ma5, ma10, macd, rsi
FROM technical_indicators
WHERE symbol = '000001'
ORDER BY trade_date DESC
LIMIT 10;

-- 查询推荐信号
SELECT trade_date, signal_score, recommendation
FROM trend_signals
WHERE symbol = '000001'
ORDER BY trade_date DESC
LIMIT 10;
```

---

## 💡 使用示例

### 示例 1: 导入贵州茅台数据

```bash
python import_tushare_data.py
# 选择 2: 导入单只股票
# 输入：600519.SH
# 名称：贵州茅台
```

### 示例 2: 导入银行板块

```python
from import_tushare_data import TushareDataImporter

importer = TushareDataImporter(token='your_token')

bank_stocks = [
    {'ts_code': '000001.SZ', 'name': '平安银行'},
    {'ts_code': '600000.SH', 'name': '浦发银行'},
    {'ts_code': '600036.SH', 'name': '招商银行'},
    {'ts_code': '601398.SH', 'name': '工商银行'},
]

importer.import_stock_pool(bank_stocks)
importer.close()
```

### 示例 3: 查看数据库状态

```bash
python import_tushare_data.py
# 选择 4: 查看数据库摘要
```

---

## 🔧 故障排除

### 问题 1: Token 无效

**错误**: `您的 token 不对，请确认`

**解决**:
- 检查 token 是否正确复制
- 在 tushare.pro 重新生成 token

### 问题 2: 无数据

**错误**: `无数据`

**解决**:
- 检查股票代码格式（000001.SZ 或 600519.SH）
- 检查日期范围是否正确

### 问题 3: 导入中断

**原因**: 网络问题或 API 限制

**解决**:
- 等待 1 分钟后重试
- 减少单次导入数量
- 提高 Tushare 积分

---

## 📈 导入的股票列表

### 默认热门股票（30 只）

**银行金融** (6 只):
- 000001.SZ 平安银行
- 000002.SZ 万科 A
- 600000.SH 浦发银行
- 600036.SH 招商银行
- 601318.SH 中国平安
- 601398.SH 工商银行

**消费** (6 只):
- 000858.SZ 五粮液
- 600519.SH 贵州茅台
- 600809.SH 山西汾酒
- 600887.SH 伊利股份
- 000333.SZ 美的集团
- 000651.SZ 格力电器

**科技** (6 只):
- 000063.SZ 中兴通讯
- 000725.SZ 京东方 A
- 002230.SZ 科大讯飞
- 002415.SZ 海康威视
- 300059.SZ 东方财富
- 300750.SZ 宁德时代

**医药** (6 只):
- 000538.SZ 云南白药
- 002007.SZ 华兰生物
- 300122.SZ 智飞生物
- 300760.SZ 迈瑞医疗
- 600276.SH 恒瑞医药
- 600436.SH 片仔癀

**新能源** (6 只):
- 002594.SZ 比亚迪
- 300014.SZ 亿纬锂能
- 300274.SZ 阳光电源
- 601012.SH 隆基股份
- 603799.SH 华友钴业

---

## 📖 相关文档

- [TUSHARE_SETUP.md](TUSHARE_SETUP.md) - Tushare 配置指南
- [DATABASE_GUIDE.md](DATABASE_GUIDE.md) - 数据库使用指南
- [PRICE_UPDATE_TUSHARE.md](PRICE_UPDATE_TUSHARE.md) - 价格更新指南

---

*最后更新：2026 年 3 月*
