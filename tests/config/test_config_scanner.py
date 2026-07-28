# [A_test] module_id: MOD-GOV_config_scanner | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_config_scanner
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_config_scanner.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.security_governance.config_scanner import ConfigScanner


class TestConfigScannerInstantiation:
    def test_create_instance(self):
        scanner = ConfigScanner()
        assert scanner is not None

    def test_initial_baseline_empty(self):
        scanner = ConfigScanner()
        assert scanner.baseline == {}


class TestSetBaseline:
    def test_set_single_baseline(self):
        scanner = ConfigScanner()
        scanner.set_baseline("config.yaml", "abc123")
        assert scanner.baseline["config.yaml"] == "abc123"

    def test_overwrite_baseline(self):
        scanner = ConfigScanner()
        scanner.set_baseline("config.yaml", "abc123")
        scanner.set_baseline("config.yaml", "def456")
        assert scanner.baseline["config.yaml"] == "def456"

    def test_multiple_baselines(self):
        scanner = ConfigScanner()
        scanner.set_baseline("a.yaml", "hash_a")
        scanner.set_baseline("b.yaml", "hash_b")
        assert len(scanner.baseline) == 2


class TestDetectModification:
    def test_no_modification_same_hash(self):
        scanner = ConfigScanner()
        scanner.set_baseline("config.yaml", "abc123")
        assert scanner.detect_modification("config.yaml", "abc123") is False

    def test_modification_detected_different_hash(self):
        scanner = ConfigScanner()
        scanner.set_baseline("config.yaml", "abc123")
        assert scanner.detect_modification("config.yaml", "def456") is True

    def test_unknown_file_no_baseline(self):
        scanner = ConfigScanner()
        assert scanner.detect_modification("unknown.yaml", "abc123") is False

    def test_empty_hash_comparison(self):
        scanner = ConfigScanner()
        scanner.set_baseline("config.yaml", "")
        assert scanner.detect_modification("config.yaml", "abc123") is True

    def test_empty_hash_same(self):
        scanner = ConfigScanner()
        scanner.set_baseline("config.yaml", "")
        assert scanner.detect_modification("config.yaml", "") is False


class TestCheckInjection:
    def test_clean_content(self):
        scanner = ConfigScanner()
        result = scanner.check_injection("normal: value")
        assert result == []

    def test_template_injection_detected(self):
        scanner = ConfigScanner()
        result = scanner.check_injection("{{ malicious }}")
        assert "template_injection" in result

    def test_code_injection_detected(self):
        scanner = ConfigScanner()
        result = scanner.check_injection("eval('malicious')")
        assert "code_injection" in result

    def test_both_injections_detected(self):
        scanner = ConfigScanner()
        result = scanner.check_injection("{{ eval('x') }}")
        assert "template_injection" in result
        assert "code_injection" in result

    def test_template_without_closing_braces(self):
        scanner = ConfigScanner()
        result = scanner.check_injection("{{ unclosed")
        assert "template_injection" not in result

    def test_eval_substring_not_detected(self):
        scanner = ConfigScanner()
        result = scanner.check_injection("evaluate_this")
        assert "code_injection" not in result

    def test_empty_content(self):
        scanner = ConfigScanner()
        result = scanner.check_injection("")
        assert result == []

    def test_partial_template_only_opening(self):
        scanner = ConfigScanner()
        result = scanner.check_injection("{{ no closing")
        assert result == []
