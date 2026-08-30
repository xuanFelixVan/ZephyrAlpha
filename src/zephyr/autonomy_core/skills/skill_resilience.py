# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_resilience
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Resilience
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.3.0

Skill 韧性——重试/降级/熔断策略 with exponential backoff.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: skill_resilience.py
# 层: 算法
# - id: A1
#   name_zh: ① SkillResilience
#   name_en: SkillResilience
#   intro: Skill 韧性——重试/降级/熔断策略.
#   desc: Skill 韧性——重试/降级/熔断策略.；公共方法（定义序）: get_failure_count, get_last_failure_time, get_circuit_open, get_circuit_open…
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: SkillResilience
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any


class SkillResilience:
    """Skill 韧性——重试/降级/熔断策略."""

    MAX_RETRIES = 3
    BASE_DELAY_S = 1.0
    MAX_DELAY_S = 30.0

    _failure_count: dict[str, int] = {}
    failure_count: dict[str, int] = _failure_count  # public alias（Stage 4 公共化）
    _last_failure_time: dict[str, float] = {}
    _circuit_open: dict[str, bool] = {}
    _circuit_open_until: dict[str, float] = {}

    # ── Stage 4 公共化：类级别状态访问器 ──
    @classmethod
    def get_failure_count(cls) -> dict[str, int]:
        """Public accessor for failure count state (Stage 4)."""
        return cls._failure_count

    @classmethod
    def get_last_failure_time(cls) -> dict[str, float]:
        """Public accessor for last failure time state (Stage 4)."""
        return cls._last_failure_time

    @classmethod
    def get_circuit_open(cls) -> dict[str, bool]:
        """Public accessor for circuit open state (Stage 4)."""
        return cls._circuit_open

    @classmethod
    def get_circuit_open_until(cls) -> dict[str, float]:
        """Public accessor for circuit open until state (Stage 4)."""
        return cls._circuit_open_until

    @classmethod
    def should_retry(cls, skill_id: str) -> bool:
        if cls.is_circuit_open(skill_id):
            return False
        count = cls._failure_count.get(skill_id, 0)
        return count < cls.MAX_RETRIES

    @classmethod
    def record_failure(cls, skill_id: str) -> int:
        cls._failure_count[skill_id] = cls._failure_count.get(skill_id, 0) + 1
        cls._last_failure_time[skill_id] = time.time()
        count = cls._failure_count[skill_id]
        if count >= cls.MAX_RETRIES:
            cls._open_circuit(skill_id)
        return count

    @classmethod
    def record_success(cls, skill_id: str):
        cls._failure_count.pop(skill_id, None)
        cls._last_failure_time.pop(skill_id, None)
        cls._circuit_open.pop(skill_id, None)
        cls._circuit_open_until.pop(skill_id, None)

    @classmethod
    def retry_with_backoff(
        cls,
        skill_id: str,
        fn: Callable[[], Any],
        max_retries: int | None = None,
    ) -> tuple[Any, int]:
        max_r = max_retries or cls.MAX_RETRIES
        last_exc = None
        for attempt in range(max_r):
            try:
                result = fn()
                cls.record_success(skill_id)
                return result, attempt + 1
            except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
                last_exc = exc
                cls.record_failure(skill_id)
                delay = min(cls.BASE_DELAY_S * (2**attempt), cls.MAX_DELAY_S)
                if attempt < max_r - 1:
                    time.sleep(delay)
        raise last_exc or RuntimeError(f"Skill {skill_id}: all {max_r} retries exhausted")

    @classmethod
    def is_circuit_open(cls, skill_id: str) -> bool:
        if not cls._circuit_open.get(skill_id, False):
            return False
        open_until = cls._circuit_open_until.get(skill_id, 0)
        if time.time() > open_until:
            cls._circuit_open[skill_id] = False
            return False
        return True

    @classmethod
    def _open_circuit(cls, skill_id: str):
        cls._circuit_open[skill_id] = True
        cls._circuit_open_until[skill_id] = time.time() + 300.0

    @classmethod
    def reset(cls, skill_id: str | None = None):
        if skill_id:
            cls._failure_count.pop(skill_id, None)
            cls._last_failure_time.pop(skill_id, None)
            cls._circuit_open.pop(skill_id, None)
            cls._circuit_open_until.pop(skill_id, None)
        else:
            cls._failure_count.clear()
            cls._last_failure_time.clear()
            cls._circuit_open.clear()
            cls._circuit_open_until.clear()


__all__ = ["SkillResilience"]
