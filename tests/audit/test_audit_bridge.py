# [A_test] module_id: SRC-TST-0344 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_audit_bridge
# [INVARIANTS] write_to_core returns None when writer unavailable
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

from zephyr.gov_audit.bridge import write_to_core


class TestWriteToCore:
    def test_returns_none_when_writer_unavailable(self):
        with patch("zephyr.governance.audit_trail.bridge._get_writer", return_value=None):
            result = write_to_core("test_event", {"key": "value"})
            assert result is None

    def test_returns_chain_hash_on_success(self):
        mock_writer = MagicMock()
        mock_writer.write.return_value = "abc123hash"
        with patch("zephyr.governance.audit_trail.bridge._get_writer", return_value=mock_writer):
            result = write_to_core("test_event", {"key": "value"})
            assert result == "abc123hash"

    def test_sets_event_type_in_event(self):
        mock_writer = MagicMock()
        mock_writer.write.return_value = "hash"
        with patch("zephyr.governance.audit_trail.bridge._get_writer", return_value=mock_writer):
            write_to_core("gate_override", {"gate_id": "G0"})
            call_args = mock_writer.write.call_args[0][0]
            assert call_args["event_type"] == "gate_override"

    def test_adds_agent_id_from_event_type_when_missing(self):
        mock_writer = MagicMock()
        mock_writer.write.return_value = "hash"
        with patch("zephyr.governance.audit_trail.bridge._get_writer", return_value=mock_writer):
            write_to_core("gate_override", {"gate_id": "G0"})
            call_args = mock_writer.write.call_args[0][0]
            assert call_args["agent_id"] == "gate_override"

    def test_preserves_existing_agent_id(self):
        mock_writer = MagicMock()
        mock_writer.write.return_value = "hash"
        with patch("zephyr.governance.audit_trail.bridge._get_writer", return_value=mock_writer):
            write_to_core("gate_override", {"agent_id": "agent-1", "gate_id": "G0"})
            call_args = mock_writer.write.call_args[0][0]
            assert call_args["agent_id"] == "agent-1"

    def test_returns_none_on_writer_exception(self):
        mock_writer = MagicMock()
        mock_writer.write.side_effect = RuntimeError("write failed")
        with patch("zephyr.governance.audit_trail.bridge._get_writer", return_value=mock_writer):
            result = write_to_core("test_event", {"key": "value"})
            assert result is None
