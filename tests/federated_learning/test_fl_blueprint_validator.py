# [A_test] module_id: SRC-TST-0938 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_blueprint_validator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.blueprint_validator
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_blueprint_validator.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.blueprint_validator import BlueprintValidator


class TestBlueprintValidatorInstantiation:
    def test_default_construction(self):
        bv = BlueprintValidator()
        assert bv is not None


class TestValidate:
    def test_validate_matching_counts(self):
        bv = BlueprintValidator()
        result = bv.validate(["a.py", "b.py"], ["a.py", "b.py"])
        assert result == 1.0

    def test_validate_mismatched_counts(self):
        bv = BlueprintValidator()
        result = bv.validate(["a.py"], ["a.py", "b.py"])
        assert result == 0.5

    def test_validate_empty_both(self):
        bv = BlueprintValidator()
        result = bv.validate([], [])
        assert result == 1.0


class TestBoundaries:
    def test_validate_empty_blueprint(self):
        bv = BlueprintValidator()
        result = bv.validate([], ["a.py"])
        assert result == 0.5

    def test_validate_empty_code(self):
        bv = BlueprintValidator()
        result = bv.validate(["a.py"], [])
        assert result == 0.5
