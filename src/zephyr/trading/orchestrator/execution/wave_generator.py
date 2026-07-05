# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.trading.orchestrator.execution.wave_generator
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.shared.utils.db_utils
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
# [A_module] module_id=MOD-ORC_wave_generator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
WaveGenerator — 根据 Task 依赖图生成执行 Wave（T-2-03）
======================================================
依据： Queue）

功能
----
1. generate_waves — 从 tasks 表读取依赖图，拓扑排序生成 Wave 列表
2. get_next_wave — 返回当前可执行的下一个 Wave
3. wave_status — 查询各 Wave 的完成状态

Wave 定义
---------
同一 Wave 内的任务无互相依赖，可并行执行。
Wave 编号从 0 开始，Wave 0 = 无前置依赖的任务。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from zephyr.shared.io.paths import DB_PATH
from zephyr.shared.utils.db_utils import get_db_connection

__all__ = [
    "Wave",
    "WaveGenerator",
    "WaveStatus",
]


@dataclass
class Wave:
    wave_id: int
    task_ids: list[str] = field(default_factory=list)


@dataclass
class WaveStatus:
    wave_id: int
    total: int = 0
    completed: int = 0
    in_progress: int = 0
    pending: int = 0
    blocked: int = 0
    other: int = 0


class WaveGenerator:
    """
    根据 Task 依赖图生成执行 Wave。

    拓扑排序算法：Kahn's algorithm，O(V+E)。
    """

    def __init__(self, db_path: Path | None = None) -> None:
        self._db_path = db_path or DB_PATH

    def generate_waves(self, phase: int | None = None) -> list[Wave]:
        """
        从 tasks 表读取依赖图，拓扑排序生成 Wave 列表。

        Parameters
        ----------
        phase : int, optional
            只考虑指定 Phase 的任务。None 表示全部。

        Returns
        -------
        list[Wave]
            按执行顺序排列的 Wave 列表。
        """
        conn = get_db_connection(self._db_path)
        try:
            if phase is not None:
                rows = conn.execute(
                    "SELECT task_id, depends_on FROM tasks WHERE phase = ?",
                    (phase,),
                ).fetchall()
            else:
                rows = conn.execute("SELECT task_id, depends_on FROM tasks").fetchall()
        finally:
            conn.close()

        task_ids: set[str] = set()
        deps_map: dict[str, set[str]] = {}

        for row in rows:
            tid = row["task_id"]
            task_ids.add(tid)
            deps_raw = row["depends_on"] or "[]"
            try:
                deps_list = json.loads(deps_raw) if isinstance(deps_raw, str) else deps_raw
            except (json.JSONDecodeError, TypeError):
                deps_list = []
            deps = {d for d in deps_list if d in task_ids or True}
            deps_map[tid] = deps

        waves: list[Wave] = []
        assigned: set[str] = set()
        wave_id = 0

        while len(assigned) < len(task_ids):
            ready: list[str] = []
            for tid in task_ids:
                if tid in assigned:
                    continue
                remaining_deps = deps_map.get(tid, set()) - assigned
                if not remaining_deps:
                    ready.append(tid)

            if not ready:
                remaining = task_ids - assigned
                if remaining:
                    waves.append(Wave(wave_id=wave_id, task_ids=sorted(remaining)))
                    assigned.update(remaining)
                break

            waves.append(Wave(wave_id=wave_id, task_ids=sorted(ready)))
            assigned.update(ready)
            wave_id += 1

        return waves

    def get_next_wave(self, phase: int | None = None) -> Wave | None:
        """返回当前可执行的下一个 Wave（第一个含非 COMPLETED/VERIFIED/CANCELLED 任务的 Wave）。"""
        terminal_statuses = {"COMPLETED", "VERIFIED", "CANCELLED"}
        waves = self.generate_waves(phase=phase)

        conn = get_db_connection(self._db_path)
        try:
            for wave in waves:
                has_actionable = False
                for tid in wave.task_ids:
                    row = conn.execute("SELECT status FROM tasks WHERE task_id = ?", (tid,)).fetchone()
                    if row and row["status"] not in terminal_statuses:
                        has_actionable = True
                        break
                if has_actionable:
                    return wave
        finally:
            conn.close()

        return None

    def wave_status(self, phase: int | None = None) -> list[WaveStatus]:
        """查询各 Wave 的完成状态。"""
        waves = self.generate_waves(phase=phase)
        result: list[WaveStatus] = []

        conn = get_db_connection(self._db_path)
        try:
            for wave in waves:
                ws = WaveStatus(wave_id=wave.wave_id, total=len(wave.task_ids))
                for tid in wave.task_ids:
                    row = conn.execute("SELECT status FROM tasks WHERE task_id = ?", (tid,)).fetchone()
                    if not row:
                        ws.other += 1
                        continue
                    status = row["status"]
                    if status in ("COMPLETED", "VERIFIED"):
                        ws.completed += 1
                    elif status == "IN_PROGRESS":
                        ws.in_progress += 1
                    elif status == "PENDING":
                        ws.pending += 1
                    elif status == "BLOCKED":
                        ws.blocked += 1
                    else:
                        ws.other += 1
                result.append(ws)
        finally:
            conn.close()

        return result
