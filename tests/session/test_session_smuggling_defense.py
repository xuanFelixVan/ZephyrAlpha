# [A_test] module_id: MOD-GOV_session_smuggling_defense | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §3
# [MODULE] tests.test_session_smuggling_defense
# [INVARIANTS] Tests must not modify production state; All imports guarded by pytest.importorskip
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError → skip; AttributeError → fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

mod = pytest.importorskip(
    "zephyr.infrastructure.a2a_protocol.layer3_coordination.session_smuggling_defense",
    reason="session_smuggling_defense module not available",
)


class TestSessionSmugglingDefense:
    def test_instantiation(self):
        obj = mod.SessionSmugglingDefense(max_attempts_per_agent=5)
        assert obj is not None

    def test_verify_session(self):
        obj = mod.SessionSmugglingDefense(max_attempts_per_agent=5)
        result = obj.verify_session(
            reported_agent="agent1",
            signature="sig_abc",
            message_id="msg_1",
            timestamp="2024-01-01T00:00:00",
        )
        assert result is not None

    def test_is_blocked_initially(self):
        obj = mod.SessionSmugglingDefense(max_attempts_per_agent=5)
        assert obj.is_blocked("agent1") is False

    def test_is_blocked_after_exceeding_attempts(self):
        obj = mod.SessionSmugglingDefense(max_attempts_per_agent=2)
        for i in range(5):
            obj.verify_session("agent1", "bad_sig", f"msg_{i}", "2024-01-01T00:00:00")
        assert obj.is_blocked("agent1") is True

    def test_verify_session_empty_signature(self):
        obj = mod.SessionSmugglingDefense(max_attempts_per_agent=5)
        result = obj.verify_session("agent1", "", "msg_1", "2024-01-01T00:00:00")
        assert result is not None


class TestSmugglingAttempt:
    def test_instantiation(self):
        attempt = mod.SmugglingAttempt(reported_agent="a1", actual_agent="a2", message_id="m1", timestamp=0.0)
        assert attempt is not None
        assert attempt.reported_agent == "a1"
