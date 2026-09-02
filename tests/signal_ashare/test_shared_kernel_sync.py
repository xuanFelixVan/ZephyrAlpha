# [BLUEPRINT] MOD-SIG-133 | docs/03_modules/_domain_signal/shared_kernel_sync/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SIG-133 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.signal_ashare.test_shared_kernel_sync
# [TESTS] src/zephyr/signal_ashare/shared_kernel_sync.py
"""MOD-SIG-133 单元测试：shared_kernel_sync 策略共享内核同步器。

蓝图验收（B14-04730/CAND-TESTB-059，A9 D-SIGNAL-101）：
公共参数/市场状态/特征缓存三命名空间单一真源注册表 +
版本广播（写即版本递增+变更事件经注入bus发布）+
一致性校验（读侧版本戳比对，漂移清单+告警回调）。
bus/告警全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.signal_ashare.shared_kernel_sync",
    reason="shared_kernel_sync not importable",
)

from zephyr.signal_ashare.shared_kernel_sync import (  # noqa: E402
    KernelChangeEvent,
    KernelDrift,
    KernelNamespace,
    ReaderStamp,
    SharedKernelError,
    SharedKernelSync,
    VersionedValue,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)

NS = KernelNamespace


def _sync(events: list | None = None, alerts: list | None = None) -> SharedKernelSync:
    return SharedKernelSync(
        bus=(lambda e: events.append(e)) if events is not None else None,
        clock=lambda: _T0,
        alert_sink=(lambda d: alerts.append(d)) if alerts is not None else None,
    )


# ----------------------------------------------------------------------
# 写 / 版本递增 / 事件发布
# ----------------------------------------------------------------------
def test_write_first_version_is_one() -> None:
    sk = _sync()
    v = sk.write(NS.COMMON_PARAMS, "threshold", 0.5)
    assert isinstance(v, VersionedValue)
    assert v.version == 1
    assert v.value == 0.5
    assert v.updated_at == _T0


def test_write_increments_version() -> None:
    sk = _sync()
    sk.write(NS.MARKET_STATE, "regime", "trend")
    v = sk.write(NS.MARKET_STATE, "regime", "range")
    assert v.version == 2
    assert sk.version_of(NS.MARKET_STATE, "regime") == 2


def test_write_publishes_event_per_write() -> None:
    events: list = []
    sk = _sync(events=events)
    sk.write(NS.FEATURE_CACHE, "f1", [1.0])
    sk.write(NS.FEATURE_CACHE, "f1", [2.0])
    assert len(events) == 2
    assert all(isinstance(e, KernelChangeEvent) for e in events)
    assert [e.version for e in events] == [1, 2]
    assert events[0].namespace == NS.FEATURE_CACHE
    assert events[0].changed_at == _T0


def test_write_works_without_bus() -> None:
    sk = SharedKernelSync(clock=lambda: _T0)
    v = sk.write(NS.COMMON_PARAMS, "k", 1)
    assert v.version == 1


def test_bus_with_publish_method() -> None:
    class _Bus:
        def __init__(self) -> None:
            self.events: list = []

        def publish(self, event) -> None:
            self.events.append(event)

    bus = _Bus()
    sk = SharedKernelSync(bus=bus, clock=lambda: _T0)
    sk.write(NS.COMMON_PARAMS, "k", 1)
    assert len(bus.events) == 1


def test_bus_not_callable_rejected() -> None:
    with pytest.raises(SharedKernelError):
        SharedKernelSync(bus=object(), clock=lambda: _T0)


# ----------------------------------------------------------------------
# 命名空间词表闭合 / 隔离
# ----------------------------------------------------------------------
def test_namespace_string_coercion() -> None:
    sk = _sync()
    sk.write("common_params", "k", 7)
    assert sk.read(NS.COMMON_PARAMS, "k").value == 7


def test_invalid_namespace_rejected() -> None:
    sk = _sync()
    with pytest.raises(SharedKernelError):
        sk.write("secret_ns", "k", 1)
    with pytest.raises(SharedKernelError):
        sk.read("secret_ns", "k")


def test_empty_key_rejected() -> None:
    sk = _sync()
    with pytest.raises(SharedKernelError):
        sk.write(NS.COMMON_PARAMS, "  ", 1)
    with pytest.raises(SharedKernelError):
        sk.read(NS.COMMON_PARAMS, "")


def test_namespaces_isolated_independent_versions() -> None:
    sk = _sync()
    sk.write(NS.COMMON_PARAMS, "k", "a")
    sk.write(NS.MARKET_STATE, "k", "b")
    sk.write(NS.COMMON_PARAMS, "k", "c")
    assert sk.version_of(NS.COMMON_PARAMS, "k") == 2
    assert sk.version_of(NS.MARKET_STATE, "k") == 1
    assert sk.read(NS.MARKET_STATE, "k").value == "b"


# ----------------------------------------------------------------------
# 读侧
# ----------------------------------------------------------------------
def test_read_unknown_key_rejected() -> None:
    sk = _sync()
    with pytest.raises(SharedKernelError):
        sk.read(NS.COMMON_PARAMS, "ghost")


def test_keys_sorted() -> None:
    sk = _sync()
    sk.write(NS.FEATURE_CACHE, "z", 1)
    sk.write(NS.FEATURE_CACHE, "a", 2)
    sk.write(NS.FEATURE_CACHE, "m", 3)
    assert sk.keys(NS.FEATURE_CACHE) == ("a", "m", "z")


def test_snapshot_versions_covers_all_namespaces() -> None:
    sk = _sync()
    sk.write(NS.COMMON_PARAMS, "p", 1)
    sk.write(NS.MARKET_STATE, "s", 2)
    snap = sk.snapshot_versions()
    assert snap[(NS.COMMON_PARAMS, "p")] == 1
    assert snap[(NS.MARKET_STATE, "s")] == 1


# ----------------------------------------------------------------------
# 一致性校验 / 漂移告警
# ----------------------------------------------------------------------
def test_check_drift_clean_when_versions_match() -> None:
    alerts: list = []
    sk = _sync(alerts=alerts)
    sk.write(NS.COMMON_PARAMS, "k", 1)
    stamps = [ReaderStamp(namespace=NS.COMMON_PARAMS, key="k", version=1)]
    assert sk.check_drift("reader_a", stamps) == ()
    assert alerts == []


def test_check_drift_detects_stale_reader() -> None:
    alerts: list = []
    sk = _sync(alerts=alerts)
    sk.write(NS.COMMON_PARAMS, "k", 1)
    sk.write(NS.COMMON_PARAMS, "k", 2)
    stamps = [ReaderStamp(namespace="common_params", key="k", version=1)]
    drifts = sk.check_drift("reader_a", stamps)
    assert len(drifts) == 1
    d = drifts[0]
    assert isinstance(d, KernelDrift)
    assert d.reader_id == "reader_a"
    assert d.reader_version == 1
    assert d.current_version == 2
    assert d.at == _T0
    assert alerts == [d]


def test_check_drift_sorted_deterministic() -> None:
    sk = _sync()
    sk.write(NS.MARKET_STATE, "b", 1)
    sk.write(NS.COMMON_PARAMS, "a", 1)
    stamps = [
        ReaderStamp(namespace=NS.MARKET_STATE, key="b", version=9),
        ReaderStamp(namespace=NS.COMMON_PARAMS, key="a", version=9),
    ]
    drifts = sk.check_drift("r", stamps)
    assert [(d.namespace.value, d.key) for d in drifts] == [
        ("common_params", "a"),
        ("market_state", "b"),
    ]


def test_check_drift_empty_reader_rejected() -> None:
    sk = _sync()
    with pytest.raises(SharedKernelError):
        sk.check_drift(" ", [])


def test_check_drift_unknown_key_rejected() -> None:
    sk = _sync()
    stamps = [ReaderStamp(namespace=NS.COMMON_PARAMS, key="ghost", version=1)]
    with pytest.raises(SharedKernelError):
        sk.check_drift("r", stamps)


def test_check_drift_invalid_stamp_version_rejected() -> None:
    sk = _sync()
    sk.write(NS.COMMON_PARAMS, "k", 1)
    with pytest.raises(SharedKernelError):
        sk.check_drift("r", [ReaderStamp(namespace=NS.COMMON_PARAMS, key="k", version=0)])
    with pytest.raises(SharedKernelError):
        sk.check_drift("r", [ReaderStamp(namespace=NS.COMMON_PARAMS, key="k", version=True)])


def test_check_drift_invalid_namespace_rejected() -> None:
    sk = _sync()
    stamps = [ReaderStamp(namespace="nope", key="k", version=1)]
    with pytest.raises(SharedKernelError):
        sk.check_drift("r", stamps)


def test_check_drift_without_alert_sink_no_crash() -> None:
    sk = SharedKernelSync(clock=lambda: _T0)
    sk.write(NS.COMMON_PARAMS, "k", 1)
    sk.write(NS.COMMON_PARAMS, "k", 2)
    drifts = sk.check_drift("r", [ReaderStamp(namespace=NS.COMMON_PARAMS, key="k", version=1)])
    assert len(drifts) == 1


# ----------------------------------------------------------------------
# 确定性
# ----------------------------------------------------------------------
def test_determinism_same_ops_same_result() -> None:
    def run() -> tuple:
        sk = _sync()
        sk.write(NS.COMMON_PARAMS, "a", 1)
        sk.write(NS.MARKET_STATE, "b", 2)
        sk.write(NS.COMMON_PARAMS, "a", 3)
        stamps = [
            ReaderStamp(namespace=NS.COMMON_PARAMS, key="a", version=1),
            ReaderStamp(namespace=NS.MARKET_STATE, key="b", version=1),
        ]
        drifts = sk.check_drift("r", stamps)
        return (
            sk.version_of(NS.COMMON_PARAMS, "a"),
            tuple((d.namespace.value, d.key, d.reader_version, d.current_version) for d in drifts),
        )

    assert run() == run()
