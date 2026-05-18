# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.a2a_protocol.test_blame
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""测试: BlameAttribution"""

from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_blame_attribution import (
    A2ABlameAttribution,
    BlameReport,
)


def test_attribute_no_records():
    ba = A2ABlameAttribution()
    report = ba.attribute("incident-1", ["agent-a"])
    assert isinstance(report, BlameReport)
    assert report.incident_id == "incident-1"
    assert len(report.items) == 0
    assert report.root_cause_agent == ""


def test_attribute_with_records():
    ba = A2ABlameAttribution()
    ba.add_record("agent-a", "write_file", 1000.0, impact_score=0.8)
    ba.add_record("agent-b", "read_file", 1001.0, impact_score=0.2)
    report = ba.attribute("incident-2", ["agent-a", "agent-b"])
    assert len(report.items) == 2
    assert report.root_cause_agent == "agent-a"
    assert report.items[0].contribution > report.items[1].contribution


def test_attribute_single_agent():
    ba = A2ABlameAttribution()
    ba.add_record("agent-a", "delete_data", 2000.0, impact_score=1.0)
    report = ba.attribute("incident-3", ["agent-a"])
    assert len(report.items) == 1
    assert report.items[0].agent_id == "agent-a"
    assert report.items[0].contribution == 1.0


def test_primary_blame():
    ba = A2ABlameAttribution()
    ba.add_record("agent-a", "action1", 1000.0, impact_score=0.9)
    ba.add_record("agent-b", "action2", 1001.0, impact_score=0.1)
    report = ba.attribute("incident-4", ["agent-a", "agent-b"])
    assert report.primary_blame is not None
    assert report.primary_blame.agent_id == "agent-a"
