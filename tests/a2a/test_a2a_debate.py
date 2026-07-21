# [A_test] module_id: MOD-GOV_a2a_debate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §3
# [MODULE] tests.test_a2a_debate
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
    "zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_debate",
    reason="a2a_debate module not available",
)


class TestA2ADebate:
    def test_instantiation(self):
        obj = mod.A2ADebate()
        assert obj is not None

    def test_instantiation_custom_rounds(self):
        obj = mod.A2ADebate(max_rounds=5)
        assert obj is not None

    def test_debate(self):
        obj = mod.A2ADebate(max_rounds=2)
        result = obj.debate("agent_a", "agent_b", "topic", "claim_a", "claim_b")
        assert result is not None

    def test_debate_returns_result(self):
        obj = mod.A2ADebate(max_rounds=1)
        result = obj.debate("a1", "a2", "test_topic", "claim1", "claim2")
        assert isinstance(result, mod.DebateResult)

    def test_debate_empty_claims(self):
        obj = mod.A2ADebate(max_rounds=1)
        result = obj.debate("a1", "a2", "topic", "", "")
        assert result is not None


class TestDebatePhase:
    def test_enum_values(self):
        assert len(mod.DebatePhase) > 0
