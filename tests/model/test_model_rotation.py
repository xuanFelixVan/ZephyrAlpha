# [A_test] module_id: SRC-TST-1287 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_model_rotation
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.model_rotation
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_model_rotation.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.model_rotation import ModelRotation


class TestModelRotationInstantiation:
    def test_default_instantiation(self):
        mr = ModelRotation()
        assert mr.models == []
        assert mr.active == ""

    def test_custom_instantiation(self):
        mr = ModelRotation(models=["a", "b", "c"], active="a")
        assert len(mr.models) == 3
        assert mr.active == "a"


class TestRotate:
    def test_rotate_single_model(self):
        mr = ModelRotation(models=["only"], active="only")
        result = mr.rotate()
        assert result == "only"

    def test_rotate_two_models(self):
        mr = ModelRotation(models=["a", "b"], active="a")
        result = mr.rotate()
        assert result == "b"

    def test_rotate_wraps_around(self):
        mr = ModelRotation(models=["a", "b", "c"], active="c")
        result = mr.rotate()
        assert result == "a"

    def test_rotate_empty_models_returns_active(self):
        mr = ModelRotation(models=[], active="")
        result = mr.rotate()
        assert result == ""

    def test_rotate_active_not_in_models_starts_at_zero(self):
        mr = ModelRotation(models=["x", "y"], active="z")
        result = mr.rotate()
        assert result == "x"

    def test_rotate_updates_active(self):
        mr = ModelRotation(models=["a", "b", "c"], active="a")
        mr.rotate()
        assert mr.active == "b"

    def test_rotate_full_cycle(self):
        mr = ModelRotation(models=["a", "b"], active="a")
        assert mr.rotate() == "b"
        assert mr.rotate() == "a"

    def test_rotate_empty_active_with_models(self):
        mr = ModelRotation(models=["a", "b"], active="")
        result = mr.rotate()
        assert result == "a"
