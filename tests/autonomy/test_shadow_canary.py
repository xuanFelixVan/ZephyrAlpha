# [A_test] module_id: MOD-GOV_shadow_canary | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_shadow_canary
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_shadow_canary.py
# [TTL] task_bound

import pytest

from zephyr.autonomy_core.context.shadow_canary import (
    CanaryResult,
    ShadowCanary,
)


class TestCanaryResult:
    def test_instantiation_defaults(self):
        cr = CanaryResult(strategy_name="test", shadow_generated=True)
        assert cr.strategy_name == "test"
        assert cr.shadow_generated is True
        assert cr.performance_delta == 0.0
        assert cr.promoted is False

    def test_instantiation_custom(self):
        cr = CanaryResult(
            strategy_name="v2",
            shadow_generated=True,
            performance_delta=5.0,
            promoted=True,
        )
        assert cr.performance_delta == 5.0
        assert cr.promoted is True

    def test_missing_required_field_raises(self):
        with pytest.raises(TypeError):
            CanaryResult()


class TestShadowCanary:
    def test_instantiation(self):
        sc = ShadowCanary()
        assert sc is not None

    def test_shadow_returns_canary_result(self):
        sc = ShadowCanary()
        result = sc.shadow("strategy_v2", "some context")
        assert isinstance(result, CanaryResult)
        assert result.strategy_name == "strategy_v2"
        assert result.shadow_generated is True

    def test_shadow_default_performance_delta(self):
        sc = ShadowCanary()
        result = sc.shadow("test", "ctx")
        assert result.performance_delta == 0.0
        assert result.promoted is False

    def test_promote_below_threshold(self):
        sc = ShadowCanary()
        result = CanaryResult(strategy_name="test", shadow_generated=True, performance_delta=2.0)
        assert sc.promote(result) is False

    def test_promote_above_threshold(self):
        sc = ShadowCanary()
        result = CanaryResult(strategy_name="test", shadow_generated=True, performance_delta=4.0)
        assert sc.promote(result) is True

    def test_promote_exactly_at_threshold(self):
        sc = ShadowCanary()
        result = CanaryResult(strategy_name="test", shadow_generated=True, performance_delta=3.0)
        assert sc.promote(result) is False

    def test_promote_negative_delta(self):
        sc = ShadowCanary()
        result = CanaryResult(strategy_name="test", shadow_generated=True, performance_delta=-1.0)
        assert sc.promote(result) is False
