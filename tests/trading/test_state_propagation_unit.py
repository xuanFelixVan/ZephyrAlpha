# [A_test] module_id: SRC-TST-2071 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-688 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_state_propagation
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""状态传播链单元测试——验证 TaskCard 状态变更 → 关联系统通知。"""


import pytest

from zephyr.orchestrator.lifecycle.state_propagation import (
    PROPAGATION_RULES,
    PropagationTarget,
    StatePropagator,
)


@pytest.fixture
def propagator():
    return StatePropagator()


class TestPropagationRules:
    def test_rules_defined(self):
        assert len(PROPAGATION_RULES) == 7

    def test_completed_notifies_vms_and_db(self):
        targets = PROPAGATION_RULES["IN_PROGRESS→COMPLETED"]["notify"]
        assert PropagationTarget.VMS in targets
        assert PropagationTarget.DB in targets


class TestPropagate:
    def test_propagate_in_progress_to_completed(self, propagator):
        targets = propagator.propagate("TASK-001", "IN_PROGRESS", "COMPLETED")
        assert PropagationTarget.VMS in targets
        assert PropagationTarget.DB in targets
        assert len(targets) == 3

    def test_propagate_in_progress_to_blocked(self, propagator):
        targets = propagator.propagate("TASK-002", "IN_PROGRESS", "BLOCKED")
        assert PropagationTarget.GATES in targets
        assert PropagationTarget.FLE in targets

    def test_propagate_pending_to_in_progress(self, propagator):
        targets = propagator.propagate("TASK-003", "PENDING", "IN_PROGRESS")
        assert PropagationTarget.GATES in targets
        assert PropagationTarget.FLE in targets

    def test_propagate_unknown_transition(self, propagator):
        targets = propagator.propagate("TASK-004", "VERIFIED", "CANCELLED")
        assert targets == []


class TestEvents:
    def test_event_recorded(self, propagator):
        propagator.propagate("TASK-001", "IN_PROGRESS", "COMPLETED")
        events = propagator.get_events()
        assert len(events) == 1
        assert events[0].task_id == "TASK-001"
        assert events[0].old_status == "IN_PROGRESS"
        assert events[0].new_status == "COMPLETED"

    def test_events_for_task(self, propagator):
        propagator.propagate("TASK-A", "PENDING", "IN_PROGRESS")
        propagator.propagate("TASK-A", "IN_PROGRESS", "COMPLETED")
        propagator.propagate("TASK-B", "PENDING", "IN_PROGRESS")
        assert len(propagator.get_events_for_task("TASK-A")) == 2
        assert len(propagator.get_events_for_task("TASK-B")) == 1


class TestNotifiableTargets:
    def test_completed_targets(self, propagator):
        targets = propagator.get_notifiable_targets("IN_PROGRESS", "COMPLETED")
        assert "vector-memory" in targets
        assert "database" in targets
