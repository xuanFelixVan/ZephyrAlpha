# [BLUEPRINT] MOD-INF-080 | docs/03_modules/_domain_infrastructure_runtime/latency_budget_allocator/blueprint.md
# [MODULE] zephyr.infra_runtime.latency_budget_allocator
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] 无（预算核心纯内存；clock/alert_sink 全注入）
# [CONSUMERS] 运行时装配批（Hot/Warm 平面阶段预算登记 / 实际耗时上报 / 预算消耗率报表）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 平面词表闭合(hot|warm); 端到端预算 HOT=10ms/WARM=1000ms; 阶段分解总和≤平面预算否则拒绝; 预算表版本逐次递增; record 仅接受已登记 plane/stage 且 actual≥0; 超预算阶段判定+告警留痕; 报表确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure_runtime/latency_budget_allocator/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] LatencyBudgetError(占位 ZA-INF-UNREGISTERED-LATENCY-BUDGET)——非法平面/空阶段/非正预算/分解超总额/未登记平面或阶段/负耗时上报时抛
# [TESTS] tests/infra_runtime/test_latency_budget_allocator.py
# [A_module] module_id=MOD-INF-080 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""LatencyBudgetAllocator — 延迟预算分配器（MOD-INF-080）。

B14-04701（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-H1FS-013，A9 运维架构
§8.3.10）：Hot <10ms / Warm <1s **端到端预算**分解至各阶段并登记 SSOT
（预算表**版本化**，每次 allocate 版本递增），各进程上报实际耗时（纯内存
记录），**超预算阶段判定 + 告警回调**，预算消耗率报表（report()）。Google
SRE 延迟预算分解思想单机化：阶段预算之和不得超过平面端到端预算，超出即
Fail-Closed 拒绝登记。

查重分工（蓝图 §0）：cold_plane_isolation=Cold 平面通道门禁（零交集）；
latency_attributor=基于 Span 的延迟归因（本件只做预算登记/上报/报表，不做
Span 归因）；performance_monitor=执行核性能采集（本件不复用其采集面）。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "BudgetTable",
    "BudgetViolation",
    "LatencyBudgetAllocator",
    "LatencyBudgetError",
    "PLANE_BUDGET_MS",
    "Plane",
    "StageBudget",
]


class LatencyBudgetError(Exception):
    """延迟预算分配输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-INF-UNREGISTERED-LATENCY-BUDGET。
    """


class Plane(str, Enum):
    """延迟平面（词表闭合；Cold 平面 >1s 不纳入预算分解）。"""

    HOT = "hot"
    WARM = "warm"


#: 平面端到端预算常量（毫秒）
PLANE_BUDGET_MS: Final[dict[Plane, float]] = {
    Plane.HOT: 10.0,
    Plane.WARM: 1000.0,
}


@dataclass(frozen=True)
class StageBudget:
    """单阶段预算条目（frozen）。"""

    stage: str
    budget_ms: float


@dataclass(frozen=True)
class BudgetTable:
    """平面预算表（SSOT 快照；version 逐次递增）。"""

    plane: Plane
    stages: tuple[StageBudget, ...]
    version: int
    allocated_at: datetime.datetime


@dataclass(frozen=True)
class BudgetViolation:
    """超预算阶段判定（告警载荷）。"""

    plane: Plane
    stage: str
    budget_ms: float
    actual_ms: float
    raised_at: datetime.datetime


class LatencyBudgetAllocator:
    """延迟预算分配件（分解登记 + 耗时上报 + 超支判定 + 消耗率报表）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        alert_sink: Callable[[BudgetViolation], None] | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._alert_sink = alert_sink
        self._tables: dict[Plane, BudgetTable] = {}
        self._versions: dict[Plane, int] = {}
        self._actuals: dict[Plane, dict[str, list[float]]] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _alert(self, violation: BudgetViolation) -> None:
        _log.warning(
            "延迟预算超支: %s/%s 预算 %.3fms 实际 %.3fms",
            violation.plane.value,
            violation.stage,
            violation.budget_ms,
            violation.actual_ms,
        )
        if self._alert_sink is not None:
            try:
                self._alert_sink(violation)
            except Exception:  # noqa: BLE001 — 告警不阻断（蓝图 §1）
                _log.exception("alert_sink 告警失败")

    def _budget_of(self, plane: Plane, stage: str) -> float:
        table = self._tables.get(plane)
        if table is None:
            raise LatencyBudgetError(f"平面未登记预算表: {plane.value!r}")
        for sb in table.stages:
            if sb.stage == stage:
                return sb.budget_ms
        raise LatencyBudgetError(f"阶段未登记: {plane.value!r}/{stage!r}")

    # ── 预算分解登记 ──────────────────────────────────────────────────────

    def allocate(self, plane: Plane, stages: Mapping[str, float]) -> int:
        """阶段预算分解登记：总和 ≤ 平面端到端预算，否则拒绝；版本递增。"""
        if not isinstance(plane, Plane):
            raise LatencyBudgetError(f"非法平面: {plane!r}")
        if not stages:
            raise LatencyBudgetError("阶段预算表为空")
        items: list[StageBudget] = []
        for stage, budget_ms in stages.items():
            if not stage:
                raise LatencyBudgetError("阶段名为空")
            if not (budget_ms > 0):
                raise LatencyBudgetError(f"阶段预算非正: {stage!r}={budget_ms}ms")
            items.append(StageBudget(stage=stage, budget_ms=float(budget_ms)))
        total = sum(sb.budget_ms for sb in items)
        cap = PLANE_BUDGET_MS[plane]
        if total > cap:
            raise LatencyBudgetError(
                f"阶段预算总和超平面预算: {total}ms > {cap}ms（{plane.value}，Fail-Closed）"
            )
        items.sort(key=lambda sb: sb.stage)  # SSOT 确定性排序
        version = self._versions.get(plane, 0) + 1
        self._versions[plane] = version
        self._tables[plane] = BudgetTable(
            plane=plane,
            stages=tuple(items),
            version=version,
            allocated_at=self._clock(),
        )
        # 新表生效：清旧实际耗时，避免跨版本混算
        self._actuals[plane] = {sb.stage: [] for sb in items}
        return version

    def table(self, plane: Plane) -> BudgetTable:
        """平面预算表查询（未登记 → Fail-Closed）。"""
        if not isinstance(plane, Plane):
            raise LatencyBudgetError(f"非法平面: {plane!r}")
        table = self._tables.get(plane)
        if table is None:
            raise LatencyBudgetError(f"平面未登记预算表: {plane.value!r}")
        return table

    # ── 实际耗时上报 ──────────────────────────────────────────────────────

    def record(self, plane: Plane, stage: str, actual_ms: float) -> bool:
        """上报实际耗时：返回是否超预算；超支触发告警回调（仍记录留痕）。"""
        if not isinstance(plane, Plane):
            raise LatencyBudgetError(f"非法平面: {plane!r}")
        budget_ms = self._budget_of(plane, stage)
        if not (actual_ms >= 0):
            raise LatencyBudgetError(f"实际耗时为负: {actual_ms}ms")
        self._actuals[plane][stage].append(float(actual_ms))
        over = actual_ms > budget_ms
        if over:
            self._alert(BudgetViolation(
                plane=plane,
                stage=stage,
                budget_ms=budget_ms,
                actual_ms=float(actual_ms),
                raised_at=self._clock(),
            ))
        return over

    # ── 报表 ─────────────────────────────────────────────────────────────

    def report(self) -> dict:
        """预算消耗率报表（consumption_ratio = 平均实际耗时 / 阶段预算）。"""
        out: dict[str, dict] = {}
        for plane in sorted(self._tables, key=lambda p: p.value):
            table = self._tables[plane]
            stages_out: dict[str, dict] = {}
            for sb in table.stages:
                samples = self._actuals.get(plane, {}).get(sb.stage, [])
                count = len(samples)
                avg = sum(samples) / count if count else 0.0
                stages_out[sb.stage] = {
                    "budget_ms": sb.budget_ms,
                    "count": count,
                    "avg_actual_ms": avg,
                    "max_actual_ms": max(samples) if samples else 0.0,
                    "consumption_ratio": avg / sb.budget_ms,
                    "over_count": sum(1 for s in samples if s > sb.budget_ms),
                }
            out[plane.value] = {
                "version": table.version,
                "plane_budget_ms": PLANE_BUDGET_MS[plane],
                "allocated_ms": sum(sb.budget_ms for sb in table.stages),
                "stages": stages_out,
            }
        return out
