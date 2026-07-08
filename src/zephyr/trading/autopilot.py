# [BLUEPRINT] SRC-193 | docs/03_modules/_cross_layer/database/blueprint.md | §auto-pilot
# [MODULE] zephyr.trading.autopilot
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.shared.models; zephyr.shared.contracts.task_repository_protocol; zephyr.governance.persistence.task_repo
# [CONSUMERS] zephyr.trading.__init__; zephyr.trading.conductor
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] AutoPilot.run_cycle() MUST call claim_next() which uses Event Sourcing partial unique index for atomic claim; status_report() MUST reflect real DB state
# [MODIFY-GUARD] claim_next uses idx_te_one_claim_per_task — do NOT change claim semantics without updating the partial unique index
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] Returns None when no tasks available; logs warnings on DB connection issues
# [TESTS] tests/test_autopilot.py
# [A_module] module_id=MOD-ORC_autopilot | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""AutoPilot — AI session 自动找活干、认领任务。

职责边界：
- scan / status_report -> 只读，告诉 AI 当前有什么活
- claim_next -> 认领一个任务（Event Sourcing 原子争抢）
- run_cycle -> 扫描 + 逐 batch 认领，返回认领到的任务列表
- 不执行任务 —— 执行是 AI session 的事
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zephyr.shared.contracts.task_repository_protocol import TaskRepositoryProtocol
    from zephyr.shared.foundation.models import TaskCard

# 5.160.11 修复：TaskStatus字符串替换为Enum引用
from zephyr.shared.foundation.constants import TaskStatus

logger = logging.getLogger(__name__)

__all__ = ["AutoPilot"]


class AutoPilot:
    """自动驾驶 —— AI session 启动后自动扫描并认领待办任务。"""

    def __init__(self, session_id: str, db_path: str | Path | None = None) -> None:
        self.session_id = session_id
        self._db_path = db_path
        self._repo: TaskRepositoryProtocol | None = None

    @property
    def repo(self) -> TaskRepositoryProtocol:
        if self._repo is None:
            from zephyr.governance.persistence.task_repo import TaskRepository

            self._repo = TaskRepository(self._db_path, enable_gate=False)
        return self._repo

    def scan(self) -> dict[str, list[TaskCard]]:
        """扫描所有 READY 任务，按 batch_id 分组，每组内按优先级+创建时间排序。

        batch_id 是 tasks 表的内部列（_row_to_taskcard 会剥离），此处通过 SQL 直接查询。

        Returns:
            {batch_id: [TaskCard, ...]} —— 空字典表示无事可做
        """
        rows = self.repo._conn.execute(
            "SELECT task_id, COALESCE(batch_id, '__no_batch__') as bid FROM tasks WHERE status='READY' AND is_deleted=0"
        ).fetchall()
        task_batch_map: dict[str, str] = {r["task_id"]: r["bid"] for r in rows}

        tasks = self.repo.list_by_status(TaskStatus.READY)
        grouped: dict[str, list[TaskCard]] = {}
        for t in tasks:
            bid = task_batch_map.get(t.task_id, "__no_batch__")
            grouped.setdefault(bid, []).append(t)
        for batch_tasks in grouped.values():
            batch_tasks.sort(
                key=lambda t: (
                    t.priority.value if hasattr(t.priority, "value") else str(t.priority),
                    t.created_at.isoformat() if t.created_at else "",
                )
            )
        return grouped

    def status_report(self) -> str:
        """生成人类可读的全局状态报告。

        Returns:
            多行字符串，包含各状态任务数 + READY 任务详情
        """
        counts = self.repo.count_by_status()
        lines = [
            "=" * 50,
            f"  AutoPilot Status Report — {self.session_id}",
            "=" * 50,
            "",
            "  全局任务统计:",
        ]
        for st in [TaskStatus.READY, TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED, TaskStatus.WAITING, TaskStatus.PENDING, TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            cnt = counts.get(st, 0)
            marker = " <<<" if st == TaskStatus.READY and cnt > 0 else ""
            lines.append(f"    {st.value:14s}: {cnt:4d}{marker}")

        ready_tasks = self.repo.list_by_status(TaskStatus.READY)
        pending_tasks = self.repo.list_by_status(TaskStatus.PENDING)
        actionable = ready_tasks + pending_tasks
        if actionable:
            rows = self.repo._conn.execute(
                "SELECT task_id, COALESCE(batch_id, '-') as bid FROM tasks WHERE status='READY' AND is_deleted=0"
            ).fetchall()
            batch_map: dict[str, str] = {r["task_id"]: r["bid"] for r in rows}

            lines.append("")
            lines.append(f"  待办任务 ({len(actionable)} 个):")
            lines.append("  " + "-" * 46)
            for t in actionable[:20]:
                bid = batch_map.get(t.task_id, "-")
                lines.append(f"    [{t.priority}] {t.task_id} | batch={bid} | {t.title[:60]}")
            if len(actionable) > 20:
                lines.append(f"    ... 还有 {len(actionable) - 20} 个任务")
        else:
            lines.append("")
            lines.append("  >>> 没有待办任务，系统空闲 <<<")

        lines.append("")
        lines.append("=" * 50)
        return "\n".join(lines)

    def claim_next(self, batch_id: str) -> TaskCard | None:
        """认领 batch 中下一个最高优先级的 READY 任务。

        使用 Event Sourcing 部分唯一索引（idx_te_one_claim_per_task）实现无锁原子争抢。
        多个 AI session 并发调用时，每个任务只会被一个 session 认领。

        Returns:
            认领到的 TaskCard，或 None（该 batch 无可用任务）
        """
        return self.repo.claim_next(batch_id, self.session_id)

    def run_cycle(self, max_tasks: int = 5) -> list[TaskCard]:
        """自动驾驶主循环：扫描 -> 逐 batch 认领 -> 返回认领到的任务列表。

        策略：按 batch 遍历，每个 batch 最多认领 1 个任务，直到达到 max_tasks 或无任务可领。

        Args:
            max_tasks: 单次循环最多认领的任务数

        Returns:
            认领到的 TaskCard 列表（AI session 应逐一执行并 transition(COMPLETED)）
        """
        from datetime import UTC, datetime

        from zephyr.shared.event_bus import EventBusBackpressure

        bus = EventBusBackpressure()
        bus.emit(
            "pipeline_start",
            payload={
                "session_id": self.session_id,
                "task_count": max_tasks,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

        grouped = self.scan()
        if not grouped:
            logger.info("AutoPilot: 没有 READY 任务")
            return []

        claimed: list[TaskCard] = []
        batch_ids = sorted(bid for bid in grouped if bid != "__no_batch__")

        for bid in batch_ids:
            if len(claimed) >= max_tasks:
                break
            task = self.claim_next(bid)
            if task is not None:
                claimed.append(task)
                logger.info(f"AutoPilot: claimed {task.task_id} [{task.priority}] {task.title}")

        if not claimed:
            logger.info("AutoPilot: 扫描到 READY 任务但认领失败（可能被其他 session 抢先）")

        return claimed


# ── EventBusBackpressure 订阅 (DM-2507-H) ──────────────────────────────

_subscribed = False
_subscribed_lock = threading.Lock()


def subscribe_eventbus() -> None:
    """订阅 EventBusBackpressure 的 task_completed 事件。

    幂等：重复调用安全。Backpressure 总线不可用时静默跳过。
    供 boot_hooks 统一调用。

    说明: task_completed 事件到达时仅记录日志——
    AutoPilot 实例化需要 session_id，模块级无法获取实例，
    真正的 run_cycle 由 AI session 主动触发。
    """
    global _subscribed
    if _subscribed:
        return
    with _subscribed_lock:
        if _subscribed:
            return
        try:
            from zephyr.shared.event_bus import EventBusBackpressure

            bus = EventBusBackpressure()
            bus.subscribe("task_completed", _on_task_completed)
            _subscribed = True
            logger.info("AutoPilot: subscribed to task_completed event")
        except Exception as e:
            logger.warning("AutoPilot: subscribe_eventbus failed: %s", e, exc_info=True)


def _on_task_completed(payload: object) -> None:
    """task_completed 事件：任务完成信号。轻量handler——仅日志记录。

    payload 期望字段: {timestamp, source_function, severity, detail}
    真正的 run_cycle 由 AI session 主动触发（需 session_id 实例化 AutoPilot）。
    """
    try:
        data = payload if isinstance(payload, dict) else {}
        detail = data.get("detail", str(payload))
        source = data.get("source_function", "unknown")
        logger.info(
            "AutoPilot: task_completed event received "
            "(source=%s, detail=%s) — run_cycle deferred to AI session",
            source,
            detail,
        )
    except Exception as e:
        logger.error("AutoPilot: _on_task_completed failed: %s", e, exc_info=True)