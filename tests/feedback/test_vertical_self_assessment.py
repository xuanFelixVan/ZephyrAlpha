# [A_test] module_id: SRC-TST-1790 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_vertical_self_assessment
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.vertical_self_assessment
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_vertical_self_assessment.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.vertical_self_assessment import VerticalSelfAssessment


class TestVerticalSelfAssessmentInstantiation:
    def test_default_params(self):
        vsa = VerticalSelfAssessment()
        assert vsa.maturity_level == 0

    def test_custom_maturity(self):
        vsa = VerticalSelfAssessment(maturity_level=3)
        assert vsa.maturity_level == 3

    def test_is_dataclass(self):
        vsa = VerticalSelfAssessment()
        assert hasattr(vsa, "__dataclass_fields__")


class TestAssess:
    def test_returns_string(self):
        vsa = VerticalSelfAssessment()
        result = vsa.assess()
        assert isinstance(result, str)

    def test_default_level_zero(self):
        vsa = VerticalSelfAssessment()
        result = vsa.assess()
        assert result == "L0"

    def test_level_one(self):
        vsa = VerticalSelfAssessment(maturity_level=1)
        assert vsa.assess() == "L1"

    def test_level_five(self):
        vsa = VerticalSelfAssessment(maturity_level=5)
        assert vsa.assess() == "L5"

    def test_high_level(self):
        vsa = VerticalSelfAssessment(maturity_level=10)
        assert vsa.assess() == "L10"

    def test_negative_level(self):
        vsa = VerticalSelfAssessment(maturity_level=-1)
        result = vsa.assess()
        assert isinstance(result, str)
        assert "L" in result

    def test_format_contains_l_prefix(self):
        vsa = VerticalSelfAssessment(maturity_level=3)
        result = vsa.assess()
        assert result.startswith("L")
