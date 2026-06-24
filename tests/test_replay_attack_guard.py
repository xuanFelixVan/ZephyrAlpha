# [A_test] module_id: SRC-TST-1445 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.replay_attack_guard
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
import sys

sys.path.insert(0, "src")

import time

import pytest

try:
    from zephyr.security.access_control.replay_attack_guard import ReplayAttackGuard
except Exception as _exc:
    pytest.skip(f"Cannot import replay_attack_guard: {_exc}", allow_module_level=True)


class TestReplayAttackGuard:
    def test_allow_fresh_nonce(self):
        guard = ReplayAttackGuard()
        result = guard.check("nonce-unique-1", time.time())
        assert result["allowed"] is True
        assert "nonce_hash" in result

    def test_block_replay_same_nonce(self):
        guard = ReplayAttackGuard()
        ts = time.time()
        guard.check("nonce-dup", ts)
        result = guard.check("nonce-dup", ts)
        assert result["allowed"] is False
        assert result["reason"] == "replay_detected"

    def test_block_expired_timestamp(self):
        guard = ReplayAttackGuard()
        old_ts = time.time() - 600
        result = guard.check("nonce-old", old_ts)
        assert result["allowed"] is False
        assert result["reason"] == "timestamp_outside_window"

    def test_block_future_timestamp(self):
        guard = ReplayAttackGuard()
        future_ts = time.time() + 600
        result = guard.check("nonce-future", future_ts)
        assert result["allowed"] is False
        assert result["reason"] == "timestamp_outside_window"

    def test_different_nonces_allowed(self):
        guard = ReplayAttackGuard()
        ts = time.time()
        r1 = guard.check("nonce-a", ts)
        r2 = guard.check("nonce-b", ts)
        assert r1["allowed"] is True
        assert r2["allowed"] is True

    def test_blocked_count_increments(self):
        guard = ReplayAttackGuard()
        ts = time.time()
        guard.check("nonce-x", ts)
        guard.check("nonce-x", ts)
        assert guard._blocked_count == 1

    def test_window_boundary_within(self):
        guard = ReplayAttackGuard()
        ts = time.time() - guard._WINDOW_SECONDS + 1
        result = guard.check("nonce-boundary", ts)
        assert result["allowed"] is True

    def test_empty_nonce(self):
        guard = ReplayAttackGuard()
        result = guard.check("", time.time())
        assert result["allowed"] is True
