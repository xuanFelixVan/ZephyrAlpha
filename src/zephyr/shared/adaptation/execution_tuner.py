# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.adaptation.execution_tuner
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-INF_execution_tuner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Execution Tuner — 执行调谐器（token/timeout 自适应）。

依据：
    蓝图 MOD-TASK_SYSTEM §6.7.2 + v0.6.0
    任务卡 TASK-INF-0127
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class TuningParams:
    max_tokens: int = 20000
    timeout_minutes: int = 60
    model: str = "deepseek"
    pipeline: str = "A"


@dataclass
class ExecutionProfile:
    task_id: str
    priority: str
    estimated_tokens: int
    timeout_minutes: int
    adjusted_tokens: int
    adjusted_timeout: int
    model: str


class ExecutionTuner:
    PRIORITY_MULTIPLIER: dict[str, float] = {
        "P0": 1.5,
        "P1": 1.2,
        "P2": 1.0,
    }

    def __init__(self) -> None:
        self._history: list[dict[str, Any]] = []
        self._default_params = TuningParams()

    def tune(self, task_card: dict[str, Any]) -> ExecutionProfile:
        task_id = task_card.get("task_id", "")
        priority = task_card.get("priority", "P2")
        estimated = task_card.get("estimated_tokens", self._default_params.max_tokens)
        timeout = task_card.get("timeout_minutes", self._default_params.timeout_minutes)

        multiplier = self.PRIORITY_MULTIPLIER.get(priority, 1.0)

        adjusted_tokens = int(estimated * multiplier)
        adjusted_timeout = int(timeout * multiplier)

        adjusted_tokens = min(adjusted_tokens, self._default_params.max_tokens * 2)
        adjusted_timeout = min(adjusted_timeout, self._default_params.timeout_minutes * 3)

        profile = ExecutionProfile(
            task_id=task_id,
            priority=priority,
            estimated_tokens=estimated,
            timeout_minutes=timeout,
            adjusted_tokens=adjusted_tokens,
            adjusted_timeout=adjusted_timeout,
            model=task_card.get("assigned_model", self._default_params.model),
        )

        self._history.append(
            {
                "task_id": task_id,
                "priority": priority,
                "original_tokens": estimated,
                "adjusted_tokens": adjusted_tokens,
            }
        )

        return profile

    def recommend_model(self, task_card: dict[str, Any]) -> str:
        estimated = task_card.get("estimated_tokens", 0)
        priority = task_card.get("priority", "P2")

        if priority == "P0" and estimated > 10000:
            return "gpt-4"
        if priority == "P0":
            return "gpt-3.5-turbo"

        return "deepseek"

    def get_average_adjustment(self) -> float:
        if not self._history:
            return 1.0
        ratios = [h["adjusted_tokens"] / max(h["original_tokens"], 1) for h in self._history]
        return sum(ratios) / len(ratios)
