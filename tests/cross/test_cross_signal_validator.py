# [A_test] module_id: SRC-TST-0654 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_cross_signal_validator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_cross_signal_validator.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.cross_signal_validator import CrossSignalValidator


class TestCrossSignalValidatorInstantiation:
    def test_default_instantiation(self):
        validator = CrossSignalValidator()
        assert validator is not None

    def test_is_dataclass(self):
        validator = CrossSignalValidator()
        assert hasattr(validator, "__dataclass_fields__")


class TestValidate:
    def test_all_corroborating_within_threshold(self):
        validator = CrossSignalValidator()
        result = validator.validate(primary=10.0, corroborating=[9.0, 11.0, 8.0])
        assert result is True

    def test_one_corroborating_outside_threshold(self):
        validator = CrossSignalValidator()
        result = validator.validate(primary=10.0, corroborating=[9.0, 20.0])
        assert result is False

    def test_all_corroborating_outside_threshold(self):
        validator = CrossSignalValidator()
        result = validator.validate(primary=10.0, corroborating=[20.0, 30.0])
        assert result is False

    def test_empty_corroborating_list(self):
        validator = CrossSignalValidator()
        result = validator.validate(primary=10.0, corroborating=[])
        assert result is True

    def test_single_corroborating_within(self):
        validator = CrossSignalValidator()
        result = validator.validate(primary=5.0, corroborating=[6.0])
        assert result is True

    def test_single_corroborating_outside(self):
        validator = CrossSignalValidator()
        result = validator.validate(primary=5.0, corroborating=[10.0])
        assert result is False

    def test_zero_primary(self):
        validator = CrossSignalValidator()
        result = validator.validate(primary=0.0, corroborating=[0.0])
        assert result is False

    def test_negative_primary(self):
        validator = CrossSignalValidator()
        result = validator.validate(primary=-10.0, corroborating=[-9.0, -11.0])
        assert result is False

    def test_boundary_exact_half(self):
        validator = CrossSignalValidator()
        result = validator.validate(primary=10.0, corroborating=[15.0])
        assert result is False

    def test_small_primary_near_zero(self):
        validator = CrossSignalValidator()
        result = validator.validate(primary=0.01, corroborating=[0.005])
        assert result is False
