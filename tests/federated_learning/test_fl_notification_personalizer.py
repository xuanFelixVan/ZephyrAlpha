# [A_test] module_id: SRC-TST-0975 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_notification_personalizer
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.actors.notification_personalizer
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_notification_personalizer.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.actors.notification_personalizer import NotificationPersonalizer


class TestNotificationPersonalizerInstantiation:
    def test_creates_with_defaults(self):
        np = NotificationPersonalizer()
        assert np.owner_preferences == {}

    def test_creates_with_preferences(self):
        np = NotificationPersonalizer(owner_preferences={"channel": "slack"})
        assert np.owner_preferences["channel"] == "slack"


class TestPersonalize:
    def test_personalize_adds_flag(self):
        np = NotificationPersonalizer()
        result = np.personalize({"severity": "high", "message": "alert"})
        assert result["personalized"] is True
        assert result["severity"] == "high"

    def test_personalize_preserves_original_keys(self):
        np = NotificationPersonalizer()
        result = np.personalize({"key1": "val1", "key2": "val2"})
        assert result["key1"] == "val1"
        assert result["key2"] == "val2"

    def test_boundary_empty_alert(self):
        np = NotificationPersonalizer()
        result = np.personalize({})
        assert result["personalized"] is True

    def test_boundary_none_values_in_alert(self):
        np = NotificationPersonalizer()
        result = np.personalize({"severity": None})
        assert result["severity"] is None
        assert result["personalized"] is True
