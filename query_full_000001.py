import sqlite3
import pandas as pd

conn = sqlite3.connect('data/stock_data.db')

query = '''
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
'''

df = pd.read_sql_query(query, conn)
print("Stock 000001 - Recent Data with Technical Indicators:")
print(df.head(10).to_string(index=False))
conn.close()