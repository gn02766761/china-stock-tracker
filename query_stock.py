"""
查询单只股票数据 - 000001 平安银行示例
"""

import sqlite3
import pandas as pd
from datetime import datetime


def query_stock(symbol: str = '000001', db_path: str = 'data/stock_data.db'):
    """查询股票数据"""
    try:
        conn = sqlite3.connect(db_path)
    except Exception as e:
        print(f"无法连接数据库：{e}")
        print("提示：请先运行 python collect_stock_data.py 收集数据")
        return
    
    print("=" * 80)
    print(f"股票查询：{symbol}")
    print("=" * 80)
    
    # 1. 股票基本信息
    print("\n【1. 股票基本信息】")
    query = "SELECT * FROM stocks WHERE symbol = ?"
    df = pd.read_sql_query(query, conn, params=(symbol,))
    if not df.empty:
        for col in df.columns:
            print(f"  {col}: {df[col].iloc[0]}")
    else:
        print(f"未找到股票 {symbol}")
    
    # 2. 最新价格
    print("\n【2. 最新价格 (最近 20 天)】")
    query = """
        SELECT trade_date, open, high, low, close, pct_chg, vol
        FROM daily_prices
        WHERE symbol = ?
        ORDER BY trade_date DESC
        LIMIT 20
    """
    df = pd.read_sql_query(query, conn, params=(symbol,))
    if not df.empty:
        print(df.to_string(index=False))
    else:
        print("暂无数据")
    
    # 3. 技术指标
    print("\n【3. 技术指标 (最近 10 天)】")
    query = """
        SELECT trade_date, ma5, ma10, ma20, macd, macd_signal, rsi
        FROM technical_indicators
        WHERE symbol = ?
        ORDER BY trade_date DESC
        LIMIT 10
    """
    df = pd.read_sql_query(query, conn, params=(symbol,))
    if not df.empty:
        print(df.round(2).to_string(index=False))
    else:
        print("暂无数据")
    
    # 4. 趋势信号
    print("\n【4. 趋势信号 (最近 10 天)】")
    query = """
        SELECT trade_date, signal_score, recommendation, trend_strength, 
               ma_trend, macd_trend, rsi_status
        FROM trend_signals
        WHERE symbol = ?
        ORDER BY trade_date DESC
        LIMIT 10
    """
    df = pd.read_sql_query(query, conn, params=(symbol,))
    if not df.empty:
        print(df.to_string(index=False))
        
        # 统计
        print("\n推荐统计:")
        print(df['recommendation'].value_counts().to_string())
    else:
        print("暂无数据")
    
    # 5. 价格趋势
    print("\n【5. 价格趋势分析】")
    query = """
        SELECT 
            COUNT(*) as days,
            MIN(trade_date) as start_date,
            MAX(trade_date) as end_date,
            MIN(close) as min_price,
            MAX(close) as max_price,
            AVG(close) as avg_price
        FROM daily_prices
        WHERE symbol = ?
    """
    df = pd.read_sql_query(query, conn, params=(symbol,))
    if not df.empty:
        row = df.iloc[0]
        print(f"  交易天数：{row['days']}")
        print(f"  日期范围：{row['start_date']} 至 {row['end_date']}")
        print(f"  价格范围：{row['min_price']:.2f} - {row['max_price']:.2f}")
        print(f"  平均价格：{row['avg_price']:.2f}")
        
        # 获取最新价
        latest = pd.read_sql_query(
            "SELECT close FROM daily_prices WHERE symbol = ? ORDER BY trade_date DESC LIMIT 1",
            conn, params=(symbol,)
        )
        if not latest.empty:
            print(f"  最新价格：{latest['close'].iloc[0]:.2f}")
    
    # 6. 均线关系
    print("\n【6. 最新均线关系】")
    query = """
        SELECT 
            d.trade_date, d.close, i.ma5, i.ma10, i.ma20, i.ma60
        FROM daily_prices d
        LEFT JOIN technical_indicators i 
            ON d.symbol = i.symbol AND d.trade_date = i.trade_date
        WHERE d.symbol = ?
        ORDER BY d.trade_date DESC
        LIMIT 5
    """
    df = pd.read_sql_query(query, conn, params=(symbol,))
    if not df.empty:
        df_rounded = df.round(2)
        print(df_rounded.to_string(index=False))
        
        # 判断排列（检查是否有 None 值）
        latest = df.iloc[0]
        if pd.notna(latest['ma5']) and pd.notna(latest['ma10']) and pd.notna(latest['ma20']):
            if latest['ma5'] > latest['ma10'] > latest['ma20']:
                print("\n形态：多头排列 ✓")
            elif latest['ma5'] < latest['ma10'] < latest['ma20']:
                print("\n形态：空头排列 ✗")
            else:
                print("\n形态：震荡")
        else:
            print("\n形态：暂无足够数据")
    else:
        print("暂无数据")
    
    conn.close()
    print("\n" + "=" * 80)


def query_all_stocks_summary():
    """查询所有股票汇总"""
    try:
        conn = sqlite3.connect('data/stock_data.db')
    except:
        print("无法连接数据库")
        return
    
    print("\n" + "=" * 80)
    print("所有股票最新汇总 (按评分排序)")
    print("=" * 80)
    
    query = """
        SELECT 
            t.symbol, s.name, d.close as price, d.pct_chg,
            t.signal_score, t.recommendation, i.rsi
        FROM trend_signals t
        LEFT JOIN stocks s ON t.symbol = s.symbol
        LEFT JOIN daily_prices d 
            ON t.symbol = d.symbol AND t.trade_date = d.trade_date
        LEFT JOIN technical_indicators i 
            ON t.symbol = i.symbol AND t.trade_date = i.trade_date
        WHERE t.trade_date = (
            SELECT MAX(trade_date) FROM trend_signals WHERE symbol = t.symbol
        )
        ORDER BY t.signal_score DESC
        LIMIT 30
    """
    
    df = pd.read_sql_query(query, conn)
    if not df.empty:
        print(df.round(2).to_string(index=False))
    else:
        print("暂无数据")
    
    conn.close()


if __name__ == "__main__":
    print("=" * 80)
    print("股票数据查询工具")
    print("=" * 80)
    
    print("\n选择查询模式:")
    print("1. 查询 000001 (默认)")
    print("2. 查询所有股票汇总")
    print("3. 自定义股票")
    
    choice = input("\n请选择 (1-3, 默认 1): ").strip() or '1'
    
    if choice == '1':
        query_stock('000001')
    elif choice == '2':
        query_all_stocks_summary()
    elif choice == '3':
        symbol = input("股票代码：").strip()
        if symbol:
            query_stock(symbol)
    else:
        print("无效选择")
