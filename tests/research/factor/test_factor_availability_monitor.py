# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] tests.factor.test_factor_availability_monitor
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.factor_availability_monitor
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] production
# [INVARIANTS] 纯内存注册表+Series测试，不触网不触库
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=可用性计算/阈值门控逻辑缺陷
# [TESTS] 本文件
# [TTL] permanent
"""FactorAvailabilityMonitor 单元测试（CAND-FAC-006 canonical / B13-04305，合并 B2-05116）。

覆盖（min_build_spec 合并定义）：
- 覆盖率+缺失比例逐日计算（覆盖率=1-缺失率，注册因子 ONLINE 状态占比）
- 三级阈值 80%/50%/20% 分级：ok/warn/degraded/blocked
- is_degraded 降级标记 + 缺失告警路由
- 低于 20% 阻断信号合成
- 降级状态写 FactorSignal 元数据供下游降权
"""

from __future__ import annotations

import datetime

import pandas as pd
import pytest

from zephyr.factor.factor_availability_monitor import (
    AvailabilityLevel,
    FactorAvailabilityMonitor,
)
from zephyr.shared.contracts.factor_signal import FactorSignal


class _FakeMeta:
    def __init__(self, factor_id: str) -> None:
        self.factor_id = factor_id


class _FakeRegistry:
    """FactorRegistry 协议替身（list_all() -> metas with factor_id）。"""

    def __init__(self, factor_ids: list[str]) -> None:
        self._metas = [_FakeMeta(fid) for fid in factor_ids]

    def list_all(self) -> list[_FakeMeta]:
        return list(self._metas)


def _series(values, start="2026-08-01") -> pd.Series:
    idx = pd.date_range(start, periods=len(values), freq="D")
    return pd.Series(values, index=idx)


def _signal(factor_id: str = "f1") -> FactorSignal:
    return FactorSignal(
        as_of_date=datetime.datetime(2026, 8, 24, tzinfo=datetime.timezone.utc),
        factor_id=factor_id,
        idempotency_key="k1",
        raw_value=1.0,
        symbol="600519.SH",
    )


class TestCoverageComputation:
    """覆盖率+缺失比例逐日计算。"""

    def test_full_coverage(self) -> None:
        reg = _FakeRegistry(["f1", "f2", "f3", "f4"])
        mon = FactorAvailabilityMonitor(registry=reg)
        values = {fid: _series([1.0, 2.0, 3.0]) for fid in ("f1", "f2", "f3", "f4")}
        rep = mon.compute_daily(values, as_of="2026-08-24")
        assert rep.registered_total == 4
        assert rep.online_count == 4
        assert rep.coverage == pytest.approx(1.0)
        assert rep.missing_ratio == pytest.approx(0.0)
        assert rep.level == AvailabilityLevel.OK
        assert rep.is_degraded is False
        assert rep.block_signal_synthesis is False

    def test_missing_series_counts_offline(self) -> None:
        reg = _FakeRegistry(["f1", "f2", "f3", "f4"])
        mon = FactorAvailabilityMonitor(registry=reg)
        values = {"f1": _series([1.0]), "f2": None, "f3": _series([3.0])}  # f4 无数据
        rep = mon.compute_daily(values, as_of="2026-08-24")
        assert rep.online_count == 2
        assert rep.coverage == pytest.approx(0.5)
        assert rep.missing_ratio == pytest.approx(0.5)
        assert rep.per_factor_missing["f2"] == pytest.approx(1.0)
        assert rep.per_factor_missing["f4"] == pytest.approx(1.0)
        assert rep.per_factor_missing["f1"] == pytest.approx(0.0)

    def test_partial_nan_series_missing_ratio(self) -> None:
        reg = _FakeRegistry(["f1"])
        mon = FactorAvailabilityMonitor(registry=reg)
        values = {"f1": _series([1.0, None, None, 4.0])}
        rep = mon.compute_daily(values, as_of="2026-08-24")
        assert rep.per_factor_missing["f1"] == pytest.approx(0.5)

    def test_empty_registry_zero_coverage(self) -> None:
        mon = FactorAvailabilityMonitor(registry=_FakeRegistry([]))
        rep = mon.compute_daily({}, as_of="2026-08-24")
        assert rep.registered_total == 0
        assert rep.coverage == pytest.approx(0.0)
        assert rep.block_signal_synthesis is True


class TestThreeTierThresholds:
    """三级阈值 80%/50%/20% 分级。"""

    def _coverage(self, online: int, total: int):
        reg = _FakeRegistry([f"f{i}" for i in range(total)])
        mon = FactorAvailabilityMonitor(registry=reg)
        values = {f"f{i}": _series([1.0]) for i in range(online)}
        return mon.compute_daily(values, as_of="2026-08-24")

    def test_90pct_ok(self) -> None:
        rep = self._coverage(9, 10)
        assert rep.level == AvailabilityLevel.OK
        assert rep.is_degraded is False

    def test_70pct_warn(self) -> None:
        rep = self._coverage(7, 10)
        assert rep.level == AvailabilityLevel.WARN
        assert rep.is_degraded is False

    def test_30pct_degraded(self) -> None:
        rep = self._coverage(3, 10)
        assert rep.level == AvailabilityLevel.DEGRADED
        assert rep.is_degraded is True
        assert rep.block_signal_synthesis is False

    def test_below_20pct_blocks(self) -> None:
        rep = self._coverage(1, 10)
        assert rep.level == AvailabilityLevel.BLOCKED
        assert rep.is_degraded is True
        assert rep.block_signal_synthesis is True

    def test_exactly_80pct_ok_boundary(self) -> None:
        rep = self._coverage(8, 10)
        assert rep.level == AvailabilityLevel.OK

    def test_exactly_50pct_warn_boundary(self) -> None:
        rep = self._coverage(5, 10)
        assert rep.level == AvailabilityLevel.WARN
        assert rep.is_degraded is False

    def test_exactly_20pct_degraded_boundary(self) -> None:
        rep = self._coverage(2, 10)
        assert rep.level == AvailabilityLevel.DEGRADED
        assert rep.block_signal_synthesis is False


class TestAlertRouting:
    """缺失告警路由复用。"""

    def test_alert_sink_invoked_on_missing(self) -> None:
        calls: list[tuple[str, str, str]] = []
        reg = _FakeRegistry(["f1", "f2", "f3"])
        mon = FactorAvailabilityMonitor(
            registry=reg, alert_sink=lambda sev, title, msg: calls.append((sev, title, msg))
        )
        mon.compute_daily({"f1": _series([1.0])}, as_of="2026-08-24")
        assert calls, "缺失因子应触发告警"
        assert any("f2" in c[2] or "f3" in c[2] for c in calls)

    def test_no_alert_on_full_coverage(self) -> None:
        calls: list[tuple[str, str, str]] = []
        reg = _FakeRegistry(["f1"])
        mon = FactorAvailabilityMonitor(
            registry=reg, alert_sink=lambda sev, title, msg: calls.append((sev, title, msg))
        )
        mon.compute_daily({"f1": _series([1.0])}, as_of="2026-08-24")
        assert calls == []


class TestSignalAnnotation:
    """降级状态写 FactorSignal 元数据供下游降权。"""

    def test_annotate_degraded_signal(self) -> None:
        reg = _FakeRegistry(["f1", "f2", "f3", "f4", "f5"])
        mon = FactorAvailabilityMonitor(registry=reg)
        rep = mon.compute_daily({"f1": _series([1.0]), "f2": _series([2.0])}, as_of="2026-08-24")
        assert rep.is_degraded is True
        sig = mon.annotate_signal(_signal("f1"), rep)
        assert sig.extra["is_degraded"] is True
        assert sig.extra["availability_level"] == "degraded"
        assert sig.extra["coverage"] == pytest.approx(0.4)
        assert sig.confidence < 1.0  # 下游可据此降权

    def test_annotate_ok_signal_unchanged_confidence(self) -> None:
        reg = _FakeRegistry(["f1"])
        mon = FactorAvailabilityMonitor(registry=reg)
        rep = mon.compute_daily({"f1": _series([1.0])}, as_of="2026-08-24")
        sig = mon.annotate_signal(_signal("f1"), rep)
        assert sig.extra["is_degraded"] is False
        assert sig.confidence == pytest.approx(1.0)

    def test_signal_weight_mapping(self) -> None:
        reg = _FakeRegistry(["f1", "f2", "f3", "f4", "f5"])
        mon = FactorAvailabilityMonitor(registry=reg)
        ok = mon.compute_daily({f"f{i}": _series([1.0]) for i in range(5)}, as_of="2026-08-24")
        assert mon.signal_weight(ok) == pytest.approx(1.0)
        blocked = mon.compute_daily({}, as_of="2026-08-24")
        assert mon.signal_weight(blocked) == pytest.approx(0.0)
