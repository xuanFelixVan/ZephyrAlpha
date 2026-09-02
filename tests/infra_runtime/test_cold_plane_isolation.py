# [BLUEPRINT] MOD-INF-079 | docs/03_modules/_domain_infrastructure_runtime/cold_plane_isolation/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INF-079 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.infra_runtime.test_cold_plane_isolation
# [TESTS] src/zephyr/infra_runtime/cold_plane_isolation.py
"""MOD-INF-079 单元测试：cold_plane_isolation Cold 平面隔离器。

蓝图验收（B14-04550/CAND-H1FS-012，A9 运维架构 §平面隔离）：
资源配额声明校验（核 16-19/内存≤20GB/IO BelowNormal/iFind≤5QPS 令牌桶）+
Cold→Warm 仅 config:* 30s 轮询通道白名单 + Cold→Hot 直连拒绝+告警（Fail-Closed）+
盘中产出入待激活队列盘后应用（pending→applied）。时钟/交易时段/告警全注入内存替身。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.infra_runtime.cold_plane_isolation",
    reason="cold_plane_isolation not importable",
)

from zephyr.infra_runtime.cold_plane_isolation import (  # noqa: E402
    ColdPlaneError,
    ColdPlaneIsolator,
    ColdPlaneViolation,
    PendingStatus,
    Plane,
    ResourceQuota,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)


class _Clock:
    def __init__(self) -> None:
        self.now = _T0

    def __call__(self) -> datetime.datetime:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += datetime.timedelta(seconds=seconds)


def _isolator(
    trading: bool = False,
    alerts: list | None = None,
    clock: _Clock | None = None,
) -> ColdPlaneIsolator:
    return ColdPlaneIsolator(
        clock=clock or _Clock(),
        is_trading_hours=lambda: trading,
        alert_sink=(lambda v: alerts.append(v)) if alerts is not None else None,
    )


def _quota(
    cores=(16, 17),
    memory_gb=20.0,
    io_priority="below_normal",
    ifind_qps=5.0,
) -> ResourceQuota:
    return ResourceQuota(
        cores=tuple(cores),
        memory_gb=memory_gb,
        io_priority=io_priority,
        ifind_qps=ifind_qps,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 配额声明校验（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestDeclareQuota:
    def test_valid_quota_accepted(self) -> None:
        iso = _isolator()
        assert iso.declare_quota(_quota(cores=(16, 17, 18, 19))).ifind_qps == 5.0

    def test_cores_outside_16_19_raises(self) -> None:
        with pytest.raises(ColdPlaneError):
            _isolator().declare_quota(_quota(cores=(15, 16)))
        with pytest.raises(ColdPlaneError):
            _isolator().declare_quota(_quota(cores=(20,)))

    def test_empty_cores_raises(self) -> None:
        with pytest.raises(ColdPlaneError):
            _isolator().declare_quota(_quota(cores=()))

    def test_memory_over_20gb_raises(self) -> None:
        with pytest.raises(ColdPlaneError):
            _isolator().declare_quota(_quota(memory_gb=20.5))
        with pytest.raises(ColdPlaneError):
            _isolator().declare_quota(_quota(memory_gb=0))

    def test_io_priority_must_be_below_normal(self) -> None:
        with pytest.raises(ColdPlaneError):
            _isolator().declare_quota(_quota(io_priority="normal"))

    def test_ifind_qps_over_5_raises(self) -> None:
        with pytest.raises(ColdPlaneError):
            _isolator().declare_quota(_quota(ifind_qps=5.1))
        with pytest.raises(ColdPlaneError):
            _isolator().declare_quota(_quota(ifind_qps=0))


# ──────────────────────────────────────────────────────────────────────────────
# 通道白名单（Cold→Warm config:* / Cold→Hot 拒绝+告警）
# ──────────────────────────────────────────────────────────────────────────────


class TestChannels:
    def test_cold_to_warm_config_channel_ok(self) -> None:
        iso = _isolator()
        iso.open_channel("config:runtime", Plane.COLD, Plane.WARM)
        assert iso.is_open("config:runtime")

    def test_cold_to_warm_non_config_rejected_with_alert(self) -> None:
        alerts: list[ColdPlaneViolation] = []
        iso = _isolator(alerts=alerts)
        with pytest.raises(ColdPlaneError):
            iso.open_channel("data:factors", Plane.COLD, Plane.WARM)
        assert len(alerts) == 1
        assert alerts[0].source is Plane.COLD
        assert alerts[0].target is Plane.WARM

    def test_cold_to_warm_poll_interval_must_be_30s(self) -> None:
        with pytest.raises(ColdPlaneError):
            _isolator().open_channel("config:runtime", Plane.COLD, Plane.WARM, poll_interval_s=10.0)

    def test_cold_to_hot_direct_rejected_with_alert(self) -> None:
        alerts: list[ColdPlaneViolation] = []
        iso = _isolator(alerts=alerts)
        with pytest.raises(ColdPlaneError):
            iso.open_channel("anything", Plane.COLD, Plane.HOT)
        assert len(alerts) == 1
        assert alerts[0].target is Plane.HOT
        assert not iso.is_open("anything")

    def test_other_directions_allowed(self) -> None:
        iso = _isolator()
        iso.open_channel("signal:flow", Plane.WARM, Plane.HOT)
        iso.open_channel("audit:trail", Plane.WARM, Plane.COLD, poll_interval_s=5.0)
        assert iso.is_open("signal:flow")
        assert iso.is_open("audit:trail")

    def test_duplicate_channel_raises(self) -> None:
        iso = _isolator()
        iso.open_channel("config:runtime", Plane.COLD, Plane.WARM)
        with pytest.raises(ColdPlaneError):
            iso.open_channel("config:runtime", Plane.COLD, Plane.WARM)

    def test_empty_channel_raises(self) -> None:
        with pytest.raises(ColdPlaneError):
            _isolator().open_channel("", Plane.COLD, Plane.WARM)


# ──────────────────────────────────────────────────────────────────────────────
# iFind 令牌桶（注入时钟）
# ──────────────────────────────────────────────────────────────────────────────


class TestIfindTokenBucket:
    def test_burst_up_to_declared_qps_then_reject(self) -> None:
        clock = _Clock()
        iso = _isolator(clock=clock)
        iso.declare_quota(_quota(ifind_qps=2.0))
        iso.acquire_ifind()
        iso.acquire_ifind()
        with pytest.raises(ColdPlaneError):
            iso.acquire_ifind()  # 第 3 次超限 Fail-Closed

    def test_refill_over_time(self) -> None:
        clock = _Clock()
        iso = _isolator(clock=clock)
        iso.declare_quota(_quota(ifind_qps=2.0))
        iso.acquire_ifind()
        iso.acquire_ifind()
        clock.advance(0.5)  # 0.5s × 2QPS = 1 令牌
        iso.acquire_ifind()
        with pytest.raises(ColdPlaneError):
            iso.acquire_ifind()

    def test_default_bucket_5qps(self) -> None:
        iso = _isolator()
        for _ in range(5):
            iso.acquire_ifind()
        with pytest.raises(ColdPlaneError):
            iso.acquire_ifind()


# ──────────────────────────────────────────────────────────────────────────────
# 待激活队列（盘中 pending → 盘后 applied）
# ──────────────────────────────────────────────────────────────────────────────


class TestPendingActivation:
    def test_submit_and_apply_after_hours(self) -> None:
        clock = _Clock()
        iso = _isolator(trading=False, clock=clock)
        iso.submit_artifact("cfg-b", {"k": 2})
        clock.advance(1.0)  # cfg-a 产出更晚
        iso.submit_artifact("cfg-a", {"k": 1})
        applied = iso.apply_pending()
        assert [a.artifact_id for a in applied] == ["cfg-b", "cfg-a"]  # 按 produced_at 序
        assert all(a.status is PendingStatus.APPLIED for a in applied)
        assert all(a.applied_at is not None for a in applied)

    def test_apply_during_trading_hours_raises(self) -> None:
        iso = _isolator(trading=True)
        iso.submit_artifact("cfg-a", {})
        with pytest.raises(ColdPlaneError):
            iso.apply_pending()
        pend = iso.pending_activations(PendingStatus.PENDING)
        assert [p.artifact_id for p in pend] == ["cfg-a"]

    def test_empty_artifact_id_raises(self) -> None:
        with pytest.raises(ColdPlaneError):
            _isolator().submit_artifact("", {})

    def test_duplicate_artifact_id_raises(self) -> None:
        iso = _isolator()
        iso.submit_artifact("cfg-a", {})
        with pytest.raises(ColdPlaneError):
            iso.submit_artifact("cfg-a", {})

    def test_apply_twice_idempotent(self) -> None:
        iso = _isolator(trading=False)
        iso.submit_artifact("cfg-a", {})
        first = iso.apply_pending()
        second = iso.apply_pending()
        assert [a.artifact_id for a in first] == [a.artifact_id for a in second]
        assert all(a.status is PendingStatus.APPLIED for a in second)

    def test_pending_filter_by_status(self) -> None:
        iso = _isolator(trading=False)
        iso.submit_artifact("cfg-a", {})
        assert len(iso.pending_activations(PendingStatus.PENDING)) == 1
        assert iso.pending_activations(PendingStatus.APPLIED) == []
        iso.apply_pending()
        assert iso.pending_activations(PendingStatus.PENDING) == []
        assert len(iso.pending_activations(PendingStatus.APPLIED)) == 1

    def test_deterministic_replay(self) -> None:
        def build() -> list[str]:
            iso = _isolator(trading=False)
            iso.submit_artifact("x-1", {"v": 1})
            iso.submit_artifact("x-2", {"v": 2})
            return [a.artifact_id for a in iso.apply_pending()]

        assert build() == build() == ["x-1", "x-2"]  # 同输入必同输出
