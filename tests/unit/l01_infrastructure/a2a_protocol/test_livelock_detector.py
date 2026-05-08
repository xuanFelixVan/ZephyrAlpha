"""测试: LivelockDetector"""

def test_livelock_detector():
    from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.livelock_detector import LivelockDetector
    ld = LivelockDetector(3)
    for _ in range(2):
        ld.record_state("a1", "h1")
    assert not ld.check_cycle("a1", "h1")
    ld.record_state("a1", "h1")
    assert ld.check_cycle("a1", "h1")
