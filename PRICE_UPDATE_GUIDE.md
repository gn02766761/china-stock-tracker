# 实时价格更新功能说明

## 📌 功能概述

系统现在支持实时价格更新，可以从 **Tushare Pro** 获取最新股票价格并更新到数据库。

**数据源**: Tushare Pro（中国 A 股专业数据源）

---

## 🚀 使用方法

### 方法 1: 使用价格更新器

```bash
python update_prices.py
```

**选项**:
1. 更新默认股票池 (3 只)
2. 更新单只股票
3. 自定义股票列表
4. 查看更新摘要

### 方法 2: 使用增强版推荐系统

```bash
python run_stock_recommender_enhanced.py
```

**选项**:
1. 更新价格并分析全部 (推荐)
2. 分析股票池 (不更新)
3. 分析单只股票
4. 自定义股票分析
5. 仅更新价格

---

## 📊 更新流程

### 1. 检查数据库
- 查询最后更新日期
- 计算需要更新的日期范围

### 2. 获取新数据（Tushare）
- 从 Tushare Pro 获取价格数据
- 包含 OHLCV 和涨跌幅
- 需要有效的 Tushare token

### 3. 保存到数据库
- 插入价格数据到 `daily_prices` 表
- 计算技术指标并保存到 `technical_indicators` 表
- 生成趋势信号并保存到 `trend_signals` 表

### 4. 分析推荐
- 运行 6 种策略分析
- 生成综合评分
- 输出推荐等级

---

## ⚠️ 注意事项

### Tushare 配置

**获取 Token**:
1. 访问 https://tushare.pro/ 注册
2. 登录后在个人中心获取 token
3. 基础数据免费使用
4. 积分可提高访问权限

**Token 限制**:
- 基础用户：每分钟 100 次调用
- 积分用户：更高调用限制
- 建议批量更新时控制频率

### 交易时间

- A 股交易时间：周一至周五 9:30-11:30, 13:00-15:00
- 非交易时间获取的是最后收盘价
- 周末和节假日数据不会更新

---

## 🔧 故障排除

### 问题 1: "Tushare token 无效"

**原因**: Token 未正确配置

**解决方法**:
- 检查 token 是否正确复制
- 确认已在 tushare.pro 注册
- 重新获取 token

### 问题 2: "无新数据"

**原因**: 
- 已经是最新数据
- 非交易时间

**解决方法**:
- 检查数据库最后更新日期
- 等待下一个交易日

### 问题 3: 数据不正确

**原因**: 
- 股票代码格式错误
- 数据源问题

**解决方法**:
- 检查股票代码格式（000xxx.SZ 或 600xxx.SH）
- 联系 Tushare 支持

---

## 💡 推荐用法

### 每日更新（推荐）

```bash
# 每天早上更新股票池
python update_prices.py
# 选择 1: 更新默认股票池
```

### 分析单只股票

```bash
python run_stock_recommender_enhanced.py
# 选择 3: 分析单只股票
# 输入：000001
```

### 批量更新和分析

```bash
python run_stock_recommender_enhanced.py
# 选择 1: 更新价格并分析全部
```

---

## 📁 数据库结构

### 更新的数据表

| 表名 | 更新内容 |
|------|----------|
| `daily_prices` | 新增价格记录 |
| `technical_indicators` | 计算并更新指标 |
| `trend_signals` | 生成趋势信号 |

### 查询最新数据

```sql
-- 查询最新价格
SELECT symbol, trade_date, close, pct_chg
FROM daily_prices
WHERE symbol = '000001'
ORDER BY trade_date DESC
LIMIT 10;

-- 查询最新信号
SELECT symbol, trade_date, signal_score, recommendation
FROM trend_signals
WHERE symbol = '000001'
ORDER BY trade_date DESC
LIMIT 10;
```

---

## 📖 相关文档

- [DATABASE_GUIDE.md](DATABASE_GUIDE.md) - 数据库使用指南
- [STOCK_RECOMMENDER_README.md](STOCK_RECOMMENDER_README.md) - 推荐系统说明
- [queries.sql](queries.sql) - SQL 查询集

---

*最后更新：2026 年 3 月*
