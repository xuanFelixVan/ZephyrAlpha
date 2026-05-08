"""测试: DeadlockGuard"""

def test_deadlock_guard():
    from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.deadlock_guard import DeadlockGuard
    dg = DeadlockGuard()
    assert dg.try_acquire("r1", "a1")
    assert not dg.try_acquire("r1", "a2")
    assert dg.release("r1", "a1")
