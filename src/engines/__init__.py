"""
交易引擎适配器模块

提供统一的多引擎交易接口，支持：
- vn.py (生产级A股引擎)
- RQAlpha (专业回测引擎)
- Backtrader (功能补充引擎)
- QMT (迅投券商官方引擎)
- backtesting.py (轻量级快速验证引擎)

使用适配器模式提供统一接口，支持运行时引擎切换。
"""

from .base import BaseEngineAdapter, EngineConfig, UnifiedOrder, OrderSide, OrderType, ExecutionResult
from .factory import EngineFactory, create_backtesting_engine
from .backtesting_adapter import BacktestingPyAdapter, SimpleMAStrategy

__all__ = [
    'BaseEngineAdapter',
    'EngineConfig',
    'UnifiedOrder',
    'OrderSide',
    'OrderType',
    'ExecutionResult',
    'EngineFactory',
    'create_backtesting_engine',
    'BacktestingPyAdapter',
    'SimpleMAStrategy',
]