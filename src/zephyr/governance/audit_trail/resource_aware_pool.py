# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §4
# [MODULE] zephyr.governance.audit_trail.resource_aware_pool
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] audit_admission_controller; orchestrator
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 双池(CPU/GPU)互不干扰; GPU路由规则: llm_inference/semantic_analysis/embedding→gpu
# [MODIFY-GUARD] audit-orchestrator/blueprint.md; resource_aware_pool.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError on submit after shutdown; PoolStats always returns current snapshot
# [TESTS] tests/audit-orchestrator/
# [A_module] module_id=MOD-GOV_resource_aware_pool | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any

from pydantic import BaseModel

_GPU_TASK_TYPES: frozenset[str] = frozenset(
    {
        "llm_inference",
        "semantic_analysis",
        "embedding",
    }
)


class PoolStats(BaseModel):
    cpu_active: int
    cpu_pending: int
    gpu_active: int
    gpu_pending: int


class ResourceAwarePool:
    def __init__(self, cpu_workers: int = 4, gpu_workers: int = 2) -> None:
        self._cpu_pool = ThreadPoolExecutor(max_workers=cpu_workers)
        self._gpu_pool = ThreadPoolExecutor(max_workers=gpu_workers)
        self._cpu_futures: list[Future] = []
        self._gpu_futures: list[Future] = []
        self._shutdown = False

    def submit(self, task_type: str, func: Callable[..., Any], *args: Any) -> Future:
        if self._shutdown:
            raise RuntimeError("ResourceAwarePool is shut down")
        pool = self._gpu_pool if self._route_task(task_type) == "gpu" else self._cpu_pool
        future = pool.submit(func, *args)
        if self._route_task(task_type) == "gpu":
            self._gpu_futures = [f for f in self._gpu_futures if not f.done()]
            self._gpu_futures.append(future)
        else:
            self._cpu_futures = [f for f in self._cpu_futures if not f.done()]
            self._cpu_futures.append(future)
        return future

    def _route_task(self, task_type: str) -> str:
        if task_type in _GPU_TASK_TYPES:
            return "gpu"
        return "cpu"

    def shutdown(self) -> None:
        if self._shutdown:
            return
        self._shutdown = True
        self._cpu_pool.shutdown(wait=True)
        self._gpu_pool.shutdown(wait=True)

    def stats(self) -> PoolStats:
        cpu_active = sum(1 for f in self._cpu_futures if not f.done())
        cpu_pending = self._cpu_pool._work_queue.qsize() if hasattr(self._cpu_pool, "_work_queue") else 0
        gpu_active = sum(1 for f in self._gpu_futures if not f.done())
        gpu_pending = self._gpu_pool._work_queue.qsize() if hasattr(self._gpu_pool, "_work_queue") else 0
        return PoolStats(
            cpu_active=cpu_active,
            cpu_pending=cpu_pending,
            gpu_active=gpu_active,
            gpu_pending=gpu_pending,
        )
