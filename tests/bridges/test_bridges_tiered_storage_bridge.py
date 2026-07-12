# [A_test] module_id: SRC-TST-0460 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_bridges_tiered_storage_bridge
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

from zephyr.gov_audit.bridges.audit_tiered_storage_bridge import AuditTieredStorageBridge


@pytest.fixture
def bridge(tmp_path):
    return AuditTieredStorageBridge(data_dir=tmp_path)


@pytest.fixture
def bridge_with_events(tmp_path):
    data_dir = tmp_path
    log_path = data_dir / "events.jsonl"
    now = datetime.now(UTC)
    events = [
        {"event_type": "file_write", "agent_id": "a", "timestamp": now.isoformat()},
        {"event_type": "file_read", "agent_id": "b", "timestamp": (now - timedelta(days=20)).isoformat()},
        {"event_type": "file_delete", "agent_id": "c", "timestamp": (now - timedelta(days=100)).isoformat()},
    ]
    with open(log_path, "w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")
    return AuditTieredStorageBridge(data_dir=data_dir)


class TestAuditTieredStorageBridge:
    def test_instantiation(self, tmp_path):
        b = AuditTieredStorageBridge(data_dir=tmp_path)
        assert b._data_dir == tmp_path
        assert b._hot_dir == tmp_path
        assert b._warm_dir == tmp_path / "warm"
        assert b._cold_dir == tmp_path / "cold"

    def test_classify_events_hot(self, bridge):
        now = datetime.now(UTC)
        events = [{"timestamp": now.isoformat(), "event_type": "test"}]
        tiers = bridge.classify_events(events)
        assert len(tiers["hot"]) == 1
        assert len(tiers["warm"]) == 0
        assert len(tiers["cold"]) == 0

    def test_classify_events_warm(self, bridge):
        ts = (datetime.now(UTC) - timedelta(days=20)).isoformat()
        events = [{"timestamp": ts, "event_type": "test"}]
        tiers = bridge.classify_events(events)
        assert len(tiers["warm"]) == 1

    def test_classify_events_cold(self, bridge):
        ts = (datetime.now(UTC) - timedelta(days=100)).isoformat()
        events = [{"timestamp": ts, "event_type": "test"}]
        tiers = bridge.classify_events(events)
        assert len(tiers["cold"]) == 1

    def test_classify_events_invalid_timestamp(self, bridge):
        events = [{"timestamp": "invalid", "event_type": "test"}]
        tiers = bridge.classify_events(events)
        assert len(tiers["hot"]) == 1

    def test_classify_events_mixed(self, bridge):
        now = datetime.now(UTC)
        events = [
            {"timestamp": now.isoformat()},
            {"timestamp": (now - timedelta(days=20)).isoformat()},
            {"timestamp": (now - timedelta(days=100)).isoformat()},
        ]
        tiers = bridge.classify_events(events)
        assert len(tiers["hot"]) == 1
        assert len(tiers["warm"]) == 1
        assert len(tiers["cold"]) == 1

    def test_classify_events_empty(self, bridge):
        tiers = bridge.classify_events([])
        assert tiers == {"hot": [], "warm": [], "cold": []}

    def test_migrate_warm_no_file(self, bridge):
        result = bridge.migrate_warm()
        assert result == 0

    def test_migrate_warm_with_events(self, bridge_with_events):
        result = bridge_with_events.migrate_warm()
        assert isinstance(result, int)

    def test_get_storage_stats_empty(self, bridge):
        stats = bridge.get_storage_stats()
        assert stats["hot_size_mb"] == 0.0
        assert stats["warm_size_mb"] == 0.0
        assert stats["cold_size_mb"] == 0.0
        assert stats["hot_events"] == 0

    def test_get_storage_stats_with_events(self, bridge_with_events):
        stats = bridge_with_events.get_storage_stats()
        assert stats["hot_size_mb"] >= 0.0
        assert stats["hot_events"] >= 0
