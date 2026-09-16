# [MODULE] tests.capacity.test_capacity_budget_lane_quota
# [TESTS] src/zephyr/orchestrator/governance/capacity_budget.py
# [A_test] module_id: MOD-GOV_capacity_budget_lane_quota | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [TTL] permanent
"""capacity_budget 泳道池 WIP 键增强单测（P2-c 运行时准入接线）。

改点：can_accept/_accept/release/get_pool_quota 由"仅枚举 SystemPool"放宽为"枚举成员
取 value、否则原样用作池键"，使 WIP 可按注册表供给的任意泳道池（default/heavy/realtime/
intraday_*）强制——同时向后兼容：默认预算含全部枚举值，未知系统无声明配额仍放行。
"""

from __future__ import annotations

from zephyr.orchestrator.governance.capacity_budget import (
    CapacityBudgetController,
    SystemPool,
)


def _lane_controller(workers: dict[str, int]) -> CapacityBudgetController:
    ctrl = CapacityBudgetController(max_concurrent_tasks=sum(workers.values()))
    ctrl.budget.wip_limit_per_system = dict(workers)
    return ctrl


class TestRawPoolKeyQuota:
    def test_registry_lane_enforces_wip(self) -> None:
        ctrl = _lane_controller({"heavy": 2, "default": 1})
        assert ctrl.try_accept("t1", "heavy") is True
        assert ctrl.try_accept("t2", "heavy") is True
        assert ctrl.try_accept("t3", "heavy") is False  # heavy WIP=2
        assert ctrl.try_accept("d1", "default") is True
        assert ctrl.try_accept("d2", "default") is False  # default WIP=1

    def test_lane_key_tracked_in_system_active(self) -> None:
        ctrl = _lane_controller({"realtime": 2})
        ctrl.try_accept("r1", "realtime")
        assert ctrl.state.system_active["realtime"] == 1
        ctrl.release("r1", "realtime")
        assert ctrl.state.system_active["realtime"] == 0

    def test_get_pool_quota_serves_lane(self) -> None:
        ctrl = _lane_controller({"intraday_minute": 4})
        assert ctrl.get_pool_quota("intraday_minute") == 4

    def test_get_pool_quota_unknown_still_default(self) -> None:
        ctrl = _lane_controller({"heavy": 2})
        assert ctrl.get_pool_quota("never_declared") == 4  # 未声明→默认 4（后向兼容）

    def test_undeclared_system_permissive(self) -> None:
        ctrl = _lane_controller({"heavy": 1})
        # unknown 不在声明配额表内 → can_accept 放行（不臆造配额）
        assert ctrl.can_accept("unknown_system") is True


class TestBackwardCompat:
    def test_enum_pool_still_works_with_default_budget(self) -> None:
        ctrl = CapacityBudgetController(max_concurrent_tasks=64)
        # 默认预算含全部枚举值：orchestrator quota=16
        for i in range(16):
            assert ctrl.try_accept(f"t{i}", SystemPool.ORCHESTRATOR.value) is True
        assert ctrl.try_accept("t16", SystemPool.ORCHESTRATOR.value) is False

    def test_normalize_key_maps_enum_and_raw(self) -> None:
        assert CapacityBudgetController._normalize_key("database") == SystemPool.DB.value
        assert CapacityBudgetController._normalize_key("heavy") == "heavy"
