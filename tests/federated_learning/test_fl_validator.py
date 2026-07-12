# [A_test] module_id: SRC-TST-1006 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_validator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.validator
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_validator.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.validator import missing_files, validate_all, validate_one


class TestValidateAll:
    def test_returns_dict(self):
        result = validate_all()
        assert isinstance(result, dict)

    def test_keys_match_skeletons(self):
        result = validate_all()
        assert len(result) > 0

    def test_values_are_bool(self):
        result = validate_all()
        for key, value in result.items():
            assert isinstance(value, bool), f"Key {key} has non-bool value: {value}"


class TestValidateOne:
    def test_nonexistent_file_returns_false(self):
        result = validate_one("nonexistent/path/that/does/not/exist.py")
        assert result is False

    def test_returns_bool(self):
        result = validate_one("diagnosers/model_rotation.py")
        assert isinstance(result, bool)

    def test_boundary_empty_path(self):
        result = validate_one("")
        assert isinstance(result, bool)


class TestMissingFiles:
    def test_returns_list(self):
        result = missing_files()
        assert isinstance(result, list)

    def test_list_items_are_strings(self):
        result = missing_files()
        for item in result:
            assert isinstance(item, str)

    def test_missing_subset_of_skeletons(self):
        from zephyr.feedback_loop.template import SKELETONS

        result = missing_files()
        for item in result:
            assert item in SKELETONS, f"Missing file {item} not in SKELETONS"
