# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.resilience.fallback
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] compliance.audit_orchestrator.feedback_bridge
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_fallback | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
fallback.py —— 降级策略模式（Phase 2 新增 | 零依赖）

设计原则：
  - 策略链：按序尝试 fallback 函数，全部失败才报错
  - 异常感知：每个 fallback 独立捕获异常，不影响链上后续策略
  - AI 可见：每个策略有 name + description，日志记录降级路径

常见场景：
  - 主 API 超时 → 降级到缓存 → 缓存空 → 返回默认值
  - LLM 模型不可用 → 降级到更便宜模型 → 最后返回预置模板
  - 数据库查询失败 → 降级到本地 JSON → 返回空结果

AI 施工约定：
  - 核心业务流程（LLM 调用 / DB 查询 / API 请求）MUST 配置降级链
  - 禁止裸 try/except 后返回 None——必须显式声明降级链
  - 降级链路日志 WARNING 级别，方便运维监控

SSoT: MOD-INF-016 §2.6 shared-resilience
Version: 0.1.0
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, ParamSpec, TypeVar

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "FallbackChain",
    "FallbackExhaustedError",
    "FallbackStep",
    "fallback",
]

logger = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


class FallbackExhaustedError(ZephyrBaseError):
    """降级链全部耗尽——所有步骤都失败了。"""
    error_code = "ZA-SH-0019"


@dataclass(frozen=True)
class FallbackStep(Generic[P, R]):
    name: str
    func: Callable[P, R]
    description: str = ""
    is_primary: bool = False


class FallbackChain(Generic[P, R]):
    """降级策略链。

    Usage::

        chain = FallbackChain("llm_call", [
            FallbackStep("gpt4o", call_gpt4o, "主模型", is_primary=True),
            FallbackStep("gpt4o_mini", call_gpt4o_mini, "便宜备选"),
            FallbackStep("template", lambda p: DEFAULT_TEMPLATE, "预置模板兜底"),
        ])
        result = chain.execute(prompt="帮我写代码")
    """

    def __init__(
        self,
        chain_name: str,
        steps: list[FallbackStep[P, R]],
    ) -> None:
        if not steps:
            raise ValueError("FallbackChain requires at least one step")
        self._chain_name: str = chain_name
        self._steps: list[FallbackStep[P, R]] = list(steps)

    @property
    def chain_name(self) -> str:
        return self._chain_name

    @property
    def step_count(self) -> int:
        return len(self._steps)

    def execute(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """同步执行降级链。"""
        last_errors: list[tuple[str, str]] = []

        for step in self._steps:
            try:
                result = step.func(*args, **kwargs)
                if step.is_primary:
                    logger.debug("fallback chain '%s': primary step '%s' OK", self._chain_name, step.name)
                else:
                    logger.warning(
                        "fallback chain '%s': degraded to step '%s' (previous errors: %s)",
                        self._chain_name,
                        step.name,
                        [e[1] for e in last_errors],
                    )
                return result
            except Exception as exc:
                last_errors.append((step.name, str(exc)))
                logger.warning(
                    "fallback chain '%s': step '%s' failed: %s",
                    self._chain_name,
                    step.name,
                    exc, exc_info=True
                )

        raise FallbackExhaustedError(
            f"FallbackChain '{self._chain_name}' exhausted all {len(self._steps)} steps",
            details={
                "chain_name": self._chain_name,
                "step_count": len(self._steps),
                "errors": dict(last_errors),
            },
        )

    async def execute_async(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """异步执行降级链。"""
        last_errors: list[tuple[str, str]] = []

        for step in self._steps:
            try:
                result = await step.func(*args, **kwargs)
                if step.is_primary:
                    logger.debug("fallback chain '%s': primary step '%s' OK", self._chain_name, step.name)
                else:
                    logger.warning(
                        "fallback chain '%s': degraded to step '%s' (previous errors: %s)",
                        self._chain_name,
                        step.name,
                        [e[1] for e in last_errors],
                    )
                return result
            except Exception as exc:
                last_errors.append((step.name, str(exc)))
                logger.warning(
                    "fallback chain '%s': step '%s' failed: %s",
                    self._chain_name,
                    step.name,
                    exc, exc_info=True
                )

        raise FallbackExhaustedError(
            f"FallbackChain '{self._chain_name}' exhausted all {len(self._steps)} steps",
            details={
                "chain_name": self._chain_name,
                "step_count": len(self._steps),
                "errors": dict(last_errors),
            },
        )


def fallback(
    *fallback_funcs: Callable[P, R],
    chain_name: str = "anonymous",
) -> Callable[P, R]:
    """装饰器形式降级链——简洁 API。

    Example::

        @fallback(call_primary_api, call_backup_api, call_default)
        def get_data(query: str) -> dict: ...

    Args:
        *fallback_funcs: 降级函数序列（按优先级从高到低）。
        chain_name: 链路名称（日志标识用）。
    """
    if not fallback_funcs:
        raise ValueError("fallback requires at least one function")

    steps = [
        FallbackStep(
            name=func.__qualname__,
            func=func,
            description=func.__doc__ or "",
            is_primary=(i == 0),
        )
        for i, func in enumerate(fallback_funcs)
    ]
    chain = FallbackChain(chain_name, steps)

    return chain.execute
