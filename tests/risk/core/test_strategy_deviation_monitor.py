# [BLUEPRINT] MOD-RK-23 | docs/03_modules/_domain_risk/strategy_deviation_monitor/blueprint.md
# [MODULE] tests.risk.core.test_strategy_deviation_monitor
# [DOMAIN] D_RISK
# [INVARIANTS] 阈值真源=alert_threshold_registry(fail-closed);双口径(累计偏差/日收益相关);事件去抖=仅级别变化发射;不改策略状态
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidDeviationInputError;DeviationConfigError
# [TESTS] self
# [A_module] module_id=MOD-RK-23 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-RK-23 Strategy Deviation Monitor 单元测试（55 号 G26 §3.4）.

覆盖:
  - 阈值从 alert_threshold_registry 加载（0.30/0.50/0.5，与注册表一致）
  - OK / WARN / RETIRE 三档判定 + 双口径（累计相对偏差 / Pearson 相关）
  - 事件去抖：仅级别变化发射（含降级）；首评 OK 不发射
  - 边界：样本不足 / 零回测累计 / 零方差相关 / 尾部长度对齐 / NaN 拒绝
  - fail-closed：注册表缺失 → DeviationConfigError
  - 基准供给桥：run 不存在 / 无 artifact → None（降级不抛）
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest
import yaml

from zephyr.risk.core.strategy_deviation_monitor import (
    DeviationAction,
    DeviationConfigError,
    InvalidDeviationInputError,
    StrategyDeviationMonitor,
)

NOW = datetime(2026, 8, 15, 15, 0, 0)


def _flat(n: int, r: float = 0.0) -> list[float]:
    return [r] * n


class TestThresholdLoading:
    def test_thresholds_match_registry(self):
        monitor = StrategyDeviationMonitor()
        th = monitor.thresholds
        assert th["warn"] == 0.30
        assert th["retire"] == 0.50
        assert th["correlation_floor"] == 0.5

    def test_missing_registry_fail_closed(self, tmp_path: Path):
        with pytest.raises(DeviationConfigError):
            StrategyDeviationMonitor(registry_path=tmp_path / "nonexistent.yaml")

    def test_missing_entry_fail_closed(self, tmp_path: Path):
        bad = tmp_path / "reg.yaml"
        bad.write_text(
            yaml.safe_dump({"thresholds": [{"threshold_id": "THD-DEVIATION-001", "value": 0.3}]}),
            encoding="utf-8",
        )
        with pytest.raises(DeviationConfigError) as exc_info:
            StrategyDeviationMonitor(registry_path=bad)
        assert exc_info.value.details["threshold_id"] == "THD-DEVIATION-002"


class TestEvaluate:
    def test_identical_series_ok(self):
        m = StrategyDeviationMonitor()
        series = [0.01, 0.02, -0.005, 0.008, 0.012, -0.003, 0.015, 0.006, -0.008, 0.01]
        v = m.evaluate("STR-A", series, series, now=NOW)
        assert v.action is DeviationAction.OK
        assert v.cum_relative_deviation == pytest.approx(0.0)
        assert v.daily_return_correlation == pytest.approx(1.0)
        assert v.sufficient_data is True

    def test_mild_wear_ok(self):
        """实盘略逊回测（正常磨损 10-20% 区间内）→ OK。"""
        m = StrategyDeviationMonitor()
        bt = _flat(10, 0.010)
        lv = _flat(10, 0.009)  # 累计偏差约 9% < 30%
        v = m.evaluate("STR-A", lv, bt, now=NOW)
        assert v.action is DeviationAction.OK
        assert 0.0 < v.cum_relative_deviation < 0.30

    def test_warn_band(self):
        m = StrategyDeviationMonitor()
        bt = _flat(10, 0.010)
        lv = _flat(10, 0.0065)  # 累计偏差 ~35%
        v = m.evaluate("STR-A", lv, bt, now=NOW)
        assert v.action is DeviationAction.WARN

    def test_retire_band(self):
        m = StrategyDeviationMonitor()
        bt = _flat(10, 0.010)
        lv = _flat(10, 0.003)  # 累计偏差 ~70%
        v = m.evaluate("STR-A", lv, bt, now=NOW)
        assert v.action is DeviationAction.RETIRE

    def test_zero_backtest_cum_live_moved_retire(self):
        m = StrategyDeviationMonitor()
        bt = [0.01, -0.01] * 5  # 累计≈0
        lv = _flat(10, 0.01)  # 累计约 10%
        v = m.evaluate("STR-A", lv, bt, now=NOW)
        assert v.action is DeviationAction.RETIRE

    def test_zero_backtest_cum_both_flat_ok(self):
        m = StrategyDeviationMonitor()
        bt = [0.01, -0.01] * 5
        lv = [0.01, -0.01] * 5
        v = m.evaluate("STR-A", lv, bt, now=NOW)
        assert v.action is DeviationAction.OK

    def test_zero_variance_correlation_none(self):
        m = StrategyDeviationMonitor()
        v = m.evaluate("STR-A", _flat(10, 0.01), _flat(10, 0.01), now=NOW)
        assert v.daily_return_correlation is None  # 零方差序列相关无定义
        assert v.correlation_below_floor is False

    def test_uncorrelated_flags_below_floor(self):
        m = StrategyDeviationMonitor()
        bt = [0.01, -0.01, 0.02, -0.02, 0.01, -0.01, 0.02, -0.02, 0.01, -0.01]
        lv = [-0.02, 0.02, -0.01, 0.01, -0.02, 0.02, -0.01, 0.01, -0.02, 0.02]
        v = m.evaluate("STR-A", lv, bt, now=NOW)
        assert v.daily_return_correlation is not None
        assert v.daily_return_correlation < 0.5
        assert v.correlation_below_floor is True

    def test_tail_alignment(self):
        m = StrategyDeviationMonitor()
        bt = _flat(12, 0.01)
        lv = _flat(10, 0.01)
        v = m.evaluate("STR-A", lv, bt, now=NOW)
        assert v.sample_size == 10
        assert v.action is DeviationAction.OK

    def test_insufficient_samples(self):
        m = StrategyDeviationMonitor()
        v = m.evaluate("STR-A", _flat(3, 0.01), _flat(3, 0.01), now=NOW)
        assert v.sufficient_data is False
        assert v.action is DeviationAction.OK
        assert v.cum_relative_deviation is None

    def test_nan_rejected(self):
        m = StrategyDeviationMonitor()
        with pytest.raises(InvalidDeviationInputError):
            m.evaluate("STR-A", [0.01] * 9 + [float("nan")], _flat(10, 0.01), now=NOW)

    def test_empty_rejected(self):
        m = StrategyDeviationMonitor()
        with pytest.raises(InvalidDeviationInputError):
            m.evaluate("STR-A", [], [], now=NOW)


class TestEventDebounce:
    def test_emit_only_on_level_change(self):
        m = StrategyDeviationMonitor()
        events = []
        m.on_deviation_alerted(events.append)
        bt = _flat(10, 0.010)
        # 首评 OK —— 不发射
        m.evaluate("STR-A", _flat(10, 0.010), bt, now=NOW)
        assert events == []
        # OK → WARN 发射一次
        m.evaluate("STR-A", _flat(10, 0.0065), bt, now=NOW)
        assert len(events) == 1
        assert events[0].previous_action is DeviationAction.OK
        assert events[0].new_action is DeviationAction.WARN
        # 同级重评不再发射
        m.evaluate("STR-A", _flat(10, 0.0065), bt, now=NOW)
        assert len(events) == 1
        # WARN → RETIRE 发射
        m.evaluate("STR-A", _flat(10, 0.003), bt, now=NOW)
        assert len(events) == 2
        assert events[1].new_action is DeviationAction.RETIRE
        # RETIRE → OK 降级也发射
        m.evaluate("STR-A", _flat(10, 0.010), bt, now=NOW)
        assert len(events) == 3
        assert events[2].new_action is DeviationAction.OK

    def test_listener_exception_isolated(self):
        m = StrategyDeviationMonitor()
        m.on_deviation_alerted(lambda e: (_ for _ in ()).throw(RuntimeError("boom")))
        bt = _flat(10, 0.010)
        v = m.evaluate("STR-A", _flat(10, 0.0065), bt, now=NOW)  # WARN, 监听器抛异常不阻断
        assert v.action is DeviationAction.WARN

    def test_latest_verdicts_snapshot(self):
        m = StrategyDeviationMonitor()
        bt = _flat(10, 0.010)
        m.evaluate("STR-A", _flat(10, 0.010), bt, now=NOW)
        m.evaluate("STR-B", _flat(10, 0.003), bt, now=NOW)
        verdicts = m.get_latest_verdicts()
        assert set(verdicts) == {"STR-A", "STR-B"}
        assert verdicts["STR-B"].action is DeviationAction.RETIRE


class TestExperimentTrackingBridge:
    def test_run_not_found_returns_none(self):
        result = StrategyDeviationMonitor.load_backtest_returns_from_experiment("run-nonexistent-mon001")
        assert result is None

    def test_artifact_parsing(self, tmp_path: Path, monkeypatch):
        csv_file = tmp_path / "nav_curve_experiment.csv"
        csv_file.write_text(",nav\n2026-08-10,1.0\n2026-08-11,1.01\n2026-08-12,1.02\n", encoding="utf-8")

        class _FakeDetail:
            artifact_paths = {"nav/nav_curve_experiment.csv": str(csv_file)}

        import zephyr.experiment_tracking.query as q

        monkeypatch.setattr(q, "get_run", lambda run_id: _FakeDetail())
        returns = StrategyDeviationMonitor.load_backtest_returns_from_experiment("run-x")
        assert returns == pytest.approx([0.01, 1.02 / 1.01 - 1.0])

    def test_artifact_missing_returns_none(self, monkeypatch):
        class _FakeDetail:
            artifact_paths = {"other.txt": "/tmp/x"}

        import zephyr.experiment_tracking.query as q

        monkeypatch.setattr(q, "get_run", lambda run_id: _FakeDetail())
        assert StrategyDeviationMonitor.load_backtest_returns_from_experiment("run-x") is None
