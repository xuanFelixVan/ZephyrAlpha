# [BLUEPRINT] MOD-INT-API-LLM-POOL | docs/03_modules/_domain_intelligence/api_llm_pool/blueprint.md | §test
# [A_test] module_id: MOD-INT-API-LLM-POOL | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ApiLlmPool 单元测试 (MOD-INT-API-LLM-POOL, MVP)。

覆盖: provider 注册 Fail-Closed 校验与重复注册拒绝 / 计费台账成本确定性与
Agent×任务归集 / 未注册 provider 与负 token Fail-Closed / 健康度（连续失败
阈值、EMA 延迟）驱动调度 / 全不健康与成本超限 degrade_to_local 信号 /
usage_sink 异常不阻断 / frozen 不可变 / 零密钥字段。
"""

from __future__ import annotations

import dataclasses

import pytest

from zephyr.intelligence.api_llm_pool import (
    ApiLlmPool,
    ApiLlmPoolConfig,
    ApiProviderSpec,
    InvalidProviderSpecError,
    InvalidUsageError,
    ProviderAlreadyRegisteredError,
    ProviderNotRegisteredError,
    ProviderSelection,
    UsageRecord,
)


def _spec(provider: str = "deepseek", **kw) -> ApiProviderSpec:
    base = {
        "provider": provider,
        "model": f"{provider}-v4",
        "input_price_per_m": 1.0,
        "output_price_per_m": 2.0,
        "rate_limit_rpm": 60,
        "timeout_s": 30.0,
    }
    base.update(kw)
    return ApiProviderSpec(**base)


def _pool(**cfg_kw) -> ApiLlmPool:
    pool = ApiLlmPool(config=ApiLlmPoolConfig(**cfg_kw))
    pool.register_provider(_spec("deepseek"))
    pool.register_provider(_spec("glm", input_price_per_m=0.5, output_price_per_m=1.0))
    return pool


# ── 注册 ─────────────────────────────────────────────────────────────────────


class TestRegisterProvider:
    def test_register_ok(self) -> None:
        pool = _pool()
        assert set(pool.providers()) == {"deepseek", "glm"}

    @pytest.mark.parametrize(
        "kw",
        [
            {"provider": ""},
            {"model": ""},
            {"input_price_per_m": -0.1},
            {"output_price_per_m": -1.0},
            {"rate_limit_rpm": 0},
            {"rate_limit_rpm": -5},
            {"timeout_s": 0.0},
            {"timeout_s": -1.0},
        ],
    )
    def test_invalid_spec_fail_closed(self, kw) -> None:
        with pytest.raises(InvalidProviderSpecError):
            _spec(**kw)

    def test_duplicate_register_rejected(self) -> None:
        pool = _pool()
        with pytest.raises(ProviderAlreadyRegisteredError):
            pool.register_provider(_spec("deepseek"))

    def test_spec_frozen(self) -> None:
        spec = _spec()
        with pytest.raises(dataclasses.FrozenInstanceError):
            spec.provider = "x"  # type: ignore[misc]


# ── 计费台账 ─────────────────────────────────────────────────────────────────


class TestUsageLedger:
    def test_cost_deterministic(self) -> None:
        pool = _pool()
        rec = pool.record_usage("deepseek", "agent_a", "task_1", 1_000_000, 500_000)
        assert isinstance(rec, UsageRecord)
        # 1M×1.0 + 0.5M×2.0 = 2.0 USD
        assert rec.cost_usd == pytest.approx(2.0)

    def test_ledger_append_only(self) -> None:
        pool = _pool()
        pool.record_usage("deepseek", "agent_a", "task_1", 1000, 2000)
        pool.record_usage("glm", "agent_b", "task_2", 3000, 4000)
        ledger = pool.ledger()
        assert len(ledger) == 2
        assert isinstance(ledger, tuple)

    def test_total_cost_grouping(self) -> None:
        pool = _pool()
        pool.record_usage("deepseek", "agent_a", "task_1", 1_000_000, 0)  # 1.0
        pool.record_usage("deepseek", "agent_a", "task_2", 0, 1_000_000)  # 2.0
        pool.record_usage("glm", "agent_b", "task_1", 1_000_000, 1_000_000)  # 1.5
        assert pool.total_cost() == pytest.approx(4.5)
        assert pool.total_cost(agent_id="agent_a") == pytest.approx(3.0)
        assert pool.total_cost(task_id="task_1") == pytest.approx(2.5)
        assert pool.total_cost(agent_id="agent_b", task_id="task_1") == pytest.approx(1.5)

    def test_unregistered_provider_fail_closed(self) -> None:
        pool = _pool()
        with pytest.raises(ProviderNotRegisteredError):
            pool.record_usage("claude", "a", "t", 1, 1)

    @pytest.mark.parametrize("in_tok,out_tok", [(-1, 0), (0, -1), (-5, -5)])
    def test_negative_tokens_fail_closed(self, in_tok, out_tok) -> None:
        pool = _pool()
        with pytest.raises(InvalidUsageError):
            pool.record_usage("deepseek", "a", "t", in_tok, out_tok)

    def test_usage_sink_called_and_exception_tolerated(self) -> None:
        seen: list[dict] = []
        pool = ApiLlmPool(usage_sink=seen.append)
        pool.register_provider(_spec())
        rec = pool.record_usage("deepseek", "a", "t", 100, 200)
        assert len(seen) == 1
        assert seen[0]["provider"] == "deepseek"
        assert seen[0]["cost_usd"] == pytest.approx(rec.cost_usd)

        def _boom(_rec) -> None:
            raise RuntimeError("sink down")

        pool2 = ApiLlmPool(usage_sink=_boom)
        pool2.register_provider(_spec())
        rec2 = pool2.record_usage("deepseek", "a", "t", 100, 200)  # 不阻断
        assert len(pool2.ledger()) == 1
        assert rec2.cost_usd >= 0


# ── 健康度与调度 ─────────────────────────────────────────────────────────────


class TestHealthAndSelection:
    def test_initial_healthy(self) -> None:
        pool = _pool()
        sel = pool.select_provider(["deepseek", "glm"])
        assert isinstance(sel, ProviderSelection)
        assert sel.selected == "deepseek"
        assert sel.degrade_to_local is False

    def test_unhealthy_after_consecutive_failures(self) -> None:
        pool = _pool(unhealthy_threshold=3)
        for _ in range(3):
            pool.record_call_result("deepseek", success=False, latency_ms=100.0)
        health = pool.health("deepseek")
        assert health.consecutive_failures == 3
        assert health.is_healthy is False
        sel = pool.select_provider(["deepseek", "glm"])
        assert sel.selected == "glm"

    def test_success_resets_consecutive_failures(self) -> None:
        pool = _pool(unhealthy_threshold=3)
        pool.record_call_result("deepseek", success=False, latency_ms=50.0)
        pool.record_call_result("deepseek", success=False, latency_ms=50.0)
        pool.record_call_result("deepseek", success=True, latency_ms=80.0)
        health = pool.health("deepseek")
        assert health.consecutive_failures == 0
        assert health.success_count == 1
        assert health.failure_count == 2
        assert health.ema_latency_ms > 0

    def test_all_unhealthy_degrades_to_local(self) -> None:
        pool = _pool(unhealthy_threshold=1)
        pool.record_call_result("deepseek", success=False, latency_ms=10.0)
        pool.record_call_result("glm", success=False, latency_ms=10.0)
        sel = pool.select_provider(["deepseek", "glm"])
        assert sel.selected is None
        assert sel.degrade_to_local is True
        assert sel.reasons

    def test_preferred_chain_order_respected(self) -> None:
        pool = _pool()
        sel = pool.select_provider(["glm", "deepseek"])
        assert sel.selected == "glm"

    def test_unknown_provider_in_chain_skipped(self) -> None:
        pool = _pool()
        sel = pool.select_provider(["claude", "glm"])
        assert sel.selected == "glm"

    def test_health_unregistered_fail_closed(self) -> None:
        pool = _pool()
        with pytest.raises(ProviderNotRegisteredError):
            pool.health("claude")
        with pytest.raises(ProviderNotRegisteredError):
            pool.record_call_result("claude", success=True, latency_ms=1.0)

    def test_invalid_latency_fail_closed(self) -> None:
        pool = _pool()
        with pytest.raises(InvalidUsageError):
            pool.record_call_result("deepseek", success=True, latency_ms=-1.0)


# ── 成本超限降级信号 ─────────────────────────────────────────────────────────


class TestCostLimitDegrade:
    def test_cost_limit_exceeded_degrades(self) -> None:
        pool = _pool(cost_limit_usd=1.0)
        pool.record_usage("deepseek", "a", "t", 1_000_000, 500_000)  # 2.0 USD
        sel = pool.select_provider(["deepseek"])
        assert sel.degrade_to_local is True

    def test_cost_under_limit_no_degrade(self) -> None:
        pool = _pool(cost_limit_usd=100.0)
        pool.record_usage("deepseek", "a", "t", 1000, 1000)
        sel = pool.select_provider(["deepseek"])
        assert sel.selected == "deepseek"
        assert sel.degrade_to_local is False

    def test_no_limit_never_degrades_on_cost(self) -> None:
        pool = _pool()  # cost_limit_usd=None
        pool.record_usage("deepseek", "a", "t", 10_000_000, 10_000_000)
        sel = pool.select_provider(["deepseek"])
        assert sel.degrade_to_local is False

    def test_invalid_config_fail_closed(self) -> None:
        with pytest.raises(InvalidProviderSpecError):
            ApiLlmPoolConfig(unhealthy_threshold=0)
        with pytest.raises(InvalidProviderSpecError):
            ApiLlmPoolConfig(cost_limit_usd=-1.0)


# ── 零密钥 ───────────────────────────────────────────────────────────────────


class TestNoSecrets:
    def test_spec_has_no_secret_fields(self) -> None:
        fields = {f.name for f in dataclasses.fields(ApiProviderSpec)}
        leaked = {f for f in fields if any(k in f.lower() for k in ("key", "secret", "token_pwd", "password", "credential"))}
        assert leaked == set()
