-- ================================================================
-- 股票数据分析 SQL 查询集
-- 用于查询 2026 年 1 月至今的股票价格和技术指标数据
-- ================================================================

-- 1. 获取单只股票的最新价格和技术指标
-- ================================================================
SELECT 
    d.symbol,
    d.trade_date,
    d.close as price,
    d.pct_chg as price_change_pct,
    d.vol as volume,
    i.ma5,
    i.ma10,
    i.ma20,
    i.macd,
    i.macd_signal,
    i.rsi,
    i.bb_upper,
    i.bb_lower,
    CASE 
        WHEN d.close > i.ma20 THEN 'BULLISH'
        ELSE 'BEARISH'
    END as trend
FROM daily_prices d
LEFT JOIN technical_indicators i 
    ON d.symbol = i.symbol AND d.trade_date = i.trade_date
WHERE d.symbol = '000001'
ORDER BY d.trade_date DESC
LIMIT 30;

-- 2. 获取所有股票的最新趋势信号（按评分排序）
-- ================================================================
SELECT 
    t.symbol,
    s.name,
    t.trade_date,
    t.signal_score,
    t.recommendation,
    t.trend_strength,
    t.ma_trend,
    t.macd_trend,
    t.rsi_status,
    d.close as current_price,
    d.pct_chg
FROM trend_signals t
LEFT JOIN stocks s ON t.symbol = s.symbol
LEFT JOIN daily_prices d 
    ON t.symbol = d.symbol AND t.trade_date = d.trade_date
WHERE t.trade_date = (
    SELECT MAX(trade_date) FROM trend_signals 
    WHERE symbol = t.symbol
)
ORDER BY t.signal_score DESC
LIMIT 50;

-- 3. 获取强烈买入信号的股票
-- ================================================================
SELECT 
    t.symbol,
    s.name,
    t.trade_date,
    t.signal_score,
    d.close as price,
    d.pct_chg,
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
AND t.trade_date = (
    SELECT MAX(trade_date) FROM trend_signals 
    WHERE symbol = t.symbol
)
ORDER BY t.signal_score DESC;

-- 4. 获取股票价格趋势分析（2026 年至今）
-- ================================================================
SELECT 
    symbol,
    COUNT(*) as trading_days,
    MIN(trade_date) as start_date,
    MAX(trade_date) as end_date,
    FIRST(close) as start_price,
    LAST(close) as end_price,
    (LAST(close) - FIRST(close)) / FIRST(close) * 100 as total_return_pct,
    MAX(close) as highest_price,
    MIN(close) as lowest_price,
    AVG(vol) as avg_volume
FROM daily_prices
WHERE trade_date >= '20260101'
GROUP BY symbol
ORDER BY total_return_pct DESC;

-- 5. 获取均线多头排列的股票
-- ================================================================
SELECT 
    d.symbol,
    s.name,
    d.close as price,
    i.ma5,
    i.ma10,
    i.ma20,
    CASE 
        WHEN i.ma5 > i.ma10 AND i.ma10 > i.ma20 THEN 'YES'
        ELSE 'NO'
    END as bullish_arrangement
FROM daily_prices d
LEFT JOIN stocks s ON d.symbol = s.symbol
LEFT JOIN technical_indicators i 
    ON d.symbol = i.symbol AND d.trade_date = i.trade_date
WHERE d.trade_date = (
    SELECT MAX(trade_date) FROM daily_prices 
    WHERE symbol = d.symbol
)
AND i.ma5 > i.ma10 
AND i.ma10 > i.ma20
AND d.close > i.ma5
ORDER BY d.pct_chg DESC;

-- 6. 获取 RSI 超卖/超买股票
-- ================================================================
-- RSI < 30 超卖
SELECT 
    t.symbol,
    s.name,
    i.rsi,
    d.close as price,
    'OVERSOLD' as status
FROM technical_indicators i
LEFT JOIN stocks s ON i.symbol = s.symbol
LEFT JOIN daily_prices d 
    ON i.symbol = d.symbol AND i.trade_date = d.trade_date
LEFT JOIN trend_signals t
    ON i.symbol = t.symbol AND i.trade_date = t.trade_date
WHERE i.rsi < 30
AND i.trade_date = (
    SELECT MAX(trade_date) FROM technical_indicators 
    WHERE symbol = i.symbol
)
ORDER BY i.rsi ASC
LIMIT 20;

-- RSI > 70 超买
SELECT 
    t.symbol,
    s.name,
    i.rsi,
    d.close as price,
    'OVERBOUGHT' as status
FROM technical_indicators i
LEFT JOIN stocks s ON i.symbol = s.symbol
LEFT JOIN daily_prices d 
    ON i.symbol = d.symbol AND i.trade_date = d.trade_date
LEFT JOIN trend_signals t
    ON i.symbol = t.symbol AND i.trade_date = t.trade_date
WHERE i.rsi > 70
AND i.trade_date = (
    SELECT MAX(trade_date) FROM technical_indicators 
    WHERE symbol = i.symbol
)
ORDER BY i.rsi DESC
LIMIT 20;

-- 7. 获取 MACD 金叉/死叉股票
-- ================================================================
-- MACD 金叉（MACD > Signal）
SELECT 
    t.symbol,
    s.name,
    i.macd,
    i.macd_signal,
    (i.macd - i.macd_signal) as macd_diff,
    d.close as price,
    'GOLDEN_CROSS' as signal
FROM technical_indicators i
LEFT JOIN stocks s ON i.symbol = s.symbol
LEFT JOIN daily_prices d 
    ON i.symbol = d.symbol AND i.trade_date = d.trade_date
LEFT JOIN trend_signals t
    ON i.symbol = t.symbol AND i.trade_date = t.trade_date
WHERE i.macd > i.macd_signal
AND i.trade_date = (
    SELECT MAX(trade_date) FROM technical_indicators 
    WHERE symbol = i.symbol
)
ORDER BY (i.macd - i.macd_signal) DESC
LIMIT 20;

-- 8. 获取布林带突破股票
-- ================================================================
-- 触及下轨（可能反弹）
SELECT 
    t.symbol,
    s.name,
    d.close as price,
    i.bb_lower,
    i.bb_middle,
    i.bb_upper,
    (d.close - i.bb_lower) / i.bb_lower * 100 as deviation_pct,
    'TOUCH_LOWER' as position
FROM technical_indicators i
LEFT JOIN stocks s ON i.symbol = s.symbol
LEFT JOIN daily_prices d 
    ON i.symbol = d.symbol AND i.trade_date = d.trade_date
LEFT JOIN trend_signals t
    ON i.symbol = t.symbol AND i.trade_date = t.trade_date
WHERE d.close <= i.bb_lower * 1.02
AND i.trade_date = (
    SELECT MAX(trade_date) FROM technical_indicators 
    WHERE symbol = i.symbol
)
ORDER BY (d.close - i.bb_lower) / i.bb_lower ASC
LIMIT 20;

-- 触及上轨（可能回调）
SELECT 
    t.symbol,
    s.name,
    d.close as price,
    i.bb_lower,
    i.bb_middle,
    i.bb_upper,
    (d.close - i.bb_upper) / i.bb_upper * 100 as deviation_pct,
    'TOUCH_UPPER' as position
FROM technical_indicators i
LEFT JOIN stocks s ON i.symbol = s.symbol
LEFT JOIN daily_prices d 
    ON i.symbol = d.symbol AND i.trade_date = d.trade_date
LEFT JOIN trend_signals t
    ON i.symbol = t.symbol AND i.trade_date = t.trade_date
WHERE d.close >= i.bb_upper * 0.98
AND i.trade_date = (
    SELECT MAX(trade_date) FROM technical_indicators 
    WHERE symbol = i.symbol
)
ORDER BY (d.close - i.bb_upper) / i.bb_upper DESC
LIMIT 20;

-- 9. 获取成交量异常放大股票
-- ================================================================
SELECT 
    d.symbol,
    s.name,
    d.close as price,
    d.vol as current_volume,
    i.obv,
    (SELECT AVG(vol) FROM daily_prices 
     WHERE symbol = d.symbol 
     AND trade_date >= date(d.trade_date, '-20 days')
    ) as avg_volume_20d,
    d.vol / (SELECT AVG(vol) FROM daily_prices 
     WHERE symbol = d.symbol 
     AND trade_date >= date(d.trade_date, '-20 days')
    ) as volume_ratio
FROM daily_prices d
LEFT JOIN stocks s ON d.symbol = s.symbol
LEFT JOIN technical_indicators i 
    ON d.symbol = i.symbol AND d.trade_date = i.trade_date
WHERE d.trade_date = (
    SELECT MAX(trade_date) FROM daily_prices 
    WHERE symbol = d.symbol
)
AND d.vol > (SELECT AVG(vol) * 2 FROM daily_prices 
     WHERE symbol = d.symbol 
     AND trade_date >= date(d.trade_date, '-20 days')
    )
ORDER BY volume_ratio DESC
LIMIT 20;

-- 10. 获取综合评分最高的股票（推荐组合）
-- ================================================================
SELECT 
    t.symbol,
    s.name,
    t.signal_score,
    t.recommendation,
    d.close as price,
    d.pct_chg,
    i.ma20,
    i.rsi,
    i.macd,
    t.ma_trend,
    t.macd_trend,
    t.rsi_status,
    CASE 
        WHEN t.signal_score >= 7 THEN '⭐⭐⭐ 强烈建议'
        WHEN t.signal_score >= 4 THEN '⭐⭐ 建议关注'
        WHEN t.signal_score >= -4 THEN '⭐ 观望'
        ELSE '⚠️ 注意风险'
    END as rating
FROM trend_signals t
LEFT JOIN stocks s ON t.symbol = s.symbol
LEFT JOIN daily_prices d 
    ON t.symbol = d.symbol AND t.trade_date = d.trade_date
LEFT JOIN technical_indicators i 
    ON t.symbol = i.symbol AND t.trade_date = i.trade_date
WHERE t.trade_date = (
    SELECT MAX(trade_date) FROM trend_signals 
    WHERE symbol = t.symbol
)
ORDER BY t.signal_score DESC
LIMIT 30;

-- 11. 获取股票历史推荐记录及结果
-- ================================================================
SELECT 
    r.symbol,
    s.name,
    r.rec_date,
    r.recommendation,
    r.price as rec_price,
    r.target_price,
    r.stop_loss,
    r.result_price,
    r.result_return,
    CASE 
        WHEN r.result_return > 10 THEN '✅ 优秀'
        WHEN r.result_return > 5 THEN '✔️ 良好'
        WHEN r.result_return > 0 THEN '➖ 持平'
        ELSE '❌ 亏损'
    END as performance
FROM recommendations r
LEFT JOIN stocks s ON r.symbol = s.symbol
WHERE r.result_price IS NOT NULL
ORDER BY r.result_return DESC
LIMIT 50;

-- 12. 获取 2026 年每月涨跌幅统计
-- ================================================================
SELECT 
    symbol,
    strftime('%Y-%m', trade_date) as month,
    FIRST(close) as month_start,
    LAST(close) as month_end,
    (LAST(close) - FIRST(close)) / FIRST(close) * 100 as monthly_return_pct,
    MAX(high) as month_high,
    MIN(low) as month_low,
    SUM(vol) as month_volume
FROM daily_prices
WHERE trade_date >= '20260101'
GROUP BY symbol, strftime('%Y-%m', trade_date)
ORDER BY symbol, month;

-- ================================================================
-- 使用示例
-- ================================================================

-- 在 Python 中使用:
-- import sqlite3
-- conn = sqlite3.connect('data/stock_data.db')
-- df = pd.read_sql_query(query, conn)

-- 在命令行使用:
-- sqlite3 data/stock_data.db < queries.sql
