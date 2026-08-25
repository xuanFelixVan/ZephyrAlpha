# [BLUEPRINT] MOD-DATA_ENG | docs/03_modules/_domain_data_eng/incremental_update_engine/blueprint.md
# [MODULE] tests.zephyr.data.test_incremental_update_engine
# [DOMAIN] D_DATA_ENG
# [DEPENDENCIES] zephyr.data_eng.incremental_update_engine
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DATA_ENG | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-DATA_ENG Incremental Update Engine（91 增量更新协调引擎）单元测试.

覆盖: 统一变更检测(水位线/updated_at/行数哈希三通道)/增量抽样全量对账
(偏差率+超容差告警+alert异常不阻断)/增量因子注册表(窗口状态更新+持久化
快照往返)/输入校验Fail-Closed.
"""

from __future__ import annotations

import pytest

from zephyr.data_eng.incremental_update_engine import (
    ChangeSignal,
    IncrementalFactorRegistry,
    IncrementalUpdateError,
    InvalidIncrementalInputError,
    SampleReconcileResult,
    SamplingReconciler,
    detect_change,
)


class TestChangeDetection:
    def test_first_observation_unknown(self):
        signal = ChangeSignal(source_id="kline_daily", watermark="2026-08-25", updated_at_max="2026-08-25T15:00:00", row_count=100, row_hash="h1")
        verdict = detect_change(None, signal)
        assert verdict.changed is True
        assert "FIRST_OBSERVATION" in verdict.reasons

    def test_unchanged(self):
        prev = ChangeSignal(source_id="s", watermark="k1", updated_at_max="t1", row_count=10, row_hash="h")
        curr = ChangeSignal(source_id="s", watermark="k1", updated_at_max="t1", row_count=10, row_hash="h")
        verdict = detect_change(prev, curr)
        assert verdict.changed is False
        assert verdict.reasons == ()

    def test_watermark_advanced(self):
        prev = ChangeSignal(source_id="s", watermark="k1", updated_at_max="t1", row_count=10, row_hash="h")
        curr = ChangeSignal(source_id="s", watermark="k2", updated_at_max="t1", row_count=10, row_hash="h")
        verdict = detect_change(prev, curr)
        assert verdict.changed is True
        assert "WATERMARK_ADVANCED" in verdict.reasons

    def test_updated_at_and_row_signals(self):
        prev = ChangeSignal(source_id="s", watermark="k1", updated_at_max="t1", row_count=10, row_hash="h")
        curr = ChangeSignal(source_id="s", watermark="k1", updated_at_max="t2", row_count=11, row_hash="h2")
        verdict = detect_change(prev, curr)
        assert verdict.changed is True
        assert "UPDATED_AT_ADVANCED" in verdict.reasons
        assert "ROW_COUNT_CHANGED" in verdict.reasons
        assert "ROW_HASH_CHANGED" in verdict.reasons

    def test_source_id_mismatch_fail_closed(self):
        prev = ChangeSignal(source_id="s1", watermark="k1", updated_at_max="t1", row_count=10, row_hash="h")
        curr = ChangeSignal(source_id="s2", watermark="k1", updated_at_max="t1", row_count=10, row_hash="h")
        with pytest.raises(InvalidIncrementalInputError):
            detect_change(prev, curr)


class TestSamplingReconciler:
    def test_full_match_no_alert(self):
        alerts: list[str] = []
        reconciler = SamplingReconciler(tolerance_ratio=0.01, alert_sink=alerts.append)
        result = reconciler.reconcile(
            incremental={"a": 1, "b": 2},
            full={"a": 1, "b": 2},
        )
        assert isinstance(result, SampleReconcileResult)
        assert result.matched == 2
        assert result.mismatched == 0
        assert result.deviation_ratio == 0.0
        assert result.alerted is False
        assert alerts == []

    def test_deviation_within_tolerance_no_alert(self):
        alerts: list[str] = []
        reconciler = SamplingReconciler(tolerance_ratio=0.5, alert_sink=alerts.append)
        result = reconciler.reconcile(
            incremental={"a": 1, "b": 2, "c": 3, "d": 4},
            full={"a": 1, "b": 2, "c": 3, "d": 99},
        )
        assert result.mismatched == 1
        assert result.deviation_ratio == pytest.approx(0.25)
        assert result.alerted is False
        assert alerts == []

    def test_deviation_breach_alerts(self):
        alerts: list[str] = []
        reconciler = SamplingReconciler(tolerance_ratio=0.01, alert_sink=alerts.append)
        result = reconciler.reconcile(
            incremental={"a": 1, "b": 2},
            full={"a": 1, "b": 99},
        )
        assert result.mismatched == 1
        assert result.alerted is True
        assert len(alerts) == 1

    def test_missing_records_counted(self):
        reconciler = SamplingReconciler(tolerance_ratio=1.0)
        result = reconciler.reconcile(
            incremental={"a": 1},
            full={"a": 1, "b": 2},
        )
        assert result.missing_in_full == 0
        assert result.missing_in_incremental == 1

    def test_alert_sink_exception_does_not_block(self):
        def _boom(_msg: str) -> None:
            raise RuntimeError("alert down")

        reconciler = SamplingReconciler(tolerance_ratio=0.0, alert_sink=_boom)
        result = reconciler.reconcile(incremental={"a": 1}, full={"a": 2})
        assert result.alerted is True  # 偏差告警已触发（sink 异常不影响结果）

    def test_invalid_tolerance_fail_closed(self):
        with pytest.raises(InvalidIncrementalInputError):
            SamplingReconciler(tolerance_ratio=-0.1)


class TestIncrementalFactorRegistry:
    def test_register_and_window_state(self):
        registry = IncrementalFactorRegistry()
        registry.register("momentum_20", window=20)
        registry.update_window_state("momentum_20", last_key="2026-08-25", updated_at="2026-08-25T15:00:00")
        state = registry.get("momentum_20")
        assert state is not None
        assert state.window == 20
        assert state.last_key == "2026-08-25"

    def test_duplicate_register_idempotent(self):
        registry = IncrementalFactorRegistry()
        registry.register("f1", window=10)
        registry.update_window_state("f1", last_key="k1", updated_at="t1")
        registry.register("f1", window=99)  # 幂等: 不覆盖既有窗口状态
        state = registry.get("f1")
        assert state is not None
        assert state.last_key == "k1"

    def test_snapshot_round_trip(self):
        registry = IncrementalFactorRegistry()
        registry.register("f1", window=10)
        registry.update_window_state("f1", last_key="k1", updated_at="t1")
        snapshot = registry.to_snapshot()
        restored = IncrementalFactorRegistry.from_snapshot(snapshot)
        state = restored.get("f1")
        assert state is not None
        assert state.window == 10
        assert state.last_key == "k1"
        assert state.updated_at == "t1"

    def test_update_unknown_factor_fail_closed(self):
        registry = IncrementalFactorRegistry()
        with pytest.raises(InvalidIncrementalInputError):
            registry.update_window_state("ghost", last_key="k", updated_at="t")

    def test_register_invalid_input(self):
        registry = IncrementalFactorRegistry()
        with pytest.raises(InvalidIncrementalInputError):
            registry.register("", window=10)
        with pytest.raises(InvalidIncrementalInputError):
            registry.register("f1", window=0)

    def test_error_hierarchy(self):
        assert issubclass(InvalidIncrementalInputError, IncrementalUpdateError)
