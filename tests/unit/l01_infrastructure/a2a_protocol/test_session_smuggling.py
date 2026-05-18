# [BLUEPRINT] DOM-GOV-001 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.l01_infrastructure.a2a_protocol.test_session_smuggling
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""测试: SessionSmuggling"""

from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination.session_smuggling_defense import (
    SessionSmugglingDefense,
)


def test_verify_session_valid_signature():
    ssd = SessionSmugglingDefense()
    assert ssd.verify_session("agent-a", "valid_signature_here_12345678", "msg-1", 1000.0)


def test_verify_session_empty_signature():
    ssd = SessionSmugglingDefense()
    assert not ssd.verify_session("agent-a", "", "msg-2", 1000.0)


def test_verify_session_short_signature():
    ssd = SessionSmugglingDefense()
    assert not ssd.verify_session("agent-a", "short", "msg-3", 1000.0)


def test_blocked_after_max_attempts():
    ssd = SessionSmugglingDefense(max_attempts_per_agent=3)
    for i in range(3):
        ssd.verify_session("agent-bad", "", f"msg-{i}", 1000.0)
    assert ssd.is_blocked("agent-bad")


def test_not_blocked_initially():
    ssd = SessionSmugglingDefense()
    assert not ssd.is_blocked("agent-clean")
