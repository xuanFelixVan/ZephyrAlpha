# [BLUEPRINT] MOD-INF-074 | docs/03_modules/_domain_infrastructure_runtime/resource_scheduler/blueprint.md
# [MODULE] zephyr.infra_runtime.resource_scheduler
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] 无（纯内存裁决；时钟/executor/告警全注入）
# [CONSUMERS] 运行时装配批（Hot/Warm/Cold 三平面进程资源准入统一入口）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 平面词表闭合(hot|warm|cold); 亲和核须为平面核子集且平面内独占; 平面累计内存≤预算; QPS令牌桶容量=回补速率=qps_limit(注入单调时钟); 超预算拒绝+告警留痕不抛; 非法输入 Fail-Closed 抛错; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure_runtime/resource_scheduler/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ResourceSchedulerError(占位 ZA-INF-UNREGISTERED-RESOURCE-SCHEDULER)——空配额表/未知平面/非法核集/负内存/非正QPS/重复requester/executor异常时抛
# [TESTS] tests/infra_runtime/test_resource_scheduler.py
# [A_module] module_id=MOD-INF-074 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
ResourceScheduler — 资源调度器（MOD-INF-074，IR-06）。

B7-09926（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-H1FS-014，D-INFRA-RUNTIME
§2）：CPU 核心亲和绑定 + 内存预算强制 + Cold/Warm/Hot 三平面资源隔离 +
QPS 限流统一入口。业界对标 cgroup 式资源隔离 + CPU 亲和 + 令牌桶限流。

纯内存逻辑：平面枚举 + 亲和映射表 + 内存预算表 + QPS 令牌桶（注入时钟），
``admit`` 统一裁决入口，超预算拒绝（返回 ``AdmitDecision(granted=False)``
并告警留痕）；实际 OS 级设置经注入 ``executor`` 回调，默认 None 仅记录到
``applied_records``。本件不做真实 cgroup/亲和系统调用。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: quotas 参数
#   fields: 参数 quotas（无注解）
#   code: resource_scheduler.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: resource_scheduler.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: executor 参数
#   fields: 参数 executor（无注解）
#   code: resource_scheduler.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: alert_sink 参数
#   fields: 参数 alert_sink（无注解）
#   code: resource_scheduler.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ResourceScheduler
#   name_en: ResourceScheduler
#   intro: 三平面资源调度器（配额注册表 + 统一准入裁决 + executor 注入）。
#   desc: 三平面资源调度器（配额注册表 + 统一准入裁决 + executor 注入）。；公共方法（定义序）: admit, plane_usage, applied_records；源码 L182-L339
#   inputs: quotas clock executor alert_sink
#   outputs: 返回值
#   （注：A1 之后另有 7 个公共定义未列入（含 7 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（8 定义）
#   name_en: public defs
#   intro: ResourceScheduler
#   downstream: 运行时装配批（Hot/Warm/Cold 三平面进程资源准入统一入口）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "AdmitDecision",
    "ExecutorRecord",
    "PlaneQuota",
    "ResourcePlane",
    "ResourceRequest",
    "ResourceScheduler",
    "ResourceSchedulerError",
    "SchedulingRejection",
]


class ResourceSchedulerError(Exception):
    """资源调度输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-INF-UNREGISTERED-RESOURCE-SCHEDULER。
    """


class ResourcePlane(str, Enum):
    """资源平面（词表闭合）。"""

    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


@dataclass(frozen=True)
class PlaneQuota:
    """单平面资源配额声明（frozen）。"""

    plane: ResourcePlane
    cpu_cores: frozenset[int]
    mem_budget_bytes: int
    qps_limit: float


@dataclass(frozen=True)
class ResourceRequest:
    """准入请求（亲和核 + 内存 + QPS 声明，frozen）。"""

    plane: ResourcePlane
    requester: str
    cpu_cores: frozenset[int]
    mem_bytes: int
    qps: float


@dataclass(frozen=True)
class AdmitDecision:
    """准入裁决结果（granted=False 时 reasons 非空，frozen）。"""

    granted: bool
    reasons: tuple[str, ...]
    decided_at: float


@dataclass(frozen=True)
class SchedulingRejection:
    """超预算拒绝（告警载荷，frozen）。"""

    request: ResourceRequest
    reasons: tuple[str, ...]
    raised_at: float


@dataclass(frozen=True)
class ExecutorRecord:
    """executor 应用记录（默认 None executor 时仅记录，frozen）。"""

    request: ResourceRequest
    applied_at: float
    executor_invoked: bool


class _TokenBucket:
    """令牌桶（注入单调时钟，容量=回补速率=qps_limit）。"""

    def __init__(self, rate: float, clock: Callable[[], float]) -> None:
        self._rate = rate
        self._clock = clock
        self._tokens = rate
        self._last = clock()

    def try_consume(self, amount: float) -> bool:
        now = self._clock()
        elapsed = now - self._last
        if elapsed > 0:
            self._tokens = min(self._rate, self._tokens + elapsed * self._rate)
            self._last = now
        if amount > self._tokens + 1e-9:  # 浮点边界容差
            return False
        self._tokens = max(0.0, self._tokens - amount)
        return True

    @property
    def tokens(self) -> float:
        return self._tokens


class ResourceScheduler:
    """三平面资源调度器（配额注册表 + 统一准入裁决 + executor 注入）。"""

    def __init__(
        self,
        *,
        quotas: Mapping[ResourcePlane, PlaneQuota],
        clock: Callable[[], float] | None = None,
        executor: Callable[[ResourceRequest], None] | None = None,
        alert_sink: Callable[[SchedulingRejection], None] | None = None,
    ) -> None:
        if not quotas:
            raise ResourceSchedulerError("quotas 为空（无平面配额声明）")
        self._clock = clock or time.monotonic
        self._executor = executor
        self._alert_sink = alert_sink
        self._quotas: dict[ResourcePlane, PlaneQuota] = {}
        for plane, quota in quotas.items():
            if not isinstance(plane, ResourcePlane):
                raise ResourceSchedulerError(f"非法平面键: {plane!r}")
            if quota.plane is not plane:
                raise ResourceSchedulerError(f"配额平面不符: 键 {plane.value} vs 配额 {quota.plane.value}")
            if not quota.cpu_cores or any(not isinstance(c, int) or c < 0 for c in quota.cpu_cores):
                raise ResourceSchedulerError(f"平面 {plane.value} cpu_cores 非法: {quota.cpu_cores!r}")
            if quota.mem_budget_bytes <= 0:
                raise ResourceSchedulerError(f"平面 {plane.value} mem_budget_bytes 非正: {quota.mem_budget_bytes}")
            if quota.qps_limit <= 0:
                raise ResourceSchedulerError(f"平面 {plane.value} qps_limit 非正: {quota.qps_limit}")
            self._quotas[plane] = quota
        self._buckets: dict[ResourcePlane, _TokenBucket] = {
            plane: _TokenBucket(quota.qps_limit, self._clock) for plane, quota in self._quotas.items()
        }
        self._allocations: dict[str, ResourceRequest] = {}
        self._applied: list[ExecutorRecord] = []

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _alert(self, rejection: SchedulingRejection) -> None:
        _log.warning(
            "资源准入拒绝: %s/%s (%s)",
            rejection.request.plane.value,
            rejection.request.requester,
            "; ".join(rejection.reasons),
        )
        if self._alert_sink is not None:
            try:
                self._alert_sink(rejection)
            except Exception:  # noqa: BLE001 — 告警不阻断（蓝图 §1）
                _log.exception("alert_sink 告警失败")

    def _quota_of(self, plane: ResourcePlane) -> PlaneQuota:
        if not isinstance(plane, ResourcePlane):
            raise ResourceSchedulerError(f"非法平面: {plane!r}")
        quota = self._quotas.get(plane)
        if quota is None:
            raise ResourceSchedulerError(f"未知平面: {plane!r}（未在配额声明中）")
        return quota

    # ── 统一准入裁决 ──────────────────────────────────────────────────────

    def admit(
        self,
        plane: ResourcePlane,
        cpu_cores: frozenset[int] | set[int],
        mem_bytes: int,
        qps: float,
        requester: str = "",
    ) -> AdmitDecision:
        """统一裁决：亲和核子集/平面内独占 + 内存预算 + QPS 令牌桶。

        超预算 → ``AdmitDecision(granted=False)`` + 告警留痕（不抛）；
        非法输入 → Fail-Closed 抛 ``ResourceSchedulerError``。
        """
        if not isinstance(plane, ResourcePlane):
            raise ResourceSchedulerError(f"非法平面: {plane!r}")
        quota = self._quota_of(plane)
        cores = frozenset(cpu_cores)
        if not cores or any(not isinstance(c, int) or c < 0 for c in cores):
            raise ResourceSchedulerError(f"cpu_cores 非法: {cpu_cores!r}")
        if not isinstance(mem_bytes, int) or mem_bytes < 0:
            raise ResourceSchedulerError(f"mem_bytes 非法: {mem_bytes!r}")
        if not isinstance(qps, (int, float)) or qps <= 0:
            raise ResourceSchedulerError(f"qps 非法: {qps!r}")
        if requester and requester in self._allocations:
            raise ResourceSchedulerError(f"requester 重复准入: {requester!r}")

        request = ResourceRequest(
            plane=plane,
            requester=requester,
            cpu_cores=cores,
            mem_bytes=mem_bytes,
            qps=float(qps),
        )

        reasons: list[str] = []
        if not cores <= quota.cpu_cores:
            reasons.append(f"亲和核越界: {sorted(cores - quota.cpu_cores)} 不在平面 {plane.value} 核集内")
        occupied = (
            set().union(*(r.cpu_cores for r in self._allocations.values() if r.plane is plane))
            if any(r.plane is plane for r in self._allocations.values())
            else set()
        )
        conflict = cores & occupied
        if conflict:
            reasons.append(f"亲和核冲突: {sorted(conflict)} 已被平面 {plane.value} 内其他 requester 独占")
        mem_used = sum(r.mem_bytes for r in self._allocations.values() if r.plane is plane)
        if mem_used + mem_bytes > quota.mem_budget_bytes:
            reasons.append(f"内存超预算: 已用 {mem_used} + 请求 {mem_bytes} > 预算 {quota.mem_budget_bytes}")
        if qps > quota.qps_limit:
            reasons.append(f"qps 超平面限流上限: {qps} > {quota.qps_limit}")

        decided_at = self._clock()
        if not reasons:
            # 前置校验全过才触碰令牌桶（拒绝路径不消耗令牌，保证确定性）
            if not self._buckets[plane].try_consume(float(qps)):
                reasons.append(f"qps 令牌不足: 请求 {qps}，桶余量 {self._buckets[plane].tokens:.6f}")
        if reasons:
            decision = AdmitDecision(granted=False, reasons=tuple(reasons), decided_at=decided_at)
            self._alert(SchedulingRejection(request=request, reasons=decision.reasons, raised_at=decided_at))
            return decision

        key = requester or f"__anon_{len(self._allocations)}"
        self._allocations[key] = request
        if self._executor is not None:
            try:
                self._executor(request)
                invoked = True
            except Exception as exc:
                raise ResourceSchedulerError(f"executor 应用失败: {exc}") from exc
        else:
            invoked = False
        self._applied.append(ExecutorRecord(request=request, applied_at=decided_at, executor_invoked=invoked))
        return AdmitDecision(granted=True, reasons=(), decided_at=decided_at)

    # ── 查询 ─────────────────────────────────────────────────────────────

    def plane_usage(self, plane: ResourcePlane) -> dict[str, object]:
        """单平面用量视图（确定性：核集排序输出）。"""
        quota = self._quota_of(plane)
        used_cores: set[int] = set()
        mem_used = 0
        for req in self._allocations.values():
            if req.plane is plane:
                used_cores |= req.cpu_cores
                mem_used += req.mem_bytes
        return {
            "plane": plane.value,
            "cores_used": tuple(sorted(used_cores)),
            "cores_free": tuple(sorted(quota.cpu_cores - used_cores)),
            "mem_used_bytes": mem_used,
            "mem_free_bytes": quota.mem_budget_bytes - mem_used,
            "qps_tokens": self._buckets[plane].tokens,
        }

    @property
    def applied_records(self) -> tuple[ExecutorRecord, ...]:
        """executor 应用记录（按准入先后，确定性）。"""
        return tuple(self._applied)
