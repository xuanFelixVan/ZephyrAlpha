# [A_test] module_id: SRC-TST-1778 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §3-§9
# [MODULE] tests.test_validator
# [INVARIANTS] MOD-FEEDBACK_LOOP 检测-诊断-动作链不可绕过; GateQueue 全局串行
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FeedbackLoopError
# [TESTS] tests/test_validator.py
# [TTL] task_bound

from zephyr.feedback_loop.template import SKELETONS
from zephyr.feedback_loop.validator import BASE, missing_files, validate_all, validate_one


class TestBASE:
    def test_base_is_string(self):
        assert isinstance(BASE, str)

    def test_base_points_to_feedback_loop(self):
        assert "feedback-loop" in BASE


class TestMissingFiles:
    def test_returns_list(self):
        result = missing_files()
        assert isinstance(result, list)

    def test_all_entries_are_strings(self):
        result = missing_files()
        for entry in result:
            assert isinstance(entry, str)

    def test_missing_subset_of_skeletons(self):
        result = missing_files()
        for entry in result:
            assert entry in SKELETONS


class TestValidateOne:
    def test_returns_bool(self):
        if len(SKELETONS) > 0:
            first_key = next(iter(SKELETONS))
            result = validate_one(first_key)
            assert isinstance(result, bool)

    def test_nonexistent_file_returns_false(self):
        result = validate_one("nonexistent_file_xyz.py")
        assert result is False

    def test_empty_string_returns_true_for_base(self):
        result = validate_one("")
        assert isinstance(result, bool)


class TestValidateAll:
    def test_returns_dict(self):
        result = validate_all()
        assert isinstance(result, dict)

    def test_all_skeletons_covered(self):
        result = validate_all()
        for rel_path in SKELETONS:
            assert rel_path in result

    def test_all_values_are_bool(self):
        result = validate_all()
        for key, value in result.items():
            assert isinstance(value, bool)

    def test_consistent_with_validate_one(self):
        result = validate_all()
        for rel_path, exists in result.items():
            assert exists == validate_one(rel_path)

    def test_consistent_with_missing_files(self):
        result = validate_all()
        missing = missing_files()
        for rel_path in missing:
            assert result[rel_path] is False
