# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.a2a_protocol.test_protocol_gateway
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""测试: ProtocolGateway"""

def test_protocol_gateway():
    from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_protocol_gateway import A2AProtocolGateway
    gw = A2AProtocolGateway()
    gw.register("a1", "http://localhost:8000")
    assert gw.resolve("a1") == "http://localhost:8000"
