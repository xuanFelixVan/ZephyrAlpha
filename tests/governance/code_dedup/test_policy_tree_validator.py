# [A_test] module_id: SRC-TST-1386 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_policy_tree_validator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
from zephyr.gov_code_quality.code_dedup.policy_tree_validator import (
    PolicyTreeReport,
    PolicyTreeValidator,
)


class TestPolicyTreeValidator:
    def test_instantiation(self):
        validator = PolicyTreeValidator()
        assert validator is not None

    def test_validate_returns_report(self):
        validator = PolicyTreeValidator()
        tree = {"rules": []}
        result = validator.validate(tree)
        assert isinstance(result, PolicyTreeReport)

    def test_validate_empty(self):
        validator = PolicyTreeValidator()
        result = validator.validate({})
        assert isinstance(result, PolicyTreeReport)

    def test_validate_from_file_not_found(self):
        validator = PolicyTreeValidator()
        result = validator.validate_from_file("nonexistent.yaml")
        assert isinstance(result, PolicyTreeReport)
