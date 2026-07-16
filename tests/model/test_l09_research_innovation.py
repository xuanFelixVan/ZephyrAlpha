# [A_test] module_id: SRC-TST-1211 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L09-001 | docs/03_modules/_domain_research/blueprint.md | §test
# [MODULE] zephyr.simulation
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_l09_research_innovation.py
# [TTL] task_bound
# [HISTORY] 2026-07-16 ARCH-MIGRATION-CLOSE: 修复 import 路径漂移（zephyr.research → zephyr.backtest）
#          + 补全 BacktestResult 新增必填字段 idempotency_key/timestamp（迁移后契约变更）。

from __future__ import annotations

from datetime import datetime

import pytest

l09 = pytest.importorskip("zephyr.simulation", reason="l09-research-innovation not importable")

from zephyr.backtest.core.engine_base import (
    BacktestEngineBase,
    BacktestResult,
    FactorDiscovery,
)


def _make_result(**overrides) -> BacktestResult:
    """构造 BacktestResult 测试实例——集中补全必填字段，避免 7 处重复。

    迁移后 BacktestResult 新增 2 个必填字段（idempotency_key/timestamp），
    旧测试未传导致 TypeError。统一通过此辅助函数构造。
    """
    defaults = {
        "strategy_id": "test_strat",
        "start_date": "2026-01-01",
        "end_date": "2026-03-31",
        "total_return": 0.10,
        "annual_return": 0.40,
        "sharpe_ratio": 1.2,
        "max_drawdown": 0.05,
        "win_rate": 0.55,
        "trades_count": 200,
        "idempotency_key": "test-key-001",
        "timestamp": datetime(2026, 1, 1),
    }
    defaults.update(overrides)
    return BacktestResult(**defaults)


class _ConcreteBacktestEngine(BacktestEngineBase):
    def run(self, signals, prices):
        return _make_result(
            strategy_id="test_strat",
            total_return=0.12,
            annual_return=0.48,
            sharpe_ratio=1.5,
            max_drawdown=0.08,
            win_rate=0.6,
            trades_count=100,
        )


class _NegativeReturnEngine(BacktestEngineBase):
    def run(self, signals, prices):
        return _make_result(
            strategy_id="bad_strat",
            total_return=-0.15,
            annual_return=-0.45,
            sharpe_ratio=-0.8,
            max_drawdown=0.25,
            win_rate=0.35,
            trades_count=50,
        )


class TestBacktestResult:
    def test_creation_required_fields(self):
        r = _make_result(strategy_id="s1", total_return=0.10, sharpe_ratio=1.2)
        assert r.strategy_id == "s1"
        assert r.total_return == 0.10
        assert r.sharpe_ratio == 1.2

    def test_frozen(self):
        r = _make_result()
        with pytest.raises(AttributeError):
            r.strategy_id = "other"

    def test_timestamp_required(self):
        """迁移后 timestamp 是必填字段（无默认值）——不传应 TypeError。"""
        with pytest.raises(TypeError):
            BacktestResult(
                strategy_id="s1",
                start_date="2026-01-01",
                end_date="2026-03-31",
                total_return=0.10,
                annual_return=0.40,
                sharpe_ratio=1.2,
                max_drawdown=0.05,
                win_rate=0.55,
                trades_count=200,
                idempotency_key="k1",
            )

    def test_idempotency_key_required(self):
        """迁移后 idempotency_key 是必填字段——不传应 TypeError。"""
        with pytest.raises(TypeError):
            BacktestResult(
                strategy_id="s1",
                start_date="2026-01-01",
                end_date="2026-03-31",
                total_return=0.10,
                annual_return=0.40,
                sharpe_ratio=1.2,
                max_drawdown=0.05,
                win_rate=0.55,
                trades_count=200,
                timestamp=datetime(2026, 1, 1),
            )

    def test_negative_return(self):
        r = _make_result(total_return=-0.20, annual_return=-0.60, sharpe_ratio=-1.5, max_drawdown=0.30, win_rate=0.30, trades_count=10)
        assert r.total_return < 0
        assert r.sharpe_ratio < 0

    def test_zero_trades(self):
        r = _make_result(total_return=0.0, annual_return=0.0, sharpe_ratio=0.0, max_drawdown=0.0, win_rate=0.0, trades_count=0)
        assert r.trades_count == 0


class TestFactorDiscovery:
    def test_creation_required_fields(self):
        f = FactorDiscovery(
            factor_id="fac-001",
            name="momentum_12m",
            ic_mean=0.05,
            ic_ir=1.8,
            t_stat=3.2,
        )
        assert f.factor_id == "fac-001"
        assert f.name == "momentum_12m"
        assert f.status == "candidate"

    def test_frozen(self):
        f = FactorDiscovery(
            factor_id="fac-001",
            name="test",
            ic_mean=0.05,
            ic_ir=1.8,
            t_stat=3.2,
        )
        with pytest.raises(AttributeError):
            f.name = "changed"

    def test_status_candidate(self):
        f = FactorDiscovery(
            factor_id="fac-001",
            name="test",
            ic_mean=0.05,
            ic_ir=1.8,
            t_stat=3.2,
        )
        assert f.status == "candidate"

    def test_status_validated(self):
        f = FactorDiscovery(
            factor_id="fac-001",
            name="test",
            ic_mean=0.05,
            ic_ir=1.8,
            t_stat=3.2,
            status="validated",
        )
        assert f.status == "validated"

    def test_status_promoted(self):
        f = FactorDiscovery(
            factor_id="fac-001",
            name="test",
            ic_mean=0.05,
            ic_ir=1.8,
            t_stat=3.2,
            status="promoted",
        )
        assert f.status == "promoted"

    def test_status_rejected(self):
        f = FactorDiscovery(
            factor_id="fac-001",
            name="test",
            ic_mean=-0.01,
            ic_ir=0.3,
            t_stat=0.5,
            status="rejected",
        )
        assert f.status == "rejected"

    def test_negative_ic(self):
        f = FactorDiscovery(
            factor_id="fac-002",
            name="bad_factor",
            ic_mean=-0.03,
            ic_ir=-0.5,
            t_stat=-1.2,
        )
        assert f.ic_mean < 0
        assert f.t_stat < 0


class TestBacktestEngineBase:
    def test_cannot_instantiate_abc(self):
        with pytest.raises(TypeError):
            BacktestEngineBase()

    def test_run_returns_backtest_result(self):
        engine = _ConcreteBacktestEngine()
        result = engine.run([], [])
        assert isinstance(result, BacktestResult)
        assert result.strategy_id == "test_strat"

    def test_run_positive_result(self):
        engine = _ConcreteBacktestEngine()
        result = engine.run([], [])
        assert result.total_return > 0
        assert result.sharpe_ratio > 0
        assert result.win_rate > 0.5

    def test_run_negative_result(self):
        engine = _NegativeReturnEngine()
        result = engine.run([], [])
        assert result.total_return < 0
        assert result.sharpe_ratio < 0

    def test_run_result_date_range(self):
        engine = _ConcreteBacktestEngine()
        result = engine.run([], [])
        assert result.start_date == "2026-01-01"
        assert result.end_date == "2026-03-31"

    def test_run_result_trades_count(self):
        engine = _ConcreteBacktestEngine()
        result = engine.run([], [])
        assert result.trades_count == 100

    def test_run_result_max_drawdown(self):
        engine = _ConcreteBacktestEngine()
        result = engine.run([], [])
        assert 0 <= result.max_drawdown <= 1.0
