# [A_test] module_id: SRC-TST-0453 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_bridge
# [INVARIANTS] write_to_core returns None when writer unavailable
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_bridge.py -q
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock, patch

from zephyr.gov_audit.bridge import _AVAILABLE, _get_writer, write_to_core


class TestWriteToCoreUnavailable:
    def test_returns_none_when_writer_unavailable(self):
        with patch("zephyr.gov_audit.bridge._get_writer", return_value=None):
            result = write_to_core("test_event", {"key": "value"})
            assert result is None

    def test_returns_none_on_writer_exception(self):
        mock_writer = MagicMock()
        mock_writer.write.side_effect = RuntimeError("write failed")
        with patch("zephyr.gov_audit.bridge._get_writer", return_value=mock_writer):
            result = write_to_core("test_event", {"key": "value"})
            assert result is None


class TestWriteToCoreSuccess:
    def test_returns_chain_hash_on_success(self):
        mock_writer = MagicMock()
        mock_writer.write.return_value = "abc123hash"
        with patch("zephyr.gov_audit.bridge._get_writer", return_value=mock_writer):
            result = write_to_core("test_event", {"key": "value"})
            assert result == "abc123hash"

    def test_sets_event_type_in_event(self):
        mock_writer = MagicMock()
        mock_writer.write.return_value = "hash"
        with patch("zephyr.gov_audit.bridge._get_writer", return_value=mock_writer):
            write_to_core("gate_override", {"gate_id": "G0"})
            call_args = mock_writer.write.call_args[0][0]
            assert call_args["event_type"] == "gate_override"

    def test_adds_agent_id_from_event_type_when_missing(self):
        mock_writer = MagicMock()
        mock_writer.write.return_value = "hash"
        with patch("zephyr.gov_audit.bridge._get_writer", return_value=mock_writer):
            write_to_core("gate_override", {"gate_id": "G0"})
            call_args = mock_writer.write.call_args[0][0]
            assert call_args["agent_id"] == "gate_override"

    def test_preserves_existing_agent_id(self):
        mock_writer = MagicMock()
        mock_writer.write.return_value = "hash"
        with patch("zephyr.gov_audit.bridge._get_writer", return_value=mock_writer):
            write_to_core("gate_override", {"agent_id": "agent-1", "gate_id": "G0"})
            call_args = mock_writer.write.call_args[0][0]
            assert call_args["agent_id"] == "agent-1"

    def test_event_type_injection_does_not_mutate_original(self):
        original = {"key": "value"}
        mock_writer = MagicMock()
        mock_writer.write.return_value = "hash"
        with patch("zephyr.gov_audit.bridge._get_writer", return_value=mock_writer):
            write_to_core("injected_type", original)
            assert "event_type" not in original


class TestGetWriterCaching:
    def test_get_writer_caches_instance(self):
        import zephyr.gov_audit.bridge as bridge_mod

        original_writer = bridge_mod._WRITER
        try:
            bridge_mod._WRITER = None
            mock_instance = MagicMock()
            with (
                patch("zephyr.gov_audit.bridge._AVAILABLE", True),
                patch("zephyr.gov_audit.bridge._CoreWriter", return_value=mock_instance, create=True),
            ):
                w1 = _get_writer()
                w2 = _get_writer()
                assert w1 is w2
        finally:
            bridge_mod._WRITER = original_writer

    def test_get_writer_returns_none_when_unavailable(self):
        with patch("zephyr.gov_audit.bridge._AVAILABLE", False):
            result = _get_writer()
            assert result is None


class TestAvailableFlag:
    def test_available_is_boolean(self):
        assert isinstance(_AVAILABLE, bool)
