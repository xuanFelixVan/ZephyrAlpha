# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.a2a_protocol.test_context_rot
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""测试: ContextRot"""

def test_context_rot():
    from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_context_rot import A2AContextRot
    cr = A2AContextRot()
    assert cr.detect_rot({}, 0) == 0.0
    assert cr.detect_rot({}, 3600) == 1.0
