# [A_test] module_id: SRC-TST-1753 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_tone_adapter_v2
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.tone_adapter_v2
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_tone_adapter_v2.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.tone_adapter_v2 import ToneAdapterV2


class TestToneAdapterV2Instantiation:
    def test_default_channels(self):
        ta = ToneAdapterV2()
        assert ta.channels == ["email", "sms", "push"]

    def test_custom_channels(self):
        ta = ToneAdapterV2(channels=["slack", "pager"])
        assert ta.channels == ["slack", "pager"]

    def test_empty_channels(self):
        ta = ToneAdapterV2(channels=[])
        assert ta.channels == []

    def test_is_dataclass(self):
        ta = ToneAdapterV2()
        assert hasattr(ta, "__dataclass_fields__")


class TestRoute:
    def test_low_severity_first_channel_only(self):
        ta = ToneAdapterV2(channels=["email", "sms", "push"])
        result = ta.route(severity=3)
        assert result == ["email"]

    def test_high_severity_all_channels(self):
        ta = ToneAdapterV2(channels=["email", "sms", "push"])
        result = ta.route(severity=9)
        assert result == ["email", "sms", "push"]

    def test_boundary_severity_eight(self):
        ta = ToneAdapterV2(channels=["email", "sms", "push"])
        result = ta.route(severity=8)
        assert result == ["email"]

    def test_boundary_severity_nine(self):
        ta = ToneAdapterV2(channels=["email", "sms", "push"])
        result = ta.route(severity=9)
        assert result == ["email", "sms", "push"]

    def test_zero_severity(self):
        ta = ToneAdapterV2(channels=["email", "sms", "push"])
        result = ta.route(severity=0)
        assert result == ["email"]

    def test_single_channel(self):
        ta = ToneAdapterV2(channels=["slack"])
        result = ta.route(severity=3)
        assert result == ["slack"]

    def test_empty_channels_returns_empty(self):
        ta = ToneAdapterV2(channels=[])
        result = ta.route(severity=9)
        assert result == []

    def test_returns_list(self):
        ta = ToneAdapterV2()
        result = ta.route(severity=5)
        assert isinstance(result, list)

    def test_negative_severity(self):
        ta = ToneAdapterV2(channels=["email", "sms"])
        result = ta.route(severity=-1)
        assert result == ["email"]
