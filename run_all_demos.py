"""
项目功能演示总览

展示所有可用的功能和模块
"""

import sys
import os

def print_header(text):
    """打印标题"""
    print("\n" + "=" * 70)
    print(text.center(70))
    print("=" * 70 + "\n")

def print_menu():
    """打印菜单"""
    print_header("中国股票分析推荐系统 - 功能总览")
    
    print("""
📊 可用功能模块:

1. 主程序分析 (main.py)
   - ML 预测（线性回归/随机森林）
   - 策略分析
   - 股票推荐
   
2. 策略演示 (run_strategy_demo.py)
   - 6 种策略回测比较
   - 策略性能评估
   
3. 股票推荐 (run_stock_recommender.py)
   - 多策略综合评分
   - 买入/卖出推荐
   - 目标价/止损价
   
4. 数据收集 (collect_stock_data.py)
   - 收集 2026 年 1 月至今数据
   - 存储到 SQLite 数据库
   
5. 股票筛选 (stock_screener.py)
   - 按推荐等级筛选
   - 按技术指标筛选
   - 自定义条件筛选
   
6. 投资组合 (portfolio_manager.py)
   - 买入/卖出交易
   - 持仓跟踪
   - 盈亏计算
   
7. SQL 查询 (queries.sql)
   - 12 种分析查询
   - 自定义查询
   
8. 查看文档
   - README.md
   - DATABASE_GUIDE.md
   - STOCK_RECOMMENDER_SUMMARY.md

""")
    
    print("-" * 70)
    choice = input("请选择功能 (1-8, 或 q 退出): ").strip()
    return choice

def run_module(choice):
    """运行选择的模块"""
    modules = {
        '1': ('python main.py', '主程序'),
        '2': ('python run_strategy_demo.py', '策略演示'),
        '3': ('python run_stock_recommender.py', '股票推荐'),
        '4': ('python collect_stock_data.py', '数据收集'),
        '5': ('python stock_screener.py', '股票筛选'),
        '6': ('python portfolio_manager.py', '投资组合'),
        '7': ('查看 queries.sql', 'SQL 查询'),
        '8': ('查看文档', '文档列表')
    }
    
    if choice not in modules:
        print("无效选择！")
        return
    
    cmd, name = modules[choice]
    print(f"\n运行 {name}...")
    
    if choice == '7':
        print("\nSQL 查询文件内容:")
        print("-" * 70)
        with open('queries.sql', 'r', encoding='utf-8') as f:
            content = f.read()
            # 显示前 50 行
            lines = content.split('\n')[:50]
            for line in lines:
                print(line)
            if len(lines) < len(content.split('\n')):
                print(f"... (共 {len(content.split(chr(10)))} 行，使用编辑器查看完整内容)")
    
    elif choice == '8':
        print("\n可用文档:")
        print("-" * 70)
        docs = [
            'README.md - 项目总览',
            'DATABASE_GUIDE.md - 数据库使用指南',
            'STOCK_RECOMMENDER_README.md - 推荐系统说明',
            'STOCK_RECOMMENDER_SUMMARY.md - 完整总结',
            'STRATEGIES_README.md - 策略详细说明',
            'PROJECT_FINAL_SUMMARY.md - 最终总结',
            'queries.sql - SQL 查询集'
        ]
        for doc in docs:
            print(f"  - {doc}")
        
        # 询问是否查看某个文档
        doc_choice = input("\n查看哪个文档？(输入编号或名称): ").strip()
        doc_files = {
            '1': 'README.md',
            '2': 'DATABASE_GUIDE.md',
            '3': 'STOCK_RECOMMENDER_README.md',
            '4': 'STOCK_RECOMMENDER_SUMMARY.md',
            '5': 'STRATEGIES_README.md',
            '6': 'PROJECT_FINAL_SUMMARY.md'
        }
        
        if doc_choice in doc_files:
            os.system(f'type {doc_files[doc_choice]}')
        elif doc_choice in doc_files.values():
            os.system(f'type {doc_choice}')
    
    else:
        # 运行 Python 脚本
        os.system(cmd)

def quick_demo():
    """快速演示（使用示例数据）"""
    print_header("快速演示")
    
    print("运行策略演示（使用示例数据）...")
    print("-" * 70)
    os.system('echo 1 | python run_strategy_demo.py')
    
    print("\n" + "=" * 70)
    print("演示完成！")
    print("=" * 70)

def main():
    """主函数"""
    print_header("中国股票分析推荐系统")
    
    print("""
欢迎使用中国股票分析推荐系统！

本系统包含以下功能:
✅ 6 种市场策略（趋势跟踪、均值回归、动量、布林带、MACD、RSI）
✅ 股票推荐引擎（多策略综合评分）
✅ SQLite 数据库存储（2026 年 1 月至今数据）
✅ 股票筛选器（多种筛选条件）
✅ 投资组合管理
✅ 12 种 SQL 分析查询

""")
    
    # 选择模式
    print("选择运行模式:")
    print("1. 功能菜单（查看所有模块）")
    print("2. 快速演示（使用示例数据）")
    print("3. 退出")
    
    choice = input("\n请输入选择 (1-3): ").strip()
    
    if choice == '1':
        while True:
            cmd = print_menu()
            if cmd.lower() == 'q':
                break
            run_module(cmd)
            
            cont = input("\n继续选择其他功能？(y/n): ").strip().lower()
            if cont != 'y':
                break
    
    elif choice == '2':
        quick_demo()
    
    elif choice == '3':
        print("\n感谢使用，再见！")
        return
    
    else:
        print("无效选择！")
    
    print_header("程序结束")

if __name__ == "__main__":
    main()
