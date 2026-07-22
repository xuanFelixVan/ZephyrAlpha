# [A_test] module_id: MOD-GOV_skill_compliance | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_compliance
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/test_skill_compliance.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.autonomy_core.skills.skill_compliance import PII_PATTERNS, SkillCompliance


class TestSkillComplianceInit:
    def test_class_methods_no_instance_needed(self):
        result = SkillCompliance.check("test-skill", "clean content")
        assert "skill_id" in result

    def test_pii_patterns_defined(self):
        assert len(PII_PATTERNS) >= 2
        pattern_types = [p[1] for p in PII_PATTERNS]
        assert "email" in pattern_types
        assert "credit_card" in pattern_types


class TestCheckPii:
    def test_no_pii_in_clean_content(self):
        result = SkillCompliance._check_pii("hello world")
        assert result["pii_detected"] is False
        assert result["findings"] == []

    def test_email_detected(self):
        result = SkillCompliance._check_pii("contact user@example.com for info")
        assert result["pii_detected"] is True
        assert any(f["type"] == "email" for f in result["findings"])

    def test_credit_card_detected(self):
        result = SkillCompliance._check_pii("card number 4111222233334444 on file")
        assert result["pii_detected"] is True
        assert any(f["type"] == "credit_card" for f in result["findings"])

    def test_multiple_pii_types(self):
        result = SkillCompliance._check_pii("email: user@example.com card: 4111222233334444")
        assert result["pii_detected"] is True
        types = {f["type"] for f in result["findings"]}
        assert "email" in types
        assert "credit_card" in types

    def test_empty_string(self):
        result = SkillCompliance._check_pii("")
        assert result["pii_detected"] is False
        assert result["findings"] == []

    def test_pii_value_truncated(self):
        result = SkillCompliance._check_pii("user: averylongemailaddress@verylongdomain.example.com")
        for f in result["findings"]:
            if f["type"] == "email":
                assert f["value"].endswith("...")
                assert len(f["value"]) <= 33


class TestCheck:
    def test_compliant_content(self):
        result = SkillCompliance.check("skill-clean", "no sensitive data here")
        assert result["skill_id"] == "skill-clean"
        assert result["compliant"] is True
        assert result["violations"] == []

    def test_noncompliant_with_email(self):
        result = SkillCompliance.check("skill-pii", "email: admin@test.com")
        assert result["compliant"] is False
        assert len(result["violations"]) >= 1
        assert result["violations"][0]["policy"] == "GDPR"
        assert result["violations"][0]["check"] == "no_pii_storage"

    def test_none_content_treated_as_empty(self):
        result = SkillCompliance.check("skill-none", None)
        assert result["compliant"] is True
        assert result["pii_check"]["pii_detected"] is False

    def test_empty_content(self):
        result = SkillCompliance.check("skill-empty", "")
        assert result["compliant"] is True

    def test_empty_skill_id(self):
        result = SkillCompliance.check("", "clean content")
        assert result["skill_id"] == ""

    def test_check_returns_pii_check_key(self):
        result = SkillCompliance.check("skill-x", "hello")
        assert "pii_check" in result
        assert "pii_detected" in result["pii_check"]
        assert "findings" in result["pii_check"]

    def test_credit_card_with_dashes(self):
        result = SkillCompliance.check("skill-cc", "card: 4111-2222-3333-4444")
        assert result["compliant"] is False

    def test_credit_card_with_spaces(self):
        result = SkillCompliance.check("skill-cc2", "card: 4111 2222 3333 4444")
        assert result["compliant"] is False
