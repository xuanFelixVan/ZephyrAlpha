# [A_test] module_id: SRC-TST-0496 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_cascade_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_cascade_detector.py -q
# [TTL] task_bound

from __future__ import annotations

import tempfile
from datetime import UTC, datetime, timedelta

from zephyr.gov_drift.cascade_detector import (
    CASCADE_CONFIG,
    CascadeAlert,
    CascadeConfig,
    CascadeEventRecord,
    _load_cascade_state,
    _save_cascade_state,
    detect_cascade,
    dry_run_impact_analysis,
    is_auto_fix_paused,
)


class TestCascadeEvent:
    def test_instantiation_defaults(self):
        evt = CascadeEventRecord(
            event_id="evt-001",
            module="zephyr.shared",
            detected_at=datetime(2026, 1, 1, tzinfo=UTC),
        )
        assert evt.event_id == "evt-001"
        assert evt.module == "zephyr.shared"
        assert evt.resolved_at is None
        assert evt.fix_diff == ""

    def test_instantiation_with_optional_fields(self):
        now = datetime.now(UTC)
        evt = CascadeEventRecord(
            event_id="evt-002",
            module="zephyr.infrastructure.budget_enforcement",
            detected_at=now,
            resolved_at=now + timedelta(minutes=5),
            fix_diff="--- a\n+++ b\n",
        )
        assert evt.resolved_at is not None
        assert evt.fix_diff == "--- a\n+++ b\n"


class TestCascadeAlert:
    def test_instantiation_defaults(self):
        now = datetime.now(UTC)
        alert = CascadeAlert(
            alert_id="cascade-test-001",
            module="zephyr.shared",
            trigger_events=[],
            cascade_count=3,
            first_detected=now,
            last_detected=now,
        )
        assert alert.auto_fix_paused is True
        assert alert.pause_until is None
        assert alert.forensics_report == ""

    def test_instantiation_full(self):
        now = datetime.now(UTC)
        later = now + timedelta(hours=1)
        alert = CascadeAlert(
            alert_id="cascade-test-002",
            module="zephyr.shared",
            trigger_events=[],
            cascade_count=5,
            first_detected=now,
            last_detected=later,
            auto_fix_paused=True,
            pause_until=later,
            forensics_report="Cascade detected",
        )
        assert alert.cascade_count == 5
        assert alert.pause_until == later
        assert "Cascade" in alert.forensics_report


class TestCascadeConfig:
    def test_instantiation_defaults(self):
        cfg = CascadeConfig()
        assert cfg.window_minutes == 30
        assert cfg.threshold == 3
        assert cfg.lockout_minutes == 60
        assert cfg.state_dir == ""

    def test_instantiation_custom(self):
        cfg = CascadeConfig(window_minutes=10, threshold=5, lockout_minutes=30, state_dir="/tmp/cs")
        assert cfg.window_minutes == 10
        assert cfg.threshold == 5
        assert cfg.lockout_minutes == 30
        assert cfg.state_dir == "/tmp/cs"


class TestDetectCascade:
    def test_no_events_returns_empty(self):
        result = detect_cascade([])
        assert result == []

    def test_below_threshold_no_alert(self):
        now = datetime.now(UTC).isoformat()
        events = [
            {"event_id": "e1", "source_file": "src/zephyr/shared/foo.py", "timestamp": now},
            {"event_id": "e2", "source_file": "src/zephyr/shared/bar.py", "timestamp": now},
        ]
        result = detect_cascade(events)
        assert result == []

    def test_at_threshold_triggers_alert(self):
        now = datetime.now(UTC).isoformat()
        events = [{"event_id": f"e{i}", "source_file": "src/zephyr/shared/mod.py", "timestamp": now} for i in range(3)]
        result = detect_cascade(events)
        assert len(result) == 1
        assert result[0].module == "zephyr"
        assert result[0].cascade_count >= 3
        assert result[0].auto_fix_paused is True
        assert result[0].pause_until is not None
        assert "Cascade detected" in result[0].forensics_report

    def test_events_outside_window_no_alert(self):
        old = (datetime.now(UTC) - timedelta(hours=2)).isoformat()
        events = [{"event_id": f"e{i}", "source_file": "src/zephyr/shared/mod.py", "timestamp": old} for i in range(4)]
        result = detect_cascade(events)
        assert result == []

    def test_events_without_timestamp_skipped(self):
        events = [{"event_id": f"e{i}", "source_file": "src/zephyr/shared/mod.py"} for i in range(5)]
        result = detect_cascade(events)
        assert result == []

    def test_unknown_module_for_no_src_prefix(self):
        now = datetime.now(UTC).isoformat()
        events = [{"event_id": f"e{i}", "source_file": "random_file.py", "timestamp": now} for i in range(4)]
        result = detect_cascade(events)
        assert len(result) == 1
        assert result[0].module == "unknown"


class TestDryRunImpactAnalysis:
    def test_valid_diff_safe(self):
        result = dry_run_impact_analysis("x = 1\n", "DET-001", "/tmp")
        assert result["detector_id"] == "DET-001"
        assert result["safe_to_apply"] is True
        assert result["side_effects"] == []

    def test_syntax_error_diff_unsafe(self):
        bad_diff = "def foo(:\n  pass\n"
        result = dry_run_impact_analysis(bad_diff, "DET-002", "/tmp")
        assert result["safe_to_apply"] is False
        assert len(result["side_effects"]) > 0
        assert "Syntax error" in result["side_effects"][0]

    def test_empty_diff_safe(self):
        result = dry_run_impact_analysis("", "DET-003", "/tmp")
        assert result["safe_to_apply"] is True
        assert result["impacted_files"] == 0


class TestIsAutoFixPaused:
    def test_no_state_dir_returns_false(self):
        original_dir = CASCADE_CONFIG.state_dir
        CASCADE_CONFIG.state_dir = ""
        try:
            assert is_auto_fix_paused("zephyr.shared") is False
        finally:
            CASCADE_CONFIG.state_dir = original_dir

    def test_paused_module_returns_true(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = CASCADE_CONFIG.state_dir
            CASCADE_CONFIG.state_dir = tmpdir
            try:
                pause_until = (datetime.now(UTC) + timedelta(hours=1)).isoformat()
                state = {
                    "events": [],
                    "alerts": [
                        {
                            "module": "zephyr.shared",
                            "auto_fix_paused": True,
                            "pause_until": pause_until,
                        }
                    ],
                }
                _save_cascade_state(state)
                assert is_auto_fix_paused("zephyr.shared") is True
            finally:
                CASCADE_CONFIG.state_dir = original_dir

    def test_expired_pause_returns_false(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = CASCADE_CONFIG.state_dir
            CASCADE_CONFIG.state_dir = tmpdir
            try:
                pause_until = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
                state = {
                    "events": [],
                    "alerts": [
                        {
                            "module": "zephyr.shared",
                            "auto_fix_paused": True,
                            "pause_until": pause_until,
                        }
                    ],
                }
                _save_cascade_state(state)
                assert is_auto_fix_paused("zephyr.shared") is False
            finally:
                CASCADE_CONFIG.state_dir = original_dir


class TestLoadSaveCascadeState:
    def test_load_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = CASCADE_CONFIG.state_dir
            CASCADE_CONFIG.state_dir = tmpdir
            try:
                state = _load_cascade_state()
                assert state == {"events": [], "alerts": []}
            finally:
                CASCADE_CONFIG.state_dir = original_dir

    def test_save_and_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = CASCADE_CONFIG.state_dir
            CASCADE_CONFIG.state_dir = tmpdir
            try:
                state = {"events": [{"id": "x"}], "alerts": [{"module": "m"}]}
                _save_cascade_state(state)
                loaded = _load_cascade_state()
                assert loaded["events"] == [{"id": "x"}]
                assert loaded["alerts"] == [{"module": "m"}]
            finally:
                CASCADE_CONFIG.state_dir = original_dir

    def test_save_no_state_dir_is_noop(self):
        original_dir = CASCADE_CONFIG.state_dir
        CASCADE_CONFIG.state_dir = ""
        try:
            _save_cascade_state({"events": [], "alerts": []})
        finally:
            CASCADE_CONFIG.state_dir = original_dir
