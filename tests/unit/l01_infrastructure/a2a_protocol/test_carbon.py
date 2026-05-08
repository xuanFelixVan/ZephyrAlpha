"""测试: Carbon"""

def test_carbon():
    from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_carbon import A2ACarbon
    r = A2ACarbon.estimate(1000000)
    assert r["tokens"] == 1000000
