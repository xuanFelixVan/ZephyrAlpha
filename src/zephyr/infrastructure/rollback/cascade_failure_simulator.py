# [BLUEPRINT] MOD-INF-089 | docs/03_modules/_domain_infrastructure_operations/cascade_failure_simulator/blueprint.md
# [MODULE] zephyr.infrastructure.rollback.cascade_failure_simulator
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES] 无（纯内存；injector/is_trading_hours/backup_confirmed/时钟全注入，不真杀进程不触网）
# [CONSUMERS] 运行时装配批（灾备演练编排 / 恢复时间度量 / 失效传播复盘）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 安全护栏三件套: 交易时段拒绝运行+备份未确认拒绝+超时终止; injector 未注入构造即 Fail-Closed; 失效传播=相邻步骤 target 有向边链; 恢复时间=注入时钟起止差; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure_operations/cascade_failure_simulator/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] CascadeSimError(占位 ZA-INF-UNREGISTERED-CASCADE-SIM)——空scenario_id/空steps/重复step_id/非法kind/空target/交易时段/备份未确认/injector缺失或异常/非法超时时抛
# [TESTS] tests/infrastructure/test_cascade_failure_simulator.py
# [A_module] module_id=MOD-INF-089 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""CascadeFailureSimulator — 级联失效仿真器（MOD-INF-089）。

B14-04693（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-DR-002，A9运维架构）：
单机级联失效仿真——进程崩溃/Redis 中断/GPU 失效组合场景脚本化（FailureScenario
Schema + run 编排），失效传播路径有向事件链记录，恢复时间测量（注入时钟），
安全护栏三件套（交易时段拒绝运行 + 备份确认前置 + 30min 超时终止）。纯仿真
编排，故障注入全经注入 injector 回调，不真杀进程。

查重分工（蓝图 §0）：chaos_injector=故障注入原语实现（本件只做场景编排并强
制经回调执行）；rollback_drill=回滚演练（本件为失效传播仿真，零交集）。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "CascadeFailureSimulator",
    "CascadeSimError",
    "FailureKind",
    "FailureScenario",
    "RunStatus",
    "SimEvent",
    "SimResult",
    "SimStep",
]

#: 默认仿真超时（分钟）
_DEFAULT_TIMEOUT_MINUTES: Final[int] = 30


class CascadeSimError(Exception):
    """级联仿真输入/护栏非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-INF-UNREGISTERED-CASCADE-SIM。
    """


class FailureKind(str, Enum):
    """失效类型（词表闭合）。"""

    PROCESS_CRASH = "process_crash"
    REDIS_OUTAGE = "redis_outage"
    GPU_FAILURE = "gpu_failure"


class RunStatus(str, Enum):
    """仿真运行状态。"""

    COMPLETED = "completed"
    ABORTED_TIMEOUT = "aborted_timeout"


@dataclass(frozen=True)
class SimStep:
    """仿真步骤（单点失效注入单元，frozen）。"""

    step_id: str
    kind: FailureKind
    target: str


@dataclass(frozen=True)
class FailureScenario:
    """级联失效场景（步骤有序组合，frozen）。"""

    scenario_id: str
    steps: tuple[SimStep, ...]


@dataclass(frozen=True)
class SimEvent:
    """失效注入事件（有向事件链节点，frozen）。"""

    seq: int
    step_id: str
    kind: FailureKind
    target: str
    ts: datetime.datetime


@dataclass(frozen=True)
class SimResult:
    """仿真结果（事件链 + 传播路径 + 恢复时间，frozen）。"""

    scenario_id: str
    status: RunStatus
    events: tuple[SimEvent, ...]
    propagation_path: tuple[tuple[str, str], ...]
    recovery_ms: float
    started_at: datetime.datetime
    finished_at: datetime.datetime


class CascadeFailureSimulator:
    """级联失效仿真器（场景编排 + 护栏 + 传播记录 + 恢复测量）。"""

    def __init__(
        self,
        *,
        injector: Callable[[SimStep], None] | None,
        is_trading_hours: Callable[[], bool] | None = None,
        backup_confirmed: Callable[[], bool] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
        timeout_minutes: int = _DEFAULT_TIMEOUT_MINUTES,
    ) -> None:
        if injector is None:
            raise CascadeSimError("injector 未注入（故障注入强制回调，禁止真杀进程旁路）")
        if not isinstance(timeout_minutes, int) or timeout_minutes <= 0:
            raise CascadeSimError(f"timeout_minutes 非法: {timeout_minutes!r}")
        self._injector = injector
        self._is_trading_hours = is_trading_hours or (lambda: False)
        self._backup_confirmed = backup_confirmed or (lambda: True)
        self._clock = clock or datetime.datetime.now
        self._timeout = datetime.timedelta(minutes=timeout_minutes)
        self._history: list[SimResult] = []

    # ── 校验 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _validate(scenario: FailureScenario) -> None:
        if not isinstance(scenario, FailureScenario):
            raise CascadeSimError(f"非法场景类型: {type(scenario).__name__}")
        if not scenario.scenario_id:
            raise CascadeSimError("scenario_id 为空")
        if not scenario.steps:
            raise CascadeSimError(f"steps 为空: {scenario.scenario_id!r}")
        seen: set[str] = set()
        for step in scenario.steps:
            if not step.step_id:
                raise CascadeSimError("step_id 为空")
            if step.step_id in seen:
                raise CascadeSimError(f"step_id 重复: {step.step_id!r}")
            seen.add(step.step_id)
            if not isinstance(step.kind, FailureKind):
                raise CascadeSimError(f"非法失效类型: {step.kind!r}")
            if not step.target:
                raise CascadeSimError(f"target 为空: {step.step_id!r}")

    # ── 编排 ─────────────────────────────────────────────────────────────

    def run(self, scenario: FailureScenario) -> SimResult:
        """运行场景：护栏三件套 → 逐步注入 → 事件链/传播路径/恢复时间。"""
        self._validate(scenario)
        if self._is_trading_hours():
            raise CascadeSimError(
                f"交易时段拒绝运行仿真: {scenario.scenario_id!r}（安全护栏）"
            )
        if not self._backup_confirmed():
            raise CascadeSimError(
                f"备份未确认，拒绝运行仿真: {scenario.scenario_id!r}（安全护栏）"
            )

        started = self._clock()
        events: list[SimEvent] = []
        edges: list[tuple[str, str]] = []
        prev_target: str | None = None
        status = RunStatus.COMPLETED
        for step in scenario.steps:
            if self._clock() - started > self._timeout:
                status = RunStatus.ABORTED_TIMEOUT
                _log.warning(
                    "仿真超时终止: %s 已运行超过 %.0f 分钟，剩余步骤跳过",
                    scenario.scenario_id, self._timeout.total_seconds() / 60.0,
                )
                break
            ts = self._clock()
            try:
                self._injector(step)
            except Exception as exc:  # noqa: BLE001 — 注入异常 Fail-Closed
                _log.exception("injector 执行异常: %s", step.step_id)
                raise CascadeSimError(
                    f"injector 执行异常: {step.step_id!r} ({exc})"
                ) from exc
            events.append(SimEvent(
                seq=len(events), step_id=step.step_id, kind=step.kind,
                target=step.target, ts=ts,
            ))
            if prev_target is not None:
                edges.append((prev_target, step.target))
            prev_target = step.target

        finished = self._clock()
        result = SimResult(
            scenario_id=scenario.scenario_id,
            status=status,
            events=tuple(events),
            propagation_path=tuple(edges),
            recovery_ms=(finished - started).total_seconds() * 1000.0,
            started_at=started,
            finished_at=finished,
        )
        self._history.append(result)
        _log.info("仿真完成: %s status=%s 事件=%d 恢复=%.1fms",
                  scenario.scenario_id, status.value, len(events), result.recovery_ms)
        return result

    # ── 查询 ─────────────────────────────────────────────────────────────

    def history(self) -> tuple[SimResult, ...]:
        """历史仿真结果（运行序）。"""
        return tuple(self._history)
