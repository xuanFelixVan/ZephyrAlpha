# [A_test] module_id: SRC-TST-0075 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-233 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.asset_inventory.test_lifecycle
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Tests for MOD-INF-026 Lifecycle module — 蓝图 §2.6 + §22 附录 H 要求 >85% 覆盖."""

from datetime import UTC, datetime, timedelta

from zephyr.infrastructure.asset_inventory.lifecycle import Lifecycle
from zephyr.infrastructure.asset_inventory.models import (
    AssetStatus,
    AssetType,
    ClassifiedAsset,
    Priority,
    UnifiedAssetIndex,
)


def _asset(
    path: str,
    asset_type: AssetType = AssetType.MODULE,
    status: AssetStatus = AssetStatus.ACTIVE,
    priority: Priority = Priority.P2,
    mtime: datetime | None = None,
    registered_in: list[str] | None = None,
) -> ClassifiedAsset:
    return ClassifiedAsset(
        relative_path=path,
        asset_type=asset_type,
        status=status,
        priority=priority,
        size_bytes=100,
        mtime_utc=mtime or datetime.now(UTC),
        sha256="a" * 64,
        registered_in=registered_in or [],
    )


class TestTimeDecay:
    def test_active_to_stale(self) -> None:
        old_mtime = datetime.now(UTC) - timedelta(days=400)
        a = _asset("src/old_mod.py", asset_type=AssetType.MODULE, mtime=old_mtime, registered_in=["REG-MOD-001"])
        index = UnifiedAssetIndex(total_assets=1, assets=[a])

        lc = Lifecycle()
        events, new_index = lc.evaluate(index)
        assert len(events) == 1
        assert events[0].event_type == "TIME_DECAY"
        assert events[0].from_status == AssetStatus.ACTIVE
        assert events[0].to_status == AssetStatus.STALE

    def test_stale_to_deprecated(self) -> None:
        very_old = datetime.now(UTC) - timedelta(days=800)
        a = _asset(
            "src/very_old.py",
            asset_type=AssetType.MODULE,
            status=AssetStatus.STALE,
            mtime=very_old,
            registered_in=["REG-MOD-001"],
        )
        index = UnifiedAssetIndex(total_assets=1, assets=[a])

        lc = Lifecycle()
        events, new_index = lc.evaluate(index)
        assert len(events) == 1
        assert events[0].to_status == AssetStatus.DEPRECATED

    def test_recent_active_no_trigger(self) -> None:
        recent = datetime.now(UTC) - timedelta(days=10)
        a = _asset("src/recent.py", asset_type=AssetType.MODULE, mtime=recent, registered_in=["REG-MOD-001"])
        index = UnifiedAssetIndex(total_assets=1, assets=[a])

        lc = Lifecycle()
        events, new_index = lc.evaluate(index)
        assert len(events) == 0

    def test_deprecated_skips_time_decay(self) -> None:
        old_mtime = datetime.now(UTC) - timedelta(days=1000)
        a = _asset("src/dead.py", asset_type=AssetType.MODULE, status=AssetStatus.DEPRECATED, mtime=old_mtime)
        index = UnifiedAssetIndex(total_assets=1, assets=[a])

        lc = Lifecycle()
        events, new_index = lc.evaluate(index)
        time_decay_events = [e for e in events if e.event_type == "TIME_DECAY"]
        assert len(time_decay_events) == 0

    def test_data_type_shorter_decay(self) -> None:
        old_mtime = datetime.now(UTC) - timedelta(days=35)
        a = _asset("data/old.db", asset_type=AssetType.DATA, mtime=old_mtime, registered_in=["REG-DATA-001"])
        index = UnifiedAssetIndex(total_assets=1, assets=[a])

        lc = Lifecycle()
        events, new_index = lc.evaluate(index)
        assert len(events) == 1
        assert events[0].to_status == AssetStatus.STALE


class TestZeroRef:
    def test_unregistered_deprecates(self) -> None:
        a = _asset("src/orphan.py", asset_type=AssetType.MODULE, registered_in=[])
        index = UnifiedAssetIndex(total_assets=1, assets=[a])

        lc = Lifecycle()
        events, new_index = lc.evaluate(index)
        zero_ref = [e for e in events if e.event_type == "ZERO_REF"]
        assert len(zero_ref) == 1
        assert zero_ref[0].to_status == AssetStatus.DEPRECATED

    def test_p0_protected_from_zero_ref(self) -> None:
        a = _asset("src/critical.py", asset_type=AssetType.MODULE, priority=Priority.P0, registered_in=[])
        index = UnifiedAssetIndex(total_assets=1, assets=[a])

        lc = Lifecycle()
        events, new_index = lc.evaluate(index)
        zero_ref = [e for e in events if e.event_type == "ZERO_REF"]
        assert len(zero_ref) == 0

    def test_registered_asset_no_zero_ref(self) -> None:
        a = _asset("src/registered.py", asset_type=AssetType.MODULE, registered_in=["REG-MOD-001"])
        index = UnifiedAssetIndex(total_assets=1, assets=[a])

        lc = Lifecycle()
        events, new_index = lc.evaluate(index)
        zero_ref = [e for e in events if e.event_type == "ZERO_REF"]
        assert len(zero_ref) == 0

    def test_deprecated_skips_zero_ref(self) -> None:
        a = _asset("src/dead.py", status=AssetStatus.DEPRECATED, registered_in=[])
        index = UnifiedAssetIndex(total_assets=1, assets=[a])

        lc = Lifecycle()
        events, new_index = lc.evaluate(index)
        zero_ref = [e for e in events if e.event_type == "ZERO_REF"]
        assert len(zero_ref) == 0


class TestDirConvention:
    def test_deprecated_dir_triggers(self) -> None:
        a = _asset("src/_deprecated/old.py")
        index = UnifiedAssetIndex(total_assets=1, assets=[a])

        lc = Lifecycle()
        events, new_index = lc.evaluate(index)
        dir_events = [e for e in events if e.event_type == "DIR_CONVENTION"]
        assert len(dir_events) == 1
        assert dir_events[0].to_status == AssetStatus.DEPRECATED

    def test_archived_dir_triggers(self) -> None:
        a = _asset("src/_archived/dead.py")
        index = UnifiedAssetIndex(total_assets=1, assets=[a])

        lc = Lifecycle()
        events, new_index = lc.evaluate(index)
        dir_events = [e for e in events if e.event_type == "DIR_CONVENTION"]
        assert len(dir_events) == 1
        assert dir_events[0].to_status == AssetStatus.ARCHIVED

    def test_normal_dir_no_trigger(self) -> None:
        a = _asset("src/zephyr/active.py")
        index = UnifiedAssetIndex(total_assets=1, assets=[a])

        lc = Lifecycle()
        events, new_index = lc.evaluate(index)
        dir_events = [e for e in events if e.event_type == "DIR_CONVENTION"]
        assert len(dir_events) == 0


class TestEvaluate:
    def test_multiple_assets(self) -> None:
        active = _asset("src/a.py")
        stale = _asset("src/b.py", status=AssetStatus.STALE, mtime=datetime.now(UTC) - timedelta(days=800))
        deprecated_dir = _asset("src/_deprecated/c.py")
        index = UnifiedAssetIndex(total_assets=3, assets=[active, stale, deprecated_dir])

        lc = Lifecycle()
        events, new_index = lc.evaluate(index)
        assert len(events) >= 2

    def test_status_updated_in_output(self) -> None:
        old_mtime = datetime.now(UTC) - timedelta(days=400)
        a = _asset("src/old.py", mtime=old_mtime, registered_in=["REG-MOD-001"])
        index = UnifiedAssetIndex(total_assets=1, assets=[a])

        lc = Lifecycle()
        events, new_index = lc.evaluate(index)
        assert new_index.assets[0].status == AssetStatus.STALE

    def test_custom_decay_days(self) -> None:
        old_mtime = datetime.now(UTC) - timedelta(days=5)
        a = _asset("src/fast.py", asset_type=AssetType.DATA, mtime=old_mtime, registered_in=["REG-DATA-001"])
        index = UnifiedAssetIndex(total_assets=1, assets=[a])

        custom = {AssetType.DATA: 3}
        lc = Lifecycle(decay_days=custom)
        events, new_index = lc.evaluate(index)
        assert len(events) == 1

    def test_event_structure(self) -> None:
        old_mtime = datetime.now(UTC) - timedelta(days=400)
        a = _asset("src/old.py", mtime=old_mtime)
        index = UnifiedAssetIndex(total_assets=1, assets=[a])

        lc = Lifecycle()
        events, new_index = lc.evaluate(index)
        assert events[0].event_id.startswith("LCEVT-")
        assert events[0].asset_path == "src/old.py"
        assert events[0].auto_applied is True
