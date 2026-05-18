# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.a2a_protocol.test_forgetting
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""测试: Forgetting"""

def test_forgetting():
    from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_forgetting import A2AForgetting
    f = A2AForgetting(3)
    for i in range(5):
        f.remember({"i": i})
    assert len(f._memory) == 3
