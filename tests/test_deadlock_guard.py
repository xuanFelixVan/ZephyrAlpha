# [A_test] module_id: SRC-TST-0711 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md | §
# [MODULE] tests.test_deadlock_guard
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_deadlock_guard.py

import pytest
from zephyr.infrastructure.a2a_protocol.layer3_coordination.deadlock_guard import DeadlockGuard


class TestDeadlockGuard:
    def test_create(self):
        dg = DeadlockGuard()
        assert dg._locks == {}

    def test_acquire_success(self):
        dg = DeadlockGuard()
        assert dg.try_acquire("resource-1", "agent-a") is True
        assert dg._locks["resource-1"] == "agent-a"

    def test_acquire_already_held(self):
        dg = DeadlockGuard()
        dg.try_acquire("resource-1", "agent-a")
        assert dg.try_acquire("resource-1", "agent-b") is False

    def test_release_success(self):
        dg = DeadlockGuard()
        dg.try_acquire("resource-1", "agent-a")
        assert dg.release("resource-1", "agent-a") is True
        assert "resource-1" not in dg._locks

    def test_release_wrong_holder(self):
        dg = DeadlockGuard()
        dg.try_acquire("resource-1", "agent-a")
        assert dg.release("resource-1", "agent-b") is False
        assert dg._locks["resource-1"] == "agent-a"

    def test_release_nonexistent(self):
        dg = DeadlockGuard()
        assert dg.release("resource-x", "agent-a") is False

    def test_acquire_after_release(self):
        dg = DeadlockGuard()
        dg.try_acquire("resource-1", "agent-a")
        dg.release("resource-1", "agent-a")
        assert dg.try_acquire("resource-1", "agent-b") is True

    def test_multiple_resources(self):
        dg = DeadlockGuard()
        assert dg.try_acquire("r1", "agent-a") is True
        assert dg.try_acquire("r2", "agent-a") is True
        assert dg.try_acquire("r2", "agent-b") is False
