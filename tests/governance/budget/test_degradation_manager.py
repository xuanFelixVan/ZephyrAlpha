# [A_test] module_id: MOD-GOV_degradation_manager | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_degradation_manager
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [INVARIANTS] DegradationLevel progression is monotonic; HALT at usage>=1.0
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

import time

from zephyr.governance.ops_governance.budget_models import BudgetDimension, ModelTier
from zephyr.governance.ops_governance.degradation_manager import (
    DegradationLevel,
    DegradationManager,
    DegradationState,
)


class TestDegradationState:
    def test_default_is_normal(self):
        state = DegradationState()
        assert state.current_level == DegradationLevel.NORMAL
        assert state.is_degraded is False

    def test_can_advance_from_normal(self):
        state = DegradationState()
        assert state.can_advance() is True

    def test_cannot_advance_from_halt(self):
        state = DegradationState(current_level=DegradationLevel.HALT)
        assert state.can_advance() is False

    def test_can_retreat_after_cooldown(self):
        state = DegradationState(recovery_cooldown_until=0.0)
        assert state.can_retreat() is True

    def test_cannot_retreat_during_cooldown(self):
        state = DegradationState(recovery_cooldown_until=time.time() + 3600)
        assert state.can_retreat() is False


class TestDegradationManager:
    def test_instantiation_defaults(self):
        mgr = DegradationManager()
        assert mgr.state.current_level == DegradationLevel.NORMAL
        assert mgr.circuit_breaker_open is False

    def test_evaluate_normal_usage(self):
        mgr = DegradationManager()
        result = mgr.evaluate(usage_ratio=0.2, dimension=BudgetDimension.TOKEN)
        assert result is None

    def test_evaluate_notify_at_50_percent(self):
        mgr = DegradationManager(anti_spiral_limit=5)
        result = mgr.evaluate(usage_ratio=0.55, dimension=BudgetDimension.TOKEN)
        assert result is not None
        assert result.level == DegradationLevel.NOTIFY

    def test_evaluate_warning_at_70_percent(self):
        mgr = DegradationManager(anti_spiral_limit=5)
        mgr.evaluate(usage_ratio=0.55, dimension=BudgetDimension.TOKEN)
        result = mgr.evaluate(usage_ratio=0.75, dimension=BudgetDimension.TOKEN)
        assert result is not None
        assert result.level == DegradationLevel.WARNING

    def test_evaluate_halt_at_100_percent(self):
        mgr = DegradationManager()
        result = mgr.evaluate(usage_ratio=1.0, dimension=BudgetDimension.COST)
        assert result is not None
        assert result.level == DegradationLevel.HALT

    def test_evaluate_model_switch(self):
        mgr = DegradationManager(anti_spiral_limit=5)
        result = mgr.evaluate(usage_ratio=0.85, dimension=BudgetDimension.TOKEN)
        assert result is not None
        assert result.level in (DegradationLevel.MODEL_SWITCH, DegradationLevel.COMPRESS)

    def test_manual_retreat(self):
        mgr = DegradationManager()
        mgr.evaluate(usage_ratio=1.0, dimension=BudgetDimension.TOKEN)
        action = mgr.manual_retreat(reason="test_reset")
        assert action.level == DegradationLevel.NORMAL
        assert mgr.state.current_level == DegradationLevel.NORMAL

    def test_anti_spiral_limit(self):
        mgr = DegradationManager(anti_spiral_limit=1)
        mgr.evaluate(usage_ratio=0.55, dimension=BudgetDimension.TOKEN)
        result = mgr.evaluate(usage_ratio=0.75, dimension=BudgetDimension.TOKEN)
        assert result is None

    def test_circuit_breaker(self):
        mgr = DegradationManager()
        mgr.record_dependency_failure("dep1")
        mgr.record_dependency_failure("dep2")
        mgr.record_dependency_failure("dep3")
        assert mgr.circuit_breaker_open is True

    def test_circuit_breaker_blocks_evaluate(self):
        mgr = DegradationManager()
        for i in range(3):
            mgr.record_dependency_failure(f"dep{i}")
        result = mgr.evaluate(usage_ratio=1.0, dimension=BudgetDimension.TOKEN)
        assert result is None

    def test_reset(self):
        mgr = DegradationManager()
        mgr.evaluate(usage_ratio=1.0, dimension=BudgetDimension.TOKEN)
        mgr.reset()
        assert mgr.state.current_level == DegradationLevel.NORMAL

    def test_compute_target_tier_model_switch(self):
        tier = DegradationManager.compute_target_tier(DegradationLevel.MODEL_SWITCH, ModelTier.PREMIUM)
        assert tier == ModelTier.ECONOMY

    def test_compute_target_tier_no_downgrade(self):
        tier = DegradationManager.compute_target_tier(DegradationLevel.NOTIFY, ModelTier.MINIMAL)
        assert tier == ModelTier.MINIMAL


class TestBoundaryCases:
    def test_evaluate_zero_usage(self):
        mgr = DegradationManager()
        result = mgr.evaluate(usage_ratio=0.0, dimension=BudgetDimension.TOKEN)
        assert result is None

    def test_evaluate_just_below_halt(self):
        mgr = DegradationManager(anti_spiral_limit=5)
        result = mgr.evaluate(usage_ratio=0.99, dimension=BudgetDimension.TOKEN)
        assert result is not None
        assert result.level != DegradationLevel.NORMAL

    def test_degradation_action_fields(self):
        mgr = DegradationManager(anti_spiral_limit=5)
        result = mgr.evaluate(usage_ratio=0.85, dimension=BudgetDimension.COST)
        assert result is not None
        assert result.source_dimension == BudgetDimension.COST
        assert result.timestamp > 0
