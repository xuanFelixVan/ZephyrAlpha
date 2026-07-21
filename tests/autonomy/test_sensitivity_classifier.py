# [A_test] module_id: MOD-GOV_sensitivity_classifier | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_sensitivity_classifier
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_sensitivity_classifier.py -q
# [TTL] task_bound
from __future__ import annotations

from zephyr.security.llm_defense.llm_security.sensitivity_classifier import (
    ClassificationResult,
    SensitivityClassifier,
    SensitivityLevel,
)


class TestSensitivityLevel:
    def test_public_value(self):
        assert SensitivityLevel.PUBLIC.value == "public"

    def test_internal_value(self):
        assert SensitivityLevel.INTERNAL.value == "internal"

    def test_confidential_value(self):
        assert SensitivityLevel.CONFIDENTIAL.value == "confidential"

    def test_restricted_value(self):
        assert SensitivityLevel.RESTRICTED.value == "restricted"

    def test_all_four_levels_exist(self):
        levels = list(SensitivityLevel)
        assert len(levels) == 4


class TestClassificationResult:
    def test_fields_assigned(self):
        result = ClassificationResult(
            ke_id="KE-1",
            level=SensitivityLevel.INTERNAL,
            confidence=0.7,
        )
        assert result.ke_id == "KE-1"
        assert result.level == SensitivityLevel.INTERNAL
        assert result.confidence == 0.7


class TestSensitivityClassifierInstantiation:
    def test_can_instantiate(self):
        clf = SensitivityClassifier()
        assert clf is not None


class TestClassify:
    def test_internal_for_normal_content(self):
        clf = SensitivityClassifier()
        result = clf.classify("KE-1", "This is a regular document")
        assert result.level == SensitivityLevel.INTERNAL

    def test_confidential_for_key_keyword(self):
        clf = SensitivityClassifier()
        result = clf.classify("KE-2", "Contains the API key for production")
        assert result.level == SensitivityLevel.CONFIDENTIAL

    def test_confidential_for_secret_keyword(self):
        clf = SensitivityClassifier()
        result = clf.classify("KE-3", "Store the secret in vault")
        assert result.level == SensitivityLevel.CONFIDENTIAL

    def test_confidential_for_case_insensitive_key(self):
        clf = SensitivityClassifier()
        result = clf.classify("KE-4", "The KEY is here")
        assert result.level == SensitivityLevel.CONFIDENTIAL

    def test_confidential_for_case_insensitive_secret(self):
        clf = SensitivityClassifier()
        result = clf.classify("KE-5", "SECRET data inside")
        assert result.level == SensitivityLevel.CONFIDENTIAL

    def test_ke_id_preserved(self):
        clf = SensitivityClassifier()
        result = clf.classify("KE-TEST", "normal content")
        assert result.ke_id == "KE-TEST"

    def test_confidence_always_0_7(self):
        clf = SensitivityClassifier()
        result_normal = clf.classify("KE-1", "normal")
        result_sensitive = clf.classify("KE-2", "secret stuff")
        assert result_normal.confidence == 0.7
        assert result_sensitive.confidence == 0.7

    def test_returns_classification_result_type(self):
        clf = SensitivityClassifier()
        result = clf.classify("KE-1", "content")
        assert isinstance(result, ClassificationResult)

    def test_empty_content_defaults_to_internal(self):
        clf = SensitivityClassifier()
        result = clf.classify("KE-EMPTY", "")
        assert result.level == SensitivityLevel.INTERNAL

    def test_key_as_substring_matches(self):
        clf = SensitivityClassifier()
        result = clf.classify("KE-6", "keyboard shortcut")
        assert result.level == SensitivityLevel.CONFIDENTIAL
