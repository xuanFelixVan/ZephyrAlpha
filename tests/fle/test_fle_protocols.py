# [A_test] module_id: SRC-TST-1020 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_fle_protocols
# [INVARIANTS] ActionType is str+Enum; FeedbackProtocolAdapter is a Protocol
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound


from zephyr.feedback_loop.protocols import ActionType, FeedbackProtocolAdapter


class TestActionTypeInstantiation:
    def test_all_members_exist(self):
        expected = {
            "NOTIFY_OWNER",
            "ADJUST_THRESHOLD",
            "REPAIR",
            "DEPLOY",
            "SELF_UPGRADE",
            "REBALANCE",
        }
        actual = {m.name for m in ActionType}
        assert actual == expected

    def test_string_values(self):
        assert ActionType.NOTIFY_OWNER.value == "NOTIFY_OWNER"
        assert ActionType.REPAIR.value == "REPAIR"
        assert ActionType.DEPLOY.value == "DEPLOY"

    def test_is_string_enum(self):
        assert isinstance(ActionType.NOTIFY_OWNER, str)
        assert ActionType.NOTIFY_OWNER == "NOTIFY_OWNER"

    def test_iteration(self):
        members = list(ActionType)
        assert len(members) == 6


class TestActionTypeComparison:
    def test_equality(self):
        assert ActionType.NOTIFY_OWNER == ActionType.NOTIFY_OWNER

    def test_inequality(self):
        assert ActionType.NOTIFY_OWNER != ActionType.REPAIR

    def test_string_comparison(self):
        assert ActionType.REPAIR == "REPAIR"


class TestFeedbackProtocolAdapter:
    def test_protocol_is_defined(self):
        assert FeedbackProtocolAdapter is not None

    def test_concrete_implementation(self):
        class MockAdapter:
            def dispatch_action(self, action_type, payload):
                return True

        adapter = MockAdapter()
        assert adapter.dispatch_action(ActionType.NOTIFY_OWNER, {}) is True

    def test_concrete_implementation_returns_false(self):
        class RejectingAdapter:
            def dispatch_action(self, action_type, payload):
                return False

        adapter = RejectingAdapter()
        assert adapter.dispatch_action(ActionType.REPAIR, {"key": "val"}) is False

    def test_dispatch_with_various_action_types(self):
        class LoggingAdapter:
            def __init__(self):
                self.calls = []

            def dispatch_action(self, action_type, payload):
                self.calls.append((action_type, payload))
                return True

        adapter = LoggingAdapter()
        for at in ActionType:
            adapter.dispatch_action(at, {"test": True})
        assert len(adapter.calls) == 6
