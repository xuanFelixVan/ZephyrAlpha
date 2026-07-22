# [A_test] module_id: MOD-GOV_provider_failover | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_provider_failover
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_provider_failover.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.intelligence_governance.provider_failover import FALLBACK_CHAIN, ProviderFailover


class TestProviderFailoverInit:
    def test_all_providers_start_healthy(self):
        pf = ProviderFailover()
        for provider in FALLBACK_CHAIN:
            assert pf._healthy[provider] is True

    def test_fallback_chain_has_expected_providers(self):
        assert FALLBACK_CHAIN == ["deepseek", "claude", "gpt"]


class TestMarkUnhealthy:
    def test_mark_single_provider_unhealthy(self):
        pf = ProviderFailover()
        pf.mark_unhealthy("deepseek")
        assert pf._healthy["deepseek"] is False
        assert pf._healthy["claude"] is True
        assert pf._healthy["gpt"] is True

    def test_mark_all_providers_unhealthy(self):
        pf = ProviderFailover()
        for p in FALLBACK_CHAIN:
            pf.mark_unhealthy(p)
        for p in FALLBACK_CHAIN:
            assert pf._healthy[p] is False


class TestMarkHealthy:
    def test_restore_previously_unhealthy_provider(self):
        pf = ProviderFailover()
        pf.mark_unhealthy("claude")
        assert pf._healthy["claude"] is False
        pf.mark_healthy("claude")
        assert pf._healthy["claude"] is True

    def test_mark_healthy_on_already_healthy_is_idempotent(self):
        pf = ProviderFailover()
        pf.mark_healthy("deepseek")
        assert pf._healthy["deepseek"] is True


class TestGetAvailable:
    def test_returns_first_healthy_provider_by_default(self):
        pf = ProviderFailover()
        assert pf.get_available() == "deepseek"

    def test_falls_to_second_when_first_unhealthy(self):
        pf = ProviderFailover()
        pf.mark_unhealthy("deepseek")
        assert pf.get_available() == "claude"

    def test_falls_to_third_when_first_two_unhealthy(self):
        pf = ProviderFailover()
        pf.mark_unhealthy("deepseek")
        pf.mark_unhealthy("claude")
        assert pf.get_available() == "gpt"

    def test_returns_none_when_all_unhealthy(self):
        pf = ProviderFailover()
        for p in FALLBACK_CHAIN:
            pf.mark_unhealthy(p)
        assert pf.get_available() == "none"

    def test_unknown_provider_not_returned(self):
        pf = ProviderFailover()
        pf._healthy["unknown"] = True
        assert pf.get_available() == "deepseek"


class TestIsDegraded:
    def test_not_degraded_when_first_provider_healthy(self):
        pf = ProviderFailover()
        assert pf.is_degraded() is False

    def test_degraded_when_first_provider_unhealthy(self):
        pf = ProviderFailover()
        pf.mark_unhealthy("deepseek")
        assert pf.is_degraded() is True

    def test_degraded_when_all_unhealthy(self):
        pf = ProviderFailover()
        for p in FALLBACK_CHAIN:
            pf.mark_unhealthy(p)
        assert pf.is_degraded() is True

    def test_recovery_restores_non_degraded_state(self):
        pf = ProviderFailover()
        pf.mark_unhealthy("deepseek")
        assert pf.is_degraded() is True
        pf.mark_healthy("deepseek")
        assert pf.is_degraded() is False


class TestProviderFailoverBoundary:
    def test_mark_unhealthy_unknown_provider_still_records(self):
        pf = ProviderFailover()
        pf.mark_unhealthy("nonexistent")
        assert pf._healthy.get("nonexistent") is False

    def test_get_available_skips_unhealthy_unknown_provider(self):
        pf = ProviderFailover()
        pf._healthy["nonexistent"] = True
        result = pf.get_available()
        assert result == "deepseek"

    def test_alternating_health_changes(self):
        pf = ProviderFailover()
        pf.mark_unhealthy("deepseek")
        assert pf.get_available() == "claude"
        pf.mark_healthy("deepseek")
        assert pf.get_available() == "deepseek"
        pf.mark_unhealthy("deepseek")
        pf.mark_unhealthy("claude")
        assert pf.get_available() == "gpt"
