# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [A_module] module_id=MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [A_test] module_id: MOD-BT-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.backtest.test_engine_base
# [DOMAIN] D_BACKTEST
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/backtest/test_engine_base.py
# [TTL] permanent
"""engine_base 单元测试（52号 四核心模块零单测清偿，AI-WAVE2C-001）。

覆盖: BacktestResult 契约（必填字段/默认值/frozen）、FactorDiscovery 默认值、
BacktestEngineBase 抽象基类契约（不可实例化/子类必须实现 run）、
最小端到端确定性用例（合成 signals/prices → 标准 BacktestResult，两次运行逐字段相等）。
纯内存合成夹具，不触网不触库。
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from zephyr.backtest.core.engine_base import (
    BacktestEngineBase,
    BacktestResult,
    FactorDiscovery,
)

_TS_START = datetime(2024, 1, 2, tzinfo=timezone.utc)
_TS_END = datetime(2024, 1, 31, tzinfo=timezone.utc)
_TS_STAMP = datetime(2024, 2, 1, tzinfo=timezone.utc)


def _make_result(**overrides) -> BacktestResult:
    """构造最小合法 BacktestResult（合成夹具）。"""
    kwargs = {
        "annual_return": 0.12,
        "end_date": _TS_END,
        "idempotency_key": "bt-000001",
        "max_drawdown": 0.08,
        "sharpe_ratio": 1.5,
        "start_date": _TS_START,
        "strategy_id": "toy_strategy",
        "timestamp": _TS_STAMP,
        "total_return": 0.03,
        "trades_count": 10,
        "win_rate": 0.6,
    }
    kwargs.update(overrides)
    return BacktestResult(**kwargs)


class TestBacktestResult:
    """BacktestResult 契约测试（CTR-P1-016 frozen dataclass）。"""

    def test_creation_with_required_fields(self):
        r = _make_result()
        assert r.strategy_id == "toy_strategy"
        assert r.total_return == 0.03
        assert r.annual_return == 0.12
        assert r.sharpe_ratio == 1.5
        assert r.max_drawdown == 0.08
        assert r.trades_count == 10
        assert r.win_rate == 0.6
        assert r.idempotency_key == "bt-000001"
        assert r.start_date == _TS_START
        assert r.end_date == _TS_END
        assert r.timestamp == _TS_STAMP

    def test_defaults(self):
        r = _make_result()
        assert r.benchmark_symbol is None
        assert r.overfitting_flag is False
        assert r.schema_version == "1.0"
        assert r.trace_context is None

    def test_overrides(self):
        r = _make_result(benchmark_symbol="000300.SH", overfitting_flag=True)
        assert r.benchmark_symbol == "000300.SH"
        assert r.overfitting_flag is True

    def test_frozen_immutable(self):
        r = _make_result()
        with pytest.raises(FrozenInstanceError):
            r.sharpe_ratio = 9.9  # type: ignore[misc]

    def test_missing_required_field_raises(self):
        with pytest.raises(TypeError):
            BacktestResult(  # type: ignore[call-arg]
                annual_return=0.12,
                end_date=_TS_END,
                idempotency_key="bt-000002",
                max_drawdown=0.08,
                sharpe_ratio=1.5,
                start_date=_TS_START,
                strategy_id="toy_strategy",
                timestamp=_TS_STAMP,
                total_return=0.03,
                trades_count=10,
                # win_rate 缺失 → TypeError
            )

    def test_equality_by_value(self):
        assert _make_result() == _make_result()
        assert _make_result() != _make_result(trades_count=11)


class TestFactorDiscovery:
    """FactorDiscovery 因子发现记录契约。"""

    def test_creation_and_default_status(self):
        f = FactorDiscovery(
            factor_id="F001",
            name="momentum_20d",
            ic_mean=0.05,
            ic_ir=0.8,
            t_stat=2.3,
        )
        assert f.factor_id == "F001"
        assert f.status == "candidate"

    def test_frozen_immutable(self):
        f = FactorDiscovery(
            factor_id="F002",
            name="value_pe",
            ic_mean=0.03,
            ic_ir=0.5,
            t_stat=1.9,
        )
        with pytest.raises(FrozenInstanceError):
            f.status = "promoted"  # type: ignore[misc]

    def test_status_transition_values(self):
        f = FactorDiscovery(
            factor_id="F003",
            name="reversal_5d",
            ic_mean=-0.02,
            ic_ir=-0.4,
            t_stat=-1.2,
            status="rejected",
        )
        assert f.status == "rejected"


class _ToyEngine(BacktestEngineBase):
    """最小合成引擎：末价/首价-1 为总收益，trades=len(signals)，确定性输出。"""

    def run(self, signals: list, prices: list) -> BacktestResult:
        total_return = float(prices[-1]) / float(prices[0]) - 1.0
        wins = sum(1 for s in signals if s > 0)
        return BacktestResult(
            annual_return=total_return,
            end_date=_TS_END,
            idempotency_key="toy-e2e",
            max_drawdown=0.0,
            sharpe_ratio=0.0,
            start_date=_TS_START,
            strategy_id="toy_engine",
            timestamp=_TS_STAMP,
            total_return=total_return,
            trades_count=len(signals),
            win_rate=wins / len(signals) if signals else 0.0,
        )


class _IncompleteEngine(BacktestEngineBase):
    """未实现 run 的子类（必须保持抽象）。"""


class TestBacktestEngineBase:
    """BacktestEngineBase ABC 契约 + 最小端到端确定性用例。"""

    def test_abstract_cannot_instantiate(self):
        with pytest.raises(TypeError):
            BacktestEngineBase()  # type: ignore[abstract]

    def test_subclass_without_run_cannot_instantiate(self):
        with pytest.raises(TypeError):
            _IncompleteEngine()  # type: ignore[abstract]

    def test_registry_is_dict(self):
        assert isinstance(BacktestEngineBase._registry, dict)

    def test_minimal_end_to_end_deterministic(self):
        """最小端到端：合成信号+价格 → BacktestResult，两次运行逐字段相等。"""
        engine = _ToyEngine()
        signals = [1, -1, 1, 1]
        prices = [10.0, 10.5, 11.0, 12.0]

        r1 = engine.run(signals, prices)
        r2 = engine.run(signals, prices)

        assert isinstance(r1, BacktestResult)
        assert r1 == r2, "相同输入必须产生相同输出（引擎契约确定性）"
        assert r1.total_return == pytest.approx(0.2)
        assert r1.trades_count == 4
        assert r1.win_rate == pytest.approx(0.75)
        assert r1.strategy_id == "toy_engine"

    def test_end_to_end_empty_signals(self):
        engine = _ToyEngine()
        r = engine.run([], [10.0, 11.0])
        assert r.trades_count == 0
        assert r.win_rate == 0.0
        assert r.total_return == pytest.approx(0.1)
