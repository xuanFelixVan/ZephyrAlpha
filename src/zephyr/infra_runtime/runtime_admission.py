# [BLUEPRINT] docs/_working/resource_schedule/resource_schedule_v2_construction_plan.md | §2.2 L-3 / §4 P2-c
# [MODULE] zephyr.infra_runtime.runtime_admission
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.orchestrator.governance.capacity_budget（并发/WIP 维）;
#   zephyr.shared.capacity_governance.api_cost_governor（令牌桶维）;
#   zephyr.infra_runtime.resource_scheduler（内存/空间维）; yaml; config/resource_profile_registry.yaml（只读真源）
# [CONSUMERS] 运行时装配批（排班表"运行时下半身"——空间维准入统一入口）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 池词表真源=config/resource_profile_registry.yaml pool_vocabulary.lanes（禁硬编码泳道名）;
#   planned/retired 实体不计入运行时预算且不获准入（裁定 R-D）; 三件配额全由注册表供给（pool+est_duration_min+peak_mem_gb）;
#   内存维单平面强制全局 mem_ceiling_gb（与排班闸同口径）; 准入=三件全过方放行，任一件失败即回滚可逆副作用;
#   时钟注入、同输入必同输出（资源平面令牌桶速率除外，按注入时钟确定性回补）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeAdmissionError——注册表损坏/未知池键/非法请求参数时抛（Fail-Closed）
# [TESTS] tests/infra_runtime/test_runtime_admission.py
# [A_module] module_id=MOD-INF-RT-ADM | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
runtime_admission — 运行时准入三件合一（P2-c / L-3）。

第一性原理：排班表管"时间维"（谁在哪个窗开工），本件管"空间维"运行时准入
（此刻能不能起、起多少并发、吃多少内存、什么速率），是排班表的"运行时下半身"。

接通此前三座零引用孤岛，配额输入统一取自
``config/resource_profile_registry.yaml``（只读真源）：

* **并发/WIP 维** → :class:`CapacityBudgetController`：每泳道池并发上限=
  ``pool_vocabulary.workers[pool]``（注册表供给，不硬编码池名）。
* **内存/空间维** → :class:`ResourceScheduler.admit`：单"运行时准入平面"承载全局
  ``mem_ceiling_gb``（引用 reaper 红线，与排班闸 check_mem_ceiling 同口径），
  每请求吃 ``peak_mem_gb``，跨活动任务求和 ≤ 天花板。
* **速率维** → :class:`ApiCostGovernor` 令牌桶：**注册表驱动参数**（每池 base_qps=
  该池 workers），无 API 成本单价表前 unit_cost=0（仅计量速率不臆造成本）。

裁定 R-D：``planned``（纸面未排产）/``retired`` 实体既不计入运行时预算和，也不获
准入（未排产不占空间）。三件缺一对接面（枚举不同轴：SystemPool/ResourcePlane/成本源
三者词表互异），故本件以**最小可用接口合一**——把注册表泳道池适配到各件原生的最小
输入面，不改动三件既有语义（capacity_budget 仅向后兼容放宽 WIP 键，见其头）。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Final, Mapping

import yaml

from zephyr.infra_runtime.resource_scheduler import (
    AdmitDecision,
    PlaneQuota,
    ResourcePlane,
    ResourceScheduler,
)
from zephyr.orchestrator.governance.capacity_budget import CapacityBudgetController
from zephyr.shared.capacity_governance.api_cost_governor import ApiCostGovernor

_log = logging.getLogger(__name__)

__all__: Final = [
    "RuntimeAdmissionError",
    "RuntimeAdmissionCoordinator",
    "PoolQuota",
    "RuntimeQuotas",
    "AdmissionResult",
    "build_runtime_quotas",
    "DEFAULT_REGISTRY_RELPATH",
]

DEFAULT_REGISTRY_RELPATH: Final = "config/resource_profile_registry.yaml"

# 运行时准入平面：把全局 mem_ceiling 承载在单一 ResourcePlane 上（排班天花板是全局
# 口径、非分池，故用单平面求全局和；池归池（并发维由 capacity 管）、平面承载空间维）。
_ADMISSION_PLANE: Final = ResourcePlane.WARM
_GIB: Final = 1024**3
_ADMISSION_QPS: Final = 1.0  # 内存平面内 qps 不作约束（速率维交 api_cost_governor）
_PLANE_QPS_LIMIT: Final = 1e9


class RuntimeAdmissionError(Exception):
    """运行时准入输入/状态非法（Fail-Closed）。"""

    error_code = "ZA-INF-RT-ADM"


@dataclass(frozen=True)
class PoolQuota:
    """单泳道池运行时配额（注册表派生，frozen）。"""

    pool: str
    workers: int  # 并发/WIP 上限
    active_entity_count: int  # 计入预算的活动实体数（R-D：不含 planned/retired）
    active_peak_mem_gb: float  # 活动实体申报内存和（GB，R-D 口径）
    max_est_duration_min: int  # 活动实体最长申报时长（min，观测用）


@dataclass(frozen=True)
class RuntimeQuotas:
    """注册表派生的运行时配额总览（frozen）。"""

    lanes: tuple[str, ...]
    mem_ceiling_gb: float
    per_pool: Mapping[str, PoolQuota]

    def workers(self) -> dict[str, int]:
        return {pool: q.workers for pool, q in self.per_pool.items()}

    @property
    def total_workers(self) -> int:
        return sum(q.workers for q in self.per_pool.values())


@dataclass(frozen=True)
class AdmissionResult:
    """一次准入裁决汇总（三件合一结果，frozen）。"""

    task_id: str
    pool: str
    granted: bool
    reasons: tuple[str, ...]
    decided_at: float
    concurrency_granted: bool = False
    memory_granted: bool = False
    rate_granted: bool = False


def _is_admissible_status(e: dict) -> bool:
    """是否可计入运行时预算并获准入（裁定 R-D）。

    retired/orphaned_source=退役不计；planned=纸面未排产亦不计不准入（防"纸面排班"
    挤占真实重活空间）。默认缺 status 视为 active。
    """
    status = str(e.get("status") or "active")
    return status in ("active",)


def build_runtime_quotas(
    entities: list[dict],
    pool_vocabulary: Mapping,
    mem_ceiling_gb: float,
) -> RuntimeQuotas:
    """从注册表实体+泳道词表派生运行时配额（纯函数，注册表只读）。

    池词表真源=``pool_vocabulary.lanes``（禁硬编码）；未挂真池的实体不臆造合成池，
    直接跳过（其账归生成器 ``sched_pool_undeclared``，与排班闸 C-7/R-C 同口径）。
    R-D：仅 ``status=active`` 实体计入内存和/时长/计数。
    """
    lanes = [str(x) for x in (pool_vocabulary.get("lanes") or [])]
    workers_map = {str(k): int(v) for k, v in (pool_vocabulary.get("workers") or {}).items()}
    ceiling = float(mem_ceiling_gb)

    per_pool: dict[str, PoolQuota] = {}
    for lane in lanes:
        members = [
            e
            for e in entities
            if str(e.get("pool") or "").strip() == lane and _is_admissible_status(e)
        ]
        active_count = len(members)
        mem_sum = sum(float(e.get("peak_mem_gb") or 0.0) for e in members)
        max_dur = max((int(e.get("est_duration_min") or 0) for e in members), default=0)
        per_pool[lane] = PoolQuota(
            pool=lane,
            workers=int(workers_map.get(lane, 0)),
            active_entity_count=active_count,
            active_peak_mem_gb=round(mem_sum, 6),
            max_est_duration_min=max_dur,
        )
    return RuntimeQuotas(lanes=tuple(lanes), mem_ceiling_gb=ceiling, per_pool=per_pool)


class RuntimeAdmissionCoordinator:
    """三件合一的运行时准入协调器（注册表供配额，时钟注入，确定性）。"""

    def __init__(
        self,
        quotas: RuntimeQuotas,
        *,
        clock: Callable[[], float] | None = None,
    ) -> None:
        if not quotas.lanes:
            raise RuntimeAdmissionError("注册表无泳道池（lanes 为空）")
        self._quotas = quotas
        self._clock = clock or _monotonic_seconds

        # ① 并发/WIP 维：capacity_budget，WIP 键=注册表真池，上限=workers
        self._capacity = CapacityBudgetController(
            max_concurrent_tasks=max(1, quotas.total_workers)
        )
        self._capacity.budget.wip_limit_per_system = dict(quotas.workers())

        # ② 内存/空间维：resource_scheduler 单平面承载全局 mem_ceiling，
        #    核集大小=总并发（核独占镜像并发上限，内存天花板先于核绑定成约束）
        plane_cores = frozenset(range(max(1, quotas.total_workers)))
        self._scheduler = ResourceScheduler(
            quotas={
                _ADMISSION_PLANE: PlaneQuota(
                    plane=_ADMISSION_PLANE,
                    cpu_cores=plane_cores,
                    mem_budget_bytes=int(round(quotas.mem_ceiling_gb * _GIB)),
                    qps_limit=_PLANE_QPS_LIMIT,
                )
            },
            clock=self._clock,
        )

        # ③ 速率维：api_cost_governor，每池注册一个源，base_qps=workers（注册表驱动）
        self._governor = ApiCostGovernor(clock=_datetime_clock(self._clock))
        for pool, worker_n in quotas.workers().items():
            self._governor.register_source(
                pool, unit_cost=0.0, base_qps=float(max(1, worker_n))
            )

        self._core_counter = 0
        self._active: dict[str, str] = {}  # task_id -> pool（供 release 归还）

    # ── 配额视图 ────────────────────────────────────────────────────────────

    def pool_quotas(self) -> Mapping[str, PoolQuota]:
        """注册表派生的每池配额（只读）。"""
        return self._quotas.per_pool

    @property
    def quotas(self) -> RuntimeQuotas:
        return self._quotas

    def active_count(self, pool: str) -> int:
        return self._capacity.state.system_active.get(pool, 0)

    # ── 统一准入 ────────────────────────────────────────────────────────────

    def request_admission(
        self,
        task_id: str,
        *,
        pool: str,
        mem_gb: float,
        status: str = "active",
    ) -> AdmissionResult:
        """一次运行时准入：并发 → 速率 → 内存，三件全过方放行，否则回滚可逆副作用。

        内存/空间准入用 :class:`ResourceScheduler`（一次性分配、无 release，符合其
        规划型设计意图），故置于最后：仅当并发与速率放行后才触它，避免副作用泄漏。
        速率令牌若已扣而后内存失败不自愈回退——令牌随注入时钟自然回补（可忽略，留痕）。
        """
        if not task_id:
            raise RuntimeAdmissionError("task_id 为空")
        pool = str(pool or "").strip()
        if pool not in self._quotas.per_pool:
            raise RuntimeAdmissionError(f"未知泳道池: {pool!r}（不在注册表 lanes 中）")
        if mem_gb is None or float(mem_gb) < 0:
            raise RuntimeAdmissionError(f"mem_gb 非法: {mem_gb!r}")
        if str(status or "active") != "active":
            return AdmissionResult(
                task_id=task_id,
                pool=pool,
                granted=False,
                reasons=(f"status={status} 未排产（R-D：planned/retired 不占运行时预算）",),
                decided_at=self._clock(),
            )
        if task_id in self._active:
            raise RuntimeAdmissionError(f"task_id 重复准入: {task_id!r}")

        reasons: list[str] = []
        conc_ok = rate_ok = mem_ok = False

        # ① 并发/WIP
        conc_ok = self._capacity.try_accept(task_id, pool)
        if not conc_ok:
            reasons.append(f"并发超泳道配额: pool={pool} workers={self._quotas.per_pool[pool].workers}")

        # ② 速率（令牌桶，注册表驱动参数）
        rate_ok = False
        if conc_ok:
            rate_ok = self._governor.try_acquire(pool, tokens=1)
            if not rate_ok:
                self._capacity.release(task_id, pool)
                conc_ok = False
                reasons.append(f"速率令牌不足: pool={pool}（base_qps={self._quotas.per_pool[pool].workers}）")

        # ③ 内存/空间（ResourceScheduler，全局 mem_ceiling）
        if conc_ok:
            core = self._next_core()
            decision: AdmitDecision = self._scheduler.admit(
                _ADMISSION_PLANE,
                frozenset({core}),
                int(round(float(mem_gb) * _GIB)),
                _ADMISSION_QPS,
                requester=task_id,
            )
            mem_ok = decision.granted
            if not mem_ok:
                self._capacity.release(task_id, pool)
                conc_ok = False
                reasons.extend(decision.reasons)

        granted = conc_ok and rate_ok and mem_ok
        if granted:
            self._active[task_id] = pool
        return AdmissionResult(
            task_id=task_id,
            pool=pool,
            granted=granted,
            reasons=tuple(reasons),
            decided_at=self._clock(),
            concurrency_granted=conc_ok,
            memory_granted=mem_ok,
            rate_granted=rate_ok,
        )

    def admit_entity(self, entity: dict) -> AdmissionResult:
        """按注册表实体准入（取 pool/peak_mem_gb/status 三字段，R-D 内建）。"""
        return self.request_admission(
            str(entity.get("task_id")),
            pool=str(entity.get("pool") or ""),
            mem_gb=float(entity.get("peak_mem_gb") or 0.0),
            status=str(entity.get("status") or "active"),
        )

    def release(self, task_id: str) -> str | None:
        """归还并发槽位（动态维）；内存平面/令牌桶无需归还（前者一次性规划、后者随时钟回补）。"""
        pool = self._active.pop(task_id, None)
        if pool is None:
            return None
        return self._capacity.release(task_id, pool)

    def snapshot(self) -> dict:
        """运行时观测快照（确定性、可序列化）。"""
        return {
            "active_tasks": self._capacity.state.active_tasks,
            "queued_tasks": self._capacity.state.queued_tasks,
            "system_active": dict(sorted(self._capacity.state.system_active.items())),
            "plane_usage_mem_used_bytes": self._scheduler.plane_usage(_ADMISSION_PLANE)["mem_used_bytes"],
        }

    def _next_core(self) -> int:
        core = self._core_counter
        self._core_counter += 1
        return core

    # ── 注册表装载（只读真源）─────────────────────────────────────────────

    @classmethod
    def from_registry(
        cls,
        registry_path: str | Path,
        *,
        clock: Callable[[], float] | None = None,
    ) -> "RuntimeAdmissionCoordinator":
        """从 config/resource_profile_registry.yaml（只读）构造协调器。"""
        p = Path(registry_path)
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            raise RuntimeAdmissionError(f"注册表 YAML 损坏（fail-closed）: {exc}") from exc
        entities = list(data.get("entities") or [])
        pool_vocabulary = data.get("pool_vocabulary") or {}
        mem_ceiling = data.get("mem_ceiling_gb")
        if mem_ceiling is None:
            raise RuntimeAdmissionError("注册表缺 mem_ceiling_gb 头部")
        quotas = build_runtime_quotas(entities, pool_vocabulary, float(mem_ceiling))
        return cls(quotas, clock=clock)


def _monotonic_seconds() -> float:
    import time

    return time.monotonic()


def _datetime_clock(seconds_clock: Callable[[], float]) -> Callable[[], datetime.datetime]:
    """把单调秒时钟适配为 ApiCostGovernor 需要的 datetime 时钟（保持确定性注入）。"""

    epoch = datetime.datetime(2026, 1, 1, tzinfo=datetime.UTC)

    def _now() -> datetime.datetime:
        return epoch + datetime.timedelta(seconds=seconds_clock())

    return _now
