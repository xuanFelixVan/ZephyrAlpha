"""
合规检查模块使用示例
演示如何使用compliance_checker模块进行监管合规检查
"""
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.modules.compliance_checker import (
    ComplianceChecker,
    OrderRecord,
    create_compliance_checker,
    ComplianceLevel,
    TradingBehaviorType
)


def example_basic_usage():
    """基本使用示例"""
    print("=" * 80)
    print("示例1: 基本使用 - 检查订单合规性")
    print("=" * 80)
    
    checker = create_compliance_checker()
    
    order = OrderRecord(
        order_id='ORDER_001',
        symbol='000001.SZ',
        direction='buy',
        quantity=1000,
        price=10.5,
        order_type='limit',
        timestamp=datetime.now(),
        status='submitted'
    )
    
    result = checker.check_order_before_submission(
        order=order,
        position_pct=0.03,
        last_trade_date=datetime.now() - timedelta(days=30)
    )
    
    print(f"\n订单ID: {order.order_id}")
    print(f"股票代码: {order.symbol}")
    print(f"交易方向: {order.direction}")
    print(f"数量: {order.quantity}")
    print(f"价格: {order.price}")
    print(f"\n合规检查结果:")
    print(f"  是否合规: {result.is_compliant}")
    print(f"  合规级别: {result.compliance_level.value}")
    print(f"  行为类型: {result.behavior_type.value}")
    
    if result.warnings:
        print(f"\n警告信息:")
        for warning in result.warnings:
            print(f"  - {warning}")
    
    if result.violations:
        print(f"\n违规信息:")
        for violation in result.violations:
            print(f"  - {violation}")
    
    if result.recommendations:
        print(f"\n建议:")
        for rec in result.recommendations:
            print(f"  - {rec}")


def example_high_frequency_check():
    """高频交易检查示例"""
    print("\n" + "=" * 80)
    print("示例2: 高频交易认定检查")
    print("=" * 80)
    
    checker = create_compliance_checker()
    
    print("\n模拟高频交易场景：每秒提交20笔订单...")
    base_time = datetime.now()
    
    for i in range(20):
        order = OrderRecord(
            order_id=f'HF_ORDER_{i:03d}',
            symbol='000001.SZ',
            direction='buy',
            quantity=100,
            price=10.5,
            order_type='limit',
            timestamp=base_time,
            status='submitted'
        )
        checker.order_tracker.add_order(order)
    
    result = checker.check_high_frequency_trading()
    
    print(f"\n高频交易检查结果:")
    print(f"  是否合规: {result.is_compliant}")
    print(f"  合规级别: {result.compliance_level.value}")
    print(f"  行为类型: {result.behavior_type.value}")
    
    if result.warnings:
        print(f"\n警告信息:")
        for warning in result.warnings:
            print(f"  - {warning}")
    
    print(f"\n详细统计:")
    stats = result.details.get('daily_stats', {})
    print(f"  总订单数: {stats.get('total_orders', 0)}")
    print(f"  每秒最大订单数: {stats.get('max_orders_per_second', 0)}")
    print(f"  每秒最大总操作数: {stats.get('max_total_per_second', 0)}")


def example_cancel_limit_check():
    """撤单限制检查示例"""
    print("\n" + "=" * 80)
    print("示例3: 撤单限制检查")
    print("=" * 80)
    
    checker = create_compliance_checker()
    
    print("\n模拟撤单场景：提交100笔订单，撤单20笔...")
    base_time = datetime.now()
    
    for i in range(100):
        order = OrderRecord(
            order_id=f'ORDER_{i:03d}',
            symbol='000001.SZ',
            direction='buy',
            quantity=100,
            price=10.5,
            order_type='limit',
            timestamp=base_time + timedelta(seconds=i),
            status='submitted'
        )
        checker.order_tracker.add_order(order)
    
    for i in range(20):
        order_id = f'ORDER_{i:03d}'
        cancel_time = base_time + timedelta(seconds=i, microseconds=100)
        checker.order_tracker.record_cancel(order_id, cancel_time)
    
    result = checker.check_cancel_limits()
    
    print(f"\n撤单限制检查结果:")
    print(f"  是否合规: {result.is_compliant}")
    print(f"  合规级别: {result.compliance_level.value}")
    
    if result.warnings:
        print(f"\n警告信息:")
        for warning in result.warnings:
            print(f"  - {warning}")
    
    print(f"\n详细统计:")
    stats = result.details.get('daily_stats', {})
    print(f"  总订单数: {stats.get('total_orders', 0)}")
    print(f"  总撤单数: {stats.get('total_cancels', 0)}")
    print(f"  撤单率: {stats.get('cancel_rate', 0):.2%}")


def example_short_term_trading_check():
    """短线交易检查示例"""
    print("\n" + "=" * 80)
    print("示例4: 短线交易合规检查")
    print("=" * 80)
    
    checker = create_compliance_checker()
    
    print("\n场景1: 持仓3%（非大股东）")
    result1 = checker.check_short_term_trading(
        symbol='000001.SZ',
        position_pct=0.03,
        is_buy=True,
        last_trade_date=datetime.now() - timedelta(days=30)
    )
    print(f"  是否合规: {result1.is_compliant}")
    print(f"  合规级别: {result1.compliance_level.value}")
    
    print("\n场景2: 持仓6%（大股东），上次交易2个月前")
    result2 = checker.check_short_term_trading(
        symbol='000001.SZ',
        position_pct=0.06,
        is_buy=False,
        last_trade_date=datetime.now() - timedelta(days=60)
    )
    print(f"  是否合规: {result2.is_compliant}")
    print(f"  合规级别: {result2.compliance_level.value}")
    if result2.violations:
        print(f"  违规信息: {result2.violations[0]}")
    
    print("\n场景3: 持仓6%（大股东），上次交易7个月前")
    result3 = checker.check_short_term_trading(
        symbol='000001.SZ',
        position_pct=0.06,
        is_buy=False,
        last_trade_date=datetime.now() - timedelta(days=210)
    )
    print(f"  是否合规: {result3.is_compliant}")
    print(f"  合规级别: {result3.compliance_level.value}")


def example_compliance_report():
    """合规报告生成示例"""
    print("\n" + "=" * 80)
    print("示例5: 生成合规报告")
    print("=" * 80)
    
    checker = create_compliance_checker()
    
    base_time = datetime.now()
    for i in range(50):
        order = OrderRecord(
            order_id=f'ORDER_{i:03d}',
            symbol='000001.SZ',
            direction='buy',
            quantity=100,
            price=10.5,
            order_type='limit',
            timestamp=base_time + timedelta(seconds=i),
            status='submitted'
        )
        checker.order_tracker.add_order(order)
    
    for i in range(10):
        order_id = f'ORDER_{i:03d}'
        cancel_time = base_time + timedelta(seconds=i, microseconds=100)
        checker.order_tracker.record_cancel(order_id, cancel_time)
    
    report = checker.generate_compliance_report()
    
    print(f"\n合规报告生成时间: {report['report_time']}")
    print(f"\n每日统计:")
    stats = report['daily_statistics']
    print(f"  总订单数: {stats['total_orders']}")
    print(f"  总撤单数: {stats['total_cancels']}")
    print(f"  撤单率: {stats['cancel_rate']:.2%}")
    
    print(f"\n合规摘要:")
    summary = report['compliance_summary']
    print(f"  总检查次数: {summary['total_checks']}")
    print(f"  合规次数: {summary['compliant_checks']}")
    print(f"  警告次数: {summary['warning_checks']}")
    print(f"  违规次数: {summary['violation_checks']}")
    print(f"  合规率: {summary['compliance_rate']:.2%}")
    
    print(f"\n当前状态:")
    status = report['current_status']
    print(f"  是否合规: {status['is_compliant']}")
    print(f"  合规级别: {status['compliance_level']}")


def example_custom_config():
    """自定义配置示例"""
    print("\n" + "=" * 80)
    print("示例6: 自定义监管配置")
    print("=" * 80)
    
    custom_config = {
        'high_frequency_criteria': {
            'per_second_threshold': 100,  # 自定义高频阈值
            'per_day_threshold': 10000
        },
        'cancel_order_limits': {
            'max_cancel_rate_per_day': 0.10  # 更严格的撤单率限制
        }
    }
    
    checker = create_compliance_checker(custom_config)
    
    print(f"\n自定义配置已应用:")
    print(f"  高频交易阈值（每秒）: {checker.config.high_frequency_criteria['per_second_threshold']}")
    print(f"  高频交易阈值（单日）: {checker.config.high_frequency_criteria['per_day_threshold']}")
    print(f"  撤单率限制: {checker.config.cancel_order_limits['max_cancel_rate_per_day']:.2%}")


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("合规检查模块使用示例")
    print("基于2026年4月7日量化监管新政")
    print("=" * 80)
    
    example_basic_usage()
    example_high_frequency_check()
    example_cancel_limit_check()
    example_short_term_trading_check()
    example_compliance_report()
    example_custom_config()
    
    print("\n" + "=" * 80)
    print("所有示例执行完成！")
    print("=" * 80)


if __name__ == '__main__':
    main()
