# [A_test] module_id: SRC-TST-1025 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_fle_validator
# [INVARIANTS] validate_all returns dict[str, bool]; validate_one returns bool; missing_files returns list[str]
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import os
from unittest.mock import patch

from zephyr.feedback_loop.validator import BASE, missing_files, validate_all, validate_one


class TestValidatorInstantiation:
    def test_base_path_defined(self):
        assert BASE is not None
        assert isinstance(BASE, str)


class TestValidateOne:
    def test_returns_bool(self):
        result = validate_one("nonexistent_file.py")
        assert isinstance(result, bool)

    def test_nonexistent_file_returns_false(self):
        result = validate_one("__nonexistent_skeleton_12345__.py")
        assert result is False

    def test_existing_file_returns_true(self):
        this_file = os.path.relpath(__file__, BASE)
        this_file = this_file.replace("\\", "/")
        result = validate_one(this_file)
        assert result is True


class TestValidateAll:
    def test_returns_dict(self):
        result = validate_all()
        assert isinstance(result, dict)

    def test_values_are_bool(self):
        result = validate_all()
        for v in result.values():
            assert isinstance(v, bool)


class TestMissingFiles:
    def test_returns_list(self):
        result = missing_files()
        assert isinstance(result, list)

    def test_items_are_strings(self):
        result = missing_files()
        for item in result:
            assert isinstance(item, str)

    def test_missing_subset_of_skeletons(self):
        from zephyr.feedback_loop.template import SKELETONS

        result = missing_files()
        for path in result:
            assert path in SKELETONS


class TestValidatorWithMockedSKELETONS:
    def test_validate_all_with_empty_skeletons(self):
        with patch("zephyr.feedback_loop.validator.SKELETONS", {}):
            result = validate_all()
            assert result == {}

    def test_missing_files_with_empty_skeletons(self):
        with patch("zephyr.feedback_loop.validator.SKELETONS", {}):
            result = missing_files()
            assert result == []

    def test_validate_one_with_mocked_path(self):
        with patch("zephyr.feedback_loop.validator.os.path.exists", return_value=True):
            result = validate_one("mocked_file.py")
            assert result is True

    def test_validate_one_with_mocked_nonexistent(self):
        with patch("zephyr.feedback_loop.validator.os.path.exists", return_value=False):
            result = validate_one("mocked_file.py")
            assert result is False
