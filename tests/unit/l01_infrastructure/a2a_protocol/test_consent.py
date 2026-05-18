# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.a2a_protocol.test_consent
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""测试: Consent"""

def test_consent():
    from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_consent import A2AConsent
    c = A2AConsent()
    c.grant("a1", "read", "admin")
    c.revoke("a1", "read")
