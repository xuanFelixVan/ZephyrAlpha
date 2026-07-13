# [A_test] module_id: SRC-TST-1752 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_tone_adapter
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.cognitive.tone_adapter
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_tone_adapter.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.cognitive.tone_adapter import ToneAdapter


class TestToneAdapterInstantiation:
    def test_default_params(self):
        ta = ToneAdapter()
        assert ta.severity == 0

    def test_custom_severity(self):
        ta = ToneAdapter(severity=5)
        assert ta.severity == 5

    def test_is_dataclass(self):
        ta = ToneAdapter()
        assert hasattr(ta, "__dataclass_fields__")


class TestAdapt:
    def test_low_severity_returns_standard(self):
        ta = ToneAdapter()
        result = ta.adapt(severity=3, owner_fatigue=0.1)
        assert result == "standard"

    def test_high_severity_returns_urgent(self):
        ta = ToneAdapter()
        result = ta.adapt(severity=8, owner_fatigue=0.1)
        assert result == "urgent"

    def test_boundary_severity_seven(self):
        ta = ToneAdapter()
        result = ta.adapt(severity=7, owner_fatigue=0.5)
        assert result == "standard"

    def test_boundary_severity_eight(self):
        ta = ToneAdapter()
        result = ta.adapt(severity=8, owner_fatigue=0.5)
        assert result == "urgent"

    def test_zero_severity(self):
        ta = ToneAdapter()
        result = ta.adapt(severity=0, owner_fatigue=0.0)
        assert result == "standard"

    def test_max_severity(self):
        ta = ToneAdapter()
        result = ta.adapt(severity=10, owner_fatigue=1.0)
        assert result == "urgent"

    def test_returns_string(self):
        ta = ToneAdapter()
        result = ta.adapt(severity=5, owner_fatigue=0.5)
        assert isinstance(result, str)

    def test_negative_severity(self):
        ta = ToneAdapter()
        result = ta.adapt(severity=-1, owner_fatigue=0.0)
        assert result == "standard"
