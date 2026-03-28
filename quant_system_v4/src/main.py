"""
清风量化交易系统 v4.0
主入口
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.base import Result, Signal, Order, Position


def main():
    """主入口"""
    print("=" * 60)
    print("清风量化交易系统 v4.0")
    print("=" * 60)
    print()

    print("系统模块:")
    print("  1. data_collector    - 数据采集")
    print("  2. data_cleaner      - 数据清洗")
    print("  3. data_storage      - 数据存储")
    print("  4. factor_registry   - 因子注册中心")
    print("  5. factor_calculator - 因子计算引擎")
    print("  6. strategy_engine   - 策略引擎")
    print("  7. risk_manager      - 风险管理")
    print("  8. backtest_framework - 回测框架")
    print("  9. trade_executor   - 交易执行")
    print(" 10. monitoring_system - 监控告警")
    print()
    print("详见: docs/SPEC.md")
    print()

    return Result(success=True, data={"version": "4.0.0"})


if __name__ == "__main__":
    main()
