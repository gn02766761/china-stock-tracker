# Tushare 配置指南

## 📌 为什么使用 Tushare？

Tushare Pro 是中国 A 股专业数据源，提供：
- ✅ 完整的 A 股历史数据
- ✅ 实时行情数据
- ✅ 财务指标数据
- ✅ 高数据质量
- ✅ 免费基础服务

---

## 🚀 快速开始

### 步骤 1: 注册账号

访问 https://tushare.pro/ 注册免费账号

### 步骤 2: 获取 Token

1. 登录后点击右上角用户名
2. 选择"个人主页"
3. 在"接口 Token"标签页复制你的 token

### 步骤 3: 配置 Token

#### 方法 1: 在程序中输入
```bash
python update_prices.py
# 程序会提示输入 token
```

#### 方法 2: 设置环境变量
```bash
# Windows
set TUSHARE_TOKEN=your_token_here

# Linux/Mac
export TUSHARE_TOKEN=your_token_here
```

#### 方法 3: 在代码中设置
```python
import tushare as ts
ts.set_token('your_token_here')
```

---

## 💡 Token 积分说明

### 基础积分（注册即得）
- 每分钟 100 次调用
- 足够日常使用

### 提高积分
- 每日签到：+10 积分/天
- 分享项目：+100 积分
- 贡献代码：+500 积分

### 积分用途
- 更多数据接口
- 更高调用频率
- 更详细的数据

---

## ⚠️ 常见问题

### Q1: 没有 token 会怎样？

系统会提示你配置 token，无法获取真实数据。

**解决方法**: 注册获取免费 token

### Q2: Token 无效？

**原因**:
- Token 复制错误
- Token 被重置

**解决方法**:
- 重新复制 token
- 在 tushare.pro 重新生成

### Q3: 调用次数超限？

**原因**: 基础用户每分钟 100 次调用

**解决方法**:
- 等待 1 分钟
- 减少调用频率
- 签到提高积分

---

## 📊 数据覆盖

### A 股主板
- 上海证券交易所 (600xxx)
- 深圳证券交易所 (000xxx)

### 创业板
- 深圳创业板 (300xxx)

### 科创板
- 上海科创板 (688xxx)

---

## 🔧 使用示例

### 更新价格
```bash
python update_prices.py
# 输入 token
# 选择 1: 更新默认股票池
```

### 分析股票
```bash
python run_stock_recommender_enhanced.py
# 选择 1: 更新价格并分析全部
```

### 查询数据
```bash
python query_stock.py
# 选择 1: 查询 000001
```

---

## 📖 相关文档

- [PRICE_UPDATE_GUIDE.md](PRICE_UPDATE_GUIDE.md) - 价格更新指南
- [README.md](README.md) - 项目总览
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 项目总结

---

*最后更新：2026 年 3 月*
