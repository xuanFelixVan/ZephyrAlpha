# [A_test] module_id: SRC-TST-1314 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_notification_personalizer
# [INVARIANTS] personalize returns dict with personalized=True
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.actors.notification_personalizer import NotificationPersonalizer


class TestNotificationPersonalizerInstantiation:
    def test_default_construction(self):
        np = NotificationPersonalizer()
        assert np.owner_preferences == {}

    def test_custom_preferences(self):
        prefs = {"channel": "email", "severity_filter": ["critical", "warning"]}
        np = NotificationPersonalizer(owner_preferences=prefs)
        assert np.owner_preferences == prefs


class TestPersonalize:
    def test_returns_personalized_flag(self):
        np = NotificationPersonalizer()
        alert = {"message": "disk full", "severity": "critical"}
        result = np.personalize(alert)
        assert result["personalized"] is True
        assert result["message"] == "disk full"
        assert result["severity"] == "critical"

    def test_preserves_original_keys(self):
        np = NotificationPersonalizer()
        alert = {"a": 1, "b": 2}
        result = np.personalize(alert)
        assert result["a"] == 1
        assert result["b"] == 2
        assert result["personalized"] is True

    def test_empty_alert(self):
        np = NotificationPersonalizer()
        result = np.personalize({})
        assert result == {"personalized": True}

    def test_with_preferences_set(self):
        np = NotificationPersonalizer(owner_preferences={"channel": "sms"})
        result = np.personalize({"msg": "test"})
        assert result["personalized"] is True
        assert result["msg"] == "test"

    def test_does_not_mutate_input(self):
        np = NotificationPersonalizer()
        alert = {"message": "test"}
        original = dict(alert)
        np.personalize(alert)
        assert alert == original
