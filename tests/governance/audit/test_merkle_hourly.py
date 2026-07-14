# [A_test] module_id: SRC-TST-1261 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_merkle_hourly
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import hashlib
import json

from zephyr.gov_audit.merkle_hourly import (
    AggregationResult,
    HourlyMerkleAggregator,
    MerkleHourlyRoot,
)


class TestHourlyMerkleAggregatorInit:
    def test_creates_merkle_dir(self, tmp_path):
        data_dir = tmp_path / "audit_test"
        manager = HourlyMerkleAggregator(data_dir=data_dir)
        assert (data_dir / "merkle_hourly").exists()


class TestAggregate:
    def test_no_events_returns_none(self, tmp_path):
        manager = HourlyMerkleAggregator(data_dir=tmp_path / "m1")
        result = manager.aggregate("2026-01-01T00")
        assert result is None

    def test_events_without_hashes_returns_none(self, tmp_path):
        data_dir = tmp_path / "m2"
        data_dir.mkdir(parents=True)
        events_path = data_dir / "events.jsonl"
        events_path.write_text(
            json.dumps({"timestamp": "2026-01-01T00:00:00Z", "event_type": "test"}),
            encoding="utf-8",
        )
        manager = HourlyMerkleAggregator(data_dir=data_dir)
        result = manager.aggregate("2026-01-01T00")
        assert result is None

    def test_aggregate_with_events(self, tmp_path):
        data_dir = tmp_path / "m3"
        data_dir.mkdir(parents=True)
        events_path = data_dir / "events.jsonl"
        h1 = hashlib.sha256(b"event1").hexdigest()
        h2 = hashlib.sha256(b"event2").hexdigest()
        events = [
            {"timestamp": "2026-01-01T00:05:00Z", "entry_hash": h1},
            {"timestamp": "2026-01-01T00:10:00Z", "entry_hash": h2},
        ]
        events_path.write_text(
            "\n".join(json.dumps(e) for e in events),
            encoding="utf-8",
        )
        manager = HourlyMerkleAggregator(data_dir=data_dir)
        result = manager.aggregate("2026-01-01T00")
        assert isinstance(result, AggregationResult)
        assert result.success is True
        assert result.entry_count == 2
        assert result.merkle_root != ""

    def test_merkle_file_written(self, tmp_path):
        data_dir = tmp_path / "m4"
        data_dir.mkdir(parents=True)
        events_path = data_dir / "events.jsonl"
        h1 = hashlib.sha256(b"e1").hexdigest()
        events_path.write_text(
            json.dumps({"timestamp": "2026-01-01T00:05:00Z", "entry_hash": h1}),
            encoding="utf-8",
        )
        manager = HourlyMerkleAggregator(data_dir=data_dir)
        result = manager.aggregate("2026-01-01T00")
        assert result is not None
        merkle_file = data_dir / "merkle_hourly" / "2026-01-01T00.merkle"
        assert merkle_file.exists()


class TestGetRoots:
    def test_no_roots(self, tmp_path):
        manager = HourlyMerkleAggregator(data_dir=tmp_path / "m5")
        roots = manager.get_roots()
        assert roots == []

    def test_returns_stored_roots(self, tmp_path):
        data_dir = tmp_path / "m6"
        data_dir.mkdir(parents=True)
        events_path = data_dir / "events.jsonl"
        h1 = hashlib.sha256(b"e1").hexdigest()
        events_path.write_text(
            json.dumps({"timestamp": "2026-01-01T00:05:00Z", "entry_hash": h1}),
            encoding="utf-8",
        )
        manager = HourlyMerkleAggregator(data_dir=data_dir)
        manager.aggregate("2026-01-01T00")
        roots = manager.get_roots()
        assert len(roots) >= 1
        assert isinstance(roots[0], MerkleHourlyRoot)


class TestVerifyRoot:
    def test_missing_merkle_file(self, tmp_path):
        manager = HourlyMerkleAggregator(data_dir=tmp_path / "m7")
        assert manager.verify_root("2026-01-01T00") is False

    def test_verify_valid_root(self, tmp_path):
        data_dir = tmp_path / "m8"
        data_dir.mkdir(parents=True)
        events_path = data_dir / "events.jsonl"
        h1 = hashlib.sha256(b"e1").hexdigest()
        events_path.write_text(
            json.dumps({"timestamp": "2026-01-01T00:05:00Z", "entry_hash": h1}),
            encoding="utf-8",
        )
        manager = HourlyMerkleAggregator(data_dir=data_dir)
        manager.aggregate("2026-01-01T00")
        assert manager.verify_root("2026-01-01T00") is True
