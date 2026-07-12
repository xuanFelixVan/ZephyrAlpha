# [A_test] module_id: SRC-TST-0298 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-346 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_ai_code_standards
# [INVARIANTS] CODE_CONVENTIONS keys must be stable; AI_FORBIDDEN must be non-empty
# [MODIFY-GUARD] Changes must sync with ai_code_standards.py
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] None
# [TESTS] tests/test_ai_code_standards.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_enforcement.behavioral_admission.ai_code_standards import AI_FORBIDDEN, CODE_CONVENTIONS


class TestCodeConventions:
    def test_is_dict(self):
        assert isinstance(CODE_CONVENTIONS, dict)

    def test_required_keys_exist(self):
        expected_keys = {"file_org", "scaffold", "header", "comments", "imports", "type_hints"}
        assert expected_keys.issubset(set(CODE_CONVENTIONS.keys()))

    def test_all_values_are_strings(self):
        for key, value in CODE_CONVENTIONS.items():
            assert isinstance(value, str), f"Value for {key} is not a string"

    def test_non_empty_values(self):
        for key, value in CODE_CONVENTIONS.items():
            assert len(value) > 0, f"Empty value for {key}"


class TestAiForbidden:
    def test_is_list(self):
        assert isinstance(AI_FORBIDDEN, list)

    def test_non_empty(self):
        assert len(AI_FORBIDDEN) > 0

    def test_all_entries_are_strings(self):
        for entry in AI_FORBIDDEN:
            assert isinstance(entry, str)

    def test_contains_forbidden_comment_rule(self):
        has_comment_rule = any("注释" in entry or "comment" in entry.lower() for entry in AI_FORBIDDEN)
        assert has_comment_rule
