# [A_test] module_id: SRC-TST-0443 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_blueprint_validator
# [INVARIANTS] Validation score must be 1.0 or 0.5 based on file count match
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.blueprint_validator import BlueprintValidator


class TestBlueprintValidatorInstantiation:
    def test_default_creation(self):
        bv = BlueprintValidator()
        assert bv is not None


class TestValidate:
    def test_matching_counts_returns_1(self):
        bv = BlueprintValidator()
        score = bv.validate(["bp1.md", "bp2.md"], ["code1.py", "code2.py"])
        assert score == 1.0

    def test_mismatched_counts_returns_05(self):
        bv = BlueprintValidator()
        score = bv.validate(["bp1.md"], ["code1.py", "code2.py"])
        assert score == 0.5

    def test_empty_both_returns_1(self):
        bv = BlueprintValidator()
        score = bv.validate([], [])
        assert score == 1.0

    def test_empty_blueprint_nonempty_code_returns_05(self):
        bv = BlueprintValidator()
        score = bv.validate([], ["code1.py"])
        assert score == 0.5

    def test_nonempty_blueprint_empty_code_returns_05(self):
        bv = BlueprintValidator()
        score = bv.validate(["bp1.md"], [])
        assert score == 0.5
