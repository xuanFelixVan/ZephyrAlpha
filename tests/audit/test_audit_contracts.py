# [A_test] module_id: SRC-TST-0347 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_audit_contracts
# [INVARIANTS] AuditWriter.write delegates to core writer
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass; exit non-zero on fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock, patch

from zephyr.gov_audit.contracts import AuditWriter


class TestAuditWriterWrite:
    def test_write_returns_event_with_chain_hash(self):
        mock_core_writer = MagicMock()
        mock_core_writer.write.return_value = "chain_hash_123"
        with patch("zephyr.governance.audit_trail.contracts._get_writer", return_value=mock_core_writer):
            result = AuditWriter.write(
                agent_id="agent-1",
                permission="write",
                resource="file.py",
                decision_basis="authorized",
            )
        assert result["chain_hash"] == "chain_hash_123"
        assert result["agent_id"] == "agent-1"
        assert result["permission"] == "write"
        assert result["resource"] == "file.py"

    def test_write_uses_custom_timestamp(self):
        mock_core_writer = MagicMock()
        mock_core_writer.write.return_value = "hash"
        with patch("zephyr.governance.audit_trail.contracts._get_writer", return_value=mock_core_writer):
            result = AuditWriter.write(
                agent_id="agent-1",
                permission="read",
                resource="file.py",
                decision_basis="authorized",
                timestamp="2026-01-01T00:00:00Z",
            )
        assert result["timestamp"] == "2026-01-01T00:00:00Z"

    def test_write_generates_timestamp_when_empty(self):
        mock_core_writer = MagicMock()
        mock_core_writer.write.return_value = "hash"
        with patch("zephyr.governance.audit_trail.contracts._get_writer", return_value=mock_core_writer):
            result = AuditWriter.write(
                agent_id="agent-1",
                permission="read",
                resource="file.py",
                decision_basis="authorized",
            )
        assert result["timestamp"] != ""

    def test_write_with_granted_false(self):
        mock_core_writer = MagicMock()
        mock_core_writer.write.return_value = "hash"
        with patch("zephyr.governance.audit_trail.contracts._get_writer", return_value=mock_core_writer):
            result = AuditWriter.write(
                agent_id="agent-1",
                permission="admin",
                resource="system",
                decision_basis="denied",
                granted=False,
            )
        assert result["granted"] is False

    def test_write_with_metadata(self):
        mock_core_writer = MagicMock()
        mock_core_writer.write.return_value = "hash"
        with patch("zephyr.governance.audit_trail.contracts._get_writer", return_value=mock_core_writer):
            result = AuditWriter.write(
                agent_id="agent-1",
                permission="write",
                resource="file.py",
                decision_basis="authorized",
                metadata={"source": "test"},
            )
        assert result["metadata"] == {"source": "test"}

    def test_write_default_metadata_empty(self):
        mock_core_writer = MagicMock()
        mock_core_writer.write.return_value = "hash"
        with patch("zephyr.governance.audit_trail.contracts._get_writer", return_value=mock_core_writer):
            result = AuditWriter.write(
                agent_id="agent-1",
                permission="write",
                resource="file.py",
                decision_basis="authorized",
            )
        assert result["metadata"] == {}

    def test_write_custom_event_type(self):
        mock_core_writer = MagicMock()
        mock_core_writer.write.return_value = "hash"
        with patch("zephyr.governance.audit_trail.contracts._get_writer", return_value=mock_core_writer):
            result = AuditWriter.write(
                agent_id="agent-1",
                permission="write",
                resource="file.py",
                decision_basis="authorized",
                event_type="custom_event",
            )
        assert result["event_type"] == "custom_event"
