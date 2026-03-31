"""
清风量化交易系统 v5.0
主入口

使用方式:
    1. 模块方式 (推荐): python -m src.main
    2. 直接运行: python src/main.py (需设置 PYTHONPATH)
    3. 安装后运行: pip install -e . && python -m src.main
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.core.base import Result, Signal, Order, Position
from src.core.exceptions import SystemException


def main():
    """主入口"""
    print("=" * 60)
    print("清风量化交易系统 v5.0")
    print("=" * 60)
    print()

    print("系统模块:")
    print("  ✅ factor_calculator - 因子计算引擎")
    print("  ✅ risk_manager      - 风险管理")
    print("  ✅ alert_manager     - 告警管理")
    print("  🔄 data_collector    - 数据采集 (规划中)")
    print("  🔄 strategy_engine   - 策略引擎 (规划中)")
    print("  🔄 trade_executor    - 交易执行 (规划中)")
    print()
    print("详见: ../docs/System_Manifest.md")
    print()

    return Result(success=True, data={"version": "5.0.0"})


if __name__ == "__main__":
    main()
