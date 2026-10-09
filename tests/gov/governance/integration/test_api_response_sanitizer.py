# [A_test] module_id: MOD-GOV_api_response_sanitizer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_api_response_sanitizer
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_api_response_sanitizer.py -q
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.security_governance.api_response_sanitizer import APIResponseSanitizer


class TestAPIResponseSanitizerInstantiation:
    def test_creates_instance(self):
        sanitizer = APIResponseSanitizer()
        assert sanitizer is not None

    def test_instance_is_correct_type(self):
        sanitizer = APIResponseSanitizer()
        assert isinstance(sanitizer, APIResponseSanitizer)


class TestSanitize:
    def test_removes_script_tag(self):
        sanitizer = APIResponseSanitizer()
        result = sanitizer.sanitize('<script>alert("xss")</script>')
        assert "[SANITIZED]" in result
        assert "<script" not in result

    def test_removes_javascript_protocol(self):
        sanitizer = APIResponseSanitizer()
        result = sanitizer.sanitize('click <a href="javascript:void(0)">here</a>')
        assert "[SANITIZED]" in result
        assert "javascript:" not in result

    def test_removes_onerror(self):
        sanitizer = APIResponseSanitizer()
        result = sanitizer.sanitize('<img onerror="bad()" src="x">')
        assert "[SANITIZED]" in result
        assert "onerror=" not in result

    def test_removes_onclick(self):
        sanitizer = APIResponseSanitizer()
        result = sanitizer.sanitize('<div onclick="steal()">click</div>')
        assert "[SANITIZED]" in result
        assert "onclick=" not in result

    def test_clean_text_unchanged(self):
        sanitizer = APIResponseSanitizer()
        clean = "Hello, this is a safe response."
        result = sanitizer.sanitize(clean)
        assert result == clean

    def test_empty_string_returns_empty(self):
        sanitizer = APIResponseSanitizer()
        result = sanitizer.sanitize("")
        assert result == ""

    def test_multiple_dangerous_patterns_all_sanitized(self):
        sanitizer = APIResponseSanitizer()
        result = sanitizer.sanitize("<script>x</script> javascript:bad() onerror=boom onclick=go")
        assert "<script" not in result
        assert "javascript:" not in result
        assert "onerror=" not in result
        assert "onclick=" not in result
        assert result.count("[SANITIZED]") == 4


class TestIsSuspicious:
    def test_detects_script_tag(self):
        sanitizer = APIResponseSanitizer()
        assert sanitizer.is_suspicious("<script>alert(1)</script>") is True

    def test_detects_eval(self):
        sanitizer = APIResponseSanitizer()
        assert sanitizer.is_suspicious('some eval("code") here') is True

    def test_detects_import(self):
        sanitizer = APIResponseSanitizer()
        assert sanitizer.is_suspicious('__import__("os")') is True

    def test_clean_text_not_suspicious(self):
        sanitizer = APIResponseSanitizer()
        assert sanitizer.is_suspicious("normal response text") is False

    def test_empty_string_not_suspicious(self):
        sanitizer = APIResponseSanitizer()
        assert sanitizer.is_suspicious("") is False

    def test_case_insensitive_detection(self):
        sanitizer = APIResponseSanitizer()
        assert sanitizer.is_suspicious("<SCRIPT>bad</SCRIPT>") is True

    def test_partial_match_not_flagged_for_eval(self):
        sanitizer = APIResponseSanitizer()
        assert sanitizer.is_suspicious("evaluation result") is False


class TestBoundaryConditions:
    def test_sanitize_preserves_surrounding_content(self):
        sanitizer = APIResponseSanitizer()
        result = sanitizer.sanitize("before<script>bad</script>after")
        assert result.startswith("before")
        assert result.endswith("after")

    def test_sanitize_with_only_dangerous_content(self):
        sanitizer = APIResponseSanitizer()
        result = sanitizer.sanitize("<script>")
        assert "[SANITIZED]" in result
        assert "<script" not in result

    def test_is_suspicious_with_mixed_case_eval(self):
        sanitizer = APIResponseSanitizer()
        assert sanitizer.is_suspicious("EVAL(") is True

    def test_sanitize_does_not_double_sanitize_marker(self):
        sanitizer = APIResponseSanitizer()
        result = sanitizer.sanitize("<script><script>double</script></script>")
        assert result.count("[SANITIZED]") >= 2
