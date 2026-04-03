"""
经济范式判断引擎模块

该模块实现了宏观经济周期识别和范式判断功能，参考桥水基金全天候策略。

主要功能:
- 经济周期识别（扩张/滞胀/衰退/复苏）
- 范式概率分布输出
- 资产配置建议
- 风险预警

模块ID: ECONOMIC_REGIME_ENGINE_001
版本: v1.0.0
创建日期: 2026-04-02
"""

from .economic_regime_engine import (
    EconomicRegime,
    RegimeAnalysis,
    MacroIndicators,
    EconomicRegimeEngine
)

__all__ = [
    'EconomicRegime',
    'RegimeAnalysis',
    'MacroIndicators',
    'EconomicRegimeEngine'
]

__version__ = '1.0.0'
