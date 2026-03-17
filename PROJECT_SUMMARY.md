# China Stock Tracker and Predictor - 完整项目总结

## 📌 项目概述

本项目是一个**完整的中国股票分析和推荐系统**，集成了市场策略、股票推荐、数据库管理、投资组合管理等功能。系统使用 6 种经典市场策略进行综合评分，为用户提供买卖建议和风险提示。

---

## 🎯 核心功能

### 1. 市场策略分析（6 种策略）
- ✅ **趋势跟踪策略** - 双均线交叉识别趋势
- ✅ **均值回归策略** - 价格回归均线
- ✅ **动量策略** - 追涨杀跌
- ✅ **布林带策略** - 触及轨道买卖
- ✅ **MACD 交叉策略** - 指标交叉信号
- ✅ **RSI 策略** - 超买超卖判断

### 2. 股票推荐系统
- ✅ 多策略信号综合评分（-10 到 10 分）
- ✅ 推荐等级（STRONG_BUY 到 STRONG_SELL）
- ✅ 目标价和止损价自动计算
- ✅ 风险评估（LOW/MEDIUM/HIGH）
- ✅ 详细推荐原因

### 3. 数据库功能
- ✅ SQLite 存储（5 个数据表）
- ✅ 2026 年 1 月至今数据收集
- ✅ 技术指标计算和存储
- ✅ 趋势信号生成
- ✅ 12 种 SQL 分析查询

### 4. 股票筛选器
- ✅ 按推荐等级筛选
- ✅ 按技术指标筛选
- ✅ 均线金叉筛选
- ✅ RSI 超卖筛选
- ✅ 成交量突破筛选
- ✅ 高动量筛选
- ✅ 自定义筛选

### 5. 投资组合管理
- ✅ 买入/卖出交易记录
- ✅ 持仓跟踪
- ✅ 盈亏计算
- ✅ 组合快照
- ✅ 交易历史

### 6. 实时价格更新
- ✅ 从 **Tushare Pro** 获取最新数据（主要数据源）
- ✅ 自动更新数据库
- ✅ 计算技术指标
- ✅ 生成趋势信号
- ✅ 支持本地 CSV 文件导入

### 7. 机器学习预测
- ✅ 线性回归
- ✅ 随机森林
- ✅ LSTM 神经网络
- ✅ 回测验证

---

## 📦 完整文件清单

### 核心模块（13 个）
| 文件 | 功能 | 行数 |
|------|------|------|
| `main.py` | 主程序入口 | ~350 |
| `strategy_analyzer.py` | 策略分析器 | ~450 |
| `stock_recommender.py` | 股票推荐引擎 | ~400 |
| `stock_screener.py` | 股票筛选器 | ~350 |
| `stock_database.py` | 数据库模块 | ~350 |
| `portfolio_manager.py` | 投资组合管理 | ~400 |
| `update_prices.py` | 价格更新器 | ~400 |
| `collect_stock_data.py` | 数据收集脚本 | ~300 |
| `run_strategy_demo.py` | 策略演示 | ~170 |
| `run_stock_recommender.py` | 推荐系统 UI | ~270 |
| `run_stock_recommender_enhanced.py` | 增强版推荐 | ~235 |
| `query_stock.py` | 股票查询工具 | ~210 |
| `run_all_demos.py` | 功能演示总览 | ~200 |

### 策略模块（strategies/ 8 个）
| 文件 | 功能 |
|------|------|
| `base_strategy.py` | 基础策略类、信号枚举、投资组合 |
| `trend_following.py` | 趋势跟踪策略 |
| `mean_reversion.py` | 均值回归策略 |
| `momentum.py` | 动量策略 |
| `bollinger_bands.py` | 布林带策略 |
| `macd_cross.py` | MACD 交叉策略 |
| `rsi_strategy.py` | RSI 策略 |
| `backtester.py` | 策略回测引擎 |

### 原有模块
| 文件 | 功能 |
|------|------|
| `models/stock_predictor.py` | ML 预测模型 |
| `utils/data_collector.py` | 数据收集 |
| `visualization/visualizer.py` | 可视化模块 |

### 数据库和查询
| 文件 | 说明 |
|------|------|
| `queries.sql` | 12 种 SQL 查询模板 |
| `data/stock_data.db` | 股票数据 SQLite |
| `data/portfolio.db` | 组合管理 SQLite |

### 文档（8 个）
| 文件 | 说明 |
|------|------|
| `README.md` | 项目总览 |
| `PROJECT_FINAL_SUMMARY.md` | 最终总结 |
| `DATABASE_GUIDE.md` | 数据库使用指南 |
| `STOCK_RECOMMENDER_README.md` | 推荐系统说明 |
| `STOCK_RECOMMENDER_SUMMARY.md` | 推荐系统总结 |
| `STRATEGIES_README.md` | 策略详细说明 |
| `PRICE_UPDATE_GUIDE.md` | 价格更新指南 |
| `MARKET_STRATEGY_UPDATE.md` | 策略更新说明 |

---

## 🚀 快速开始

### 安装依赖
```bash
pip install pandas numpy matplotlib seaborn scikit-learn tushare tensorflow plotly requests beautifulsoup4
```

### 配置 Tushare Token（推荐）
```bash
# 1. 访问 https://tushare.pro/ 注册
# 2. 获取免费 token
# 3. 在程序中输入 token
```

### 使用方法

#### 1. 主程序（包含所有功能）
```bash
python main.py
# 选择：1=ML 预测，2=策略分析，3=策略比较，4=股票推荐
```

#### 2. 策略演示
```bash
python run_strategy_demo.py
# 比较 6 种策略性能
```

#### 3. 股票推荐
```bash
python run_stock_recommender_enhanced.py
# 选择 1: 更新价格并分析全部（推荐）
```

#### 4. 股票筛选
```bash
python stock_screener.py
# 按条件筛选股票
```

#### 5. 价格更新（使用 Tushare）
```bash
python update_prices.py
# 从 Tushare 获取最新数据
```

#### 6. 投资组合
```bash
python portfolio_manager.py
# 管理持仓和盈亏
```

#### 7. 查询股票
```bash
python query_stock.py
# 查询单只股票数据
```

#### 8. 功能演示总览
```bash
python run_all_demos.py
# 查看所有可用功能
```

---

## 📊 系统架构

```
┌─────────────────────────────────────────────────┐
│              用户界面层                          │
│  main.py  run_*.py  query_stock.py             │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│              业务逻辑层                          │
│  stock_recommender.py  strategy_analyzer.py    │
│  stock_screener.py  portfolio_manager.py       │
│  update_prices.py                               │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│              策略模块层                          │
│  strategies/ (6 种策略 + 回测引擎)              │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│              数据访问层                          │
│  stock_database.py  collect_stock_data.py      │
│  utils/data_collector.py (Tushare)             │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│              数据存储层                          │
│  data/stock_data.db (SQLite)                   │
│  data/portfolio.db (SQLite)                     │
└─────────────────────────────────────────────────┘
```

---

## 📈 核心特性

### 评分系统
```
综合评分：-10 到 10 分

STRONG_BUY (7-10):  强烈买入 ⭐⭐⭐
BUY (4-7):          买入 ⭐⭐
HOLD (-4-4):        持有 ⭐
SELL (-7--4):       卖出 ⚠️
STRONG_SELL (-10--7): 强烈卖出 ⚠️⚠️
```

### 策略权重
| 策略 | 权重 | 说明 |
|------|------|------|
| 趋势跟踪 | 1.5 | 核心策略 |
| 动量 | 1.3 | 重视 momentum |
| MACD | 1.2 | 经典指标 |
| 布林带 | 1.0 | 标准权重 |
| 均值回归 | 1.0 | 标准权重 |
| RSI | 1.0 | 标准权重 |

### 技术指标
- **均线**: MA5, MA10, MA20, MA30, MA60
- **MACD**: MACD 线，信号线，柱状图
- **RSI**: 相对强弱指标
- **KDJ**: 随机指标
- **布林带**: 上轨，中轨，下轨
- **ATR**: 平均真实波幅
- **OBV**: 能量潮

---

## 🗄️ 数据库结构

### 数据表（5 个）
| 表名 | 说明 | 主要字段 |
|------|------|----------|
| `stocks` | 股票基本信息 | symbol, name, market, industry |
| `daily_prices` | 日线价格 | symbol, trade_date, open, high, low, close, vol |
| `technical_indicators` | 技术指标 | MA, MACD, RSI, KDJ, BB, ATR, OBV |
| `trend_signals` | 趋势信号 | signal_score, recommendation, trend_strength |
| `recommendations` | 推荐记录 | score, target_price, stop_loss, result_return |

### SQL 查询（12 种）
1. 获取最新价格和技术指标
2. 获取所有股票最新趋势信号
3. 获取强烈买入股票
4. 获取价格趋势分析
5. 获取均线多头排列股票
6. 获取 RSI 超卖/超买股票
7. 获取 MACD 金叉/死叉股票
8. 获取布林带突破股票
9. 获取成交量异常放大股票
10. 获取综合评分最高股票
11. 获取推荐历史及结果
12. 获取月度涨跌幅统计

---

## 💻 使用示例

### 示例 1: 获取强烈买入股票
```bash
python stock_screener.py
# 选择 1: 强烈买入股票
```

### 示例 2: 分析单只股票
```bash
python run_stock_recommender_enhanced.py
# 选择 3: 分析单只股票
# 输入：000001
```

### 示例 3: 更新价格（使用 Tushare）
```bash
python update_prices.py
# 选择 1: 更新默认股票池
# 使用 Tushare 数据源
```

### 示例 4: 使用 API
```python
from stock_recommender import StockRecommender

recommender = StockRecommender()
signal = recommender.analyze_stock(data, '000001', '平安银行')

print(f"推荐：{signal.recommendation}")
print(f"评分：{signal.score:.2f}")
print(f"目标价：{signal.target_price}")
print(f"止损价：{signal.stop_loss}")
```

### 示例 5: 管理投资组合
```python
from portfolio_manager import Portfolio

portfolio = Portfolio(initial_cash=1000000)
portfolio.buy('000001', 1000, 15.00)
portfolio.buy('600519', 100, 1500.00)
portfolio.update_prices({'000001': 16.00, '600519': 1600.00})
portfolio.print_summary()
```

---

## 📁 项目结构

```
China_stock_trade/
├── 主程序
│   ├── main.py                          # 主程序入口
│   ├── strategy_analyzer.py             # 策略分析器
│   ├── stock_recommender.py             # 股票推荐引擎
│   ├── stock_screener.py                # 股票筛选器
│   ├── stock_database.py                # 数据库模块
│   ├── portfolio_manager.py             # 组合管理
│   ├── update_prices.py                 # 价格更新器
│   ├── collect_stock_data.py            # 数据收集
│   ├── run_strategy_demo.py             # 策略演示
│   ├── run_stock_recommender.py         # 推荐 UI
│   ├── run_stock_recommender_enhanced.py # 增强版推荐
│   ├── query_stock.py                   # 股票查询
│   └── run_all_demos.py                 # 功能演示总览
│
├── 策略模块 (strategies/)
│   ├── base_strategy.py                 # 基础类
│   ├── trend_following.py               # 趋势跟踪
│   ├── mean_reversion.py                # 均值回归
│   ├── momentum.py                      # 动量
│   ├── bollinger_bands.py               # 布林带
│   ├── macd_cross.py                    # MACD
│   ├── rsi_strategy.py                  # RSI
│   └── backtester.py                    # 回测引擎
│
├── 原有模块
│   ├── models/stock_predictor.py        # ML 预测
│   ├── utils/data_collector.py          # 数据收集
│   └── visualization/visualizer.py      # 可视化
│
├── 数据
│   ├── data/
│   │   ├── stock_data.db                # 股票数据库
│   │   ├── portfolio.db                 # 组合数据库
│   │   ├── stock_recommendations_*.md   # 推荐报告
│   │   ├── screen_*.csv                 # 筛选结果
│   │   └── *_analysis.csv               # 分析数据
│   └── queries.sql                      # SQL 查询集
│
└── 文档
    ├── README.md                        # 项目总览
    ├── PROJECT_FINAL_SUMMARY.md         # 最终总结
    ├── DATABASE_GUIDE.md                # 数据库指南
    ├── STOCK_RECOMMENDER_README.md      # 推荐说明
    ├── STOCK_RECOMMENDER_SUMMARY.md     # 推荐总结
    ├── STRATEGIES_README.md             # 策略说明
    ├── PRICE_UPDATE_GUIDE.md            # 价格更新指南
    └── MARKET_STRATEGY_UPDATE.md        # 策略更新
```

---

## ⚠️ 风险提示

1. **仅供参考**: 不构成投资建议
2. **历史不代表未来**: 回测成绩不代表未来表现
3. **股市有风险**: 投资需谨慎，可能损失本金
4. **及时止损**: 建议设置止损位
5. **分散投资**: 不要全仓单只股票
6. **数据延迟**: Tushare 数据可能有延迟，请以交易所实时数据为准

---

## 📖 文档索引

| 文档 | 说明 |
|------|------|
| [README.md](README.md) | 项目总览和快速开始 |
| [PROJECT_FINAL_SUMMARY.md](PROJECT_FINAL_SUMMARY.md) | 完整功能总结 |
| [DATABASE_GUIDE.md](DATABASE_GUIDE.md) | 数据库使用指南 |
| [STOCK_RECOMMENDER_README.md](STOCK_RECOMMENDER_README.md) | 推荐系统说明 |
| [STOCK_RECOMMENDER_SUMMARY.md](STOCK_RECOMMENDER_SUMMARY.md) | 推荐系统总结 |
| [STRATEGIES_README.md](STRATEGIES_README.md) | 策略详细说明 |
| [PRICE_UPDATE_GUIDE.md](PRICE_UPDATE_GUIDE.md) | 价格更新指南 |
| [queries.sql](queries.sql) | SQL 查询集 |

---

## 🎓 学习路径

### 初学者
1. 运行 `python run_all_demos.py` 查看所有功能
2. 运行 `python run_stock_recommender.py` (选择 3 使用示例数据)
3. 阅读 [README.md](README.md)

### 进阶用户
1. 收集数据：`python collect_stock_data.py`
2. 更新价格：`python update_prices.py`
3. 筛选股票：`python stock_screener.py`
4. 使用 API 自定义分析

### 高级用户
1. 修改策略参数
2. 添加自定义策略
3. 使用 SQL 查询深度分析
4. 扩展投资组合管理功能

---

## 🏆 项目亮点

1. ✅ **6 种经典策略**综合评分
2. ✅ **完整数据库**支持（SQLite）
3. ✅ **12 种 SQL 查询**模板
4. ✅ **股票筛选器**多种条件
5. ✅ **投资组合管理**功能
6. ✅ **实时价格更新**
7. ✅ **详细文档**支持（8 个文档）
8. ✅ **交互式 UI**界面
9. ✅ **API 可扩展**设计
10. ✅ **机器学习预测**集成

---

## 📊 统计信息

- **总代码量**: 约 5000+ 行
- **Python 模块**: 21 个
- **策略模块**: 8 个
- **文档**: 8 个
- **SQL 查询**: 12 种
- **数据表**: 5 个
- **策略数量**: 6 种

---

## 🔧 技术栈

- **Python**: 3.7+
- **数据处理**: pandas, numpy
- **机器学习**: scikit-learn, tensorflow
- **可视化**: matplotlib, plotly, seaborn
- **数据库**: SQLite
- **数据源**: Tushare Pro（中国 A 股专业数据源）

---

*版本：v3.0 - 完整版*  
*最后更新：2026 年 3 月 16 日*  
*总代码量：约 5000 行*
