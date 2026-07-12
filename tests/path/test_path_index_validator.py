# [A_test] module_id: SRC-TST-1361 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_path_index_validator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
from zephyr.gov_code_quality.code_dedup.path_index_validator import (
    PathIndexValidator,
)


class TestPathIndexValidator:
    def test_instantiation(self):
        validator = PathIndexValidator()
        assert validator is not None

    def test_validate_returns_list(self):
        validator = PathIndexValidator()
        result = validator.validate({"func_a": ["src/a.py", "src/b.py"]})
        assert isinstance(result, (list, dict))

    def test_validate_empty(self):
        validator = PathIndexValidator()
        result = validator.validate({})
        assert isinstance(result, (list, dict))
