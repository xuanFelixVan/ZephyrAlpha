# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_cross_model
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_skill_cross_model | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Cross-Model
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.2.0
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ModelProvider(str, Enum):
    DEEPSEEK = "DeepSeek"
    CLAUDE = "Claude"
    GPT = "GPT"
    GEMINI = "Gemini"
    QWEN = "Qwen"
    LLAMA = "Llama"
    MISTRAL = "Mistral"


@dataclass
class ModelCapability:
    provider: ModelProvider
    max_context_tokens: int
    supports_system_prompt: bool = True
    supports_function_calling: bool = False
    supports_streaming: bool = False
    supports_vision: bool = False
    prompt_format: str = "default"
    tag_style: str = "default"
    stop_tokens: list[str] = field(default_factory=list)


_MODEL_CAPABILITIES: dict[str, ModelCapability] = {
    "DeepSeek": ModelCapability(
        provider=ModelProvider.DEEPSEEK,
        max_context_tokens=131072,
        supports_function_calling=True,
        supports_streaming=True,
        prompt_format="openai",
        tag_style="openai",
        stop_tokens=["<|end▁of▁sentence|>"],
    ),
    "Claude": ModelCapability(
        provider=ModelProvider.CLAUDE,
        max_context_tokens=200000,
        supports_function_calling=True,
        supports_streaming=True,
        supports_vision=True,
        prompt_format="anthropic",
        tag_style="xml",
        stop_tokens=["\n\nHuman:", "\n\nAssistant:"],
    ),
    "GPT": ModelCapability(
        provider=ModelProvider.GPT,
        max_context_tokens=128000,
        supports_function_calling=True,
        supports_streaming=True,
        supports_vision=True,
        prompt_format="openai",
        tag_style="openai",
    ),
    "Gemini": ModelCapability(
        provider=ModelProvider.GEMINI,
        max_context_tokens=1048576,
        supports_function_calling=True,
        supports_streaming=True,
        supports_vision=True,
        prompt_format="google",
        tag_style="google",
    ),
    "Qwen": ModelCapability(
        provider=ModelProvider.QWEN,
        max_context_tokens=131072,
        supports_function_calling=True,
        supports_streaming=True,
        prompt_format="openai",
        tag_style="openai",
    ),
}


@dataclass
class CrossModelContext:
    system_prompt: str = ""
    user_content: str = ""
    tools: list[dict[str, Any]] = field(default_factory=list)
    history: list[dict[str, str]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class SkillCrossModel:
    def __init__(self, default_provider: str = "DeepSeek"):
        self._default_provider = default_provider
        self._fallback_chain: list[str] = []
        self._adapter_registry: dict[str, callable] = {}
        self._normalization_rules: dict[str, dict[str, str]] = {
            "role_mapping": {"system": "system", "user": "user", "assistant": "assistant"},
            "stop_phrase_mapping": {},
        }

    def get_capability(self, provider: str) -> ModelCapability | None:
        return _MODEL_CAPABILITIES.get(provider)

    def supports_feature(self, provider: str, feature: str) -> bool:
        cap = self.get_capability(provider)
        if cap is None:
            return False
        return getattr(cap, f"supports_{feature}", False)

    def set_fallback_chain(self, providers: list[str]) -> None:
        self._fallback_chain = [p for p in providers if p in _MODEL_CAPABILITIES]

    def resolve_provider(self, preferred: str | None = None) -> str:
        target = preferred or self._default_provider
        if target in _MODEL_CAPABILITIES:
            return target
        for fb in self._fallback_chain:
            if fb in _MODEL_CAPABILITIES:
                return fb
        return self._default_provider

    def adapt_messages(self, context: CrossModelContext, target_provider: str) -> dict[str, Any]:
        cap = self.get_capability(target_provider)
        if cap is None:
            return {"error": f"Unknown provider: {target_provider}"}

        messages: list[dict[str, Any]] = []

        if context.system_prompt:
            if cap.tag_style == "anthropic":
                messages.append({"role": "user", "content": f"<system>{context.system_prompt}</system>"})
            else:
                messages.append({"role": "system", "content": context.system_prompt})

        for h in context.history:
            role = self._normalization_rules["role_mapping"].get(h.get("role", ""), "user")
            messages.append({"role": role, "content": h.get("content", "")})

        if context.user_content:
            messages.append({"role": "user", "content": context.user_content})

        payload: dict[str, Any] = {
            "provider": target_provider,
            "format": cap.prompt_format,
            "messages": messages,
        }

        if context.tools:
            if cap.prompt_format == "anthropic":
                payload["tools"] = self._adapt_tools_anthropic(context.tools)
            else:
                payload["tools"] = context.tools

        return payload

    def _adapt_tools_anthropic(self, tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
        adapted = []
        for tool in tools:
            t = tool.copy()
            if "function" in t:
                t["name"] = t["function"].get("name", "")
                t["description"] = t["function"].get("description", "")
                t["input_schema"] = t["function"].get("parameters", {})
                del t["function"]
            adapted.append(t)
        return adapted

    def normalize_output(self, raw_output: str, provider: str) -> str:
        cap = self.get_capability(provider)
        if cap is None:
            return raw_output

        normalized = raw_output

        for stop in cap.stop_tokens:
            idx = normalized.find(stop)
            if idx != -1:
                normalized = normalized[:idx]

        if cap.tag_style == "xml":
            import re

            normalized = re.sub(r"</?system>", "", normalized)
            normalized = re.sub(r"</?function_calls>", "", normalized)
            normalized = re.sub(r"</?invoke>", "", normalized)

        return normalized.strip()

    def score_compatibility(self, skill_prompt: str, provider: str) -> dict[str, Any]:
        cap = self.get_capability(provider)
        if cap is None:
            return {"score": 0.0, "issues": [f"Unknown provider: {provider}"]}

        score = 1.0
        issues: list[str] = []

        estimated_tokens = len(skill_prompt) // 3
        if estimated_tokens > cap.max_context_tokens * 0.8:
            score -= 0.3
            issues.append(f"Prompt may exceed {provider} context window")

        if not cap.supports_system_prompt and "System:" in skill_prompt:
            score -= 0.1
            issues.append(f"{provider} does not support system prompts")

        return {"score": max(0.0, score), "provider": provider, "issues": issues}

    def adapt(self, skill_id: str, target_model: str) -> dict[str, Any]:
        compatible = target_model in _MODEL_CAPABILITIES
        cap = self.get_capability(target_model) if compatible else None
        return {
            "skill_id": skill_id,
            "target_model": target_model,
            "compatible": compatible,
            "max_context": cap.max_context_tokens if cap else 0,
            "features": {
                "function_calling": cap.supports_function_calling if cap else False,
                "streaming": cap.supports_streaming if cap else False,
                "vision": cap.supports_vision if cap else False,
            }
            if cap
            else {},
        }

    def list_providers(self) -> list[dict[str, Any]]:
        return [
            {
                "name": name,
                "max_context": cap.max_context_tokens,
                "format": cap.prompt_format,
                "features": {
                    "function_calling": cap.supports_function_calling,
                    "streaming": cap.supports_streaming,
                    "vision": cap.supports_vision,
                },
            }
            for name, cap in _MODEL_CAPABILITIES.items()
        ]
