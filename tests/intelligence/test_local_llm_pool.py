# [BLUEPRINT] MOD-INT-LOCAL-LLM-POOL | docs/03_modules/_domain_intelligence/local_llm_pool/blueprint.md | §test
# [A_test] module_id: MOD-INT-LOCAL-LLM-POOL | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# add-design-node tests/intelligence/test_local_llm_pool.py MOD-INT-LOCAL-LLM-POOL D_INTELLIGENCE planned --granularity file
"""LocalLlmPool 单元测试 (MOD-INT-LOCAL-LLM-POOL, MVP)。

覆盖: 模型规格非法 Fail-Closed / 重复注册 / 显存预算门超限拒载 /
健康度阈值判定 / select_model 角色优先与降级 / 未注册 Fail-Closed /
profile_sink 异常不阻断 / unload 未加载 Fail-Closed / gpu_stats_provider
异常降级内嵌台账。
"""

from __future__ import annotations

import pytest

from zephyr.intelligence.local_llm_pool import (
    InvalidLocalModelSpecError,
    LoadDecision,
    LocalLlmPool,
    LocalLlmPoolConfig,
    LocalModelAlreadyRegisteredError,
    LocalModelNotRegisteredError,
    LocalModelSelection,
    LocalModelSpec,
    PoolBudgets,
)


def _spec(name: str = "qwen", vram: float = 4.0, role: str = "primary") -> LocalModelSpec:
    return LocalModelSpec(name=name, quant="awq-4bit", vram_gb=vram, role=role)


class TestRegister:
    def test_ok(self) -> None:
        pool = LocalLlmPool()
        pool.register_model(_spec())
        assert pool.health("qwen").is_healthy is True

    def test_duplicate(self) -> None:
        pool = LocalLlmPool()
        pool.register_model(_spec())
        with pytest.raises(LocalModelAlreadyRegisteredError):
            pool.register_model(_spec())

    @pytest.mark.parametrize(
        "bad",
        [
            {"name": ""},
            {"vram_gb": -1},
            {"role": "bad"},
        ],
    )
    def test_invalid_spec(self, bad: dict) -> None:
        base = {"name": "qwen", "quant": "awq", "vram_gb": 4.0, "role": "primary"}
        base.update(bad)
        with pytest.raises(InvalidLocalModelSpecError):
            LocalModelSpec(**base)


class TestLoad:
    def test_ok(self) -> None:
        pool = LocalLlmPool()
        pool.register_model(_spec(vram=1.0))
        dec = pool.request_load("qwen", "intraday")
        assert dec.loaded is True

    def test_budget_exceeded(self) -> None:
        pool = LocalLlmPool(config=LocalLlmPoolConfig(budgets=PoolBudgets(intraday_gb=2.0)))
        pool.register_model(_spec(vram=3.0))
        dec = pool.request_load("qwen", "intraday")
        assert dec.loaded is False
        assert dec.degrade_to_api is True

    def test_unregistered(self) -> None:
        pool = LocalLlmPool()
        with pytest.raises(LocalModelNotRegisteredError):
            pool.request_load("qwen")

    def test_gpu_provider_fallback(self) -> None:
        def bad() -> dict:
            raise RuntimeError("boom")

        pool = LocalLlmPool(gpu_stats_provider=bad)
        pool.register_model(_spec(vram=1.0))
        dec = pool.request_load("qwen", "intraday")
        assert dec.loaded is True


class TestUnload:
    def test_ok(self) -> None:
        pool = LocalLlmPool()
        pool.register_model(_spec(vram=1.0))
        pool.request_load("qwen")
        dec = pool.request_unload("qwen")
        assert dec.loaded is False

    def test_not_loaded(self) -> None:
        pool = LocalLlmPool()
        pool.register_model(_spec(vram=1.0))
        with pytest.raises(LocalModelNotRegisteredError):
            pool.request_unload("qwen")


class TestHealth:
    def test_healthy(self) -> None:
        pool = LocalLlmPool()
        pool.register_model(_spec())
        h = pool.health("qwen")
        assert h.is_healthy is True

    def test_unhealthy(self) -> None:
        pool = LocalLlmPool(config=LocalLlmPoolConfig(unhealthy_threshold=2))
        pool.register_model(_spec())
        pool.record_call_result("qwen", False, 100)
        pool.record_call_result("qwen", False, 100)
        assert pool.health("qwen").is_healthy is False

    def test_profile_sink_error_not_blocking(self) -> None:
        def bad(model: str, data: dict) -> None:
            raise RuntimeError("boom")

        pool = LocalLlmPool(profile_sink=bad)
        pool.register_model(_spec())
        pool.record_call_result("qwen", True, 50)
        assert pool.health("qwen").success_count == 1


class TestSelect:
    def test_preferred_role(self) -> None:
        pool = LocalLlmPool()
        pool.register_model(_spec(name="qwen", role="primary", vram=1.0))
        pool.register_model(_spec(name="deep", role="backup", vram=1.0))
        pool.request_load("qwen")
        pool.request_load("deep")
        sel = pool.select_model(preferred_role="primary")
        assert sel.selected == "qwen"

    def test_no_loaded(self) -> None:
        pool = LocalLlmPool()
        pool.register_model(_spec(vram=1.0))
        sel = pool.select_model()
        assert sel.selected is None
        assert sel.degrade_to_api is True

    def test_unhealthy_fallback(self) -> None:
        pool = LocalLlmPool(config=LocalLlmPoolConfig(unhealthy_threshold=1))
        pool.register_model(_spec(name="qwen", vram=1.0))
        pool.request_load("qwen")
        pool.record_call_result("qwen", False, 100)
        sel = pool.select_model()
        assert sel.selected is None
        assert sel.degrade_to_api is True
