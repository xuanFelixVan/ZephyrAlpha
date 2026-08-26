# [BLUEPRINT] MOD-DATENG-005 | docs/03_modules/_domain_data_eng/gpu_resource_manager/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-DATENG-005 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.data_eng.test_gpu_resource_manager
# [TESTS] src/zephyr/data_eng/gpu_resource_manager.py
"""MOD-DATENG-005 单元测试：gpu_resource_manager GPU资源管理器。

蓝图验收（B5-07239/CAND-DATENG-008，B5 R-100）：
显存分区预算（训练/推理配额）+ 时段优先调度（盘中推理/盘后训练，注入时
段表）+ 显存水位监控（注入 nvml_probe）+ OOM 降级 CPU 裁决 + telemetry。
probe/时钟/回调全内存替身，不触设备。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.data_eng.gpu_resource_manager",
    reason="gpu_resource_manager not importable",
)

from zephyr.data_eng.gpu_resource_manager import (  # noqa: E402
    GpuResourceError,
    GpuResourceManager,
    GpuSample,
    TimeWindowRule,
    WorkloadKind,
)

# 盘中 09:30（570min）；盘后 15:00（900min）
_T_OPEN = datetime.datetime(2026, 8, 25, 9, 30, 0)
_T_CLOSE = datetime.datetime(2026, 8, 25, 15, 0, 0)

_MARKET_RULE = TimeWindowRule(start_minute=570, end_minute=900, preferred=WorkloadKind.INFERENCE)


def _mgr(
    *,
    now: datetime.datetime = _T_CLOSE,
    probe=None,
    telemetry: list | None = None,
    alerts: list | None = None,
    total: int = 10000,
) -> GpuResourceManager:
    mgr = GpuResourceManager(
        total_memory_mb=total,
        clock=lambda: now,
        nvml_probe=probe,
        telemetry_sink=(lambda p: telemetry.append(p)) if telemetry is not None else None,
        alert_sink=(lambda m: alerts.append(m)) if alerts is not None else None,
    )
    mgr.register_quota(WorkloadKind.TRAINING, 6000)
    mgr.register_quota(WorkloadKind.INFERENCE, 4000)
    return mgr


# ── 构造/注册 Fail-Closed ─────────────────────────────────────────────────


def test_init_rejects_bad_total_and_watermark():
    with pytest.raises(GpuResourceError, match="total_memory_mb"):
        GpuResourceManager(total_memory_mb=0)
    with pytest.raises(GpuResourceError, match="oom_watermark"):
        GpuResourceManager(total_memory_mb=1000, oom_watermark=1.5)


def test_register_quota_rejects_bad_args():
    mgr = GpuResourceManager(total_memory_mb=1000)
    with pytest.raises(GpuResourceError, match="非法负载类型"):
        mgr.register_quota("training", 100)  # type: ignore[arg-type]
    with pytest.raises(GpuResourceError, match="budget_mb"):
        mgr.register_quota(WorkloadKind.TRAINING, 0)
    with pytest.raises(GpuResourceError, match="budget_mb"):
        mgr.register_quota(WorkloadKind.TRAINING, 2000)


def test_set_schedule_rejects_invalid_and_overlapping_rules():
    mgr = _mgr()
    with pytest.raises(GpuResourceError, match="时段窗口非法"):
        mgr.set_schedule([TimeWindowRule(900, 570, WorkloadKind.TRAINING)])
    with pytest.raises(GpuResourceError, match="时段窗口非法"):
        mgr.set_schedule([TimeWindowRule(0, 1441, WorkloadKind.TRAINING)])
    with pytest.raises(GpuResourceError, match="重叠"):
        mgr.set_schedule([
            TimeWindowRule(570, 900, WorkloadKind.INFERENCE),
            TimeWindowRule(800, 1000, WorkloadKind.TRAINING),
        ])


# ── acquire Fail-Closed ───────────────────────────────────────────────────


def test_acquire_rejects_unregistered_kind_and_bad_request():
    mgr = GpuResourceManager(total_memory_mb=1000, clock=lambda: _T_CLOSE)
    with pytest.raises(GpuResourceError, match="未注册配额"):
        mgr.acquire("w1", WorkloadKind.TRAINING, 100)
    mgr.register_quota(WorkloadKind.TRAINING, 500)
    with pytest.raises(GpuResourceError, match="workload_id 为空"):
        mgr.acquire("", WorkloadKind.TRAINING, 100)
    with pytest.raises(GpuResourceError, match="request_mb"):
        mgr.acquire("w1", WorkloadKind.TRAINING, 0)


def test_acquire_rejects_duplicate_workload():
    mgr = _mgr()
    mgr.acquire("w1", WorkloadKind.TRAINING, 100)
    with pytest.raises(GpuResourceError, match="重复分配"):
        mgr.acquire("w1", WorkloadKind.INFERENCE, 100)


# ── 授予与配额降级 ────────────────────────────────────────────────────────


def test_grant_within_quota_records_and_telemetry():
    telemetry: list = []
    mgr = _mgr(telemetry=telemetry)
    v = mgr.acquire("w1", WorkloadKind.TRAINING, 2000)
    assert v.on_gpu is True and v.degraded_to_cpu is False
    assert v.granted_mb == 2000 and v.reason == "GRANTED"
    assert telemetry == [v]


def test_quota_exceeded_degrades_to_cpu_with_alert():
    alerts: list = []
    mgr = _mgr(alerts=alerts)
    assert mgr.acquire("w1", WorkloadKind.INFERENCE, 3000).on_gpu is True
    v2 = mgr.acquire("w2", WorkloadKind.INFERENCE, 2000)  # 3000+2000>4000
    assert v2.on_gpu is False and v2.degraded_to_cpu is True
    assert "QUOTA_EXCEEDED" in v2.reason
    assert any("降级CPU" in m for m in alerts)


def test_release_frees_quota_and_unknown_release_rejected():
    mgr = _mgr()
    mgr.acquire("w1", WorkloadKind.INFERENCE, 3000)
    mgr.release("w1")
    assert mgr.acquire("w2", WorkloadKind.INFERENCE, 3000).on_gpu is True
    with pytest.raises(GpuResourceError, match="未知 workload"):
        mgr.release("w1")


# ── 时段优先调度 ──────────────────────────────────────────────────────────


def test_market_hours_training_degraded_inference_granted():
    mgr = _mgr(now=_T_OPEN)
    mgr.set_schedule([_MARKET_RULE])
    vt = mgr.acquire("t1", WorkloadKind.TRAINING, 1000)
    assert vt.degraded_to_cpu is True
    assert "TIME_WINDOW_PRIORITY" in vt.reason
    vi = mgr.acquire("i1", WorkloadKind.INFERENCE, 1000)
    assert vi.on_gpu is True


def test_after_market_training_granted():
    mgr = _mgr(now=_T_CLOSE)  # 15:00 恰在窗口外（右开区间）
    mgr.set_schedule([_MARKET_RULE])
    assert mgr.acquire("t1", WorkloadKind.TRAINING, 1000).on_gpu is True


def test_no_schedule_no_time_window_restriction():
    mgr = _mgr(now=_T_OPEN)
    assert mgr.acquire("t1", WorkloadKind.TRAINING, 1000).on_gpu is True


# ── OOM 水位裁决与监控 ────────────────────────────────────────────────────


def test_oom_guard_degrades_when_probe_near_watermark():
    alerts: list = []
    mgr = _mgr(probe=lambda: GpuSample(used_mb=8800, total_mb=10000), alerts=alerts)
    v = mgr.acquire("w1", WorkloadKind.TRAINING, 500)  # 8800+500>9000
    assert v.degraded_to_cpu is True
    assert "OOM_GUARD" in v.reason
    assert alerts


def test_oom_guard_passes_when_probe_low():
    mgr = _mgr(probe=lambda: GpuSample(used_mb=1000, total_mb=10000))
    assert mgr.acquire("w1", WorkloadKind.TRAINING, 500).on_gpu is True


def test_acquire_skips_probe_check_when_not_injected():
    mgr = _mgr()
    assert mgr.acquire("w1", WorkloadKind.TRAINING, 5500).on_gpu is True


def test_check_watermark_alerts_above_threshold():
    telemetry: list = []
    alerts: list = []
    mgr = _mgr(
        probe=lambda: GpuSample(used_mb=9500, total_mb=10000),
        telemetry=telemetry,
        alerts=alerts,
    )
    sample = mgr.check_watermark()
    assert sample.used_mb == 9500
    assert telemetry == [sample]
    assert any("水位告警" in m for m in alerts)


def test_check_watermark_requires_probe_and_valid_sample():
    mgr = _mgr()
    with pytest.raises(GpuResourceError, match="nvml_probe 未注入"):
        mgr.check_watermark()
    mgr2 = _mgr(probe=lambda: GpuSample(used_mb=-1, total_mb=10000))
    with pytest.raises(GpuResourceError, match="采样非法"):
        mgr2.check_watermark()


# ── 状态快照与确定性 ──────────────────────────────────────────────────────


def test_status_snapshot():
    mgr = _mgr()
    mgr.set_schedule([_MARKET_RULE])
    mgr.acquire("w1", WorkloadKind.TRAINING, 2000)
    mgr.acquire("w2", WorkloadKind.INFERENCE, 1000)
    s = mgr.status()
    assert s["total_memory_mb"] == 10000
    assert s["quotas_mb"] == {"inference": 4000, "training": 6000}
    assert s["used_by_kind_mb"] == {"inference": 1000, "training": 2000}
    assert s["allocations"] == 2
    assert s["schedule_rules"] == 1


def test_same_input_same_output():
    def _run():
        mgr = _mgr(now=_T_OPEN)
        mgr.set_schedule([_MARKET_RULE])
        return (
            mgr.acquire("t1", WorkloadKind.TRAINING, 1000),
            mgr.acquire("i1", WorkloadKind.INFERENCE, 1000),
            mgr.acquire("i2", WorkloadKind.INFERENCE, 3500),
        )

    assert _run() == _run()
