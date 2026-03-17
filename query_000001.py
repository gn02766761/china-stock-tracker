import sqlite3

conn = sqlite3.connect('data/stock_data.db')
cursor = conn.cursor()

# Query for 000001
cursor.execute('''
SELECT symbol, trade_date, close, pct_chg, vol
FROM daily_prices
WHERE symbol = '000001'
ORDER BY trade_date DESC
LIMIT 10
''')

rows = cursor.fetchall()
print("Recent data for stock 000001:")
print("Symbol | Date | Close | Change% | Volume")
print("-" * 50)
for row in rows:
    print(f"{row[0]} | {row[1]} | {row[2]:.2f} | {row[3]:.2f}% | {row[4]}")

conn.close()