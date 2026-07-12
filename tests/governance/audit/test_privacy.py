# [A_test] module_id: SRC-TST-1400 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_privacy
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_audit.privacy import (
    PIICategory,
    PIIScanResult,
    PrivacyGuard,
    RedactionPolicy,
    hash_path,
)


class TestPIICategory:
    def test_all_categories(self):
        expected = {"EMAIL", "PHONE", "SSN", "CREDIT_CARD", "API_KEY", "IP_ADDRESS", "CUSTOM"}
        assert set(e.name for e in PIICategory) == expected


class TestRedactionPolicy:
    def test_all_policies(self):
        expected = {"MASK", "HASH", "REMOVE", "REPLACE"}
        assert set(e.name for e in RedactionPolicy) == expected


class TestPrivacyGuardInit:
    def test_default_policy(self):
        guard = PrivacyGuard()
        assert guard._default_policy == RedactionPolicy.MASK

    def test_custom_policy(self):
        guard = PrivacyGuard(default_policy=RedactionPolicy.HASH)
        assert guard._default_policy == RedactionPolicy.HASH

    def test_custom_patterns(self):
        guard = PrivacyGuard(custom_patterns={PIICategory.CUSTOM: [r"\bTEST_\w+\b"]})
        assert PIICategory.CUSTOM in guard._patterns


class TestDetectPII:
    def test_detect_email(self):
        guard = PrivacyGuard()
        result = guard.detect_pii("Contact us at user@example.com for info")
        assert isinstance(result, PIIScanResult)
        assert result.has_pii is True
        emails = [d for d in result.detections if d.category == PIICategory.EMAIL]
        assert len(emails) >= 1

    def test_detect_phone(self):
        guard = PrivacyGuard()
        result = guard.detect_pii("Call 123-456-7890 now")
        assert result.has_pii is True
        phones = [d for d in result.detections if d.category == PIICategory.PHONE]
        assert len(phones) >= 1

    def test_detect_ssn(self):
        guard = PrivacyGuard()
        result = guard.detect_pii("SSN: 123-45-6789")
        assert result.has_pii is True

    def test_detect_credit_card(self):
        guard = PrivacyGuard()
        result = guard.detect_pii("Card: 4111-1111-1111-1111")
        assert result.has_pii is True

    def test_detect_api_key(self):
        guard = PrivacyGuard()
        result = guard.detect_pii("api_key: sk-abcdefghijklmnopqrstuvwxyz1234567890")
        assert result.has_pii is True

    def test_detect_ip_address(self):
        guard = PrivacyGuard()
        result = guard.detect_pii("Server at 192.168.1.1")
        assert result.has_pii is True

    def test_no_pii(self):
        guard = PrivacyGuard()
        result = guard.detect_pii("This is a normal text without PII")
        assert result.has_pii is False
        assert result.detections == []

    def test_empty_text(self):
        guard = PrivacyGuard()
        result = guard.detect_pii("")
        assert result.has_pii is False

    def test_custom_pattern_detection(self):
        guard = PrivacyGuard(custom_patterns={PIICategory.CUSTOM: [r"\bPROJECT_\w+\b"]})
        result = guard.detect_pii("Access PROJECT_SECRET_DATA here")
        assert result.has_pii is True
        customs = [d for d in result.detections if d.category == PIICategory.CUSTOM]
        assert len(customs) >= 1


class TestRedact:
    def test_mask_policy(self):
        guard = PrivacyGuard(default_policy=RedactionPolicy.MASK)
        result = guard.redact("Email: user@example.com")
        assert "user@example.com" not in result

    def test_hash_policy(self):
        guard = PrivacyGuard(default_policy=RedactionPolicy.HASH)
        result = guard.redact("Email: user@example.com")
        assert "user@example.com" not in result
        assert "[HASH:" in result

    def test_remove_policy(self):
        guard = PrivacyGuard(default_policy=RedactionPolicy.REMOVE)
        result = guard.redact("Email: user@example.com")
        assert "user@example.com" not in result

    def test_replace_policy(self):
        guard = PrivacyGuard(default_policy=RedactionPolicy.REPLACE)
        result = guard.redact("Email: user@example.com")
        assert "[REDACTED]" in result

    def test_custom_replacement(self):
        guard = PrivacyGuard(default_policy=RedactionPolicy.REPLACE)
        result = guard.redact("Email: user@example.com", replacement="[HIDDEN]")
        assert "[HIDDEN]" in result

    def test_no_pii_unchanged(self):
        guard = PrivacyGuard()
        result = guard.redact("Normal text without PII")
        assert result == "Normal text without PII"

    def test_explicit_policy_override(self):
        guard = PrivacyGuard(default_policy=RedactionPolicy.MASK)
        result = guard.redact("Email: user@example.com", policy=RedactionPolicy.REMOVE)
        assert "user@example.com" not in result
        assert "[HASH:" not in result


class TestHashPath:
    def test_returns_hex_string(self):
        result = hash_path("/some/path")
        assert len(result) == 16
        assert all(c in "0123456789abcdef" for c in result)

    def test_deterministic(self):
        r1 = hash_path("/same/path")
        r2 = hash_path("/same/path")
        assert r1 == r2

    def test_different_paths_different_hashes(self):
        r1 = hash_path("/path/a")
        r2 = hash_path("/path/b")
        assert r1 != r2

    def test_empty_path(self):
        result = hash_path("")
        assert isinstance(result, str)
        assert len(result) == 16


class TestPrivacyGuardHashPath:
    def test_static_method_matches_function(self):
        guard = PrivacyGuard()
        assert guard.hash_path("/test") == hash_path("/test")
