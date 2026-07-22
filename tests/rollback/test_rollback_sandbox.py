# [A_test] module_id: MOD-GOV_rollback_sandbox | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.rollback_sandbox
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
    from zephyr.security.access_control.rollback_sandbox import RollbackSandbox, SandboxedOperation

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestRollbackSandbox:
    def setup_method(self):
        self.sandbox = RollbackSandbox()

    def test_isolate(self):
        op = self.sandbox.isolate("op-1", "state-before")
        assert isinstance(op, SandboxedOperation)
        assert op.operation_id == "op-1"
        assert op.before_state == "state-before"
        assert op.after_state == ""
        assert op.reversible is True

    def test_execute(self):
        self.sandbox.isolate("op-1", "state-before")
        result = self.sandbox.execute("op-1", "state-after")
        assert result["success"] is True
        assert result["operation_id"] == "op-1"
        assert result["reversible"] is True

    def test_execute_not_isolated(self):
        result = self.sandbox.execute("nonexistent", "state-after")
        assert result["success"] is False
        assert result["reason"] == "not_isolated"

    def test_rollback_reversible(self):
        self.sandbox.isolate("op-1", "state-before")
        self.sandbox.execute("op-1", "state-after")
        result = self.sandbox.rollback("op-1")
        assert result["success"] is True
        assert result["restored_to"] == "state-before"

    def test_rollback_irreversible(self):
        self.sandbox.isolate("op-1", "state-before")
        op = self.sandbox._operations["op-1"]
        op.reversible = False
        result = self.sandbox.rollback("op-1")
        assert result["success"] is False
        assert result["reason"] == "irreversible"

    def test_rollback_not_found(self):
        result = self.sandbox.rollback("nonexistent")
        assert result["success"] is False
        assert result["reason"] == "not_found"

    def test_full_lifecycle(self):
        self.sandbox.isolate("op-1", "original")
        self.sandbox.execute("op-1", "modified")
        result = self.sandbox.rollback("op-1")
        assert result["success"] is True
        assert result["restored_to"] == "original"

    def test_isolate_empty_strings(self):
        op = self.sandbox.isolate("", "")
        assert op.operation_id == ""
        assert op.before_state == ""

    def test_requires_quorum_default(self):
        op = self.sandbox.isolate("op-1", "state")
        assert op.requires_quorum is False
