# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.a2a_protocol.test_idle_guard
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""测试: IdleGuard"""

def test_idle_guard():
    from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_idle_guard import A2AIdleGuard
    ig = A2AIdleGuard(5)
    assert ig.check_idle("a1", 0, 10)
    assert not ig.check_idle("a1", 9, 10)
