# [A_test] module_id: MOD-GOV_lifecycle_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain_infrastructure_operations/asset_inventory/blueprint.md | §
# [MODULE] tests.test_lifecycle
# [INVARIANTS] Lifecycle.evaluate returns events and updated index; TIME_DECAY/ZERO_REF/DIR_CONVENTION rules fire
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] None
# [TESTS] tests/test_lifecycle_root.py
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from zephyr.infrastructure.asset_inventory.lifecycle import DEFAULT_DECAY_DAYS, Lifecycle, _generate_event_id
from zephyr.infrastructure.asset_inventory.models import (
    AssetLayer,
    AssetStatus,
    AssetType,
    ClassifiedAsset,
    Priority,
    UnifiedAssetIndex,
)


def _make_asset(**overrides) -> ClassifiedAsset:
    defaults = dict(
        relative_path="src/zephyr/test.py",
        asset_type=AssetType.MODULE,
        layer=AssetLayer.CROSS_LAYER,
        status=AssetStatus.ACTIVE,
        priority=Priority.P3,
        size_bytes=100,
        mtime_utc=datetime.now(UTC),
        sha256="abc123",
    )
    defaults.update(overrides)
    return ClassifiedAsset(**defaults)


def _make_index(assets=None, **overrides) -> UnifiedAssetIndex:
    if assets is None:
        assets = [_make_asset()]
    defaults = dict(
        total_assets=len(assets),
        assets=assets,
    )
    defaults.update(overrides)
    return UnifiedAssetIndex(**defaults)


class TestLifecycleInstantiation:
    def test_default(self):
        lc = Lifecycle()
        assert lc.decay_days == DEFAULT_DECAY_DAYS

    def test_custom_decay(self):
        custom = {AssetType.MODULE: 100}
        lc = Lifecycle(decay_days=custom)
        assert lc.decay_days[AssetType.MODULE] == 100

    def test_custom_root(self, tmp_path):
        lc = Lifecycle(root=tmp_path)
        assert lc.root == tmp_path


class TestLifecycleEvaluate:
    def test_no_events_for_fresh_assets(self):
        asset = _make_asset(mtime_utc=datetime.now(UTC), registered_in=["REG-001"])
        index = _make_index(assets=[asset])
        lc = Lifecycle()
        events, new_index = lc.evaluate(index)
        assert len(events) == 0

    def test_time_decay_active_to_stale(self):
        old_mtime = datetime.now(UTC) - timedelta(days=400)
        asset = _make_asset(mtime_utc=old_mtime, status=AssetStatus.ACTIVE)
        index = _make_index(assets=[asset])
        lc = Lifecycle()
        events, new_index = lc.evaluate(index)
        time_decay_events = [e for e in events if e.event_type == "TIME_DECAY"]
        assert len(time_decay_events) >= 1
        assert time_decay_events[0].to_status == AssetStatus.STALE

    def test_time_decay_stale_to_deprecated(self):
        very_old_mtime = datetime.now(UTC) - timedelta(days=800)
        asset = _make_asset(mtime_utc=very_old_mtime, status=AssetStatus.STALE)
        index = _make_index(assets=[asset])
        lc = Lifecycle()
        events, new_index = lc.evaluate(index)
        time_decay_events = [e for e in events if e.event_type == "TIME_DECAY"]
        assert len(time_decay_events) >= 1
        assert time_decay_events[0].to_status == AssetStatus.DEPRECATED

    def test_zero_ref_unregistered(self):
        asset = _make_asset(registered_in=[], priority=Priority.P2)
        index = _make_index(assets=[asset])
        lc = Lifecycle()
        events, new_index = lc.evaluate(index)
        zero_ref_events = [e for e in events if e.event_type == "ZERO_REF"]
        assert len(zero_ref_events) >= 1

    def test_zero_ref_skips_p0(self):
        asset = _make_asset(registered_in=[], priority=Priority.P0)
        index = _make_index(assets=[asset])
        lc = Lifecycle()
        events, new_index = lc.evaluate(index)
        zero_ref_events = [e for e in events if e.event_type == "ZERO_REF"]
        assert len(zero_ref_events) == 0

    def test_zero_ref_skips_already_deprecated(self):
        asset = _make_asset(registered_in=[], status=AssetStatus.DEPRECATED)
        index = _make_index(assets=[asset])
        lc = Lifecycle()
        events, new_index = lc.evaluate(index)
        zero_ref_events = [e for e in events if e.event_type == "ZERO_REF"]
        assert len(zero_ref_events) == 0

    def test_dir_convention_deprecated(self):
        asset = _make_asset(relative_path="src/_deprecated/old.py", status=AssetStatus.ACTIVE)
        index = _make_index(assets=[asset])
        lc = Lifecycle()
        events, new_index = lc.evaluate(index)
        dir_events = [e for e in events if e.event_type == "DIR_CONVENTION"]
        assert len(dir_events) >= 1
        assert dir_events[0].to_status == AssetStatus.DEPRECATED

    def test_dir_convention_archived(self):
        asset = _make_asset(relative_path="src/_archived/old.py", status=AssetStatus.ACTIVE)
        index = _make_index(assets=[asset])
        lc = Lifecycle()
        events, new_index = lc.evaluate(index)
        dir_events = [e for e in events if e.event_type == "DIR_CONVENTION"]
        assert len(dir_events) >= 1
        assert dir_events[0].to_status == AssetStatus.ARCHIVED

    def test_evaluate_updates_index(self):
        old_mtime = datetime.now(UTC) - timedelta(days=400)
        asset = _make_asset(mtime_utc=old_mtime, status=AssetStatus.ACTIVE)
        index = _make_index(assets=[asset])
        lc = Lifecycle()
        events, new_index = lc.evaluate(index)
        if events:
            assert new_index.assets[0].status != AssetStatus.ACTIVE or len(events) == 0

    def test_evaluate_empty_index(self):
        index = _make_index(assets=[])
        lc = Lifecycle()
        events, new_index = lc.evaluate(index)
        assert events == []
        assert new_index.total_assets == 0


class TestDefaultDecayDays:
    def test_all_asset_types_covered(self):
        for at in AssetType:
            assert at in DEFAULT_DECAY_DAYS

    def test_reasonable_values(self):
        for at, days in DEFAULT_DECAY_DAYS.items():
            assert days > 0


class TestGenerateEventId:
    def test_format(self):
        eid = _generate_event_id()
        assert eid.startswith("LCEVT-")
