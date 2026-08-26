# [BLUEPRINT] MOD-INF-074 | docs/03_modules/_domain_infrastructure_runtime/resource_scheduler/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-INF-074 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.infra_runtime.test_resource_scheduler
# [TESTS] src/zephyr/infra_runtime/resource_scheduler.py
"""MOD-INF-074 单元测试：resource_scheduler 资源调度器。

蓝图验收（B7-09926/CAND-H1FS-014，D-INFRA-RUNTIME §2）：
CPU 核心亲和绑定（平面核子集+平面内独占）+ 内存预算强制 +
Hot/Warm/Cold 三平面隔离 + QPS 令牌桶限流（注入时钟）统一裁决入口。
executor/告警全注入内存替身，不触 OS。
"""

from __future__ import annotations

import pytest

pytest.importorskip(
    "zephyr.infra_runtime.resource_scheduler",
    reason="resource_scheduler not importable",
)

from zephyr.infra_runtime.resource_scheduler import (  # noqa: E402
    PlaneQuota,
    ResourcePlane,
    ResourceRequest,
    ResourceScheduler,
    ResourceSchedulerError,
    SchedulingRejection,
)


class _FakeClock:
    """确定性单调时钟替身。"""

    def __init__(self, t0: float = 1000.0) -> None:
        self.now = t0

    def __call__(self) -> float:
        return self.now

    def advance(self, dt: float) -> None:
        self.now += dt


_QUOTAS = {
    ResourcePlane.HOT: PlaneQuota(
        plane=ResourcePlane.HOT,
        cpu_cores=frozenset({0, 1, 2, 3}),
        mem_budget_bytes=8 * 1024**3,
        qps_limit=100.0,
    ),
    ResourcePlane.WARM: PlaneQuota(
        plane=ResourcePlane.WARM,
        cpu_cores=frozenset({4, 5, 6, 7}),
        mem_budget_bytes=12 * 1024**3,
        qps_limit=20.0,
    ),
    ResourcePlane.COLD: PlaneQuota(
        plane=ResourcePlane.COLD,
        cpu_cores=frozenset({16, 17, 18, 19}),
        mem_budget_bytes=20 * 1024**3,
        qps_limit=5.0,
    ),
}

_GIB = 1024**3


def _scheduler(
    clock: _FakeClock | None = None,
    alerts: list | None = None,
    executor=None,
) -> ResourceScheduler:
    return ResourceScheduler(
        quotas=_QUOTAS,
        clock=clock or _FakeClock(),
        executor=executor,
        alert_sink=(lambda r: alerts.append(r)) if alerts is not None else None,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 构造校验（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_empty_quotas_raises(self) -> None:
        with pytest.raises(ResourceSchedulerError):
            ResourceScheduler(quotas={})

    def test_plane_key_mismatch_raises(self) -> None:
        bad = {
            ResourcePlane.HOT: PlaneQuota(
                plane=ResourcePlane.WARM,
                cpu_cores=frozenset({0}),
                mem_budget_bytes=_GIB,
                qps_limit=1.0,
            )
        }
        with pytest.raises(ResourceSchedulerError):
            ResourceScheduler(quotas=bad)

    def test_invalid_quota_fields_raise(self) -> None:
        with pytest.raises(ResourceSchedulerError):
            ResourceScheduler(quotas={
                ResourcePlane.HOT: PlaneQuota(
                    plane=ResourcePlane.HOT,
                    cpu_cores=frozenset(),
                    mem_budget_bytes=_GIB,
                    qps_limit=1.0,
                )
            })
        with pytest.raises(ResourceSchedulerError):
            ResourceScheduler(quotas={
                ResourcePlane.HOT: PlaneQuota(
                    plane=ResourcePlane.HOT,
                    cpu_cores=frozenset({0}),
                    mem_budget_bytes=0,
                    qps_limit=1.0,
                )
            })
        with pytest.raises(ResourceSchedulerError):
            ResourceScheduler(quotas={
                ResourcePlane.HOT: PlaneQuota(
                    plane=ResourcePlane.HOT,
                    cpu_cores=frozenset({0}),
                    mem_budget_bytes=_GIB,
                    qps_limit=0.0,
                )
            })


# ──────────────────────────────────────────────────────────────────────────────
# 准入裁决：正常路径
# ──────────────────────────────────────────────────────────────────────────────


class TestAdmitOk:
    def test_admit_granted(self) -> None:
        sched = _scheduler()
        d = sched.admit(ResourcePlane.HOT, frozenset({0, 1}), 2 * _GIB, 50.0, requester="trading_core")
        assert d.granted is True
        assert d.reasons == ()

    def test_admit_records_without_executor(self) -> None:
        sched = _scheduler()
        sched.admit(ResourcePlane.HOT, frozenset({0}), _GIB, 10.0, requester="p1")
        records = sched.applied_records
        assert len(records) == 1
        assert records[0].executor_invoked is False
        assert records[0].request.requester == "p1"

    def test_admit_invokes_executor(self) -> None:
        applied: list[ResourceRequest] = []
        sched = _scheduler(executor=lambda req: applied.append(req))
        sched.admit(ResourcePlane.WARM, frozenset({4}), _GIB, 5.0, requester="signal_engine")
        assert len(applied) == 1
        assert applied[0].cpu_cores == frozenset({4})
        assert sched.applied_records[0].executor_invoked is True

    def test_anonymous_requester_allowed(self) -> None:
        sched = _scheduler()
        assert sched.admit(ResourcePlane.COLD, frozenset({16}), _GIB, 1.0).granted is True

    def test_plane_isolation_independent_budgets(self) -> None:
        sched = _scheduler()
        assert sched.admit(ResourcePlane.HOT, frozenset({0}), 8 * _GIB, 100.0, requester="h").granted
        # HOT 已满不影响 WARM/COLD
        assert sched.admit(ResourcePlane.WARM, frozenset({4}), 12 * _GIB, 20.0, requester="w").granted
        assert sched.admit(ResourcePlane.COLD, frozenset({16}), 20 * _GIB, 5.0, requester="c").granted


# ──────────────────────────────────────────────────────────────────────────────
# 准入裁决：超预算拒绝 + 告警
# ──────────────────────────────────────────────────────────────────────────────


class TestAdmitReject:
    def test_core_out_of_plane_rejected_with_alert(self) -> None:
        alerts: list[SchedulingRejection] = []
        sched = _scheduler(alerts=alerts)
        d = sched.admit(ResourcePlane.HOT, frozenset({16}), _GIB, 1.0, requester="x")
        assert d.granted is False
        assert any("亲和核越界" in r for r in d.reasons)
        assert len(alerts) == 1
        assert alerts[0].request.requester == "x"

    def test_core_conflict_rejected(self) -> None:
        sched = _scheduler()
        assert sched.admit(ResourcePlane.HOT, frozenset({0, 1}), _GIB, 1.0, requester="a").granted
        d = sched.admit(ResourcePlane.HOT, frozenset({1, 2}), _GIB, 1.0, requester="b")
        assert d.granted is False
        assert any("亲和核冲突" in r for r in d.reasons)

    def test_memory_over_budget_rejected(self) -> None:
        sched = _scheduler()
        assert sched.admit(ResourcePlane.HOT, frozenset({0}), 6 * _GIB, 1.0, requester="a").granted
        d = sched.admit(ResourcePlane.HOT, frozenset({1}), 3 * _GIB, 1.0, requester="b")
        assert d.granted is False
        assert any("内存超预算" in r for r in d.reasons)

    def test_memory_exact_budget_granted(self) -> None:
        sched = _scheduler()
        assert sched.admit(ResourcePlane.HOT, frozenset({0}), 4 * _GIB, 1.0, requester="a").granted
        assert sched.admit(ResourcePlane.HOT, frozenset({1}), 4 * _GIB, 1.0, requester="b").granted

    def test_qps_over_limit_rejected(self) -> None:
        sched = _scheduler()
        d = sched.admit(ResourcePlane.COLD, frozenset({16}), _GIB, 6.0, requester="a")
        assert d.granted is False
        assert any("限流上限" in r for r in d.reasons)

    def test_qps_token_bucket_exhaustion_and_refill(self) -> None:
        clock = _FakeClock()
        sched = _scheduler(clock=clock)
        assert sched.admit(ResourcePlane.COLD, frozenset({16}), _GIB, 5.0, requester="a").granted
        d = sched.admit(ResourcePlane.COLD, frozenset({17}), _GIB, 1.0, requester="b")
        assert d.granted is False  # 桶已空
        assert any("令牌不足" in r for r in d.reasons)
        clock.advance(0.4)  # 回补 5*0.4=2 个令牌
        d2 = sched.admit(ResourcePlane.COLD, frozenset({17}), _GIB, 2.0, requester="b")
        assert d2.granted is True

    def test_rejection_does_not_consume_tokens(self) -> None:
        clock = _FakeClock()
        sched = _scheduler(clock=clock)
        d = sched.admit(ResourcePlane.COLD, frozenset({99}), _GIB, 5.0, requester="bad")
        assert d.granted is False  # 越界核拒绝，不消耗令牌
        assert sched.admit(ResourcePlane.COLD, frozenset({16}), _GIB, 5.0, requester="ok").granted


# ──────────────────────────────────────────────────────────────────────────────
# 非法输入（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestAdmitInvalid:
    def test_invalid_plane_raises(self) -> None:
        sched = _scheduler()
        with pytest.raises(ResourceSchedulerError):
            sched.admit("hot", frozenset({0}), _GIB, 1.0)  # type: ignore[arg-type]

    def test_invalid_cores_raise(self) -> None:
        sched = _scheduler()
        with pytest.raises(ResourceSchedulerError):
            sched.admit(ResourcePlane.HOT, frozenset(), _GIB, 1.0)
        with pytest.raises(ResourceSchedulerError):
            sched.admit(ResourcePlane.HOT, frozenset({-1}), _GIB, 1.0)

    def test_invalid_mem_raises(self) -> None:
        sched = _scheduler()
        with pytest.raises(ResourceSchedulerError):
            sched.admit(ResourcePlane.HOT, frozenset({0}), -1, 1.0)

    def test_invalid_qps_raises(self) -> None:
        sched = _scheduler()
        with pytest.raises(ResourceSchedulerError):
            sched.admit(ResourcePlane.HOT, frozenset({0}), _GIB, 0.0)
        with pytest.raises(ResourceSchedulerError):
            sched.admit(ResourcePlane.HOT, frozenset({0}), _GIB, -3.0)

    def test_duplicate_requester_raises(self) -> None:
        sched = _scheduler()
        sched.admit(ResourcePlane.HOT, frozenset({0}), _GIB, 1.0, requester="dup")
        with pytest.raises(ResourceSchedulerError):
            sched.admit(ResourcePlane.HOT, frozenset({1}), _GIB, 1.0, requester="dup")

    def test_executor_exception_raises_fail_closed(self) -> None:
        def _boom(req: ResourceRequest) -> None:
            raise RuntimeError("os call failed")

        sched = _scheduler(executor=_boom)
        with pytest.raises(ResourceSchedulerError):
            sched.admit(ResourcePlane.HOT, frozenset({0}), _GIB, 1.0, requester="a")


# ──────────────────────────────────────────────────────────────────────────────
# 查询与确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestQueryDeterminism:
    def test_plane_usage_view(self) -> None:
        sched = _scheduler()
        sched.admit(ResourcePlane.HOT, frozenset({2, 0}), 3 * _GIB, 10.0, requester="a")
        usage = sched.plane_usage(ResourcePlane.HOT)
        assert usage["cores_used"] == (0, 2)
        assert usage["cores_free"] == (1, 3)
        assert usage["mem_used_bytes"] == 3 * _GIB
        assert usage["mem_free_bytes"] == 5 * _GIB

    def test_plane_usage_unknown_plane_raises(self) -> None:
        sched = _scheduler()
        with pytest.raises(ResourceSchedulerError):
            sched.plane_usage("warm")  # type: ignore[arg-type]

    def test_same_inputs_same_outputs(self) -> None:
        def _run() -> tuple[bool, tuple[str, ...], tuple[tuple[int, ...], ...]]:
            sched = _scheduler(clock=_FakeClock(42.0))
            d1 = sched.admit(ResourcePlane.HOT, frozenset({0, 1}), 2 * _GIB, 50.0, requester="a")
            d2 = sched.admit(ResourcePlane.HOT, frozenset({1}), 7 * _GIB, 10.0, requester="b")
            usage = sched.plane_usage(ResourcePlane.HOT)
            return d1.granted, d2.reasons, (usage["cores_used"], usage["cores_free"])  # type: ignore[return-value]

        assert _run() == _run()
