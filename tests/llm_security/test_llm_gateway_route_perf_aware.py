# [A_test] module_id: MOD-INF-009 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [BLUEPRINT] MOD-INF-009 | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/10_llm_infrastructure.md | §4-Phase1.4
# [MODULE] tests.llm_security.test_llm_gateway_route_perf_aware
# [DOMAIN] D_INFRA_RUNTIME
# [INVARIANTS] 纯路由元数据查询测试——route() 不发起任何网络/真实 LLM 调用；既有 hint 映射断言零破坏
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STARTUP] imported
# [MATURITY] testing
# [STABILITY] volatile
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/llm_security/test_llm_gateway_route_perf_aware.py
# [TTL] task_bound

"""
test_llm_gateway_route_perf_aware.py — LLMGateway.route() 接 ModelRouter perf-aware 决策（10号文 §4 Phase 1.4）
==================================================================================================================
零网络（route() 纯元数据查询，ModelRouter 决策仅消费内存常量）。覆盖：
- 返回含 tier/reason/performance_score 三字段，且既有五键（skill_id/provider/model/base_url/
  max_context_tokens）语义零变化
- tier 为合法 ModelTier 值；performance_score 为 float；reason 非空
- model_hint 命中 ModelRouter 已知 provider -> reason 含 preferred-provider 标记
- 未知 hint -> 既有 deepseek 配置兜底不变，三字段仍在
- 治理层故障（ModelRouter.route 抛错）-> 降级占位字段（tier=None，reason 标 router-unavailable），
  hint 映射不中断
"""

from __future__ import annotations

import pytest

budget_models = pytest.importorskip("zephyr.governance.ops_governance.budget_models")
gw_mod = pytest.importorskip("zephyr.infrastructure.pipeline.llm_gateway")
router_mod = pytest.importorskip("zephyr.governance.intelligence_governance.model_router")

LLMGateway = gw_mod.LLMGateway
ModelTier = budget_models.ModelTier

_LEGACY_KEYS = {"skill_id", "provider", "model", "base_url", "max_context_tokens"}
_PERF_KEYS = {"tier", "reason", "performance_score"}


class TestRoutePerfAwareFields:
    def test_route_returns_perf_aware_three_fields(self):
        result = LLMGateway.route("test-skill")
        assert _PERF_KEYS <= set(result)  # 三字段齐备
        assert _LEGACY_KEYS <= set(result)  # 既有五键零破坏

    def test_route_tier_is_valid_model_tier_value(self):
        result = LLMGateway.route("test-skill")
        assert result["tier"] in {t.value for t in ModelTier}
        assert isinstance(result["reason"], str) and result["reason"]
        assert isinstance(result["performance_score"], float)

    def test_route_default_hint_deepseek_preferred_reason(self):
        # 无缺省 hint -> provider=deepseek；deepseek 在 ModelRouter ECONOMY 层有候选 -> preferred-provider 命中
        result = LLMGateway.route("test-skill")
        assert result["provider"] == "deepseek"
        assert "preferred-provider:deepseek" in result["reason"]
        assert result["tier"] == ModelTier.ECONOMY.value

    def test_route_known_hint_keeps_legacy_mapping(self):
        result = LLMGateway.route("test-skill", model_hint="claude")
        assert result["provider"] == "claude"  # hint 映射语义不变
        assert result["model"] == gw_mod._PROVIDERS["claude"].default_model
        assert result["max_context_tokens"] == gw_mod._PROVIDERS["claude"].max_context_tokens
        assert _PERF_KEYS <= set(result)

    def test_route_unknown_hint_fallback_config_and_fields_present(self):
        result = LLMGateway.route("test-skill", model_hint="nonexistent")
        assert result["provider"] == "nonexistent"  # 既有透传语义不变
        assert result["model"] == gw_mod._PROVIDERS["deepseek"].default_model
        assert result["tier"] in {t.value for t in ModelTier}
        assert isinstance(result["performance_score"], float)


class TestRouteRouterFailureDegradation:
    def test_router_exception_degrades_to_placeholder_fields(self, monkeypatch):
        def _boom(*args, **kwargs):
            raise RuntimeError("model_router store down")

        monkeypatch.setattr(router_mod.ModelRouter, "route", _boom)
        result = LLMGateway.route("test-skill", model_hint="claude")
        # hint 映射不中断（既有消费方零破坏）
        assert result["provider"] == "claude"
        assert result["model"] == gw_mod._PROVIDERS["claude"].default_model
        # 三字段以占位值存在并在 reason 标注
        assert result["tier"] is None
        assert result["reason"].startswith("router-unavailable")
        assert result["performance_score"] == 0.0

    def test_router_import_failure_degrades(self, monkeypatch):
        import builtins

        real_import = builtins.__import__

        def _guarded_import(name, *args, **kwargs):
            if "model_router" in name:
                raise ImportError("simulated governance layer missing")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _guarded_import)
        result = LLMGateway.route("test-skill")
        assert result["provider"] == "deepseek"
        assert result["tier"] is None
        assert "router-unavailable" in result["reason"]
