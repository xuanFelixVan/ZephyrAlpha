# [A_test] module_id: SRC-TST-0455 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_bridges_contracts
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock, patch

from zephyr.gov_audit.contracts import AuditWriter


class TestAuditWriter:
    def test_write_basic(self, tmp_path):
        with patch("zephyr.governance.audit_trail.contracts._CoreAuditWriter") as mock_cls:
            mock_writer = MagicMock()
            mock_writer.write.return_value = "abc123"
            mock_cls.return_value = mock_writer
            result = AuditWriter.write(
                agent_id="agent-1",
                permission="read",
                resource="/tmp/f.py",
                decision_basis="RBAC check passed",
            )
            assert result["event_type"] == "rbac_decision"
            assert result["agent_id"] == "agent-1"
            assert result["permission"] == "read"
            assert result["resource"] == "/tmp/f.py"
            assert result["decision_basis"] == "RBAC check passed"
            assert result["granted"] is False
            assert "chain_hash" in result

    def test_write_with_granted(self, tmp_path):
        with patch("zephyr.governance.audit_trail.contracts._CoreAuditWriter") as mock_cls:
            mock_writer = MagicMock()
            mock_writer.write.return_value = "hash123"
            mock_cls.return_value = mock_writer
            result = AuditWriter.write(
                agent_id="agent-2",
                permission="write",
                resource="/tmp/out.py",
                decision_basis="Approved",
                granted=True,
            )
            assert result["granted"] is True

    def test_write_with_timestamp(self):
        with patch("zephyr.governance.audit_trail.contracts._CoreAuditWriter") as mock_cls:
            mock_writer = MagicMock()
            mock_writer.write.return_value = "hash"
            mock_cls.return_value = mock_writer
            result = AuditWriter.write(
                agent_id="a1",
                permission="read",
                resource="/tmp/f",
                decision_basis="ok",
                timestamp="2026-01-01T00:00:00Z",
            )
            assert result["timestamp"] == "2026-01-01T00:00:00Z"

    def test_write_with_session_id(self):
        with patch("zephyr.governance.audit_trail.contracts._CoreAuditWriter") as mock_cls:
            mock_writer = MagicMock()
            mock_writer.write.return_value = "hash"
            mock_cls.return_value = mock_writer
            result = AuditWriter.write(
                agent_id="a1",
                permission="read",
                resource="/tmp/f",
                decision_basis="ok",
                session_id="sess-1",
            )
            assert result["session_id"] == "sess-1"

    def test_write_with_metadata(self):
        with patch("zephyr.governance.audit_trail.contracts._CoreAuditWriter") as mock_cls:
            mock_writer = MagicMock()
            mock_writer.write.return_value = "hash"
            mock_cls.return_value = mock_writer
            meta = {"source": "test", "priority": "high"}
            result = AuditWriter.write(
                agent_id="a1",
                permission="read",
                resource="/tmp/f",
                decision_basis="ok",
                metadata=meta,
            )
            assert result["metadata"] == meta

    def test_write_default_metadata(self):
        with patch("zephyr.governance.audit_trail.contracts._CoreAuditWriter") as mock_cls:
            mock_writer = MagicMock()
            mock_writer.write.return_value = "hash"
            mock_cls.return_value = mock_writer
            result = AuditWriter.write(
                agent_id="a1",
                permission="read",
                resource="/tmp/f",
                decision_basis="ok",
            )
            assert result["metadata"] == {}

    def test_write_auto_timestamp(self):
        with patch("zephyr.governance.audit_trail.contracts._CoreAuditWriter") as mock_cls:
            mock_writer = MagicMock()
            mock_writer.write.return_value = "hash"
            mock_cls.return_value = mock_writer
            result = AuditWriter.write(
                agent_id="a1",
                permission="read",
                resource="/tmp/f",
                decision_basis="ok",
            )
            assert result["timestamp"] != ""
