# [A_test] module_id: MOD-GOV_pricing_sync | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_pricing_sync
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_pricing_sync.py
# [TTL] task_bound

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from zephyr.governance.data_governance.pricing_sync import PriceEntry, PricingSync


class TestPricingSyncInit:
    def test_init_with_nonexistent_path(self, tmp_path: Path):
        ps = PricingSync(pricing_path=str(tmp_path / "nonexistent.yaml"))
        assert ps.all_models() == []

    def test_init_with_existing_yaml(self, tmp_path: Path):
        pricing_file = tmp_path / "model_pricing.yaml"
        data = {
            "gpt-4": {"input_price": 0.03, "output_price": 0.06, "provider": "openai"},
        }
        pricing_file.write_text(yaml.dump(data), encoding="utf-8")
        ps = PricingSync(pricing_path=str(pricing_file))
        assert "gpt-4" in ps.all_models()


class TestUpdatePrice:
    def test_update_price_creates_entry(self, tmp_path: Path):
        ps = PricingSync(pricing_path=str(tmp_path / "prices.yaml"))
        entry = ps.update_price("claude-3", 0.01, 0.03, "anthropic")
        assert entry.model == "claude-3"
        assert entry.input_per_1k == 0.01
        assert entry.output_per_1k == 0.03
        assert entry.provider == "anthropic"

    def test_update_price_persists_to_disk(self, tmp_path: Path):
        pricing_file = tmp_path / "prices.yaml"
        ps = PricingSync(pricing_path=str(pricing_file))
        ps.update_price("gpt-4", 0.03, 0.06, "openai")
        ps2 = PricingSync(pricing_path=str(pricing_file))
        loaded = ps2.get_price("gpt-4")
        assert loaded is not None
        assert loaded.input_per_1k == 0.03

    def test_update_price_overwrites_existing(self, tmp_path: Path):
        ps = PricingSync(pricing_path=str(tmp_path / "prices.yaml"))
        ps.update_price("gpt-4", 0.03, 0.06, "openai")
        ps.update_price("gpt-4", 0.05, 0.10, "openai")
        entry = ps.get_price("gpt-4")
        assert entry.input_per_1k == 0.05


class TestGetPrice:
    def test_get_price_returns_entry(self, tmp_path: Path):
        ps = PricingSync(pricing_path=str(tmp_path / "prices.yaml"))
        ps.update_price("claude-3", 0.01, 0.03, "anthropic")
        entry = ps.get_price("claude-3")
        assert entry is not None
        assert entry.provider == "anthropic"

    def test_get_price_missing_model_returns_none(self, tmp_path: Path):
        ps = PricingSync(pricing_path=str(tmp_path / "prices.yaml"))
        assert ps.get_price("nonexistent") is None


class TestEstimateCost:
    def test_estimate_cost_known_model(self, tmp_path: Path):
        ps = PricingSync(pricing_path=str(tmp_path / "prices.yaml"))
        ps.update_price("gpt-4", 0.03, 0.06, "openai")
        cost = ps.estimate_cost("gpt-4", 1000, 1000)
        assert cost == pytest.approx(0.03 + 0.06)

    def test_estimate_cost_unknown_model_returns_zero(self, tmp_path: Path):
        ps = PricingSync(pricing_path=str(tmp_path / "prices.yaml"))
        assert ps.estimate_cost("unknown", 1000, 1000) == 0.0

    def test_estimate_cost_zero_tokens(self, tmp_path: Path):
        ps = PricingSync(pricing_path=str(tmp_path / "prices.yaml"))
        ps.update_price("gpt-4", 0.03, 0.06, "openai")
        assert ps.estimate_cost("gpt-4", 0, 0) == 0.0


class TestAllModelsAndProviders:
    def test_all_models(self, tmp_path: Path):
        ps = PricingSync(pricing_path=str(tmp_path / "prices.yaml"))
        ps.update_price("gpt-4", 0.03, 0.06, "openai")
        ps.update_price("claude-3", 0.01, 0.03, "anthropic")
        assert set(ps.all_models()) == {"gpt-4", "claude-3"}

    def test_providers_deduplicates(self, tmp_path: Path):
        ps = PricingSync(pricing_path=str(tmp_path / "prices.yaml"))
        ps.update_price("gpt-4", 0.03, 0.06, "openai")
        ps.update_price("gpt-3.5", 0.001, 0.002, "openai")
        assert ps.providers() == ["openai"]

    def test_all_models_empty(self, tmp_path: Path):
        ps = PricingSync(pricing_path=str(tmp_path / "prices.yaml"))
        assert ps.all_models() == []


class TestSyncFromLitellm:
    def test_sync_from_litellm_valid_file(self, tmp_path: Path):
        litellm_file = tmp_path / "litellm_prices.json"
        litellm_data = {
            "gpt-4": {
                "input_cost_per_token": 3e-05,
                "output_cost_per_token": 6e-05,
                "litellm_provider": "openai",
            },
            "claude-3": {
                "input_cost_per_token": 1e-05,
                "output_cost_per_token": 3e-05,
                "litellm_provider": "anthropic",
            },
        }
        litellm_file.write_text(json.dumps(litellm_data), encoding="utf-8")
        ps = PricingSync(pricing_path=str(tmp_path / "prices.yaml"))
        count = ps.sync_from_litellm(str(litellm_file))
        assert count == 2
        assert ps.get_price("gpt-4") is not None

    def test_sync_from_litellm_skips_zero_price(self, tmp_path: Path):
        litellm_file = tmp_path / "litellm_prices.json"
        litellm_data = {
            "free-model": {
                "input_cost_per_token": 0.0,
                "output_cost_per_token": 0.0,
                "litellm_provider": "test",
            },
        }
        litellm_file.write_text(json.dumps(litellm_data), encoding="utf-8")
        ps = PricingSync(pricing_path=str(tmp_path / "prices.yaml"))
        count = ps.sync_from_litellm(str(litellm_file))
        assert count == 0

    def test_sync_from_litellm_missing_file(self, tmp_path: Path):
        ps = PricingSync(pricing_path=str(tmp_path / "prices.yaml"))
        count = ps.sync_from_litellm(str(tmp_path / "missing.json"))
        assert count == 0

    def test_sync_from_litellm_invalid_json(self, tmp_path: Path):
        litellm_file = tmp_path / "bad.json"
        litellm_file.write_text("not valid json{{{", encoding="utf-8")
        ps = PricingSync(pricing_path=str(tmp_path / "prices.yaml"))
        count = ps.sync_from_litellm(str(litellm_file))
        assert count == 0

    def test_sync_from_litellm_empty_path(self, tmp_path: Path):
        ps = PricingSync(pricing_path=str(tmp_path / "prices.yaml"))
        count = ps.sync_from_litellm("")
        assert count == 0


class TestPriceEntry:
    def test_price_entry_defaults(self):
        entry = PriceEntry(model="test", input_per_1k=1.0, output_per_1k=2.0, provider="p")
        assert entry.updated_at > 0
