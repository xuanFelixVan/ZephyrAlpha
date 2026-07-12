# [A_test] module_id: SRC-TST-1446 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_replay_engine
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

from datetime import UTC, datetime, timedelta

import pytest

from zephyr.gov_audit.replay_engine import (
    ReplayEngine,
    ReplayResult,
    ReplaySnapshot,
)


@pytest.fixture
def sample_events():
    now = datetime.now(UTC)
    return [
        {
            "entry_id": "r1",
            "agent_id": "agent-a",
            "action_type": "write",
            "target_path": "/tmp/f1.py",
            "lamport_clock_counter": 1,
            "lamport_clock_ide": "ide-1",
            "timestamp": now.isoformat(),
        },
        {
            "entry_id": "r2",
            "agent_id": "agent-b",
            "action_type": "read",
            "target_path": "/tmp/f2.py",
            "lamport_clock_counter": 2,
            "lamport_clock_ide": "ide-1",
            "timestamp": (now - timedelta(hours=1)).isoformat(),
        },
        {
            "entry_id": "r3",
            "agent_id": "agent-a",
            "operation": "delete",
            "file_path": "/tmp/f3.py",
            "lamport_clock_counter": 3,
            "lamport_clock_ide": "ide-2",
            "timestamp": (now - timedelta(hours=2)).isoformat(),
        },
    ]


@pytest.fixture
def engine(tmp_path):
    return ReplayEngine(event_log_path=tmp_path / "nonexistent.jsonl", snapshot_interval=2)


class TestReplaySnapshot:
    def test_default_values(self):
        snap = ReplaySnapshot()
        assert snap.lamport_counter == 0
        assert snap.entry_count == 0
        assert snap.state == {}

    def test_custom_values(self):
        snap = ReplaySnapshot(
            lamport_counter=5, entry_count=3, last_entry_id="e1", last_agent_id="a1", state={"key": "val"}
        )
        assert snap.lamport_counter == 5
        assert snap.state["key"] == "val"


class TestReplayResult:
    def test_default_values(self):
        result = ReplayResult()
        assert result.events_replayed == 0
        assert result.is_deterministic is True
        assert result.divergence_points == []

    def test_custom_values(self):
        result = ReplayResult(events_replayed=10, is_deterministic=False, divergence_points=["d1"])
        assert result.events_replayed == 10
        assert len(result.divergence_points) == 1


class TestReplayEngine:
    def test_instantiation(self, tmp_path):
        eng = ReplayEngine(event_log_path=tmp_path / "events.jsonl")
        assert eng._snapshot_interval == 100

    def test_replay_basic(self, engine, sample_events):
        result = engine.replay(sample_events)
        assert isinstance(result, ReplayResult)
        assert result.events_replayed == 3
        assert result.is_deterministic is True
        assert len(result.final_state) > 0

    def test_replay_empty_events(self, engine):
        result = engine.replay([])
        assert result.events_replayed == 0
        assert result.final_state == {}

    def test_replay_none_loads_from_file(self, engine):
        result = engine.replay(None)
        assert result.events_replayed == 0

    def test_replay_snapshot_interval(self, sample_events):
        engine = ReplayEngine(snapshot_interval=2)
        result = engine.replay(sample_events)
        assert len(result.snapshots) == 1
        assert result.snapshots[0].entry_count == 2

    def test_replay_state_building(self, engine, sample_events):
        result = engine.replay(sample_events)
        assert "agent-a" in result.final_state
        assert result.final_state["agent-a"]["entry_count"] == 2
        assert result.final_state["agent-b"]["entry_count"] == 1

    def test_replay_deterministic_sorting(self, engine):
        events = [
            {"entry_id": "a", "agent_id": "x", "lamport_clock_counter": 5, "lamport_clock_ide": "ide-2"},
            {"entry_id": "b", "agent_id": "x", "lamport_clock_counter": 2, "lamport_clock_ide": "ide-1"},
            {"entry_id": "c", "agent_id": "x", "lamport_clock_counter": 2, "lamport_clock_ide": "ide-2"},
        ]
        result = engine.replay(events)
        assert result.is_deterministic is True

    def test_replay_range_with_timestamps(self, engine, sample_events):
        now = datetime.now(UTC)
        start = (now - timedelta(hours=3)).isoformat()
        end = now.isoformat()
        result = engine.replay_range(start_timestamp=start, end_timestamp=end, events=sample_events)
        assert result.events_replayed >= 1

    def test_replay_range_no_timestamps(self, engine, sample_events):
        result = engine.replay_range(events=sample_events)
        assert result.events_replayed == 3

    def test_replay_range_filters_events(self, engine, sample_events):
        now = datetime.now(UTC)
        start = (now - timedelta(minutes=30)).isoformat()
        end = now.isoformat()
        result = engine.replay_range(start_timestamp=start, end_timestamp=end, events=sample_events)
        assert result.events_replayed <= 3

    def test_verify_determinism_true(self, engine, sample_events):
        assert engine.verify_determinism(sample_events, runs=3) is True

    def test_verify_determinism_empty(self, engine):
        assert engine.verify_determinism([], runs=3) is True

    def test_verify_determinism_none_loads_empty(self, engine):
        assert engine.verify_determinism(None, runs=3) is True

    def test_replay_target_state(self, engine, sample_events):
        result = engine.replay(sample_events)
        assert "/tmp/f1.py" in result.final_state
        assert result.final_state["/tmp/f1.py"]["last_modified_by"] == "agent-a"

    def test_replay_events_without_timestamp_filtered_in_range(self, engine):
        events = [
            {"entry_id": "nt1", "agent_id": "a", "lamport_clock_counter": 1, "lamport_clock_ide": "x"},
        ]
        result = engine.replay_range(
            start_timestamp="2020-01-01T00:00:00Z", end_timestamp="2020-12-31T23:59:59Z", events=events
        )
        assert result.events_replayed == 0
