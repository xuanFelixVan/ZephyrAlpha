# [A_test] module_id: SRC-TST-1286 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_model_health
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.health.model_health
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_model_health.py
# [TTL] task_bound

import pytest

from zephyr.feedback_loop.diagnosers.health.model_health import ModelHealth


class TestModelHealthInstantiation:
    def test_required_model_id(self):
        mh = ModelHealth(model_id="gpt-4")
        assert mh.model_id == "gpt-4"

    def test_default_accuracy(self):
        mh = ModelHealth(model_id="gpt-4")
        assert mh.accuracy == 100.0

    def test_default_last_validation(self):
        mh = ModelHealth(model_id="gpt-4")
        assert mh.last_validation == 0.0

    def test_custom_values(self):
        mh = ModelHealth(model_id="claude-3", accuracy=92.5, last_validation=1700000000.0)
        assert mh.accuracy == 92.5
        assert mh.last_validation == 1700000000.0

    def test_missing_model_id_raises(self):
        with pytest.raises(TypeError):
            ModelHealth()


class TestDegraded:
    def test_not_degraded_at_threshold(self):
        mh = ModelHealth(model_id="m1", accuracy=85.0)
        assert mh.degraded is False

    def test_degraded_below_threshold(self):
        mh = ModelHealth(model_id="m1", accuracy=84.9)
        assert mh.degraded is True

    def test_not_degraded_at_full_accuracy(self):
        mh = ModelHealth(model_id="m1", accuracy=100.0)
        assert mh.degraded is False

    def test_degraded_at_zero_accuracy(self):
        mh = ModelHealth(model_id="m1", accuracy=0.0)
        assert mh.degraded is True

    def test_degraded_at_boundary_minus_epsilon(self):
        mh = ModelHealth(model_id="m1", accuracy=84.999)
        assert mh.degraded is True
