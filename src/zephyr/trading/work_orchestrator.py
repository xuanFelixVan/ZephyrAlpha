# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.work_orchestrator
# [DOMAIN] D_TRADING
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
                dag = WorkDAG(**data)
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
            work.created_at = datetime.now().isoformat()
        with self._lock:
            self._items[work.item_id] = work
            if not work.depends_on:
                work.status = "READY"
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
                status="READY" if not deps else "PENDING",
            )
            iid = self.submit(item)
            node_items[node.node_id] = iid
        return dag_id

    def schedule_next(self) -> list[WorkItem]:
        ready: list[WorkItem] = []
        with self._lock:
            for item in self._items.values():
                if item.status == "READY":
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
            for low_layer in ["api", "local", "trae"]:
                if low_layer != layer and self._slots_used.get(low_layer, 0) < self._slots.get(low_layer, 0):
                    if {"P0": 0, "P1": 1, "P2": 2}.get(layer, 1) < {"P0": 0, "P1": 1, "P2": 2}.get(low_layer, 1):
                        pass
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
            item.status = "COMPLETED" if error is None else "FAILED"
            item.completed_at = datetime.now().isoformat()
            item.result = result
            item.error = error
            self._slots_used[item.layer] = max(0, self._slots_used.get(item.layer, 0) - 1)

            for other in self._items.values():
                if other.status == "PENDING" and item_id in other.depends_on:
                    all_done = True
                    for dep_id in other.depends_on:
                        dep = self._items.get(dep_id)
                        if dep is None or dep.status not in ("COMPLETED",):
                            all_done = False
                            break
                    if all_done:
                        other.status = "READY"

    def status(self, item_id: str) -> str | None:
        item = self._items.get(item_id)
        return item.status if item else None

    def pending_count(self) -> dict[str, int]:
        counts: dict[str, int] = {"trae": 0, "local": 0, "api": 0}
        with self._lock:
            for item in self._items.values():
                if item.status in ("PENDING", "READY"):
                    counts[item.layer] = counts.get(item.layer, 0) + 1
        return counts

    def running_count(self) -> dict[str, int]:
        return dict(self._slots_used)
