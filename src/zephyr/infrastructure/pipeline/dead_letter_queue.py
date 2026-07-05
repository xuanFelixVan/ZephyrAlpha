# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] zephyr.infrastructure.pipeline.dead_letter_queue
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__; zephyr.shared.events.dlq_bridge
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_dead_letter_queue | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
DeadLetterQueue — 死信队列
==========================
永久失败任务存储（B169）。

职责：
  - 检查并记录死信条目（全部模块失败时写入）
  - 排出并清空死信队列
  - 序列化/反序列化（save_state / load_state）

使用：
    from zephyr.infrastructure.pipeline.dead_letter_queue import DeadLetterQueue

    dlq = DeadLetterQueue()
    entry = dlq.enqueue(task_card, results, status, max_retries=3)
    for dead in dlq.drain():
        ...
"""

from __future__ import annotations

from zephyr.infrastructure.pipeline.models import DeadLetterEntry, ModuleResult, ModuleStatus, PipelineStatus


class DeadLetterQueue:
    """死信队列——B169 永久失败任务存储。"""

    def __init__(self) -> None:
        self._entries: list[DeadLetterEntry] = []

    def enqueue(
        self,
        task_card,
        results: list[ModuleResult],
        status: PipelineStatus,
        max_retries: int = 3,
    ) -> DeadLetterEntry | None:
        """检查并记录死信。仅在全部模块失败时写入。

        Args:
            task_card: 任务卡片（含 task_id）
            results: 模块执行结果列表
            status: 管线状态
            max_retries: 最大重试次数

        Returns:
            新写入的 DeadLetterEntry，不符合条件时返回 None
        """
        if status not in (PipelineStatus.FAILURE, PipelineStatus.CLAUDE_RESCUE):
            return None
        all_failed = all(r.status == ModuleStatus.FAILURE for r in results)
        if not all_failed:
            return None
        entry = DeadLetterEntry(
            task_id=task_card.task_id,
            failure_reason=f"All {len(results)} modules failed",
            retry_count=max_retries,
            last_error=results[0].errors[0] if results and results[0].errors else "unknown",
        )
        self._entries.append(entry)
        return entry

    def drain(self) -> list[DeadLetterEntry]:
        """排出并清空所有死信条目。"""
        entries = list(self._entries)
        self._entries.clear()
        return entries

    @property
    def entries(self) -> list[DeadLetterEntry]:
        """只读访问死信列表。"""
        return list(self._entries)

    @property
    def count(self) -> int:
        """死信数量。"""
        return len(self._entries)

    def save_state(self) -> list[dict]:
        """序列化为持久化字典列表。"""
        return [e.model_dump() for e in self._entries]

    def load_state(self, data: list[dict]) -> None:
        """从持久化数据反序列化。"""
        self._entries = [DeadLetterEntry(**d) for d in data]
