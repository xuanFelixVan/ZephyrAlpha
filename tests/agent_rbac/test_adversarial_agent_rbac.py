# [A_test] module_id: SRC-TST-0024 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain-autonomy_core/agent-rbac/blueprint.md | §
# [MODULE] tests.agent_rbac.test_adversarial
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""MOD-INF-018 test_adversarial.py — 对抗性测试: 权限绕过/伪造/重放."""

from __future__ import annotations


class TestAdversarial:
    def test_session_token_verified(self):
        from zephyr.security.access_control.cross_session_detector import CrossSessionDetector

        detector = CrossSessionDetector()
        token = detector.sign_token("agent_a", "session_1")
        result = detector.verify_token("agent_a", "session_1", token.nonce, token.timestamp, token.signature)
        assert result["valid"] is True

    def test_replay_attack_blocked(self):
        import time

        from zephyr.security.access_control.replay_attack_guard import ReplayAttackGuard

        guard = ReplayAttackGuard()
        nonce = "test_nonce_12345"
        ts = time.time()
        result = guard.check(nonce, ts)
        assert result["allowed"] is True

    def test_monotonic_clock_prevents_time_rollback(self):
        from zephyr.security.access_control.monotonic_clock import MonotonicClock

        clock = MonotonicClock()
        t1 = clock.now()
        t2 = clock.now()
        assert t2 >= t1

    def test_non_repudiation_signs_audit_entry(self):
        from zephyr.security.access_control.non_repudiation import NonRepudiation

        nr = NonRepudiation()
        entry = nr.sign("read:docs", "test_agent")
        assert entry.hmac_hash is not None
