# [A_test] module_id: SRC-TST-1002 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_scheduler_safety
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.scheduler_safety
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_scheduler_safety.py
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock

from zephyr.feedback_loop.scheduler_safety import SafetyGateManager


class TestSafetyGateManagerInstantiation:
    def test_creates_with_defaults(self):
        manager = SafetyGateManager()
        assert manager.numerical_guard is not None
        assert manager.temporal_guard is not None
        assert manager.wireheading_prevention is not None
        assert manager.deployment_suppression is not None
        assert manager.config_reload_guard is not None
        assert manager.boot_attestation is not None


class TestRunSafetyGates:
    def test_returns_dict_of_bools(self):
        manager = SafetyGateManager()
        manager.wireheading_prevention = MagicMock()
        manager.wireheading_prevention.validate_metric = MagicMock(return_value=True)
        manager.deployment_suppression = MagicMock()
        manager.deployment_suppression.check = MagicMock(return_value={"allowed": True})
        anomaly = MagicMock()
        anomaly.evidence = {"metric_name": "cpu", "value": 0.5}
        diagnosis = MagicMock()
        result = manager.run_safety_gates(anomaly, diagnosis)
        assert isinstance(result, dict)
        for key, value in result.items():
            assert isinstance(value, bool), f"Key {key} has non-bool value: {value}"

    def test_contains_expected_gates(self):
        manager = SafetyGateManager()
        manager.wireheading_prevention = MagicMock()
        manager.wireheading_prevention.validate_metric = MagicMock(return_value=True)
        manager.deployment_suppression = MagicMock()
        manager.deployment_suppression.check = MagicMock(return_value={"allowed": True})
        anomaly = MagicMock()
        anomaly.evidence = {"metric_name": "cpu", "value": 0.5}
        diagnosis = MagicMock()
        result = manager.run_safety_gates(anomaly, diagnosis)
        expected = [
            "numerical_stability",
            "temporal_integrity",
            "wireheading",
            "deployment_suppression",
            "config_consistency",
        ]
        for gate in expected:
            assert gate in result, f"Missing gate: {gate}"

    def test_boundary_none_evidence(self):
        manager = SafetyGateManager()
        manager.wireheading_prevention = MagicMock()
        manager.wireheading_prevention.validate_metric = MagicMock(return_value=True)
        manager.deployment_suppression = MagicMock()
        manager.deployment_suppression.check = MagicMock(return_value={"allowed": True})
        anomaly = MagicMock()
        anomaly.evidence = {}
        diagnosis = MagicMock()
        result = manager.run_safety_gates(anomaly, diagnosis)
        assert isinstance(result, dict)
