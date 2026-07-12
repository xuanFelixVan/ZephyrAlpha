# [A_test] module_id: SRC-TST-1313 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_notification_feedback
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.collectors.notification_feedback
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_notification_feedback.py
# [TTL] task_bound


from zephyr.feedback_loop.collectors.notification_feedback import NotificationFeedback


class TestNotificationFeedbackInstantiation:
    def test_default_responses_is_empty_list(self):
        nf = NotificationFeedback()
        assert nf.responses == []

    def test_responses_with_initial_data(self):
        initial = [{"id": "n1", "action": "ack"}]
        nf = NotificationFeedback(responses=initial)
        assert nf.responses == initial
        assert len(nf.responses) == 1


class TestNotificationFeedbackRecord:
    def test_record_appends_entry(self):
        nf = NotificationFeedback()
        nf.record("notif-001", "acknowledged")
        assert len(nf.responses) == 1
        assert nf.responses[0] == {"id": "notif-001", "action": "acknowledged"}

    def test_record_multiple_entries(self):
        nf = NotificationFeedback()
        nf.record("notif-001", "acknowledged")
        nf.record("notif-002", "dismissed")
        nf.record("notif-003", "escalated")
        assert len(nf.responses) == 3
        assert nf.responses[0]["id"] == "notif-001"
        assert nf.responses[1]["action"] == "dismissed"
        assert nf.responses[2]["id"] == "notif-003"

    def test_record_preserves_order(self):
        nf = NotificationFeedback()
        nf.record("a", "alpha")
        nf.record("b", "beta")
        nf.record("c", "gamma")
        ids = [r["id"] for r in nf.responses]
        assert ids == ["a", "b", "c"]


class TestNotificationFeedbackBoundaries:
    def test_record_empty_strings(self):
        nf = NotificationFeedback()
        nf.record("", "")
        assert nf.responses == [{"id": "", "action": ""}]

    def test_record_with_special_characters(self):
        nf = NotificationFeedback()
        nf.record("notif-特殊", "行动/动作")
        assert nf.responses[0]["id"] == "notif-特殊"
        assert nf.responses[0]["action"] == "行动/动作"

    def test_record_does_not_overwrite_previous(self):
        nf = NotificationFeedback()
        nf.record("n1", "ack")
        nf.record("n1", "dismiss")
        assert len(nf.responses) == 2
        assert nf.responses[0]["action"] == "ack"
        assert nf.responses[1]["action"] == "dismiss"
