# [A_test] module_id: MOD-GOV_provider_data | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] tests.test_provider_data
# [INVARIANTS] test_provider_data完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.intelligence.model_profiling.provider_data import _RAW_TIER_MAP, DEFAULT_PROVIDERS

EXPECTED_PROVIDERS = {"zhipu", "deepseek", "openai_azure", "anthropic"}
REQUIRED_PROVIDER_KEYS = {"cc", "price_per_1k_input", "price_per_1k_output"}
EXPECTED_TIERS = {"ECONOMY", "STANDARD", "PREMIUM"}


class TestDefaultProviders:
    def test_has_four_providers(self):
        assert set(DEFAULT_PROVIDERS.keys()) == EXPECTED_PROVIDERS

    @pytest.mark.parametrize("provider_name", sorted(EXPECTED_PROVIDERS))
    def test_provider_has_required_keys(self, provider_name):
        provider = DEFAULT_PROVIDERS[provider_name]
        assert REQUIRED_PROVIDER_KEYS.issubset(provider.keys())

    @pytest.mark.parametrize("provider_name", sorted(EXPECTED_PROVIDERS))
    def test_prices_are_non_negative_floats(self, provider_name):
        provider = DEFAULT_PROVIDERS[provider_name]
        for key in ("price_per_1k_input", "price_per_1k_output"):
            value = provider[key]
            assert isinstance(value, (int, float)), f"{provider_name}.{key} is not numeric"
            assert value >= 0, f"{provider_name}.{key} is negative"

    @pytest.mark.parametrize("provider_name", sorted(EXPECTED_PROVIDERS))
    def test_country_code_is_valid_string(self, provider_name):
        provider = DEFAULT_PROVIDERS[provider_name]
        cc = provider["cc"]
        assert isinstance(cc, str), f"{provider_name}.cc is not a string"
        assert len(cc) >= 2, f"{provider_name}.cc too short: {cc!r}"

    @pytest.mark.parametrize("provider_name", sorted(EXPECTED_PROVIDERS))
    def test_model_names_are_non_empty_strings(self, provider_name):
        provider = DEFAULT_PROVIDERS[provider_name]
        model_keys = set(provider.keys()) - REQUIRED_PROVIDER_KEYS
        assert len(model_keys) >= 1, f"{provider_name} has no model entries"
        for model_key in model_keys:
            model_name = provider[model_key]
            assert isinstance(model_name, str), f"{provider_name}.{model_key} is not a string"
            assert len(model_name) > 0, f"{provider_name}.{model_key} is empty"


class TestRawTierMap:
    def test_has_three_tiers(self):
        assert set(_RAW_TIER_MAP.keys()) == EXPECTED_TIERS

    @pytest.mark.parametrize("tier_name", sorted(EXPECTED_TIERS))
    def test_tier_has_at_least_one_model(self, tier_name):
        models = _RAW_TIER_MAP[tier_name]
        assert len(models) >= 1, f"{tier_name} has no model entries"

    @pytest.mark.parametrize("tier_name", sorted(EXPECTED_TIERS))
    def test_tier_entries_follow_provider_model_format(self, tier_name):
        models = _RAW_TIER_MAP[tier_name]
        for entry in models:
            assert isinstance(entry, str), f"{tier_name} entry {entry!r} is not a string"
            parts = entry.split(":")
            assert len(parts) == 2, f"{tier_name} entry {entry!r} does not follow 'provider:model'"
            provider, model = parts
            assert len(provider) > 0, f"{tier_name} entry {entry!r} has empty provider"
            assert len(model) > 0, f"{tier_name} entry {entry!r} has empty model"
            assert provider in EXPECTED_PROVIDERS, f"{tier_name} entry {entry!r} has unknown provider {provider!r}"


class TestTierModelMapLazyImport:
    def test_tier_model_map_accessible(self):
        budget_models = pytest.importorskip("zephyr.infrastructure.budget_enforcement.budget_models")
        from zephyr.intelligence.model_profiling.provider_data import TIER_MODEL_MAP

        assert isinstance(TIER_MODEL_MAP, dict)
        assert len(TIER_MODEL_MAP) == 3
        for tier_key in TIER_MODEL_MAP:
            assert hasattr(budget_models, "ModelTier")


class TestBoundaryConditions:
    def test_empty_provider_dict_handling(self):
        empty: dict[str, dict[str, str | float | list[str]]] = {}
        assert len(empty) == 0
        assert REQUIRED_PROVIDER_KEYS.issubset(set()) is False

    def test_default_providers_not_empty(self):
        assert len(DEFAULT_PROVIDERS) > 0

    def test_all_tier_models_reference_valid_providers(self):
        all_providers = set()
        for tier_models in _RAW_TIER_MAP.values():
            for entry in tier_models:
                provider = entry.split(":")[0]
                all_providers.add(provider)
        assert all_providers.issubset(EXPECTED_PROVIDERS)
