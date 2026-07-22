# [A_test] module_id: MOD-GOV_llm_gateway | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_llm_gateway
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/test_llm_gateway.py
# [TTL] task_bound

from __future__ import annotations

import os
from unittest.mock import patch

from zephyr.infrastructure.pipeline.llm_gateway import (
    _PROVIDERS,
    LLMGateway,
    LLMResponse,
    ProviderConfig,
)


class TestLLMResponse:
    def test_construction_with_defaults(self):
        resp = LLMResponse(content="hello", model="test-model", provider="test")
        assert resp.content == "hello"
        assert resp.model == "test-model"
        assert resp.provider == "test"
        assert resp.tokens_input == 0
        assert resp.tokens_output == 0
        assert resp.cost_usd == 0.0
        assert resp.latency_ms == 0
        assert resp.simulated is False
        assert resp.error is None

    def test_construction_with_all_fields(self):
        resp = LLMResponse(
            content="world",
            model="gpt-4",
            provider="openai",
            tokens_input=100,
            tokens_output=50,
            cost_usd=0.05,
            latency_ms=1200,
            simulated=True,
            error="timeout",
        )
        assert resp.content == "world"
        assert resp.model == "gpt-4"
        assert resp.provider == "openai"
        assert resp.tokens_input == 100
        assert resp.tokens_output == 50
        assert resp.cost_usd == 0.05
        assert resp.latency_ms == 1200
        assert resp.simulated is True
        assert resp.error == "timeout"

    def test_empty_content(self):
        resp = LLMResponse(content="", model="m", provider="p")
        assert resp.content == ""

    def test_error_field_accepts_none_and_str(self):
        resp_none = LLMResponse(content="a", model="m", provider="p", error=None)
        resp_str = LLMResponse(content="a", model="m", provider="p", error="fail")
        assert resp_none.error is None
        assert resp_str.error == "fail"


class TestProviderConfig:
    def test_construction_with_required_fields(self):
        cfg = ProviderConfig(
            base_url="https://api.test.com",
            default_model="test-model",
            api_key_env="TEST_API_KEY",
        )
        assert cfg.base_url == "https://api.test.com"
        assert cfg.default_model == "test-model"
        assert cfg.api_key_env == "TEST_API_KEY"

    def test_defaults(self):
        cfg = ProviderConfig(
            base_url="https://api.test.com",
            default_model="test-model",
            api_key_env="TEST_API_KEY",
        )
        assert cfg.fallback is None
        assert cfg.max_context_tokens == 128_000
        assert cfg.cost_per_1k_input == 0.0
        assert cfg.cost_per_1k_output == 0.0

    def test_with_all_fields(self):
        cfg = ProviderConfig(
            base_url="https://api.test.com",
            default_model="test-model",
            api_key_env="TEST_API_KEY",
            fallback="other",
            max_context_tokens=200_000,
            cost_per_1k_input=0.01,
            cost_per_1k_output=0.05,
        )
        assert cfg.fallback == "other"
        assert cfg.max_context_tokens == 200_000
        assert cfg.cost_per_1k_input == 0.01
        assert cfg.cost_per_1k_output == 0.05


class TestProviders:
    def test_has_four_providers(self):
        assert len(_PROVIDERS) == 4

    def test_has_expected_provider_keys(self):
        expected = {"deepseek", "glm", "claude", "openai"}
        assert set(_PROVIDERS.keys()) == expected

    def test_each_provider_has_required_config_keys(self):
        for name, cfg in _PROVIDERS.items():
            assert isinstance(cfg, ProviderConfig), f"{name} is not ProviderConfig"
            assert cfg.base_url, f"{name} missing base_url"
            assert cfg.default_model, f"{name} missing default_model"
            assert cfg.api_key_env, f"{name} missing api_key_env"
            assert cfg.max_context_tokens > 0, f"{name} max_context_tokens must be > 0"

    def test_deepseek_falls_back_to_glm(self):
        assert _PROVIDERS["deepseek"].fallback == "glm"

    def test_glm_falls_back_to_deepseek(self):
        assert _PROVIDERS["glm"].fallback == "deepseek"

    def test_claude_has_no_fallback(self):
        assert _PROVIDERS["claude"].fallback is None

    def test_openai_has_no_fallback(self):
        assert _PROVIDERS["openai"].fallback is None


class TestLLMGatewayListProviders:
    def test_returns_list(self):
        providers = LLMGateway.list_providers()
        assert isinstance(providers, list)

    def test_contains_expected_providers(self):
        providers = LLMGateway.list_providers()
        assert "deepseek" in providers
        assert "glm" in providers
        assert "claude" in providers
        assert "openai" in providers

    def test_returns_four_providers(self):
        assert len(LLMGateway.list_providers()) == 4


class TestLLMGatewayGetProviderConfig:
    def test_known_provider_returns_config(self):
        cfg = LLMGateway.get_provider_config("deepseek")
        assert cfg is not None
        assert isinstance(cfg, ProviderConfig)
        assert cfg.default_model is not None

    def test_unknown_provider_returns_none(self):
        cfg = LLMGateway.get_provider_config("nonexistent")
        assert cfg is None

    def test_all_known_providers_return_config(self):
        for name in ["deepseek", "glm", "claude", "openai"]:
            cfg = LLMGateway.get_provider_config(name)
            assert cfg is not None, f"{name} should return a config"


class TestLLMGatewayRoute:
    def test_returns_dict_with_required_keys(self):
        result = LLMGateway.route("test-skill")
        assert "skill_id" in result
        assert "provider" in result
        assert "model" in result
        assert "base_url" in result
        assert "max_context_tokens" in result

    def test_default_provider_is_deepseek(self):
        result = LLMGateway.route("test-skill")
        assert result["provider"] == "deepseek"
        assert result["skill_id"] == "test-skill"

    def test_model_hint_overrides_provider(self):
        result = LLMGateway.route("test-skill", model_hint="claude")
        assert result["provider"] == "claude"
        assert result["model"] == _PROVIDERS["claude"].default_model

    def test_unknown_model_hint_uses_deepseek_config(self):
        result = LLMGateway.route("test-skill", model_hint="nonexistent")
        assert result["provider"] == "nonexistent"
        assert result["model"] == _PROVIDERS["deepseek"].default_model
        assert result["max_context_tokens"] == _PROVIDERS["deepseek"].max_context_tokens

    def test_max_context_tokens_matches_config(self):
        result = LLMGateway.route("test-skill", model_hint="claude")
        assert result["max_context_tokens"] == _PROVIDERS["claude"].max_context_tokens


class TestLLMGatewayCall:
    def test_no_api_key_returns_simulated_response(self):
        with patch.dict(os.environ, {}, clear=False):
            for key in ["DEEPSEEK_API_KEY", "GLM_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"]:
                os.environ.pop(key, None)
            resp = LLMGateway.call(
                [{"role": "user", "content": "test"}],
                provider="deepseek",
                fallback_chain=["deepseek"],
            )
            assert resp.simulated is True
            assert resp.error is not None

    def test_all_providers_fail_gracefully_without_keys(self):
        with patch.dict(os.environ, {}, clear=False):
            for provider in ["deepseek", "glm", "claude", "openai"]:
                env_key = _PROVIDERS[provider].api_key_env
                os.environ.pop(env_key, None)
            resp = LLMGateway.call(
                [{"role": "user", "content": "test"}],
                provider="deepseek",
            )
            assert resp.simulated is True

    def test_empty_messages_returns_simulated(self):
        with patch.dict(os.environ, {}, clear=False):
            for key in ["DEEPSEEK_API_KEY", "GLM_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"]:
                os.environ.pop(key, None)
            resp = LLMGateway.call([], provider="deepseek", fallback_chain=["deepseek"])
            assert resp.simulated is True

    def test_response_has_correct_provider(self):
        with patch.dict(os.environ, {}, clear=False):
            for key in ["DEEPSEEK_API_KEY", "GLM_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"]:
                os.environ.pop(key, None)
            resp = LLMGateway.call(
                [{"role": "user", "content": "test"}],
                provider="deepseek",
                fallback_chain=["deepseek"],
            )
            assert resp.provider == "deepseek"

    def test_fallback_chain_tries_next_provider(self):
        with patch.dict(os.environ, {}, clear=False):
            for key in ["DEEPSEEK_API_KEY", "GLM_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"]:
                os.environ.pop(key, None)
            resp = LLMGateway.call(
                [{"role": "user", "content": "test"}],
                provider="deepseek",
                fallback_chain=["deepseek", "glm"],
            )
            assert resp.simulated is True
