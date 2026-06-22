# [A_test] module_id: SRC-TST-1220 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md | §3
# [MODULE] tests.test_legacy_auditor
# [INVARIANTS] Tests must not modify production state; All imports guarded by pytest.importorskip
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError → skip; AttributeError → fail
# [TESTS] self

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

legacy_auditor = pytest.importorskip(
    "zephyr.infrastructure.a2a_protocol.legacy_auditor",
    reason="legacy_auditor module not available",
)


class TestA2AAuditor:
    def test_instantiation(self):
        obj = legacy_auditor.A2AAuditor()
        assert obj is not None

    def test_log_message_returns_dict(self):
        with patch.object(legacy_auditor, "AuditWriter", create=True) as mock_aw:
            mock_aw.write = MagicMock(return_value={"agent_id": "a1", "granted": True})
            obj = legacy_auditor.A2AAuditor()
            result = obj.log_message("a1", "a2", "QUERY", "s1")
            assert isinstance(result, dict)

    def test_log_message_passes_correct_args(self):
        with patch.object(legacy_auditor, "AuditWriter", create=True) as mock_aw:
            mock_aw.write = MagicMock(return_value={"ok": True})
            obj = legacy_auditor.A2AAuditor()
            obj.log_message("agent_x", "agent_y", "COMMAND", "sess_1")
            mock_aw.write.assert_called_once_with(
                agent_id="agent_x",
                permission="a2a_message",
                resource="a2a://agent_y",
                decision_basis="A2A→Audit: COMMAND",
                session_id="sess_1",
                granted=True,
                metadata={"from": "agent_x", "to": "agent_y", "type": "COMMAND"},
            )

    def test_log_message_default_session_id(self):
        with patch.object(legacy_auditor, "AuditWriter", create=True) as mock_aw:
            mock_aw.write = MagicMock(return_value={"ok": True})
            obj = legacy_auditor.A2AAuditor()
            obj.log_message("a1", "a2", "NOTIFY")
            call_kwargs = mock_aw.write.call_args
            assert call_kwargs[1]["session_id"] == ""

    def test_log_message_empty_agents(self):
        with patch.object(legacy_auditor, "AuditWriter", create=True) as mock_aw:
            mock_aw.write = MagicMock(return_value={"ok": True})
            obj = legacy_auditor.A2AAuditor()
            result = obj.log_message("", "", "QUERY")
            assert isinstance(result, dict)
