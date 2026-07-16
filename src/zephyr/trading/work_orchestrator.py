# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.work_orchestrator
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.trading.__init__
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
# [A_module] module_id=MOD-ORC_work_orchestrator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

__all__ = [
    "WorkOrchestrator",
]

"""
WorkOrchestrator — 工作编排子系统
==================================
蓝图: ARC-0001 §4.3
借鉴: Airflow DAG + Temporal Workflow + K8s Job
"""

import threading
import uuid
from datetime import datetime
from pathlib import Path

import yaml

from zephyr.trading.capability_registry import CapabilityRegistry
from zephyr.trading.work_dag import WorkDAG, WorkItem
from zephyr.gov_enforcement.rule_enforcement.task_types import TaskStatus
from zephyr.shared.io.serialization import filter_dataclass_fields
from zephyr.shared.utils.time_utils import now_utc


class WorkOrchestrator:
    """工作编排子系统——决定什么工作、什么时候、用什么模型、什么顺序。"""

    def __init__(
        self,
        capability_registry: CapabilityRegistry,
        dag_dir: Path | None = None,
        max_parallel_l1: int = 1,
        max_parallel_l2: int = 3,
        max_parallel_l3: int = 2,
    ) -> None:
        self._registry = capability_registry
        self._dag_dir = dag_dir
        self._dags: dict[str, WorkDAG] = {}
        self._items: dict[str, WorkItem] = {}
        self._slots: dict[str, int] = {"trae": max_parallel_l1, "local": max_parallel_l2, "api": max_parallel_l3}
        self._slots_used: dict[str, int] = {"trae": 0, "local": 0, "api": 0}
        self._lock = threading.Lock()

    def register_dag(self, dag: WorkDAG) -> None:
        # 5.142.3 修复: _dags 访问统一用 self._lock 保护, 避免与 list_dags/load_dags 并发抛 RuntimeError
        with self._lock:
            self._dags[dag.dag_id] = dag

    def get_dag(self, dag_id: str) -> WorkDAG | None:
        # 5.85.4 修复: 返回深拷贝避免外部修改内部调度状态
        # 5.142.3 修复: _dags 读访问纳入 self._lock, 取出后再 model_copy (copy 在锁外避免长持锁)
        with self._lock:
            dag = self._dags.get(dag_id)
        return dag.model_copy(deep=True) if dag is not None else None

    def list_dags(self) -> list[WorkDAG]:
        # 5.85.4 修复: 返回深拷贝避免外部修改内部调度状态
        # 5.142.3 修复: _dags 迭代纳入 self._lock, 取出快照后再 model_copy
        with self._lock:
            snapshot = list(self._dags.values())
        return [d.model_copy(deep=True) for d in snapshot]

    def load_dags(self) -> int:
        if self._dag_dir is None or not self._dag_dir.exists():
            return 0
        count = 0
        for path in self._dag_dir.glob("*.yaml"):
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
                dag = WorkDAG(**filter_dataclass_fields(WorkDAG, data))
                # 5.142.3 修复: 写入 _dags 必须持锁
                with self._lock:
                    self._dags[dag.dag_id] = dag
                count += 1
            except Exception:
                continue
        return count

    def submit(self, work: WorkItem) -> str:
        if not work.item_id:
            work.item_id = f"WI-{uuid.uuid4().hex[:8]}"
        if not work.created_at:
            work.created_at = now_utc().isoformat()
        with self._lock:
            self._items[work.item_id] = work
            if not work.depends_on:
                work.status = TaskStatus.READY
        return work.item_id

    def submit_dag(self, dag_id: str, params: dict | None = None) -> str:
        # 5.142.3 修复: _dags 读访问纳入 self._lock, 取出 dag 后释放锁再 submit (避免与 submit 嵌套持锁)
        with self._lock:
            dag = self._dags.get(dag_id)
        if dag is None:
            return ""
        params = params or {}
        edge_map: dict[str, list[str]] = {}
        for edge in dag.edges:
            edge_map.setdefault(edge.to_node, []).append(edge.from_node)

        node_items: dict[str, str] = {}
        for node in dag.nodes:
            layer = node.layer_override or dag.default_layer
            priority = node.priority_override or dag.default_priority
            deps = [node_items[dep] for dep in edge_map.get(node.node_id, []) if dep in node_items]
            item = WorkItem(
                item_id=f"WI-{uuid.uuid4().hex[:8]}",
                dag_id=dag_id,
                node_id=node.node_id,
                capability_id=node.capability_id,
                work_type=node.work_type,
                params={**node.params, **params},
                layer=layer,
                priority=priority,
                depends_on=deps,
                status=TaskStatus.READY if not deps else TaskStatus.PENDING,
            )
            iid = self.submit(item)
            node_items[node.node_id] = iid
        return dag_id

    def schedule_next(self) -> list[WorkItem]:
        ready: list[WorkItem] = []
        with self._lock:
            for item in self._items.values():
                if item.status == TaskStatus.READY:
                    # 5.85.4 修复: 返回深拷贝避免外部修改内部调度状态
                    ready.append(item.model_copy(deep=True))
        ready.sort(key=lambda x: {"P0": 0, "P1": 1, "P2": 2}.get(x.priority, 1))
        return ready

    def resolve_layer(self, work: WorkItem) -> str:
        return work.layer

    def resolve_priority(self, work: WorkItem) -> str:
        return work.priority

    def acquire_slot(self, layer: str) -> bool:
        with self._lock:
            if self._slots_used.get(layer, 0) < self._slots.get(layer, 0):
                self._slots_used[layer] = self._slots_used.get(layer, 0) + 1
                return True
            return False

    def release_slot(self, layer: str) -> None:
        with self._lock:
            self._slots_used[layer] = max(0, self._slots_used.get(layer, 0) - 1)

    def available_slots(self, layer: str) -> int:
        with self._lock:
            return self._slots.get(layer, 0) - self._slots_used.get(layer, 0)

    def complete_item(self, item_id: str, result: dict | None = None, error: str | None = None) -> None:
        with self._lock:
            item = self._items.get(item_id)
            if item is None:
                return
            item.status = TaskStatus.COMPLETED if error is None else TaskStatus.FAILED
            item.completed_at = now_utc().isoformat()
            item.result = result
            item.error = error
            self._slots_used[item.layer] = max(0, self._slots_used.get(item.layer, 0) - 1)

            for other in self._items.values():
                if other.status == TaskStatus.PENDING and item_id in other.depends_on:
                    all_done = True
                    for dep_id in other.depends_on:
                        dep = self._items.get(dep_id)
                        if dep is None or dep.status not in (TaskStatus.COMPLETED,):
                            all_done = False
                            break
                    if all_done:
                        other.status = TaskStatus.READY

            self._cleanup_completed(just_completed_id=item_id)

    def _cleanup_completed(self, just_completed_id: str | None = None) -> None:
        """5.65.3 修复：清理已完成且无PENDING依赖的item，防止_items无界增长。

        just_completed_id: 本次 complete_item 刚完成的 item_id，跳过不删，
        确保调用方可立即通过 status() 查询完成状态。
        """
        pending_deps: set[str] = set()
        for other in self._items.values():
            if other.status == TaskStatus.PENDING:
                pending_deps.update(other.depends_on)
        stale = [
            iid for iid, it in self._items.items()
            if it.status in (TaskStatus.COMPLETED, TaskStatus.FAILED)
            and iid not in pending_deps
            and iid != just_completed_id
        ]
        for iid in stale:
            del self._items[iid]

    def status(self, item_id: str) -> str | None:
        item = self._items.get(item_id)
        return item.status if item else None

    def pending_count(self) -> dict[str, int]:
        counts: dict[str, int] = {"trae": 0, "local": 0, "api": 0}
        with self._lock:
            for item in self._items.values():
                if item.status in (TaskStatus.PENDING, TaskStatus.READY):
                    counts[item.layer] = counts.get(item.layer, 0) + 1
        return counts

    def running_count(self) -> dict[str, int]:
        return dict(self._slots_used)
