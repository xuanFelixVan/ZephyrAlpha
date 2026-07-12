# [A_test] module_id: SRC-TST-1028 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_forensics_engine
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_forensics_engine.py -q
# [TTL] task_bound

from __future__ import annotations

import json
import os
from datetime import UTC, datetime

from zephyr.gov_drift.forensics_engine import (
    FORENSICS_CONFIG,
    ForensicsConfig,
    ForensicsReport,
    ForensicsTimelineEntry,
    generate_forensics_report,
    git_checkout_snapshot,
    replay_baseline_history,
    serialize_report,
)


class TestForensicsTimelineEntryInstantiation:
    def test_all_fields(self):
        now = datetime.now(UTC)
        entry = ForensicsTimelineEntry(
            timestamp=now,
            action="modify",
            actor="system",
            state_before="CLEAN",
            state_after="DRIFTED",
            file_changed="test.py",
            diff_summary="+1 -0",
        )
        assert entry.timestamp == now
        assert entry.action == "modify"
        assert entry.actor == "system"
        assert entry.state_before == "CLEAN"
        assert entry.state_after == "DRIFTED"
        assert entry.file_changed == "test.py"
        assert entry.diff_summary == "+1 -0"

    def test_different_action_types(self):
        now = datetime.now(UTC)
        for action in ("create", "modify", "delete", "rename"):
            entry = ForensicsTimelineEntry(
                timestamp=now,
                action=action,
                actor="user",
                state_before="A",
                state_after="B",
                file_changed="f.py",
                diff_summary="N/A",
            )
            assert entry.action == action


class TestForensicsReportInstantiation:
    def test_all_required_fields(self):
        report = ForensicsReport(
            report_id="fr-001",
            drift_event_id="de-001",
            module="test_module",
            detector_id="det-1",
            severity="MAJOR",
            state="DETECTED",
            timeline=[],
            state_diffs=[],
            actor_trace=[],
            dependency_impact={},
        )
        assert report.report_id == "fr-001"
        assert report.drift_event_id == "de-001"
        assert report.module == "test_module"
        assert report.detector_id == "det-1"
        assert report.severity == "MAJOR"
        assert report.state == "DETECTED"
        assert report.timeline == []
        assert report.state_diffs == []
        assert report.actor_trace == []
        assert report.dependency_impact == {}

    def test_generated_at_auto_set(self):
        report = ForensicsReport(
            report_id="fr-002",
            drift_event_id="de-002",
            module="mod",
            detector_id="det",
            severity="LOW",
            state="FIXED",
            timeline=[],
            state_diffs=[],
            actor_trace=[],
            dependency_impact={},
        )
        assert isinstance(report.generated_at, datetime)
        assert report.generated_at.tzinfo is not None

    def test_with_timeline_entries(self):
        now = datetime.now(UTC)
        entry = ForensicsTimelineEntry(
            timestamp=now,
            action="modify",
            actor="agent",
            state_before="A",
            state_after="B",
            file_changed="f.py",
            diff_summary="+1",
        )
        report = ForensicsReport(
            report_id="fr-003",
            drift_event_id="de-003",
            module="mod",
            detector_id="det",
            severity="HIGH",
            state="DETECTED",
            timeline=[entry],
            state_diffs=[{"before": "A", "after": "B"}],
            actor_trace=["agent"],
            dependency_impact={"sibling_modules": ["a.py"]},
        )
        assert len(report.timeline) == 1
        assert len(report.state_diffs) == 1
        assert "agent" in report.actor_trace


class TestForensicsConfigInstantiation:
    def test_defaults(self):
        config = ForensicsConfig()
        assert config.state_dir == ""
        assert config.max_timeline_entries == 50
        assert config.include_blame is True

    def test_custom_config(self):
        config = ForensicsConfig(
            state_dir="/tmp/forensics",
            max_timeline_entries=100,
            include_blame=False,
        )
        assert config.state_dir == "/tmp/forensics"
        assert config.max_timeline_entries == 100
        assert config.include_blame is False

    def test_global_config_instance(self):
        assert isinstance(FORENSICS_CONFIG, ForensicsConfig)
        assert FORENSICS_CONFIG.max_timeline_entries == 50
        assert FORENSICS_CONFIG.include_blame is True


class TestReplayBaselineHistory:
    def test_empty_history(self):
        report = replay_baseline_history("test.py", [], [])
        assert report.timeline == []
        assert report.state_diffs == []
        assert report.actor_trace == []

    def test_single_entry(self):
        history = [
            {"timestamp": "2025-01-01T00:00:00Z", "action": "create", "state_after": "CLEAN", "diff": "+5"},
        ]
        report = replay_baseline_history("test.py", history, [])
        assert len(report.timeline) == 1
        assert report.timeline[0].action == "create"
        assert report.timeline[0].state_after == "CLEAN"

    def test_multiple_entries_with_state_diffs(self):
        history = [
            {"timestamp": "2025-01-01T00:00:00Z", "action": "create", "state_after": "CLEAN", "diff": "+5"},
            {"timestamp": "2025-01-02T00:00:00Z", "action": "modify", "state_after": "DRIFTED", "diff": "+1 -2"},
        ]
        report = replay_baseline_history("test.py", history, [])
        assert len(report.timeline) == 2
        assert len(report.state_diffs) >= 1

    def test_drift_events_actor_trace(self):
        history = [
            {"timestamp": "2025-01-01T00:00:00Z", "action": "modify", "state_after": "DRIFTED", "diff": "+1"},
        ]
        drift_events = [{"source_file": "test.py", "detector_id": "det-1"}]
        report = replay_baseline_history("test.py", history, drift_events)
        assert "det-1" in report.actor_trace

    def test_report_id_format(self):
        report = replay_baseline_history("test.py", [], [])
        assert report.report_id.startswith("forensics-")

    def test_max_timeline_entries_respected(self):
        entries = [
            {"timestamp": f"2025-01-{i:02d}T00:00:00Z", "action": "modify", "state_after": "DRIFTED", "diff": "+1"}
            for i in range(1, 60)
        ]
        report = replay_baseline_history("test.py", entries, [])
        assert len(report.timeline) <= FORENSICS_CONFIG.max_timeline_entries

    def test_invalid_timestamp_handled(self):
        history = [
            {"timestamp": "invalid-date", "action": "create", "state_after": "CLEAN", "diff": "+1"},
        ]
        report = replay_baseline_history("test.py", history, [])
        assert len(report.timeline) == 1
        assert isinstance(report.timeline[0].timestamp, datetime)

    def test_missing_timestamp_handled(self):
        history = [
            {"action": "create", "state_after": "CLEAN", "diff": "+1"},
        ]
        report = replay_baseline_history("test.py", history, [])
        assert len(report.timeline) == 1

    def test_no_state_diff_when_same_state(self):
        history = [
            {"timestamp": "2025-01-01T00:00:00Z", "action": "touch", "state_after": "CLEAN", "diff": "+0"},
            {"timestamp": "2025-01-02T00:00:00Z", "action": "touch", "state_after": "CLEAN", "diff": "+0"},
        ]
        report = replay_baseline_history("test.py", history, [])
        assert len(report.state_diffs) == 0

    def test_sibling_modules_in_dependency_impact(self, tmp_path):
        sibling = tmp_path / "other.py"
        sibling.write_text("x = 1", encoding="utf-8")
        target = tmp_path / "target.py"
        target.write_text("y = 2", encoding="utf-8")
        history = [
            {"timestamp": "2025-01-01T00:00:00Z", "action": "modify", "state_after": "DRIFTED", "diff": "+1"},
        ]
        report = replay_baseline_history(str(target), history, [])
        assert "sibling_modules" in report.dependency_impact
        assert "other.py" in report.dependency_impact["sibling_modules"]


class TestGitCheckoutSnapshot:
    def test_invalid_commit(self, tmp_path):
        result = git_checkout_snapshot("invalid_hash_12345", "test.py", str(tmp_path))
        assert result is None

    def test_nonexistent_project_root(self):
        result = git_checkout_snapshot("abc123", "test.py", "/nonexistent/path")
        assert result is None


class TestGenerateForensicsReport:
    def test_basic_report(self, tmp_path):
        report = generate_forensics_report(
            drift_event_id="de-001",
            source_file="test.py",
            project_root=str(tmp_path),
        )
        assert report.drift_event_id == "test"
        assert report.detector_id == "forensics_engine"
        assert report.severity == "MAJOR"
        assert report.state == "DETECTED"

    def test_with_history(self, tmp_path):
        history = [
            {"timestamp": "2025-01-01T00:00:00Z", "action": "create", "state_after": "CLEAN", "diff": "+5"},
        ]
        report = generate_forensics_report(
            drift_event_id="de-002",
            source_file="test.py",
            project_root=str(tmp_path),
            baseline_history=history,
        )
        assert len(report.timeline) == 1

    def test_with_drift_events(self, tmp_path):
        history = [
            {"timestamp": "2025-01-01T00:00:00Z", "action": "modify", "state_after": "DRIFTED", "diff": "+1"},
        ]
        drift_events = [{"source_file": "test.py", "detector_id": "det-x"}]
        report = generate_forensics_report(
            drift_event_id="de-003",
            source_file="test.py",
            project_root=str(tmp_path),
            baseline_history=history,
            drift_events=drift_events,
        )
        assert "det-x" in report.actor_trace

    def test_none_history_and_events(self, tmp_path):
        report = generate_forensics_report(
            drift_event_id="de-004",
            source_file="test.py",
            project_root=str(tmp_path),
            baseline_history=None,
            drift_events=None,
        )
        assert report.timeline == []


class TestSerializeReport:
    def test_serialize_creates_file(self, tmp_path):
        report = ForensicsReport(
            report_id="fr-001",
            drift_event_id="de-001",
            module="test",
            detector_id="det-1",
            severity="MAJOR",
            state="DETECTED",
            timeline=[],
            state_diffs=[],
            actor_trace=[],
            dependency_impact={},
        )
        output_dir = str(tmp_path / "forensics_output")
        path = serialize_report(report, output_dir)
        assert os.path.exists(path)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["report_id"] == "fr-001"
        assert data["severity"] == "MAJOR"

    def test_serialize_with_timeline(self, tmp_path):
        entry = ForensicsTimelineEntry(
            timestamp=datetime.now(UTC),
            action="modify",
            actor="system",
            state_before="CLEAN",
            state_after="DRIFTED",
            file_changed="test.py",
            diff_summary="+1",
        )
        report = ForensicsReport(
            report_id="fr-002",
            drift_event_id="de-002",
            module="test",
            detector_id="det-1",
            severity="MAJOR",
            state="DETECTED",
            timeline=[entry],
            state_diffs=[],
            actor_trace=[],
            dependency_impact={},
        )
        output_dir = str(tmp_path / "forensics_output2")
        path = serialize_report(report, output_dir)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert len(data["timeline"]) == 1
        assert data["timeline"][0]["action"] == "modify"

    def test_serialize_safe_id_replaces_slashes(self, tmp_path):
        report = ForensicsReport(
            report_id="fr/with/slashes",
            drift_event_id="de-001",
            module="test",
            detector_id="det-1",
            severity="MAJOR",
            state="DETECTED",
            timeline=[],
            state_diffs=[],
            actor_trace=[],
            dependency_impact={},
        )
        output_dir = str(tmp_path / "forensics_output3")
        path = serialize_report(report, output_dir)
        assert "/" not in os.path.basename(path)

    def test_serialize_safe_id_replaces_backslashes(self, tmp_path):
        report = ForensicsReport(
            report_id="fr\\with\\backslash",
            drift_event_id="de-001",
            module="test",
            detector_id="det-1",
            severity="MAJOR",
            state="DETECTED",
            timeline=[],
            state_diffs=[],
            actor_trace=[],
            dependency_impact={},
        )
        output_dir = str(tmp_path / "forensics_output4")
        path = serialize_report(report, output_dir)
        assert "\\" not in os.path.basename(path)

    def test_serialize_json_structure(self, tmp_path):
        report = ForensicsReport(
            report_id="fr-005",
            drift_event_id="de-005",
            module="mod",
            detector_id="det",
            severity="LOW",
            state="FIXED",
            timeline=[],
            state_diffs=[{"before": "A", "after": "B"}],
            actor_trace=["agent-1"],
            dependency_impact={"sibling_modules": ["a.py"]},
        )
        output_dir = str(tmp_path / "forensics_output5")
        path = serialize_report(report, output_dir)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["report_id"] == "fr-005"
        assert data["drift_event_id"] == "de-005"
        assert data["module"] == "mod"
        assert data["detector_id"] == "det"
        assert data["severity"] == "LOW"
        assert data["state"] == "FIXED"
        assert len(data["state_diffs"]) == 1
        assert data["actor_trace"] == ["agent-1"]
        assert "sibling_modules" in data["dependency_impact"]
        assert "generated_at" in data

    def test_serialize_creates_output_dir(self, tmp_path):
        report = ForensicsReport(
            report_id="fr-006",
            drift_event_id="de-006",
            module="mod",
            detector_id="det",
            severity="MAJOR",
            state="DETECTED",
            timeline=[],
            state_diffs=[],
            actor_trace=[],
            dependency_impact={},
        )
        output_dir = str(tmp_path / "new_dir" / "sub_dir")
        path = serialize_report(report, output_dir)
        assert os.path.isdir(str(tmp_path / "new_dir" / "sub_dir"))
