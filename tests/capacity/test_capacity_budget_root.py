# [A_test] module_id: SRC-TST-0493 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_capacity_budget
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_capacity_budget_root.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.orchestrator.governance.capacity_budget import (
    DEFAULT_POOL_QUOTAS,
    CapacityBudget,
    CapacityBudgetController,
    CapacityState,
    SystemPool,
)


class TestSystemPool:
    def test_all_pools_exist(self):
        assert SystemPool.ORCHESTRATOR.value == "orchestrator"
        assert SystemPool.SCRIPT_SYSTEM.value == "script_system"
        assert SystemPool.KB.value == "knowledge_base"
        assert SystemPool.GATES.value == "gate_engine"
        assert SystemPool.CE.value == "context-engine"
        assert SystemPool.PIPELINE.value == "pipeline"
        assert SystemPool.FLE.value == "feedback-loop"
        assert SystemPool.VMS.value == "vector-memory"
        assert SystemPool.DB.value == "database"
        assert SystemPool.LSG.value == "llm-security"
        assert SystemPool.TELEMETRY.value == "system-telemetry"
        assert SystemPool.MCP.value == "mcp_servers"

    def test_pool_count(self):
        assert len(SystemPool) == 12


class TestDefaultPoolQuotas:
    def test_all_pools_have_quotas(self):
        for pool in SystemPool:
            assert pool in DEFAULT_POOL_QUOTAS

    def test_quotas_positive(self):
        for pool, quota in DEFAULT_POOL_QUOTAS.items():
            assert quota > 0


class TestCapacityBudget:
    def test_default_construction(self):
        cb = CapacityBudget()
        assert cb.max_concurrent_tasks == 64
        assert len(cb.wip_limit_per_system) == 12

    def test_custom_max_concurrent(self):
        cb = CapacityBudget(max_concurrent_tasks=32)
        assert cb.max_concurrent_tasks == 32

    def test_zero_max_concurrent_raises(self):
        with pytest.raises(Exception):
            CapacityBudget(max_concurrent_tasks=0)


class TestCapacityState:
    def test_default_construction(self):
        cs = CapacityState()
        assert cs.active_tasks == 0
        assert cs.queued_tasks == 0
        assert cs.max_concurrent == 64
        assert len(cs.system_active) == 12

    def test_all_systems_initially_zero(self):
        cs = CapacityState()
        for pool in SystemPool:
            assert cs.system_active[pool.value] == 0


class TestCapacityBudgetControllerInstantiation:
    def test_default_construction(self):
        ctrl = CapacityBudgetController()
        assert ctrl.max_concurrent == 64
        assert ctrl.state.active_tasks == 0

    def test_custom_max_concurrent(self):
        ctrl = CapacityBudgetController(max_concurrent_tasks=16)
        assert ctrl.max_concurrent == 16


class TestCapacityBudgetControllerCanAccept:
    def test_can_accept_when_empty(self):
        ctrl = CapacityBudgetController()
        assert ctrl.can_accept("orchestrator") is True

    def test_can_accept_unknown_system(self):
        ctrl = CapacityBudgetController()
        assert ctrl.can_accept("unknown_system") is True

    def test_cannot_accept_when_full(self):
        ctrl = CapacityBudgetController(max_concurrent_tasks=2)
        ctrl.try_accept("t1", "orchestrator")
        ctrl.try_accept("t2", "orchestrator")
        assert ctrl.can_accept("orchestrator") is False

    def test_cannot_accept_when_pool_full(self):
        ctrl = CapacityBudgetController(max_concurrent_tasks=64)
        for i in range(16):
            ctrl.try_accept(f"t{i}", "orchestrator")
        assert ctrl.can_accept("orchestrator") is False


class TestCapacityBudgetControllerTryAccept:
    def test_try_accept_success(self):
        ctrl = CapacityBudgetController()
        result = ctrl.try_accept("t1", "orchestrator")
        assert result is True
        assert ctrl.state.active_tasks == 1

    def test_try_accept_queues_when_full(self):
        ctrl = CapacityBudgetController(max_concurrent_tasks=1)
        ctrl.try_accept("t1", "orchestrator")
        result = ctrl.try_accept("t2", "orchestrator")
        assert result is False
        assert ctrl.state.queued_tasks == 1

    def test_try_accept_tracks_system_active(self):
        ctrl = CapacityBudgetController()
        ctrl.try_accept("t1", "orchestrator")
        assert ctrl.state.system_active["orchestrator"] == 1


class TestCapacityBudgetControllerRelease:
    def test_release_decrements_active(self):
        ctrl = CapacityBudgetController()
        ctrl.try_accept("t1", "orchestrator")
        ctrl.release("t1", "orchestrator")
        assert ctrl.state.active_tasks == 0

    def test_release_decrements_system_active(self):
        ctrl = CapacityBudgetController()
        ctrl.try_accept("t1", "orchestrator")
        ctrl.release("t1", "orchestrator")
        assert ctrl.state.system_active["orchestrator"] == 0

    def test_release_dequeues_next_task(self):
        ctrl = CapacityBudgetController(max_concurrent_tasks=1)
        ctrl.try_accept("t1", "orchestrator")
        ctrl.try_accept("t2", "orchestrator")
        next_task = ctrl.release("t1", "orchestrator")
        assert next_task == "t2"
        assert ctrl.state.queued_tasks == 0

    def test_release_no_queued_returns_none(self):
        ctrl = CapacityBudgetController()
        ctrl.try_accept("t1", "orchestrator")
        result = ctrl.release("t1", "orchestrator")
        assert result is None

    def test_release_unknown_system(self):
        ctrl = CapacityBudgetController()
        ctrl.try_accept("t1", "unknown_system")
        ctrl.release("t1", "unknown_system")
        assert ctrl.state.active_tasks == 0

    def test_release_floor_zero(self):
        ctrl = CapacityBudgetController()
        ctrl.release("nonexistent", "orchestrator")
        assert ctrl.state.active_tasks == 0
        assert ctrl.state.system_active["orchestrator"] == 0


class TestCapacityBudgetControllerGetQueuePosition:
    def test_position_in_queue(self):
        ctrl = CapacityBudgetController(max_concurrent_tasks=1)
        ctrl.try_accept("t1", "orchestrator")
        ctrl.try_accept("t2", "orchestrator")
        ctrl.try_accept("t3", "orchestrator")
        assert ctrl.get_queue_position("t2") == 1
        assert ctrl.get_queue_position("t3") == 2

    def test_position_not_in_queue(self):
        ctrl = CapacityBudgetController()
        assert ctrl.get_queue_position("nonexistent") == -1

    def test_position_empty_queue(self):
        ctrl = CapacityBudgetController()
        assert ctrl.get_queue_position("t1") == -1


class TestCapacityBudgetControllerGetPoolQuota:
    def test_known_system(self):
        ctrl = CapacityBudgetController()
        quota = ctrl.get_pool_quota("orchestrator")
        assert quota == 16

    def test_unknown_system(self):
        ctrl = CapacityBudgetController()
        quota = ctrl.get_pool_quota("nonexistent")
        assert quota == 4

    def test_all_known_systems(self):
        ctrl = CapacityBudgetController()
        for pool in SystemPool:
            quota = ctrl.get_pool_quota(pool.value)
            assert quota > 0
