# [BLUEPRINT] MOD-L00-004 | tests/zephyr/data/test_storage_tiering.py
# [MODULE] tests.zephyr.data.test_storage_tiering
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.storage_tiering
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L00-004 | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""StorageTiering 单元测试——冷热分层TTL迁移/分区/UFL事实层/双副本/恢复演练（CAND-DAT-006 / B1-00584）。

覆盖：
    1. 分区策略：日线按年、分钟按月
    2. 层级判定：按数据年龄 classify 热/温/冷
    3. TTL 迁移闭环：热→温（Redis→CH）、温→冷（CH→Parquet 分区归档）
    4. UFL 追加式事实层：is_deterministic=True 方可写入，改/删一律拒绝
    5. D/E 双副本一致性校验：缺文件/哈希不一致检出
    6. RTO/RPO 分级演练：L1~L6 达标判定
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest

from zephyr.data.storage_tiering import (
    RECOVERY_LEVELS,
    StorageTiering,
    Tier,
    TierPolicy,
    UFLFact,
    UFLFactLayer,
    UFLMutationError,
    check_replica_consistency,
    partition_key,
)

UTC = timezone.utc
NOW = datetime(2026, 8, 25, 12, 0, 0, tzinfo=UTC)


# ── 1. 分区策略 ──


class TestPartitionKey:
    def test_daily_partition_by_year(self):
        assert partition_key("daily", date(2026, 8, 25)) == "year=2026"

    def test_minute_partition_by_month(self):
        assert partition_key("minute", date(2026, 8, 25)) == "year=2026/month=08"

    def test_unknown_freq_raises(self):
        with pytest.raises(ValueError):
            partition_key("tick", date(2026, 8, 25))


# ── 2/3. 层级判定与 TTL 迁移 ──


def _policy() -> TierPolicy:
    return TierPolicy(hot_ttl_seconds=60, warm_retention_days=30)


class TestClassify:
    def test_fresh_is_hot(self):
        st = StorageTiering(policy=_policy())
        ts = NOW - timedelta(seconds=10)
        assert st.classify(ts, now=NOW) is Tier.HOT

    def test_medium_is_warm(self):
        st = StorageTiering(policy=_policy())
        ts = NOW - timedelta(days=3)
        assert st.classify(ts, now=NOW) is Tier.WARM

    def test_old_is_cold(self):
        st = StorageTiering(policy=_policy())
        ts = NOW - timedelta(days=90)
        assert st.classify(ts, now=NOW) is Tier.COLD


class _FakeRedis:
    """最小 Redis 假后端：data={key: (ts, value)}。"""

    def __init__(self, data):
        self.data = dict(data)
        self.deleted = []

    def keys(self):
        return list(self.data)

    def get(self, key):
        return self.data.get(key)

    def delete(self, key):
        self.deleted.append(key)
        self.data.pop(key, None)


class TestMigrateHotToWarm:
    def test_expired_hot_key_migrated_to_warm(self):
        st = StorageTiering(policy=_policy())
        old_ts = NOW - timedelta(seconds=120)
        fresh_ts = NOW - timedelta(seconds=5)
        redis = _FakeRedis(
            {
                "bar:000001.SZ": (old_ts, "row-old"),
                "bar:600000.SH": (fresh_ts, "row-fresh"),
            }
        )
        warm_writes = []
        report = st.migrate_hot_to_warm(
            redis_client=redis,
            warm_insert=lambda key, ts, value: warm_writes.append((key, ts, value)),
            now=NOW,
        )
        assert report.migrated == 1
        assert report.skipped == 1
        assert warm_writes == [("bar:000001.SZ", old_ts, "row-old")]
        assert redis.deleted == ["bar:000001.SZ"]

    def test_empty_hot_layer(self):
        st = StorageTiering(policy=_policy())
        redis = _FakeRedis({})
        report = st.migrate_hot_to_warm(redis_client=redis, warm_insert=lambda *a: None, now=NOW)
        assert report.migrated == 0 and report.skipped == 0


class TestMigrateWarmToCold:
    def test_old_partition_archived_to_parquet_path(self):
        st = StorageTiering(policy=_policy())
        rows = [("000001.SZ", date(2026, 1, 5), 1.0)]
        parquet_writes = []
        dropped = []
        report = st.migrate_warm_to_cold(
            dataset="kline_daily",
            freq="daily",
            partition_date=date(2026, 1, 5),
            rows=rows,
            parquet_write=lambda path, r: parquet_writes.append((path, r)),
            warm_drop=lambda ds, pkey: dropped.append((ds, pkey)),
            now=NOW,
        )
        assert report.migrated == 1
        assert parquet_writes[0][0].endswith("kline_daily/year=2026")
        assert parquet_writes[0][1] == rows
        assert dropped == [("kline_daily", "year=2026")]

    def test_fresh_partition_not_archived(self):
        st = StorageTiering(policy=_policy())
        report = st.migrate_warm_to_cold(
            dataset="kline_daily",
            freq="daily",
            partition_date=date(2026, 8, 20),
            rows=[],
            parquet_write=lambda *a: None,
            warm_drop=lambda *a: None,
            now=NOW,
        )
        assert report.migrated == 0 and report.skipped == 1


# ── 4. UFL 追加式事实层 ──


def _fact(key: str = "bar:000001.SZ:2026-08-25", value: str = "v1") -> UFLFact:
    return UFLFact(key=key, value=value, ts=NOW, is_deterministic=True)


class TestUFLFactLayer:
    def test_append_deterministic_fact(self):
        layer = UFLFactLayer()
        layer.append(_fact())
        assert layer.get("bar:000001.SZ:2026-08-25") == "v1"

    def test_non_deterministic_rejected(self):
        layer = UFLFactLayer()
        bad = UFLFact(key="k", value="v", ts=NOW, is_deterministic=False)
        with pytest.raises(UFLMutationError):
            layer.append(bad)

    def test_same_fact_idempotent(self):
        layer = UFLFactLayer()
        layer.append(_fact())
        layer.append(_fact())  # 同 key 同 value → 幂等放行
        assert layer.count == 1

    def test_conflicting_value_rejected(self):
        layer = UFLFactLayer()
        layer.append(_fact())
        with pytest.raises(UFLMutationError):
            layer.append(_fact(value="v2"))

    def test_update_delete_forbidden(self):
        layer = UFLFactLayer()
        layer.append(_fact())
        with pytest.raises(UFLMutationError):
            layer.update("bar:000001.SZ:2026-08-25", "v9")
        with pytest.raises(UFLMutationError):
            layer.delete("bar:000001.SZ:2026-08-25")


# ── 5. D/E 双副本一致性校验 ──


class TestReplicaConsistency:
    def test_identical_trees_pass(self, tmp_path: Path):
        d = tmp_path / "d"
        e = tmp_path / "e"
        for root in (d, e):
            (root / "a").mkdir(parents=True)
            (root / "a" / "f1.parquet").write_bytes(b"same-bytes")
        report = check_replica_consistency(d, e)
        assert report.consistent is True
        assert report.matched == 1

    def test_missing_and_hash_mismatch_detected(self, tmp_path: Path):
        d = tmp_path / "d"
        e = tmp_path / "e"
        d.mkdir()
        e.mkdir()
        (d / "f1.parquet").write_bytes(b"v1")
        (e / "f1.parquet").write_bytes(b"v2")
        (d / "f2.parquet").write_bytes(b"only-on-d")
        report = check_replica_consistency(d, e)
        assert report.consistent is False
        assert "f2.parquet" in report.missing_in_replica
        assert "f1.parquet" in report.hash_mismatch


# ── 6. RTO/RPO 分级恢复演练 ──


class TestRecoveryDrill:
    def test_levels_cover_l1_to_l6(self):
        assert sorted(RECOVERY_LEVELS) == ["L1", "L2", "L3", "L4", "L5", "L6"]

    def test_drill_pass_within_targets(self):
        st = StorageTiering(policy=_policy())
        result = st.evaluate_drill("L1", observed_rto_minutes=3.0, observed_rpo_seconds=0.5)
        assert result.passed is True

    def test_drill_fail_when_rto_exceeded(self):
        st = StorageTiering(policy=_policy())
        result = st.evaluate_drill("L1", observed_rto_minutes=10.0, observed_rpo_seconds=0.5)
        assert result.passed is False

    def test_drill_fail_when_rpo_exceeded(self):
        st = StorageTiering(policy=_policy())
        result = st.evaluate_drill("L6", observed_rto_minutes=60.0, observed_rpo_seconds=90000.0)
        assert result.passed is False

    def test_unknown_level_raises(self):
        st = StorageTiering(policy=_policy())
        with pytest.raises(ValueError):
            st.evaluate_drill("L9", observed_rto_minutes=1.0, observed_rpo_seconds=1.0)
