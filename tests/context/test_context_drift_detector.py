# [A_test] module_id: MOD-GOV_context_drift_detector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.detectors.context_drift_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.access_control.detectors.context_drift_detector import ContextDriftDetector

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")


class TestContextDriftDetectorRecord:
    def test_record_operation(self):
        d = ContextDriftDetector()
        d.record_operation("agent-1", "read")
        assert "agent-1" in d._contexts
        assert d._contexts["agent-1"] == ["read"]

    def test_record_multiple_operations(self):
        d = ContextDriftDetector()
        d.record_operation("agent-2", "read")
        d.record_operation("agent-2", "write")
        assert len(d._contexts["agent-2"]) == 2

    def test_record_multiple_agents(self):
        d = ContextDriftDetector()
        d.record_operation("agent-a", "read")
        d.record_operation("agent-b", "write")
        assert "agent-a" in d._contexts
        assert "agent-b" in d._contexts


class TestContextDriftDetectorScopeCreep:
    def test_no_drift(self):
        d = ContextDriftDetector()
        d.record_operation("agent-1", "read")
        d.record_operation("agent-1", "write")
        result = d.detect_scope_creep("agent-1", ["read", "write"])
        assert result["exceeded"] is False
        assert result["violations"] == 0

    def test_drift_detected(self):
        d = ContextDriftDetector()
        d.record_operation("agent-2", "read")
        d.record_operation("agent-2", "nuke")
        d.record_operation("agent-2", "purge")
        result = d.detect_scope_creep("agent-2", ["read"])
        assert result["exceeded"] is True
        assert result["violations"] == 2

    def test_no_operations_for_agent(self):
        d = ContextDriftDetector()
        result = d.detect_scope_creep("unknown-agent", ["read"])
        assert result["total_ops"] == 0
        assert result["violations"] == 0
        assert result["exceeded"] is False

    def test_empty_declared_scope(self):
        d = ContextDriftDetector()
        d.record_operation("agent-3", "read")
        result = d.detect_scope_creep("agent-3", [])
        assert result["exceeded"] is True

    def test_window_parameter(self):
        d = ContextDriftDetector()
        for i in range(100):
            d.record_operation("agent-4", "read")
        result = d.detect_scope_creep("agent-4", ["read"], window=10)
        assert result["total_ops"] == 10

    def test_violation_ratio_calculation(self):
        d = ContextDriftDetector()
        d.record_operation("agent-5", "read")
        d.record_operation("agent-5", "write")
        d.record_operation("agent-5", "nuke")
        result = d.detect_scope_creep("agent-5", ["read", "write"])
        assert result["violation_ratio"] == pytest.approx(1.0 / 3.0)

    def test_recent_violations_limited(self):
        d = ContextDriftDetector()
        for _ in range(10):
            d.record_operation("agent-6", "bad_op")
        result = d.detect_scope_creep("agent-6", ["read"])
        assert len(result["recent_violations"]) <= 5


class TestContextDriftDetectorReset:
    def test_reset_clears_agent(self):
        d = ContextDriftDetector()
        d.record_operation("agent-1", "read")
        d.reset("agent-1")
        assert "agent-1" not in d._contexts

    def test_reset_nonexistent_agent(self):
        d = ContextDriftDetector()
        d.reset("nonexistent")

    def test_reset_then_record(self):
        d = ContextDriftDetector()
        d.record_operation("agent-2", "read")
        d.reset("agent-2")
        d.record_operation("agent-2", "write")
        assert d._contexts["agent-2"] == ["write"]
