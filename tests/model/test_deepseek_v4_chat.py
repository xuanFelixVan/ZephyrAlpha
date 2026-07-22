# [A_test] module_id: MOD-GOV_deepseek_v4_chat | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] tests.test_deepseek_v4_chat
# [INVARIANTS] test_deepseek_v4_chat完整性
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

from zephyr.intelligence.model_profiling.deepseek_v4_chat import (
    DEFAULT_BASE_URL,
    PRICING_RMB,
    SYSTEM_PROMPTS,
    DeepSeekV4Chat,
)


class TestDeepSeekV4ChatInit:
    def test_default_init(self):
        chat = DeepSeekV4Chat()
        assert chat._model == "deepseek-v4-pro"
        assert isinstance(chat._api_key, str)
        assert chat._base_url == DEFAULT_BASE_URL
        assert chat._thinking is True
        assert chat._temperature == 0.1
        assert chat._max_tokens == 4096
        assert chat._timeout == 120.0
        assert chat.cumulative_cost_rmb == 0.0
        assert chat.cumulative_input_tokens == 0
        assert chat.cumulative_output_tokens == 0
        assert chat.call_count == 0

    def test_custom_init(self):
        chat = DeepSeekV4Chat(
            model="deepseek-v4-flash",
            api_key="sk-test",
            base_url="https://custom.api.com/",
            thinking=False,
            temperature=0.5,
            max_tokens=2048,
            timeout_s=60.0,
        )
        assert chat._model == "deepseek-v4-flash"
        assert chat._api_key == "sk-test"
        assert chat._base_url == "https://custom.api.com"
        assert chat._thinking is False
        assert chat._temperature == 0.5
        assert chat._max_tokens == 2048
        assert chat._timeout == 60.0

    def test_none_api_key_falls_back_to_env(self):
        import os as _os

        chat = DeepSeekV4Chat(api_key=None)
        expected = _os.getenv("DEEPSEEK_API_KEY", "")
        assert chat._api_key == expected

    def test_empty_api_key_falls_back_to_env(self):
        import os as _os

        chat = DeepSeekV4Chat(api_key="")
        expected = _os.getenv("DEEPSEEK_API_KEY", "")
        assert chat._api_key == expected


class TestModelProperty:
    def test_model_thinking(self):
        chat = DeepSeekV4Chat(model="deepseek-v4-pro", thinking=True)
        assert chat.model == "deepseek-v4-pro-thinking"

    def test_model_non_thinking(self):
        chat = DeepSeekV4Chat(model="deepseek-v4-flash", thinking=False)
        assert chat.model == "deepseek-v4-flash-non-thinking"

    def test_model_id_equals_model(self):
        chat = DeepSeekV4Chat()
        assert chat.model_id == chat.model


class TestSupportedWorkTypes:
    def test_returns_frozenset(self):
        chat = DeepSeekV4Chat()
        assert isinstance(chat.supported_work_types, frozenset)

    def test_supported_types_count(self):
        chat = DeepSeekV4Chat()
        assert len(chat.supported_work_types) == 31

    def test_matches_system_prompts_keys(self):
        chat = DeepSeekV4Chat()
        assert chat.supported_work_types == frozenset(SYSTEM_PROMPTS.keys())


class TestResetCostCounters:
    def test_resets_all_counters(self):
        chat = DeepSeekV4Chat()
        chat.cumulative_cost_rmb = 1.5
        chat.cumulative_input_tokens = 100
        chat.cumulative_output_tokens = 200
        chat.call_count = 5
        chat.reset_cost_counters()
        assert chat.cumulative_cost_rmb == 0.0
        assert chat.cumulative_input_tokens == 0
        assert chat.cumulative_output_tokens == 0
        assert chat.call_count == 0


class TestParseJson:
    def test_valid_json(self):
        result = DeepSeekV4Chat._parse_json('{"key": "value"}')
        assert result == {"key": "value"}

    def test_json_in_code_block(self):
        raw = '```json\n{"key": "value"}\n```'
        result = DeepSeekV4Chat._parse_json(raw)
        assert result == {"key": "value"}

    def test_invalid_json_returns_empty(self):
        result = DeepSeekV4Chat._parse_json("not json at all")
        assert result == {}

    def test_empty_string_returns_empty(self):
        result = DeepSeekV4Chat._parse_json("")
        assert result == {}

    def test_json_with_extra_text(self):
        raw = 'Here is the result: {"key": "value"} done'
        result = DeepSeekV4Chat._parse_json(raw)
        assert result == {"key": "value"}

    def test_expected_keys_missing(self):
        result = DeepSeekV4Chat._parse_json('{"key": "value"}', expected_keys=["missing"])
        assert result == {"key": "value"}

    def test_non_dict_json_returns_empty(self):
        result = DeepSeekV4Chat._parse_json("[1, 2, 3]")
        assert result == {}


class TestStripThinkBlock:
    def test_with_think_tags(self):
        text = "<think>reasoning here</think> actual output"
        result = DeepSeekV4Chat._strip_think_block(text)
        assert "actual output" in result
        assert "reasoning" not in result

    def test_no_think_tags(self):
        text = "just normal output"
        result = DeepSeekV4Chat._strip_think_block(text)
        assert result == "just normal output"

    def test_empty_string(self):
        result = DeepSeekV4Chat._strip_think_block("")
        assert result == ""

    def test_none_input(self):
        result = DeepSeekV4Chat._strip_think_block(None)
        assert result is None


class TestPricingRmb:
    def test_has_both_models(self):
        assert "deepseek-v4-flash" in PRICING_RMB
        assert "deepseek-v4-pro" in PRICING_RMB

    @pytest.mark.parametrize("model", ["deepseek-v4-flash", "deepseek-v4-pro"])
    def test_required_keys(self, model):
        assert "input_per_1M" in PRICING_RMB[model]
        assert "output_per_1M" in PRICING_RMB[model]
        assert "input_cache_hit_per_1M" in PRICING_RMB[model]

    @pytest.mark.parametrize("model", ["deepseek-v4-flash", "deepseek-v4-pro"])
    def test_prices_are_positive(self, model):
        assert PRICING_RMB[model]["input_per_1M"] > 0
        assert PRICING_RMB[model]["output_per_1M"] > 0


class TestSystemPrompts:
    def test_prompts_count(self):
        assert len(SYSTEM_PROMPTS) == 31

    def test_all_values_are_strings(self):
        for key, value in SYSTEM_PROMPTS.items():
            assert isinstance(value, str), f"{key} prompt is not a string"
            assert len(value) > 0, f"{key} prompt is empty"


class TestDefaultBaseUrl:
    def test_value(self):
        assert DEFAULT_BASE_URL == "https://api.deepseek.com"
