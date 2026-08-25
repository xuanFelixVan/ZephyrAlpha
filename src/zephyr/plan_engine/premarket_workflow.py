# [BLUEPRINT] MOD-PLAN-021 | docs/03_modules/_domain_plan_engine/premarket_workflow/blueprint.md
# [MODULE] zephyr.plan_engine.premarket_workflow
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.trading.work_dag(WorkDAG/WorkNode/WorkEdge)
# [CONSUMERS] 运行时装配批（conductor 执行 DAG；进度 state_sink 接 state_store 落库）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 三段式排程全在08:00-09:15窗口且段序单调; 依赖必须存在; premarket_check/readiness_confirm为mandatory必备工序; 进度状态机PENDING→RUNNING→DONE/FAILED/SKIPPED非法迁移Fail-Closed; mandatory失败→blocked+人工接管点; ready=mandatory全DONE且无blocked; mandatory不可跳过; state_sink异常不阻断如实记录; 只编排不核查不调度执行
# [MODIFY-GUARD] tests/plan_engine/test_premarket_workflow.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PremarketWorkflowError(未登记错误码-申请中)
# [TESTS] tests/plan_engine/test_premarket_workflow.py
# [A_module] module_id=MOD-PLAN-021 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: trading_date + stages(默认三段式SOP)
# A1: SOP校验(排程窗口/段序/依赖存在/mandatory必备)
# A2: build_premarket_dag(→WorkDAG复用MOD-INF-035模型)
# A3: 进度追踪(状态机+mandatory失败阻断+人工接管点+state_sink回调)
# O1: WorkDAG / progress快照(ready/blocked/takeover_point/by_stage)
# [/ALGO_FLOW]
"""D-TRADING-15 A股盘前标准化工作流（MOD-PLAN-021）。

真源：construction_backlog_dig.tsv B10-02213（D-TRADING-15 §30.2.5，裁定=做 P1）
+ CAND-PLAN-015。TSV 裁定注记："盘前SOP分钟级编排单人项目用work_dag即可承载，
无需独立BPM引擎"——本模块=该编排层。

与检查器族分工（查重铁律④）：premarket_checker（MOD-EX-063）是盘前**就绪核查
判定器**（四道关），本模块是**工作流编排**——把数据同步/隔夜复盘/预案生成/
盘前检查/就绪确认编成 08:00-09:15 三段式分钟级 DAG，premarket_check 只是确认
段其中一道工序。W-P1-22 盘前检查器候选（B1-00382/B14-04680）属检查器族将被
归并；CAND-PLAN-017（B14-04681，P2 工作流引擎）与本件近重复，归并指向本件。

三段式 SOP（排程全在 08:00-09:15 窗口）：
  - 段1 数据就绪（08:00-08:30）：data_sync → quality_gate（mandatory）
  - 段2 分析（08:30-09:00）：overnight_review → scenario_plan → llm_premarket
    （llm 非 mandatory，失败降级不阻断）
  - 段3 确认（09:00-09:15）：premarket_check（mandatory，MOD-EX-063 工序）
    → readiness_confirm（mandatory，人工在环确认点）

进度追踪：PremarketWorkflowTracker 状态机 PENDING→RUNNING→DONE/FAILED/
SKIPPED（非法迁移 Fail-Closed）；mandatory 工序 FAILED → blocked +
takeover_point（人工接管点）；ready = 全部 mandatory DONE 且无 blocked；
进度快照经 state_sink 回调落 state_store（装配批接线，sink 异常不阻断
如实记录）。

不做什么：不做就绪核查判定（归 MOD-EX-063）、不做真实调度执行（conductor
装配面）、不直接写 state_store（state_sink 回调委托）、不重造 WorkDAG
模型（MOD-INF-035 直用）。

SSoT: docs/03_modules/_domain_plan_engine/premarket_workflow/blueprint.md
"""

from __future__ import annotations

import datetime as _dt
import logging
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Final

from zephyr.trading.work_dag import WorkDAG, WorkEdge, WorkNode

__all__: Final = [
    "PremarketWorkflowError",
    "PremarketWorkflowTracker",
    "StageSpec",
    "StageStatus",
    "build_premarket_dag",
    "default_stages",
]

_log = logging.getLogger(__name__)

_WINDOW_START: Final = "08:00"
_WINDOW_END: Final = "09:15"
_PHASE_DEADLINE: Final = {1: "08:30", 2: "09:00", 3: "09:15"}
_MANDATORY_REQUIRED: Final = frozenset({"premarket_check", "readiness_confirm"})


class PremarketWorkflowError(Exception):
    """盘前工作流错误（SOP 非法/状态机非法迁移）。"""

    error_code = "ZA-PLAN-0007"  # 2026-08-25 主代理正式登记（P1 R4W19）

    def __init__(self, *args: object, error_code: str | None = None) -> None:
        super().__init__(*args)
        if error_code is not None:
            self.error_code = error_code


class StageStatus(str, Enum):
    """工序进度状态机。"""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass(frozen=True)
class StageSpec:
    """盘前工序规格（不可变，纯声明）。

    Attributes:
        stage_id: 工序唯一标识
        name: 工序中文名
        phase: 段号（1=数据就绪 / 2=分析 / 3=确认）
        scheduled_at: 分钟级排程时点 "HH:MM"（08:00-09:15 窗口内）
        deadline: 工序截止时点（不得越段界）
        capability_id: 执行能力标识（挂 work_dag 节点）
        mandatory: 是否必备工序（失败阻断）
        depends_on: 前置工序（success 条件边）
    """

    stage_id: str
    name: str
    phase: int
    scheduled_at: str
    deadline: str
    capability_id: str
    mandatory: bool
    depends_on: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.stage_id:
            raise PremarketWorkflowError("stage_id不能为空")
        if self.phase not in (1, 2, 3):
            raise PremarketWorkflowError(f"phase必须∈(1,2,3), got {self.phase}")
        for label, hhmm in (("scheduled_at", self.scheduled_at), ("deadline", self.deadline)):
            if not isinstance(hhmm, str) or len(hhmm) != 5 or hhmm[2] != ":":
                raise PremarketWorkflowError(f"{label}必须HH:MM格式, got {hhmm!r}")
            if not _WINDOW_START <= hhmm <= _WINDOW_END:
                raise PremarketWorkflowError(
                    f"{label}必须在{_WINDOW_START}-{_WINDOW_END}窗口内, got {hhmm}"
                )
        if self.scheduled_at > self.deadline:
            raise PremarketWorkflowError(
                f"scheduled_at({self.scheduled_at})不得晚于deadline({self.deadline})"
            )
        if self.deadline > _PHASE_DEADLINE[self.phase]:
            raise PremarketWorkflowError(
                f"段{self.phase}工序deadline不得晚于{_PHASE_DEADLINE[self.phase]}, got {self.deadline}"
            )
        if not self.capability_id:
            raise PremarketWorkflowError("capability_id不能为空")


def default_stages() -> tuple[StageSpec, ...]:
    """默认三段式 SOP（08:00-09:15 分钟级排程，§30.2.5）。"""
    return (
        StageSpec(
            stage_id="data_sync",
            name="行情与契约数据同步",
            phase=1,
            scheduled_at="08:00",
            deadline="08:20",
            capability_id="data.scheduler.sync_daily",
            mandatory=True,
        ),
        StageSpec(
            stage_id="quality_gate",
            name="数据质量门",
            phase=1,
            scheduled_at="08:20",
            deadline="08:30",
            capability_id="data.quality_gate.check",
            mandatory=True,
            depends_on=("data_sync",),
        ),
        StageSpec(
            stage_id="overnight_review",
            name="隔夜复盘与边界修正",
            phase=2,
            scheduled_at="08:30",
            deadline="08:40",
            capability_id="plan_engine.overnight_boundary_reviser.revise",
            mandatory=True,
            depends_on=("quality_gate",),
        ),
        StageSpec(
            stage_id="scenario_plan",
            name="三情景预案生成",
            phase=2,
            scheduled_at="08:40",
            deadline="08:50",
            capability_id="plan_engine.scenario_planner.compute",
            mandatory=True,
            depends_on=("overnight_review",),
        ),
        StageSpec(
            stage_id="llm_premarket",
            name="LLM盘前情报分析",
            phase=2,
            scheduled_at="08:50",
            deadline="09:00",
            capability_id="plan_engine.llm_premarket_analysis.analyze",
            mandatory=False,
            depends_on=("overnight_review",),
        ),
        StageSpec(
            stage_id="premarket_check",
            name="盘前就绪核查(MOD-EX-063)",
            phase=3,
            scheduled_at="09:00",
            deadline="09:10",
            capability_id="ex_core.premarket_checker.check",
            mandatory=True,
            depends_on=("scenario_plan",),
        ),
        StageSpec(
            stage_id="readiness_confirm",
            name="就绪确认(人工在环)",
            phase=3,
            scheduled_at="09:10",
            deadline="09:15",
            capability_id="plan_engine.premarket_workflow.confirm",
            mandatory=True,
            depends_on=("premarket_check",),
        ),
    )


def _validate_stages(stages: Sequence[StageSpec]) -> None:
    """SOP 拓扑校验（Fail-Closed）。"""
    if not stages:
        raise PremarketWorkflowError("SOP工序不能为空")
    ids = [s.stage_id for s in stages]
    if len(ids) != len(set(ids)):
        raise PremarketWorkflowError("stage_id不得重复")
    id_set = set(ids)
    for s in stages:
        unknown = set(s.depends_on) - id_set
        if unknown:
            raise PremarketWorkflowError(f"工序{s.stage_id}依赖不存在: {sorted(unknown)}")
    mandatory_ids = {s.stage_id for s in stages if s.mandatory}
    missing = _MANDATORY_REQUIRED - mandatory_ids
    if missing:
        raise PremarketWorkflowError(f"mandatory必备工序缺失: {sorted(missing)}")


def build_premarket_dag(
    trading_date: str,
    stages: Sequence[StageSpec] | None = None,
) -> WorkDAG:
    """构建盘前三段式 WorkDAG（复用 MOD-INF-035 模型，纯声明不调度执行）。"""
    try:
        _dt.date.fromisoformat(trading_date)
    except (TypeError, ValueError) as exc:
        raise PremarketWorkflowError(f"trading_date必须ISO格式YYYY-MM-DD, got {trading_date!r}") from exc
    specs = tuple(stages) if stages is not None else default_stages()
    _validate_stages(specs)

    nodes = [
        WorkNode(
            node_id=s.stage_id,
            capability_id=s.capability_id,
            work_type="premarket_sop",
            params={
                "trading_date": trading_date,
                "phase": s.phase,
                "scheduled_at": s.scheduled_at,
                "deadline": s.deadline,
                "mandatory": s.mandatory,
                "name": s.name,
            },
        )
        for s in specs
    ]
    edges = [
        WorkEdge(from_node=dep, to_node=s.stage_id, condition="success")
        for s in specs
        for dep in s.depends_on
    ]
    return WorkDAG(
        dag_id=f"premarket_sop:{trading_date}",
        name="A股盘前标准化工作流(D-TRADING-15)",
        description="08:00-09:15三段式SOP：数据就绪→分析→确认（MOD-PLAN-021）",
        nodes=nodes,
        edges=edges,
        default_priority="P1",
        timeout_minutes=75,
    )


class PremarketWorkflowTracker:
    """盘前工作流进度追踪器（状态机 + 阻断/接管点 + state_sink 回调）。"""

    def __init__(
        self,
        trading_date: str,
        stages: Sequence[StageSpec],
        state_sink: Callable[[dict], None] | None = None,
    ) -> None:
        if not trading_date:
            raise PremarketWorkflowError("trading_date不能为空")
        _validate_stages(stages)
        self._trading_date = trading_date
        self._specs: dict[str, StageSpec] = {s.stage_id: s for s in stages}
        self._status: dict[str, StageStatus] = {s.stage_id: StageStatus.PENDING for s in stages}
        self._failed_reason: dict[str, str] = {}
        self._state_sink = state_sink

    @property
    def blocked(self) -> bool:
        """mandatory 工序失败 → 阻断。"""
        return any(
            self._status[sid] is StageStatus.FAILED and self._specs[sid].mandatory
            for sid in self._specs
        )

    @property
    def takeover_point(self) -> str | None:
        """人工接管点（首个失败的 mandatory 工序）。"""
        for sid, spec in self._specs.items():
            if spec.mandatory and self._status[sid] is StageStatus.FAILED:
                return sid
        return None

    @property
    def ready(self) -> bool:
        """就绪 = 全部 mandatory DONE 且无阻断。"""
        if self.blocked:
            return False
        return all(
            self._status[sid] is StageStatus.DONE
            for sid, spec in self._specs.items()
            if spec.mandatory
        )

    def _emit(self) -> None:
        if self._state_sink is None:
            return
        try:
            self._state_sink(self.progress())
        except Exception:  # noqa: BLE001 — sink 异常不阻断如实记录（装配批接线）
            _log.warning("state_sink 回调异常（不阻断）", exc_info=True)

    def _stage(self, stage_id: str) -> StageSpec:
        if stage_id not in self._specs:
            raise PremarketWorkflowError(f"未知工序: {stage_id}")
        return self._specs[stage_id]

    def mark_running(self, stage_id: str) -> None:
        self._stage(stage_id)
        if self._status[stage_id] is not StageStatus.PENDING:
            raise PremarketWorkflowError(
                f"工序{stage_id}仅PENDING可转RUNNING, 当前{self._status[stage_id].value}"
            )
        self._status[stage_id] = StageStatus.RUNNING
        self._emit()

    def mark_done(self, stage_id: str) -> None:
        self._stage(stage_id)
        if self._status[stage_id] is not StageStatus.RUNNING:
            raise PremarketWorkflowError(
                f"工序{stage_id}仅RUNNING可转DONE, 当前{self._status[stage_id].value}"
            )
        self._status[stage_id] = StageStatus.DONE
        self._emit()

    def mark_failed(self, stage_id: str, reason: str = "") -> None:
        self._stage(stage_id)
        if self._status[stage_id] is not StageStatus.RUNNING:
            raise PremarketWorkflowError(
                f"工序{stage_id}仅RUNNING可转FAILED, 当前{self._status[stage_id].value}"
            )
        self._status[stage_id] = StageStatus.FAILED
        self._failed_reason[stage_id] = reason
        self._emit()

    def mark_skipped(self, stage_id: str, reason: str = "") -> None:
        spec = self._stage(stage_id)
        if spec.mandatory:
            raise PremarketWorkflowError(f"mandatory工序{stage_id}不可跳过")
        if self._status[stage_id] is not StageStatus.PENDING:
            raise PremarketWorkflowError(
                f"工序{stage_id}仅PENDING可转SKIPPED, 当前{self._status[stage_id].value}"
            )
        self._status[stage_id] = StageStatus.SKIPPED
        self._failed_reason[stage_id] = reason
        self._emit()

    def progress(self) -> dict:
        """进度快照（state_store 落库契约）。"""
        by_stage = {sid: st.value for sid, st in self._status.items()}
        done = sum(1 for st in self._status.values() if st is StageStatus.DONE)
        return {
            "trading_date": self._trading_date,
            "by_stage": by_stage,
            "done": done,
            "total": len(self._status),
            "blocked": self.blocked,
            "takeover_point": self.takeover_point,
            "ready": self.ready,
            "failed_reason": dict(self._failed_reason),
        }
