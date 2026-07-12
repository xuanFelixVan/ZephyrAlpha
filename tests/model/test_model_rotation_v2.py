# [A_test] module_id: SRC-TST-1288 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_model_rotation_v2
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.model_rotation_v2
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_model_rotation_v2.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.model_rotation_v2 import ModelRotationV2


class TestModelRotationV2Instantiation:
    def test_default_instantiation(self):
        mr = ModelRotationV2()
        assert mr.models == {}

    def test_custom_instantiation(self):
        mr = ModelRotationV2(models={"a": 0.9, "b": 0.5})
        assert len(mr.models) == 2


class TestSelect:
    def test_select_highest_weight(self):
        mr = ModelRotationV2(models={"a": 0.3, "b": 0.9, "c": 0.5})
        result = mr.select()
        assert result == "b"

    def test_select_empty_models(self):
        mr = ModelRotationV2(models={})
        result = mr.select()
        assert result == ""

    def test_select_single_model(self):
        mr = ModelRotationV2(models={"only": 0.7})
        result = mr.select()
        assert result == "only"

    def test_select_equal_weights(self):
        mr = ModelRotationV2(models={"a": 0.5, "b": 0.5})
        result = mr.select()
        assert result in ("a", "b")

    def test_select_zero_weight_model(self):
        mr = ModelRotationV2(models={"a": 0.0, "b": 0.1})
        result = mr.select()
        assert result == "b"

    def test_select_negative_weight(self):
        mr = ModelRotationV2(models={"a": -0.5, "b": -0.1})
        result = mr.select()
        assert result == "b"

    def test_select_all_zero_weights(self):
        mr = ModelRotationV2(models={"a": 0.0, "b": 0.0})
        result = mr.select()
        assert result in ("a", "b")
