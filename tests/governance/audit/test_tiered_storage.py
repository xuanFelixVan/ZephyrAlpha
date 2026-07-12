# [A_test] module_id: SRC-TST-1740 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_tiered_storage
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

import pytest

from zephyr.gov_audit.tiered_storage import (
    MigrationRecord,
    StorageTier,
    TierConfig,
    TieredStorageManager,
)


@pytest.fixture
def data_dir(tmp_path):
    return tmp_path / "audit-trail"


@pytest.fixture
def manager(data_dir):
    config = TierConfig(hot_days=7, warm_days=90)
    return TieredStorageManager(data_dir=data_dir, config=config)


@pytest.fixture
def manager_with_hot_files(data_dir):
    config = TierConfig(hot_days=7, warm_days=90)
    mgr = TieredStorageManager(data_dir=data_dir, config=config)
    hot_dir = data_dir / "hot"
    hot_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC)
    events = [
        {"entry_id": "e1", "event_type": "file_write", "timestamp": now.isoformat()},
        {"entry_id": "e2", "event_type": "file_read", "timestamp": now.isoformat()},
    ]
    log_path = hot_dir / "events.jsonl"
    with open(log_path, "w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")
    return mgr


class TestStorageTier:
    def test_enum_values(self):
        assert StorageTier.HOT == "hot"
        assert StorageTier.WARM == "warm"
        assert StorageTier.COLD == "cold"


class TestTierConfig:
    def test_default_values(self):
        config = TierConfig()
        assert config.hot_days == 7
        assert config.warm_days == 90
        assert config.hot_dir == "hot"
        assert config.warm_dir == "warm"
        assert config.cold_dir == "cold"

    def test_custom_values(self):
        config = TierConfig(hot_days=3, warm_days=30, cold_dir="archive")
        assert config.hot_days == 3
        assert config.cold_dir == "archive"


class TestMigrationRecord:
    def test_default_values(self):
        rec = MigrationRecord()
        assert rec.source_tier == StorageTier.HOT
        assert rec.target_tier == StorageTier.WARM
        assert rec.entries_migrated == 0

    def test_custom_values(self):
        rec = MigrationRecord(
            source_tier=StorageTier.WARM, target_tier=StorageTier.COLD, file_name="test.jsonl.gz", entries_migrated=10
        )
        assert rec.source_tier == StorageTier.WARM


class TestTieredStorageManager:
    def test_instantiation_creates_dirs(self, data_dir):
        mgr = TieredStorageManager(data_dir=data_dir)
        assert (data_dir / "hot").exists()
        assert (data_dir / "warm").exists()
        assert (data_dir / "cold").exists()

    def test_get_tier_hot(self, manager):
        now = datetime.now(UTC).isoformat()
        assert manager.get_tier(now) == StorageTier.HOT

    def test_get_tier_warm(self, manager):
        ts = (datetime.now(UTC) - timedelta(days=30)).isoformat()
        assert manager.get_tier(ts) == StorageTier.WARM

    def test_get_tier_cold(self, manager):
        ts = (datetime.now(UTC) - timedelta(days=120)).isoformat()
        assert manager.get_tier(ts) == StorageTier.COLD

    def test_get_tier_invalid_timestamp(self, manager):
        assert manager.get_tier("not-a-date") == StorageTier.HOT

    def test_get_tier_none_timestamp(self, manager):
        assert manager.get_tier("") == StorageTier.HOT

    def test_migrate_hot_to_warm(self, manager_with_hot_files, data_dir):
        mgr = manager_with_hot_files
        hot_file = data_dir / "hot" / "events.jsonl"
        assert hot_file.exists()
        records = mgr.migrate(StorageTier.HOT, StorageTier.WARM)
        assert len(records) >= 1
        assert records[0].source_tier == StorageTier.HOT
        assert records[0].target_tier == StorageTier.WARM
        assert not hot_file.exists()
        warm_files = list((data_dir / "warm").glob("*.jsonl.gz"))
        assert len(warm_files) >= 1

    def test_migrate_nonexistent_source(self, manager, data_dir):
        records = mgr.migrate(StorageTier.HOT, StorageTier.WARM) if (mgr := manager) else []
        assert records == []

    def test_migrate_specific_file(self, manager_with_hot_files, data_dir):
        mgr = manager_with_hot_files
        records = mgr.migrate(StorageTier.HOT, StorageTier.WARM, file_name="events.jsonl")
        assert len(records) >= 1

    def test_migrate_nonexistent_file(self, manager_with_hot_files):
        records = manager_with_hot_files.migrate(StorageTier.HOT, StorageTier.WARM, file_name="nonexistent.jsonl")
        assert records == []

    def test_auto_migrate_no_expired(self, manager_with_hot_files):
        records = manager_with_hot_files.auto_migrate()
        assert isinstance(records, list)

    def test_auto_migrate_with_expired_hot(self, data_dir):
        config = TierConfig(hot_days=0, warm_days=90)
        mgr = TieredStorageManager(data_dir=data_dir, config=config)
        hot_dir = data_dir / "hot"
        hot_dir.mkdir(parents=True, exist_ok=True)
        old_time = (datetime.now(UTC) - timedelta(days=10)).timestamp()
        log_path = hot_dir / "old.jsonl"
        log_path.write_text('{"test": true}\n', encoding="utf-8")
        import os

        os.utime(log_path, (old_time, old_time))
        records = mgr.auto_migrate()
        assert len(records) >= 1

    def test_count_jsonl_lines(self, data_dir):
        mgr = TieredStorageManager(data_dir=data_dir)
        test_file = data_dir / "hot" / "test.jsonl"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write('{"a": 1}\n{"b": 2}\n\n{"c": 3}\n')
        assert TieredStorageManager._count_jsonl_lines(test_file) == 3
