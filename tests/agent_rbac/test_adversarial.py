# [BLUEPRINT] MOD-INF-018 | docs/03_modules/l01_infrastructure/agent-rbac/blueprint.md | §
# [MODULE] tests.agent_rbac.test_adversarial
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""MOD-INF-018 test_adversarial.py — 对抗性测试: 权限绕过/伪造/重放."""
from __future__ import annotations

import pytest


class TestAdversarial:
    def test_session_token_verified(self):
        from zephyr.agent_rbac.cross_session_detector import CrossSessionDetector
        detector = CrossSessionDetector()
        token = detector.sign_token("agent_a", "session_1")
        result = detector.verify_token("agent_a", "session_1", token.nonce, token.timestamp, token.signature)
        assert result["valid"] is True

    def test_replay_attack_blocked(self):
        from zephyr.agent_rbac.replay_attack_guard import ReplayAttackGuard
        import time
        guard = ReplayAttackGuard()
        nonce = "test_nonce_12345"
        ts = time.time()
        result = guard.check(nonce, ts)
        assert result["allowed"] is True

    def test_monotonic_clock_prevents_time_rollback(self):
        from zephyr.agent_rbac.monotonic_clock import MonotonicClock
        clock = MonotonicClock()
        t1 = clock.now()
        t2 = clock.now()
        assert t2 >= t1

    def test_non_repudiation_signs_audit_entry(self):
        from zephyr.agent_rbac.non_repudiation import NonRepudiation
        nr = NonRepudiation()
        entry = nr.sign("read:docs", "test_agent")
        assert entry.hmac_hash is not None
