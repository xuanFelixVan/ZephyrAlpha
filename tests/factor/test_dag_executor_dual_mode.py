# [A_test] module_id: MOD-L02-024 | layer=test | stability=volatile | safety=L
# [BLUEPRINT] MOD-L02-024 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-04
# [MODULE] tests.factor.test_dag_executor_dual_mode
# [DOMAIN] D_FACTOR
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/factor/test_dag_executor_dual_mode.py
# [A_module] module_id=MOD-L02-024 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""D_FACTOR-04 Pipeline 双模运行测试——executor 双模切换 + 时间窗口。

覆盖：
- determine_mode: 盘前batch / 盘中incremental / 其他时段batch
- batch 模式（默认，向后兼容）
- incremental 模式 + cached_results 调用 incremental_compute
- DagExecutionReport.mode 字段正确
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
import pytest

executor_mod = pytest.importorskip("zephyr.factor.core.dag_manager.executor")
dag_mod = pytest.importorskip("zephyr.factor.core.factor_dag.dag")
factor_base = pytest.importorskip("zephyr.factor.factor_base")

DagExecutor = executor_mod.DagExecutor
DagExecutorConfig = executor_mod.DagExecutorConfig
BATCH = executor_mod.BATCH
INCREMENTAL = executor_mod.INCREMENTAL
determine_mode = executor_mod.determine_mode

FactorDAG = dag_mod.FactorDAG
FactorNode = dag_mod.FactorNode
build_dag_from_registry = dag_mod.build_dag_from_registry

FactorBase = factor_base.FactorBase
FactorMeta = factor_base.FactorMeta
FactorRegistry = factor_base.FactorRegistry


@pytest.fixture(autouse=True)
def clear_registry():
    FactorRegistry.clear()
    yield
    FactorRegistry.clear()


def _register_incremental_factor(fid: str) -> None:
    """注册支持 incremental_compute 的测试因子。"""

    class _IncFactor(FactorBase):
        meta = FactorMeta(factor_id=fid, name=fid, domain="test")

        def compute(self, data: pd.DataFrame, **kwargs) -> pd.Series:
            return data["close"].pct_change(5)

        def incremental_compute(
            self,
            data: pd.DataFrame,
            window: int = 5,
            cached: pd.Series | None = None,
            **kwargs,
        ) -> pd.Series:
            if cached is None or cached.empty:
                return self.compute(data)
            last_idx = cached.index[-1]
            if last_idx not in data.index:
                return self.compute(data)
            new_data = data[data.index > last_idx]
            if new_data.empty:
                return cached
            last_pos = data.index.get_loc(last_idx)
            start_pos = max(0, last_pos - window + 1)
            tail = data.iloc[start_pos:]
            tail_factor = tail["close"].pct_change(window)
            new_factor = tail_factor[tail_factor.index > last_idx]
            return pd.concat([cached, new_factor])

    FactorRegistry.register(_IncFactor)


def _make_data(n: int = 30) -> pd.DataFrame:
    """构造测试行情数据。"""
    rng = np.random.RandomState(42)
    dates = pd.date_range("2026-01-01", periods=n, freq="B")
    close = 100.0 + np.cumsum(rng.randn(n) * 0.5)
    return pd.DataFrame({"close": close}, index=dates)


class TestDetermineMode:
    def test_pre_market_batch(self):
        """03:00-09:15 → batch。"""
        assert determine_mode(datetime(2026, 7, 28, 3, 0)) == BATCH
        assert determine_mode(datetime(2026, 7, 28, 6, 30)) == BATCH
        assert determine_mode(datetime(2026, 7, 28, 9, 14)) == BATCH

    def test_intraday_incremental(self):
        """09:30-15:00 → incremental。"""
        assert determine_mode(datetime(2026, 7, 28, 9, 30)) == INCREMENTAL
        assert determine_mode(datetime(2026, 7, 28, 10, 0)) == INCREMENTAL
        assert determine_mode(datetime(2026, 7, 28, 14, 59)) == INCREMENTAL

    def test_other_times_batch(self):
        """其他时段 → batch（默认安全）。"""
        assert determine_mode(datetime(2026, 7, 28, 0, 0)) == BATCH
        assert determine_mode(datetime(2026, 7, 28, 9, 16)) == BATCH
        assert determine_mode(datetime(2026, 7, 28, 15, 1)) == BATCH
        assert determine_mode(datetime(2026, 7, 28, 23, 59)) == BATCH

    def test_boundary_0915(self):
        """09:15 是 batch 结束（不包含）。"""
        assert determine_mode(datetime(2026, 7, 28, 9, 15)) == BATCH

    def test_boundary_0930(self):
        """09:30 是 incremental 开始（包含）。"""
        assert determine_mode(datetime(2026, 7, 28, 9, 30)) == INCREMENTAL

    def test_boundary_1500(self):
        """15:00 是 incremental 结束（不包含）。"""
        assert determine_mode(datetime(2026, 7, 28, 15, 0)) == BATCH


class TestBatchMode:
    def test_default_mode_is_batch(self):
        """不指定 mode 时默认为 batch。"""
        _register_incremental_factor("inc_1")
        dag = build_dag_from_registry(["inc_1"])
        data = _make_data(30)
        executor = DagExecutor(DagExecutorConfig(max_workers=2))
        report = executor.execute(dag, data)
        assert report.mode == BATCH

    def test_batch_mode_uses_compute(self):
        """batch 模式调用 compute()，结果正确。"""
        _register_incremental_factor("inc_1")
        dag = build_dag_from_registry(["inc_1"])
        data = _make_data(30)
        executor = DagExecutor(DagExecutorConfig(max_workers=2))
        report = executor.execute(dag, data, mode=BATCH)
        assert report.mode == BATCH
        result = report.results["inc_1"]
        assert result.success is True
        assert result.series is not None
        # pct_change(5) 前 5 个为 NaN
        assert result.series.iloc[:5].isna().all()
        assert result.series.iloc[5:].notna().all()


class TestIncrementalMode:
    def test_incremental_with_cache(self):
        """incremental 模式 + cached_results 调用 incremental_compute。"""
        _register_incremental_factor("inc_1")
        dag = build_dag_from_registry(["inc_1"])
        full_data = _make_data(40)
        # 先用 batch 模式计算前 30 天作为缓存
        cache_data = full_data.iloc[:30]
        executor = DagExecutor(DagExecutorConfig(max_workers=2))
        cache_report = executor.execute(dag, cache_data, mode=BATCH)
        cached = cache_report.results["inc_1"].series
        # 用 incremental 模式计算全部 40 天
        inc_report = executor.execute(dag, full_data, mode=INCREMENTAL, cached_results={"inc_1": cached})
        assert inc_report.mode == INCREMENTAL
        inc_result = inc_report.results["inc_1"]
        assert inc_result.success is True
        assert inc_result.series is not None
        # 增量结果应有 40 个数据点
        assert len(inc_result.series) == 40

    def test_incremental_without_cache_falls_back(self):
        """incremental 模式但无缓存时回退到 compute()。"""
        _register_incremental_factor("inc_1")
        dag = build_dag_from_registry(["inc_1"])
        data = _make_data(30)
        executor = DagExecutor(DagExecutorConfig(max_workers=2))
        report = executor.execute(dag, data, mode=INCREMENTAL)
        assert report.mode == INCREMENTAL
        result = report.results["inc_1"]
        assert result.success is True
        # 无缓存 → 回退到 compute，结果与 batch 一致
        assert len(result.series) == 30

    def test_incremental_matches_batch(self):
        """增量模式结果与全量模式一致（在有缓存的情况下）。"""
        _register_incremental_factor("inc_1")
        dag = build_dag_from_registry(["inc_1"])
        full_data = _make_data(40)
        executor = DagExecutor(DagExecutorConfig(max_workers=2))
        # 全量计算
        batch_report = executor.execute(dag, full_data, mode=BATCH)
        batch_series = batch_report.results["inc_1"].series
        # 增量计算（缓存前 30 天）
        cache_data = full_data.iloc[:30]
        cache_report = executor.execute(dag, cache_data, mode=BATCH)
        cached = cache_report.results["inc_1"].series
        inc_report = executor.execute(dag, full_data, mode=INCREMENTAL, cached_results={"inc_1": cached})
        inc_series = inc_report.results["inc_1"].series
        # 比较 non-NaN 部分
        valid = batch_series.notna()
        pd.testing.assert_series_equal(inc_series[valid], batch_series[valid], check_names=False)


class TestReportModeField:
    def test_report_has_mode_field(self):
        _register_incremental_factor("inc_1")
        dag = build_dag_from_registry(["inc_1"])
        data = _make_data(30)
        executor = DagExecutor(DagExecutorConfig(max_workers=2))
        report = executor.execute(dag, data, mode=BATCH)
        assert hasattr(report, "mode")
        assert report.mode == BATCH

    def test_report_mode_incremental(self):
        _register_incremental_factor("inc_1")
        dag = build_dag_from_registry(["inc_1"])
        data = _make_data(30)
        executor = DagExecutor(DagExecutorConfig(max_workers=2))
        report = executor.execute(dag, data, mode=INCREMENTAL)
        assert report.mode == INCREMENTAL
