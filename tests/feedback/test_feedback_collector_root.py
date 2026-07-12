# [A_test] module_id: SRC-TST-2125 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_feedback_collector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.feedback_collector
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_feedback_collector_root.py
# [TTL] task_bound

import pytest

from zephyr.feedback_loop.feedback_collector import (
    ActionResult,
    FeedbackChannel,
    FeedbackCollector,
    OwnerAck,
    OwnerResponse,
)


class TestFeedbackChannel:
    def test_enum_values(self):
        assert FeedbackChannel.ACTION_RESULT == "action_result"
        assert FeedbackChannel.OWNER_ACK == "owner_ack"

    def test_is_str_enum(self):
        assert isinstance(FeedbackChannel.ACTION_RESULT, str)


class TestOwnerResponse:
    def test_enum_values(self):
        assert OwnerResponse.ACK == "ack"
        assert OwnerResponse.OVERRIDE == "override"
        assert OwnerResponse.IGNORE == "ignore"

    def test_is_str_enum(self):
        assert isinstance(OwnerResponse.ACK, str)

    def test_all_three_members(self):
        assert len(OwnerResponse) == 3


class TestActionResult:
    def test_instantiation_with_all_fields(self):
        ar = ActionResult(
            action_type="repair",
            anomaly_id="anom-001",
            pre_value=100.0,
            post_value=90.0,
            success_flag=True,
            timestamp=1000.0,
        )
        assert ar.action_type == "repair"
        assert ar.anomaly_id == "anom-001"
        assert ar.pre_value == 100.0
        assert ar.post_value == 90.0
        assert ar.success_flag is True
        assert ar.timestamp == 1000.0

    def test_delta_computed_from_pre_and_post(self):
        ar = ActionResult(
            action_type="repair",
            anomaly_id="anom-002",
            pre_value=100.0,
            post_value=80.0,
            success_flag=True,
            timestamp=0.0,
        )
        assert ar.delta == pytest.approx(-20.0)

    def test_delta_zero_when_pre_equals_post(self):
        ar = ActionResult(
            action_type="noop",
            anomaly_id="anom-003",
            pre_value=50.0,
            post_value=50.0,
            success_flag=False,
            timestamp=0.0,
        )
        assert ar.delta == pytest.approx(0.0)

    def test_delta_positive_when_post_greater(self):
        ar = ActionResult(
            action_type="scale_up",
            anomaly_id="anom-004",
            pre_value=10.0,
            post_value=25.0,
            success_flag=True,
            timestamp=0.0,
        )
        assert ar.delta == pytest.approx(15.0)

    def test_missing_required_field_raises(self):
        with pytest.raises(TypeError):
            ActionResult(action_type="repair", anomaly_id="anom-005")


class TestOwnerAck:
    def test_instantiation_with_all_fields(self):
        ack = OwnerAck(
            anomaly_id="anom-001",
            response=OwnerResponse.ACK,
            timestamp=1000.0,
            note="confirmed",
        )
        assert ack.anomaly_id == "anom-001"
        assert ack.response == OwnerResponse.ACK
        assert ack.timestamp == 1000.0
        assert ack.note == "confirmed"

    def test_default_note_is_empty(self):
        ack = OwnerAck(
            anomaly_id="anom-002",
            response=OwnerResponse.IGNORE,
            timestamp=0.0,
        )
        assert ack.note == ""

    def test_missing_required_field_raises(self):
        with pytest.raises(TypeError):
            OwnerAck(anomaly_id="anom-003", response=OwnerResponse.ACK)


class TestFeedbackCollector:
    def test_instantiation_default_window(self):
        fc = FeedbackCollector()
        assert fc.window_seconds == 300.0
        assert len(fc.action_results) == 0
        assert len(fc.owner_acks) == 0

    def test_instantiation_custom_window(self):
        fc = FeedbackCollector(window_seconds=60.0)
        assert fc.window_seconds == 60.0

    def test_collect_action_result_appends(self):
        fc = FeedbackCollector()
        ar = ActionResult(
            action_type="repair",
            anomaly_id="anom-001",
            pre_value=100.0,
            post_value=90.0,
            success_flag=True,
            timestamp=1000.0,
        )
        fc.collect_action_result(ar)
        assert len(fc.action_results) == 1
        assert fc.action_results[0].anomaly_id == "anom-001"

    def test_collect_owner_ack_appends(self):
        fc = FeedbackCollector()
        ack = OwnerAck(
            anomaly_id="anom-001",
            response=OwnerResponse.ACK,
            timestamp=1000.0,
        )
        fc.collect_owner_ack(ack)
        assert len(fc.owner_acks) == 1
        assert fc.owner_acks[0].anomaly_id == "anom-001"

    def test_repair_failure_rate_empty(self):
        fc = FeedbackCollector()
        assert fc.repair_failure_rate() == 0.0

    def test_repair_failure_rate_all_success(self):
        fc = FeedbackCollector()
        for i in range(5):
            fc.collect_action_result(
                ActionResult(
                    action_type="repair",
                    anomaly_id=f"anom-{i}",
                    pre_value=100.0,
                    post_value=90.0,
                    success_flag=True,
                    timestamp=1000.0 + i,
                )
            )
        assert fc.repair_failure_rate() == pytest.approx(0.0)

    def test_repair_failure_rate_mixed(self):
        fc = FeedbackCollector()
        fc.collect_action_result(
            ActionResult(
                action_type="repair",
                anomaly_id="a1",
                pre_value=100.0,
                post_value=90.0,
                success_flag=True,
                timestamp=1000.0,
            )
        )
        fc.collect_action_result(
            ActionResult(
                action_type="repair",
                anomaly_id="a2",
                pre_value=100.0,
                post_value=100.0,
                success_flag=False,
                timestamp=1001.0,
            )
        )
        assert fc.repair_failure_rate() == pytest.approx(0.5)

    def test_repair_failure_rate_all_fail(self):
        fc = FeedbackCollector()
        for i in range(3):
            fc.collect_action_result(
                ActionResult(
                    action_type="repair",
                    anomaly_id=f"anom-{i}",
                    pre_value=100.0,
                    post_value=100.0,
                    success_flag=False,
                    timestamp=1000.0 + i,
                )
            )
        assert fc.repair_failure_rate() == pytest.approx(1.0)

    def test_owner_override_rate_empty(self):
        fc = FeedbackCollector()
        assert fc.owner_override_rate() == 0.0

    def test_owner_override_rate_all_ack(self):
        fc = FeedbackCollector()
        for i in range(4):
            fc.collect_owner_ack(
                OwnerAck(
                    anomaly_id=f"anom-{i}",
                    response=OwnerResponse.ACK,
                    timestamp=1000.0 + i,
                )
            )
        assert fc.owner_override_rate() == pytest.approx(0.0)

    def test_owner_override_rate_mixed(self):
        fc = FeedbackCollector()
        fc.collect_owner_ack(
            OwnerAck(
                anomaly_id="a1",
                response=OwnerResponse.ACK,
                timestamp=1000.0,
            )
        )
        fc.collect_owner_ack(
            OwnerAck(
                anomaly_id="a2",
                response=OwnerResponse.OVERRIDE,
                timestamp=1001.0,
            )
        )
        assert fc.owner_override_rate() == pytest.approx(0.5)

    def test_window_trims_old_action_results(self):
        fc = FeedbackCollector(window_seconds=10.0)
        fc.collect_action_result(
            ActionResult(
                action_type="repair",
                anomaly_id="old",
                pre_value=100.0,
                post_value=90.0,
                success_flag=True,
                timestamp=0.0,
            )
        )
        fc.collect_action_result(
            ActionResult(
                action_type="repair",
                anomaly_id="new",
                pre_value=100.0,
                post_value=90.0,
                success_flag=True,
                timestamp=20.0,
            )
        )
        ids = [ar.anomaly_id for ar in fc.action_results]
        assert "old" not in ids
        assert "new" in ids

    def test_window_trims_old_owner_acks(self):
        fc = FeedbackCollector(window_seconds=10.0)
        fc.collect_action_result(
            ActionResult(
                action_type="repair",
                anomaly_id="anchor",
                pre_value=100.0,
                post_value=90.0,
                success_flag=True,
                timestamp=20.0,
            )
        )
        fc.collect_owner_ack(
            OwnerAck(
                anomaly_id="old",
                response=OwnerResponse.ACK,
                timestamp=0.0,
            )
        )
        fc.collect_owner_ack(
            OwnerAck(
                anomaly_id="new",
                response=OwnerResponse.ACK,
                timestamp=20.0,
            )
        )
        ids = [a.anomaly_id for a in fc.owner_acks]
        assert "old" not in ids
        assert "new" in ids
