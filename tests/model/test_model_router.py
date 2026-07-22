# [A_test] module_id: MOD-GOV_model_router | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] tests.test_model_router
# [INVARIANTS] resolve_model returns "none" for C pipeline; fallback_chain_for returns list
# [MODIFY-GUARD] only when ModelRouter public API changes
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import failure -> skip
# [TESTS] pytest tests/test_model_router.py -q
# [TTL] task_bound

from __future__ import annotations

from dataclasses import dataclass, field

from zephyr.infrastructure.pipeline.model_router import ModelRouter


@dataclass
class MockTaskCard:
    execution_model: str = "deepseek"
    assigned_pipeline: str = "A"
    title: str = "normal task"
    tags: list[str] = field(default_factory=list)
    ai_autonomy_level: str = "safe"


class TestModelRouterResolveModel:
    def test_default_deepseek(self):
        card = MockTaskCard()
        assert ModelRouter.resolve_model(card) == "deepseek"

    def test_c_pipeline_returns_none(self):
        card = MockTaskCard(assigned_pipeline="C")
        assert ModelRouter.resolve_model(card) == "none"

    def test_critical_keyword_chinese(self):
        card = MockTaskCard(title="关键任务处理")
        assert ModelRouter.resolve_model(card) == "claude"

    def test_critical_keyword_english(self):
        card = MockTaskCard(title="Critical system rescue")
        assert ModelRouter.resolve_model(card) == "claude"

    def test_rescue_keyword(self):
        card = MockTaskCard(title="Emergency rescue operation")
        assert ModelRouter.resolve_model(card) == "claude"

    def test_security_tag(self):
        card = MockTaskCard(tags=["security"])
        assert ModelRouter.resolve_model(card) == "claude"

    def test_experimental_tag(self):
        card = MockTaskCard(tags=["experimental"])
        assert ModelRouter.resolve_model(card) == "claude"

    def test_unsafe_autonomy_level(self):
        card = MockTaskCard(ai_autonomy_level="unsafe")
        assert ModelRouter.resolve_model(card) == "claude"

    def test_safe_autonomy_level_uses_execution_model(self):
        card = MockTaskCard(execution_model="glm", ai_autonomy_level="safe")
        assert ModelRouter.resolve_model(card) == "glm"

    def test_no_tags_normal_task(self):
        card = MockTaskCard(execution_model="deepseek", tags=[], title="regular task")
        assert ModelRouter.resolve_model(card) == "deepseek"

    def test_other_tags_not_security_or_experimental(self):
        card = MockTaskCard(tags=["performance", "refactor"])
        assert ModelRouter.resolve_model(card) == "deepseek"

    def test_c_pipeline_overrides_all(self):
        card = MockTaskCard(assigned_pipeline="C", tags=["security"], title="Critical task")
        assert ModelRouter.resolve_model(card) == "none"

    def test_title_case_insensitive(self):
        card = MockTaskCard(title="CRITICAL MISSION")
        assert ModelRouter.resolve_model(card) == "claude"

    def test_glm_execution_model(self):
        card = MockTaskCard(execution_model="glm", assigned_pipeline="B")
        assert ModelRouter.resolve_model(card) == "glm"


class TestModelRouterFallbackChain:
    def test_deepseek_chain(self):
        chain = ModelRouter.fallback_chain_for("deepseek")
        assert chain == ["glm", "claude"]

    def test_glm_chain(self):
        chain = ModelRouter.fallback_chain_for("glm")
        assert chain == ["deepseek", "claude"]

    def test_claude_chain_empty(self):
        chain = ModelRouter.fallback_chain_for("claude")
        assert chain == []

    def test_unknown_model_empty(self):
        chain = ModelRouter.fallback_chain_for("unknown_model")
        assert chain == []


class TestModelRouterEstimateCost:
    def test_deepseek_cost(self):
        # 5.12.2#2 治本：estimate_cost 返回 float（总成本），非 dict
        result = ModelRouter.estimate_cost("deepseek", 1000)
        assert isinstance(result, float)
        assert result > 0.0

    def test_claude_cost(self):
        result = ModelRouter.estimate_cost("claude", 1000)
        assert result > 0.0

    def test_glm_cost_zero(self):
        result = ModelRouter.estimate_cost("glm", 1000)
        assert result == 0.0

    def test_unknown_model_zero(self):
        result = ModelRouter.estimate_cost("nonexistent", 1000)
        assert result == 0.0

    def test_zero_tokens(self):
        result = ModelRouter.estimate_cost("deepseek", 0)
        assert result == 0.0

    def test_cost_scales_with_tokens(self):
        cost_1k = ModelRouter.estimate_cost("deepseek", 1000)
        cost_2k = ModelRouter.estimate_cost("deepseek", 2000)
        assert abs(cost_2k - 2 * cost_1k) < 1e-9

    def test_input_output_breakdown(self):
        # 5.12.2#2 治本：分项明细用 estimate_cost_detailed
        result = ModelRouter.estimate_cost_detailed("deepseek", 1000)
        expected_input = (1000 / 1000.0) * ModelRouter.MODEL_COST_PER_1K_INPUT["deepseek"]
        expected_output = (1000 / 1000.0) * ModelRouter.MODEL_COST_PER_1K_OUTPUT["deepseek"]
        assert abs(result["input_cost"] - round(expected_input, 6)) < 1e-9
        assert abs(result["output_cost"] - round(expected_output, 6)) < 1e-9
        assert abs(result["total_cost"] - round(expected_input + expected_output, 6)) < 1e-9


class TestModelRouterModelVersion:
    def test_deepseek_version(self):
        assert ModelRouter.model_version_for("deepseek") == "deepseek-v4-pro"

    def test_glm_version(self):
        assert ModelRouter.model_version_for("glm") == "glm-5.1"

    def test_claude_version(self):
        assert ModelRouter.model_version_for("claude") == "claude-opus-4.7"

    def test_unknown_model_returns_name(self):
        assert ModelRouter.model_version_for("custom_model") == "custom_model"


class TestModelRouterContextLimit:
    def test_deepseek_limit(self):
        assert ModelRouter.context_limit_for("deepseek") == 128_000

    def test_glm_limit(self):
        assert ModelRouter.context_limit_for("glm") == 128_000

    def test_claude_limit(self):
        assert ModelRouter.context_limit_for("claude") == 200_000

    def test_unknown_model_default(self):
        assert ModelRouter.context_limit_for("unknown") == 128_000


class TestModelRouterClassVars:
    def test_fallback_chain_keys(self):
        assert set(ModelRouter.FALLBACK_CHAIN.keys()) == {"deepseek", "glm", "claude"}

    def test_model_version_map_keys(self):
        assert set(ModelRouter.MODEL_VERSION_MAP.keys()) == {"deepseek", "glm", "claude"}

    def test_context_limits_keys(self):
        assert set(ModelRouter.MODEL_CONTEXT_LIMITS.keys()) == {"deepseek", "glm", "claude"}

    def test_cost_per_1k_input_keys(self):
        assert set(ModelRouter.MODEL_COST_PER_1K_INPUT.keys()) == {"deepseek", "glm", "claude"}

    def test_cost_per_1k_output_keys(self):
        assert set(ModelRouter.MODEL_COST_PER_1K_OUTPUT.keys()) == {"deepseek", "glm", "claude"}

    def test_all_costs_non_negative(self):
        for model, cost in ModelRouter.MODEL_COST_PER_1K_INPUT.items():
            assert cost >= 0.0
        for model, cost in ModelRouter.MODEL_COST_PER_1K_OUTPUT.items():
            assert cost >= 0.0
