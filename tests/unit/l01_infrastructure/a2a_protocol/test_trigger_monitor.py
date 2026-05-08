"""测试: TriggerMonitor"""

def test_trigger_monitor():
    from zephyr.l01_infrastructure.a2a_protocol.layer2_communication.trigger_monitor import TriggerMonitor

    tm = TriggerMonitor()
    tm.watch("T1", lambda ctx: ctx.get("x", 0) > 5)
    assert tm.check("T1", {"x": 10})
    assert not tm.check("T1", {"x": 3})
