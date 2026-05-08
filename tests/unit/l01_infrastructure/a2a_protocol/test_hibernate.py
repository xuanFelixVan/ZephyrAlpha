"""测试: Hibernate"""

def test_hibernate():
    from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_hibernate import A2AHibernate
    h = A2AHibernate()
    h.sleep("a1", "idle")
    assert h.is_sleeping("a1")
    h.wake("a1")
    assert not h.is_sleeping("a1")
