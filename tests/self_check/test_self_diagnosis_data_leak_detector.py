# [A_test] module_id: SRC-TST-1555 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_self_diagnosis_data_leak_detector
# [INVARIANTS] scan returns dict with status/findings_count/critical_findings/high_findings/findings; sanitize redacts patterns
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_self_diagnosis_data_leak_detector.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.self_diagnosis_data_leak_detector import (
    SelfDiagnosisDataLeakDetector,
)


class TestSelfDiagnosisDataLeakDetectorInstantiation:
    def test_default_patterns_non_empty(self):
        obj = SelfDiagnosisDataLeakDetector()
        assert len(obj.sensitive_patterns) > 0

    def test_default_findings_empty(self):
        obj = SelfDiagnosisDataLeakDetector()
        assert obj.findings == []

    def test_custom_patterns(self):
        custom = [(r"test_pattern", "test", "low")]
        obj = SelfDiagnosisDataLeakDetector(sensitive_patterns=custom)
        assert len(obj.sensitive_patterns) == 1


class TestSelfDiagnosisDataLeakDetectorScan:
    def test_scan_clean_text(self):
        obj = SelfDiagnosisDataLeakDetector()
        result = obj.scan("This is a normal diagnostic report with no secrets.")
        assert result["status"] == "clean"
        assert result["findings_count"] == 0

    def test_scan_empty_text(self):
        obj = SelfDiagnosisDataLeakDetector()
        result = obj.scan("")
        assert result["status"] == "clean"
        assert result["findings_count"] == 0

    def test_scan_detects_openai_key(self):
        obj = SelfDiagnosisDataLeakDetector()
        result = obj.scan("key found: sk-abcdefghijklmnopqrstuvwxyz1234567890")
        assert result["status"] == "critical_leak"
        assert result["critical_findings"] >= 1

    def test_scan_detects_google_api_key(self):
        obj = SelfDiagnosisDataLeakDetector()
        result = obj.scan("google key: AIzaSyAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        assert result["status"] == "critical_leak"
        assert result["critical_findings"] >= 1

    def test_scan_detects_database_url(self):
        obj = SelfDiagnosisDataLeakDetector()
        result = obj.scan("db connection: postgres://admin:pass@db.host.com/dbname")
        assert result["status"] == "critical_leak"
        assert result["critical_findings"] >= 1

    def test_scan_detects_email(self):
        obj = SelfDiagnosisDataLeakDetector()
        result = obj.scan("contact: admin@example.com for details")
        assert result["status"] in ("low_risk", "high_risk", "critical_leak")
        assert result["findings_count"] >= 1

    def test_scan_detects_secret_assignment(self):
        obj = SelfDiagnosisDataLeakDetector()
        result = obj.scan('private_key = "supersecretvalue12345678"')
        assert result["status"] == "critical_leak"
        assert result["critical_findings"] >= 1

    def test_scan_returns_dict_structure(self):
        obj = SelfDiagnosisDataLeakDetector()
        result = obj.scan("clean text")
        assert "status" in result
        assert "findings_count" in result
        assert "critical_findings" in result
        assert "high_findings" in result
        assert "findings" in result

    def test_scan_findings_capped_at_20(self):
        obj = SelfDiagnosisDataLeakDetector()
        text = " ".join(["sk-abcdefghijklmnopqrstuvwxyz1234567890"] * 30)
        result = obj.scan(text)
        assert len(result["findings"]) <= 20

    def test_scan_high_risk_status(self):
        obj = SelfDiagnosisDataLeakDetector()
        api_key_like = "abcdefghijklmnopqrstuvwx_yz0123456789ABCD:abcdefghijklmnopqrstuvwxyz0123456789ABCDEF="
        result = obj.scan(api_key_like)
        assert result["status"] in ("high_risk", "critical_leak")

    def test_scan_resets_findings_each_call(self):
        obj = SelfDiagnosisDataLeakDetector()
        obj.scan("sk-abcdefghijklmnopqrstuvwxyz1234567890")
        assert len(obj.findings) > 0
        obj.scan("clean text")
        assert len(obj.findings) == 0


class TestSelfDiagnosisDataLeakDetectorSanitize:
    def test_sanitize_clean_text_unchanged(self):
        obj = SelfDiagnosisDataLeakDetector()
        text = "This is clean text."
        assert obj.sanitize(text) == text

    def test_sanitize_empty_text(self):
        obj = SelfDiagnosisDataLeakDetector()
        assert obj.sanitize("") == ""

    def test_sanitize_redacts_openai_key(self):
        obj = SelfDiagnosisDataLeakDetector()
        text = "key: sk-abcdefghijklmnopqrstuvwxyz1234567890"
        sanitized = obj.sanitize(text)
        assert "sk-abcde" in sanitized
        assert "[REDACTED]" in sanitized

    def test_sanitize_redacts_database_url(self):
        obj = SelfDiagnosisDataLeakDetector()
        text = "db: postgres://admin:pass@db.host.com/dbname"
        sanitized = obj.sanitize(text)
        assert "[REDACTED]" in sanitized

    def test_sanitize_preserves_non_sensitive(self):
        obj = SelfDiagnosisDataLeakDetector()
        text = "System health is OK. CPU at 45%."
        sanitized = obj.sanitize(text)
        assert "System health is OK" in sanitized
