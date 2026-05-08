"""测试: Immune"""

def test_immune():
    from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_immune import A2AImmune
    im = A2AImmune()
    assert not im.detect_threat("a1", {})
