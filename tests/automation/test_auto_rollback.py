# [A_test] module_id: SRC-TST-0379 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_auto_rollback
# [INVARIANTS] should_rollback returns True when post < pre * 0.7
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_auto_rollback.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.verifiers.auto_rollback import AutoRollback


class TestAutoRollbackInstantiation:
    def test_default_construction(self):
        ar = AutoRollback()
        assert ar is not None


class TestShouldRollback:
    def test_should_rollback_severe_degradation(self):
        ar = AutoRollback()
        assert ar.should_rollback(pre_metric=100.0, post_metric=50.0) is True

    def test_should_not_rollback_minor_change(self):
        ar = AutoRollback()
        assert ar.should_rollback(pre_metric=100.0, post_metric=80.0) is False

    def test_boundary_exact_threshold(self):
        ar = AutoRollback()
        assert ar.should_rollback(pre_metric=100.0, post_metric=70.0) is False

    def test_just_below_threshold(self):
        ar = AutoRollback()
        assert ar.should_rollback(pre_metric=100.0, post_metric=69.99) is True

    def test_improvement(self):
        ar = AutoRollback()
        assert ar.should_rollback(pre_metric=50.0, post_metric=100.0) is False

    def test_zero_pre_metric(self):
        ar = AutoRollback()
        result = ar.should_rollback(pre_metric=0.0, post_metric=0.0)
        assert result is False

    def test_negative_metrics(self):
        ar = AutoRollback()
        result = ar.should_rollback(pre_metric=-10.0, post_metric=-8.0)
        assert isinstance(result, bool)
