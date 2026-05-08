"""测试: Consent"""

def test_consent():
    from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.a2a_consent import A2AConsent
    c = A2AConsent()
    c.grant("a1", "read", "admin")
    c.revoke("a1", "read")
