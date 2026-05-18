# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.a2a_protocol.test_constitutional
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""测试: Constitutional"""

def test_constitutional():
    from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_constitutional import A2AConstitutional
    c = A2AConstitutional()
    assert c.can_veto("delete")
    assert not c.can_veto("read")
