# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.a2a_protocol.test_protocol_security
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""测试: Protocol Security"""

def test_protocol_security():
    from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_protocol_security import A2AProtocolSecurity
    ps = A2AProtocolSecurity()
    ps.block("a1", "suspicious")
    assert ps.is_blocked("a1")
