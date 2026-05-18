# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.a2a_protocol.test_carbon
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""测试: Carbon"""

def test_carbon():
    from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_carbon import A2ACarbon
    r = A2ACarbon.estimate(1000000)
    assert r["tokens"] == 1000000
