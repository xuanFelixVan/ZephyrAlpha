# [BLUEPRINT] MOD-BT-017 | (auto-injected by S4 reconciler) | §D-BACKTEST BT-17
# [A_module] module_id=MOD-BT-017 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [A_test] module_id: MOD-BT-017 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.backtest.test_scheduler
# [DOMAIN] D_BACKTEST
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/backtest/test_scheduler.py
# [TTL] task_bound
"""D-BACKTEST BT-17 回测自动调度器测试——使用 Mock 引擎（无 IO 依赖）。

覆盖：
- submit: 单任务提交 / queue_size 正确
- submit_grid: 参数网格展开 / 空网格 / 单参数 / 多参数笛卡尔积
- run_all: FIFO执行 / 并发不丢任务 / 空队列返回空列表
- get_result: 查询结果 / 不存在返回None
- get_summary: 最优/最差/均值 / 无结果空摘要
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd
import pytest

from zephyr.backtest.core.engine_base import BacktestResult
from zephyr.backtest.services.scheduler import (
    BacktestScheduler,
    BacktestTask,
    GridSearchSummary,
    _expand_param_grid,
)


def _make_result(
    strategy_id: str = "strat_a",
    sharpe: float = 1.0,
    total_return: float = 0.1,
) -> BacktestResult:
    """构造测试用 BacktestResult。"""
    now = datetime.now(timezone.utc)
    return BacktestResult(
        annual_return=total_return,
        end_date=now,
        idempotency_key=f"key-{strategy_id}-{sharpe}",
        max_drawdown=-0.05,
        sharpe_ratio=sharpe,
        start_date=now,
        strategy_id=strategy_id,
        timestamp=now,
        total_return=total_return,
        trades_count=10,
        win_rate=0.6,
    )


def _mock_engine_factory(sharpe: float = 1.0, **kwargs: Any):
    """Mock 引擎工厂——返回带 run 方法的对象。"""

    class _MockEngine:
        def run(self, data: pd.DataFrame, signals: pd.DataFrame) -> BacktestResult:
            return _make_result(sharpe=sharpe, total_return=sharpe * 0.1)

    return _MockEngine()


def _param_aware_factory(**kwargs: Any):
    """根据 params['sharpe'] 返回不同结果的 Mock 工厂。"""
    sharpe = kwargs.get("sharpe", 1.0)

    class _MockEngine:
        def run(self, data: pd.DataFrame, signals: pd.DataFrame) -> BacktestResult:
            return _make_result(sharpe=float(sharpe), total_return=float(sharpe) * 0.1)

    return _MockEngine()


class TestExpandParamGrid:
    def test_empty_grid(self):
        assert _expand_param_grid({}) == [{}]

    def test_single_param(self):
        result = _expand_param_grid({"a": [1, 2, 3]})
        assert result == [{"a": 1}, {"a": 2}, {"a": 3}]

    def test_multi_params_cartesian(self):
        result = _expand_param_grid({"a": [1, 2], "b": [10, 20]})
        assert len(result) == 4
        assert {"a": 1, "b": 10} in result
        assert {"a": 2, "b": 20} in result

    def test_single_value_param(self):
        result = _expand_param_grid({"a": [42]})
        assert result == [{"a": 42}]


class TestSubmit:
    def test_submit_single_task(self):
        scheduler = BacktestScheduler(engine_factory=_mock_engine_factory)
        task_id = scheduler.submit("s1", pd.DataFrame(), pd.DataFrame())
        assert task_id.startswith("task-")
        assert scheduler.queue_size == 1

    def test_submit_with_params(self):
        scheduler = BacktestScheduler(engine_factory=_mock_engine_factory)
        task_id = scheduler.submit("s1", pd.DataFrame(), pd.DataFrame(), {"horizon": 10})
        assert task_id.startswith("task-")
        assert scheduler.queue_size == 1


class TestSubmitGrid:
    def test_grid_expansion(self):
        scheduler = BacktestScheduler(engine_factory=_mock_engine_factory)
        task_ids = scheduler.submit_grid(
            "s1",
            pd.DataFrame(),
            pd.DataFrame(),
            {"horizon": [5, 10, 20], "threshold": [0.01, 0.02]},
        )
        assert len(task_ids) == 6  # 3 × 2 = 6
        assert scheduler.queue_size == 6

    def test_empty_grid(self):
        scheduler = BacktestScheduler(engine_factory=_mock_engine_factory)
        task_ids = scheduler.submit_grid("s1", pd.DataFrame(), pd.DataFrame(), {})
        assert len(task_ids) == 1

    def test_single_param_grid(self):
        scheduler = BacktestScheduler(engine_factory=_mock_engine_factory)
        task_ids = scheduler.submit_grid(
            "s1",
            pd.DataFrame(),
            pd.DataFrame(),
            {"horizon": [5, 10, 20]},
        )
        assert len(task_ids) == 3


class TestRunAll:
    def test_empty_queue_returns_empty(self):
        scheduler = BacktestScheduler(engine_factory=_mock_engine_factory)
        results = scheduler.run_all()
        assert results == []

    def test_run_all_executes_all_tasks(self):
        scheduler = BacktestScheduler(engine_factory=_mock_engine_factory)
        scheduler.submit_grid(
            "s1",
            pd.DataFrame(),
            pd.DataFrame(),
            {"horizon": [5, 10, 20]},
        )
        results = scheduler.run_all(max_workers=2)
        assert len(results) == 3
        assert scheduler.queue_size == 0  # queue cleared after run

    def test_run_all_concurrent_no_loss(self):
        scheduler = BacktestScheduler(engine_factory=_mock_engine_factory)
        for i in range(10):
            scheduler.submit("s1", pd.DataFrame(), pd.DataFrame(), {"idx": i})
        results = scheduler.run_all(max_workers=4)
        assert len(results) == 10

    def test_run_all_with_param_aware_factory(self):
        scheduler = BacktestScheduler(engine_factory=_param_aware_factory)
        scheduler.submit_grid(
            "s1",
            pd.DataFrame(),
            pd.DataFrame(),
            {"sharpe": [0.5, 1.0, 2.0]},
        )
        results = scheduler.run_all()
        sharpes = sorted(r.sharpe_ratio for r in results)
        assert sharpes == [0.5, 1.0, 2.0]


class TestGetResult:
    def test_get_existing_result(self):
        scheduler = BacktestScheduler(engine_factory=_mock_engine_factory)
        task_id = scheduler.submit("s1", pd.DataFrame(), pd.DataFrame())
        scheduler.run_all()
        result = scheduler.get_result(task_id)
        assert result is not None
        assert isinstance(result, BacktestResult)

    def test_get_nonexistent_result(self):
        scheduler = BacktestScheduler(engine_factory=_mock_engine_factory)
        assert scheduler.get_result("unknown") is None


class TestGetSummary:
    def test_summary_with_results(self):
        scheduler = BacktestScheduler(engine_factory=_param_aware_factory)
        scheduler.submit_grid(
            "s1",
            pd.DataFrame(),
            pd.DataFrame(),
            {"sharpe": [0.5, 1.0, 2.0]},
        )
        scheduler.run_all()
        summary = scheduler.get_summary("s1")
        assert isinstance(summary, GridSearchSummary)
        assert summary.total_runs == 3
        assert summary.best_result.sharpe_ratio == 2.0
        assert summary.worst_result.sharpe_ratio == 0.5
        assert summary.mean_sharpe == pytest.approx(1.166, rel=0.01)

    def test_summary_empty_strategy(self):
        scheduler = BacktestScheduler(engine_factory=_mock_engine_factory)
        summary = scheduler.get_summary("nonexistent")
        assert summary.total_runs == 0
        assert summary.best_result is None

    def test_summary_best_params_correct(self):
        scheduler = BacktestScheduler(engine_factory=_param_aware_factory)
        scheduler.submit_grid(
            "s1",
            pd.DataFrame(),
            pd.DataFrame(),
            {"sharpe": [0.5, 2.0]},
        )
        scheduler.run_all()
        summary = scheduler.get_summary("s1")
        assert summary.best_params == {"sharpe": 2.0}
        assert summary.worst_params == {"sharpe": 0.5}

    def test_summary_multiple_strategies(self):
        scheduler = BacktestScheduler(engine_factory=_param_aware_factory)
        scheduler.submit_grid(
            "s1",
            pd.DataFrame(),
            pd.DataFrame(),
            {"sharpe": [1.0, 2.0]},
        )
        scheduler.submit_grid(
            "s2",
            pd.DataFrame(),
            pd.DataFrame(),
            {"sharpe": [0.5, 3.0]},
        )
        scheduler.run_all()
        s1 = scheduler.get_summary("s1")
        s2 = scheduler.get_summary("s2")
        assert s1.total_runs == 2
        assert s2.total_runs == 2
        assert s1.best_result.sharpe_ratio == 2.0
        assert s2.best_result.sharpe_ratio == 3.0
