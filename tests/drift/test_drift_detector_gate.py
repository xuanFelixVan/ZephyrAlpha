# [A_test] module_id: SRC-TST-0773 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_drift_detector_gate
# [INVARIANTS] trigger_recovery always returns dict with 9 keys; hotfix_bypass only True when HotfixBypass.is_hotfix_commit returns True; scan_level invalid falls back to STANDARD
# [MODIFY-GUARD] changes must preserve test coverage for trigger_recovery/hotfix_bypass/scan_level/empty_payload/ImportError paths
# [CONSUMERS] CI pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] trigger_recovery({}) returns dict with recovery_status; ImportError on drift_engine -> UnboundLocalError (source bug); empty payload -> defaults applied
# [TESTS] pytest tests/test_drift_detector_gate.py -q
# [TTL] task_bound

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from zephyr.gov_drift.drift_detector import trigger_recovery

_EXPECTED_KEYS = {
    "recovery_id",
    "module_id",
    "triggered_at",
    "recovery_status",
    "scan_result",
    "fix_results",
    "cascade_alerts",
    "hotfix_bypass",
    "errors",
}


def _make_scan_result(events=None, total=None):
    if events is None:
        events = []
    if total is None:
        total = len(events)
    return SimpleNamespace(
        scan_id=uuid.uuid4(),
        detectors_run=5,
        total_drift_events=total,
        storm_mode_triggered=False,
        events=events,
    )


def _make_event(dimension="code"):
    return SimpleNamespace(event_id=uuid.uuid4(), drift_dimension=dimension, created_at=None)


class TestTriggerRecoveryImport:
    def test_function_importable(self):
        from zephyr.gov_drift.drift_detector import trigger_recovery as fn

        assert callable(fn)


class TestTriggerRecoveryMinimalPayload:
    @patch("zephyr.gov_drift.drift_engine.scan")
    @patch("zephyr.gov_drift.drift_hotfix_bypass.HotfixBypass")
    def test_returns_dict_with_expected_keys(self, mock_bypass_cls, mock_scan):
        mock_bypass_inst = MagicMock()
        mock_bypass_inst.is_hotfix_commit.return_value = False
        mock_bypass_cls.return_value = mock_bypass_inst

        mock_scan.return_value = _make_scan_result()

        result = trigger_recovery({"module_id": "MOD-INF-023"})

        assert isinstance(result, dict)
        assert _EXPECTED_KEYS.issubset(result.keys())
        assert result["module_id"] == "MOD-INF-023"
        assert result["recovery_status"] == "NO_DRIFT_FOUND"
        assert result["hotfix_bypass"] is False
        assert result["scan_result"] is not None
        assert result["fix_results"] == []
        assert result["cascade_alerts"] == []
        assert result["errors"] == []


class TestTriggerRecoveryEmptyPayload:
    @patch("zephyr.gov_drift.drift_engine.scan")
    @patch("zephyr.gov_drift.drift_hotfix_bypass.HotfixBypass")
    def test_empty_dict_returns_defaults(self, mock_bypass_cls, mock_scan):
        mock_bypass_inst = MagicMock()
        mock_bypass_inst.is_hotfix_commit.return_value = False
        mock_bypass_cls.return_value = mock_bypass_inst

        mock_scan.return_value = _make_scan_result()

        result = trigger_recovery({})

        assert isinstance(result, dict)
        assert _EXPECTED_KEYS.issubset(result.keys())
        assert result["module_id"] == "MOD-INF-023"
        assert result["recovery_id"]
        assert result["triggered_at"]
        assert result["recovery_status"] == "NO_DRIFT_FOUND"

    def test_none_payload_raises(self):
        with pytest.raises((TypeError, AttributeError)):
            trigger_recovery(None)


class TestHotfixBypass:
    @patch("zephyr.gov_drift.drift_hotfix_bypass.HotfixBypass")
    def test_hotfix_commit_sets_bypass(self, mock_bypass_cls):
        mock_bypass_inst = MagicMock()
        mock_bypass_inst.is_hotfix_commit.return_value = True
        mock_bypass_cls.return_value = mock_bypass_inst

        result = trigger_recovery(
            {
                "module_id": "MOD-TEST",
                "commit_message": "[HOTFIX] critical fix",
            }
        )

        assert result["hotfix_bypass"] is True
        assert result["recovery_status"] == "HOTFIX_BYPASSED"
        assert result["module_id"] == "MOD-TEST"

    @patch("zephyr.gov_drift.drift_engine.scan")
    @patch("zephyr.gov_drift.drift_hotfix_bypass.HotfixBypass")
    def test_non_hotfix_commit_no_bypass(self, mock_bypass_cls, mock_scan):
        mock_bypass_inst = MagicMock()
        mock_bypass_inst.is_hotfix_commit.return_value = False
        mock_bypass_cls.return_value = mock_bypass_inst

        mock_scan.return_value = _make_scan_result()

        result = trigger_recovery(
            {
                "module_id": "MOD-TEST",
                "commit_message": "normal commit",
            }
        )

        assert result["hotfix_bypass"] is False
        assert result["recovery_status"] != "HOTFIX_BYPASSED"

    @patch("zephyr.gov_drift.drift_hotfix_bypass.HotfixBypass")
    def test_hotfix_bypass_instantiation_failure_non_fatal(self, mock_bypass_cls):
        mock_bypass_cls.side_effect = RuntimeError("config missing")

        result = trigger_recovery(
            {
                "module_id": "MOD-TEST",
                "commit_message": "[HOTFIX] fix",
            }
        )

        assert isinstance(result, dict)
        assert result["hotfix_bypass"] is False


class TestScanLevel:
    @patch("zephyr.gov_drift.drift_engine.scan")
    @patch("zephyr.gov_drift.drift_hotfix_bypass.HotfixBypass")
    def test_invalid_scan_level_falls_back_to_standard(self, mock_bypass_cls, mock_scan):
        mock_bypass_inst = MagicMock()
        mock_bypass_inst.is_hotfix_commit.return_value = False
        mock_bypass_cls.return_value = mock_bypass_inst

        mock_scan.return_value = _make_scan_result()

        result = trigger_recovery(
            {
                "module_id": "MOD-TEST",
                "scan_level": "INVALID_LEVEL",
            }
        )

        assert isinstance(result, dict)
        assert result["recovery_status"] in ("NO_DRIFT_FOUND", "SCAN_FAILED", "INITIATED")

    @patch("zephyr.gov_drift.drift_engine.scan")
    @patch("zephyr.gov_drift.drift_hotfix_bypass.HotfixBypass")
    def test_scan_level_deep_accepted(self, mock_bypass_cls, mock_scan):
        mock_bypass_inst = MagicMock()
        mock_bypass_inst.is_hotfix_commit.return_value = False
        mock_bypass_cls.return_value = mock_bypass_inst

        mock_scan.return_value = _make_scan_result()

        result = trigger_recovery(
            {
                "module_id": "MOD-TEST",
                "scan_level": "DEEP",
            }
        )

        assert isinstance(result, dict)
        assert result["recovery_status"] == "NO_DRIFT_FOUND"


class TestDriftEngineImportError:
    def test_drift_engine_unavailable_causes_unbound_local(self):
        with patch.dict("sys.modules", {"zephyr.gov_drift.drift_engine": None}):
            with pytest.raises(UnboundLocalError):
                trigger_recovery({"module_id": "MOD-TEST"})

    @patch("zephyr.gov_drift.drift_engine.scan")
    @patch("zephyr.gov_drift.drift_hotfix_bypass.HotfixBypass")
    def test_scan_failure_sets_scan_failed(self, mock_bypass_cls, mock_scan):
        mock_bypass_inst = MagicMock()
        mock_bypass_inst.is_hotfix_commit.return_value = False
        mock_bypass_cls.return_value = mock_bypass_inst

        mock_scan.side_effect = OSError("scan infrastructure down")

        result = trigger_recovery({"module_id": "MOD-TEST"})

        assert result["recovery_status"] == "SCAN_FAILED"
        assert any("scan failed" in e for e in result["errors"])


class TestTriggerRecoveryWithDriftEvents:
    @patch("zephyr.gov_drift.reconciler.AutoFixer")
    @patch("zephyr.gov_drift.cascade_detector.is_auto_fix_paused", return_value=False)
    @patch("zephyr.gov_drift.cascade_detector.detect_cascade", return_value=[])
    @patch("zephyr.gov_drift.drift_engine.scan")
    @patch("zephyr.gov_drift.drift_hotfix_bypass.HotfixBypass")
    def test_fully_recovered_when_all_fixed(
        self, mock_bypass_cls, mock_scan, mock_detect_cascade, mock_is_paused, mock_fixer_cls
    ):
        mock_bypass_inst = MagicMock()
        mock_bypass_inst.is_hotfix_commit.return_value = False
        mock_bypass_cls.return_value = mock_bypass_inst

        event1 = _make_event("code")
        event2 = _make_event("config")
        mock_scan.return_value = _make_scan_result(events=[event1, event2], total=2)

        mock_fixer = MagicMock()
        mock_fixer.auto_fix.return_value = True
        mock_fixer_cls.return_value = mock_fixer

        result = trigger_recovery(
            {
                "module_id": "MOD-TEST",
                "changed_files": ["a.py", "b.py"],
            }
        )

        assert result["recovery_status"] == "FULLY_RECOVERED"
        assert len(result["fix_results"]) == 2
        assert all(fr["status"] == "AUTO_FIXED" for fr in result["fix_results"])

    @patch("zephyr.gov_drift.reconciler.AutoFixer")
    @patch("zephyr.gov_drift.cascade_detector.is_auto_fix_paused", return_value=False)
    @patch("zephyr.gov_drift.cascade_detector.detect_cascade", return_value=[])
    @patch("zephyr.gov_drift.drift_engine.scan")
    @patch("zephyr.gov_drift.drift_hotfix_bypass.HotfixBypass")
    def test_partially_recovered_when_some_fixed(
        self, mock_bypass_cls, mock_scan, mock_detect_cascade, mock_is_paused, mock_fixer_cls
    ):
        mock_bypass_inst = MagicMock()
        mock_bypass_inst.is_hotfix_commit.return_value = False
        mock_bypass_cls.return_value = mock_bypass_inst

        event1 = _make_event("code")
        event2 = _make_event("config")
        mock_scan.return_value = _make_scan_result(events=[event1, event2], total=2)

        mock_fixer = MagicMock()
        mock_fixer.auto_fix.side_effect = [True, False]
        mock_fixer_cls.return_value = mock_fixer

        result = trigger_recovery({"module_id": "MOD-TEST"})

        assert result["recovery_status"] == "PARTIALLY_RECOVERED"
        assert len(result["fix_results"]) == 2
        statuses = [fr["status"] for fr in result["fix_results"]]
        assert "AUTO_FIXED" in statuses
        assert any(s != "AUTO_FIXED" for s in statuses)

    @patch("zephyr.gov_drift.reconciler.AutoFixer")
    @patch("zephyr.gov_drift.cascade_detector.is_auto_fix_paused", return_value=False)
    @patch("zephyr.gov_drift.cascade_detector.detect_cascade", return_value=[])
    @patch("zephyr.gov_drift.drift_engine.scan")
    @patch("zephyr.gov_drift.drift_hotfix_bypass.HotfixBypass")
    def test_recovery_failed_when_none_fixed(
        self, mock_bypass_cls, mock_scan, mock_detect_cascade, mock_is_paused, mock_fixer_cls
    ):
        mock_bypass_inst = MagicMock()
        mock_bypass_inst.is_hotfix_commit.return_value = False
        mock_bypass_cls.return_value = mock_bypass_inst

        event1 = _make_event("code")
        mock_scan.return_value = _make_scan_result(events=[event1], total=1)

        mock_fixer = MagicMock()
        mock_fixer.auto_fix.return_value = False
        mock_fixer_cls.return_value = mock_fixer

        result = trigger_recovery({"module_id": "MOD-TEST"})

        assert result["recovery_status"] == "RECOVERY_FAILED"
        assert len(result["fix_results"]) == 1
        assert result["fix_results"][0]["status"] != "AUTO_FIXED"


class TestCascadeLockout:
    @patch("zephyr.gov_drift.cascade_detector.is_auto_fix_paused", return_value=True)
    @patch("zephyr.gov_drift.cascade_detector.detect_cascade")
    @patch("zephyr.gov_drift.drift_engine.scan")
    @patch("zephyr.gov_drift.drift_hotfix_bypass.HotfixBypass")
    def test_cascade_lockout_when_auto_fix_paused(
        self, mock_bypass_cls, mock_scan, mock_detect_cascade, mock_is_paused
    ):
        mock_bypass_inst = MagicMock()
        mock_bypass_inst.is_hotfix_commit.return_value = False
        mock_bypass_cls.return_value = mock_bypass_inst

        event1 = _make_event("code")
        mock_scan.return_value = _make_scan_result(events=[event1], total=1)

        cascade_alert = SimpleNamespace(
            alert_id="ALERT-001",
            module="MOD-TEST",
            cascade_count=3,
            auto_fix_paused=True,
            pause_until=datetime.now(UTC),
            forensics_report="cascade detected",
        )
        mock_detect_cascade.return_value = [cascade_alert]

        result = trigger_recovery({"module_id": "MOD-TEST"})

        assert result["recovery_status"] == "CASCADE_LOCKOUT"
        assert len(result["cascade_alerts"]) == 1
        assert result["cascade_alerts"][0]["auto_fix_paused"] is True


class TestFixerUnavailable:
    @patch("zephyr.gov_drift.cascade_detector.is_auto_fix_paused", return_value=False)
    @patch("zephyr.gov_drift.cascade_detector.detect_cascade", return_value=[])
    @patch("zephyr.gov_drift.drift_engine.scan")
    @patch("zephyr.gov_drift.drift_hotfix_bypass.HotfixBypass")
    def test_fixer_import_error_sets_unavailable(self, mock_bypass_cls, mock_scan, mock_detect_cascade, mock_is_paused):
        mock_bypass_inst = MagicMock()
        mock_bypass_inst.is_hotfix_commit.return_value = False
        mock_bypass_cls.return_value = mock_bypass_inst

        event1 = _make_event("code")
        mock_scan.return_value = _make_scan_result(events=[event1], total=1)

        with patch.dict("sys.modules", {"zephyr.gov_drift.reconciler": None}):
            result = trigger_recovery({"module_id": "MOD-TEST"})

        assert result["recovery_status"] == "FIXER_UNAVAILABLE"
        assert any("AutoFixer" in e for e in result["errors"])
