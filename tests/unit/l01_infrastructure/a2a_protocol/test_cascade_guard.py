# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.a2a_protocol.test_cascade_guard
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""测试: CascadeGuard"""

def test_cascade_guard():
    from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.cascade_guard import CascadeGuard
    cg = CascadeGuard(3)
    assert cg.check("a1")
    cg.record_failure("a1")
    cg.record_failure("a1")
    assert cg.check("a1")
    cg.record_failure("a1")
    assert not cg.check("a1")
