# [A_test] module_id: SRC-TST-1701 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_success_validator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
from zephyr.gov_code_quality.code_dedup.success_validator import (
    SuccessValidator,
    ValidationResult,
)


class TestSuccessValidator:
    def test_instantiation(self):
        validator = SuccessValidator()
        assert validator is not None

    def test_validate_success(self):
        validator = SuccessValidator()
        result = validator.validate("fix-001", before_count=10, after_count=5)
        assert isinstance(result, ValidationResult)
        assert result.success is True

    def test_validate_failure(self):
        validator = SuccessValidator()
        result = validator.validate("fix-002", before_count=5, after_count=10)
        assert isinstance(result, ValidationResult)
        assert result.success is False

    def test_validate_zero_to_zero(self):
        validator = SuccessValidator()
        result = validator.validate("fix-003", before_count=0, after_count=0)
        assert isinstance(result, ValidationResult)

    def test_summary(self):
        validator = SuccessValidator()
        validator.validate("fix-001", before_count=10, after_count=5)
        result = validator.summary()
        assert isinstance(result, dict)
        assert "success_rate" in result
