# [A_test] module_id: SRC-TST-0369 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_auditor
# [INVARIANTS] AuditWriter.write mocked for isolation
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock, patch

from zephyr.infrastructure.rollback.auditor import RollbackAuditor


class TestRollbackAuditorInstantiation:
    def test_instantiation(self):
        auditor = RollbackAuditor()
        assert auditor is not None

    def test_has_log_rollback_method(self):
        auditor = RollbackAuditor()
        assert callable(getattr(auditor, "log_rollback", None))


class TestLogRollback:
    @patch("zephyr.gov_audit.contracts.AuditWriter")
    def test_log_rollback_calls_audit_writer(self, mock_writer_cls):
        mock_write = MagicMock(return_value={"status": "ok"})
        mock_writer_cls.write = mock_write
        auditor = RollbackAuditor()
        result = auditor.log_rollback(
            agent_id="agent-1",
            resource="src/main.py",
            rollback_target="abc123",
            session_id="sess-1",
        )
        mock_write.assert_called_once_with(
            agent_id="agent-1",
            permission="rollback",
            resource="src/main.py",
            decision_basis="Rollback→Audit: abc123",
            session_id="sess-1",
            granted=True,
            metadata={"rollback_target": "abc123"},
        )
        assert result == {"status": "ok"}

    @patch("zephyr.gov_audit.contracts.AuditWriter")
    def test_log_rollback_default_session_id(self, mock_writer_cls):
        mock_write = MagicMock(return_value={"status": "ok"})
        mock_writer_cls.write = mock_write
        auditor = RollbackAuditor()
        auditor.log_rollback(
            agent_id="agent-2",
            resource="config.yaml",
            rollback_target="def456",
        )
        call_kwargs = mock_write.call_args
        assert call_kwargs[1]["session_id"] == ""

    @patch("zephyr.gov_audit.contracts.AuditWriter")
    def test_log_rollback_passes_rollback_target_metadata(self, mock_writer_cls):
        mock_write = MagicMock(return_value={"event_id": "ev-1"})
        mock_writer_cls.write = mock_write
        auditor = RollbackAuditor()
        result = auditor.log_rollback(
            agent_id="agent-3",
            resource="db.sqlite",
            rollback_target="v2.0",
        )
        call_kwargs = mock_write.call_args
        assert call_kwargs[1]["metadata"] == {"rollback_target": "v2.0"}

    @patch("zephyr.gov_audit.contracts.AuditWriter")
    def test_log_rollback_granted_is_true(self, mock_writer_cls):
        mock_write = MagicMock(return_value={})
        mock_writer_cls.write = mock_write
        auditor = RollbackAuditor()
        auditor.log_rollback(
            agent_id="agent-4",
            resource="x.py",
            rollback_target="r1",
        )
        call_kwargs = mock_write.call_args
        assert call_kwargs[1]["granted"] is True

    @patch("zephyr.gov_audit.contracts.AuditWriter")
    def test_log_rollback_permission_is_rollback(self, mock_writer_cls):
        mock_write = MagicMock(return_value={})
        mock_writer_cls.write = mock_write
        auditor = RollbackAuditor()
        auditor.log_rollback(
            agent_id="agent-5",
            resource="y.py",
            rollback_target="r2",
        )
        call_kwargs = mock_write.call_args
        assert call_kwargs[1]["permission"] == "rollback"

    @patch("zephyr.gov_audit.contracts.AuditWriter")
    def test_log_rollback_decision_basis_format(self, mock_writer_cls):
        mock_write = MagicMock(return_value={})
        mock_writer_cls.write = mock_write
        auditor = RollbackAuditor()
        auditor.log_rollback(
            agent_id="agent-6",
            resource="z.py",
            rollback_target="commit-sha",
        )
        call_kwargs = mock_write.call_args
        assert call_kwargs[1]["decision_basis"] == "Rollback→Audit: commit-sha"

    @patch("zephyr.gov_audit.contracts.AuditWriter")
    def test_log_rollback_returns_writer_result(self, mock_writer_cls):
        expected = {"event_id": "ev-99", "written": True}
        mock_write = MagicMock(return_value=expected)
        mock_writer_cls.write = mock_write
        auditor = RollbackAuditor()
        result = auditor.log_rollback(
            agent_id="agent-7",
            resource="w.py",
            rollback_target="r3",
        )
        assert result == expected

    @patch("zephyr.gov_audit.contracts.AuditWriter")
    def test_log_rollback_empty_strings(self, mock_writer_cls):
        mock_write = MagicMock(return_value={})
        mock_writer_cls.write = mock_write
        auditor = RollbackAuditor()
        result = auditor.log_rollback(
            agent_id="",
            resource="",
            rollback_target="",
            session_id="",
        )
        assert result == {}
        call_kwargs = mock_write.call_args
        assert call_kwargs[1]["agent_id"] == ""
        assert call_kwargs[1]["resource"] == ""
        assert call_kwargs[1]["decision_basis"] == "Rollback→Audit: "
