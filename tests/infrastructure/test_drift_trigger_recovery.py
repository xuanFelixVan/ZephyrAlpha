# [A_test] module_id: SRC-TST-0152 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-309 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.infrastructure.test_drift_trigger_recovery
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Trigger Router → Drift Recovery 集成测试
==========================================
验证 trigger_router.yaml drift_detected 事件能正确触发
zephyr.governance.drift_detection.drift_detector.trigger_recovery 完成恢复闭环。

覆盖场景：
  1. trigger_recovery 可被 trigger_router 正确导入
  2. 无漂移时返回 NO_DRIFT_FOUND
  3. Hotfix 旁路 [HOTFIX] commit
  4. 级联锁定 CASCADE_LOCKOUT
  5. 修复失败兜底回滚 MANUAL_REQUIRED
  6. handle_drift_detected 真实调用链（非 fallback stub）
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch


def test_trigger_recovery_importable():
    from zephyr.governance.drift_detection.drift_detector import trigger_recovery

    assert callable(trigger_recovery)


def test_trigger_recovery_via_gates_init():
    from zephyr.governance.rule_enforcement import trigger_recovery

    assert callable(trigger_recovery)


def test_handle_drift_detected_uses_trigger_recovery():
    from zephyr.orchestrator.execution.trigger_router import handle_drift_detected

    assert callable(handle_drift_detected)

    payload = {"module_id": "MOD-INF-023", "changed_files": [], "commit_message": ""}

    with patch("zephyr.governance.drift_detection.drift_detector.trigger_recovery") as mock_recovery:
        mock_recovery.return_value = {
            "recovery_id": "test-123",
            "recovery_status": "NO_DRIFT_FOUND",
        }
        result = handle_drift_detected(payload)
        mock_recovery.assert_called_once_with(payload)
        assert result["handler"] == "drift_detected"
        assert result["phase"] == "operational"


def test_handle_drift_detected_fallback_on_import_error():
    from zephyr.orchestrator.execution.trigger_router import handle_drift_detected

    payload = {"module_id": "MOD-INF-023"}

    with (
        patch(
            "zephyr.governance.drift_detection.drift_detector.trigger_recovery",
            side_effect=ImportError("test import error"),
        ),
        patch(
            "zephyr.trading.orchestrator.trigger_router._stub_response",
            return_value={"stub": True},
        ),
    ):
        result = handle_drift_detected(payload)
        assert result.get("stub") is True or "drift_detected" in str(result)


def test_trigger_recovery_hotfix_bypass():
    from zephyr.governance.drift_detection.drift_detector import trigger_recovery

    payload = {
        "module_id": "MOD-INF-023",
        "commit_message": "[HOTFIX] critical production fix",
        "changed_files": [],
    }

    with patch(
        "zephyr.governance.drift_detection.drift_hotfix_bypass.HotfixBypass.is_hotfix_commit",
        return_value=True,
    ):
        result = trigger_recovery(payload)
        assert result["hotfix_bypass"] is True
        assert result["recovery_status"] == "HOTFIX_BYPASSED"


def test_trigger_recovery_no_drift():
    from zephyr.governance.drift_detection.drift_detector import trigger_recovery

    mock_scan_result = MagicMock()
    mock_scan_result.scan_id = uuid.uuid4()
    mock_scan_result.detectors_run = 5
    mock_scan_result.total_drift_events = 0
    mock_scan_result.storm_mode_triggered = False
    mock_scan_result.events = []

    payload = {"module_id": "MOD-INF-023", "changed_files": []}

    with (
        patch("zephyr.governance.drift_detection.drift_engine.scan", return_value=mock_scan_result),
        patch(
            "zephyr.governance.drift_detection.drift_hotfix_bypass.HotfixBypass.is_hotfix_commit",
            return_value=False,
        ),
    ):
        result = trigger_recovery(payload)
        assert result["recovery_status"] == "NO_DRIFT_FOUND"
        assert result["scan_result"]["total_drift_events"] == 0


def test_trigger_recovery_cascade_lockout():
    from zephyr.governance.drift_detection.drift_detector import trigger_recovery

    mock_event = MagicMock()
    mock_event.event_id = uuid.uuid4()
    mock_event.drift_dimension = "D5_blueprint_code_sync"
    mock_event.created_at = datetime.now(UTC)

    mock_scan_result = MagicMock()
    mock_scan_result.scan_id = uuid.uuid4()
    mock_scan_result.detectors_run = 5
    mock_scan_result.total_drift_events = 1
    mock_scan_result.storm_mode_triggered = False
    mock_scan_result.events = [mock_event]

    payload = {"module_id": "MOD-INF-023", "changed_files": []}

    with (
        patch("zephyr.governance.drift_detection.drift_engine.scan", return_value=mock_scan_result),
        patch(
            "zephyr.governance.drift_detection.drift_hotfix_bypass.HotfixBypass.is_hotfix_commit",
            return_value=False,
        ),
        patch(
            "zephyr.governance.drift_detection.cascade_detector.detect_cascade",
            return_value=[],
        ),
        patch(
            "zephyr.governance.drift_detection.cascade_detector.is_auto_fix_paused",
            return_value=True,
        ),
    ):
        result = trigger_recovery(payload)
        assert result["recovery_status"] == "CASCADE_LOCKOUT"


def test_trigger_recovery_auto_fix_success():
    from zephyr.governance.drift_detection.drift_detector import trigger_recovery

    mock_event = MagicMock()
    mock_event.event_id = uuid.uuid4()
    mock_event.drift_dimension = "D5_blueprint_code_sync"
    mock_event.created_at = datetime.now(UTC)

    mock_scan_result = MagicMock()
    mock_scan_result.scan_id = uuid.uuid4()
    mock_scan_result.detectors_run = 5
    mock_scan_result.total_drift_events = 1
    mock_scan_result.storm_mode_triggered = False
    mock_scan_result.events = [mock_event]

    payload = {"module_id": "MOD-INF-023", "changed_files": []}

    with (
        patch("zephyr.governance.drift_detection.drift_engine.scan", return_value=mock_scan_result),
        patch(
            "zephyr.governance.drift_detection.drift_hotfix_bypass.HotfixBypass.is_hotfix_commit",
            return_value=False,
        ),
        patch(
            "zephyr.governance.drift_detection.cascade_detector.detect_cascade",
            return_value=[],
        ),
        patch(
            "zephyr.governance.drift_detection.cascade_detector.is_auto_fix_paused",
            return_value=False,
        ),
        patch(
            "zephyr.governance.drift_detection.reconciler.AutoFixer",
        ) as MockAutoFixer,
    ):
        mock_fixer = MockAutoFixer.return_value
        mock_fixer.auto_fix.return_value = True
        result = trigger_recovery(payload)
        assert result["recovery_status"] == "FULLY_RECOVERED"
        assert len(result["fix_results"]) == 1
        assert result["fix_results"][0]["status"] == "AUTO_FIXED"


def test_trigger_recovery_auto_fix_failure_fallback():
    from zephyr.governance.drift_detection.drift_detector import trigger_recovery

    mock_event = MagicMock()
    mock_event.event_id = uuid.uuid4()
    mock_event.drift_dimension = "D5_unknown_dimension"
    mock_event.created_at = datetime.now(UTC)
    mock_event.auto_fixable = False

    mock_scan_result = MagicMock()
    mock_scan_result.scan_id = uuid.uuid4()
    mock_scan_result.detectors_run = 5
    mock_scan_result.total_drift_events = 1
    mock_scan_result.storm_mode_triggered = False
    mock_scan_result.events = [mock_event]

    payload = {"module_id": "MOD-INF-023", "changed_files": []}

    with (
        patch("zephyr.governance.drift_detection.drift_engine.scan", return_value=mock_scan_result),
        patch(
            "zephyr.governance.drift_detection.drift_hotfix_bypass.HotfixBypass.is_hotfix_commit",
            return_value=False,
        ),
        patch(
            "zephyr.governance.drift_detection.cascade_detector.detect_cascade",
            return_value=[],
        ),
        patch(
            "zephyr.governance.drift_detection.cascade_detector.is_auto_fix_paused",
            return_value=False,
        ),
        patch(
            "zephyr.governance.drift_detection.reconciler.AutoFixer",
        ) as MockAutoFixer,
    ):
        mock_fixer = MockAutoFixer.return_value
        mock_fixer.auto_fix.return_value = False
        result = trigger_recovery(payload)
        assert result["recovery_status"] == "RECOVERY_FAILED"
        assert len(result["fix_results"]) == 1
        assert result["fix_results"][0]["status"] in (
            "MANUAL_REQUIRED",
            "FALLBACK_ERROR",
        )
