# [BLUEPRINT] MOD-ML-007 | docs/03_modules/_domain_machine_learning_train/blueprint.md
# [MODULE] zephyr.ml_train.meta_learning_evolution
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] 无（标准库）
# [CONSUMERS] MOD-ML-001 training_pipeline（超参先验推荐位）；MOD-ML-009 learning_effect_feedback（经验回写）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 经验只读复用（recommend 不改库）；上下文匹配=精确匹配声明键；推荐结果仅作训练先验，禁直接生效实盘（B-009）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无自定义异常——未知任务 recall 返回空表、summary 抛 ValueError
# [TESTS] tests/ml_train/test_meta_learning_evolution.py
# [A_module] module_id=MOD-ML-007 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""D_ML_TRAIN — MOD-ML-007 元学习演进（跨任务经验库，轻量）。

统一框架派路线（宪章 §3 约束二）的轻量载体：跨训练任务沉淀
``(任务, 上下文, 指标)`` 经验，新任务启动时按上下文匹配推荐历史最佳配置作
训练先验。纯内存/标准库实现，不引重依赖；推荐结果仅为候选先验，是否采纳
走人工/治理闸门（B-007/B-009）。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

_log = logging.getLogger(__name__)


@dataclass(frozen=True)
class TaskExperience:
    """单条跨任务经验。

    Attributes
    ----------
    task_id : 任务标识（如 density / limit_up / seat）。
    context : 任务上下文（regime/超参等键值对，推荐时按声明键精确匹配）。
    metrics : 该次任务产出指标（如 {"score": 0.8}）。
    """

    task_id: str
    context: dict[str, Any]
    metrics: dict[str, float]
    recorded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class MetaLearningStore:
    """跨任务经验库（MOD-ML-007）。"""

    def __init__(self) -> None:
        self._experiences: dict[str, list[TaskExperience]] = {}

    # ── 记录/回溯 ────────────────────────────────────────────────────

    def record(self, experience: TaskExperience) -> None:
        """登记一条任务经验。"""
        self._experiences.setdefault(experience.task_id, []).append(experience)
        _log.info("经验登记: %s metrics=%s", experience.task_id, experience.metrics)

    def recall(self, task_id: str) -> list[TaskExperience]:
        """按任务回溯全部经验（未知任务返回空表）。"""
        return list(self._experiences.get(task_id, []))

    # ── 推荐（只读复用） ─────────────────────────────────────────────

    def recommend(
        self,
        task_id: str,
        context: dict[str, Any],
        metric: str = "score",
    ) -> TaskExperience | None:
        """按上下文匹配推荐历史最佳经验（无匹配回退全局最佳）。

        上下文匹配语义：经验 context 在 ``context`` 声明的每个键上取值相等。
        """
        pool = self._experiences.get(task_id)
        if not pool:
            return None
        matched = [
            e for e in pool if all(e.context.get(k) == v for k, v in context.items())
        ]
        candidates = matched if matched else pool
        best = max(candidates, key=lambda e: e.metrics.get(metric, float("-inf")))
        _log.info("经验推荐: %s matched=%d best=%s", task_id, len(matched), best.metrics)
        return best

    # ── 演进摘要 ─────────────────────────────────────────────────────

    def evolution_summary(self, task_id: str, metric: str) -> dict[str, Any]:
        """任务演进摘要（经验数/最佳/最新/均值）。"""
        pool = self._experiences.get(task_id)
        if not pool:
            raise ValueError(f"任务 {task_id!r} 无经验沉淀")
        values = [e.metrics.get(metric, 0.0) for e in pool]
        return {
            "task_id": task_id,
            "n_experiences": len(pool),
            "best": max(values),
            "latest": values[-1],
            "mean": sum(values) / len(values),
        }


__all__ = [
    "MetaLearningStore",
    "TaskExperience",
]
