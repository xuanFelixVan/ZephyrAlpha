# [A_test] module_id: SRC-TST-0978 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_protocols
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.protocols
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_protocols.py
# [TTL] task_bound

from __future__ import annotations

from typing import Any

from zephyr.feedback_loop.protocols import ActionType, FeedbackProtocolAdapter


class TestActionType:
    def test_all_action_types_exist(self):
        expected = {"NOTIFY_OWNER", "ADJUST_THRESHOLD", "REPAIR", "DEPLOY", "SELF_UPGRADE", "REBALANCE"}
        actual = {at.value for at in ActionType}
        assert actual == expected

    def test_action_type_is_string_enum(self):
        assert isinstance(ActionType.REPAIR, str)
        assert ActionType.REPAIR.value == "REPAIR"

    def test_action_type_comparison(self):
        assert ActionType.REPAIR == "REPAIR"
        assert ActionType.NOTIFY_OWNER != ActionType.REPAIR


class TestFeedbackProtocolAdapter:
    def test_protocol_defines_dispatch_action(self):
        assert hasattr(FeedbackProtocolAdapter, "dispatch_action")

    def test_concrete_implementation(self):
        class StubAdapter:
            def dispatch_action(self, action_type: ActionType, payload: dict[str, Any]) -> bool:
                return True

        adapter = StubAdapter()
        assert adapter.dispatch_action(ActionType.REPAIR, {}) is True

    def test_concrete_implementation_returns_false(self):
        class FailingAdapter:
            def dispatch_action(self, action_type: ActionType, payload: dict[str, Any]) -> bool:
                return False

        adapter = FailingAdapter()
        assert adapter.dispatch_action(ActionType.REPAIR, {}) is False
