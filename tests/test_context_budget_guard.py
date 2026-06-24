# [A_test] module_id: SRC-TST-0584 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infra_ops/capacity_assurance/blueprint.md | §test
# [MODULE] tests.test_context_budget_guard
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_context_budget_guard.py

import pytest

mod = pytest.importorskip(
    "zephyr.ops.capacity_assurance.context_budget_guard", reason="context_budget_guard not available"
)
ContextBudgetGuard = mod.ContextBudgetGuard


class TestContextBudgetGuard:
    def test_instantiation(self):
        cbg = ContextBudgetGuard()
        assert cbg.max_context_tokens == 128000

    def test_instantiation_custom_budget(self):
        cbg = ContextBudgetGuard(max_context_tokens=64000)
        assert cbg.max_context_tokens == 64000

    def test_check_healthy(self):
        cbg = ContextBudgetGuard(max_context_tokens=100000)
        result = cbg.check(50000)
        assert result["level"] == "HEALTHY"
        assert result["usage_pct"] == 50.0
        assert result["suggestion"] == ""

    def test_check_warning(self):
        cbg = ContextBudgetGuard(max_context_tokens=100000)
        result = cbg.check(85000)
        assert result["level"] == "WARNING"
        assert "truncation" in result["suggestion"]

    def test_check_critical(self):
        cbg = ContextBudgetGuard(max_context_tokens=100000)
        result = cbg.check(96000)
        assert result["level"] == "CRITICAL"

    def test_check_zero_tokens(self):
        cbg = ContextBudgetGuard(max_context_tokens=100000)
        result = cbg.check(0)
        assert result["level"] == "HEALTHY"
        assert result["usage_pct"] == 0.0

    def test_check_exact_warning_threshold(self):
        cbg = ContextBudgetGuard(max_context_tokens=100000)
        result = cbg.check(80001)
        assert result["level"] == "WARNING"

    def test_sli_id_constant(self):
        assert ContextBudgetGuard.SLI_ID == "CAP-CTX-001"

    def test_thresholds(self):
        assert ContextBudgetGuard.WARN_THRESHOLD == 0.80
        assert ContextBudgetGuard.CRITICAL_THRESHOLD == 0.95
