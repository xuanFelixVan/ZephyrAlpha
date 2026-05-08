"""测试: Protocol Security"""

def test_protocol_security():
    from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_protocol_security import A2AProtocolSecurity
    ps = A2AProtocolSecurity()
    ps.block("a1", "suspicious")
    assert ps.is_blocked("a1")
