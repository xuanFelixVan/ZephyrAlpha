# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.task_queue
# [DOMAIN] D_DATA
# [DEPENDENCIES] yaml(标准库); threading
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] DAG无环检测(有环则ValueError); 任务状态PENDING→RUNNING→SUCCESS/FAILED; 前置全SUCCESS才READY; 线程安全(threading.Lock)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] load_yaml解析失败→ValueError; get_ready_tasks无就绪任务返回空列表; mark_completed未知task_id→KeyError
# [TESTS] tests/zephyr/data/test_task_queue.py
# [A_module] module_id=MOD-L00-004-task_queue | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""任务依赖图 + 优先级队列（MOD-L00-004 §6.3 任务依赖图 + §6.4 并发控制）。

管理任务间的 DAG 依赖关系，决定哪些任务可以执行：
- 前置全部 SUCCESS → 当前任务 READY
- 前置有 FAILED → 当前任务 BLOCKED（不执行）
- 前置有 PENDING/RUNNING → 当前任务 PENDING（等待）

DAG 依赖示例（蓝图 §6.3）：
    adj_factor → kline_daily_hfq → kline_daily_none
    kline_daily → daily_valuation
    stock_list → (所有依赖标的列表的任务)

线程安全：所有状态操作用 threading.Lock 保护。
"""
from __future__ import annotations

from typing import Final
import logging
import threading
from collections import defaultdict
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

# 任务状态常量
PENDING: Final[str] = "PENDING"
RUNNING: Final[str] = "RUNNING"
SUCCESS: Final[str] = "SUCCESS"
FAILED: Final[str] = "FAILED"
BLOCKED: Final[str] = "BLOCKED"  # 前置失败，不可执行


# class-name-alias: MOD-L00-004 数据源集成器的 DAG 依赖图 + 优先级队列，与 infrastructure/queue/task_queue.py 的后台任务队列同名不同义，过渡期共存（阶段4退役旧版或重命名）
class TaskQueue:
    """任务依赖图 + 优先级队列。

    用法：
        q = TaskQueue()
        q.load_yaml("config/tasks.yaml")
        for task_id in q.get_ready_tasks():
            q.mark_running(task_id)
            # ... 执行任务 ...
            q.mark_completed(task_id)  # 或 q.mark_failed(task_id)
    """

    def __init__(self):
        self._tasks: dict[str, dict] = {}  # task_id → task_def
        self._status: dict[str, str] = {}  # task_id → status
        self._dependencies: dict[str, list[str]] = {}  # task_id → [dep_task_id, ...]
        self._lock = threading.Lock()

    def load_yaml(self, path: str | Path) -> None:
        """从 tasks.yaml 加载任务清单。

        Args:
            path: yaml 文件路径

        Raises:
            ValueError: yaml 解析失败或 DAG 有环
        """
        import yaml
        p = Path(path)
        with open(p, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        tasks = data.get("tasks", [])
        if not tasks:
            raise ValueError(f"tasks.yaml 无任务定义: {p}")
        with self._lock:
            self._tasks.clear()
            self._status.clear()
            self._dependencies.clear()
            for t in tasks:
                tid = t["task_id"]
                self._tasks[tid] = t
                self._status[tid] = PENDING
                self._dependencies[tid] = t.get("dependencies", [])
        # DAG 无环检测
        cycle = self._detect_cycle()
        if cycle:
            raise ValueError(f"任务依赖图有环: {' → '.join(cycle)}")

    def add_task(self, task_def: dict) -> None:
        """编程式添加任务（测试用）。"""
        with self._lock:
            tid = task_def["task_id"]
            self._tasks[tid] = task_def
            self._status[tid] = PENDING
            self._dependencies[tid] = task_def.get("dependencies", [])

    # ============== DAG 检测 ==============

    def _detect_cycle(self) -> list[str] | None:
        """DFS 检测 DAG 是否有环。有环返回环路径，无环返回 None。"""
        WHITE, GRAY, BLACK = 0, 1, 2
        color = defaultdict(lambda: WHITE)
        path: list[str] = []

        def dfs(node: str) -> list[str] | None:
            color[node] = GRAY
            path.append(node)
            for dep in self._dependencies.get(node, []):
                if dep not in self._tasks:
                    continue  # 未知依赖跳过
                if color[dep] == GRAY:
                    # 找到环
                    idx = path.index(dep)
                    return path[idx:] + [dep]
                if color[dep] == WHITE:
                    result = dfs(dep)
                    if result:
                        return result
            path.pop()
            color[node] = BLACK
            return None

        for tid in self._tasks:
            if color[tid] == WHITE:
                result = dfs(tid)
                if result:
                    return result
        return None

    # ============== 状态查询 ==============

    def get_ready_tasks(self) -> list[str]:
        """获取所有 READY 任务（前置全 SUCCESS，自身 PENDING）。

        Returns:
            就绪任务 task_id 列表（按 task_id 排序，保证确定性）
        """
        with self._lock:
            ready = []
            for tid, status in self._status.items():
                if status != PENDING:
                    continue
                deps = self._dependencies.get(tid, [])
                if not deps:
                    ready.append(tid)
                elif all(self._status.get(d) == SUCCESS for d in deps):
                    ready.append(tid)
                elif any(self._status.get(d) == FAILED for d in deps):
                    # 前置有失败 → 标记 BLOCKED
                    self._status[tid] = BLOCKED
            return sorted(ready)

    def get_task(self, task_id: str) -> dict | None:
        """查任务定义。"""
        with self._lock:
            return self._tasks.get(task_id)

    def get_status(self, task_id: str) -> str | None:
        """查任务状态。"""
        with self._lock:
            return self._status.get(task_id)

    def list_all(self) -> list[dict]:
        """列出所有任务（含状态）。"""
        with self._lock:
            result = []
            for tid, tdef in self._tasks.items():
                item = dict(tdef)
                item["status"] = self._status.get(tid, PENDING)
                result.append(item)
            return result

    def list_by_status(self, status: str) -> list[str]:
        """按状态过滤任务。"""
        with self._lock:
            return sorted(tid for tid, s in self._status.items() if s == status)

    # ============== 状态变更 ==============

    def mark_running(self, task_id: str) -> None:
        """标记任务为 RUNNING。"""
        with self._lock:
            if task_id not in self._tasks:
                raise KeyError("未知 task_id")
            self._status[task_id] = RUNNING

    def mark_completed(self, task_id: str) -> None:
        """标记任务为 SUCCESS。"""
        with self._lock:
            if task_id not in self._tasks:
                raise KeyError("未知 task_id")
            self._status[task_id] = SUCCESS

    def mark_failed(self, task_id: str) -> None:
        """标记任务为 FAILED。后续依赖此任务的任务会变 BLOCKED。"""
        with self._lock:
            if task_id not in self._tasks:
                raise KeyError("未知 task_id")
            self._status[task_id] = FAILED

    def reset(self, task_id: str | None = None) -> None:
        """重置任务状态为 PENDING。task_id=None 重置全部。"""
        with self._lock:
            if task_id:
                if task_id in self._status:
                    self._status[task_id] = PENDING
            else:
                for tid in self._status:
                    self._status[tid] = PENDING

    # ============== 完成检测 ==============

    def is_done(self) -> bool:
        """所有任务是否终态（SUCCESS/FAILED/BLOCKED）。"""
        with self._lock:
            terminal = {SUCCESS, FAILED, BLOCKED}
            return all(s in terminal for s in self._status.values())

    def has_failed(self) -> bool:
        """是否有失败任务。"""
        with self._lock:
            return any(s == FAILED for s in self._status.values())

    def summary(self) -> dict[str, int]:
        """状态汇总。"""
        with self._lock:
            counts: dict[str, int] = defaultdict(int)
            for s in self._status.values():
                counts[s] += 1
            return dict(counts)
