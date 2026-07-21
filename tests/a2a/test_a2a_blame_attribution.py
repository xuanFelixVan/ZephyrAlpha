# [A_test] module_id: MOD-GOV_a2a_blame_attribution | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §3
# [MODULE] tests.test_a2a_blame_attribution
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
    "zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_blame_attribution",
    reason="a2a_blame_attribution module not available",
)


class TestA2ABlameAttribution:
    def test_instantiation(self):
        obj = mod.A2ABlameAttribution()
        assert obj is not None

    def test_add_record(self):
        obj = mod.A2ABlameAttribution()
        obj.add_record("agent1", "delete_file", "2024-01-01T00:00:00", 0.8)
        obj.add_record("agent2", "modify_config", "2024-01-01T00:01:00", 0.3)

    def test_attribute(self):
        obj = mod.A2ABlameAttribution()
        obj.add_record("agent1", "delete_file", "2024-01-01T00:00:00", 0.9)
        obj.add_record("agent2", "modify_config", "2024-01-01T00:01:00", 0.3)
        report = obj.attribute("incident_1", ["agent1", "agent2"])
        assert report is not None
        assert report.primary_blame is not None or report.root_cause_agent is not None

    def test_attribute_empty_suspects(self):
        obj = mod.A2ABlameAttribution()
        report = obj.attribute("incident_2", [])
        assert report is not None

    def test_add_record_zero_impact(self):
        obj = mod.A2ABlameAttribution()
        obj.add_record("agent1", "read_file", "2024-01-01T00:00:00", 0.0)


class TestBlameReport:
    def test_primary_blame_with_items(self):
        item = mod.BlameItem(agent_id="agent1", action="delete", contribution=0.9)
        report = mod.BlameReport(incident_id="inc_1", items=[item], root_cause_agent="agent1")
        assert report.root_cause_agent == "agent1"

    def test_primary_blame_empty(self):
        report = mod.BlameReport(incident_id="inc_2")
        assert report.root_cause_agent == ""
