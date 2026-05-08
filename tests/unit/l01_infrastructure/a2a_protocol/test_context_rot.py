"""测试: ContextRot"""

def test_context_rot():
    from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_context_rot import A2AContextRot
    cr = A2AContextRot()
    assert cr.detect_rot({}, 0) == 0.0
    assert cr.detect_rot({}, 3600) == 1.0
