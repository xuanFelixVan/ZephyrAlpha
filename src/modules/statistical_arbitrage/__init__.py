"""
统计套利模块

该模块实现了配对交易、市场中性组合构建和统计套利信号生成功能。

主要功能:
- 配对交易策略
- 市场中性组合构建
- 统计套利信号生成

模块ID: STATISTICAL_ARBITRAGE_MODULE_001
版本: v1.0.0
创建日期: 2026-04-02
"""

from .statistical_arbitrage_module import (
    SignalType,
    CointegratedPair,
    PairTradingSignal,
    PortfolioAllocation,
    StatisticalArbitrageModule
)

__all__ = [
    'SignalType',
    'CointegratedPair',
    'PairTradingSignal',
    'PortfolioAllocation',
    'StatisticalArbitrageModule'
]

__version__ = '1.0.0'
