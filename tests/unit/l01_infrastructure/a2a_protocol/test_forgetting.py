"""测试: Forgetting"""

def test_forgetting():
    from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_forgetting import A2AForgetting
    f = A2AForgetting(3)
    for i in range(5):
        f.remember({"i": i})
    assert len(f._memory) == 3
