# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l09_research_innovation.test_backtest_base
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""
单元测试：src/zephyr/l09_research_innovation/backtest_base.py
=============================================================

覆盖矩阵：
  BacktestEngineBase (ABC):
    - 抽象类不可实例化 × 1
    - 注册表登记 × 1
  BacktestResult:
    - frozen × 1
    - 默认 timestamp × 1
  FactorDiscovery:
    - 默认 status × 1
"""

from datetime import datetime

import pytest
from zephyr.l09_research_innovation.backtest_base import (
    BacktestEngineBase,
    BacktestResult,
    FactorDiscovery,
)


class TestBacktestEngineBaseABC:
    def test_abstract_cannot_instantiate(self):
        with pytest.raises(TypeError):
            BacktestEngineBase()

    def test_registry_exists(self):
        assert hasattr(BacktestEngineBase, "_registry")
        assert isinstance(BacktestEngineBase._registry, dict)


class TestBacktestResult:
    def test_frozen(self):
        r = BacktestResult(
            strategy_id="s1",
            start_date="2025-01-01",
            end_date="2025-12-31",
            total_return=0.1,
            annual_return=0.1,
            sharpe_ratio=1.5,
            max_drawdown=0.05,
            win_rate=0.6,
            trades_count=100,
        )
        with pytest.raises(AttributeError):
            r.total_return = 0.2

    def test_default_timestamp(self):
        r = BacktestResult(
            strategy_id="s1",
            start_date="2025-01-01",
            end_date="2025-12-31",
            total_return=0.1,
            annual_return=0.1,
            sharpe_ratio=1.5,
            max_drawdown=0.05,
            win_rate=0.6,
            trades_count=100,
        )
        assert isinstance(r.timestamp, datetime)


class TestFactorDiscovery:
    def test_default_status(self):
        fd = FactorDiscovery(
            factor_id="f1",
            name="test",
            ic_mean=0.05,
            ic_ir=1.2,
            t_stat=2.5,
        )
        assert fd.status == "candidate"
