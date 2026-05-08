"""测试: VectorReputation"""

def test_reputation():
    from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_vector_reputation import A2AVectorReputation
    vr = A2AVectorReputation()
    vr.rate("a1", "accuracy", 0.9)
    assert vr.reputation("a1")["accuracy"] == 0.9
