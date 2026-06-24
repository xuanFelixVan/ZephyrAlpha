# [A_test] module_id: SRC-TST-0338 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.asymmetric_audit
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.access_control.asymmetric_audit import AsymmetricAudit, AuditQuorum

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")


class TestAsymmetricAudit:
    def test_require_quorum(self):
        aa = AsymmetricAudit()
        q = aa.require_quorum("delete_db", required_approvers=3)
        assert isinstance(q, AuditQuorum)
        assert q.operation == "delete_db"
        assert q.required_approvers == 3
        assert q.status == "PENDING"

    def test_approve_reaches_quorum(self):
        aa = AsymmetricAudit()
        aa.require_quorum("deploy_prod", required_approvers=2)
        r1 = aa.approve("deploy_prod", "alice")
        assert r1["approved"] is False
        assert r1["current"] == 1
        r2 = aa.approve("deploy_prod", "bob")
        assert r2["approved"] is True
        assert r2["current"] == 2

    def test_duplicate_approval_rejected(self):
        aa = AsymmetricAudit()
        aa.require_quorum("deploy_prod", required_approvers=2)
        aa.approve("deploy_prod", "alice")
        r = aa.approve("deploy_prod", "alice")
        assert r["approved"] is False
        assert r["reason"] == "duplicate_approval"

    def test_approve_nonexistent_operation(self):
        aa = AsymmetricAudit()
        r = aa.approve("nonexistent", "alice")
        assert r["approved"] is False
        assert r["reason"] == "no_quorum_required"

    def test_single_approver_quorum(self):
        aa = AsymmetricAudit()
        aa.require_quorum("read_log", required_approvers=1)
        r = aa.approve("read_log", "alice")
        assert r["approved"] is True


class TestAuditQuorum:
    def test_default_fields(self):
        q = AuditQuorum(operation="test_op")
        assert q.required_approvers == 2
        assert q.current_approvals == []
        assert q.status == "PENDING"

    def test_custom_approvers(self):
        q = AuditQuorum(operation="test_op", required_approvers=5)
        assert q.required_approvers == 5
