# [BLUEPRINT] SRC-194 | docs/03_modules/_cross_layer/database/blueprint.md | §conductor
# [MODULE] zephyr.trading.conductor
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.shared.models; zephyr.trading.__init__; zephyr.shared.contracts.task_repository_protocol; zephyr.governance.persistence.task_repo
# [CONSUMERS] AI session conductor loop (replaces manual AutoPilot.run_cycle + serial execution)
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] plan_cycle() MUST detect file conflicts before grouping; _group_by_conflict MUST guarantee no two tasks in same group share files_in_scope/allowed_touch
# [MODIFY-GUARD] conflict detection uses files_in_scope + allowed_touch — adding new conflict dimensions requires updating _get_task_files
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] plan_cycle returns empty list when no tasks available; mark_completed/mark_failed propagate transition errors
# [TESTS] tests/test_conductor.py
# [A_module] module_id=MOD-ORC_conductor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Conductor — AI session 全自动指挥官。

职责：
- plan_cycle: 认领任务 + 文件冲突检测 + 并行分组
- mark_completed / mark_failed: 任务状态转换 + 依赖级联
- is_done: 判断是否还有可做任务
- status_report: 全局状态报告

不执行任务 —— 执行是 AI session / sub-agent 的事。
Conductor 只负责"找活 + 认领 + 分组"，AI 拿到分组后并行派发。
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zephyr.governance.persistence.task_repo import TaskRepository
    from zephyr.shared.foundation.models import TaskCard
    from zephyr.trading.autopilot import AutoPilot

logger = logging.getLogger(__name__)

__all__ = ["Conductor"]


class Conductor:
    """全自动指挥官 —— 认领 + 冲突检测 + 并行分组 + 状态管理。"""

    def __init__(
        self,
        session_id: str,
        db_path: str | Path | None = None,
        max_parallel: int = 3,
    ) -> None:
        self.session_id = session_id
        self._db_path = db_path
        self._max_parallel = max_parallel
        self._autopilot = None
        self._repo = None

    @property
    def autopilot(self) -> AutoPilot:
        from zephyr.trading.autopilot import AutoPilot

        if self._autopilot is None:
            self._autopilot = AutoPilot(self.session_id, self._db_path)
        return self._autopilot

    @property
    def repo(self) -> TaskRepository:
        if self._repo is None:
            from zephyr.governance.persistence.task_repo import TaskRepository

            self._repo = TaskRepository(self._db_path, enable_gate=False)
        return self._repo

    def plan_cycle(self, max_tasks: int = 10) -> list[list[TaskCard]]:
        """认领任务 + 冲突检测 + 返回并行执行分组。

        流程:
            1. recover_stale_claims() — 回收超时任务
            2. AutoPilot.run_cycle() — 认领 READY 任务
            3. _detect_file_conflicts() — 检测 files_in_scope / allowed_touch 交集
            4. _group_by_conflict() — 贪心着色分组，无冲突同组可并行
            5. 截断每组不超过 max_parallel

        Returns:
            [[TaskCard, ...], ...] — 组内无冲突可并行，组间有冲突需串行。
            空列表 = 无可做任务。
        """
        try:
            rows = self.repo._conn.execute(
                "SELECT DISTINCT COALESCE(batch_id, '') FROM tasks WHERE status='IN_PROGRESS' AND is_deleted=0"
            ).fetchall()
            for row in rows:
                bid = row[0] if row[0] else "__no_batch__"
                if bid != "__no_batch__":
                    self.repo.recover_stale_claims(bid)
        except Exception as exc:
            logger.warning("Conductor: recover_stale_claims failed: %s", exc, exc_info=True)

        claimed = self.autopilot.run_cycle(max_tasks=max_tasks)
        if not claimed:
            logger.info("Conductor: 无可认领任务")
            return []

        logger.info("Conductor: 认领到 %d 个任务", len(claimed))

        conflict_map = self._detect_file_conflicts(claimed)
        groups = self._group_by_conflict(claimed, conflict_map)

        for i, group in enumerate(groups):
            task_ids = [t.task_id for t in group]
            logger.info("Conductor: 执行组 %d — %s", i, task_ids)

        return groups

    def mark_completed(self, task_id: str, note: str | None = None) -> None:
        """标记任务 COMPLETED + 触发依赖级联解锁。"""
        self.repo.transition(task_id, "COMPLETED", session_id=self.session_id, note=note)
        logger.info("Conductor: %s -> COMPLETED", task_id)

    def mark_failed(self, task_id: str, note: str) -> None:
        """标记任务 FAILED。note 必须包含根因分析。"""
        self.repo.transition(task_id, "FAILED", session_id=self.session_id, note=note)
        # 5.53.1 修复：任务失败是负向事件，原用 INFO 在海量日志中被淹没。改为 WARNING。
        logger.warning("Conductor: %s -> FAILED (note=%s)", task_id, note)

    def is_done(self) -> bool:
        """检查是否还有可做的任务（READY 或 IN_PROGRESS）。"""
        counts = self.repo.count_by_status()
        ready = counts.get("READY", 0)
        in_progress = counts.get("IN_PROGRESS", 0)
        return ready == 0 and in_progress == 0

    def status_report(self) -> str:
        """全局状态报告（委托 AutoPilot + 追加 Conductor 信息）。"""
        base = self.autopilot.status_report()
        counts = self.repo.count_by_status()
        ready = counts.get("READY", 0)
        in_progress = counts.get("IN_PROGRESS", 0)
        conductor_info = [
            "",
            f"  Conductor: session={self.session_id}",
            f"  Conductor: max_parallel={self._max_parallel}",
            f"  Conductor: is_done={self.is_done()}",
            f"  Conductor: remaining={ready + in_progress}",
        ]
        return base + "\n".join(conductor_info)

    def _get_task_files(self, task: TaskCard) -> set[str]:
        """提取任务涉及的所有文件路径（files_in_scope + allowed_touch）。"""
        files: set[str] = set()

        fis = getattr(task, "files_in_scope", None) or []
        if isinstance(fis, str):
            try:
                fis = json.loads(fis)
            except (json.JSONDecodeError, TypeError):
                fis = [fis] if fis else []
            # 5.48.2 修复：json.loads 后添加类型校验
            if not isinstance(fis, list):
                fis = []
        files.update(str(f) for f in fis)

        at = getattr(task, "allowed_touch", None) or []
        if isinstance(at, str):
            try:
                at = json.loads(at)
            except (json.JSONDecodeError, TypeError):
                at = [at] if at else []
            # 5.48.2 修复：json.loads 后添加类型校验
            if not isinstance(at, list):
                at = []
        files.update(str(f) for f in at)

        do = getattr(task, "downstream_outputs", None) or []
        if isinstance(do, str):
            try:
                do = json.loads(do)
            except (json.JSONDecodeError, TypeError):
                do = []
            # 5.48.2 修复：json.loads 后添加类型校验
            if not isinstance(do, list):
                do = []
        for item in do:
            if isinstance(item, dict) and "path" in item:
                files.add(str(item["path"]))

        return files

    def _detect_file_conflicts(self, tasks: list[TaskCard]) -> dict[str, set[str]]:
        """检测任务间的文件冲突。

        Returns:
            {task_id: {conflicting_task_id, ...}} — 冲突邻接表。
        """
        task_files: dict[str, set[str]] = {}
        for t in tasks:
            task_files[t.task_id] = self._get_task_files(t)

        conflict_map: dict[str, set[str]] = {t.task_id: set() for t in tasks}

        for i, t1 in enumerate(tasks):
            for t2 in tasks[i + 1 :]:
                overlap = task_files[t1.task_id] & task_files[t2.task_id]
                if overlap:
                    conflict_map[t1.task_id].add(t2.task_id)
                    conflict_map[t2.task_id].add(t1.task_id)
                    logger.debug(
                        "Conductor: 冲突 %s ↔ %s (文件: %s)",
                        t1.task_id,
                        t2.task_id,
                        overlap,
                    )

        return conflict_map

    def _group_by_conflict(
        self,
        tasks: list[TaskCard],
        conflict_map: dict[str, set[str]],
    ) -> list[list[TaskCard]]:
        """贪心图着色分组：无冲突的任务分到同一组可并行执行。

        算法:
            1. 按优先级排序（高优先级先分配，确保其在最早组）
            2. 对每个任务，找第一个没有冲突的组加入
            3. 所有组都冲突则新建组

        每组截断到 max_parallel 个任务。
        """
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (
                t.priority.value if hasattr(t.priority, "value") else str(t.priority),
                t.created_at.isoformat() if t.created_at else "",
            ),
        )

        groups: list[list[TaskCard]] = []
        group_task_ids: list[set[str]] = []

        for task in sorted_tasks:
            placed = False
            for gi, gids in enumerate(group_task_ids):
                if not (conflict_map.get(task.task_id, set()) & gids):
                    groups[gi].append(task)
                    gids.add(task.task_id)
                    placed = True
                    break

            if not placed:
                groups.append([task])
                group_task_ids.append({task.task_id})

        for i, group in enumerate(groups):
            if len(group) > self._max_parallel:
                groups[i] = group[: self._max_parallel]
                overflow = group[self._max_parallel :]
                for t in overflow:
                    groups.append([t])
                    group_task_ids.append({t.task_id})

        return groups