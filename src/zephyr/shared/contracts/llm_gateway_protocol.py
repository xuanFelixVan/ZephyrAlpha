# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §4
# [MODULE] zephyr.shared.contracts.llm_gateway_protocol
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.infrastructure.pipeline; zephyr.infrastructure.auto_fix_engine
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Protocol MUST NOT import from zephyr.trading; only structural subtyping
# [MODIFY-GUARD] shared/contracts/__init__.py; all consumers of LLMGateway
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] LLMGatewayProtocol.call returns LLMResponse; LLMResponse.error is set on failure
# [TESTS] tests/test_llm_gateway_protocol.py
# [A_module] module_id=MOD-SHR_llm_gateway_protocol | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
LLMGatewayProtocol — LLM 网关抽象接口
=====================================
从 zephyr.infrastructure.pipeline.llm_gateway.LLMGateway 提取的 Protocol 接口。
D-INFRA 和 D-ORCH 均依赖此接口，消除跨域直接依赖。

实现方: zephyr.infrastructure.pipeline.llm_gateway.LLMGateway
消费者: zephyr.infrastructure.pipeline.llm_gateway
        zephyr.infrastructure.auto_fix_engine.llm_fix_adapter
        zephyr.integration.pipeline_orchestrator
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True)
class LLMResponse:
    """LLM 调用响应 — 与 orchestration.agent_lifecycle.llm_gateway.LLMResponse 结构一致。"""

    content: str
    model: str
    provider: str
    tokens_input: int = 0
    tokens_output: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0
    simulated: bool = False
    error: str | None = None


@dataclass(frozen=True)
class ProviderConfig:
    """LLM Provider 配置 — 与 orchestration.agent_lifecycle.llm_gateway.ProviderConfig 结构一致。"""

    base_url: str
    default_model: str
    api_key_env: str
    fallback: str | None = None
    max_context_tokens: int = 128_000
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0


@runtime_checkable
class LLMGatewayProtocol(Protocol):
    """LLM 网关 Protocol — 多模型智能路由 + 降级链。

    实现方 MUST 提供以下 4 个 classmethod 签名。
    消费方通过此 Protocol 类型注解，运行时通过 ServiceRegistry/工厂获取具体实例。
    """

    # 5.143.2 修复: Protocol 声明为 classmethod 以匹配实现 (LLMGateway 全部用 @classmethod),
    # 原声明为实例方法 (def call(self, ...)) 导致 runtime_checkable isinstance 检查失效
    @classmethod
    def call(
        cls,
        messages: list[dict[str, str]],
        *,
        provider: str = "deepseek",
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
        fallback_chain: list[str] | None = None,
    ) -> LLMResponse:
        """发送消息到 LLM，返回响应。支持降级链自动切换 provider。"""
        ...

    @classmethod
    def route(cls, skill_id: str, model_hint: str | None = None) -> dict[str, Any]:
        """根据 skill_id 和模型提示，返回路由信息。"""
        ...

    @classmethod
    def list_providers(cls) -> list[str]:
        """列出所有可用的 LLM provider 名称。"""
        ...

    @classmethod
    def get_provider_config(cls, provider: str) -> ProviderConfig | None:
        """获取指定 provider 的配置。"""
        ...


__all__ = [
    "LLMGatewayProtocol",
    "LLMResponse",
    "ProviderConfig",
]
