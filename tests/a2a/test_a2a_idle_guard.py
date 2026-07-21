# [A_test] module_id: MOD-GOV_a2a_idle_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §3
# [MODULE] tests.test_a2a_idle_guard
# [INVARIANTS] Tests must not modify production state; All imports guarded by pytest.importorskip
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError → skip; AttributeError → fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import time

import pytest

mod = pytest.importorskip(
    "zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_idle_guard",
    reason="a2a_idle_guard module not available",
)


class TestA2AIdleGuard:
    def test_instantiation(self):
        obj = mod.A2AIdleGuard(idle_timeout=300)
        assert obj is not None

    def test_check_idle_active(self):
        obj = mod.A2AIdleGuard(idle_timeout=300)
        now = time.time()
        result = obj.check_idle("agent1", last_active=now, now=now)
        assert result is False

    def test_check_idle_expired(self):
        obj = mod.A2AIdleGuard(idle_timeout=300)
        now = time.time()
        last_active = now - 600
        result = obj.check_idle("agent1", last_active=last_active, now=now)
        assert result is True

    def test_check_idle_exactly_at_timeout(self):
        obj = mod.A2AIdleGuard(idle_timeout=300)
        now = time.time()
        last_active = now - 300
        result = obj.check_idle("agent1", last_active=last_active, now=now)
        assert isinstance(result, bool)
