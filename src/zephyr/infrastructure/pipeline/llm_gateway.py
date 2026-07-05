# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] zephyr.infrastructure.pipeline.llm_gateway
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_llm_gateway | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — LLM Gateway
Blueprint: docs/03_modules/infrastructure_runtime_integration/agent-spec/blueprint.md
Author: factory-agent
Version: 0.2.0

v0.2.0: 接入真实 LLM API（OpenAI-compatible / Anthropic SDK）
  - 支持 DeepSeek / GLM(Zhipu) / Claude / OpenAI 四个 provider
  - base_url 从环境变量读取，无硬编码密钥
  - 降级链：provider 不可用时 fallback 到下一个
  - LSG 安全：输入/输出经 sanitizer 过滤
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass
from typing import Any
from zephyr.shared.utils.async_utils import run_sync  # 5.12.8 修复：统一 async/sync 边界
from zephyr.shared.security.secrets import get_secret_or_default

logger = logging.getLogger(__name__)

_lsg_gateway = None


def _get_lsg_gateway():
    global _lsg_gateway
    if _lsg_gateway is not None:
        return _lsg_gateway
    try:
        import importlib

        _lsg_gateway = importlib.import_module("zephyr.security.llm_defense.llm_security.gateway").LSGSecurityGateway()
        return _lsg_gateway
    except ImportError:
        logger.debug("LSG not available, skipping security scan")
        return None
    except Exception:
        logger.warning("LSG init failed, security scans disabled", exc_info=True)
        return None


def _lsg_scan_input_sync(text: str, metadata: dict[str, Any] | None = None) -> str | None:
    gw = _get_lsg_gateway()
    if gw is None:
        return None
    try:
        import importlib

        SecurityDecision = importlib.import_module(
            "zephyr.shared.contracts.security.security_decision"
        ).SecurityDecision
        result = run_sync(gw.scan_input(text, source="llm_gateway", metadata=metadata or {}))
        if result.decision in (SecurityDecision.DENY, SecurityDecision.BLOCK):
            return result.blocked_by or "lsg_input_scan"
    except Exception:
        # 5.16.9 修复：移除废弃的 get_event_loop fallback，run_sync 已处理所有场景
        pass
    return None


def _lsg_scan_output_sync(text: str, metadata: dict[str, Any] | None = None) -> tuple[str, str | None]:
    gw = _get_lsg_gateway()
    if gw is None:
        return text, None
    try:
        import importlib

        SecurityDecision = importlib.import_module(
            "zephyr.shared.contracts.security.security_decision"
        ).SecurityDecision
        result = run_sync(gw.scan_output(text, source="llm_gateway", metadata=metadata or {}))
        if result.decision in (SecurityDecision.DENY, SecurityDecision.BLOCK):
            return "[BLOCKED BY LSG]", result.blocked_by or "lsg_output_scan"
        if result.sanitized_output:
            return result.sanitized_output, None
    except Exception:
        # 5.16.9 修复：移除废弃的 get_event_loop fallback，run_sync 已处理所有场景
        pass
    return text, None


@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str
    tokens_input: int = 0
    tokens_output: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0
    simulated: bool = False
    error: str | None = None


@dataclass
class ProviderConfig:
    base_url: str
    default_model: str
    api_key_env: str
    fallback: str | None = None
    max_context_tokens: int = 128_000
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0


_PROVIDERS: dict[str, ProviderConfig] = {
    "deepseek": ProviderConfig(
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
        default_model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        api_key_env="DEEPSEEK_API_KEY",
        fallback="glm",
        max_context_tokens=128_000,
        cost_per_1k_input=0.001,
        cost_per_1k_output=0.002,
    ),
    "glm": ProviderConfig(
        base_url=os.getenv("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"),
        default_model=os.getenv("GLM_MODEL", "glm-4-flash"),
        api_key_env="GLM_API_KEY",
        fallback="deepseek",
        max_context_tokens=128_000,
        cost_per_1k_input=0.001,
        cost_per_1k_output=0.001,
    ),
    "claude": ProviderConfig(
        base_url=os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com"),
        default_model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
        api_key_env="ANTHROPIC_API_KEY",
        fallback=None,
        max_context_tokens=200_000,
        cost_per_1k_input=0.020,
        cost_per_1k_output=0.080,
    ),
    "openai": ProviderConfig(
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        default_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        api_key_env="OPENAI_API_KEY",
        fallback=None,
        max_context_tokens=128_000,
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
    ),
}


def _call_openai_compatible(
    provider: str,
    config: ProviderConfig,
    messages: list[dict[str, str]],
    model: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 4096,
) -> LLMResponse:
    api_key = get_secret_or_default(config.api_key_env, "")
    if not api_key:
        return LLMResponse(
            content="",
            model=model or config.default_model,
            provider=provider,
            simulated=True,
            error=f"API key not set: {config.api_key_env}",
        )

    try:
        from openai import OpenAI
    except ImportError:
        return LLMResponse(
            content="",
            model=model or config.default_model,
            provider=provider,
            simulated=True,
            error="openai package not installed — pip install openai",
        )

    resolved_model = model or config.default_model
    start = time.monotonic()

    try:
        client = OpenAI(base_url=config.base_url, api_key=api_key)
        response = client.chat.completions.create(
            model=resolved_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        latency_ms = int((time.monotonic() - start) * 1000)

        content = response.choices[0].message.content or ""
        tokens_input = getattr(response.usage, "prompt_tokens", 0) or 0
        tokens_output = getattr(response.usage, "completion_tokens", 0) or 0
        cost_usd = round(
            (tokens_input / 1000.0) * config.cost_per_1k_input + (tokens_output / 1000.0) * config.cost_per_1k_output,
            6,
        )

        return LLMResponse(
            content=content,
            model=resolved_model,
            provider=provider,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            simulated=False,
        )
    except Exception as exc:
        latency_ms = int((time.monotonic() - start) * 1000)
        logger.warning("LLMGateway _call_openai_compatible(%s) failed: %s", provider, exc, exc_info=True)
        return LLMResponse(
            content="",
            model=resolved_model,
            provider=provider,
            latency_ms=latency_ms,
            simulated=True,
            error="internal error",
        )


def _call_anthropic(
    config: ProviderConfig,
    messages: list[dict[str, str]],
    model: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 4096,
) -> LLMResponse:
    api_key = get_secret_or_default(config.api_key_env, "")
    if not api_key:
        return LLMResponse(
            content="",
            model=model or config.default_model,
            provider="claude",
            simulated=True,
            error=f"API key not set: {config.api_key_env}",
        )

    try:
        import anthropic
    except ImportError:
        return LLMResponse(
            content="",
            model=model or config.default_model,
            provider="claude",
            simulated=True,
            error="anthropic package not installed — pip install anthropic",
        )

    resolved_model = model or config.default_model
    start = time.monotonic()

    system_msg = ""
    user_messages: list[dict[str, str]] = []
    for m in messages:
        if m["role"] == "system":
            system_msg = m["content"]
        else:
            user_messages.append(m)

    try:
        client = anthropic.Anthropic(api_key=api_key)
        kwargs: dict[str, Any] = {
            "model": resolved_model,
            "messages": user_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if system_msg:
            kwargs["system"] = system_msg

        response = client.messages.create(**kwargs)
        latency_ms = int((time.monotonic() - start) * 1000)

        content = response.content[0].text if response.content else ""
        tokens_input = getattr(response.usage, "input_tokens", 0) or 0
        tokens_output = getattr(response.usage, "output_tokens", 0) or 0
        cost_usd = round(
            (tokens_input / 1000.0) * config.cost_per_1k_input + (tokens_output / 1000.0) * config.cost_per_1k_output,
            6,
        )

        return LLMResponse(
            content=content,
            model=resolved_model,
            provider="claude",
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            simulated=False,
        )
    except Exception as exc:
        latency_ms = int((time.monotonic() - start) * 1000)
        logger.warning("LLMGateway _call_anthropic failed: %s", exc, exc_info=True)
        return LLMResponse(
            content="",
            model=resolved_model,
            provider="claude",
            latency_ms=latency_ms,
            simulated=True,
            error="internal error",
        )


class LLMGateway:
    """LLM 网关——多模型智能路由 + 降级链 + 真实 API 调用

    __implements__: zephyr.shared.contracts.llm_gateway_protocol.LLMGatewayProtocol
    """

    __implements__: str = "zephyr.shared.contracts.llm_gateway_protocol.LLMGatewayProtocol"

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
        user_text = " ".join(m.get("content", "") for m in messages if m.get("role") != "system")
        blocked_by = _lsg_scan_input_sync(user_text, {"provider": provider, "model": model})
        if blocked_by:
            logger.warning("LLMGateway input blocked by LSG layer: %s", blocked_by)
            return LLMResponse(
                content="",
                model=model or "unknown",
                provider=provider,
                simulated=True,
                error=f"Input blocked by LSG: {blocked_by}",
            )

        chain = fallback_chain or cls._build_fallback_chain(provider)
        for prov in chain:
            config = _PROVIDERS.get(prov)
            if config is None:
                continue
            if prov == "claude":
                resp = _call_anthropic(config, messages, model, temperature, max_tokens)
            else:
                resp = _call_openai_compatible(prov, config, messages, model, temperature, max_tokens)
            if not resp.simulated:
                safe_content, output_blocked = _lsg_scan_output_sync(
                    resp.content, {"provider": prov, "model": resp.model}
                )
                if output_blocked:
                    logger.warning("LLMGateway output blocked by LSG layer: %s", output_blocked)
                    return LLMResponse(
                        content="[BLOCKED BY LSG]",
                        model=resp.model,
                        provider=resp.provider,
                        tokens_input=resp.tokens_input,
                        tokens_output=resp.tokens_output,
                        cost_usd=resp.cost_usd,
                        latency_ms=resp.latency_ms,
                        simulated=True,
                        error=f"Output blocked by LSG: {output_blocked}",
                    )
                resp.content = safe_content
                return resp
            # 5.53.2 修复：Provider 降级是异常路径，原用 INFO 难以从海量日志定位失败。
            # 改为 WARNING。
            logger.warning("LLMGateway provider=%s failed, trying next in chain", prov)
        return LLMResponse(
            content="",
            model=model or "unknown",
            provider=provider,
            simulated=True,
            error="all providers in fallback chain failed",
        )

    @classmethod
    def _build_fallback_chain(cls, primary: str) -> list[str]:
        chain = [primary]
        config = _PROVIDERS.get(primary)
        if config and config.fallback:
            chain.append(config.fallback)
        if "claude" not in chain:
            chain.append("claude")
        return chain

    @classmethod
    def route(cls, skill_id: str, model_hint: str | None = None) -> dict[str, Any]:
        provider = model_hint or "deepseek"
        config = _PROVIDERS.get(provider, _PROVIDERS["deepseek"])
        return {
            "skill_id": skill_id,
            "provider": provider,
            "model": config.default_model,
            "base_url": config.base_url,
            "max_context_tokens": config.max_context_tokens,
        }

    @classmethod
    def list_providers(cls) -> list[str]:
        return list(_PROVIDERS.keys())

    @classmethod
    def get_provider_config(cls, provider: str) -> ProviderConfig | None:
        return _PROVIDERS.get(provider)