"""
测试价格更新器功能
"""

import sys
sys.path.append('.')

from update_prices import RealTimePriceUpdater

def test_updater():
    """测试更新器"""
    print("=" * 70)
    print("测试价格更新器")
    print("=" * 70)
    
    # 创建更新器（不使用 token，使用示例数据）
    print("\n使用示例数据测试...")
    updater = RealTimePriceUpdater(token=None)
    
    # 测试更新单只股票
    print("\n测试 1: 更新单只股票 (000001)")
    print("-" * 50)
    result = updater.update_single_stock('000001', '平安银行')
    
    print(f"  结果：{result['success']}")
    print(f"  消息：{result['message']}")
    print(f"  最新价格：{result['latest_price']}")
    print(f"  数据源：{result['data_source']}")
    
    # 测试更新摘要
    print("\n测试 2: 查看更新摘要")
    print("-" * 50)
    summary = updater.get_update_summary()
    print(summary.to_string(index=False))
    
    updater.close()
    
    print("\n" + "=" * 70)
    print("测试完成!")
    print("=" * 70)

if __name__ == "__main__":
    test_updater()
