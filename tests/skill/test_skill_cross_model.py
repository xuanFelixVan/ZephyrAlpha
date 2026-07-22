# [A_test] module_id: MOD-GOV_skill_cross_model | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_cross_model
# [INVARIANTS] SkillCrossModel must correctly adapt messages across model providers
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 = all pass; exit != 0 = regression
# [TESTS] tests/test_skill_cross_model.py
# [TTL] task_bound


from zephyr.autonomy_core.skills.skill_cross_model import (
    CrossModelContext,
    ModelCapability,
    ModelProvider,
    SkillCrossModel,
)


class TestModelProviderEnum:
    def test_all_providers_exist(self):
        assert ModelProvider.DEEPSEEK.value == "DeepSeek"
        assert ModelProvider.CLAUDE.value == "Claude"
        assert ModelProvider.GPT.value == "GPT"
        assert ModelProvider.GEMINI.value == "Gemini"
        assert ModelProvider.QWEN.value == "Qwen"
        assert ModelProvider.LLAMA.value == "Llama"
        assert ModelProvider.MISTRAL.value == "Mistral"


class TestModelCapabilityDataclass:
    def test_defaults(self):
        cap = ModelCapability(provider=ModelProvider.DEEPSEEK, max_context_tokens=131072)
        assert cap.supports_system_prompt is True
        assert cap.supports_function_calling is False
        assert cap.supports_streaming is False
        assert cap.supports_vision is False
        assert cap.prompt_format == "default"
        assert cap.tag_style == "default"
        assert cap.stop_tokens == []


class TestCrossModelContextDataclass:
    def test_defaults(self):
        ctx = CrossModelContext()
        assert ctx.system_prompt == ""
        assert ctx.user_content == ""
        assert ctx.tools == []
        assert ctx.history == []
        assert ctx.metadata == {}

    def test_custom_values(self):
        ctx = CrossModelContext(
            system_prompt="You are helpful",
            user_content="Hello",
            tools=[{"name": "tool1"}],
            history=[{"role": "user", "content": "Hi"}],
            metadata={"key": "val"},
        )
        assert ctx.system_prompt == "You are helpful"
        assert ctx.user_content == "Hello"
        assert len(ctx.tools) == 1
        assert len(ctx.history) == 1


class TestSkillCrossModelInstantiation:
    def test_default_provider(self):
        scm = SkillCrossModel()
        assert scm._default_provider == "DeepSeek"

    def test_custom_default_provider(self):
        scm = SkillCrossModel(default_provider="Claude")
        assert scm._default_provider == "Claude"

    def test_internal_state_initialized(self):
        scm = SkillCrossModel()
        assert scm._fallback_chain == []
        assert scm._adapter_registry == {}


class TestGetCapability:
    def test_known_provider(self):
        scm = SkillCrossModel()
        cap = scm.get_capability("DeepSeek")
        assert cap is not None
        assert cap.provider == ModelProvider.DEEPSEEK
        assert cap.max_context_tokens == 131072

    def test_unknown_provider_returns_none(self):
        scm = SkillCrossModel()
        assert scm.get_capability("UnknownModel") is None

    def test_all_known_providers(self):
        scm = SkillCrossModel()
        for name in ("DeepSeek", "Claude", "GPT", "Gemini", "Qwen"):
            cap = scm.get_capability(name)
            assert cap is not None


class TestSupportsFeature:
    def test_deepseek_function_calling(self):
        scm = SkillCrossModel()
        assert scm.supports_feature("DeepSeek", "function_calling") is True

    def test_deepseek_vision(self):
        scm = SkillCrossModel()
        assert scm.supports_feature("DeepSeek", "vision") is False

    def test_claude_vision(self):
        scm = SkillCrossModel()
        assert scm.supports_feature("Claude", "vision") is True

    def test_unknown_provider_returns_false(self):
        scm = SkillCrossModel()
        assert scm.supports_feature("UnknownModel", "function_calling") is False

    def test_unknown_feature_returns_false(self):
        scm = SkillCrossModel()
        assert scm.supports_feature("DeepSeek", "nonexistent_feature") is False


class TestSetFallbackChain:
    def test_valid_providers(self):
        scm = SkillCrossModel()
        scm.set_fallback_chain(["Claude", "GPT", "Qwen"])
        assert scm._fallback_chain == ["Claude", "GPT", "Qwen"]

    def test_filters_unknown_providers(self):
        scm = SkillCrossModel()
        scm.set_fallback_chain(["Claude", "FakeModel", "GPT"])
        assert scm._fallback_chain == ["Claude", "GPT"]

    def test_empty_list(self):
        scm = SkillCrossModel()
        scm.set_fallback_chain([])
        assert scm._fallback_chain == []

    def test_all_unknown(self):
        scm = SkillCrossModel()
        scm.set_fallback_chain(["Fake1", "Fake2"])
        assert scm._fallback_chain == []


class TestResolveProvider:
    def test_preferred_available(self):
        scm = SkillCrossModel()
        assert scm.resolve_provider("Claude") == "Claude"

    def test_preferred_none_uses_default(self):
        scm = SkillCrossModel()
        assert scm.resolve_provider(None) == "DeepSeek"

    def test_preferred_unknown_falls_back(self):
        scm = SkillCrossModel()
        scm.set_fallback_chain(["GPT", "Qwen"])
        assert scm.resolve_provider("UnknownModel") == "GPT"

    def test_preferred_and_fallback_both_unknown(self):
        scm = SkillCrossModel(default_provider="DeepSeek")
        scm.set_fallback_chain([])
        result = scm.resolve_provider("UnknownModel")
        assert result == "DeepSeek"


class TestAdaptMessages:
    def test_basic_openai_format(self):
        scm = SkillCrossModel()
        ctx = CrossModelContext(system_prompt="Be helpful", user_content="Hello")
        result = scm.adapt_messages(ctx, "DeepSeek")
        assert result["provider"] == "DeepSeek"
        assert result["format"] == "openai"
        assert any(m["role"] == "system" for m in result["messages"])

    def test_claude_system_prompt_as_role(self):
        scm = SkillCrossModel()
        ctx = CrossModelContext(system_prompt="Be helpful", user_content="Hello")
        result = scm.adapt_messages(ctx, "Claude")
        system_msgs = [m for m in result["messages"] if m.get("role") == "system"]
        assert len(system_msgs) == 1
        assert system_msgs[0]["content"] == "Be helpful"

    def test_anthropic_tag_style_wraps_system(self):
        from zephyr.autonomy_core.skills.skill_cross_model import _MODEL_CAPABILITIES

        scm = SkillCrossModel()
        ctx = CrossModelContext(system_prompt="Be helpful", user_content="Hello")
        orig = _MODEL_CAPABILITIES.get("Claude")
        _MODEL_CAPABILITIES["Claude"] = orig.__class__(
            provider=orig.provider,
            max_context_tokens=orig.max_context_tokens,
            supports_system_prompt=orig.supports_system_prompt,
            supports_function_calling=orig.supports_function_calling,
            supports_streaming=orig.supports_streaming,
            supports_vision=orig.supports_vision,
            prompt_format=orig.prompt_format,
            tag_style="anthropic",
            stop_tokens=orig.stop_tokens,
        )
        try:
            result = scm.adapt_messages(ctx, "Claude")
            wrapped = [m for m in result["messages"] if "<system>" in m.get("content", "")]
            assert len(wrapped) == 1
        finally:
            _MODEL_CAPABILITIES["Claude"] = orig

    def test_unknown_provider_returns_error(self):
        scm = SkillCrossModel()
        ctx = CrossModelContext(user_content="Hello")
        result = scm.adapt_messages(ctx, "UnknownModel")
        assert "error" in result

    def test_history_included(self):
        scm = SkillCrossModel()
        ctx = CrossModelContext(
            user_content="Hello",
            history=[{"role": "user", "content": "Previous"}, {"role": "assistant", "content": "Response"}],
        )
        result = scm.adapt_messages(ctx, "DeepSeek")
        assert len(result["messages"]) >= 3

    def test_empty_context(self):
        scm = SkillCrossModel()
        ctx = CrossModelContext()
        result = scm.adapt_messages(ctx, "DeepSeek")
        assert result["provider"] == "DeepSeek"
        assert result["messages"] == []

    def test_tools_adapted_for_anthropic(self):
        scm = SkillCrossModel()
        ctx = CrossModelContext(
            user_content="Use tool",
            tools=[{"function": {"name": "my_tool", "description": "A tool", "parameters": {"type": "object"}}}],
        )
        result = scm.adapt_messages(ctx, "Claude")
        assert "tools" in result
        assert result["tools"][0].get("name") == "my_tool"
        assert "function" not in result["tools"][0]

    def test_tools_passthrough_for_openai(self):
        scm = SkillCrossModel()
        tools = [{"function": {"name": "my_tool", "description": "A tool", "parameters": {}}}]
        ctx = CrossModelContext(user_content="Use tool", tools=tools)
        result = scm.adapt_messages(ctx, "DeepSeek")
        assert result["tools"] == tools


class TestNormalizeOutput:
    def test_strips_stop_tokens(self):
        scm = SkillCrossModel()
        raw = "Hello world<|end▁of▁sentence|>extra"
        result = scm.normalize_output(raw, "DeepSeek")
        assert "<|end▁of▁sentence|>" not in result
        assert result == "Hello world"

    def test_xml_tag_removal_for_claude(self):
        scm = SkillCrossModel()
        raw = "<system>Be helpful</system><function_calls><invoke>call</invoke></function_calls>Result"
        result = scm.normalize_output(raw, "Claude")
        assert "<system>" not in result
        assert "<function_calls>" not in result
        assert "<invoke>" not in result
        assert "Result" in result

    def test_unknown_provider_returns_raw(self):
        scm = SkillCrossModel()
        raw = "Hello world"
        result = scm.normalize_output(raw, "UnknownModel")
        assert result == raw

    def test_no_stop_tokens_in_output(self):
        scm = SkillCrossModel()
        raw = "Clean output"
        result = scm.normalize_output(raw, "DeepSeek")
        assert result == "Clean output"

    def test_empty_string(self):
        scm = SkillCrossModel()
        result = scm.normalize_output("", "DeepSeek")
        assert result == ""


class TestScoreCompatibility:
    def test_known_provider_high_score(self):
        scm = SkillCrossModel()
        result = scm.score_compatibility("Short prompt", "DeepSeek")
        assert result["score"] == 1.0
        assert result["issues"] == []

    def test_unknown_provider_zero_score(self):
        scm = SkillCrossModel()
        result = scm.score_compatibility("prompt", "UnknownModel")
        assert result["score"] == 0.0
        assert len(result["issues"]) > 0

    def test_long_prompt_reduces_score(self):
        scm = SkillCrossModel()
        long_prompt = "x" * 400000
        result = scm.score_compatibility(long_prompt, "DeepSeek")
        assert result["score"] < 1.0
        assert any("context window" in i for i in result["issues"])

    def test_score_never_below_zero(self):
        scm = SkillCrossModel()
        long_prompt = "x" * 1000000
        result = scm.score_compatibility(long_prompt, "DeepSeek")
        assert result["score"] >= 0.0


class TestAdapt:
    def test_compatible_provider(self):
        scm = SkillCrossModel()
        result = scm.adapt("my-skill", "Claude")
        assert result["compatible"] is True
        assert result["target_model"] == "Claude"
        assert result["max_context"] == 200000
        assert result["features"]["vision"] is True

    def test_incompatible_provider(self):
        scm = SkillCrossModel()
        result = scm.adapt("my-skill", "UnknownModel")
        assert result["compatible"] is False
        assert result["max_context"] == 0
        assert result["features"] == {}


class TestListProviders:
    def test_returns_all_known_providers(self):
        scm = SkillCrossModel()
        providers = scm.list_providers()
        names = [p["name"] for p in providers]
        assert "DeepSeek" in names
        assert "Claude" in names
        assert "GPT" in names
        assert "Gemini" in names
        assert "Qwen" in names

    def test_provider_has_required_fields(self):
        scm = SkillCrossModel()
        providers = scm.list_providers()
        for p in providers:
            assert "name" in p
            assert "max_context" in p
            assert "format" in p
            assert "features" in p
            assert "function_calling" in p["features"]
