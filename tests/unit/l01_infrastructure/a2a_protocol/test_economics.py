"""测试: Economics"""

def test_economics():
    from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_economics import A2AEconomics
    e = A2AEconomics()
    r = e.track("t1", 100, 200, "deepseek")
    assert r["cost_usd"] >= 0
