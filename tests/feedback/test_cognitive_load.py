# [A_test] module_id: SRC-TST-0540 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_cognitive_load
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.cognitive.cognitive_load
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_cognitive_load.py
# [TTL] task_bound

import pytest

from zephyr.feedback_loop.diagnosers.cognitive.cognitive_load import CognitiveLoad


class TestCognitiveLoad:
    def test_instantiation_default(self):
        cl = CognitiveLoad()
        assert cl.notifications_per_hour == 0.0
        assert cl.fatigue_score == 0.0

    def test_instantiation_custom(self):
        cl = CognitiveLoad(notifications_per_hour=5.0, fatigue_score=0.3)
        assert cl.notifications_per_hour == 5.0
        assert cl.fatigue_score == 0.3

    def test_update_zero_notifications(self):
        cl = CognitiveLoad()
        cl.update(new_notifications=0)
        assert cl.notifications_per_hour == 0
        assert cl.fatigue_score == 0.0

    def test_update_single_notification(self):
        cl = CognitiveLoad()
        cl.update(new_notifications=1)
        assert cl.notifications_per_hour == 1
        assert cl.fatigue_score == pytest.approx(0.1)

    def test_update_multiple_notifications(self):
        cl = CognitiveLoad()
        cl.update(new_notifications=5)
        assert cl.notifications_per_hour == 5
        assert cl.fatigue_score == pytest.approx(0.5)

    def test_update_accumulates_fatigue(self):
        cl = CognitiveLoad()
        cl.update(new_notifications=3)
        cl.update(new_notifications=4)
        assert cl.fatigue_score == pytest.approx(0.3 + 0.4)

    def test_update_fatigue_capped_at_one(self):
        cl = CognitiveLoad()
        cl.update(new_notifications=20)
        assert cl.fatigue_score == 1.0

    def test_update_fatigue_does_not_exceed_one(self):
        cl = CognitiveLoad(fatigue_score=0.95)
        cl.update(new_notifications=2)
        assert cl.fatigue_score == 1.0

    def test_update_replaces_notifications_per_hour(self):
        cl = CognitiveLoad(notifications_per_hour=10.0)
        cl.update(new_notifications=3)
        assert cl.notifications_per_hour == 3

    def test_update_negative_notifications(self):
        cl = CognitiveLoad()
        cl.update(new_notifications=-5)
        assert cl.notifications_per_hour == -5
        assert cl.fatigue_score == pytest.approx(-0.5)

    def test_update_large_notification_count(self):
        cl = CognitiveLoad()
        cl.update(new_notifications=100)
        assert cl.fatigue_score == 1.0

    def test_update_sequential_accumulation(self):
        cl = CognitiveLoad()
        for i in range(5):
            cl.update(new_notifications=1)
        assert cl.fatigue_score == pytest.approx(0.5)

    def test_update_preserves_previous_fatigue(self):
        cl = CognitiveLoad(fatigue_score=0.5)
        cl.update(new_notifications=2)
        assert cl.fatigue_score == pytest.approx(0.7)

    def test_update_float_notifications(self):
        cl = CognitiveLoad()
        cl.update(new_notifications=3)
        assert isinstance(cl.notifications_per_hour, int)
