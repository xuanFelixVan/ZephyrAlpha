# [A_test] module_id: MOD-GOV_skill_guardrails | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_guardrails
# [INVARIANTS] each test gets a fresh SkillGuardrails instance; no shared state
# [MODIFY-GUARD] skill_guardrails.py
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] all tests must pass independently
# [TESTS] pytest tests/test_skill_guardrails.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.autonomy_core.skills.skill_guardrails import DESTRUCTIVE, SkillGuardrails


class TestSkillGuardrailsInstantiation:
    def test_init_creates_empty_violations(self):
        g = SkillGuardrails()
        assert g._violations == []

    def test_init_active_by_default(self):
        g = SkillGuardrails()
        assert g._active is True

    def test_allowed_property_true_on_fresh(self):
        g = SkillGuardrails()
        assert g.allowed is True

    def test_allowed_false_after_violation(self):
        g = SkillGuardrails()
        g.check_pre_execution("sk", "rm -rf /", budget_remaining=100)
        assert g.allowed is False

    def test_allowed_false_when_deactivated(self):
        g = SkillGuardrails()
        g._active = False
        assert g.allowed is False

    def test_min_output_constant(self):
        assert SkillGuardrails.MIN_OUTPUT == 5


class TestCheckPreExecution:
    def test_clean_operation_allowed(self):
        g = SkillGuardrails()
        result = g.check_pre_execution("sk-1", "read config", budget_remaining=100)
        assert result["allowed"] is True
        assert result["violations"] == []

    def test_destructive_rm_rf_blocked(self):
        g = SkillGuardrails()
        result = g.check_pre_execution("sk-2", "rm -rf /tmp/junk")
        assert result["allowed"] is False
        assert any(v["type"] == "destructive" for v in result["violations"])

    def test_destructive_drop_table_blocked(self):
        g = SkillGuardrails()
        result = g.check_pre_execution("sk-3", "DROP TABLE users")
        assert result["allowed"] is False
        assert any(v["type"] == "destructive" for v in result["violations"])

    def test_budget_exhausted_blocked(self):
        g = SkillGuardrails()
        result = g.check_pre_execution("sk-4", "safe op", budget_remaining=0)
        assert result["allowed"] is False
        assert any(v["type"] == "budget_exhausted" for v in result["violations"])

    def test_budget_negative_blocked(self):
        g = SkillGuardrails()
        result = g.check_pre_execution("sk-5", "safe op", budget_remaining=-10)
        assert result["allowed"] is False

    def test_budget_none_allowed(self):
        g = SkillGuardrails()
        result = g.check_pre_execution("sk-6", "safe op", budget_remaining=None)
        assert result["allowed"] is True

    def test_budget_positive_allowed(self):
        g = SkillGuardrails()
        result = g.check_pre_execution("sk-7", "safe op", budget_remaining=500)
        assert result["allowed"] is True

    def test_operation_truncated_in_result(self):
        g = SkillGuardrails()
        long_op = "a" * 300
        result = g.check_pre_execution("sk-8", long_op)
        assert len(result["operation"]) <= 200

    def test_violations_accumulate(self):
        g = SkillGuardrails()
        g.check_pre_execution("sk", "rm -rf /", budget_remaining=0)
        assert len(g._violations) == 2

    def test_case_insensitive_destructive(self):
        g = SkillGuardrails()
        result = g.check_pre_execution("sk", "RM -RF /stuff")
        assert result["allowed"] is False

    def test_empty_operation_allowed(self):
        g = SkillGuardrails()
        result = g.check_pre_execution("sk", "")
        assert result["allowed"] is True


class TestCheckOutput:
    def test_valid_output_allowed(self):
        g = SkillGuardrails()
        result = g.check_output("sk-1", "This is a valid output with enough content")
        assert result["allowed"] is True
        assert result["violations"] == []

    def test_too_short_output_warning(self):
        g = SkillGuardrails()
        result = g.check_output("sk-2", "ab")
        assert result["allowed"] is False
        assert any(v["type"] == "too_short" for v in result["violations"])

    def test_empty_output_warning(self):
        g = SkillGuardrails()
        result = g.check_output("sk-3", "")
        assert result["allowed"] is False

    def test_whitespace_only_output_warning(self):
        g = SkillGuardrails()
        result = g.check_output("sk-4", "   \n\t  ")
        assert result["allowed"] is False

    def test_exactly_min_output_allowed(self):
        g = SkillGuardrails()
        result = g.check_output("sk-5", "abcde")
        assert result["allowed"] is True

    def test_one_below_min_output_warning(self):
        g = SkillGuardrails()
        result = g.check_output("sk-6", "abcd")
        assert result["allowed"] is False


class TestDestructivePatterns:
    def test_all_destructive_patterns_defined(self):
        assert "rm -rf" in DESTRUCTIVE
        assert "DROP TABLE" in DESTRUCTIVE
        assert "TRUNCATE" in DESTRUCTIVE
        assert "DELETE FROM" in DESTRUCTIVE
        assert "format c:" in DESTRUCTIVE
        assert "rmdir /s" in DESTRUCTIVE

    def test_destructive_severity_levels(self):
        assert DESTRUCTIVE["rm -rf"] == "critical"
        assert DESTRUCTIVE["DROP TABLE"] == "critical"
        assert DESTRUCTIVE["TRUNCATE"] == "high"
        assert DESTRUCTIVE["DELETE FROM"] == "high"
