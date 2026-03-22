import sqlite3

conn = sqlite3.connect('data/stock_data.db')
cursor = conn.cursor()

# Check data range for 000001
cursor.execute('SELECT MIN(trade_date), MAX(trade_date), COUNT(*) FROM daily_prices WHERE symbol = "000001"')
result = cursor.fetchone()
print(f'平安银行 (000001) 数据范围: {result[0]} 到 {result[1]}, 共 {result[2]} 条记录')

# Get recent 5 records
cursor.execute('SELECT trade_date, close FROM daily_prices WHERE symbol = "000001" ORDER BY trade_date DESC LIMIT 5')
recent = cursor.fetchall()
print('最近5条记录:')
for row in recent:
    print(f'{row[0]}: ¥{row[1]:.2f}')

conn.close()