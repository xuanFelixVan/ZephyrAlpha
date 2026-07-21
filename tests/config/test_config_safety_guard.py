# [A_test] module_id: MOD-GOV_config_safety_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_config_safety_guard
# [INVARIANTS] domain_bounds_enforced;rejected_when_out_of_range;unknown_key_wide_domain
# [MODIFY-GUARD] source-change-only
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.ExitCode
# [TESTS] test_config_safety_guard.py
# [TTL] task_bound

from zephyr.shared.ai_guards.config_safety_guard import ConfigGuardResult, ConfigSafetyGuard


class TestConfigGuardResult:
    def test_creation(self):
        r = ConfigGuardResult(key="threshold_pct", value=0.8, min_val=0.5, max_val=0.99, valid=True)
        assert r.key == "threshold_pct"
        assert r.valid is True
        assert r.rejected is False

    def test_rejected_explicit(self):
        r = ConfigGuardResult(key="x", value=1.0, min_val=0.0, max_val=1.0, valid=False, rejected=True)
        assert r.rejected is True


class TestConfigSafetyGuard:
    def test_valid_threshold_pct(self):
        guard = ConfigSafetyGuard()
        result = guard.validate("threshold_pct", 0.75)
        assert result.valid is True
        assert result.rejected is False

    def test_invalid_threshold_pct_too_low(self):
        guard = ConfigSafetyGuard()
        result = guard.validate("threshold_pct", 0.3)
        assert result.valid is False
        assert result.rejected is True

    def test_invalid_threshold_pct_too_high(self):
        guard = ConfigSafetyGuard()
        result = guard.validate("threshold_pct", 1.5)
        assert result.valid is False

    def test_valid_top_k(self):
        guard = ConfigSafetyGuard()
        result = guard.validate("top_k", 10)
        assert result.valid is True

    def test_invalid_top_k_zero(self):
        guard = ConfigSafetyGuard()
        result = guard.validate("top_k", 0)
        assert result.valid is False

    def test_valid_max_age_s(self):
        guard = ConfigSafetyGuard()
        result = guard.validate("max_age_s", 3600)
        assert result.valid is True

    def test_invalid_max_age_s_too_low(self):
        guard = ConfigSafetyGuard()
        result = guard.validate("max_age_s", 30)
        assert result.valid is False

    def test_boundary_min(self):
        guard = ConfigSafetyGuard()
        result = guard.validate("threshold_pct", 0.5)
        assert result.valid is True

    def test_boundary_max(self):
        guard = ConfigSafetyGuard()
        result = guard.validate("threshold_pct", 0.99)
        assert result.valid is True

    def test_unknown_key_accepted(self):
        guard = ConfigSafetyGuard()
        result = guard.validate("unknown_key", 42.0)
        assert result.valid is True

    def test_unknown_key_zero_accepted(self):
        guard = ConfigSafetyGuard()
        result = guard.validate("unknown_key", 0.0)
        assert result.valid is True

    def test_result_contains_domain_info(self):
        guard = ConfigSafetyGuard()
        result = guard.validate("top_k", 5)
        assert result.min_val == 1
        assert result.max_val == 20
