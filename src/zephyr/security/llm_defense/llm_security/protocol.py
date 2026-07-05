# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] zephyr.security.llm_defense.llm_security.protocol
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.shared.contracts.security.security_decision
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SEC_protocol | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from zephyr.shared.contracts.security.security_decision import SecurityDecision


@dataclass
class SecurityContext:
    request_id: str
    layer_name: str
    raw_input: str
    metadata: dict[str, Any] = field(default_factory=dict)
    traces: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class SecurityResult:
    decision: SecurityDecision
    reason: str
    layer_name: str
    score: float = 1.0
    details: dict[str, Any] = field(default_factory=dict)


class LLMSecurityProtocol(ABC):
    """LLM Security Gateway 九层防御统一接口契约（L0-L8）。

    所有 LSG 防御层 MUST 继承本协议并实现 evaluate()。
    原则：fail-closed — 层不可用 → 返回 DENY，禁止 bypass。
    """

    DEFAULT_BLOCK: bool = True
    UNCERTAINTY_THRESHOLD: float = 0.5

    @classmethod
    def fail_closed_default(cls) -> SecurityDecision:
        """返回 LSG 默认安全决策——fail-closed = BLOCK."""
        return SecurityDecision.BLOCK

    @classmethod
    def is_uncertain(cls, score: float) -> bool:
        """当安全分数低于不确定性阈值时视为不确定."""
        return score < cls.UNCERTAINTY_THRESHOLD

    @abstractmethod
    async def evaluate(self, ctx: SecurityContext) -> SecurityResult:
        """对单次 LLM 交互执行安全评估。

        Args:
            ctx: 安全上下文，包含原始输入和请求元数据。

        Returns:
            SecurityResult: 决策+原因+分数。
        """
        ...

    @abstractmethod
    def layer_name(self) -> str:
        """返回本层的唯一名称，如 'l1_input'、'l3_output'。

        Returns:
            str: 层名称标识符。
        """
        ...

    @abstractmethod
    def layer_index(self) -> int:
        """返回本层在九层防御中的序号（0-8）。

        Returns:
            int: 层索引，L0=0, L1=1, ..., L8=8。
        """
        ...

    async def pre_check(self, ctx: SecurityContext) -> SecurityResult | None:
        """可选前置检查钩子。返回非 None 值将短路 evaluate()。

        Args:
            ctx: 安全上下文。

        Returns:
            Optional[SecurityResult]: 若需短路则返回结果，否则 None。
        """
        return None

    async def post_check(self, ctx: SecurityContext, result: SecurityResult) -> SecurityResult:
        """可选后置检查钩子。可修改/增强 evaluate() 的返回结果。

        Args:
            ctx: 安全上下文。
            result: evaluate() 的原始返回值。

        Returns:
            SecurityResult: 可能修改后的结果。
        """
        return result
