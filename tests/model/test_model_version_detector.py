# [A_test] module_id: MOD-GOV_model_version_detector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_model_version_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_model_version_detector.py -q
# [TTL] task_bound

from zephyr.governance.intelligence_governance.model_version_detector import ModelVersionDetector


class TestModelVersionDetectorInstantiation:
    def test_creates_instance_with_empty_versions(self):
        mvd = ModelVersionDetector()
        assert isinstance(mvd, ModelVersionDetector)
        assert mvd.known_versions == {}


class TestRecordVersion:
    def test_record_stores_version(self):
        mvd = ModelVersionDetector()
        mvd.record_version("gpt-4", "v1.0")
        assert mvd.known_versions["gpt-4"] == "v1.0"

    def test_record_overwrites_existing_version(self):
        mvd = ModelVersionDetector()
        mvd.record_version("gpt-4", "v1.0")
        mvd.record_version("gpt-4", "v2.0")
        assert mvd.known_versions["gpt-4"] == "v2.0"

    def test_record_multiple_models(self):
        mvd = ModelVersionDetector()
        mvd.record_version("model-a", "1.0")
        mvd.record_version("model-b", "2.0")
        assert len(mvd.known_versions) == 2


class TestDetectChange:
    def test_detect_change_no_known_version(self):
        mvd = ModelVersionDetector()
        assert mvd.detect_change("unknown-model", "v1.0") is False

    def test_detect_change_same_version(self):
        mvd = ModelVersionDetector()
        mvd.record_version("gpt-4", "v1.0")
        assert mvd.detect_change("gpt-4", "v1.0") is False

    def test_detect_change_different_version(self):
        mvd = ModelVersionDetector()
        mvd.record_version("gpt-4", "v1.0")
        assert mvd.detect_change("gpt-4", "v2.0") is True

    def test_detect_change_after_overwrite(self):
        mvd = ModelVersionDetector()
        mvd.record_version("gpt-4", "v1.0")
        mvd.record_version("gpt-4", "v2.0")
        assert mvd.detect_change("gpt-4", "v2.0") is False
        assert mvd.detect_change("gpt-4", "v1.0") is True


class TestShouldDegrade:
    def test_should_degrade_matches_detect_change(self):
        mvd = ModelVersionDetector()
        mvd.record_version("gpt-4", "v1.0")
        assert mvd.should_degrade("gpt-4", "v2.0") is True

    def test_should_degrade_no_change(self):
        mvd = ModelVersionDetector()
        mvd.record_version("gpt-4", "v1.0")
        assert mvd.should_degrade("gpt-4", "v1.0") is False

    def test_should_degrade_unknown_model(self):
        mvd = ModelVersionDetector()
        assert mvd.should_degrade("unknown", "v1.0") is False


class TestBoundary:
    def test_empty_model_id(self):
        mvd = ModelVersionDetector()
        mvd.record_version("", "v1.0")
        assert mvd.detect_change("", "v1.0") is False
        assert mvd.detect_change("", "v2.0") is True

    def test_empty_version_string(self):
        mvd = ModelVersionDetector()
        mvd.record_version("model", "")
        assert mvd.detect_change("model", "") is False
        assert mvd.detect_change("model", "any") is True

    def test_unicode_model_id_and_version(self):
        mvd = ModelVersionDetector()
        mvd.record_version("模型-α", "版本-1")
        assert mvd.detect_change("模型-α", "版本-1") is False
        assert mvd.detect_change("模型-α", "版本-2") is True

    def test_very_long_version_string(self):
        mvd = ModelVersionDetector()
        long_ver = "v" * 10000
        mvd.record_version("model", long_ver)
        assert mvd.detect_change("model", long_ver) is False
        assert mvd.detect_change("model", long_ver + "x") is True

    def test_case_sensitive_version(self):
        mvd = ModelVersionDetector()
        mvd.record_version("model", "V1.0")
        assert mvd.detect_change("model", "v1.0") is True
