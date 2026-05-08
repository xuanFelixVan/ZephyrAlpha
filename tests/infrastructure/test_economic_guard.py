"""Test Economic Guard."""
from zephyr.infrastructure.escalation_protocol.economic_guard import EconomicGuard

def test_within_budget():
    g=EconomicGuard()
    ok,msg=g.check_single(1.0)
    assert ok

def test_exceeds_single():
    g=EconomicGuard()
    g.MAX_SINGLE_COST=5.0
    ok,msg=g.check_single(6.0)
    assert not ok
