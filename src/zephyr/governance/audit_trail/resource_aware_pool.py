# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §4
# [MODULE] zephyr.governance.audit_trail.resource_aware_pool
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] audit_admission_controller; orchestrator
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 双池(CPU/GPU)互不干扰; GPU路由规则: llm_inference/semantic_analysis/embedding->gpu
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
    def __init__(self, cpu_workers: int = 4, gpu_workers: int = 2, max_pending: int | None = None) -> None:
        self._cpu_pool = ThreadPoolExecutor(max_workers=cpu_workers)
        self._gpu_pool = ThreadPoolExecutor(max_workers=gpu_workers)
        self._cpu_futures: list[Future] = []
        self._gpu_futures: list[Future] = []
        self._shutdown = False
        # 5.67.1 修复：添加 maxsize 背压，防止无限制提交导致内存耗尽
        self._max_cpu_pending = max_pending if max_pending is not None else cpu_workers * 2
        self._max_gpu_pending = max_pending if max_pending is not None else gpu_workers * 2

    def _pending_count(self, pool: ThreadPoolExecutor) -> int:
        q = getattr(pool, "_work_queue", None)
        return q.qsize() if q is not None else 0

    def submit(self, task_type: str, func: Callable[..., Any], *args: Any) -> Future:
        if self._shutdown:
            raise RuntimeError("ResourceAwarePool is shut down")
        is_gpu = self._route_task(task_type) == "gpu"
        pool = self._gpu_pool if is_gpu else self._cpu_pool
        # 5.67.1 修复：提交前检查队列是否已满，满则 raise 实现背压
        pending = self._pending_count(pool)
        max_pending = self._max_gpu_pending if is_gpu else self._max_cpu_pending
        if pending >= max_pending:
            raise RuntimeError(
                f"ResourceAwarePool {'gpu' if is_gpu else 'cpu'} queue full "
                f"(pending={pending}, max={max_pending})"
            )
        future = pool.submit(func, *args)
        if is_gpu:
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
        cpu_pending = self._pending_count(self._cpu_pool)
        gpu_active = sum(1 for f in self._gpu_futures if not f.done())
        gpu_pending = self._pending_count(self._gpu_pool)
        return PoolStats(
            cpu_active=cpu_active,
            cpu_pending=cpu_pending,
            gpu_active=gpu_active,
            gpu_pending=gpu_pending,
        )
