# [BLUEPRINT] MOD-DATENG-006 | docs/03_modules/_domain_data_eng/data_lake_manager/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-DATENG-006 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.data_eng.test_data_lake_manager
# [TESTS] src/zephyr/data_eng/data_lake_manager.py
"""MOD-DATENG-006 单元测试：data_lake_manager 数据湖分层管理器。

蓝图验收（B5-07240/CAND-DATENG-009，B5）：
热(CH近30天)/温(Parquet)/冷(ZSTD)三层策略注册表 + 迁移调度计划 + 保留
清理裁决 + 自动压缩归档编排；迁移/清理/压缩执行全注入内存替身，不触盘。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.data_eng.data_lake_manager",
    reason="data_lake_manager not importable",
)

from zephyr.data_eng.data_lake_manager import (  # noqa: E402
    DataLakeError,
    DataLakeManager,
    DatasetState,
    LakeTier,
    TierPolicy,
)

_T0 = datetime.datetime(2026, 8, 25, 15, 0, 0)
_DAY = datetime.timedelta(days=1)


def _mgr(
    *,
    migrate=None,
    purge=None,
    compress=None,
    alerts: list | None = None,
    clock=lambda: _T0,
) -> DataLakeManager:
    mgr = DataLakeManager(
        clock=clock,
        migrate_executor=migrate,
        purge_executor=purge,
        compress_executor=compress,
        alert_sink=(lambda m: alerts.append(m)) if alerts is not None else None,
    )
    mgr.register_tier_policy(TierPolicy(tier=LakeTier.HOT, max_age_days=30))
    mgr.register_tier_policy(TierPolicy(tier=LakeTier.WARM, max_age_days=180))
    mgr.register_tier_policy(TierPolicy(tier=LakeTier.COLD, max_age_days=730, codec="zstd"))
    return mgr


def _ds(name: str, tier: LakeTier, age_days: int, **kw) -> DatasetState:
    return DatasetState(name=name, tier=tier, oldest_data_at=_T0 - age_days * _DAY, **kw)


# ── 注册 Fail-Closed ──────────────────────────────────────────────────────


def test_register_tier_policy_rejects_bad_args():
    mgr = DataLakeManager(clock=lambda: _T0)
    with pytest.raises(DataLakeError, match="非法层"):
        mgr.register_tier_policy(TierPolicy(tier="hot", max_age_days=30))  # type: ignore[arg-type]
    with pytest.raises(DataLakeError, match="max_age_days"):
        mgr.register_tier_policy(TierPolicy(tier=LakeTier.HOT, max_age_days=0))
    with pytest.raises(DataLakeError, match="codec 为空"):
        mgr.register_tier_policy(TierPolicy(tier=LakeTier.HOT, max_age_days=30, codec=""))


def test_register_tier_policy_rejects_duplicate():
    mgr = _mgr()
    with pytest.raises(DataLakeError, match="重复注册"):
        mgr.register_tier_policy(TierPolicy(tier=LakeTier.HOT, max_age_days=7))


def test_register_dataset_rejects_bad_state():
    mgr = _mgr()
    with pytest.raises(DataLakeError, match="name 为空"):
        mgr.register_dataset(_ds("", LakeTier.HOT, 1))
    with pytest.raises(DataLakeError, match="size_bytes"):
        mgr.register_dataset(_ds("d1", LakeTier.HOT, 1, size_bytes=-1))
    with pytest.raises(DataLakeError, match="晚于当前时刻"):
        mgr.register_dataset(DatasetState(name="d2", tier=LakeTier.HOT, oldest_data_at=_T0 + _DAY))
    mgr.register_dataset(_ds("d1", LakeTier.HOT, 1))
    with pytest.raises(DataLakeError, match="重复注册"):
        mgr.register_dataset(_ds("d1", LakeTier.HOT, 2))


# ── 迁移调度计划与执行 ────────────────────────────────────────────────────


def test_plan_migrations_moves_only_overaged_one_step_down():
    mgr = _mgr()
    mgr.register_dataset(_ds("hot_old", LakeTier.HOT, 45))
    mgr.register_dataset(_ds("hot_fresh", LakeTier.HOT, 10))
    mgr.register_dataset(_ds("warm_old", LakeTier.WARM, 200))
    mgr.register_dataset(_ds("cold_rest", LakeTier.COLD, 400))
    tasks = mgr.plan_migrations()
    assert [(t.dataset, t.from_tier, t.to_tier) for t in tasks] == [
        ("hot_old", LakeTier.HOT, LakeTier.WARM),
        ("warm_old", LakeTier.WARM, LakeTier.COLD),
    ]
    assert all("超" in t.reason for t in tasks)
    assert all(t.planned_at == _T0 for t in tasks)


def test_plan_migrations_skips_tier_without_policy():
    mgr = DataLakeManager(clock=lambda: _T0)
    mgr.register_tier_policy(TierPolicy(tier=LakeTier.WARM, max_age_days=180))
    mgr.register_dataset(_ds("d1", LakeTier.HOT, 365))  # HOT 无策略 → 不裁决
    assert mgr.plan_migrations() == ()


def test_run_migrations_executes_and_advances_tier():
    moved: list = []
    mgr = _mgr(migrate=lambda t: moved.append(t))
    mgr.register_dataset(_ds("d1", LakeTier.HOT, 45))
    tasks = mgr.run_migrations()
    assert [t.dataset for t in tasks] == ["d1"]
    assert moved == list(tasks)
    assert mgr.dataset("d1").tier is LakeTier.WARM
    # 45d 龄在 WARM（上限 180d）内 → 不再迁移
    assert mgr.run_migrations() == ()


def test_run_migrations_requires_executor():
    mgr = _mgr()
    mgr.register_dataset(_ds("d1", LakeTier.HOT, 45))
    with pytest.raises(DataLakeError, match="migrate_executor 未注入"):
        mgr.run_migrations()


# ── 保留策略执行 ──────────────────────────────────────────────────────────


def test_plan_purge_only_overaged_cold_datasets():
    mgr = _mgr()
    mgr.register_dataset(_ds("cold_expired", LakeTier.COLD, 800))
    mgr.register_dataset(_ds("cold_kept", LakeTier.COLD, 365))
    mgr.register_dataset(_ds("warm_old", LakeTier.WARM, 800))  # 非 COLD 不清理
    decisions = mgr.plan_purge()
    assert [(d.dataset, d.tier) for d in decisions] == [("cold_expired", LakeTier.COLD)]
    assert "超保留期" in decisions[0].reason


def test_run_purge_executes_removes_and_alerts():
    purged: list = []
    alerts: list = []
    mgr = _mgr(purge=lambda d: purged.append(d), alerts=alerts)
    mgr.register_dataset(_ds("d1", LakeTier.COLD, 800))
    decisions = mgr.run_purge()
    assert [d.dataset for d in decisions] == ["d1"]
    assert purged == list(decisions)
    with pytest.raises(DataLakeError, match="未知数据集"):
        mgr.dataset("d1")
    assert any("清理" in m for m in alerts)


def test_run_purge_requires_executor():
    mgr = _mgr()
    mgr.register_dataset(_ds("d1", LakeTier.COLD, 800))
    with pytest.raises(DataLakeError, match="purge_executor 未注入"):
        mgr.run_purge()


# ── 自动压缩归档编排 ──────────────────────────────────────────────────────


def test_plan_compression_only_uncompressed_cold():
    mgr = _mgr()
    mgr.register_dataset(_ds("c1", LakeTier.COLD, 100))
    mgr.register_dataset(_ds("c2", LakeTier.COLD, 100, compressed=True))
    mgr.register_dataset(_ds("w1", LakeTier.WARM, 100))
    tasks = mgr.plan_compression()
    assert [(t.dataset, t.codec) for t in tasks] == [("c1", "zstd")]


def test_run_compression_executes_and_marks():
    done: list = []
    mgr = _mgr(compress=lambda t: done.append(t))
    mgr.register_dataset(_ds("c1", LakeTier.COLD, 100))
    tasks = mgr.run_compression()
    assert [t.dataset for t in tasks] == ["c1"]
    assert done == list(tasks)
    assert mgr.dataset("c1").compressed is True
    assert mgr.run_compression() == ()


def test_run_compression_requires_executor():
    mgr = _mgr()
    mgr.register_dataset(_ds("c1", LakeTier.COLD, 100))
    with pytest.raises(DataLakeError, match="compress_executor 未注入"):
        mgr.run_compression()


# ── 只读检索 / 生命周期编排 / 确定性 ──────────────────────────────────────


def test_list_datasets_sorted_and_tier_filtered():
    mgr = _mgr()
    mgr.register_dataset(_ds("b", LakeTier.WARM, 10))
    mgr.register_dataset(_ds("a", LakeTier.HOT, 10))
    mgr.register_dataset(_ds("c", LakeTier.WARM, 10))
    assert [d.name for d in mgr.list_datasets()] == ["a", "b", "c"]
    assert [d.name for d in mgr.list_datasets(tier=LakeTier.WARM)] == ["b", "c"]


def test_full_lifecycle_hot_to_purge():
    purged: list = []
    mgr = _mgr(migrate=lambda t: None, purge=lambda d: purged.append(d), compress=lambda t: None)
    mgr.register_dataset(_ds("bars", LakeTier.HOT, 40))
    mgr.run_migrations()
    assert mgr.dataset("bars").tier is LakeTier.WARM
    mgr._clock = lambda: _T0 + 200 * _DAY  # 推进 200 天：240d > WARM 180d
    mgr.run_migrations()
    assert mgr.dataset("bars").tier is LakeTier.COLD
    mgr.run_compression()
    assert mgr.dataset("bars").compressed is True
    mgr._clock = lambda: _T0 + 800 * _DAY  # 840d > COLD 保留 730d
    assert [d.dataset for d in mgr.run_purge()] == ["bars"]
    assert [d.dataset for d in purged] == ["bars"]
    assert mgr.list_datasets() == ()


def test_same_input_same_output():
    def _run():
        mgr = _mgr()
        mgr.register_dataset(_ds("b", LakeTier.HOT, 45))
        mgr.register_dataset(_ds("a", LakeTier.WARM, 200))
        mgr.register_dataset(_ds("c", LakeTier.COLD, 800))
        return mgr.plan_migrations(), mgr.plan_purge(), mgr.plan_compression()

    assert _run() == _run()
