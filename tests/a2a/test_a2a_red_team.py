# [A_test] module_id: MOD-GOV_a2a_red_team | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §3
# [MODULE] tests.test_a2a_red_team
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
    "zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_red_team",
    reason="a2a_red_team module not available",
)


class TestA2ARedTeam:
    def test_instantiation(self):
        obj = mod.A2ARedTeam()
        assert obj is not None

    def test_attack_vectors_property(self):
        obj = mod.A2ARedTeam()
        vectors = obj.attack_vectors
        assert isinstance(vectors, list)

    def test_list_vectors(self):
        obj = mod.A2ARedTeam()
        result = obj.list_vectors()
        assert isinstance(result, list)

    def test_list_vectors_by_category(self):
        obj = mod.A2ARedTeam()
        result = obj.list_vectors(category=mod.AttackCategory.AGENT_CARD_SPOOFING)
        assert isinstance(result, list)

    def test_get_vector(self):
        obj = mod.A2ARedTeam()
        vectors = obj.attack_vectors
        if vectors:
            vid = vectors[0].vector_id if hasattr(vectors[0], "vector_id") else "v1"
            result = obj.get_vector(vid)
            assert result is not None

    def test_attack(self):
        obj = mod.A2ARedTeam()
        vectors = obj.attack_vectors
        if vectors:
            vid = vectors[0].vector_id if hasattr(vectors[0], "vector_id") else "v1"
            result = obj.attack("proto_1", vid)
            assert isinstance(result, dict)

    def test_run_all_vectors(self):
        obj = mod.A2ARedTeam()
        result = obj.run_all_vectors("proto_1")
        assert isinstance(result, list)

    def test_run_full_red_team(self):
        obj = mod.A2ARedTeam()
        result = obj.run_full_red_team("proto_1")
        assert isinstance(result, mod.RedTeamReport)

    def test_severity_summary(self):
        obj = mod.A2ARedTeam()
        result = obj.severity_summary()
        assert isinstance(result, dict)


class TestEnums:
    def test_attack_severity(self):
        assert len(mod.AttackSeverity) > 0

    def test_attack_category(self):
        assert len(mod.AttackCategory) > 0
