# [A_test] module_id: SRC-TST-0482 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_canary_manager
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_canary_manager.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.orchestrator.fault_tolerance.canary_manager import CanaryManager


class TestCanaryManagerInstantiation:
    def test_default_construction(self):
        cm = CanaryManager()
        assert cm is not None

    def test_default_weight(self):
        cm = CanaryManager()
        assert cm._canary_weight == 0.1


class TestCanaryManagerSetWeight:
    def test_set_weight_normal(self):
        cm = CanaryManager()
        cm.set_weight(0.5)
        assert cm._canary_weight == 0.5

    def test_set_weight_zero(self):
        cm = CanaryManager()
        cm.set_weight(0.0)
        assert cm._canary_weight == 0.0

    def test_set_weight_one(self):
        cm = CanaryManager()
        cm.set_weight(1.0)
        assert cm._canary_weight == 1.0

    def test_set_weight_above_one_clamped(self):
        cm = CanaryManager()
        cm.set_weight(2.0)
        assert cm._canary_weight == 1.0

    def test_set_weight_below_zero_clamped(self):
        cm = CanaryManager()
        cm.set_weight(-0.5)
        assert cm._canary_weight == 0.0

    def test_set_weight_small_positive(self):
        cm = CanaryManager()
        cm.set_weight(0.01)
        assert cm._canary_weight == pytest.approx(0.01)


class TestCanaryManagerShouldRollback:
    def test_rollback_when_above_double_baseline(self):
        cm = CanaryManager()
        assert cm.should_rollback(0.21, 0.1) is True

    def test_no_rollback_at_exact_double(self):
        cm = CanaryManager()
        assert cm.should_rollback(0.2, 0.1) is False

    def test_no_rollback_below_double(self):
        cm = CanaryManager()
        assert cm.should_rollback(0.19, 0.1) is False

    def test_no_rollback_zero_error_rate(self):
        cm = CanaryManager()
        assert cm.should_rollback(0.0, 0.1) is False

    def test_rollback_zero_baseline_any_error(self):
        cm = CanaryManager()
        assert cm.should_rollback(0.01, 0.0) is True

    def test_rollback_high_error_rate(self):
        cm = CanaryManager()
        assert cm.should_rollback(1.0, 0.05) is True

    def test_rollback_equal_error_and_baseline(self):
        cm = CanaryManager()
        assert cm.should_rollback(0.1, 0.1) is False


class TestCanaryManagerPromote:
    def test_promote_sets_weight_to_one(self):
        cm = CanaryManager()
        cm.set_weight(0.1)
        cm.promote()
        assert cm._canary_weight == 1.0

    def test_promote_from_zero(self):
        cm = CanaryManager()
        cm.set_weight(0.0)
        cm.promote()
        assert cm._canary_weight == 1.0

    def test_promote_idempotent(self):
        cm = CanaryManager()
        cm.promote()
        cm.promote()
        assert cm._canary_weight == 1.0
