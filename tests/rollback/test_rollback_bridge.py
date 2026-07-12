# [A_test] module_id: SRC-TST-1475 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_rollback_bridge
# [INVARIANTS] 漂移→回滚桥接不可禁用
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_rollback_bridge.py
# [TTL] task_bound


from zephyr.gov_drift.rollback_bridge import DriftRollbackBridge


class TestDriftRollbackBridgeInstantiation:
    def test_instantiation(self):
        bridge = DriftRollbackBridge()
        assert bridge is not None


class TestOnDriftDetected:
    def test_high_severity_triggers_rollback(self):
        bridge = DriftRollbackBridge()
        result = bridge.on_drift_detected("agent-1", "behavioral", "HIGH")
        assert result["triggered"] is True
        assert result["action"] == "ROLLBACK"
        assert result["agent_id"] == "agent-1"
        assert result["drift_type"] == "behavioral"

    def test_critical_severity_triggers_rollback(self):
        bridge = DriftRollbackBridge()
        result = bridge.on_drift_detected("agent-2", "config", "CRITICAL")
        assert result["triggered"] is True
        assert result["action"] == "ROLLBACK"

    def test_low_severity_observes(self):
        bridge = DriftRollbackBridge()
        result = bridge.on_drift_detected("agent-3", "behavioral", "LOW")
        assert result["triggered"] is False
        assert result["action"] == "OBSERVE"

    def test_medium_severity_observes(self):
        bridge = DriftRollbackBridge()
        result = bridge.on_drift_detected("agent-4", "config", "MEDIUM")
        assert result["triggered"] is False
        assert result["action"] == "OBSERVE"

    def test_empty_agent_id(self):
        bridge = DriftRollbackBridge()
        result = bridge.on_drift_detected("", "behavioral", "HIGH")
        assert result["triggered"] is True
        assert result["agent_id"] == ""

    def test_empty_drift_type(self):
        bridge = DriftRollbackBridge()
        result = bridge.on_drift_detected("agent-5", "", "CRITICAL")
        assert result["triggered"] is True
        assert result["drift_type"] == ""

    def test_case_sensitive_severity(self):
        bridge = DriftRollbackBridge()
        result = bridge.on_drift_detected("agent-6", "behavioral", "high")
        assert result["triggered"] is False
        assert result["action"] == "OBSERVE"

    def test_unknown_severity_observes(self):
        bridge = DriftRollbackBridge()
        result = bridge.on_drift_detected("agent-7", "behavioral", "UNKNOWN")
        assert result["triggered"] is False
        assert result["action"] == "OBSERVE"

    def test_result_has_all_keys(self):
        bridge = DriftRollbackBridge()
        result = bridge.on_drift_detected("agent-8", "behavioral", "HIGH")
        assert set(result.keys()) == {"triggered", "agent_id", "drift_type", "action"}
