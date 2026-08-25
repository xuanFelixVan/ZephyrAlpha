# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] tests.factor.test_factor_production_pipeline
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.factor_production_pipeline
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] production
# [INVARIANTS] 纯内存编排测试，executor/store_writer/broadcast_sink 注入式，不触网不触库
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=双模编排/算力预算/超时降级/容量规划逻辑缺陷
# [TESTS] 本文件
# [TTL] permanent
"""FactorProductionPipeline 单元测试（CAND-FAC-009 / B1-00144，C-009 因子与信号生产管线）。

覆盖（min_build_spec）：
- 双模管线：盘前全量批算（分块编排）+ 盘中增量（事件驱动 mode）
- 因子值落 feature_store（store_writer 委托）并广播（broadcast_sink）
- 算力预算：累计预算耗尽后续块降级跳过；单块超时标 timeout 降级
- 7000+标的×N_max-4因子容量规划校验
查重锚点：计算执行委托 compute_executor（DagExecutor 语义注入），本件不重建
intraday_factor_loop/DAG/feature_store_writer 计算与存储本体。
"""

from __future__ import annotations

import pytest

from zephyr.factor.factor_production_pipeline import (
    ComputeMode,
    FactorProductionPipeline,
    PipelineConfigError,
)

_SYMBOLS_10 = [f"00000{i}.SZ" for i in range(10)]
_FACTORS = ["momentum_20d", "value_pe"]


def _executor_ok(rows=None):
    calls: list[tuple] = []

    def _exec(symbols, factor_ids, mode):
        calls.append((tuple(symbols), tuple(factor_ids), mode))
        return [
            {"trade_date": "2026-08-25", "symbol": s, "factor_id": f, "value": 1.0}
            for s in symbols
            for f in factor_ids
        ]

    _exec.calls = calls
    return _exec


class TestCapacityPlan:
    """7000+标的×N_max-4因子容量规划。"""

    def test_within_budget(self) -> None:
        pipe = FactorProductionPipeline(compute_executor=_executor_ok(), chunk_size=100)
        plan = pipe.capacity_plan(_SYMBOLS_10, _FACTORS)
        assert plan.within_budget is True
        assert plan.symbols == 10
        assert plan.factors == 2
        assert plan.estimated_cells == 20
        assert plan.max_symbols == 7500
        assert plan.max_factors == 4

    def test_over_symbol_budget(self) -> None:
        pipe = FactorProductionPipeline(compute_executor=_executor_ok(), max_symbols=100)
        plan = pipe.capacity_plan([f"s{i}" for i in range(101)], _FACTORS)
        assert plan.within_budget is False
        assert "标的" in plan.reason

    def test_over_factor_budget(self) -> None:
        pipe = FactorProductionPipeline(compute_executor=_executor_ok(), max_factors=2)
        plan = pipe.capacity_plan(_SYMBOLS_10, ["a", "b", "c"])
        assert plan.within_budget is False
        assert "因子" in plan.reason

    def test_custom_capacity_limits(self) -> None:
        pipe = FactorProductionPipeline(
            compute_executor=_executor_ok(), max_symbols=8000, max_factors=8
        )
        plan = pipe.capacity_plan(_SYMBOLS_10, _FACTORS)
        assert plan.max_symbols == 8000
        assert plan.max_factors == 8


class TestPremarketFullBatch:
    """盘前全量批算编排。"""

    def test_full_batch_chunks_and_persists(self) -> None:
        executor = _executor_ok()
        stored: list[dict] = []
        broadcast: list[dict] = []
        pipe = FactorProductionPipeline(
            compute_executor=executor,
            store_writer=stored.extend,
            broadcast_sink=broadcast.append,
            chunk_size=4,
        )
        verdict = pipe.run_premarket(_SYMBOLS_10, _FACTORS)
        assert verdict.mode == ComputeMode.PREMARKET_FULL
        assert verdict.symbols_done == 10
        assert verdict.degraded is False
        assert len(executor.calls) == 3  # 4+4+2 三块
        assert all(c[2] == ComputeMode.PREMARKET_FULL for c in executor.calls)
        assert len(stored) == 10 * 2  # 长表一行一值
        assert len(broadcast) == 1
        assert broadcast[0]["rows"] == 20

    def test_executor_failure_degrades_chunk_not_abort(self) -> None:
        def _flaky(symbols, factor_ids, mode):
            if "000001.SZ" in symbols:
                raise RuntimeError("compute boom")
            return [
                {"trade_date": "2026-08-25", "symbol": s, "factor_id": f, "value": 1.0}
                for s in symbols
                for f in factor_ids
            ]

        pipe = FactorProductionPipeline(compute_executor=_flaky, chunk_size=5)
        verdict = pipe.run_premarket(_SYMBOLS_10, _FACTORS)
        assert verdict.degraded is True
        assert verdict.symbols_done == 5  # 第二块成功
        assert "compute boom" in verdict.reason

    def test_store_writer_rows_injected(self) -> None:
        stored: list[dict] = []
        pipe = FactorProductionPipeline(
            compute_executor=_executor_ok(), store_writer=stored.extend, chunk_size=100
        )
        pipe.run_premarket(_SYMBOLS_10[:2], _FACTORS)
        assert {r["symbol"] for r in stored} == set(_SYMBOLS_10[:2])
        assert {r["factor_id"] for r in stored} == set(_FACTORS)


class TestComputeBudget:
    """算力预算与超时降级。"""

    def test_budget_exhaustion_skips_remaining_chunks(self) -> None:
        # clock 调用序：started → 每块(elapsed → chunk_start → chunk_end)
        timeline = iter([0.0, 0.0, 0.0, 100.0, 200.0])
        clock = lambda: next(timeline)  # noqa: E731

        executor = _executor_ok()
        pipe = FactorProductionPipeline(
            compute_executor=executor,
            chunk_size=4,
            compute_budget_seconds=150.0,
            clock=clock,
        )
        verdict = pipe.run_premarket(_SYMBOLS_10, _FACTORS)
        # 块1: elapsed=0 执行（0→100s 完成 4 标的）；块2: elapsed=200≥150 预算耗尽跳过
        assert verdict.degraded is True
        assert verdict.symbols_done == 4
        assert "预算" in verdict.reason

    def test_slow_chunk_marked_timeout(self) -> None:
        # 块1: 0→60s（>30s 超时标记）；块2: 65→70s 正常
        timeline = iter([0.0, 0.0, 0.0, 60.0, 60.0, 65.0, 70.0])
        clock = lambda: next(timeline)  # noqa: E731

        pipe = FactorProductionPipeline(
            compute_executor=_executor_ok(),
            chunk_size=5,
            batch_timeout_seconds=30.0,
            compute_budget_seconds=1e9,
            clock=clock,
        )
        verdict = pipe.run_premarket(_SYMBOLS_10, _FACTORS)
        assert verdict.timeout_count == 1
        assert verdict.degraded is True
        assert verdict.symbols_done == 10  # 超时块结果仍落库（无法真中断），但标记


class TestIntradayIncremental:
    """盘中增量模式。"""

    def test_intraday_mode_event_driven(self) -> None:
        executor = _executor_ok()
        pipe = FactorProductionPipeline(compute_executor=executor, chunk_size=100)
        verdict = pipe.run_intraday(_SYMBOLS_10[:3], _FACTORS, event={"tick": "000001.SZ"})
        assert verdict.mode == ComputeMode.INTRADAY_INCREMENTAL
        assert executor.calls[0][2] == ComputeMode.INTRADAY_INCREMENTAL
        assert verdict.symbols_done == 3

    def test_empty_symbols_short_circuit(self) -> None:
        pipe = FactorProductionPipeline(compute_executor=_executor_ok())
        verdict = pipe.run_premarket([], _FACTORS)
        assert verdict.symbols_done == 0
        assert verdict.degraded is False

    def test_executor_not_callable_raises(self) -> None:
        with pytest.raises(PipelineConfigError):
            FactorProductionPipeline(compute_executor=123)  # type: ignore[arg-type]

    def test_verdict_frozen(self) -> None:
        pipe = FactorProductionPipeline(compute_executor=_executor_ok(), chunk_size=100)
        verdict = pipe.run_premarket(_SYMBOLS_10[:1], _FACTORS)
        with pytest.raises(AttributeError):
            verdict.degraded = True  # type: ignore[misc]
