# [A_test] module_id: SRC-TST-1563 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_self_monitor
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
import time
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from zephyr.gov_audit.self_monitor import SelfMonitor


@pytest.fixture
def data_dir(tmp_path):
    return tmp_path / "audit-trail"


@pytest.fixture
def data_dir_with_events(data_dir):
    data_dir.mkdir(parents=True, exist_ok=True)
    log_path = data_dir / "events.jsonl"
    events = [
        {"entry_id": "e1", "event_type": "file_write", "agent_id": "a", "timestamp": datetime.now(UTC).isoformat()},
        {"entry_id": "e2", "event_type": "file_read", "agent_id": "b", "timestamp": datetime.now(UTC).isoformat()},
    ]
    with open(log_path, "w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")
    return data_dir


@pytest.fixture
def monitor(data_dir):
    return SelfMonitor(data_dir=data_dir, heartbeat_interval=300, health_check_interval=600)


class TestSelfMonitor:
    def test_instantiation(self, data_dir):
        mon = SelfMonitor(data_dir=data_dir)
        assert mon._heartbeat_interval == 300
        assert mon._health_check_interval == 600

    def test_heartbeat_no_file(self, monitor):
        result = monitor.heartbeat()
        assert "timestamp" in result
        assert result["total_events"] == 0
        assert result["file_size_mb"] == 0.0
        assert result["healthy"] is True

    def test_heartbeat_with_events(self, data_dir_with_events):
        mon = SelfMonitor(data_dir=data_dir_with_events)
        result = mon.heartbeat()
        assert result["total_events"] == 2
        assert result["file_size_mb"] >= 0.0

    def test_check_basic(self, data_dir_with_events):
        mon = SelfMonitor(data_dir=data_dir_with_events)
        with (
            patch("zephyr.governance.integrity.IntegrityVerifier") as mock_v,
            patch("zephyr.gov_audit.query.AuditQuery") as mock_q,
        ):
            mock_v_inst = MagicMock()
            mock_v_inst.verify_chain.return_value = {"status": "valid", "events_checked": 2, "issues": []}
            mock_v.return_value = mock_v_inst
            mock_q_inst = MagicMock()
            mock_q_inst._load_events.return_value = []
            mock_q.return_value = mock_q_inst
            health = mon.check()
            assert "timestamp" in health
            assert "healthy" in health
            assert "file_size_mb" in health

    def test_check_empty_dir(self, monitor):
        health = monitor.check()
        assert health["file_size_mb"] == 0.0
        assert health["healthy"] is True

    def test_last_health_property(self, monitor):
        monitor.check()
        last = monitor.last_health
        assert isinstance(last, dict)
        assert "timestamp" in last

    def test_is_running_default(self, monitor):
        assert monitor.is_running is False

    def test_write_heartbeat(self, data_dir):
        with patch("zephyr.gov_audit.writer.AuditWriter") as mock_cls:
            mock_writer = MagicMock()
            mock_writer.write.return_value = "abc123def456"
            mock_writer.event_count = 1
            mock_cls.return_value = mock_writer
            mon = SelfMonitor(data_dir=data_dir)
            result = mon.write_heartbeat()
            assert "chain_hash" in result
            assert result["event_count"] == 1

    def test_start_and_stop_scheduler(self, monitor):
        monitor.start_scheduler(daemon=True)
        assert monitor.is_running is True
        monitor.stop_scheduler()
        time.sleep(0.2)
        assert monitor.is_running is False

    def test_event_count_no_file(self, monitor):
        assert monitor._event_count() == 0

    def test_file_size_mb_no_file(self, monitor):
        assert monitor._file_size_mb() == 0.0

    def test_load_events_raw_no_file(self, monitor):
        assert monitor._load_events_raw(limit=10) == []

    def test_load_events_raw_with_data(self, data_dir_with_events):
        mon = SelfMonitor(data_dir=data_dir_with_events)
        events = mon._load_events_raw(limit=10)
        assert len(events) == 2
