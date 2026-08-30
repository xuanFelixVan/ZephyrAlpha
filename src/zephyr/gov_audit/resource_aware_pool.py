# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §4
# [MODULE] zephyr.gov_audit.resource_aware_pool
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] audit_admission_controller; orchestrator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 双池(CPU/GPU)互不干扰; GPU路由规则: llm_inference/semantic_analysis/embedding->gpu
# [MODIFY-GUARD] audit-orchestrator/blueprint.md; resource_aware_pool.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError on submit after shutdown; PoolStats always returns current snapshot
# [TESTS] tests/audit-orchestrator/
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: cpu_workers 参数
#   fields: 参数 cpu_workers（无注解）
#   code: resource_aware_pool.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: gpu_workers 参数
#   fields: 参数 gpu_workers（无注解）
#   code: resource_aware_pool.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: max_pending 参数
#   fields: 参数 max_pending（无注解）
#   code: resource_aware_pool.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ResourceAwarePool
#   name_en: ResourceAwarePool
#   intro: class ResourceAwarePool 源码 L83-L162
#   desc: 公共方法（定义序）: gpu_futures, cpu_futures, submit, shutdown, stats；源码 L83-L162
#   inputs: cpu_workers gpu_workers max_pending
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: ResourceAwarePool
#   downstream: audit_admission_controller; orchestrator
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

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

    @property
    def gpu_futures(self) -> list[Future]:
        """只读：gpu_futures（Stage 4 公共化）。"""
        return self._gpu_futures

    @gpu_futures.setter
    def gpu_futures(self, value):
        """写入：gpu_futures（Stage 4 公共化）。"""
        self._gpu_futures = value

    @property
    def cpu_futures(self) -> list[Future]:
        """只读：cpu_futures（Stage 4 公共化）。"""
        return self._cpu_futures

    @cpu_futures.setter
    def cpu_futures(self, value):
        """写入：cpu_futures（Stage 4 公共化）。"""
        self._cpu_futures = value

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
                f"ResourceAwarePool {'gpu' if is_gpu else 'cpu'} queue full (pending={pending}, max={max_pending})"
            )
        future = pool.submit(func, *args)
        # 治本（裁定#18 G12）：原代码过滤已完成 futures 导致 _cpu_futures 丢失历史记录，
        # 测试契约 (test_batch_submit) 要求所有提交的 futures 都保留在列表中。
        # stats() 方法已用 f.done() 区分 active/pending，无需在 submit 时清理。
        if is_gpu:
            self._gpu_futures.append(future)
        else:
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
