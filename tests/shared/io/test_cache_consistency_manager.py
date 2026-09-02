# [BLUEPRINT] MOD-SHARED-005 | docs/03_modules/_domain_shared/cache_consistency_manager/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-SHARED-005 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.shared.io.test_cache_consistency_manager
# [TESTS] src/zephyr/shared/io/cache_consistency_manager.py
"""MOD-SHARED-005 单元测试：cache_consistency_manager 缓存一致性管理器。

蓝图验收（B13-04324/CAND-SHARED-003，A3数据架构）：
分层缓存注册（L1/L2/L3 词表）+ TTL/事件/版本戳三失效策略注册表 +
按数据类型写穿写回裁定 + 一致性巡检（源版本戳比对 + 不一致清单 + 告警回调）。
时钟/告警全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.shared.io.cache_consistency_manager",
    reason="cache_consistency_manager not importable",
)

from zephyr.shared.io.cache_consistency_manager import (  # noqa: E402
    CacheConsistencyError,
    CacheConsistencyManager,
    CacheTier,
    InconsistencyRecord,
    InvalidationStrategy,
    WritePolicy,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)


class _Clock:
    """可变注入时钟（测试替身）。"""

    def __init__(self, now: datetime.datetime = _T0) -> None:
        self.now = now

    def __call__(self) -> datetime.datetime:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += datetime.timedelta(seconds=seconds)


def _manager(clock: _Clock | None = None, alerts: list | None = None) -> CacheConsistencyManager:
    return CacheConsistencyManager(
        clock=clock or _Clock(),
        alert_sink=(lambda r: alerts.append(r)) if alerts is not None else None,
    )


def _ttl_entry(mgr: CacheConsistencyManager, key: str = "k1", ttl: float = 60.0) -> None:
    mgr.register_entry(
        key,
        data_type="bar",
        tiers=[CacheTier.L1_MEMORY, CacheTier.L2_REDIS],
        strategy=InvalidationStrategy.TTL,
        ttl_seconds=ttl,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 条目注册
# ──────────────────────────────────────────────────────────────────────────────


class TestRegisterEntry:
    def test_register_ok(self) -> None:
        mgr = _manager()
        _ttl_entry(mgr)
        assert mgr.keys() == ("k1",)

    def test_register_invalid_args_raise(self) -> None:
        mgr = _manager()
        with pytest.raises(CacheConsistencyError):
            mgr.register_entry(
                "", data_type="bar", tiers=[CacheTier.L1_MEMORY], strategy=InvalidationStrategy.TTL, ttl_seconds=60
            )
        with pytest.raises(CacheConsistencyError):
            mgr.register_entry(
                "k", data_type="", tiers=[CacheTier.L1_MEMORY], strategy=InvalidationStrategy.TTL, ttl_seconds=60
            )
        with pytest.raises(CacheConsistencyError):
            mgr.register_entry("k", data_type="bar", tiers=[], strategy=InvalidationStrategy.TTL, ttl_seconds=60)
        with pytest.raises(CacheConsistencyError):
            mgr.register_entry(
                "k",
                data_type="bar",
                tiers=["l4_gpu"],  # type: ignore[list-item]
                strategy=InvalidationStrategy.TTL,
                ttl_seconds=60,
            )
        with pytest.raises(CacheConsistencyError):
            mgr.register_entry("k", data_type="bar", tiers=[CacheTier.L1_MEMORY], strategy="forever")  # type: ignore[arg-type]

    def test_ttl_strategy_requires_positive_ttl(self) -> None:
        mgr = _manager()
        with pytest.raises(CacheConsistencyError):
            mgr.register_entry(
                "k", data_type="bar", tiers=[CacheTier.L1_MEMORY], strategy=InvalidationStrategy.TTL
            )  # 缺 ttl
        with pytest.raises(CacheConsistencyError):
            mgr.register_entry(
                "k", data_type="bar", tiers=[CacheTier.L1_MEMORY], strategy=InvalidationStrategy.TTL, ttl_seconds=0
            )

    def test_non_ttl_strategy_rejects_ttl(self) -> None:
        mgr = _manager()
        with pytest.raises(CacheConsistencyError):
            mgr.register_entry(
                "k", data_type="bar", tiers=[CacheTier.L1_MEMORY], strategy=InvalidationStrategy.EVENT, ttl_seconds=60
            )

    def test_duplicate_register_raises(self) -> None:
        mgr = _manager()
        _ttl_entry(mgr)
        with pytest.raises(CacheConsistencyError):
            _ttl_entry(mgr)


# ──────────────────────────────────────────────────────────────────────────────
# 写策略注册表
# ──────────────────────────────────────────────────────────────────────────────


class TestWritePolicyRegistry:
    def test_set_and_query(self) -> None:
        mgr = _manager()
        mgr.set_write_policy("bar", WritePolicy.WRITE_THROUGH)
        assert mgr.write_policy_for("bar") is WritePolicy.WRITE_THROUGH

    def test_query_unregistered_raises(self) -> None:
        with pytest.raises(CacheConsistencyError):
            _manager().write_policy_for("ghost")

    def test_set_invalid_args_raise(self) -> None:
        mgr = _manager()
        with pytest.raises(CacheConsistencyError):
            mgr.set_write_policy("", WritePolicy.WRITE_THROUGH)
        with pytest.raises(CacheConsistencyError):
            mgr.set_write_policy("bar", "write_around")  # type: ignore[arg-type]
        mgr.set_write_policy("bar", WritePolicy.WRITE_BACK)
        with pytest.raises(CacheConsistencyError):
            mgr.set_write_policy("bar", WritePolicy.WRITE_THROUGH)  # 重复注册


# ──────────────────────────────────────────────────────────────────────────────
# 写入（写穿/写回裁定 + 版本不变量）
# ──────────────────────────────────────────────────────────────────────────────


class TestWrite:
    def test_write_through_commits_immediately(self) -> None:
        mgr = _manager()
        mgr.set_write_policy("bar", WritePolicy.WRITE_THROUGH)
        _ttl_entry(mgr)
        mgr.write("k1", {"px": 10.5}, version=1)
        snap = mgr.snapshot("k1")
        assert snap.dirty is False
        assert snap.version == 1
        assert snap.written_at == _T0

    def test_write_back_marks_dirty_until_flush(self) -> None:
        mgr = _manager()
        mgr.set_write_policy("bar", WritePolicy.WRITE_BACK)
        _ttl_entry(mgr)
        mgr.write("k1", "v1", version=1)
        assert mgr.snapshot("k1").dirty is True
        assert mgr.flush("k1") is True
        assert mgr.snapshot("k1").dirty is False
        assert mgr.flush("k1") is False  # 幂等

    def test_write_invalid_args_raise(self) -> None:
        mgr = _manager()
        mgr.set_write_policy("bar", WritePolicy.WRITE_THROUGH)
        _ttl_entry(mgr)
        with pytest.raises(CacheConsistencyError):
            mgr.write("ghost", 1, version=1)  # 未知键
        with pytest.raises(CacheConsistencyError):
            mgr.write("k1", 1, version=-1)  # 负版本

    def test_write_without_policy_fail_closed(self) -> None:
        mgr = _manager()
        _ttl_entry(mgr)  # data_type=bar 未注册写策略
        with pytest.raises(CacheConsistencyError):
            mgr.write("k1", 1, version=1)

    def test_version_rollback_raises(self) -> None:
        mgr = _manager()
        mgr.set_write_policy("bar", WritePolicy.WRITE_THROUGH)
        _ttl_entry(mgr)
        mgr.write("k1", 1, version=2)
        with pytest.raises(CacheConsistencyError):
            mgr.write("k1", 1, version=2)  # 同版本=回退
        with pytest.raises(CacheConsistencyError):
            mgr.write("k1", 1, version=1)


# ──────────────────────────────────────────────────────────────────────────────
# 失效策略（TTL / EVENT / VERSION）
# ──────────────────────────────────────────────────────────────────────────────


class TestInvalidation:
    def test_ttl_valid_within_window_expires_after(self) -> None:
        clock = _Clock()
        mgr = _manager(clock)
        mgr.set_write_policy("bar", WritePolicy.WRITE_THROUGH)
        _ttl_entry(mgr, ttl=60.0)
        mgr.write("k1", 1, version=1)
        clock.advance(59.0)
        assert mgr.is_valid("k1") is True
        clock.advance(2.0)  # 61s 超窗
        assert mgr.is_valid("k1") is False
        assert mgr.read("k1") is None  # 未命中语义

    def test_event_invalidation(self) -> None:
        mgr = _manager()
        mgr.set_write_policy("bar", WritePolicy.WRITE_THROUGH)
        mgr.register_entry("k1", data_type="bar", tiers=[CacheTier.L1_MEMORY], strategy=InvalidationStrategy.EVENT)
        mgr.write("k1", 1, version=1)
        assert mgr.is_valid("k1") is True
        mgr.invalidate("k1")
        assert mgr.is_valid("k1") is False
        mgr.write("k1", 2, version=2)  # 重写复位失效标记
        assert mgr.is_valid("k1") is True

    def test_invalidate_strategy_mismatch_raises(self) -> None:
        mgr = _manager()
        mgr.set_write_policy("bar", WritePolicy.WRITE_THROUGH)
        _ttl_entry(mgr)  # TTL 策略
        with pytest.raises(CacheConsistencyError):
            mgr.invalidate("k1")
        with pytest.raises(CacheConsistencyError):
            mgr.invalidate("ghost")

    def test_version_strategy(self) -> None:
        mgr = _manager()
        mgr.set_write_policy("bar", WritePolicy.WRITE_THROUGH)
        mgr.register_entry("k1", data_type="bar", tiers=[CacheTier.L3_DISK], strategy=InvalidationStrategy.VERSION)
        mgr.write("k1", 1, version=7)
        assert mgr.is_valid("k1", source_version=7) is True
        assert mgr.is_valid("k1", source_version=8) is False
        with pytest.raises(CacheConsistencyError):
            mgr.is_valid("k1")  # 缺源版本戳

    def test_never_written_is_invalid(self) -> None:
        mgr = _manager()
        _ttl_entry(mgr)
        assert mgr.is_valid("k1") is False
        with pytest.raises(CacheConsistencyError):
            mgr.snapshot("k1")  # 无快照


# ──────────────────────────────────────────────────────────────────────────────
# 一致性巡检
# ──────────────────────────────────────────────────────────────────────────────


class TestPatrol:
    def _three_keys(self, mgr: CacheConsistencyManager) -> None:
        mgr.set_write_policy("bar", WritePolicy.WRITE_THROUGH)
        for key in ("a", "b", "c"):
            mgr.register_entry(key, data_type="bar", tiers=[CacheTier.L1_MEMORY], strategy=InvalidationStrategy.VERSION)

    def test_consistent_patrol_empty(self) -> None:
        mgr = _manager()
        self._three_keys(mgr)
        mgr.write("a", 1, version=1)
        mgr.write("b", 1, version=2)
        assert mgr.patrol({"a": 1, "b": 2}) == ()

    def test_mismatch_records_with_alerts(self) -> None:
        alerts: list[InconsistencyRecord] = []
        mgr = _manager(alerts=alerts)
        self._three_keys(mgr)
        mgr.write("a", 1, version=1)
        mgr.write("b", 1, version=2)
        records = mgr.patrol({"a": 1, "b": 3})  # b 源侧已 v3
        assert len(records) == 1
        assert records[0].key == "b"
        assert records[0].cached_version == 2
        assert records[0].source_version == 3
        assert alerts == list(records)  # 逐条告警

    def test_missing_source_stamp_recorded(self) -> None:
        mgr = _manager()
        self._three_keys(mgr)
        mgr.write("a", 1, version=1)
        records = mgr.patrol({})  # 源侧缺版本戳
        assert len(records) == 1
        assert records[0].source_version is None

    def test_patrol_sample_subset_sorted(self) -> None:
        mgr = _manager()
        self._three_keys(mgr)
        mgr.write("a", 1, version=1)
        mgr.write("b", 1, version=1)
        mgr.write("c", 1, version=1)
        records = mgr.patrol({"a": 9, "b": 1, "c": 9}, sample_keys=["c", "a"])
        assert [r.key for r in records] == ["a", "c"]  # 确定性排序

    def test_patrol_unknown_sample_key_raises(self) -> None:
        mgr = _manager()
        self._three_keys(mgr)
        with pytest.raises(CacheConsistencyError):
            mgr.patrol({}, sample_keys=["ghost"])


# ──────────────────────────────────────────────────────────────────────────────
# 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_inputs_same_outputs(self) -> None:
        def _run() -> tuple:
            clock = _Clock()
            alerts: list[InconsistencyRecord] = []
            mgr = _manager(clock, alerts)
            mgr.set_write_policy("bar", WritePolicy.WRITE_BACK)
            mgr.register_entry(
                "k1", data_type="bar", tiers=[CacheTier.L1_MEMORY], strategy=InvalidationStrategy.TTL, ttl_seconds=30
            )
            mgr.register_entry("k2", data_type="bar", tiers=[CacheTier.L2_REDIS], strategy=InvalidationStrategy.VERSION)
            mgr.write("k1", "x", version=1)
            mgr.write("k2", "y", version=3)
            clock.advance(10.0)
            valid = mgr.is_valid("k1")
            dirty = mgr.snapshot("k1").dirty
            records = mgr.patrol({"k2": 4})
            return (valid, dirty, records, tuple(alerts), mgr.keys())

        assert _run() == _run()
