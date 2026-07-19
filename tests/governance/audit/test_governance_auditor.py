# [A_test] module_id: SRC-TST-1068 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_governance_auditor
# [INVARIANTS] RollbackAuditor.log_rollback must delegate to AuditWriter.write
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] TypeError on wrong arg types; ValueError on empty strings
# [TESTS] tests/test_governance_auditor.py
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from zephyr.infrastructure.rollback.auditor import RollbackAuditor


class TestRollbackAuditorInstantiation:
    def test_can_instantiate(self):
        auditor = RollbackAuditor()
        assert auditor is not None

    def test_is_instance_of_rollback_auditor(self):
        auditor = RollbackAuditor()
        assert isinstance(auditor, RollbackAuditor)


class TestLogRollback:
    @patch("zephyr.infrastructure.rollback.auditor.AuditWriter")
    def test_log_rollback_returns_dict(self, mock_audit_writer_cls):
        mock_writer = MagicMock()
        mock_writer.write.return_value = {
            "event_type": "rbac_decision",
            "agent_id": "agent-1",
            "permission": "rollback",
            "resource": "file.py",
            "decision_basis": "Rollback→Audit: commit_abc",
            "timestamp": "2026-01-01T00:00:00+00:00",
            "session_id": "sess-1",
            "granted": True,
            "metadata": {"rollback_target": "commit_abc"},
            "chain_hash": "abc123",
        }
        mock_audit_writer_cls.write = mock_writer.write

        auditor = RollbackAuditor()
        result = auditor.log_rollback(
            agent_id="agent-1",
            resource="file.py",
            rollback_target="commit_abc",
            session_id="sess-1",
        )

        assert isinstance(result, dict)
        assert result["agent_id"] == "agent-1"
        assert result["permission"] == "rollback"
        assert result["granted"] is True

    @patch("zephyr.infrastructure.rollback.auditor.AuditWriter")
    def test_log_rollback_passes_rollback_target_in_metadata(self, mock_audit_writer_cls):
        mock_write = MagicMock(
            return_value={
                "event_type": "rbac_decision",
                "agent_id": "agent-2",
                "permission": "rollback",
                "resource": "src/main.py",
                "decision_basis": "Rollback→Audit: sha_xyz",
                "timestamp": "2026-01-01T00:00:00+00:00",
                "session_id": "",
                "granted": True,
                "metadata": {"rollback_target": "sha_xyz"},
                "chain_hash": "def456",
            }
        )
        mock_audit_writer_cls.write = mock_write

        auditor = RollbackAuditor()
        result = auditor.log_rollback(
            agent_id="agent-2",
            resource="src/main.py",
            rollback_target="sha_xyz",
        )

        mock_write.assert_called_once()
        call_kwargs = mock_write.call_args
        assert call_kwargs.kwargs["metadata"]["rollback_target"] == "sha_xyz"
        assert "Rollback->Audit: sha_xyz" in call_kwargs.kwargs["decision_basis"]

    @patch("zephyr.infrastructure.rollback.auditor.AuditWriter")
    def test_log_rollback_with_empty_session_id(self, mock_audit_writer_cls):
        mock_write = MagicMock(
            return_value={
                "event_type": "rbac_decision",
                "agent_id": "agent-3",
                "permission": "rollback",
                "resource": "mod.py",
                "decision_basis": "Rollback→Audit: target1",
                "timestamp": "2026-01-01T00:00:00+00:00",
                "session_id": "",
                "granted": True,
                "metadata": {"rollback_target": "target1"},
                "chain_hash": "ghi789",
            }
        )
        mock_audit_writer_cls.write = mock_write

        auditor = RollbackAuditor()
        result = auditor.log_rollback(
            agent_id="agent-3",
            resource="mod.py",
            rollback_target="target1",
            session_id="",
        )

        call_kwargs = mock_write.call_args.kwargs
        assert call_kwargs["session_id"] == ""


class TestLogRollbackBoundaryCases:
    @patch("zephyr.infrastructure.rollback.auditor.AuditWriter")
    def test_log_rollback_with_empty_agent_id(self, mock_audit_writer_cls):
        mock_write = MagicMock(
            return_value={
                "event_type": "rbac_decision",
                "agent_id": "",
                "permission": "rollback",
                "resource": "file.py",
                "decision_basis": "Rollback→Audit: t1",
                "timestamp": "2026-01-01T00:00:00+00:00",
                "session_id": "",
                "granted": True,
                "metadata": {"rollback_target": "t1"},
                "chain_hash": "x",
            }
        )
        mock_audit_writer_cls.write = mock_write

        auditor = RollbackAuditor()
        result = auditor.log_rollback(
            agent_id="",
            resource="file.py",
            rollback_target="t1",
        )

        assert result["agent_id"] == ""

    @patch("zephyr.infrastructure.rollback.auditor.AuditWriter")
    def test_log_rollback_with_empty_resource(self, mock_audit_writer_cls):
        mock_write = MagicMock(
            return_value={
                "event_type": "rbac_decision",
                "agent_id": "a1",
                "permission": "rollback",
                "resource": "",
                "decision_basis": "Rollback→Audit: t2",
                "timestamp": "2026-01-01T00:00:00+00:00",
                "session_id": "",
                "granted": True,
                "metadata": {"rollback_target": "t2"},
                "chain_hash": "y",
            }
        )
        mock_audit_writer_cls.write = mock_write

        auditor = RollbackAuditor()
        result = auditor.log_rollback(
            agent_id="a1",
            resource="",
            rollback_target="t2",
        )

        assert result["resource"] == ""

    @patch("zephyr.infrastructure.rollback.auditor.AuditWriter")
    def test_log_rollback_audit_writer_exception_propagates(self, mock_audit_writer_cls):
        mock_audit_writer_cls.write = MagicMock(side_effect=RuntimeError("audit chain broken"))

        auditor = RollbackAuditor()
        with pytest.raises(RuntimeError, match="audit chain broken"):
            auditor.log_rollback(
                agent_id="a1",
                resource="f.py",
                rollback_target="t3",
            )
