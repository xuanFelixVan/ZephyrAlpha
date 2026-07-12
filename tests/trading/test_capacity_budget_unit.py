# [A_test] module_id: SRC-TST-1985 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-602 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_capacity_budget
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""容量预算单元测试——验证并发上限 + WIP Limit 强制执行。"""


import pytest

from zephyr.orchestrator.governance.capacity_budget import (
    CapacityBudgetController,
)


@pytest.fixture
def controller():
    return CapacityBudgetController(max_concurrent_tasks=5)


class TestInitialState:
    def test_initial_active_zero(self, controller):
        assert controller.state.active_tasks == 0

    def test_max_concurrent(self, controller):
        assert controller.max_concurrent == 5


class TestCanAccept:
    def test_accept_within_limit(self, controller):
        for i in range(5):
            assert controller.can_accept("orchestrator")

    def test_reject_over_limit(self, controller):
        for i in range(5):
            controller.try_accept(f"TASK-{i}", "orchestrator")
        assert not controller.can_accept("orchestrator")

    def test_system_pool_limit(self, controller):
        ctrl = CapacityBudgetController(max_concurrent_tasks=64)
        ctrl._budget.wip_limit_per_system["orchestrator"] = 4
        for i in range(4):
            assert ctrl.try_accept(f"T-{i}", "orchestrator")
        assert not ctrl.try_accept("T-OVER", "orchestrator")


class TestTryAccept:
    def test_try_accept_success(self, controller):
        result = controller.try_accept("TASK-001", "orchestrator")
        assert result is True
        assert controller.state.active_tasks == 1

    def test_try_accept_queued(self, controller):
        for i in range(5):
            controller.try_accept(f"TASK-{i}", "orchestrator")
        result = controller.try_accept("TASK-QUEUED", "orchestrator")
        assert result is False
        assert controller.state.queued_tasks == 1


class TestRelease:
    def test_release_no_queue(self, controller):
        controller.try_accept("TASK-001", "orchestrator")
        next_task = controller.release("TASK-001", "orchestrator")
        assert next_task is None
        assert controller.state.active_tasks == 0

    def test_release_with_queue(self, controller):
        for i in range(5):
            controller.try_accept(f"TASK-{i}", "orchestrator")
        controller.try_accept("TASK-QUEUED", "orchestrator")
        next_task = controller.release("TASK-0", "orchestrator")
        assert next_task == "TASK-QUEUED"
        assert controller.state.active_tasks == 5


class TestQueuePosition:
    def test_position_in_queue(self, controller):
        for i in range(5):
            controller.try_accept(f"TASK-{i}", "orchestrator")
        controller.try_accept("TASK-A", "orchestrator")
        controller.try_accept("TASK-B", "orchestrator")
        assert controller.get_queue_position("TASK-A") == 1
        assert controller.get_queue_position("TASK-B") == 2

    def test_position_not_in_queue(self, controller):
        assert controller.get_queue_position("NONEXISTENT") == -1


class TestPoolQuota:
    def test_orchestrator_quota(self, controller):
        assert controller.get_pool_quota("orchestrator") == 16

    def test_mcp_quota(self, controller):
        assert controller.get_pool_quota("mcp_servers") == 2
