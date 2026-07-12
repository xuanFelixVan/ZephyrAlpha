# [A_test] module_id: SRC-TST-1879 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
from zephyr.feedback_loop.protocols import ActionType, FeedbackProtocolAdapter


class TestActionType:
    def test_enum_values(self):
        assert ActionType.NOTIFY_OWNER.value == "NOTIFY_OWNER"
        assert ActionType.ADJUST_THRESHOLD.value == "ADJUST_THRESHOLD"
        assert ActionType.REPAIR.value == "REPAIR"
        assert ActionType.DEPLOY.value == "DEPLOY"
        assert ActionType.SELF_UPGRADE.value == "SELF_UPGRADE"
        assert ActionType.REBALANCE.value == "REBALANCE"

    def test_is_str_enum(self):
        assert isinstance(ActionType.NOTIFY_OWNER, str)

    def test_all_members(self):
        members = list(ActionType)
        assert len(members) == 6

    def test_from_value(self):
        assert ActionType("REPAIR") == ActionType.REPAIR


class TestFeedbackProtocolAdapter:
    def test_is_protocol(self):
        assert (
            hasattr(FeedbackProtocolAdapter, "__protocol_attrs__")
            or hasattr(FeedbackProtocolAdapter, "__abstractmethods__")
            or hasattr(FeedbackProtocolAdapter, "_is_protocol")
        )

    def test_concrete_implementation(self):
        class MockAdapter:
            def dispatch_action(self, action_type, payload):
                return True

        adapter = MockAdapter()
        assert adapter.dispatch_action(ActionType.NOTIFY_OWNER, {}) is True

    def test_dispatch_action_signature(self):
        import inspect

        sig = inspect.signature(FeedbackProtocolAdapter.dispatch_action)
        params = list(sig.parameters.keys())
        assert "self" in params
        assert "action_type" in params
        assert "payload" in params
