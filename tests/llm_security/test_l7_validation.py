# [A_test] module_id: MOD-GOV_l7_validation | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] tests.llm_security.test_l7_validation
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
import pytest

from zephyr.security.llm_defense.llm_security.self_protection.l7_validation import (
    CodeIntegrityGuard,
    DeepSeekSpecialRiskManager,
    LiteLLMProviderIsolator,
    ProviderFailClosedAdapter,
    RegressionType,
    ValidationLayer,
)


class TestCodeIntegrityGuard:
    def test_register_and_check(self, tmp_path):
        guard = CodeIntegrityGuard()
        fp = tmp_path / "test.py"
        fp.write_text("hello", encoding="utf-8")
        sha = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
        guard.register_baseline(str(fp), sha)
        check = guard.check_integrity(str(fp))
        assert check.passed is True
        assert check.actual_sha256 == sha

    def test_check_fails_on_tamper(self, tmp_path):
        guard = CodeIntegrityGuard()
        fp = tmp_path / "test.py"
        fp.write_text("hello", encoding="utf-8")
        guard.register_baseline(str(fp), "wrong_hash_abcdef")
        check = guard.check_integrity(str(fp))
        assert check.passed is False


class TestDeepSeekRiskManager:
    def test_overconfident_blocked(self):
        mgr = DeepSeekSpecialRiskManager()
        result = mgr.check_hallucination("This is guaranteed 100% absolutely correct!")
        assert result["blocked"] is True

    def test_normal_passes(self):
        mgr = DeepSeekSpecialRiskManager()
        result = mgr.check_hallucination("The weather is likely rainy today.")
        assert result["blocked"] is False

    def test_censorship_detection(self):
        mgr = DeepSeekSpecialRiskManager()
        result = mgr.assess_censorship_impact("I cannot answer that question.")
        assert result["censorship_detected"] is True

    def test_temperature_drift(self):
        mgr = DeepSeekSpecialRiskManager()
        result = mgr.monitor_temperature_drift(1.0, baseline_temp=0.7)
        assert result["drift_detected"] is True


class TestLiteLLMProviderIsolator:
    def test_deepseek_has_issues(self):
        iso = LiteLLMProviderIsolator()
        result = iso.run_provider_security_check("deepseek")
        assert len(result["issues"]) > 0
        assert result["risk_level"] in ("high", "medium")


class TestProviderFailClosedAdapter:
    def test_deepseek_strategy(self):
        adapter = ProviderFailClosedAdapter()
        result = adapter.get_strategy("deepseek")
        assert result["strategy"] == "block_and_alert"
        assert result["fail_closed"] is True


class TestValidationLayer:
    def test_validate_unit_tests_below_threshold(self):
        layer = ValidationLayer()
        assert layer.validate_unit_tests(50.0) is False

    def test_validate_unit_tests_above_threshold(self):
        layer = ValidationLayer()
        assert layer.validate_unit_tests(85.0) is True

    def test_validate_integration_tests(self):
        layer = ValidationLayer()
        results = [
            {"name": "test1", "passed": True},
            {"name": "test2", "passed": False},
        ]
        report = layer.validate_integration_tests(results)
        assert report["total"] == 2
        assert report["passed"] == 1
        assert report["all_passed"] is False

    def test_trigger_security_regression(self):
        layer = ValidationLayer()
        from unittest.mock import MagicMock

        gateway = MagicMock()
        result = layer.trigger_security_regression(RegressionType.WEEKLY, gateway=gateway)
        assert result.total_scenarios == 10
        assert result.passed == 10
        assert result.failed == 0
        assert len(layer.regression_history) == 1

    def test_auto_trigger_initial(self):
        layer = ValidationLayer()
        from unittest.mock import MagicMock

        gateway = MagicMock()
        results = layer.auto_trigger_if_due(gateway=gateway)
        assert len(results) >= 2

    @pytest.mark.asyncio
    async def test_evaluate_with_low_coverage(self):
        layer = ValidationLayer()
        ctx = type("ctx", (), {"metadata": {"coverage_pct": 50.0}})()
        result = await layer.evaluate(ctx)
        from zephyr.shared.contracts.security.security_decision import SecurityDecision

        assert result.decision == SecurityDecision.DENY
